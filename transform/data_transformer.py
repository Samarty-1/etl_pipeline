from numbers import Real


def transform_data(data):
    """
    Transforms a list of lists by converting all numerical values to floats.
    Assumes the input is a table of data, where each sub-list is a row.
    """
    transformed_data = []
    #Adding test comment
    #Test comment
    #BRANCH COMMENT1

    for row in data:
        new_row = []
        for value in row:
            try:
                new_row.append(float(value))
            except ValueError:
                new_row.append(value)
        transformed_data.append(new_row)
    
    return transformed_data

if __name__ == "__main__":
    data = [
        ["name", "age", "weight"],
        ["John Doe", "30", "75.5"],
        ["Jane Doe", "25", "68.2"],
    ]
    
    transformed_data = transform_data(data)
    for row in transformed_data:
        print(row)

def standardize_data(data):
    """
    Standardize each numeric column using its sample standard deviation.

    Accepts a pandas DataFrame or a list of rows whose first row is a header.
    Returns a copy, preserving headers and nonnumeric values. Constant columns
    and columns with only one numeric value are centered to zero.
    """
    if hasattr(data, 'select_dtypes'):
        standardized_data = data.copy()
        numeric_data = data.select_dtypes(include='number')
        scale = numeric_data.std()
        scale = scale.mask((scale == 0) | scale.isna(), 1.0)
        standardized_data[numeric_data.columns] = (numeric_data - numeric_data.mean()) / scale
        return standardized_data

    standardized_data = [list(row) for row in data]
    if not data:
        return standardized_data

    for column_index in range(len(data[0])):
        numeric_rows = [
            row for row in standardized_data[1:]
            if isinstance(row[column_index], Real)
            and not isinstance(row[column_index], bool)
        ]
        if not numeric_rows:
            continue
        values = [row[column_index] for row in numeric_rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values)
        scale = (variance / (len(values) - 1)) ** 0.5 if len(values) > 1 else 0.0
        for row in numeric_rows:
            row[column_index] = (row[column_index] - mean) / scale if scale else 0.0

    return standardized_data

if __name__ == "__main__":
    data = [
        ["name", "age", "weight"],
        ["John Doe", "30", "75.5"],
        ["Jane Doe", "25", "68.2"],
    ]
    
    transformed_data = transform_data(data)
    standardized_data = standardize_data(transformed_data)
    for row in standardized_data:
        print(row)

print("If you can read this, then you are too close to me or yourself")
