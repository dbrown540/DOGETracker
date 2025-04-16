"""
This function opens a CSV file in read mode with UTF-8 encoding, skips the
header row, and counts the remaining rows. It handles cases where the file
does not exist by catching the FileNotFoundError and returning 0.


    int: The number of data rows in the CSV file. Returns 0 if the file
    does not exist.
"""
import csv

def count_rows_in_csv(file_path: str) -> int:
    """
    Counts the number of data rows (excluding the header) in a CSV file,
    handling multiline fields safely.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        int: The number of data rows.
    """
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            return sum(1 for _ in reader)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return 0
