import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from collections import defaultdict
import os

TABLE_NAME = "amocrm_data"

def guess_type(values, field_name):
    field_name_low = field_name.lower()
    if "date" in field_name_low or "дата" in field_name_low:
        return "TIMESTAMP"
    bool_vals = {"да", "нет", "yes", "no", "true", "false"}
    if all(v.lower() in bool_vals for v in values if v):
        return "BOOLEAN"
    if all(re.fullmatch(r"[+-]?\d+(\.\d+)?", v) for v in values if v):
        return "NUMERIC"
    return "TEXT"

def clean_value(value, col_type):
    if not value:
        return "NULL"
    v = value.strip()
    if col_type == "NUMERIC":
        return v.replace(",", ".")
    elif col_type == "BOOLEAN":
        return "TRUE" if v.lower() in ("да","yes","true","1") else "FALSE"
    elif col_type == "TIMESTAMP":
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(v, fmt)
                return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
            except ValueError:
                continue
        return f"'{v}'"
    else:
        return f"'{v.replace(\"'\", \"''\")}'"

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    rows, all_fields = [], defaultdict(list)
    for elem in root:
        row = {}
        for child in elem:
            val = child.text or ""
            row[child.tag] = val.strip()
            all_fields[child.tag].append(val.strip())
        rows.append(row)
    return rows, all_fields

def convert(file_path):
    rows, all_fields = parse_xml(file_path)
    column_types = {}
    for field, values in all_fields.items():
        sample = [v for v in values[:200] if v]
        column_types[field] = guess_type(sample, field)
    create_sql = [f"CREATE TABLE {TABLE_NAME} ("]
    create_sql.append("    id SERIAL PRIMARY KEY,")
    for i, (field, col_type) in enumerate(column_types.items()):
        comma = "," if i < len(column_types)-1 else ""
        create_sql.append(f"    {field.lower()} {col_type}{comma}")
    create_sql.append(");")
    create_sql = "\n".join(create_sql)
    col_names = [f.lower() for f in column_types.keys()]
    insert_sql = []
    for row in rows:
        vals = [clean_value(row.get(col, ""), column_types[col]) for col in column_types.keys()]
        insert_sql.append(f"INSERT INTO {TABLE_NAME} ({', '.join(col_names)}) VALUES ({', '.join(vals)});")
    base = os.path.splitext(file_path)[0]
    with open(base+"_create.sql","w",encoding="utf-8") as f: f.write(create_sql)
    with open(base+"_insert.sql","w",encoding="utf-8") as f: f.write("\n".join(insert_sql))
    return base+"_create.sql", base+"_insert.sql"

def run_app():
    def choose_file():
        filename = filedialog.askopenfilename(filetypes=[("XML files","*.xml")])
        if filename:
            file_var.set(filename)
    def do_convert():
        if not file_var.get():
            messagebox.showerror("Ошибка","Выберите XML файл!")
            return
        try:
            f1,f2 = convert(file_var.get())
            messagebox.showinfo("Готово", f"SQL файлы сохранены:\n{f1}\n{f2}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    root = tk.Tk()
    root.title("XML → SQL Converter")
    tk.Label(root,text="Выберите XML файл:").pack(pady=5)
    file_var = tk.StringVar()
    entry = tk.Entry(root,textvariable=file_var,width=50)
    entry.pack(side="left",padx=5,pady=5)
    tk.Button(root,text="Обзор",command=choose_file).pack(side="left",padx=5)
    tk.Button(root,text="Конвертировать",command=do_convert).pack(pady=10)
    root.mainloop()

if __name__=="__main__":
    run_app()
