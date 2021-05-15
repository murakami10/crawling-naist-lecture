import pytest

from src.croning_naist_syllabus.FetchData import FetchData, LectureNameUrl


def test_fetch_data():

    fetch_data = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    fetch_data.scrape_lectures([FetchData.LECTURE_TYPE_SPECIALIZED])

    specialized_lecture = LectureNameUrl(
        name="高性能計算基盤",
        url="https://syllabus.naist.jp/subjects/preview_detail/666",
    )

    assert (
        specialized_lecture
        in fetch_data.name_and_url_of_lectures[FetchData.LECTURE_TYPE_SPECIALIZED]
    )

    fetch_data.scrape_details([specialized_lecture])
    assert 1 == fetch_data.lectures_details[specialized_lecture.name][0].number
    assert "4/22 [2]" == fetch_data.lectures_details[specialized_lecture.name][0].date
    assert (
        "スーパスカラとVLIW (日本語教科書８章)"
        == fetch_data.lectures_details[specialized_lecture.name][0].theme
    )
