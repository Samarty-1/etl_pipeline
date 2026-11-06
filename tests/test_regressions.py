import contextlib
import copy
import importlib
import io
import math

import pandas as pd
import pytest

from extract.csv_extractor import extract_data
from transform import data_transformer
from transform.data_transformer import standardize_data, transform_data


def test_csv_returns_rows_and_handles_bom_quotes_and_unicode(tmp_path):
    path = tmp_path / 'data.csv'
    path.write_text('\ufeffname,value\n"Renée, A",1\nBob,3\n', encoding='utf-8')
    assert extract_data(path) == [['name', 'value'], ['Renée, A', '1'], ['Bob', '3']]


def test_csv_pipeline(tmp_path):
    path = tmp_path / 'data.csv'
    path.write_text('name,x,y\nA,1,100\nB,2,200\nC,3,300\n', encoding='utf-8')
    assert standardize_data(transform_data(extract_data(path))) == [
        ['name', 'x', 'y'], ['A', -1.0, -1.0], ['B', 0.0, 0.0], ['C', 1.0, 1.0]]


def test_transform_preserves_missing_values_and_booleans():
    assert transform_data([['x', 'flag'], [None, True], ['2', False]]) == [
        ['x', 'flag'], [None, True], [2.0, False]]


def test_transform_does_not_mutate_input():
    source = [['x'], ['2']]
    result = transform_data(source)
    assert source == [['x'], ['2']]
    assert result == [['x'], [2.0]]


def test_table_scales_columns_independently_without_mutation():
    source = [['x', 'y', 'label'], [1, 100, 'A'], [2, 200, 'B'], [3, 300, 'C']]
    before = copy.deepcopy(source)
    assert standardize_data(source) == [
        ['x', 'y', 'label'], [-1.0, -1.0, 'A'], [0.0, 0.0, 'B'], [1.0, 1.0, 'C']]
    assert source == before


@pytest.mark.parametrize('source', [[], [['x']], [['label'], ['A'], ['B']]])
def test_empty_and_nonnumeric_tables(source):
    assert standardize_data(source) == source


@pytest.mark.parametrize('source, expected', [
    ([['x'], [7.0], [7.0]], [['x'], [0.0], [0.0]]),
    ([['x'], [7.0]], [['x'], [0.0]]),
    ([['x'], [None], [7.0]], [['x'], [None], [0.0]]),
])
def test_degenerate_table_columns(source, expected):
    assert standardize_data(source) == expected


def test_dataframe_preserves_index_text_boolean_and_missing_values():
    source = pd.DataFrame({'x': [1.0, 2.0, 3.0, None],
                           'constant': [5, 5, 5, 5],
                           'label': ['a', 'b', 'c', 'd'],
                           'flag': [True, False, True, False]}, index=[4, 3, 2, 1])
    before = source.copy(deep=True)
    result = standardize_data(source)
    assert result['x'].iloc[:3].tolist() == [-1.0, 0.0, 1.0]
    assert math.isnan(result['x'].iloc[3])
    assert result['constant'].tolist() == [0.0] * 4
    pd.testing.assert_series_equal(result['label'], source['label'])
    pd.testing.assert_series_equal(result['flag'], source['flag'])
    pd.testing.assert_frame_equal(source, before)
    assert result.index.equals(source.index)


def test_nullable_dataframe():
    source = pd.DataFrame({'x': pd.Series([1, 2, 3, None], dtype='Int64')})
    result = standardize_data(source)
    assert result['x'].iloc[:3].tolist() == [-1.0, 0.0, 1.0]
    assert pd.isna(result['x'].iloc[3])


def test_ragged_table_is_rejected():
    with pytest.raises(ValueError, match='rectangular'):
        standardize_data([['x', 'y'], [1.0]])


@pytest.mark.parametrize('source', [[['x'], [1.0], [float('inf')]],
                                    pd.DataFrame({'x': [1.0, float('inf')]})])
def test_infinity_is_rejected(source):
    with pytest.raises(ValueError, match='infinite'):
        standardize_data(source)


def test_import_is_silent():
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        importlib.reload(data_transformer)
    assert output.getvalue() == ''


def test_float_table_columns_are_not_pooled():
    source = [['x', 'y'], [1.0, 100.0], [2.0, 200.0], [3.0, 300.0]]
    assert standardize_data(source) == [
        ['x', 'y'], [-1.0, -1.0], [0.0, 0.0], [1.0, 1.0]]


def test_dataframe_duplicate_column_labels():
    source = pd.DataFrame([[1, 100], [2, 200], [3, 300]], columns=['x', 'x'])
    expected = pd.DataFrame([[-1.0, -1.0], [0.0, 0.0], [1.0, 1.0]], columns=['x', 'x'])
    pd.testing.assert_frame_equal(standardize_data(source), expected)


def test_all_missing_dataframe():
    source = pd.DataFrame({'x': [float('nan'), float('nan')]})
    pd.testing.assert_frame_equal(standardize_data(source), source)


def test_empty_dataframe():
    source = pd.DataFrame({'x': pd.Series(dtype='float64')})
    pd.testing.assert_frame_equal(standardize_data(source), source)


def test_csv_embedded_newline_and_empty_file(tmp_path):
    path = tmp_path / 'data.csv'
    path.write_bytes(b'name,value\r\n"A\r\nB",1\r\n')
    assert extract_data(path) == [['name', 'value'], ['A\r\nB', '1']]
    path.write_bytes(b'')
    assert extract_data(path) == []


def test_csv_missing_file_propagates_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_data(tmp_path / 'absent.csv')
