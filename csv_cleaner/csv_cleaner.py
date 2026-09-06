"""Clean messy CSV files: trim whitespace, drop empty rows, remove duplicates."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

EXIT_OK = 0
EXIT_ERROR = 1
DELIMITERS = ",;\t|"
_NON_WORD = re.compile(r"[^\w]+")


@dataclass(frozen=True)
class Table:
    """A parsed CSV file: one header row plus the data rows."""

    header: list[str]
    rows: list[list[str]]


def normalize_header(fields: Iterable[str]) -> list[str]:
    """Turn arbitrary column titles into snake_case identifiers."""
    return [_NON_WORD.sub("_", field.strip().lower()).strip("_") for field in fields]


def detect_delimiter(line: str) -> str:
    """Return the candidate delimiter that occurs most often in *line*.

    The header row is the most reliable line in a CSV file, so counting
    separators there beats csv.Sniffer, which needs several consistently
    shaped rows and gives up on ragged data.
    """
    counts = {sep: line.count(sep) for sep in DELIMITERS}
    best = max(DELIMITERS, key=lambda sep: counts[sep])
    return best if counts[best] else ","


def read_table(path: Path, encoding: str = "utf-8-sig") -> Table:
    """Read *path* into a Table, detecting its delimiter from the header."""
    with path.open("r", encoding=encoding, newline="") as handle:
        delimiter = detect_delimiter(handle.readline())
        handle.seek(0)
        reader = csv.reader(handle, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            return Table(header=[], rows=[])
        return Table(header=normalize_header(header), rows=list(reader))


def dedupe_header(fields: Iterable[str]) -> list[str]:
    """Make column names unique: name, name_2, name_3."""
    seen: set[str] = set()
    result: list[str] = []
    for field in fields:
        candidate, n = field, 1
        while candidate in seen:
            n += 1
            candidate = f"{field}_{n}"
        seen.add(candidate)
        result.append(candidate)
    return result


def normalize_row(row: Sequence[str], width: int) -> list[str]:
    """Strip every cell and force *row* to exactly *width* columns."""
    cells = [cell.strip() for cell in row[:width]]
    cells.extend([""] * (width - len(cells)))
    return cells


def is_blank(row: Sequence[str]) -> bool:
    """True if every cell in *row* is empty."""
    return not any(row)


def unique(rows: Iterable[list[str]]) -> Iterator[list[str]]:
    """Yield rows in original order, skipping exact repeats."""
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            yield row


def clean_table(table: Table, *, keep_duplicates: bool = False) -> Table:
    """Return a cleaned copy of *table*; the input is left untouched."""
    header = dedupe_header(table.header)
    width = len(header)

    rows: Iterator[list[str]] = (normalize_row(row, width) for row in table.rows)
    rows = (row for row in rows if not is_blank(row))
    if not keep_duplicates:
        rows = unique(rows)

    return Table(header=header, rows=list(rows))


@contextmanager
def open_output(path: Path | None) -> Iterator[TextIO]:
    """Yield a writable text stream: *path* if given, otherwise stdout."""
    if path is None:
        yield sys.stdout
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        yield handle


def write_table(table: Table, stream: TextIO) -> None:
    """Write *table* as comma-separated CSV with a header row."""
    if not table.header:
        return
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(table.header)
    writer.writerows(table.rows)


def describe(label: str, table: Table) -> str:
    """One-line summary of a table's shape for the report."""
    return f"{label}: {len(table.rows)} rows x {len(table.header)} columns"


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line interface."""
    parser = argparse.ArgumentParser(
        prog="csv-cleaner",
        description=__doc__,
    )
    parser.add_argument("input", type=Path, help="path to the input CSV file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="path to the output CSV file (default: stdout)",
    )
    parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="do not remove duplicate rows",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)

    if not args.input.is_file():
        print(f"error: no such file: {args.input}", file=sys.stderr)
        return EXIT_ERROR

    try:
        table = read_table(args.input)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    cleaned = clean_table(table, keep_duplicates=args.keep_duplicates)

    try:
        with open_output(args.output) as stream:
            write_table(cleaned, stream)
    except OSError as exc:
        print(f"error: cannot write {args.output}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    print(describe("input", table), file=sys.stderr)
    print(describe("output", cleaned), file=sys.stderr)
    print(f"removed: {len(table.rows) - len(cleaned.rows)} rows", file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
