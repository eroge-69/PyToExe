import os
import tkinter as tk
from tkinter import filedialog, messagebox
import multiprocessing as mp
import pandas as pd
import dbf
import numpy as np

# Словарь месторождений
FIELDS = {
    1: "Медвежье",
    2: "Юбилейное",
    3: "Ямсовейское",
    4: "Бованенковское",
    5: "Харасавейское",
    7: "Ныда",
    8: "Юбилейное апт-альб"
}

# Пути по умолчанию
DEFAULT_DBF = r"E:\ЛАБОРАТОРИЯ КПРМ\BD_ASU\plast.dbf"
DEFAULT_EER1 = r"E:\ЛАБОРАТОРИЯ КПРМ\BD_ASU\eer1.dbf"
DEFAULT_OUTPUT_DIR = r"D:\scripts"

# Создание датафреймов из dbf
def load_dbf_as_dataframe(dbf_path, date_col_name, date_format):
    """
    Загружает данные из DBF-файла в pandas DataFrame.
    Преобразует указанную колонку с датой в формат datetime.
    
    Args:
        dbf_path (str): Путь к DBF-файлу.
        date_col_name (str): Имя колонки с датой для преобразования.
        date_format (str): Формат даты в исходном файле (например, '%Y%m%d').
    
    Returns:
        pd.DataFrame: Загруженный и обработанный DataFrame.
    """
    try:
        table = dbf.Table(dbf_path, codepage="cp866")
        table.open()
        
        field_names = table.field_names
        records = []
        for rec in table:
            row = {field: rec[field] for field in field_names}
            records.append(row)
        
        df = pd.DataFrame(records)
        table.close()

        df[date_col_name] = pd.to_datetime(
            df[date_col_name].astype(str), format=date_format, errors="coerce"
        )
        return df
    except Exception as e:
        messagebox.showerror("Ошибка загрузки файла", f"Не удалось загрузить файл {dbf_path}. Ошибка: {e}")
        return pd.DataFrame()

def process_field(args):
    """
    Основная логика обработки данных для одного месторождения.
    Объединяет данные из plast.dbf и eer1.dbf и сохраняет результат в txt- и csv-файлы.

    Args:
        args (tuple): Кортеж, содержащий:
                      - df_plast (pd.DataFrame): DataFrame с данными из plast.dbf.
                      - df_eer1 (pd.DataFrame): DataFrame с данными из eer1.dbf.
                      - field_id (int): ID месторождения.
                      - output_dir (str): Путь к папке для сохранения.

    Returns:
        str: Путь к созданному файлу (в данном случае, путь к txt-файлу).
    """
    df_plast, df_eer1, field_id, output_dir = args
    field_name = FIELDS.get(field_id, str(field_id))

    # --- Подготовка данных из plast.dbf ---
    df_plast_field = df_plast[df_plast["BBL1"] == field_id][["BBL3", "BL1", "BL4"]].copy()
    df_plast_field.columns = ["Скважина", "Дата", "Давление"]
    df_plast_field["Дата"] = df_plast_field["Дата"] + pd.offsets.MonthBegin(1)
    df_plast_field["Дата_merge"] = df_plast_field["Дата"].dt.strftime("%d.%m.%Y")

    # --- Подготовка данных из eer1.dbf ---
    df_eer1_field = df_eer1[df_eer1["BB1"] == field_id][["BB3", "BS1", "BS10"]].copy()
    df_eer1_field.columns = ["Скважина", "Дата", "Добыча"]
    df_eer1_field["Дата"] = df_eer1_field["Дата"] + pd.offsets.MonthBegin(1)
    df_eer1_field["Дата_merge"] = df_eer1_field["Дата"].dt.strftime("%d.%m.%Y")

    # --- Объединение датафреймов ---
    df_combined = pd.merge(
        df_plast_field,
        df_eer1_field[["Скважина", "Дата_merge", "Добыча"]],
        on=["Скважина", "Дата_merge"],
        how="left"
    )
    df_combined = df_combined.drop(columns="Дата_merge")
    df_combined["Дата"] = df_combined["Дата"].dt.strftime("%d.%m.%Y")
    df_combined["Добыча"] = df_combined["Добыча"].replace(np.nan, "")
    
    # --- Сохранение в TXT файл ---
    output_file_txt = os.path.join(output_dir, f"{field_name}.txt")
    df_combined.to_csv(
        output_file_txt,
        sep="\t",
        index=False,
        header=["Скважина", "Дата", "Давление", "Добыча"]
    )
    
    # --- Сохранение в CSV файл ---
    output_file_csv = os.path.join(output_dir, f"{field_name}.csv")
    df_combined.to_csv(
        output_file_csv,
        sep=";", # Используем точку с запятой, так как это часто используется в CSV
        index=False,
        header=["Скважина", "Дата", "Давление", "Добыча"]
    )

    return output_file_txt

def run_processing(dbf_path, eer1_path, selected_fields, output_dir):
    """
    Запускает параллельную обработку данных для выбранных месторождений.
    """
    df_plast = load_dbf_as_dataframe(dbf_path, date_col_name="BL1", date_format="%Y%m%d")
    df_eer1 = load_dbf_as_dataframe(eer1_path, date_col_name="BS1", date_format="%Y%m")
    
    if df_plast.empty or df_eer1.empty:
        return []

    args_list = [(df_plast, df_eer1, field_id, output_dir) for field_id in selected_fields]

    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.map(process_field, args_list)

    return results

def main():
    root = tk.Tk()
    root.title("Выгрузка пластовых давлений")
    
    # Функция для выбора файла
    def choose_file(entry):
        filepath = filedialog.askopenfilename(filetypes=[("DBF files", "*.dbf")])
        if filepath:
            entry.delete(0, tk.END)
            entry.insert(0, filepath)
    
    def choose_output():
        folder = filedialog.askdirectory()
        if folder:
            entry_output.delete(0, tk.END)
            entry_output.insert(0, folder)
    
    def start():
        dbf_path = entry_file.get()
        eer1_path = entry_eer1.get()
        output_dir = entry_output.get()

        if not os.path.isfile(dbf_path):
            messagebox.showerror("Ошибка", "Выберите DBF-файл plast.dbf!")
            return
        if not os.path.isfile(eer1_path):
            messagebox.showerror("Ошибка", "Выберите DBF-файл eer1.dbf!")
            return
        if not os.path.isdir(output_dir):
            messagebox.showerror("Ошибка", "Выберите папку для сохранения!")
            return

        selected_indices = listbox_fields.curselection()
        if not selected_indices:
            messagebox.showerror("Ошибка", "Выберите хотя бы одно месторождение!")
            return

        selected_fields = [list(FIELDS.keys())[i] for i in selected_indices]
        
        try:
            results = run_processing(dbf_path, eer1_path, selected_fields, output_dir)
            if results:
                messagebox.showinfo("Готово", "Файлы успешно созданы:\n" + "\n".join(results))
            else:
                messagebox.showinfo("Готово", "Операция завершена. Файлы не были созданы, так как данные не были найдены или загружены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    font = ("Arial", 14)
    
    # Интерфейс для файла plast.dbf
    tk.Label(root, text="Выберите DBF-файл plast.dbf:", font=font).pack(anchor="w")
    frame_file = tk.Frame(root)
    frame_file.pack(fill="x")
    entry_file = tk.Entry(frame_file, width=50, font=font)
    entry_file.pack(side="left", fill="x", expand=True)
    entry_file.insert(0, DEFAULT_DBF)
    tk.Button(frame_file, text="Выбрать", command=lambda: choose_file(entry_file), font=font).pack(side="right")
    
    # Интерфейс для файла eer1.dbf
    tk.Label(root, text="Выберите DBF-файл eer1.dbf:", font=font).pack(anchor="w")
    frame_eer1 = tk.Frame(root)
    frame_eer1.pack(fill="x")
    entry_eer1 = tk.Entry(frame_eer1, width=50, font=font)
    entry_eer1.pack(side="left", fill="x", expand=True)
    entry_eer1.insert(0, DEFAULT_EER1)
    tk.Button(frame_eer1, text="Выбрать", command=lambda: choose_file(entry_eer1), font=font).pack(side="right")
    
    # Интерфейс для папки сохранения
    tk.Label(root, text="Папка для сохранения:", font=font).pack(anchor="w")
    frame_output = tk.Frame(root)
    frame_output.pack(fill="x")
    entry_output = tk.Entry(frame_output, width=50, font=font)
    entry_output.pack(side="left", fill="x", expand=True)
    entry_output.insert(0, DEFAULT_OUTPUT_DIR)
    tk.Button(frame_output, text="Выбрать", command=choose_output, font=font).pack(side="right")
    
    # Список месторождений
    tk.Label(root, text="Выберите месторождения (можно несколько):", font=font).pack(anchor="w")
    listbox_fields = tk.Listbox(root, selectmode=tk.MULTIPLE, height=len(FIELDS), font=font)
    for name in FIELDS.values():
        listbox_fields.insert(tk.END, name)
    listbox_fields.pack(fill="both", expand=True)

    tk.Button(root, text="Запустить скрипт", command=start, font=font).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
