import openpyxl
from openpyxl.utils import range_boundaries
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

def is_merged_cell(cell, merged_ranges):
    """Проверка, находится ли ячейка в объединённой области"""
    for merged_range in merged_ranges:
        min_col, min_row, max_col, max_row = range_boundaries(str(merged_range))
        if min_row <= cell.row <= max_row and min_col <= cell.column <= max_col:
            return True
    return False

def is_product_code(value):
    """Проверка, что значение — код товара (5–6 символов, буквы/цифры)"""
    if value is None:
        return False
    value = str(value).strip()
    return bool(re.fullmatch(r'[A-Za-z0-9]{5,6}', value))

def process_file(filepath):
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active

    merged_ranges = ws.merged_cells.ranges
    rows_to_delete = []

    for row in ws.iter_rows(min_row=1):
        first_cell = row[0]
        third_cell = row[2]

        # Пропускаем объединённые ячейки
        if is_merged_cell(first_cell, merged_ranges):
            continue

        # Если это товарная строка без остатка — удаляем
        if is_product_code(first_cell.value) and (third_cell.value is None or str(third_cell.value).strip() == ""):
            rows_to_delete.append(first_cell.row)

    # Удаляем строки с конца, чтобы не сбить нумерацию
    for row_idx in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(row_idx)

    # Сохраняем новый файл рядом с исходным
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    new_filename = os.path.join(dirname, f"filtered_{basename}")
    wb.save(new_filename)

    return new_filename

def main():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        title="Выберите Excel-файл",
        filetypes=[("Excel files", "*.xlsx")]
    )
    if not filepath:
        return

    try:
        result_file = process_file(filepath)
        messagebox.showinfo("Готово", f"Файл сохранён:\n{result_file}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    main()
