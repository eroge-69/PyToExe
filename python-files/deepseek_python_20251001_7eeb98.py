import pandas as pd
import os
import sys

def main():
    try:
        # Получаем путь к папке, где находится EXE-файл
        if getattr(sys, 'frozen', False):
            # Если запущен как EXE
            folder_path = os.path.dirname(sys.executable)
        else:
            # Если запущен как скрипт
            folder_path = os.path.dirname(os.path.abspath(__file__))
        
        print(f"Ищем файлы в папке: {folder_path}")
        print("Обработка...")
        
        # Список для хранения DataFrame'ов
        all_data = []
        processed_files = []
        
        # Проходим по всем файлам в папке
        for file in os.listdir(folder_path):
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('combined_file'):
                file_path = os.path.join(folder_path, file)
                print(f"Обрабатывается файл: {file}")
                
                # Читаем файл
                df = pd.read_excel(file_path)
                all_data.append(df)
                processed_files.append(file)
        
        if not all_data:
            print("Не найдено Excel файлов для обработки!")
            input("Нажмите Enter для выхода...")
            return
        
        # Объединяем все DataFrame в один
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Сохраняем результат в новый файл
        output_file = 'combined_file.xlsx'
        combined_df.to_excel(output_file, index=False)
        
        print(f"\nУспешно объединено!")
        print(f"Обработано файлов: {len(processed_files)}")
        print(f"Результирующий файл: {output_file}")
        print(f"Размер объединенных данных: {len(combined_df)} строк")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()