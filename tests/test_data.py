from src.crawling_naist_syllabus.fetch import Lecture, LectureDetail

lecture_test_data1 = Lecture(
    name="高性能計算基盤",
    url="dummy_http",
    details=[
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
    ],
)

# lecture_test_data1のdetailに一つ辞書を追加
lecture_test_data2 = Lecture(
    name="高性能計算基盤",
    url="dummy_http",
    details=[
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
        LectureDetail(
            3,
            "5/20 [2]",
            "FPGA (Field Programmable Gate Array)",
            "大量の演算器を制御する方法とは",
        ),
    ],
)
lecture_test_data3 = Lecture(
    name="ソフトウェア工学",
    url="http_dummy2",
    details=[
        LectureDetail(
            1,
            "4/26 [1]",
            "概論",
            "ソフトウェア開発の現状と課題",
        ),
        LectureDetail(
            2,
            "5/10 [2]",
            "ソフトウェアの信頼性",
            "ソフトウェアテスト、コードカバレッジ、ソフトウェアメトリクス",
        ),
    ],
)
