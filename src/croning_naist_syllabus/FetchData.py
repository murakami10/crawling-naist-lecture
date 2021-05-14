import re
from typing import NamedTuple

import lxml.html
import requests


class FetchData:

    LECTURE_TYPE_GENERAL = "general"
    LECTURE_TYPE_INTRODUCTION = "introduction"
    LECTURE_TYPE_BASIC = "basic"
    LECTURE_TYPE_SPECIALIZED = "specialized"

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

    def scrape_lectures(self, lectures: list):

        self.name_and_url_of_lectures = {}

        for lecture in lectures:

            self.name_and_url_of_lectures[lecture] = self.scrape_name_and_url(lecture)

    def scrape_name_and_url(self, lecture):
        """
        授業科目の名前とURLを取得
        """
        lecture_datas = []

        # start_index_of_lectureにないkeyを指定すると例外を投げる
        # 例外に気づくためにcatchしない
        index = self.START_INDEX_OF_LECTURE[lecture]

        while value := self.root.cssselect(
            f"#contents > table > tbody > tr:nth-child({index}) > td.w20pr"
        ):

            # aタグをのURLを調べ、Noneであれば"not exist"を代入
            url = value[0].find("a")
            if url is None:
                url = "not exist"
            else:
                url = url.get("href")

            lecture_datas.append(LectureNameUrl(name=value[0].text_content(), url=url))
            index += 1

        return lecture_datas

    def scrape_details(self, lectures: list):

        self.lectures_details = {}
        for lecture in lectures:
            if not isinstance(lecture, LectureNameUrl):
                continue

            response = requests.get(lecture.url)

            # 無効なurlの際に例外を投げる
            response.raise_for_status()

            self.lectures_details[lecture.name] = self.scrape_detail_of_lecture(
                response
            )

    def scrape_detail_of_lecture(self, response: requests.Response):
        """
        授業の詳細な情報を取得
        """

        root = lxml.html.fromstring(response.content)

        lecture = []
        index = 2

        while element := root.cssselect(
            f"#contents > table:nth-child(12) > tbody > tr:nth-child({index})"
        ):
            td_element = element[0].findall("td")

            # 空白文字(\n\t\r\f\v)を空白に変更する関数
            normalize_spaces = lambda text: re.sub(r"\s+", " ", text).strip()

            lecture.append(
                LectureDetail(
                    number=int(td_element[0].text_content()),
                    date=td_element[1].text_content(),
                    theme=normalize_spaces(td_element[3].text_content()),
                    content=normalize_spaces(td_element[4].text_content()),
                )
            )

            index += 1
        return lecture


class LectureNameUrl(NamedTuple):
    name: str
    url: str


class LectureDetail(NamedTuple):
    number: int
    date: str
    theme: str
    content: str
