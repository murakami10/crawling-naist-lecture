from .fetch import FetchData
from .operatedb import OperateMongoDB


def load_data(lecture_type, omd: OperateMongoDB, fd: FetchData):
    """
    授業データをDBから取り出す。データが無ければrequestを送り取得、保存する
    """
    count = omd.count_lecture(lecture_type)

    if count == 0:
        fd.scrape_lectures([lecture_type])

        for lecture_type, names_and_urls in fd.name_and_url_of_lectures.items():

            for name_and_url in names_and_urls:
                omd.add_lecture_detail(
                    [{"name": name_and_url.name, "url": name_and_url.url}]
                )

    lectures = omd.get_all_lectures(lecture_type)

    return lectures


def load_details_data(
    checked_lecture_type, lecture_name, refetch, omd: OperateMongoDB, fd: FetchData
):
    """
    授業の詳細データをDBから取得する。なければrequestを送り取得、保存する
    """

    lecture = omd.get_lecture(checked_lecture_type, lecture_name)

    if "details" in lecture.keys() and not refetch:
        return lecture["details"]

    details = fd.scrape_one_details(lecture["url"])
    lecture_details = {
        "name": lecture_name,
        "details": details,
    }
    omd.update_lecture_details_with_name([lecture_details])

    return details
