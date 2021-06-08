import pytest

from src.crawling_naist_syllabus.control import load_details, load_lectures
from src.crawling_naist_syllabus.fetch import FetchData
from src.crawling_naist_syllabus.operatedb import OperateMongoDB
from tests.test_data import lecture_test_data2, lecture_test_data3

TEST_DATABASE_NAME = "test_db"
TEST_LECTURE_TYPE = FetchData.LECTURE_TYPE_SPECIALIZED
TEST_LECTURE_NAME = "高性能計算基盤"


@pytest.fixture()
def prepare_fd_and_omd():
    omd = OperateMongoDB(database_name=TEST_DATABASE_NAME)
    omd.client.drop_database(TEST_DATABASE_NAME)
    omd.select_collection_from_lecture_type(TEST_LECTURE_TYPE)
    fd = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    return (fd, omd)


@pytest.fixture()
def prepare_fd_and_omd_with_data():
    """
    databaseにデータが登録済みのomdを渡す
    """

    omd = OperateMongoDB(database_name=TEST_DATABASE_NAME)
    omd.client.drop_database(TEST_DATABASE_NAME)
    omd.select_collection_from_lecture_type(TEST_LECTURE_TYPE)

    # omdにデータをset
    omd.add_lecture([lecture_test_data2, lecture_test_data3])
    omd.update_lecture_details(lecture_test_data2)
    omd.update_lecture_details(lecture_test_data3)

    fd = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    return (fd, omd)


def test_load_lectures(prepare_fd_and_omd):
    fd, omd = prepare_fd_and_omd

    # count == 0 のとき授業情報が登録されていない
    _, count = omd.load_lectures_with_lecture_type(TEST_LECTURE_TYPE)
    assert count == 0

    lectures = load_lectures(TEST_LECTURE_TYPE, omd, fd)
    fail_flag = True
    for lecture in lectures:
        if lecture.name == "高性能計算基盤" and (
            lecture.url == "https://syllabus.naist.jp/subjects/preview_detail/666"
        ):
            fail_flag = False

    if fail_flag:
        pytest.fail("can't scrape lecture name and url")


def test_load_lectures_with_data_registered(prepare_fd_and_omd_with_data, monkeypatch):
    """
    databaseにデータが登録されているとしてload_dataをテストする
    """
    fd, omd = prepare_fd_and_omd_with_data

    # count != 0 のとき授業情報が登録されている
    _, count = omd.load_lectures_with_lecture_type(TEST_LECTURE_TYPE)
    assert count != 0

    lectures = load_lectures(TEST_LECTURE_TYPE, omd, fd)
    fail_flag = True
    for lecture in lectures:
        if (
            lecture.name == lecture_test_data2.name
            and lecture.url == lecture_test_data2.url
        ):
            fail_flag = False

    if fail_flag:
        pytest.fail("can't load lecture name and url")


def test_load_details(prepare_fd_and_omd):
    fd, omd = prepare_fd_and_omd

    _ = load_lectures(TEST_LECTURE_TYPE, omd, fd)
    # 授業情報の詳細が登録されているか調べる(lecture.details is None だと登録されていない)
    lecture = omd.load_lecture(TEST_LECTURE_TYPE, TEST_LECTURE_NAME)
    assert lecture.details is None

    details = load_details(TEST_LECTURE_TYPE, TEST_LECTURE_NAME, omd, fd)
    assert details[0].number == 1
    assert details[0].date == "4/22 [2]"
    assert details[0].theme == "スーパスカラとVLIW (日本語教科書８章)"


def test_load_details_wiht_data_registered(prepare_fd_and_omd_with_data):
    """
    授業の詳細情報が登録されている状態でload_detailsをテストする
    """
    fd, omd = prepare_fd_and_omd_with_data

    # 授業情報の詳細が登録されているか調べる(lecture.details is not None だと登録されている)
    lecture = omd.load_lecture(TEST_LECTURE_TYPE, TEST_LECTURE_NAME)
    assert lecture.details is not None

    details = load_details(TEST_LECTURE_TYPE, TEST_LECTURE_NAME, omd, fd)
    assert details[0].number == 1
    assert details[0].date == "4/22 [2]"
    assert details[0].theme == "スーパスカラとVLIW (日本語教科書８章)"
