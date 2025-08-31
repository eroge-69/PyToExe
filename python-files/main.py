import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os
import re


print("Данная программа предназначена для вертикального объединения Excel-файлов.\n"
      "Первая строка (заголовок) сохраняется только из первого файла,\n"
      "а во всех последующих файлах она автоматически удаляется.\n\n"
      "Если порядок соединения файлов важен —\n"
      "переименуйте файлы в порядке 1, 2, 3 и т.д.,\n"
      "чтобы программа обработала их в нужной последовательности.")

def merge_excel_files():
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    # Выбор нескольких файлов Excel
    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы Excel для объединения",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not file_paths:
        print("Файлы не выбраны.")
        return

    # Извлечение чисел из названий файлов для сортировки
    def extract_number(filename):
        match = re.search(r'\d+', os.path.basename(filename))
        return int(match.group()) if match else float('inf')

    # Сортировка файлов по числовому порядку
    file_paths_sorted = sorted(file_paths, key=extract_number)
    
    # Чтение первого файла с заголовком
    df_list = [pd.read_excel(file_paths_sorted[0])]
    first_columns = df_list[0].columns.tolist()
    print(f"Столбцы в первом файле ({os.path.basename(file_paths_sorted[0])}): {first_columns}")

    # Чтение оставшихся файлов, пропуская заголовок и принудительно задавая имена столбцов
    for path in file_paths_sorted[1:]:
        try:
            # Попытка определить правильную начальную строку
            for skip in range(2):  # Попытка пропустить 0 или 1 строку, если заголовок отсутствует
                df = pd.read_excel(path, skiprows=skip, names=first_columns)
                if len(df.columns) == len(first_columns):
                    break
            else:
                df = pd.read_excel(path, skiprows=1)  # Резервный вариант с автоопределением
                if len(df.columns) == len(first_columns):
                    df.columns = first_columns
                else:
                    print(f"Ошибка: Не удается выровнять столбцы для {os.path.basename(path)}. Пропуск файла.")
                    continue

            current_columns = df.columns.tolist()
            if len(current_columns) != len(first_columns):
                print(f"Предупреждение: Файл {os.path.basename(path)} имеет разное количество столбцов. Пропуск недействительных строк.")
                df = pd.read_excel(path, skiprows=1)
                if len(df.columns) == len(first_columns):
                    df.columns = first_columns
                else:
                    print(f"Ошибка: Не удается выровнять столбцы для {os.path.basename(path)}. Пропуск файла.")
                    continue
            df_list.append(df)
        except Exception as e:
            print(f"Ошибка обработки {os.path.basename(path)}: {str(e)}. Пропуск файла.")
            continue

    # Объединение всех датафреймов вертикально
    if df_list:
        merged_df = pd.concat(df_list, axis=0, ignore_index=True)
    else:
        print("Нет подходящих файлов для объединения.")
        return

    # Запрос пути для сохранения выходного файла
    output_path = filedialog.asksaveasfilename(
        title="Сохранить объединенный файл Excel",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if output_path:
        merged_df.to_excel(output_path, index=False)
        print(f"Объединенный файл сохранен в: {output_path}")
    else:
        print("Сохранение отменено.")

if __name__ == "__main__":
    merge_excel_files()