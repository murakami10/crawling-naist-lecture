import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
import requests

from src.croning_naist_syllabus.FetchData import FetchData


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
    detail_file = syllabus_directory.join("subjects/preview_detail/666.html")
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
