import logging
from typing import List

from .fetch import FetchData
from .operatedb import OperateMongoDB
from .structure import LectureDetail

logger = logging.getLogger(__name__)


def load_data(lecture_type, omd: OperateMongoDB, fd: FetchData):
    """
    授業データをDBから取り出す。データが無ければrequestを送り取得、保存する
    """
    lectures, count = omd.load_lectures_with_lecture_type(lecture_type)

    if count == 0:
        # 授業情報が登録されていない
        lectures = fd.scrape_name_and_url(lecture_type)
        omd.add_lecture(lectures)

    logger.debug(lectures)

    return lectures


def load_details(
    checked_lecture_type,
    lecture_name,
    omd: OperateMongoDB,
    fd: FetchData,
    refetch=False,
) -> List[LectureDetail]:
    """
    授業の詳細データをDBから取得する。なければrequestを送り取得、保存する
    """

    lecture = omd.load_lecture(checked_lecture_type, lecture_name)

    if lecture.details is not None and not refetch:
        return lecture.details

    lecture = fd.scrape_detail(lecture)
    omd.update_lecture_details(lecture)

    return lecture.details
