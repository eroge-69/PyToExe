
import pandas as pd
import sys
import os

def convert_excel_to_csv(input_excel_path, output_csv_path):
    df = pd.read_excel(input_excel_path, engine='openpyxl')
    df.to_csv(output_csv_path, sep=';', index=False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: excel_to_csv.exe <input_excel_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + ".csv"
    convert_excel_to_csv(input_file, output_file)
    print(f"Converted '{input_file}' to '{output_file}'")
