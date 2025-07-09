import sys
import os
import re
import subprocess

# Установка необходимых библиотек
required = ['pandas', 'openpyxl', 'xlrd']
for package in required:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import pandas as pd
from tkinter import Tk, filedialog, messagebox

# Отключаем главное окно tkinter
root = Tk()
root.withdraw()

# === Выбор Excel-файла ===
input_file = filedialog.askopenfilename(
    title="Выберите Excel-файл (.xls или .xlsx)",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not input_file:
    print("Файл не выбран. Завершение.")
    sys.exit(1)

file_ext = os.path.splitext(input_file)[1].lower()
if file_ext == '.xls':
    engine = 'xlrd'
elif file_ext == '.xlsx':
    engine = 'openpyxl'
else:
    messagebox.showerror("Ошибка", "Поддерживаются только файлы .xls и .xlsx")
    sys.exit(1)

# === Чтение Excel-файла ===
xlsx = pd.ExcelFile(input_file, engine=engine)

# Пустой DataFrame для сбора результатов
grouped_values_df = pd.DataFrame(columns=['Sheet', 'Hour', 'Value'])

# Функция извлечения номера из имени листа
def extract_number(sheet_name):
    number = re.findall(r'\d+', sheet_name)
    return int(number[0]) if number else 0

# Обработка каждого листа
for sheet_name in xlsx.sheet_names:
    df = pd.read_excel(xlsx, sheet_name=sheet_name, engine=engine)

    # Поиск времени в формате h:mm:ss
    time_pattern = r'(\b\d{1,2}:\d{2}:\d{2}\b)'
    time_values = df.stack().astype(str).str.extractall(time_pattern)

    if not time_values.empty:
        time_values['Time'] = pd.to_datetime(time_values[0], format='%H:%M:%S', errors='coerce').dt.time
        time_values['Hour'] = pd.to_datetime(time_values['Time'], format='%H:%M:%S', errors='coerce').dt.hour
        time_values = time_values.dropna()
        time_values = time_values.rename(columns={0: 'Value'})
        time_values['Sheet'] = sheet_name
        grouped_values_df = pd.concat([grouped_values_df, time_values[['Sheet', 'Hour', 'Value']]])

# Группировка значений
grouped_values_df = grouped_values_df.groupby(['Sheet', 'Hour'])['Value'].apply(list).reset_index()

# Сводная таблица
pivot_df = grouped_values_df.pivot(index='Hour', columns='Sheet', values='Value').reset_index()

# Сортировка столбцов по имени листа
sorted_columns = sorted(pivot_df.columns[1:], key=extract_number)
pivot_df = pivot_df[['Hour'] + sorted_columns]

# Преобразование списков в строки
for column in pivot_df.columns[1:]:
    pivot_df[column] = pivot_df[column].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)

# === Выбор пути сохранения ===
save_path = filedialog.asksaveasfilename(
    title="Сохранить как",
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")],
    initialfile="processed_data.xlsx"
)

if not save_path:
    print("Сохранение отменено.")
    sys.exit(0)

# Сохраняем файл
with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
    pivot_df.to_excel(writer, sheet_name='Processed Data', index=False)

# === Сообщение об успехе ===
messagebox.showinfo("Готово", f"Файл успешно сохранён:\n{save_path}")
