import dataclasses
from typing import List, NamedTuple


class LectureDetail(NamedTuple):
    number: int
    date: str
    theme: str
    content: str


@dataclasses.dataclass
class Lecture:
    name: str
    url: str
    details: List[LectureDetail] = None

    def get_dict_name_url(self):
        return {"name": self.name, "url": self.url}

    def details_to_list_of_dict(self):
        detail_list = []
        for detail in self.details:
            detail_list.append(dict(detail._asdict()))
        return detail_list

    def dict_to_lecturedetail(self, dict_list: List[dict]) -> List[LectureDetail]:
        self.details = []
        for dic in dict_list:
            self.details.append(LectureDetail(**dic))
