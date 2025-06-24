
import os
import tkinter as tk
from tkinter import filedialog
from openpyxl import Workbook
from datetime import datetime

def choose_directory():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Seleziona una cartella da esportare")
    return folder_selected

def walk_directory(root_path):
    for dirpath, dirnames, filenames in os.walk(root_path):
        yield dirpath, dirnames, filenames

def export_structure_to_excel(root_path, output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Struttura Cartelle"

    ws.append(["Percorso", "Tipo", "Nome"])

    for dirpath, dirnames, filenames in walk_directory(root_path):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            ws.append([full_path, "Cartella", dirname])
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            ws.append([full_path, "File", filename])

    wb.save(output_file)

def main():
    selected_folder = choose_directory()
    if not selected_folder:
        print("Nessuna cartella selezionata.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"StrutturaCartelle_{timestamp}.xlsx"
    export_structure_to_excel(selected_folder, output_filename)
    print(f"Struttura esportata con successo in '{output_filename}'")

if __name__ == "__main__":
    main()
