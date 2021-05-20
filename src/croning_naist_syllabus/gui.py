import logging

import PySimpleGUI as sg

from .fetch import FetchData
from .operatedb import OperateMongoDB

logger = logging.getLogger(__name__)


class GUI:

    sg.theme("SandyBeach")
    SIZE = (300, 300)

    def __init__(self, url="https://syllabus.naist.jp/subjects/preview_list"):
        self.url = url
        self.fd = FetchData(self.url)
        self.omd = OperateMongoDB()
        self.omd.client.drop_database(self.omd.database_name)

    def start_display(self):
        layout = [
            [
                sg.Button(
                    "授業情報を取得する",
                    font=(10),
                    size=(15, 3),
                    key="start_display",
                    button_color=("#000000", "#ffffff"),
                )
            ]
        ]
        return sg.Window(
            "NAIST講義クローニング", layout, element_justification="c", size=self.SIZE
        )

    def request_lectures(self):
        # fix
        self.omd.client.drop_database(self.omd.database_name)

        self.fd.scrape_lectures(FetchData.LECTURE_TYPES)
        layout = []
        for lecture_type, names_and_urls in self.fd.name_and_url_of_lectures.items():
            self.omd.select_collection_from_lecture_type(lecture_type)
            layout.append(
                [
                    sg.Radio(
                        FetchData.EN_TO_JA[lecture_type],
                        group_id="lecture_type",
                        key=lecture_type,
                    )
                ]
            )

            for name_and_url in names_and_urls:
                self.omd.add_lecture_detail(
                    [{"name": name_and_url.name, "url": name_and_url.url}]
                )

        layout.append([sg.Button("一覧を表示する", key="request_lectures")])
        return sg.Window(
            "NAISTの授業一覧", layout, element_justification="c", size=self.SIZE
        )

    def display_lecture(self, lecture_types: dict):
        layout1 = []
        type = None
        for lecture_type, checked in lecture_types.items():

            if not lecture_type in FetchData.LECTURE_TYPES:
                continue

            if checked:
                type = lecture_type

            layout1.append(
                [
                    sg.Radio(
                        FetchData.EN_TO_JA[lecture_type],
                        default=checked,
                        group_id="lecture_type",
                        key=lecture_type,
                    )
                ]
            )

        layout1.append([sg.Button("一覧を表示する", key="request_lectures")])

        if type is None:
            logger.error("type is None in diplay_lecture method")
            exit()

        lectures = self.omd.get_all_lecture(type)
        layout2 = []
        layout2_two_set = []
        for lecture in lectures:
            if len(layout2_two_set) == 2:
                layout2.append(layout2_two_set)
                layout2_two_set = []

            layout2_two_set.append(
                sg.Radio(lecture["name"], group_id="lecture", key=lecture["name"])
            )

        layout2.append(layout2_two_set)
        layout2.append([sg.Button("詳細を表示する", key="detail")])

        layout = [[sg.Frame("", layout1), sg.Frame(FetchData.EN_TO_JA[type], layout2)]]

        return sg.Window("授業一覧", layout, element_justification="c")

    def display_details(self, lectures: dict):
        lecture_name = None
        for lecture, checked in lectures.items():
            if lecture in FetchData.LECTURE_TYPES:
                continue

            if checked:
                lecture_name = lecture
                break

        if lecture_name is None:
            logger.error("lecture_name is None")
            exit()

        lecture = self.omd.get_lecture(lecture_name)
        lecture_details = {
            "name": lecture_name,
            "details": self.fd.scrape_one_details(lecture["url"]),
        }
        self.omd.update_lecture_details([lecture_details])
        layout = []
        for lecture in lecture_details["details"]:
            layout.append(
                [
                    sg.Text(lecture.number),
                    sg.Text(lecture.date),
                    sg.Text(lecture.theme),
                    sg.Text(lecture.content),
                ]
            )

        layout.append([sg.Button("戻る", key="start_display")])

        return sg.Window("授業の詳細", layout)
