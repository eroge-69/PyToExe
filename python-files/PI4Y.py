import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def process_excel(file_path):
    # Загружаем Excel (лист General_1, заголовки со второй строки)
    df = pd.read_excel(file_path, sheet_name="General_1", header=1)

    # Переименуем для удобства
    df = df.rename(columns={
        "Unnamed: 0": "Shipment ID",
        "Unnamed: 4": "Location ID",
        "Unnamed: 6": "Pallet ID",
        "Unnamed: 8": "Pending to be picked oLPN",
        "Unnamed: 9": "Pending to be packed oLPN",
        "Unnamed: 10": "Packed oLPN",
    })

    cols_to_check = [
        "Pending to be picked oLPN",
        "Pending to be packed oLPN",
        "Packed oLPN",
    ]

    # Проверяем строки, где все три = 0
    df["AllZero"] = df[cols_to_check].eq(0).all(axis=1)

    # Проверяем по Location ID: все строки должны быть с нулями
    location_groups = df.groupby("Location ID")["AllZero"].transform("all")
    filtered = df[location_groups]

    # Берем только Shipment ID + Pallet ID
    result = filtered[["Shipment ID", "Pallet ID"]].sort_values(by="Shipment ID")

    # Группируем по Shipment ID
    grouped = result.groupby("Shipment ID")["Pallet ID"].apply(list).reset_index()

    return grouped


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Выберите Excel файл",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        messagebox.showwarning("Внимание", "Файл не выбран")
        return

    result = process_excel(file_path)

    # Формируем текст для окна
    output = ""
    for _, row in result.iterrows():
        output += f"Shipment ID: {row['Shipment ID']}\n"
        output += f"Pallet IDs: {', '.join(map(str, row['Pallet ID']))}\n\n"

    # Сохраняем в Excel
    save_path = os.path.join(os.path.dirname(file_path), "result.xlsx")
    result.to_excel(save_path, index=False)

    if output.strip():
        messagebox.showinfo("Результат",
                            f"{output}\n\nДанные также сохранены в:\n{save_path}")
    else:
        messagebox.showinfo("Результат", "Подходящих записей не найдено")


if __name__ == "__main__":
    main()
