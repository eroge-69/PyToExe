import pandas as pd
import os
from pathlib import Path
import sys
import re
import shutil

def find_header_row(file_path):
    """Находит строку с заголовком таблицы по 4-му столбцу"""
    try:
        # Читаем первые 20 строк для поиска заголовка
        temp_df = pd.read_excel(file_path, sheet_name='Выделенные причины', header=None, nrows=20)
        
        # Ищем строку с ожидаемым заголовком в 4-м столбце
        for i, row in temp_df.iterrows():
            if len(row) > 3 and str(row[3]).strip() == 'Запрош. дата':
                return i
        return None
    except Exception as e:
        print(f"    Ошибка при поиске заголовка: {str(e)}")
        return None

def extract_date_from_filename(filename):
    """Извлекает дату из названия файла в формате ГГГГ.ММ.ДД"""
    # Ищем последовательность из 8 цифр (формат ГГГГММДД)
    match = re.search(r'(\d{8})', filename)
    if match:
        date_str = match.group(1)
        try:
            # Форматируем дату в нужный формат
            return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
        except:
            return None
    return None

def verify_integrity(original_df, saved_path):
    """Проверяет целостность сохраненных данных"""
    try:
        # Читаем сохраненный файл
        saved_df = pd.read_excel(saved_path)
        
        # Сравниваем размеры
        if original_df.shape == saved_df.shape:
            print(f"\nПроверка целостности: УСПЕШНО (строк: {original_df.shape[0]}, столбцов: {original_df.shape[1]})")
            return True
        else:
            print(f"\nПроверка целостности: ОШИБКА!")
            print(f"  Оригинальные данные: {original_df.shape[0]} строк, {original_df.shape[1]} столбцов")
            print(f"  Сохраненные данные: {saved_df.shape[0]} строк, {saved_df.shape[1]} столбцов")
            return False
    except Exception as e:
        print(f"\nОшибка при проверке целостности: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("Скрипт для объединения Excel-файлов")
    print("=" * 50)
    
    # Запрос пути к исходным файлам
    input_path = input("\nВведите путь к папке с исходными файлами: ").strip()
    
    # Проверка существования пути
    folder_path = Path(input_path)
    if not folder_path.exists() or not folder_path.is_dir():
        print("\nОшибка: Указанный путь не существует или не является папкой")
        input("Нажмите Enter для выхода...")
        return

    # Запрос пути для сохранения
    output_folder = input("\nВведите путь для сохранения результата (оставьте пустым для сохранения в текущей папке): ").strip()
    if not output_folder:
        output_folder = Path.cwd()
    else:
        output_folder = Path(output_folder)
        if not output_folder.exists():
            print(f"\nСоздаем папку для сохранения: {output_folder}")
            output_folder.mkdir(parents=True, exist_ok=True)

    # Поиск всех Excel-файлов
    files = list(folder_path.glob('*.xlsx'))
    if not files:
        print("\nВ указанной папке не найдено Excel-файлов")
        input("Нажмите Enter для выхода...")
        return

    all_dfs = []
    total_files = len(files)
    processed_files = 0
    
    print(f"\nНайдено файлов: {total_files}")
    print("=" * 50)
    print("Начинаем обработку...")
    
    # Обработка каждого файла
    for i, file_path in enumerate(files):
        # Расчет прогресса
        progress = (i + 1) / total_files * 100
        print(f"\nОбработка файла {i+1}/{total_files} ({progress:.1f}%): {file_path.name}")
        
        try:
            # Поиск строки с заголовком
            header_row = find_header_row(file_path)
            if header_row is None:
                print("    Не найдена строка заголовка с 'Запрош. дата' в 4-м столбце. Пропускаем файл.")
                continue

            # Чтение данных с найденной строки заголовка
            df = pd.read_excel(
                file_path,
                sheet_name='Выделенные причины',
                header=header_row
            )
            
            # Добавление колонок в начало таблицы
            df.insert(0, 'Имя файла', file_path.name)
            file_date = extract_date_from_filename(file_path.name)
            df.insert(1, 'Дата из названия', file_date)
            
            all_dfs.append(df)
            processed_files += 1
            print("    Успешно обработан")
            
        except Exception as e:
            print(f"    Ошибка при обработке файла: {str(e)}")

    # Объединение результатов
    if not all_dfs:
        print("\nНет данных для сохранения")
        input("Нажмите Enter для выхода...")
        return

    final_df = pd.concat(all_dfs, ignore_index=True)
    
    # Сохранение результата
    output_path = output_folder / "СВОД_результат.xlsx"
    final_df.to_excel(output_path, index=False)
    print(f"\nРезультат сохранен в файл: {output_path}")
    
    # Проверка целостности
    print("\nПроверка целостности данных...")
    if verify_integrity(final_df, output_path):
        print("Все данные успешно сохранены без потерь.")
    else:
        print("Обнаружены расхождения в сохраненных данных!")
    
    # Создание резервной копии
    try:
        backup_path = output_folder / "СВОД_резервная_копия.xlsx"
        shutil.copyfile(output_path, backup_path)
        print(f"\nСоздана резервная копия: {backup_path}")
    except Exception as e:
        print(f"\nНе удалось создать резервную копию: {str(e)}")
    
    print("\nОбработка завершена!")
    print(f"Успешно обработано файлов: {processed_files}/{total_files}")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")