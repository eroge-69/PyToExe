
import csv
import sys
import os

def is_valid_row(row):
    return len(row) == 2 and row[0].isdigit()

def main():
    file_path = input("Enter path to CSV file: ").strip()
    if not os.path.isfile(file_path):
        print("File does not exist.")
        return

    print("\nReading and validating CSV content...\n")
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader, start=1):
            if is_valid_row(row):
                print(f"[Row {i}] VALID: ID = {row[0]}")
            else:
                print(f"[Row {i}] INVALID: {row}")

if __name__ == "__main__":
    main()
