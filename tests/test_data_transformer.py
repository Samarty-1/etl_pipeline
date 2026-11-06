import unittest
from transform.data_transformer import transform_data
from transform.data_transformer import standardize_data
import numpy as np
import pandas as pd

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


if __name__ == "__main__":
    unittest.main()
