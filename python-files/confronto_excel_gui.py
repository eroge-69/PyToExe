import pandas as pd
import tkinter as tk
from tkinter import filedialog

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    return file_path

def compare_excel_files(file1, file2):
    # Read the first sheet of both files
    df1 = pd.read_excel(file1, sheet_name=0, engine='openpyxl')
    df2 = pd.read_excel(file2, sheet_name=0, engine='openpyxl')
    
    # Find differences
    comparison_values = df1.values == df2.values
    rows, cols = comparison_values.shape
    
    # Create a DataFrame to store differences
    differences = pd.DataFrame(index=df1.index, columns=df1.columns)
    
    for row in range(rows):
        for col in range(cols):
            if not comparison_values[row, col]:
                differences.iloc[row, col] = f"{df1.iloc[row, col]} != {df2.iloc[row, col]}"
    
    # Save differences to a new Excel file
    differences.to_excel("differenze.xlsx", engine='openpyxl')

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Select the first file
    print("Seleziona il primo file Excel (A):")
    file1 = select_file()
    print(f"File selezionato: {file1}")

    # Select the second file
    print("Seleziona il secondo file Excel (B):")
    file2 = select_file()
    print(f"File selezionato: {file2}")

    # Compare the files and save differences
    compare_excel_files(file1, file2)
    print("Confronto completato. Differenze salvate in 'differenze.xlsx'.")

if __name__ == "__main__":
    main()
