# ETL pipeline: CSV extraction and data transformation

Small in-memory Python utilities for reading CSV files, converting numeric
strings, and standardizing numeric columns. Originally published by
[Priit Adler](https://github.com/adlerpriit/etl_pipeline) under the MIT license.

## Setup and tests

Python 3.11 or newer:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Run commands from the repository root. Runtime-only installations can use
`requirements.txt`. If your environment restricts the system temporary folder,
run tests with `python -m pytest -q --basetemp=.test-tmp` instead. Pytest clears
its specified base temporary directory, so use a dedicated disposable path.

## Example

```python
from extract.csv_extractor import extract_data
from transform.data_transformer import transform_data, standardize_data

# input.csv:
# name,age,weight
# Alice,20,50
# Bob,30,70
# Charlie,40,90
rows = extract_data('input.csv')
result = standardize_data(transform_data(rows))
print(result)
# [['name', 'age', 'weight'],
#  ['Alice', -1.0, -1.0], ['Bob', 0.0, 0.0], ['Charlie', 1.0, 1.0]]
```

`standardize_data` also accepts pandas DataFrames and returns a new DataFrame
with the same index and column labels. Input objects are not mutated.

## Data contract

- CSV extraction returns rows including the header; it supports UTF-8 with or
  without a BOM, quoted delimiters and embedded newlines. Errors propagate.
- Numeric conversion operates on every cell, retaining text, missing values
  and booleans. Numeric-looking identifiers (including column names) become
  floats, so apply conversion only when that is appropriate for your schema.
- Row-table standardization expects a rectangular table whose first row is a
  header. Numeric strings must be converted first. DataFrame standardization
  processes integer and floating-point columns; object and complex columns
  remain unchanged.
- Each column uses `(x - mean) / sample_std`, with `ddof=1`, matching pandas'
  default standard deviation. This corrects the previous behavior that pooled
  unrelated columns and used population standard deviation.
- Missing observations are excluded from statistics and remain missing.
  Constant columns and single observations become zero. Text and booleans
  are preserved. Infinite numeric values and ragged tables raise `ValueError`.
- These functions load data into memory. They provide extraction and
  transformation utilities, not a database loader or a production scheduler.
  For predictive modeling, fit scaling statistics on training data only;
  this function recomputes statistics for each call.

## Improvement provenance

Source snapshot: upstream commit `7de87058bf7ef6ce487150173e964261bd228c78`.
The improvements were initially developed against a source snapshot retrieved
through the GitHub connector. They were then transferred onto an upstream Git
clone, preserving the original project history, for publication in the
[Samarty-1 fork](https://github.com/Samarty-1/etl_pipeline/tree/fix/etl-correctness).

The original tests failed to import their module. After correcting imports,
the regression suite demonstrated 17 failures and 2 passes before fixes.
See `IMPROVEMENTS.md` for the final verification and scope.
