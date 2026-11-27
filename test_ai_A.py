import pytest

from load_scores import load_scores


def test_load_scores_keeps_trimmed_names_and_inclusive_boundary_scores(tmp_path):
    csv_path = tmp_path / "scores.csv"
    csv_path.write_text(
        "\ufeffname,score\n"
        "  민수  , 0 \n"
        "영희,100\n"
        "민수,75\n",
        encoding="utf-8",
        newline="",
    )

    kept, skipped = load_scores(csv_path)

    assert kept == [("민수", 0), ("영희", 100), ("민수", 75)]
    assert skipped == []


def test_load_scores_returns_empty_lists_for_header_only_file(tmp_path):
    csv_path = tmp_path / "scores.csv"
    csv_path.write_text("name,score\n", encoding="utf-8")

    assert load_scores(csv_path) == ([], [])


def test_load_scores_records_invalid_rows_and_ignores_blank_lines(tmp_path):
    csv_path = tmp_path / "scores.csv"
    csv_path.write_text(
        "name,score\n"
        "\n"
        "민수\n"
        ",80\n"
        "영희,\n"
        "철수,abc\n"
        "지수,-1\n"
        "준호,101\n"
        "유나,90,extra\n"
        "다현,80\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_path)

    assert kept == [("다현", 80)]
    assert skipped == [
        (3, "민수", "열 개수가 2가 아님"),
        (4, ",80", "이름이 비어 있음"),
        (5, "영희,", "점수가 비어 있음"),
        (6, "철수,abc", "점수가 정수가 아님"),
        (7, "지수,-1", "점수가 0~100 밖"),
        (8, "준호,101", "점수가 0~100 밖"),
        (9, "유나,90,extra", "열 개수가 2가 아님"),
    ]


def test_load_scores_propagates_file_not_found_error(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing_path)