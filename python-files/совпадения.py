import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess  # Импортируем модуль для открытия папки


def process_files():
    folder_path = folder_path_var.get()
    column_name = column_name_var.get()
    additional_column_name = additional_column_name_var.get()  # Получаем имя дополнительного столбца
    min_matches = min_matches_var.get()

    if not folder_path or not column_name:
        messagebox.showerror("Ошибка", "Пожалуйста, укажите путь к папке и имя основного столбца.")
        return

    try:
        min_matches = int(min_matches)  # Преобразуем введенное значение в целое число
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для минимального количества совпадений.")
        return

    value_files_dict = {}

    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_excel(file_path)

            if column_name in df.columns:
                unique_values = df[column_name].dropna().unique()
                for value in unique_values:
                    if value not in value_files_dict:
                        value_files_dict[value] = []
                    value_files_dict[value].append(filename)

    # Используем значение min_matches для фильтрации
    result_dict = {value: files for value, files in value_files_dict.items() if len(files) >= min_matches}

    result_df = pd.DataFrame(list(result_dict.items()), columns=['Value', 'Files'])
    result_df['Count'] = result_df['Files'].apply(len)

    # Проверяем наличие данных в дополнительном столбце и добавляем информацию в результат
    if additional_column_name:
        additional_data = []
        for value in result_df['Value']:
            unique_additional_data = set()  # Множество для хранения уникальных значений из дополнительного столбца
            for filename in value_files_dict[value]:
                file_path = os.path.join(folder_path, filename)
                df = pd.read_excel(file_path)
                if additional_column_name in df.columns:
                    # Получаем данные из дополнительного столбца для текущего значения
                    data = df[df[column_name] == value][additional_column_name].dropna().tolist()
                    unique_additional_data.update(data)  # Добавляем данные в множество
            # Берем одно значение из множества, если оно не пустое
            additional_data.append(next(iter(unique_additional_data), '') if unique_additional_data else '')

        result_df[additional_column_name] = additional_data  # Добавляем новый столбец в DataFrame

    output_file = 'совпадения.xlsx'
    result_df.to_excel(output_file, index=False)

    messagebox.showinfo("Готово", f"Результаты сохранены в файл: {output_file}")

    # Открываем папку с результатами
    output_folder = os.path.dirname(os.path.abspath(output_file))
    os.startfile(output_folder)  # Для Windows




def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_var.set(folder_selected)


# Создаем главное окно
root = tk.Tk()
root.title("Обработка Excel файлов")

# Создаем переменные для хранения значений
folder_path_var = tk.StringVar()
column_name_var = tk.StringVar()
additional_column_name_var = tk.StringVar()  # Новая переменная для дополнительного столбца
min_matches_var = tk.StringVar()  # Переменная для минимального количества совпадений

# Создаем элементы интерфейса
tk.Label(root, text="Путь к папке:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Обзор", command=browse_folder).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Имя основного столбца:").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=column_name_var).grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Имя дополнительного столбца:").grid(row=2, column=0, padx=10, pady=10)  # Метка для нового поля
tk.Entry(root, textvariable=additional_column_name_var).grid(row=2, column=1, padx=10, pady=10)  # Поле для ввода

tk.Label(root, text="Минимум совпадений:").grid(row=3, column=0, padx=10, pady=10)  # Метка для нового поля
tk.Entry(root, textvariable=min_matches_var).grid(row=3, column=1, padx=10, pady=10)  # Поле для ввода

tk.Button(root, text="Обработать", command=process_files).grid(row=4, columnspan=3, pady=20)

# Запускаем главный цикл
root.mainloop()