import pytest

from src.crawling_naist_syllabus.control import load_data, load_details_data
from src.crawling_naist_syllabus.fetch import FetchData
from src.crawling_naist_syllabus.operatedb import OperateMongoDB

TEST_DATABASE_NAME = "test_db"
TEST_LECTURE_TYPE = FetchData.LECTURE_TYPE_SPECIALIZED
TEST_LECTURE_NAME = "高性能計算基盤"


@pytest.fixture()
def prepare_omd_and_fd():
    omd = OperateMongoDB(database_name=TEST_DATABASE_NAME)
    omd.select_collection_from_lecture_type(TEST_LECTURE_TYPE)
    fd = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    yield (omd, fd)

    omd.client.drop_database(TEST_DATABASE_NAME)


def test_load_data(prepare_omd_and_fd):
    omd, fd = prepare_omd_and_fd

    lectures = load_data(TEST_LECTURE_TYPE, omd, fd)
    fail_flag = True
    for lecture in lectures:
        if (
            lecture["name"] == "高性能計算基盤"
            and lecture["url"]
            == "https://syllabus.naist.jp/subjects/preview_detail/666"
        ):
            fail_flag = False

    if fail_flag:
        pytest.fail("can't scrape lecture name and url")


def test_load_details_data(prepare_omd_and_fd):
    omd, fd = prepare_omd_and_fd

    _ = load_data(TEST_LECTURE_TYPE, omd, fd)
    details = load_details_data(TEST_LECTURE_TYPE, TEST_LECTURE_NAME, omd, fd, False)
    assert details[0].number == 1
    assert details[0].date == "4/22 [2]"
    assert details[0].theme == "スーパスカラとVLIW (日本語教科書８章)"
