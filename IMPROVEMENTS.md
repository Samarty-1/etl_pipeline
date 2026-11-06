# Improvement report

## Selection

Selected `adlerpriit/etl_pipeline` from a GitHub search for small MIT-licensed
Python ETL projects. It had concrete, verifiable problems in both production
functions and test execution. This is not a claim that it is objectively the
worst project on GitHub; no exhaustive ranking was performed.

## Fixed behavior

| Before | After |
| --- | --- |
| CSV extractor printed rows and returned None | Returns rows usable by the transformation stage |
| Tests imported a nonexistent top-level module | Imports resolve from the repository root |
| Standardizer pooled floats across unrelated features | Scales each column independently |
| DataFrame input in the existing test crashed | Supports DataFrames, including nullable integers and duplicate labels |
| Empty, nonnumeric, constant and singleton data could divide by zero | Handles those cases explicitly |
| None crashed numeric conversion; booleans became floats | Preserves missing values and booleans |
| Infinite values silently produced invalid results | Rejects infinity with ValueError |
| Importing the transformer printed unrelated text | Imports are silent |
| README contained only a title; no dependency manifest | Setup instructions, API contract, dependency files and CI workflow |

## Verification

Original `python -m unittest discover -s tests -v`: import error.
After correcting test imports and adding the initial regressions, but before
changing production code: **17 failed, 2 passed**.
After production fixes: **19 passed**.
Final suite, including additional boundary checks: **25 passed**.

Command: `python -m pytest -q --basetemp=.test-tmp-final --tb=short`.
`git diff --check` also passed.

Verified locally on Windows with Python 3.13.15, pandas 3.0.5, NumPy 2.5.2,
and pytest 9.1.1. Tests exercise real temporary CSV files and transformations;
no external services or mocked implementations are involved.
The GitHub Actions matrix is provided but has not been run remotely. Other
versions admitted by the dependency ranges have not been tested locally.

## Delivery and limits

The improvements are prepared on branch `fix/etl-correctness` in the
`Samarty-1/etl_pipeline` fork, based on the original upstream history. No
upstream repository was changed and no pull request was submitted.

Standardization now uses sample standard deviation for both input formats,
matching the existing DataFrame test. This changes the old row-table output.
The utilities still operate in memory and do not implement a loading stage,
train/test fit-transform state, or schema-aware numeric conversion. Very large
numeric magnitudes may exceed floating-point precision or statistical range.
