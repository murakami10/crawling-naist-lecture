import re
from typing import List

import lxml.html
import requests

from .structure import Lecture, LectureDetail


class FetchData:

    LECTURE_TYPE_GENERAL = "general"
    LECTURE_TYPE_INTRODUCTION = "introduction"
    LECTURE_TYPE_BASIC = "basic"
    LECTURE_TYPE_SPECIALIZED = "specialized"

    LECTURE_TYPES = [
        LECTURE_TYPE_SPECIALIZED,
        LECTURE_TYPE_BASIC,
        LECTURE_TYPE_GENERAL,
        LECTURE_TYPE_INTRODUCTION,
    ]

    EN_TO_JA = {
        LECTURE_TYPE_GENERAL: "一般科目",
        LECTURE_TYPE_INTRODUCTION: "序論科目",
        LECTURE_TYPE_BASIC: "基礎科目",
        LECTURE_TYPE_SPECIALIZED: "専門科目",
    }

    START_INDEX_OF_LECTURE = {
        LECTURE_TYPE_GENERAL: 5,
        LECTURE_TYPE_INTRODUCTION: 35,
        LECTURE_TYPE_BASIC: 40,
        LECTURE_TYPE_SPECIALIZED: 67,
    }

    def __init__(self, url: str):
        self.response: requests.Response = requests.get(url)
        # ステータスコードが200番以外なら例外を起こす
        self.response.raise_for_status()
        self.root = lxml.html.fromstring(self.response.content)
        self.root.make_links_absolute(self.response.url)

    def scrape_name_and_url(self, lecture_type) -> List[Lecture]:
        """
        授業科目の名前とURLを取得
        """

        lectures: List[Lecture] = []

        # start_index_of_lectureにないkeyを指定すると例外を投げる
        # 例外に気づくためにcatchしない
        index = self.START_INDEX_OF_LECTURE[lecture_type]

        while value := self.root.cssselect(
            f"#contents > table  > tr:nth-child({index}) > td.w20pr"
        ):

            # aタグをのURLを調べ、Noneであれば"not exist"を代入
            url = value[0].find("a")
            if url is None:
                url = "not exist"
            else:
                url = url.get("href")

            lectures.append(Lecture(value[0].text_content(), url))
            index += 1

        return lectures

    def scrape_detail(self, lecture: Lecture) -> Lecture:
        """
        授業の詳細な情報を取得
        """

        response = requests.get(lecture.url)
        # 無効なurlの際に例外を投げる
        response.raise_for_status()

        root = lxml.html.fromstring(response.content)

        lecture_details = []
        index = 2

        while element := root.cssselect(
            f"#contents > table:nth-child(12) >  tr:nth-child({index})"
        ):
            td_element = element[0].findall("td")

            # 空白文字(\n\t\r\f\v)を空白に変更する関数
            normalize_spaces = lambda text: re.sub(r"\s+", " ", text).strip()

            lecture_details.append(
                LectureDetail(
                    number=int(td_element[0].text_content()),
                    date=td_element[1].text_content(),
                    theme=normalize_spaces(td_element[3].text_content()),
                    content=normalize_spaces(td_element[4].text_content()),
                )
            )

            index += 1

        lecture.details = lecture_details
        return lecture
