"""Conversion and per-column standardization for small in-memory datasets."""

from numbers import Real

import numpy as np
import pandas as pd


def transform_data(data):
    """Return new rows with numeric values converted to floats.

    Text, missing values and booleans are preserved. This function treats
    every row equally; numeric column names should be supplied separately.
    """
    transformed = []
    for row in data:
        converted = []
        for value in row:
            if value is None or value is pd.NA or isinstance(value, (bool, np.bool_)):
                converted.append(value)
                continue
            try:
                converted.append(float(value))
            except (TypeError, ValueError):
                converted.append(value)
        transformed.append(converted)
    return transformed


def _standardize_column(column):
    """Scale finite observations using sample standard deviation (ddof=1)."""
    values = column.astype('float64')
    if np.isinf(values).any():
        raise ValueError('Cannot standardize infinite values')
    present = values.notna()
    if present.sum() < 2 or values[present].nunique() == 1:
        values.loc[present] = 0.0
        return values
    return (values - values.mean()) / values.std(ddof=1)


def standardize_data(data):
    """Return a standardized copy of a DataFrame or header-first row table.

    Scale each numeric column independently using sample standard deviation.
    Missing observations do not contribute to statistics and remain missing.
    Constant and singleton numeric columns become zero; text and booleans
    stay unchanged. Infinite values and ragged row tables raise ValueError.
    For row tables, convert numeric strings with transform_data first.
    """
    if isinstance(data, pd.DataFrame):
        result = data.copy(deep=True)
        for position, dtype in enumerate(data.dtypes):
            if pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_float_dtype(dtype):
                result.isetitem(position, _standardize_column(data.iloc[:, position]))
        return result

    result = [list(row) for row in data]
    if not result:
        return result
    width = len(result[0])
    if any(len(row) != width for row in result):
        raise ValueError('Expected a rectangular table with a header row')
    for column in range(width):
        positions = [row for row in range(1, len(result))
                     if isinstance(result[row][column], Real)
                     and not isinstance(result[row][column], (bool, np.bool_))]
        if not positions:
            continue
        values = pd.Series([result[row][column] for row in positions], dtype='float64')
        scaled = _standardize_column(values)
        for row, value in zip(positions, scaled):
            result[row][column] = value
    return result


if __name__ == '__main__':
    example = [['name', 'age', 'weight'],
               ['John Doe', '30', '75.5'], ['Jane Doe', '25', '68.2']]
    for row in standardize_data(transform_data(example)):
        print(row)
