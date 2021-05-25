import logging

import PySimpleGUI as sg

from .control import load_data, load_details_data
from .fetch import FetchData, LectureDetail
from .operatedb import OperateMongoDB

logger = logging.getLogger(__name__)


class GUI:

    sg.theme("SandyBeach")

    def __init__(self, url="https://syllabus.naist.jp/subjects/preview_list"):
        self.url = url
        self.fd = FetchData(self.url)
        self.omd = OperateMongoDB()

    def start_display(self):
        layout = self._get_lecture_type_layout()

        layout.append([sg.Button("授業一覧を表示する", key="display_lecture", font=(20))])
        return sg.Window(
            "NAISTの授業一覧", layout, element_justification="c", size=(200, 150)
        )

    def display_lectures(self, lecture_types: dict):

        self.checked_lecture_type = None

        for lecture_type, checked in lecture_types.items():

            if not lecture_type in FetchData.LECTURE_TYPES:
                continue

            if checked == True:
                self.checked_lecture_type = lecture_type
                break

        if self.checked_lecture_type is None:
            logger.error("type is not checked")
            exit()

        layout_lecture_type = self._get_lecture_type_layout(self.checked_lecture_type)
        layout_lecture_type.append([sg.Button("一覧を表示", key="start_display", font=(20))])

        layout_lecture_column = self._get_lecture_column_layout(
            self.checked_lecture_type
        )

        layout = [
            [
                sg.Frame(
                    "Lecture Type",
                    layout=layout_lecture_type,
                ),
                sg.Frame(
                    "Lecture",
                    layout=[
                        layout_lecture_column,
                        [sg.Button("授業の詳細を表示する", font=(20), key="display_detail")],
                    ],
                ),
            ]
        ]

        return sg.Window("授業一覧", layout, resizable=True, size=(1300, 700))

    def display_details(self, lectures: dict, refetch=False):

        lecture_name = None

        for lecture, checked in lectures.items():

            if lecture in FetchData.LECTURE_TYPES:
                continue

            if checked:
                lecture_name = lecture
                break

            if lecture == "detail_name":
                lecture_name = checked

        if self.checked_lecture_type is None:
            logger.error("type is not checked")
            exit()

        if lecture_name is None:
            logger.error("lecture is not checked")
            exit()

        layout_lecture_type = self._get_lecture_type_layout(self.checked_lecture_type)
        layout_lecture_type.append(
            [sg.Button("一覧を表示", key="display_lecture", font=(20))]
        )

        layout_lecture_column = self._get_lecture_column_layout(
            self.checked_lecture_type, lecture_name
        )

        layout_lecture_details = self._get_lecture_details_layout(
            self.checked_lecture_type, lecture_name, refetch
        )
        layout_lecture_details.append(
            [sg.Button("授業の詳細を再取得する", font=(20), key="refetch_details")]
        )

        layout = [
            [
                sg.Frame(
                    "Lecture Type",
                    layout=layout_lecture_type,
                ),
                sg.Frame(
                    "Lecture",
                    layout=[
                        layout_lecture_column,
                        [sg.Button("授業の詳細を表示する", font=(20), key="display_detail")],
                    ],
                ),
                sg.Frame(
                    "Details",
                    layout=layout_lecture_details,
                    font=(30),
                ),
            ]
        ]

        return sg.Window("授業の詳細", layout, size=(1300, 700))

    def _get_lecture_type_layout(
        self, checked_lecture_type=FetchData.LECTURE_TYPE_SPECIALIZED
    ):
        layouts = []

        for lecture_type in FetchData.LECTURE_TYPES:
            layouts.append(
                [
                    sg.Radio(
                        FetchData.EN_TO_JA[lecture_type],
                        group_id="lecture_type",
                        default=True if checked_lecture_type == lecture_type else False,
                        key=lecture_type,
                        font=(20),
                    )
                ]
            )

        return layouts

    def _get_lecture_column_layout(
        self, checked_lecture_type, checked_lecture_name="not_checked"
    ):
        lectures = load_data(checked_lecture_type, self.omd, self.fd)
        if checked_lecture_name == "not_checked":
            checked_lecture_name = lectures[0]["name"]

        layout_lecture = []
        for lecture in lectures:
            layout_lecture.append(
                [
                    sg.Radio(
                        lecture["name"],
                        group_id="lecture",
                        key=lecture["name"],
                        default=True
                        if checked_lecture_name == lecture["name"]
                        else False,
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

    def _get_lecture_details_layout(
        self, checked_lecture_type, lecture_name, refetch=False
    ):
        lecture_details = load_details_data(
            checked_lecture_type, lecture_name, self.omd, self.fd, refetch
        )
        layout_lecture_details = []
        for lecture in lecture_details:

            if isinstance(lecture, LectureDetail):
                detail: dict = lecture._asdict()
            elif isinstance(lecture, dict):
                detail: dict = lecture
            else:
                logger.error("lecture type is not dict or LectureNameUrl")
                exit()

            layout_lecture_details.append(
                [sg.Text(value, font=(20)) for value in detail.values()]
            )

        return layout_lecture_details
