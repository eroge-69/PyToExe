# Script Functionality:
# 1. Process CSV with less memory consumption
# 2. Remove row from key words list
# 3. Replace PARTID with DEVID
# 4. Replace NAN value with dummy integer (1e6)

import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Load in filter keyword from filter_keyword list and exclude the rows from output file
def should_filter(row_dict, filter_words):
    value = row_dict.get('TESTNAME_NO_LOOP','')
    for word in filter_words:
        if word and word in value:
            return True
    return False


# Replace NAN value from VALUE column with 1e6 to prevent SpotFire data loading issue
def clean_value(value):
    #invalud_Value = {'Invalid Value1', 'Invalid Value2,' ...}
    invalid_value = {'1.#INF00','-1.#IND00','1.#QNAN0', 'NaN', 'NULL'} 
    if value.strip().upper() in invalid_value:
        return '1000000'
    return value

# Procss CSV file
def process_csv(input_path, raw_filter_input):
    base, ext = os.path.splitext(input_path)
    output_path = base + '_Modify.csv'

    # Split filter words and turn into list
    filter_words = [w.strip() for w in raw_filter_input.split(',') if w.strip()]

    with open(input_path, 'r', newline='') as inflile, open(output_path, 'w', newline='') as outfile:
        reader = csv.DictReader(inflile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        removed = 0
        fixed = 0

        for row in reader:
            if should_filter(row, filter_words):
                removed += 1
                continue
            row['PARTID'] = row['DEVID']
            if 'VALUE' in row:
                original = row['VALUE']
                row['VALUE'] = clean_value(row['VALUE'])
                if row['VALUE'] != original:
                    fixed += 1
            writer.writerow(row)
    return output_path, removed, fixed

# GUI for file selection
def select_file():
    filepath = filedialog.askopenfilename(
        title= "Please Select .CSV file",
        filetypes=[("CSV File", "*.csv")]
    )
    if not filepath:
        return
    
    #
    keywords = entry_keywords.get()

    try:
        output_path, removed, fixed = process_csv(filepath, keywords)
        messagebox.showinfo(
            "Complete data processing!",
            f"Output File: {output_path}\n"
            f"Number of Deleted Tests: {removed}\n Number of Fix Value: {fixed}"
        )
    except Exception as e:
        messagebox.showerror("ERROR!",f"Error during data processing: \n{str(e)}")

# Main GUI
def run_gui():
    global entry_keywords

    root = tk.TK()
    root.title("CSV Processor")
    root.geometry("500x250")

    tk.Label(root, text="Please enter fitler keyword for TESTNAME_NO_LOOP column and sepearte them by ,", font=("Arial", 12)).pack(pady=10)

    entry_keywords = tk.Entry(root, font=("Arial", 12), width=50)
    entry_keywords.pack(pady=5)

    tk.Button(root, text="Select CSV file",command=select_file, font=("Arial", 12),width=30).pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    run_gui()