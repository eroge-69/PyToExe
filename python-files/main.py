import tkinter as tk
from tkinter import filedialog
import os
import csv
from datetime import datetime

# === CSV Processing Functions ===

def delete_first_line(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines = lines[1:]
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def filter_rows_ending_with_semicolon_one(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if any(cell.strip().endswith(';1') for cell in row):
                writer.writerow(row)

def process_line(line):
    semicolon_positions = [i for i, char in enumerate(line) if char == ';']
    if len(semicolon_positions) < 4:
        return line.strip()
    first = semicolon_positions[0]
    third = semicolon_positions[2]
    fourth = semicolon_positions[3]
    part1 = line[:first]
    part2 = line[third + 1:fourth]
    return f"{part1};{part2}".strip()

def process_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            processed = process_line(line)
            outfile.write(processed + '\n')

def is_binary_string(s):
    return all(c in '01' for c in s) and len(s) > 0

def convert_bin_to_hex_if_needed(value):
    value = value.strip()
    if is_binary_string(value):
        return format(int(value, 2), 'x')
    else:
        return value

def process_csv_binary_to_hex_no_prefix(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            parts = line.strip().split(';')
            if len(parts) < 2:
                outfile.write(line)
                continue
            parts[1] = convert_bin_to_hex_if_needed(parts[1])
            new_line = ';'.join(parts)
            outfile.write(new_line + '\n')

def add_header_to_csv(input_file, output_file, reference, selected_r):
    today = datetime.today().strftime('%Y/%m/%d')
    version_value = "1.1" if selected_r == "R1" else "1.0"
    header_lines = [
        f"Version;{version_value}",
        f"Reference;{reference}",
        f"Date;{today}"
    ]
    with open(input_file, 'r', encoding='utf-8') as infile:
        original_lines = infile.readlines()
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in header_lines:
            outfile.write(line + '\n')
        outfile.writelines(original_lines)

def remove_duplicate_lines(input_file, output_file):
    seen = set()
    unique_rows = []
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_rows.append(row)
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(unique_rows)

def remove_quotes_and_empty_lines_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    cleaned_lines = [line.replace('"', '') for line in lines if line.strip()]
    while cleaned_lines and cleaned_lines[-1].strip() == '':
        cleaned_lines.pop()
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)

def cleanup_temp_csv_files(except_file):
    for file in os.listdir():
        if file.endswith(".csv") and file != except_file:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Could not delete {file}: {e}")

# === GUI Logic ===

def select_input_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        entry_input_file.delete(0, tk.END)
        entry_input_file.insert(0, filepath)

def run_full_pipeline():
    reference = entry_reference.get().strip()
    selected_r = var_r.get()
    input_file = entry_input_file.get()

    if not reference:
        result_label.config(text="Please enter a reference.", fg="red")
        return

    if not input_file or not os.path.isfile(input_file):
        result_label.config(text="Please select a valid input CSV file.", fg="red")
        return

    try:
        # Step-by-step processing
        delete_first_line(input_file)

        step1 = 'filtered_output.csv'
        step2 = 'columns_off.csv'
        step3 = 'Hexa_conv.csv'
        step4 = 'temp_with_header.csv'
        final_output = f"{reference}.csv"

        filter_rows_ending_with_semicolon_one(input_file, step1)
        process_csv(step1, step2)
        process_csv_binary_to_hex_no_prefix(step2, step3)
        add_header_to_csv(step3, step4, reference, selected_r)
        remove_duplicate_lines(step4, final_output)
        remove_quotes_and_empty_lines_from_csv(final_output)

        # Cleanup intermediate files
        cleanup_temp_csv_files(final_output)

        result_label.config(text=f"✅ File '{final_output}' created successfully.", fg="green")

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}", fg="red")

# === GUI Setup ===

root = tk.Tk()
root.title("CSV Processor")

tk.Label(root, text="Enter Reference:").grid(row=0, column=0, padx=10, pady=10)
entry_reference = tk.Entry(root)
entry_reference.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Select R1 or R2:").grid(row=1, column=0, padx=10, pady=10)
var_r = tk.StringVar(value="R1")
tk.Radiobutton(root, text="R1", variable=var_r, value="R1").grid(row=1, column=1, sticky="w")
tk.Radiobutton(root, text="R2", variable=var_r, value="R2").grid(row=1, column=1)

tk.Label(root, text="Select Input CSV File:").grid(row=2, column=0, padx=10, pady=10)
entry_input_file = tk.Entry(root, width=40)
entry_input_file.grid(row=2, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_input_file).grid(row=2, column=2, padx=10, pady=10)

tk.Button(root, text="Generate", command=run_full_pipeline).grid(row=3, column=1, pady=10)

result_label = tk.Label(root, text="", fg="green")
result_label.grid(row=4, column=1, pady=10)

root.mainloop()