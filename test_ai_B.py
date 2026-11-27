import pytest

from load_scores import load_scores


def test_load_scores_accepts_trimmed_header_and_valid_boundary_scores(tmp_path):
    csv_path = tmp_path / "scores.csv"
    csv_path.write_text(
        "  name , score  \n"
        " 민수 , 0 \n"
        "영희,100\n",
        encoding="utf-8",
        newline="",
    )

    kept, skipped = load_scores(csv_path)

    assert kept == [("민수", 0), ("영희", 100)]
    assert skipped == []


def test_load_scores_returns_empty_results_for_header_only_file(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("name,score\n", encoding="utf-8")

    assert load_scores(csv_path) == ([], [])


def test_load_scores_rejects_header_with_wrong_names_or_order(tmp_path):
    csv_path = tmp_path / "wrong_header.csv"
    csv_path.write_text("name,grade\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_scores(csv_path)


def test_load_scores_reports_invalid_rows_and_keeps_later_valid_duplicate(
    tmp_path,
):
    csv_path = tmp_path / "mixed.csv"
    csv_path.write_text(
        "name,score\n"
        "\n"
        "서한별,\n"
        "서한별,88\n"
        "김하나,88\n"
        "김하나,91\n"
        "민수,abc\n"
        "영희,-1\n"
        "지수,101\n"
        ",90\n"
        "철수,75,extra\n"
        "다현,80\n",
        encoding="utf-8",
        newline="",
    )

    kept, skipped = load_scores(csv_path)

    assert kept == [("서한별", 88), ("김하나", 88), ("다현", 80)]
    assert [(line_no, original) for line_no, original, _ in skipped] == [
        (2, ""),
        (3, "서한별,"),
        (6, "김하나,91"),
        (7, "민수,abc"),
        (8, "영희,-1"),
        (9, "지수,101"),
        (10, ",90"),
        (11, "철수,75,extra"),
    ]
    assert [reason for _, _, reason in skipped] == [
        "빈 줄",
        "이름 또는 점수가 비어 있음",
        "중복된 이름",
        "점수가 정수가 아님",
        "점수가 0~100 범위를 벗어남",
        "점수가 0~100 범위를 벗어남",
        "이름 또는 점수가 비어 있음",
        "열 개수가 2개가 아님",
    ]


def test_load_scores_raises_file_not_found_error_with_missing_path(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError) as error:
        load_scores(missing_path)

    assert (
        error.value.filename == str(missing_path)
        or str(missing_path) in str(error.value)
    )


def test_load_scores_rejects_directory_as_input_path(tmp_path):
    directory_path = tmp_path / "scores"
    directory_path.mkdir()

    with pytest.raises(FileNotFoundError) as error:
        load_scores(directory_path)

    assert (
        error.value.filename == str(directory_path)
        or str(directory_path) in str(error.value)
    )