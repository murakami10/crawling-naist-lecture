import pytest

from src.crawling_naist_syllabus.fetch import FetchData
from src.crawling_naist_syllabus.operatedb import OperateMongoDB
from tests.test_data import (lecture_test_data1, lecture_test_data2,
                             lecture_test_data3)

# テストで用いるcollectionの名前
TEST_LECTURE_TYPE = FetchData.LECTURE_TYPE_SPECIALIZED


# select_collection_from_typeをスタブする
def set_attr_to_select_collection_from_lecture_type(monkeypatch):
    def dummy_func_select_collection_from_lecture_type(self, lecture_type):
        self.collection = self.database[lecture_type]

    monkeypatch.setattr(
        OperateMongoDB,
        "select_collection_from_lecture_type",
        dummy_func_select_collection_from_lecture_type,
    )


@pytest.fixture()
def omd_connect_db(monkeypatch):
    """
    テストに使用したdatabaseはdropする
    :return:
    """
    omd = OperateMongoDB(database_name="test")

    yield omd

    omd.client.drop_database("test")


@pytest.fixture()
def omd_select_collection(omd_connect_db, monkeypatch):
    omd: OperateMongoDB = omd_connect_db

    set_attr_to_select_collection_from_lecture_type(monkeypatch)
    omd.select_collection_from_lecture_type(TEST_LECTURE_TYPE)
    return omd


@pytest.fixture()
def omd_with_one_document(omd_select_collection, monkeypatch):
    """
    ドキュメント１つ追加したOperateMongoDBのinstanceを返す
    """
    omd: OperateMongoDB = omd_select_collection

    def dummy_func_of_add_lecture(self, lecture_details):
        self.collection.insert_many(lecture_details)

    monkeypatch.setattr(OperateMongoDB, "add_lecture", dummy_func_of_add_lecture)
    omd.add_lecture([lecture_test_data1.get_dict_name_url()])
    return omd


@pytest.fixture()
def omd_with_two_document(omd_select_collection, monkeypatch):
    """
    ドキュメント１つ追加したOperateMongoDBのinstanceを返す
    """
    omd: OperateMongoDB = omd_select_collection

    def dummy_func_of_add_lecture_detail(self, lecture_details):
        self.collection.insert_many(lecture_details)

    monkeypatch.setattr(OperateMongoDB, "add_lecture", dummy_func_of_add_lecture_detail)
    omd.add_lecture(
        [lecture_test_data1.get_dict_name_url(), lecture_test_data3.get_dict_name_url()]
    )
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


def test_add_lecture(omd_select_collection):
    """
    講義の情報を追加する
    """
    omd: OperateMongoDB = omd_select_collection

    omd.add_lecture([lecture_test_data1])

    lecture_from_db = omd.collection.find_one({"name": lecture_test_data1.name})

    assert lecture_from_db["name"] == lecture_test_data1.name
    assert lecture_from_db["url"] == lecture_test_data1.url


def test_add_lecture_without_sellected_collection(
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
        omd.add_lecture([lecture])
    assert "collection is not set" in caplog.messages


def test_update_lecture_details(omd_with_one_document, monkeypatch):
    omd: OperateMongoDB = omd_with_one_document

    omd.update_lecture_details(lecture_test_data2)

    details = omd.collection.find_one({"name": lecture_test_data2.name})["details"]

    for detail, test_data in zip(details, lecture_test_data2.details):
        assert detail["number"] == test_data.number
        assert detail["date"] == test_data.date
        assert detail["theme"] == test_data.theme
        assert detail["content"] == test_data.content


def test_load_lecture(omd_with_one_document, monkeypatch):

    omd: OperateMongoDB = omd_with_one_document
    set_attr_to_select_collection_from_lecture_type(monkeypatch)

    # dbのdetailsにlecture_test_data2のdetails情報を追加
    omd.update_lecture_details(lecture_test_data2)

    lecture = omd.load_lecture(TEST_LECTURE_TYPE, lecture_test_data1.name)

    assert lecture == lecture_test_data2


def test_load_lecture_without_lecture(omd_with_one_document, monkeypatch):
    """
    登録されている授業なしでloadする
    """

    omd: OperateMongoDB = omd_with_one_document
    set_attr_to_select_collection_from_lecture_type(monkeypatch)

    lecture = omd.load_lecture(TEST_LECTURE_TYPE, lecture_test_data3.name)
    assert lecture == None


def test_load_all_lectures(omd_with_two_document, monkeypatch):
    omd: OperateMongoDB = omd_with_two_document

    set_attr_to_select_collection_from_lecture_type(monkeypatch)

    lectures, count = omd.load_lectures_with_lecture_type(TEST_LECTURE_TYPE)
    for lecture in lectures:
        assert lecture.name in [
            lecture_test_data1.name,
            lecture_test_data3.name,
        ]

    assert count == 2
