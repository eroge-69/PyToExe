import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import re

def main():
    # Открываем диалоговое окно
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Выберите текстовый файл",
        filetypes=[("Text files", "*.txt")]
    )

    if not file_path:
        print("Файл не выбран.")
        return

    try:
        # Чтение таблицы с табуляцией
        df = pd.read_csv(file_path, sep='\t', dtype=str)

        # Проверка наличия нужных колонок
        if 'Konzentration' not in df.columns:
            print("Колонка 'Konzentration' не найдена.")
            return
        if df.shape[1] < 5:
            print("Файл должен содержать как минимум 5 колонок.")
            return

        # Извлекаем нужные данные
        probe_ids = df.iloc[:, 4]  # Пятая колонка
        koncentration = pd.to_numeric(df['Konzentration'], errors='coerce')

        # Ищем только те строки, где проба соответствует шаблону 12345-1
        pattern = re.compile(r'^\d{5}-\d$')
        mask = probe_ids.str.match(pattern)

        filtered_df = pd.DataFrame({
            'Probe': probe_ids[mask],
            'Konzentration': koncentration[mask]
        }).dropna()

        # Разделение по группам
        group1 = filtered_df[filtered_df['Konzentration'] < 0.5].sort_values('Konzentration')['Probe']
        group2 = filtered_df[(filtered_df['Konzentration'] >= 0.5) & (filtered_df['Konzentration'] <= 1)].sort_values('Konzentration')['Probe']
        group3 = filtered_df[filtered_df['Konzentration'] > 1].sort_values('Konzentration')['Probe']

        # Формируем строки
        line1 = ';'.join(group1)
        line2 = ';'.join(group2)
        line3 = ';'.join(group3)

        # Имя выходного файла
        date_str = datetime.today().strftime('%Y-%m-%d')
        output_filename = f"{date_str}_EOX_ready.txt"

        # Запись в файл
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(line1 + '\n')
            f.write(line2 + '\n')
            f.write("Achtung!: " + line3 + '\n')

        print(f"Готово! Файл сохранен как: {output_filename}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()