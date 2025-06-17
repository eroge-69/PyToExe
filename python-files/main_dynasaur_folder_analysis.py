import os
import re
import json
import pandas as pd
from openpyxl import load_workbook


def natural_sort_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


def collect_folders_with_criteria(root_dir):
    folder_data = {}
    for subdir, _, files in os.walk(root_dir):
        if 'criteria.csv' in files:
            csv_path = os.path.join(subdir, 'criteria.csv')
            rel_path = os.path.relpath(subdir, root_dir)
            parts = rel_path.split(os.sep)
            if len(parts) == 1:
                folder_name = parts[0]
                parsed = parse_criteria_file(csv_path)
                folder_data[folder_name] = parsed
    return folder_data


def parse_criteria_file(csv_path):
    df = pd.read_csv(csv_path, sep=';', header=None)
    result = {}

    name_row = df.iloc[2]  # Zeile 3
    value_row = df.iloc[4]  # Zeile 5

    i = 0
    while i < len(name_row):
        try:
            name = str(name_row[i]).strip()
            if not name or '_' not in name:
                i += 1
                continue

            value = value_row[i]
            time_value = value_row[i + 1] if i + 1 < len(value_row) else None

            result[name] = value
            result[name + "_time"] = time_value
            i += 2
        except Exception:
            i += 1
            continue

    return result


def insert_folder_names_to_excel(file_path, folder_names):
    wb = load_workbook(file_path)
    ws = wb.active

    for idx, folder_name in enumerate(folder_names, start=3):  # ab Zeile 3
        ws.cell(row=idx, column=1, value=folder_name)

    wb.save(file_path)


def update_excel_data(excel_path, data_dict, folder_names):
    wb = load_workbook(excel_path)
    ws = wb.active

    col_map = {}
    for col in range(2, ws.max_column + 1):
        name_cell = ws.cell(row=1, column=col).value
        if name_cell is None:
            for c in range(col - 1, 1, -1):
                prev_val = ws.cell(row=1, column=c).value
                if prev_val is not None:
                    name_cell = prev_val
                    break

        type_cell = ws.cell(row=2, column=col).value
        if name_cell is None or type_cell is None:
            continue

        name = str(name_cell).strip()
        type_ = str(type_cell).strip()
        key = f"{name}_{type_}"
        col_map[key] = col

    for row_idx, folder in enumerate(folder_names, start=3):
        ws.cell(row=row_idx, column=1, value=folder)
        entry = data_dict.get(folder, {})
        for key, val in entry.items():
            col = col_map.get(key)
            if col:
                try:
                    val_num = float(val)
                    ws.cell(row=row_idx, column=col, value=val_num)
                except (ValueError, TypeError):
                    ws.cell(row=row_idx, column=col, value=val)

    wb.save(excel_path)


def update_cross_section_excel(excel_path, data_dict, folder_names):
    wb = load_workbook(excel_path)
    ws = wb.active

    col_map = {}
    for col in range(2, ws.max_column + 1):
        name_cell = ws.cell(row=1, column=col).value
        if name_cell is None:
            for c in range(col - 1, 1, -1):
                prev_val = ws.cell(row=1, column=c).value
                if prev_val is not None:
                    name_cell = prev_val
                    break
        type_cell = ws.cell(row=2, column=col).value
        if name_cell is None or type_cell is None:
            continue

        name = str(name_cell).strip()
        typ = str(type_cell).strip()
        key = f"{name}_{typ}"
        col_map[key] = col

    for row_idx, folder in enumerate(folder_names, start=3):
        ws.cell(row=row_idx, column=1, value=folder)
        entry = data_dict.get(folder, {})
        for key, val in entry.items():
            col = col_map.get(key)
            if col:
                try:
                    val_num = float(val)
                    ws.cell(row=row_idx, column=col, value=val_num)
                except (ValueError, TypeError):
                    ws.cell(row=row_idx, column=col, value=val)

    wb.save(excel_path)


def process_all(root_dir, mps_file, ps99_file, cross_section_file):
    print("🔍 Sammle Ordner mit criteria.csv...")
    folder_data_all = collect_folders_with_criteria(root_dir)

    print("📋 Sortiere Ordnernamen natürlich...")
    folder_names_sorted = sorted(folder_data_all.keys(), key=natural_sort_key)

    print("📝 Schreibe Ordnernamen in Excel-Dateien...")
    insert_folder_names_to_excel(mps_file, folder_names_sorted)
    insert_folder_names_to_excel(ps99_file, folder_names_sorted)
    insert_folder_names_to_excel(cross_section_file, folder_names_sorted)

    print("📊 Füge Daten in Excel-Dateien ein...")

    folder_data_mps = {}
    folder_data_ps99 = {}
    folder_data_cross = {}
    for folder, values in folder_data_all.items():
        mps_entry = {k: v for k, v in values.items() if "_MPS_" in k}
        ps99_entry = {k: v for k, v in values.items() if "_PS99_" in k}
        cross_entry = {k: v for k, v in values.items() if "_MAX" in k and "_MPS_" not in k and "_PS99_" not in k}
        if mps_entry:
            folder_data_mps[folder] = mps_entry
        if ps99_entry:
            folder_data_ps99[folder] = ps99_entry
        if cross_entry:
            folder_data_cross[folder] = cross_entry

    update_excel_data(mps_file, folder_data_mps, folder_names_sorted)
    update_excel_data(ps99_file, folder_data_ps99, folder_names_sorted)
    update_cross_section_excel(cross_section_file, folder_data_cross, folder_names_sorted)

    print("✅ Fertig!")


# 📖 Lade Konfiguration
with open("settings.json", "r", encoding="utf-8") as f:
    config = json.load(f)

root_dir = config["root_dir"]
mps_file = config["mps_file"]
ps99_file = config["ps99_file"]
cross_file = config["cross_section_file"]

process_all(root_dir, mps_file, ps99_file, cross_file)
