import unittest
from transform.data_transformer import transform_data
from transform.data_transformer import standardize_data
import numpy as np
import pandas as pd
import pytest

# Here is a comment for indicating new info

class TestDataTransformer(unittest.TestCase):
    
    def test_transform_data(self):
        # Define the input and expected output
        input_data = [
            ["name", "age", "weight"],
            ["John Doe", "30", "75.5"],
            ["Jane Doe", "25", "68.2"],
        ]

        expected_output = [
            ["name", "age", "weight"],
            ["John Doe", 30.0, 75.5],
            ["Jane Doe", 25.0, 68.2],
        ]

        # Call the function with the test input
        actual_output = transform_data(input_data)

        # Assert that the actual output matches the expected output
        self.assertEqual(actual_output, expected_output)

def test_standardize_data():
    # Create a sample DataFrame
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': [100, 200, 300, 400, 500],
        'C': ['a', 'b', 'c', 'd', 'e']
    }
    df = pd.DataFrame(data)

    # Standardize the data
    df_standardized = standardize_data(df.copy())

    # Check that the numeric columns have mean 0 and std deviation 1
    for col in ['A', 'B']:
        assert np.isclose(df_standardized[col].mean(), 0)
        assert np.isclose(df_standardized[col].std(), 1)

    # Check that the non-numeric column has not changed
    assert df_standardized['C'].equals(df['C'])


def test_standardize_list_columns_independently():
    data = [
        ['name', 'small', 'large'],
        ['first', 1.0, 100.0],
        ['second', 2.0, 200.0],
        ['third', 3.0, 300.0],
    ]

    result = standardize_data(data)

    assert result == [
        ['name', 'small', 'large'],
        ['first', -1.0, -1.0],
        ['second', 0.0, 0.0],
        ['third', 1.0, 1.0],
    ]
    assert data[1] == ['first', 1.0, 100.0]


@pytest.mark.parametrize('data, expected', [
    ([['value'], [7.0], [7.0]], [['value'], [0.0], [0.0]]),
    ([['value'], [7.0]], [['value'], [0.0]]),
    ([['value'], [1], [2], [3]], [['value'], [-1.0], [0.0], [1.0]]),
    ([['name'], ['Alice'], ['Bob']], [['name'], ['Alice'], ['Bob']]),
    ([['name']], [['name']]),
    ([], []),
])
def test_standardize_list_degenerate_columns(data, expected):
    assert standardize_data(data) == expected


@pytest.mark.parametrize('data, expected', [
    ({'value': [7.0, 7.0], 'name': ['a', 'b']},
     {'value': [0.0, 0.0], 'name': ['a', 'b']}),
    ({'value': [7.0]}, {'value': [0.0]}),
    ({'name': ['a', 'b']}, {'name': ['a', 'b']}),
    ({'value': pd.Series(dtype=float)}, {'value': pd.Series(dtype=float)}),
])
def test_standardize_dataframe_degenerate_columns(data, expected):
    frame = pd.DataFrame(data)
    frame.index = pd.Index(range(10, 10 + len(frame)), name='row')
    original = frame.copy(deep=True)
    expected_frame = pd.DataFrame(expected, index=frame.index)

    result = standardize_data(frame)

    pd.testing.assert_frame_equal(result, expected_frame)
    pd.testing.assert_frame_equal(frame, original)


if __name__ == "__main__":
    unittest.main()
