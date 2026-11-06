"""Read CSV rows for use by the transformation stage."""

import csv


def extract_data(file_name):
    """Return all rows, including the header, from a UTF-8 CSV file.

    Accepts paths or path-like objects. An optional UTF-8 BOM is stripped.
    File and decoding errors propagate to the caller.
    """
    with open(file_name, 'r', encoding='utf-8-sig', newline='') as file:
        return list(csv.reader(file))


if __name__ == '__main__':
    for row in extract_data('data.csv'):
        print(row)
