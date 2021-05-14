import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
import requests

from src.croning_naist_syllabus.FetchData import (
    FetchData,
    LectureDetail,
    LectureNameUrl,
)


@pytest.fixture(scope="session")
def start_http_server():
    host, port = ("127.0.0.1", 8888)
    url = f"http://{host}:{port}/index.html"
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    thred = threading.Thread(target=server.serve_forever)
    thred.start()
    yield url
    server.shutdown()
    thred.join()


@pytest.fixture()
def fetch_data():
    """
    FetchDataのインスタンスを返す
    """
    fd = FetchData("http://127.0.0.1:8888/tests/syllabus.html")
    return fd


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http://127.0.0.1:8888/not_existed_index.html",
        "httpaaaa",
    ],
)
def test_init_with_invalid_url(start_http_server, invalid_url):
    with pytest.raises(Exception):
        FetchData(invalid_url)


def test_init_with_valid_url(start_http_server):
    valid_url = "http://127.0.0.1:8888/tests/index.html"
    _ = FetchData(valid_url)


general_lecture = LectureNameUrl(
    name="技術と倫理", url="https://syllabus.naist.jp/subjects/preview_detail/644"
)
introduction_lecture = LectureNameUrl(
    name="情報理工学序論", url="https://syllabus.naist.jp/subjects/preview_detail/662"
)
basic_lecture = LectureNameUrl(
    name="情報科学基礎Ⅰ", url="https://syllabus.naist.jp/subjects/preview_detail/791"
)
specialized_lecture = LectureNameUrl(
    name="ソフトウェア工学", url="https://syllabus.naist.jp/subjects/preview_detail/688"
)


@pytest.mark.parametrize(
    "lecture_type, contained_data",
    [
        (FetchData.LECTURE_TYPE_GENERAL, general_lecture),
        (FetchData.LECTURE_TYPE_INTRODUCTION, introduction_lecture),
        (FetchData.LECTURE_TYPE_BASIC, basic_lecture),
        (FetchData.LECTURE_TYPE_SPECIALIZED, specialized_lecture),
    ],
)
def test_scrape_name_and_url_with_basic(
    start_http_server, fetch_data, lecture_type, contained_data
):
    name_and_url_list = fetch_data.scrape_name_and_url(lecture_type)
    assert contained_data in name_and_url_list


def test_scrape_name_and_url_key_error(start_http_server, fetch_data):
    with pytest.raises(KeyError):
        fetch_data.scrape_name_and_url("key error")


def dummy_init(self, url):
    pass


def test_scrape_lecture(start_http_server, monkeypatch):
    def dummy_scrape_name_and_url(self, lecture):
        return [
            LectureNameUrl(
                name="例",
                url="http://example.com",
            )
        ]

    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    monkeypatch.setattr(FetchData, "scrape_name_and_url", dummy_scrape_name_and_url)
    fetch_data = FetchData("url")

    fetch_data.scrape_lectures([FetchData.LECTURE_TYPE_BASIC])

    assert (
        LectureNameUrl(name="例", url="http://example.com")
        in fetch_data.name_and_url_of_lectures[FetchData.LECTURE_TYPE_BASIC]
    )


def test_scrape_detail_of_lecture(start_http_server, monkeypatch):

    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    fetch_data = FetchData("url")
    detail_url = "http://127.0.0.1:8888/tests/detail_1.html"
    response: requests.Response = requests.get(detail_url)
    detail_lecture_data = fetch_data.scrape_detail_of_lecture(response)
    assert 1 == detail_lecture_data[0].number
    assert "4/22 [2]" == detail_lecture_data[0].date
    assert "スーパスカラとVLIW (日本語教科書８章)" == detail_lecture_data[0].theme


def test_scrape_details(start_http_server, monkeypatch):

    lecture_detail = LectureDetail(
        number=1,
        date="4/22 [2]",
        theme="スーパスカラとVLIW (日本語教科書８章)",
        content="高性能基盤の説明です",
    )

    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    monkeypatch.setattr(
        FetchData,
        "scrape_detail_of_lecture",
        lambda self, response: [lecture_detail],
    )

    detail_url = "http://127.0.0.1:8888/tests/detail_1.html"
    lecture = LectureNameUrl(name="高性能計算基盤", url=detail_url)
    fetch_data = FetchData("url")
    fetch_data.scrape_details([lecture])

    assert lecture_detail in fetch_data.lectures_details["高性能計算基盤"]


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http://127.0.0.1:8888/not_existed_index.html",
        "httpaaaa",
    ],
)
def test_scrape_details_with_invalid_url(start_http_server, monkeypatch, invalid_url):

    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    lecture = LectureNameUrl(name="高性能計算基盤", url=invalid_url)
    fetch_data = FetchData("url")
    with pytest.raises(Exception):
        fetch_data.scrape_details([lecture])


def test_scrape_details_with_not_lecture_name_url(start_http_server, monkeypatch):
    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    detail_url = "http://127.0.0.1:8888/tests/detail_1.html"
    not_instance_of_lecture_name_url = {"name": "高性能計算基盤", "url": detail_url}
    fetch_data = FetchData("url")
    fetch_data.scrape_details(not_instance_of_lecture_name_url)

    assert fetch_data.lectures_details == {}
