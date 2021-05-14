from typing import NamedTuple

import lxml.html
import requests


class FetchData:

    LECTURE_TYPE_GENERAL = "general"
    LECTURE_TYPE_INTRODUCTION = "introduction"
    LECTURE_TYPE_BASIC = "basic"
    LECTURE_TYPE_SPECIALIZED = "specialized"

    start_index_of_lecture = {
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

    def choose_lecture(self, lectures: list):

        self.name_and_url_of_lectures = {}

        for lecture in lectures:

            self.name_and_url_of_lectures[lecture] = self.get_name_and_url(lecture)

    def get_name_and_url(self, lecture):
        """
        授業科目の名前とURLを取得
        """
        lecture_datas = []

        # start_index_of_lectureにないkeyを指定すると例外を投げる
        # 例外に気づくためにcatchしない
        index = self.start_index_of_lecture[lecture]

        while True:

            value = self.root.cssselect(
                f"#contents > table > tbody > tr:nth-child({index}) > td.w20pr"
            )

            if not value:
                break

            # aタグをのURLを調べ、Noneであれば"not exist"を代入
            url = value[0].find("a")
            if url is None:
                url = "not exist"
            else:
                url = url.get("href")

            lecture_datas.append(LectureNameUrl(name=value[0].text_content(), url=url))
            index += 1

        return lecture_datas


class LectureNameUrl(NamedTuple):
    name: str
    url: str
