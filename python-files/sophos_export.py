import zipfile
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from tkinter import filedialog, Tk, messagebox

def extract_abf(abf_path, extract_to):
    with zipfile.ZipFile(abf_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def parse_json(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return json.load(f)

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = []
    for elem in root:
        row = {child.tag: child.text for child in elem}
        data.append(row)
    return data

def export_to_excel(data_dict, output_path):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for sheet, data in data_dict.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet[:31], index=False)

def main():
    Tk().withdraw()
    abf_file = filedialog.askopenfilename(
        title="Sophos .abf auswählen",
        filetypes=[("Sophos Backup", "*.abf")]
    )

    if not abf_file:
        messagebox.showerror("Abbruch", "Keine Datei ausgewählt.")
        return

    extract_dir = Path("temp_extract")
    extract_dir.mkdir(exist_ok=True)

    try:
        extract_abf(abf_file, extract_dir)
    except zipfile.BadZipFile:
        messagebox.showerror("Fehler", "Die .abf-Datei ist nicht im ZIP-Format oder beschädigt.")
        return

    data_dict = {}

    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = Path(root) / file
            if file.endswith(".json"):
                try:
                    data_dict[file] = parse_json(file_path)
                except:
                    pass
            elif file.endswith(".xml"):
                try:
                    data_dict[file] = parse_xml(file_path)
                except:
                    pass

    if not data_dict:
        messagebox.showerror("Fehler", "Keine verwertbaren Daten gefunden.")
        return

    output_path = Path(abf_file).with_suffix(".xlsx")
    export_to_excel(data_dict, output_path)

    messagebox.showinfo("Fertig", f"Export abgeschlossen:\n{output_path}")

if __name__ == "__main__":
    main()