import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest

from src.croning_naist_syllabus.FetchData import FetchData


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
