# csv-cleaner

Cleans messy CSV files so they can be loaded into a database or a DataFrame
without surprises.

## What it does

- Detects the delimiter automatically (`,` `;` `\t` `|`) by counting
  separators in the header row; falls back to comma.
- Strips a UTF-8 BOM and leading/trailing whitespace in every cell.
- Normalizes headers to `snake_case` and makes duplicate names unique
  (`name`, `name_2`, ...).
- Pads short rows with empty cells and truncates long ones to the header width.
- Drops rows that are completely empty.
- Removes exact duplicate rows, keeping the first occurrence
  (disable with `--keep-duplicates`).

## Usage

```bash
python csv_cleaner.py input.csv -o output.csv
python csv_cleaner.py input.csv > output.csv      # data on stdout, report on stderr
python csv_cleaner.py input.csv -o input.csv      # in-place is safe
```

Example:

```bash
$ python csv_cleaner.py messy.csv -o clean.csv
input: 5 rows x 4 columns
output: 3 rows x 4 columns
removed: 2 rows
```

## Behaviour and guarantees

- Output is always comma-separated UTF-8 without BOM, `\n` line endings.
- The whole input is read into memory before the output is opened, so
  writing back to the input path does not lose data.
- Rows longer than the header are truncated silently. This is a cleaner,
  not a validator: it prefers a rectangular result over failing mid-file.
- The delimiter is chosen from the header row only. `csv.Sniffer` was
  rejected because it needs several consistently shaped rows and gives up
  on exactly the ragged files this tool exists to fix.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | success |
| 1 | input file missing, unreadable, or output cannot be written |

## Limitations

- Header-less files are not supported: the first row is always the header.
- Files are processed in memory, so very large inputs are bounded by RAM.
