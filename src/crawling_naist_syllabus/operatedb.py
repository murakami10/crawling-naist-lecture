import logging
import os
from typing import List

import pymongo.collection
from dotenv import load_dotenv
from pymongo import MongoClient, common

from .fetch import FetchData
from .structure import Lecture

logger = logging.getLogger(__name__)
load_dotenv()


class OperateMongoDB:
    def __init__(
        self,
        host="127.0.0.1",
        port=int(os.getenv("MONGO_PORT")),
        username=os.getenv("MONGO_INIT_USERNAME"),
        password=os.getenv("MONGO_INIT_PASSWORD"),
        serverSelectionTimeoutMS=common.SERVER_SELECTION_TIMEOUT,
        database_name="lecture_details",
    ):

        self.client = MongoClient(
            host,
            port,
            username=username,
            password=password,
            serverSelectionTimeoutMS=serverSelectionTimeoutMS,
        )

        self.database_name = database_name
        self.database = self.client[self.database_name]

    def select_collection_from_lecture_type(self, lecture_type):

        if lecture_type in FetchData.LECTURE_TYPES:

            self.collection = self.database[lecture_type]

        else:
            logger.error(
                "selected lecture_type is not included in FetchData.Lecture_TYPES"
            )
            exit()

    def add_lecture(self, lecture_details: List[Lecture]):
        """
        授業の情報を追加する
        """
        if self.collection is None:
            logger.error("collection is not set")
            exit()

        for lecture in lecture_details:
            self.collection.insert_one(lecture.get_dict_name_url())

    def update_lecture_details(self, lecture: Lecture):
        """
        lectureのdetailを更新する
        """
        if not isinstance(self.collection, pymongo.collection.Collection):
            logger.error("collection is not set")
            exit()

        update = self.collection.update_one(
            filter={"name": lecture.name},
            update={"$set": {"details": lecture.details_to_list_of_dict()}},
        )
        if update is None:
            logger.warning("Can't find " + lecture.name)

    def load_lecture(self, lecture_type, lecture_name) -> Lecture:
        """
        保存した情報から授業情報をロードする
        """

        self.select_collection_from_lecture_type(lecture_type)
        lecture_name_url: dict = self.collection.find_one({"name": lecture_name})
        if lecture_name_url is None:
            logger.info("not find " + lecture_name)
            return None

        lecture: Lecture = Lecture(lecture_name_url["name"], lecture_name_url["url"])
        if "details" in lecture_name_url.keys():
            lecture.dict_to_lecturedetail(lecture_name_url["details"])

        return lecture

    def load_lectures_with_lecture_type(self, lecture_type) -> (List[Lecture], int):
        """
        保存したデータから授業情報一覧をロードする
        """
        self.select_collection_from_lecture_type(lecture_type)
        lectures = [
            Lecture(lecture["name"], lecture["url"])
            for lecture in self.collection.find()
        ]
        count = self.collection.estimated_document_count()
        return lectures, count
