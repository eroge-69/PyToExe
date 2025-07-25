import os
import pandas as pd
from tqdm import tqdm
from pyxlsb import open_workbook
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style

# Unikal sütun adları funksiyası
def make_unique_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        if col is None or str(col).strip() == '':
            col = "Unnamed"
        count = seen.get(col, 0)
        new_col = f"{col}_{count}" if count > 0 else col
        seen[col] = count + 1
        new_cols.append(new_col)
    return new_cols

# Əsas funksiya
def birlesdir():
    input_folder = input_dir.get()
    output_folder = output_dir.get()
    if not input_folder or not output_folder:
        messagebox.showwarning("Xəta", "Hər iki qovluğu seçin.")
        return

    excel_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.xlsb', '.xlsx'))]
    if not excel_files:
        messagebox.showinfo("Boş qovluq", "Heç bir .xlsb və ya .xlsx faylı tapılmadı.")
        return

    all_dataframes = []

    status_label.config(text="Birləşdirmə prosesi başlayır...")
    root.update_idletasks()

    for idx, file in enumerate(excel_files):
        file_path = os.path.join(input_folder, file)
        ext = os.path.splitext(file)[1].lower()

        try:
            if ext == '.xlsb':
                with open_workbook(file_path) as wb:
                    sheet_names = wb.sheets
                    first_sheet_name = sheet_names[0]
                    with wb.get_sheet(first_sheet_name) as sheet:
                        rows = [row for row in sheet.rows()]
                        if not rows:
                            continue
                        raw_headers = [cell.v for cell in rows[0]]
                        headers = make_unique_columns(raw_headers)
                        data = [[cell.v for cell in row] for row in rows[1:]]
                        df = pd.DataFrame(data, columns=headers)
            elif ext == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
                df.columns = make_unique_columns(df.columns)
            else:
                continue

            df["Fayl Adı"] = file
            all_dataframes.append(df)

        except Exception as e:
            print(f"Xəta: {file} faylı oxunmadı. Səbəb: {e}")

        progress["value"] = int(((idx+1) / len(excel_files)) * 100)
        root.update_idletasks()

    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, "birlesdirilmis.xlsx")
        combined_df.to_excel(output_file, index=False)
        status_label.config(text=f"✅ Uğurla tamamlandı: {output_file}")
        messagebox.showinfo("Uğur", "Birləşdirmə tamamlandı!")
    else:
        status_label.config(text="⚠️ Fayl oxunmadı.")
        messagebox.showwarning("Nəticə", "Heç bir fayl oxunmadı və ya məlumat tapılmadı.")

# Qovluq seçici funksiyalar
def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_dir.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_dir.set(folder)

# GUI qurulması
root = tk.Tk()
root.title("Excel Faylları Birləşdirici")
root.geometry("500x250")
root.resizable(False, False)

input_dir = tk.StringVar()
output_dir = tk.StringVar()

tk.Label(root, text="Giriş qovluğu:").pack(pady=(10, 0))
tk.Entry(root, textvariable=input_dir, width=60).pack()
tk.Button(root, text="Seç", command=select_input_folder).pack()

tk.Label(root, text="Çıxış qovluğu:").pack(pady=(10, 0))
tk.Entry(root, textvariable=output_dir, width=60).pack()
tk.Button(root, text="Seç", command=select_output_folder).pack()

tk.Button(root, text="Birləşdirməyə başla", command=birlesdir, bg="green", fg="white").pack(pady=10)

progress = Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

root.mainloop()
