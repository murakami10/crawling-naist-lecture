import pytest

from src.crawling_naist_syllabus.operatedb import FetchData, OperateMongoDB
from tests.test_data import lecture_test_data1, lecture_test_data2, lecture_test_data3

TEST_DATABASE_NAME = "test_db"


@pytest.fixture()
def clear_collection():
    """
    テストの前にcollectionを消しておく
    """
    omd = OperateMongoDB(database_name=TEST_DATABASE_NAME)
    omd.select_collection_from_lecture_type(FetchData.LECTURE_TYPE_SPECIALIZED)
    omd.database.drop_collection(FetchData.LECTURE_TYPE_SPECIALIZED)


def test_operaete_mongo_db(clear_collection):
    omd = OperateMongoDB(database_name=TEST_DATABASE_NAME)

    # LECTURE_TYPE_SPECIALIZEDというcollectionを作る
    test_collection = FetchData.LECTURE_TYPE_SPECIALIZED
    omd.select_collection_from_lecture_type(test_collection)

    # レクチャーをDBに登録
    omd.add_lecture([lecture_test_data1, lecture_test_data3])
    assert (
        omd.collection.find_one({"name": lecture_test_data1.name})["name"]
        == lecture_test_data1.name
    )
    assert (
        omd.collection.find_one({"name": lecture_test_data3.name})["name"]
        == lecture_test_data3.name
    )

    # DBをupdateする
    omd.update_lecture_details(lecture_test_data2)
    omd.update_lecture_details(lecture_test_data3)
    assert (
        omd.collection.find_one({"name": lecture_test_data2.name})["details"]
        == lecture_test_data2.details_to_list_of_dict()
    )
    assert (
        omd.collection.find_one({"name": lecture_test_data3.name})["details"]
        == lecture_test_data3.details_to_list_of_dict()
    )

    # レクチャーを1つ取得する
    lecture = omd.load_lecture(
        FetchData.LECTURE_TYPE_SPECIALIZED, lecture_test_data2.name
    )
    assert lecture.name == lecture_test_data2.name
    assert lecture.details == lecture_test_data2.details

    # レクチャーをすべて取得する
    lectures, count = omd.load_lectures_with_lecture_type(test_collection)
    assert count == 2
    for lecture in lectures:
        assert lecture.name in [
            lecture_test_data2.name,
            lecture_test_data3.name,
        ]

        assert lecture.url in [lecture_test_data2.url, lecture_test_data3.url]
