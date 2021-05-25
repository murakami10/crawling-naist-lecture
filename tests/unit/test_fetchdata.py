from src.crawling_naist_syllabus.fetch import FetchData, LectureNameUrl


def test_fetch_data():

    fetch_data = FetchData("https://syllabus.naist.jp/subjects/preview_list")

    fetch_data.scrape_lectures([FetchData.LECTURE_TYPE_SPECIALIZED])

    specialized_lectures = [
        LectureNameUrl(
            name="高性能計算基盤",
            url="https://syllabus.naist.jp/subjects/preview_detail/666",
        ),
        LectureNameUrl(
            name="ソフトウェア工学",
            url="https://syllabus.naist.jp/subjects/preview_detail/688",
        ),
    ]

    for specialized_lecture in specialized_lectures:
        assert (
            specialized_lecture
            in fetch_data.name_and_url_of_lectures[FetchData.LECTURE_TYPE_SPECIALIZED]
        )

    details = fetch_data.get_one_lecture_details(specialized_lectures[0].url)

    assert 1 == details[0].number
    assert "4/22 [2]" == details[0].date
    assert "スーパスカラとVLIW (日本語教科書８章)" == details[0].theme
