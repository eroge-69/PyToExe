
#!/usr/bin/env python3
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import warnings
import re

os.environ["TK_SILENCE_DEPRECATION"] = "1"
warnings.filterwarnings("ignore")

def выбрать_файл(заголовок):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=заголовок, filetypes=[("Excel files", "*.xls *.xlsx *.xlsb"), ("All files", "*.*")])

def нормализовать_код(ячейка):
    if pd.isna(ячейка):
        return None
    cleaned = str(ячейка)
    cleaned = re.sub(r"[^0-9]", "", cleaned)
    return int(cleaned) if cleaned.isdigit() else None

def найти_начало_и_колонку(raw):
    for i in range(len(raw)):
        for j in range(2):
            значение = нормализовать_код(raw.iloc[i, j])
            if значение is not None:
                return i, j
    return None, None

def сравнить_транзит(transit_path, gggg_path):
    engine = "pyxlsb" if transit_path.lower().endswith(".xlsb") else "openpyxl"
    transit_df = pd.read_excel(transit_path, usecols=[1, 2, 3, 4], sheet_name=0, engine=engine)
    transit_df.columns = ["Ячейка", "Код", "Наименование", "Количество"]
    transit_df = transit_df[transit_df["Код"].notna() & transit_df["Количество"].notna()].copy()
    transit_df["Код"] = transit_df["Код"].apply(нормализовать_код)
    transit_df["Количество"] = pd.to_numeric(transit_df["Количество"], errors="coerce")
    transit_df = transit_df.dropna(subset=["Код", "Количество", "Наименование"])
    transit_df["Код"] = transit_df["Код"].astype(int)
    transit_df["Количество"] = transit_df["Количество"].round(0).astype("Int64")
    transit_df["Наименование"] = transit_df["Наименование"].astype(str).str.strip().str.lower()

    raw = pd.read_excel(gggg_path, header=None)
    start_row, код_колонка = найти_начало_и_колонку(raw)
    if start_row is None or код_колонка is None:
        raise ValueError("❌ Не удалось найти начало таблицы GGGG — проверь формат второго файла.")

    cols = [код_колонка, код_колонка + 1, код_колонка + 2]
    gggg_df = pd.read_excel(gggg_path, header=start_row, usecols=cols)
    gggg_df.columns = ["Код", "Наименование", "Количество"]
    gggg_df["Код"] = gggg_df["Код"].apply(нормализовать_код)
    gggg_df["Количество"] = pd.to_numeric(gggg_df["Количество"], errors="coerce")
    gggg_df = gggg_df.dropna(subset=["Код", "Количество", "Наименование"])
    gggg_df["Код"] = gggg_df["Код"].astype(int)
    gggg_df["Количество"] = gggg_df["Количество"].round(0).astype("Int64")
    gggg_df["Наименование"] = gggg_df["Наименование"].astype(str).str.strip().str.lower()

    grouped = transit_df.groupby(["Код", "Наименование"], as_index=False)["Количество"].sum().rename(columns={"Количество": "Транзит_суммарно"})
    merged = pd.merge(grouped, gggg_df, on=["Код", "Наименование"], how="right")
    merged["Расхождение"] = merged["Транзит_суммарно"] - merged["Количество"]

    расхождения = merged[merged["Транзит_суммарно"].notna() & merged["Расхождение"] != 0].copy()
    не_найденные = merged[merged["Транзит_суммарно"].isna()][["Код", "Наименование", "Количество"]].copy()

    detailed = pd.merge(transit_df, расхождения[["Код", "Наименование", "Расхождение"]], on=["Код", "Наименование"], how="inner")
    detailed["Расхождение"] = (
        detailed.sort_values(by="Ячейка")
        .groupby(["Код", "Наименование"])["Расхождение"]
        .transform(lambda x: [None]*(len(x)-1) + [x.iloc[-1]])
    )

    result = detailed[["Ячейка", "Код", "Наименование", "Количество", "Расхождение"]]
    is_cartridge = result["Наименование"].str.contains("картридж", case=False)
    result = pd.concat([
        result[~is_cartridge].sort_values(by="Код"),
        result[is_cartridge].sort_values(by="Код")
    ])

    base_dir = os.path.dirname(transit_path)
    result.to_excel(os.path.join(base_dir, "расхождения.xlsx"), index=False)
    не_найденные.to_excel(os.path.join(base_dir, "ненайденные.xlsx"), index=False)

    print("✅ Сравнение завершено. Файлы 'расхождения.xlsx' и 'ненайденные.xlsx' сохранены.")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    transit = выбрать_файл("Выберите файл ТРАНЗИТ")
    gggg = выбрать_файл("Выберите файл GGGG")
    сравнить_транзит(transit, gggg)
