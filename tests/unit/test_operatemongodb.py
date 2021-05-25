import pytest

from src.crawling_naist_syllabus.operatedb import FetchData, OperateMongoDB
from tests.test_data import lecture_test_data1, lecture_test_data2, lecture_test_data3


@pytest.fixture()
def clear_collection():
    """
    テストの前にcollectionを消しておく
    """
    omd = OperateMongoDB()
    omd.select_collection_from_lecture_type(FetchData.LECTURE_TYPE_SPECIALIZED)
    omd.database.drop_collection(FetchData.LECTURE_TYPE_SPECIALIZED)


def test_operaete_mongo_db(clear_collection):
    omd = OperateMongoDB()

    # LECTURE_TYPE_SPECIALIZEDというcollectionを作る
    omd.select_collection_from_lecture_type(FetchData.LECTURE_TYPE_SPECIALIZED)
    assert omd.collection is not None

    # レクチャーをDBに登録
    omd.add_lecture_detail([lecture_test_data1, lecture_test_data3])
    print(omd.collection.find_one({"name": lecture_test_data1["name"]})["details"])
    print(lecture_test_data1["details"])
    assert (
        omd.collection.find_one({"name": lecture_test_data1["name"]})["details"]
        == lecture_test_data1["details"]
    )
    assert (
        omd.collection.find_one({"name": lecture_test_data3["name"]})["details"]
        == lecture_test_data3["details"]
    )

    # DBをupdateする
    omd.update_lecture_details_with_name([lecture_test_data2])
    assert (
        omd.collection.find_one({"name": lecture_test_data2["name"]})["details"]
        == lecture_test_data2["details"]
    )

    # 指定したレクチャーを取得する
    details = omd.get_lecture_details(lecture_test_data2["name"])
    assert details == lecture_test_data2["details"]

    details = omd.get_lecture_details(lecture_test_data3["name"])
    assert details == lecture_test_data3["details"]
