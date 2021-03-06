import logging

import PySimpleGUI as sg

from .control import load_details, load_lectures
from .fetch import FetchData, LectureDetail
from .operatedb import OperateMongoDB

logger = logging.getLogger(__name__)


class GUI:

    sg.theme("SandyBeach")
    checked_lecture_type = FetchData.LECTURE_TYPE_SPECIALIZED
    checked_lecture_name = None

    def __init__(self, url="https://syllabus.naist.jp/subjects/preview_list"):
        self.url = url
        self.fd = FetchData(self.url)
        self.omd = OperateMongoDB()

    def loop(self):
        window = self.start_display()

        while True:
            event, values = window.read()
            logger.debug(event, values)
            if event == None:
                break
            elif event == "display_lecture":
                window.close()
                window = self.display_lectures(values)
            elif event == "display_detail":
                window.close()
                window = self.display_details(values)
            elif event == "refetch_details":
                window.close()
                window = self.display_details(values, True)

        window.close()

    def start_display(self):
        layout = self._create_lecture_type_layout()

        layout.append([sg.Button("授業一覧を表示する", key="display_lecture", font=(20))])
        return sg.Window(
            "NAISTの授業一覧", layout, element_justification="c", size=(200, 150)
        )

    def display_lectures(self, lecture_types: dict):

        # checkされたlecture_typeを見つける
        for lecture_type, checked in lecture_types.items():

            if not lecture_type in FetchData.LECTURE_TYPES:
                continue

            if checked == True:
                self.checked_lecture_type = lecture_type
                break

        if self.checked_lecture_type is None:
            logger.error("type is not checked")
            exit()

        layout = [
            [
                sg.Frame(
                    "Lecture Type",
                    layout=self._create_lecture_type_layout(),
                ),
                sg.Frame(
                    "Lecture",
                    layout=[
                        self._create_lecture_column_layout(init=True),
                        [sg.Button("授業の詳細を表示する", font=(20), key="display_detail")],
                    ],
                ),
            ]
        ]

        return sg.Window("授業一覧", layout, resizable=True, size=(1300, 700))

    def display_details(self, lectures: dict, refetch=False):

        for lecture, checked in lectures.items():

            if refetch:
                break

            if lecture in FetchData.LECTURE_TYPES:
                continue

            if checked:
                self.checked_lecture_name = lecture
                break

        if self.checked_lecture_name is None:
            logger.error("lecture is not checked")
            exit()

        layout = [
            [
                sg.Frame(
                    "Lecture Type",
                    layout=self._create_lecture_type_layout(),
                ),
                sg.Frame(
                    "Lecture",
                    layout=[
                        self._create_lecture_column_layout(),
                        [sg.Button("授業の詳細を表示する", font=(20), key="display_detail")],
                    ],
                ),
                sg.Frame(
                    "Details",
                    layout=self._create_lecture_details_layout(refetch),
                    font=(30),
                ),
            ]
        ]

        return sg.Window("授業の詳細", layout, size=(1300, 700))

    def _create_lecture_type_layout(self):
        layouts = []
        for lecture_type in FetchData.LECTURE_TYPES:
            layouts.append(
                [
                    sg.Radio(
                        FetchData.EN_TO_JA[lecture_type],
                        group_id="lecture_type",
                        default=(
                            True if self.checked_lecture_type == lecture_type else False
                        ),
                        key=lecture_type,
                        font=(20),
                    )
                ]
            )

        layouts.append([sg.Button("一覧を表示", key="display_lecture", font=(20))])

        return layouts

    def _create_lecture_column_layout(self, init=False):

        lectures = load_lectures(self.checked_lecture_type, self.omd, self.fd)

        if init:
            self.checked_lecture_name = lectures[0].name

        layout_lecture = []
        for lecture in lectures:
            layout_lecture.append(
                [
                    sg.Radio(
                        lecture.name,
                        group_id="lecture",
                        key=lecture.name,
                        default=(
                            True if self.checked_lecture_name == lecture.name else False
                        ),
                        font=(20),
                    )
                ]
            )

        layout_lecture_column = [
            sg.Column(
                layout_lecture,
                scrollable=True,
                vertical_scroll_only=True,
                size=(300, 600),
            )
        ]

        return layout_lecture_column

    def _create_lecture_details_layout(self, refetch=False):
        lecture_details = load_details(
            self.checked_lecture_type,
            self.checked_lecture_name,
            self.omd,
            self.fd,
            refetch,
        )
        layout_lecture_details = []
        for lecture_detail in lecture_details:
            layout_lecture_details.append(
                [sg.Text(value, font=(20)) for value in list(lecture_detail)]
            )

        layout_lecture_details.append(
            [sg.Button("授業の詳細を再取得する", font=(20), key="refetch_details")]
        )
        return layout_lecture_details
