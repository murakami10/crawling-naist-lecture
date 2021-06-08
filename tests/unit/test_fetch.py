from src.crawling_naist_syllabus.fetch import FetchData
from src.crawling_naist_syllabus.structure import Lecture


def test_fetch():

    fd = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    lectures = fd.scrape_name_and_url(FetchData.LECTURE_TYPE_SPECIALIZED)

    specialized_lectures = [
        Lecture(
            name="高性能計算基盤",
            url="https://syllabus.naist.jp/subjects/preview_detail/666",
        ),
        Lecture(
            name="ソフトウェア工学",
            url="https://syllabus.naist.jp/subjects/preview_detail/688",
        ),
    ]

    for specialized_lecture in specialized_lectures:
        assert specialized_lecture in lectures

    lecture = specialized_lectures[0]
    lecture = fd.scrape_detail(lecture)
    detail = lecture.details[0]

    assert 1 == detail.number
    assert "4/22 [2]" == detail.date
    assert "スーパスカラとVLIW (日本語教科書８章)" == detail.theme
