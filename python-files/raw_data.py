import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Function to browse and open the Excel file
def browse_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        filetypes=[
            ("Excel Files", "*.xlsx"),
            ("Excel Files", "*.xls"),
            ("All Files", "*.*")  # optional: show everything
        ]
    )
    return file_path

# Main function
def process_excel():
    # Browse to open the Excel file
    file_path = browse_file()
    if not file_path:
        print("No file selected.")
        return

    try:
        print(f"File selected: {file_path}")  # Debug info

        # Load the Excel file and the 'Raw data' sheet
        excel_data = pd.ExcelFile(file_path)
        if 'Raw data' not in excel_data.sheet_names:
            print("Sheet 'Raw data' not found in the Excel file.")
            return

        raw_data = excel_data.parse('Raw data')

        # Validate necessary columns exist
        required_columns = ['S7', 'C3', 'C2']
        if not all(col in raw_data.columns for col in required_columns):
            print(f"The required columns {required_columns} are not all present in the sheet.")
            return

        # Group data by S7 and count occurrences, copying corresponding C3 and C2 values
        result = (raw_data.groupby('S7')
                        .agg(Q_ty=('S7', 'size'),
                             City=('C3', 'first'),
                             Name=('C2', 'first'))
                        .reset_index()
                        .rename(columns={'S7': 'DX Nr.'}))

        # Save the result to a new Excel file
        if file_path.endswith(".xlsx"):
            output_file = file_path.replace('.xlsx', '_result.xlsx')
        elif file_path.endswith(".xls"):
            output_file = file_path.replace('.xls', '_result.xlsx')
        else:
            output_file = file_path + "_result.xlsx"

        result.to_excel(output_file, index=False, sheet_name='Result')

        print(f"Result saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_excel()
