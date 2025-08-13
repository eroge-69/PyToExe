
import os
import csv
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_pressure_values(base_path):
    summary = {}
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path) and folder_name[0] in ['C', 'D'] and folder_name[1:6].isdigit():
            year_folder = os.path.join(folder_path, '2025')
            if os.path.exists(year_folder):
                subfolders = [os.path.join(year_folder, f) for f in os.listdir(year_folder) if os.path.isdir(os.path.join(year_folder, f))]
                if subfolders:
                    newest_folder = max(subfolders, key=os.path.getmtime)
                    raw_folder = os.path.join(newest_folder, 'raw')
                    status_file = os.path.join(raw_folder, 'status.csv')
                    if os.path.exists(status_file):
                        with open(status_file, newline='', encoding='utf-8') as csvfile:
                            reader = csv.reader(csvfile)
                            next(reader, None)
                            pressures = []
                            for row in reader:
                                if len(row) > 1:
                                    try:
                                        pressure = float(row[1])
                                        if pressure != 0:
                                            pressures.append(pressure)
                                    except ValueError:
                                        continue
                            if pressures:
                                summary[folder_name] = pressures
    return summary

def plot_pressures(pressure_summary):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab20.colors
    index = 0
    for i, (folder, pressures) in enumerate(sorted(pressure_summary.items())):
        x = list(range(index, index + len(pressures)))
        ax.bar(x, pressures, label=folder, color=colors[i % len(colors)])
        index += len(pressures) + 1
    ax.set_title("Druckwerte aus status.csv-Dateien")
    ax.set_ylabel("Druck")
    ax.set_xlabel("Messungen (gruppiert nach Ordner)")
    ax.legend(title="Ordner", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def select_folder_and_plot():
    folder_selected = filedialog.askdirectory(title="Wähle den Ordner 'Runs Biotype instruments'")
    if folder_selected:
        pressure_summary = extract_pressure_values(folder_selected)
        if pressure_summary:
            plot_pressures(pressure_summary)
        else:
            messagebox.showinfo("Keine Daten", "Keine gültigen Druckdaten gefunden.")

# GUI Setup
root = tk.Tk()
root.title("Druckdaten Visualisierung")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="Klicke auf den Button, um den Ordner 'Runs Biotype instruments' auszuwählen und die Druckdaten zu visualisieren.")
label.pack(pady=10)

button = tk.Button(frame, text="Ordner auswählen und visualisieren", command=select_folder_and_plot)
button.pack(pady=10)

root.mainloop()
