# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 16:05:59 2025

@author: nx364029
"""

import os
import csv
import tkinter as tk
from tkinter import filedialog

def filter_column_values_from_files(file_paths, output_file):
    filtered_data = {}
    max_length = 0

    for file_path in file_paths:
        values = []
        with open(file_path, "r") as infile:
            for line in infile:
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        if parts[2] == "10":
                            values.append(parts[1].replace('.', ','))
                    except ValueError:
                        continue
        key = os.path.splitext(os.path.basename(file_path))[0]
        filtered_data[key] = values
        max_length = max(max_length, len(values))

    with open(output_file, "w", newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        headers = list(filtered_data.keys())
        writer.writerow(headers)

        for i in range(max_length):
            row = [filtered_data[key][i] if i < len(filtered_data[key]) else "" for key in headers]
            writer.writerow(row)

# GUI to select multiple files
root = tk.Tk()
root.withdraw()
print("Dateiauswahl wird geöffnet...")
selected_files = filedialog.askopenfilenames(title="Wähle eine oder mehrere .txt-Dateien aus", filetypes=[("Textdateien", "*.txt")])
print("Dateien ausgewählt:", selected_files)

if selected_files:
    output_csv = os.path.join(os.path.dirname(selected_files[0]), "combined_filtered_output.csv")
    filter_column_values_from_files(selected_files, output_csv)
    print(f"Ergebnis gespeichert in: {output_csv}")
else:
    print("Keine Dateien ausgewählt.")
