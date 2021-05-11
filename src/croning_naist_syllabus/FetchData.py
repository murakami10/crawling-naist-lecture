import lxml.html
import requests


class FetchData:
    def __init__(self, url: str):
        self.response: requests.Response = requests.get(url)
        # ステータスコードが200番以外なら例外を起こす
        self.response.raise_for_status()

    def serach_for_lecture_name(self):
        root = lxml.html.fromstring(self.response)
