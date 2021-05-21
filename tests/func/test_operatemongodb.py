import pytest

from src.croning_naist_syllabus.fetch import FetchData
from src.croning_naist_syllabus.operatedb import OperateMongoDB
from tests.test_data import lecture_test_data1, lecture_test_data2, lecture_test_data3

# テストで用いるcollectionの名前
TEST_LECTURE_TYPE = FetchData.LECTURE_TYPE_SPECIALIZED


@pytest.fixture()
def omd_connect_db():
    """
    テストに使用したdatabaseはdropする
    :return:
    """
    omd = OperateMongoDB()

    yield omd

    omd.client.drop_database(omd.database_name)


@pytest.fixture()
def omd_select_collection(omd_connect_db, monkeypatch):
    omd: OperateMongoDB = omd_connect_db

    def dummy_func_select_collection_from_lecture_type(self, lecture_type):
        self.collection = self.database[lecture_type]

    monkeypatch.setattr(
        OperateMongoDB,
        "select_collection_from_lecture_type",
        dummy_func_select_collection_from_lecture_type,
    )
    omd.select_collection_from_lecture_type(TEST_LECTURE_TYPE)

    return omd


@pytest.fixture()
def omd_data_is_set(omd_select_collection, monkeypatch):
    omd: OperateMongoDB = omd_select_collection

    def dummy_func_of_add_lecture_detail(self, lecture_details):
        self.collection.insert_many(lecture_details)

    monkeypatch.setattr(
        OperateMongoDB, "add_lecture_detail", dummy_func_of_add_lecture_detail
    )
    omd.add_lecture_detail([lecture_test_data1])
    return omd


def test_init():
    # 接続エラーが起きないかのテスト
    _ = OperateMongoDB(serverSelectionTimeoutMS=3)


def test_select_collection_from_lecture_type(omd_connect_db):
    omd: OperateMongoDB = omd_connect_db
    omd.select_collection_from_lecture_type(FetchData.LECTURE_TYPE_BASIC)

    assert omd.collection is not None


def test_select_database_from_not_lecture_type(omd_connect_db, caplog):
    """
    存在しないlecture_typeを引数に渡す
    """
    omd: OperateMongoDB = omd_connect_db

    with pytest.raises(SystemExit):
        omd.select_collection_from_lecture_type("not_existed_lecture_type")
    assert (
        "selected lecture_type is not included in FetchData.Lecture_TYPES"
        in caplog.messages
    )


def test_add_lecture_detail(omd_select_collection):
    """
    講義の情報を追加する
    """
    omd: OperateMongoDB = omd_select_collection

    omd.add_lecture_detail([lecture_test_data1])

    assert (
        omd.collection.find_one({"name": lecture_test_data1["name"]})["details"]
        == lecture_test_data1["details"]
    )


def test_add_lecture_detail_without_sellected_collection(
    omd_select_collection, monkeypatch, caplog
):
    """
    collectionが選択されずにadd_lecture_detailを実行
    """
    omd: OperateMongoDB = omd_select_collection

    omd.collection = None

    # 追加されるデータ
    lecture = {
        "name": "高性能計算基盤",
    }

    with pytest.raises(SystemExit):
        omd.add_lecture_detail([lecture])
    assert "collection is not set" in caplog.messages


def test_update_lecture_details(omd_data_is_set, monkeypatch, caplog):
    omd: OperateMongoDB = omd_data_is_set

    # lecture_test_data1はすでにデータに登録されている
    omd.update_lecture_details_with_name([lecture_test_data2, lecture_test_data3])

    assert (
        omd.collection.find_one({"name": lecture_test_data2["name"]})["details"]
        == lecture_test_data2["details"]
    )

    assert omd.collection.find_one({"name": lecture_test_data3["name"]}) is None

    assert "Can't find " + lecture_test_data3["name"] in caplog.messages


def test_get_lecture_details(omd_data_is_set, caplog):
    omd: OperateMongoDB = omd_data_is_set

    details = omd.get_lecture_detail(lecture_test_data1["name"])

    assert details == lecture_test_data1["details"]

    with pytest.raises(SystemExit):
        omd.get_lecture_detail(lecture_test_data3["name"])

    assert lecture_test_data3["name"] + " is not existed in db" in caplog.messages
