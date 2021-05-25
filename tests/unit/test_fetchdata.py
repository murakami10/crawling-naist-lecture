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

    fetch_data.scrape_details(specialized_lectures)

    assert 1 == fetch_data.lecture_details[specialized_lectures[0].name][0].number
    assert (
        "4/22 [2]" == fetch_data.lecture_details[specialized_lectures[0].name][0].date
    )
    assert (
        "スーパスカラとVLIW (日本語教科書８章)"
        == fetch_data.lecture_details[specialized_lectures[0].name][0].theme
    )

    assert 1 == fetch_data.lecture_details[specialized_lectures[1].name][0].number
    assert (
        "4/26 [2]" == fetch_data.lecture_details[specialized_lectures[1].name][0].date
    )
    assert "概論" == fetch_data.lecture_details[specialized_lectures[1].name][0].theme
