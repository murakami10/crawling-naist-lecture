import logging
import os

import pymongo.collection
from dotenv import load_dotenv
from pymongo import MongoClient, common

from .FetchData import FetchData

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
    ):

        self.client = MongoClient(
            host,
            port,
            username=username,
            password=password,
            serverSelectionTimeoutMS=serverSelectionTimeoutMS,
        )

        self.database_name = "lecture_details"
        self.database = self.client[self.database_name]

    def __del__(self):
        self.client.close()

    def select_collection_from_lecture_type(self, lecture_type):

        if lecture_type in FetchData.LECTURE_TYPES:

            self.collection = self.database[lecture_type]

        else:
            logger.error(
                "selected lecture_type is not included in FetchData.Lecture_TYPES"
            )
            exit()

    def add_lecture_detail(self, lecture_details: list):
        if isinstance(self.collection, pymongo.collection.Collection):
            self.collection.insert_many(lecture_details)
        else:
            logger.error("collection is not set")
            exit()

    def update_lecture_details(self, lecture_details: list):
        """
        lectureのdetailを更新する
        """
        if not isinstance(self.collection, pymongo.collection.Collection):
            logger.error("collection is not set")
            exit()

        for lecture_detail in lecture_details:
            update = self.collection.find_one_and_update(
                filter={"name": lecture_detail["name"]},
                update={"$set": {"details": lecture_detail["details"]}},
            )
            if update is None:
                logger.warning("Can't find " + lecture_detail["name"])

    def get_lecture_detail(self, lecture_type, lecture_name):

        self.select_collection_from_lecture_type(lecture_type)

        lecture = self.collection.find_one({"name": lecture_name})
        if lecture is None:
            logger.error(lecture_name + " is not existed in db")
            exit()
        return lecture["details"]
