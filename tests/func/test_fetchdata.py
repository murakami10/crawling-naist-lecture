import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
import requests

from src.crawling_naist_syllabus.fetch import FetchData
from src.crawling_naist_syllabus.structure import Lecture


@pytest.fixture(scope="session")
def fetch_and_save_syllabus_html(tmpdir_factory):
    """
    naistのシラバスを取得し、一時ディレクトリに保存する
    :return syllabus.htmlが存在するdirectoryを返す
    """
    syllabus_directory = tmpdir_factory.mktemp("syllabus_directory")

    response = requests.get("https://syllabus.naist.jp/subjects/preview_list")
    syllabus_file = syllabus_directory.join("syllabus.html")
    syllabus_file.write(response.content)

    # 実際のサイトにスクレイピングするため、アクセスの間隔をあける
    time.sleep(1)

    response = requests.get("https://syllabus.naist.jp/subjects/preview_detail/666")
    detail_file = syllabus_directory.join("detail_1.html")
    detail_file.write(response.content)

    return syllabus_file.dirpath()


@pytest.fixture(scope="session")
def start_http_server():
    """
    現在のdirectory配下を公開する
    """
    host, port = ("127.0.0.1", 8888)
    url = f"http://{host}:{port}/tests/index.html"
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    thred = threading.Thread(target=server.serve_forever)
    thred.start()
    yield url
    server.shutdown()
    thred.join()


@pytest.fixture(scope="session")
def start_http_server_with_specific_directory(fetch_and_save_syllabus_html):
    """
    指定したdirectoryをlocalhostで公開する
    :param fetch_and_save_syllabus_html 公開するdirectory
    """

    class HandlerWithDirectory(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            """
            指定したdirectoryを公開
            """
            super().__init__(*args, directory=fetch_and_save_syllabus_html, **kwargs)

    host, port = ("127.0.0.1", 8889)
    server = HTTPServer((host, port), HandlerWithDirectory)
    url = f"http://{host}:{port}/"
    # スレッドの起動
    thred = threading.Thread(target=server.serve_forever)
    thred.start()
    yield url
    server.shutdown()
    thred.join()


@pytest.fixture()
def fetch_data(start_http_server_with_specific_directory):
    """
    FetchDataのインスタンスを返す
    """
    fd = FetchData(start_http_server_with_specific_directory + "syllabus.html")
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
    try:
        _ = FetchData(start_http_server)
    except Exception:
        pytest.fail("Exception raised")


general_lecture = Lecture(
    name="技術と倫理",
    url="http://127.0.0.1:8889/subjects/preview_detail/644",
)
introduction_lecture = Lecture(
    name="情報理工学序論",
    url="http://127.0.0.1:8889/subjects/preview_detail/662",
)
basic_lecture = Lecture(
    name="情報科学基礎Ⅰ",
    url="http://127.0.0.1:8889/subjects/preview_detail/791",
)
specialized_lecture = Lecture(
    name="ソフトウェア工学",
    url="http://127.0.0.1:8889/subjects/preview_detail/688",
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
def test_scrape_name_and_url(fetch_data, lecture_type, contained_data):
    name_and_url_list = fetch_data.scrape_name_and_url(lecture_type)
    assert contained_data in name_and_url_list


def test_scrape_name_and_url_key_error(fetch_data):
    with pytest.raises(KeyError):
        fetch_data.scrape_name_and_url("key error")


def dummy_init(self, url):
    pass


def test_scrape_detail_of_lecture(
    start_http_server_with_specific_directory, monkeypatch
):

    monkeypatch.setattr(FetchData, "__init__", dummy_init)
    fetch_data = FetchData("url")
    detail_url = start_http_server_with_specific_directory + "/detail_1.html"
    lecture = Lecture(name="高性能計算基盤", url=detail_url)
    lecture = fetch_data.scrape_detail(lecture)
    assert 1 == lecture.details[0].number
    assert "4/22 [2]" == lecture.details[0].date
    assert "スーパスカラとVLIW (日本語教科書８章)" == lecture.details[0].theme
