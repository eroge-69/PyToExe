import sys
import pandas as pd

def main():
    if len(sys.argv) != 2:
        print("Usage: sum_numbers.exe <path_to_excel_file>")
        sys.exit(1)

    excel_path = sys.argv[1]
    # Read the sheet (default first sheet)
    df = pd.read_excel(excel_path)

    # Compute sum
    df['Sum'] = df['number 1'] + df['number 2']

    # Overwrite the original file (or change filename if you prefer)
    df.to_excel(excel_path, index=False)
    print(f"Updated '{excel_path}' with a new 'Sum' column.")

if __name__ == "__main__":
    main()
