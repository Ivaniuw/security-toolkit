import pytest

from csv_cleaner import (
    Table,
    clean_table,
    dedupe_header,
    detect_delimiter,
    main,
    normalize_header,
    normalize_row,
    read_table,
)


# --- detect_delimiter: роздільник рахуємо по рядку заголовка ---
@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("a,b,c", ","),
        ("a;b;c", ";"),
        ("a\tb\tc", "\t"),
        ("a|b|c", "|"),
        ("name", ","),  # одна колонка → дефолт
        ("a,b;c,d", ","),  # перемагає найчастіший
        ("a,b;c", ","),  # нічия → пріоритет коми
    ],
)
def test_detect_delimiter(line, expected):
    assert detect_delimiter(line) == expected


# --- normalize_header ---
def test_normalize_header_snake_cases_titles():
    assert normalize_header([" First Name ", "E-mail Address", "(id)"]) == [
        "first_name",
        "e_mail_address",
        "id",
    ]


def test_normalize_header_keeps_unicode_letters():
    assert normalize_header(["Ім'я"]) == ["ім_я"]


# --- dedupe_header ---
def test_dedupe_header_suffixes_repeats():
    assert dedupe_header(["name", "name", "name"]) == ["name", "name_2", "name_3"]


def test_dedupe_header_never_collides_with_existing_suffix():
    result = dedupe_header(["name", "name", "name_2"])
    assert result == ["name", "name_2", "name_2_2"]
    assert len(set(result)) == len(result)


# --- normalize_row ---
def test_normalize_row_strips_and_pads():
    assert normalize_row([" a ", "b"], 3) == ["a", "b", ""]


def test_normalize_row_truncates_extra_cells():
    assert normalize_row(["a", "b", "c"], 2) == ["a", "b"]


# --- clean_table ---
def test_clean_table_drops_blank_and_duplicate_rows():
    table = Table(header=["id", "name"], rows=[["1", "Ann"], ["", "  "], ["1", "Ann"]])
    assert clean_table(table).rows == [["1", "Ann"]]


def test_clean_table_can_keep_duplicates():
    table = Table(header=["id"], rows=[["1"], ["1"]])
    assert clean_table(table, keep_duplicates=True).rows == [["1"], ["1"]]


def test_clean_table_does_not_mutate_input():
    table = Table(header=["name", "name"], rows=[[" x ", "y"]])
    clean_table(table)
    assert table.header == ["name", "name"]
    assert table.rows == [[" x ", "y"]]


# --- read_table ---
def test_read_table_strips_bom_and_detects_semicolon(tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("\ufeffID;Name\n1;Ann\n", encoding="utf-8")
    table = read_table(path)
    assert table.header == ["id", "name"]
    assert table.rows == [["1", "Ann"]]


def test_read_table_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    assert read_table(path) == Table(header=[], rows=[])


# --- main: наскрізні сценарії через CLI ---
MESSY = (
    " ID ;Name; Name ; E-mail Address\n"
    "1;Ann;A.;ann@example.com\n"
    ";  ;;\n"
    "1;Ann;A.;ann@example.com\n"
    "3;Cid\n"
)


def test_main_writes_clean_csv(tmp_path, capsys):
    src = tmp_path / "messy.csv"
    dst = tmp_path / "clean.csv"
    src.write_text(MESSY, encoding="utf-8")

    assert main([str(src), "-o", str(dst)]) == 0

    assert dst.read_text(encoding="utf-8") == (
        "id,name,name_2,e_mail_address\n1,Ann,A.,ann@example.com\n3,Cid,,\n"
    )
    assert "removed: 2 rows" in capsys.readouterr().err


def test_main_writes_to_stdout_by_default(tmp_path, capsys):
    src = tmp_path / "in.csv"
    src.write_text("a,b\n1,2\n", encoding="utf-8")

    assert main([str(src)]) == 0

    captured = capsys.readouterr()
    assert captured.out == "a,b\n1,2\n"
    assert captured.err.startswith("input: 1 rows x 2 columns")


def test_main_missing_input_returns_error(tmp_path, capsys):
    assert main([str(tmp_path / "nope.csv")]) == 1
    assert "no such file" in capsys.readouterr().err


def test_main_unwritable_output_returns_error(tmp_path, capsys):
    src = tmp_path / "in.csv"
    src.write_text("a\n1\n", encoding="utf-8")
    dst = tmp_path / "missing" / "out.csv"

    assert main([str(src), "-o", str(dst)]) == 1
    assert "cannot write" in capsys.readouterr().err


def test_main_in_place_is_safe(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("a,b\n1,2\n1,2\n", encoding="utf-8")

    assert main([str(path), "-o", str(path)]) == 0
    assert path.read_text(encoding="utf-8") == "a,b\n1,2\n"
