import pytest

from src.crawling_naist_syllabus.structure import Lecture, LectureDetail


@pytest.fixture()
def lecture_init():
    name = "test"
    url = "https://www.google.com"
    details = [
        LectureDetail(
            1,
            "4/22 [2]",
            "スーパスカラとVLIW (日本語教科書８章)",
            "高性能基盤の説明です",
        ),
        LectureDetail(
            2,
            "5/13 [2]",
            "ベクトル型アクセラレータとGPU (日本語教科書９章)",
            "さらに並列度を向上させる大規模計算の仕組み",
        ),
    ]

    lecture = Lecture(name=name, url=url, details=details)
    return (lecture, name, url, details)


def test_get_dict_name_url(lecture_init):
    lecture, name, url, _ = lecture_init
    assert lecture.get_dict_name_url() == {"name": name, "url": url}


def test_details_to_list_of_dict(lecture_init):
    lecture, _, _, details = lecture_init
    detail_list = lecture.details_to_list_of_dict()
    for index, detail in enumerate(detail_list):
        assert detail["number"] == details[index].number
        assert detail["date"] == details[index].date
        assert detail["theme"] == details[index].theme
        assert detail["content"] == details[index].content


def test_dict_to_lecturedetail():
    name = "test"
    url = "https://www.google.com"
    lecture = Lecture(name, url)
    test_dict = [
        {
            "number": "1",
            "date": "4/22 [2]",
            "theme": "スーパスカラとVLIW (日本語教科書８章)",
            "content": "高性能基盤の説明です",
        }
    ]
    lecture.dict_to_lecturedetail(test_dict)
    lecture_details_0 = lecture.details[0]
    test_0 = test_dict[0]

    assert lecture_details_0.number == test_0["number"]
    assert lecture_details_0.date == test_0["date"]
    assert lecture_details_0.theme == test_0["theme"]
    assert lecture_details_0.content == test_0["content"]
