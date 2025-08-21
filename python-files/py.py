import os
import re

def natural_sort_key(s):
    """
    Ключ для естественной сортировки (1, 2, 10 вместо 1, 10, 2)
    """
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

def collect_text_files_natural_order():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "combined_txt.txt")
    
    # Получаем и сортируем папки с естественной сортировкой
    all_items = os.listdir(script_dir)
    folders = [item for item in all_items if os.path.isdir(os.path.join(script_dir, item))]
    folders.sort(key=natural_sort_key)
    
    # Собираем файлы в порядке папок
    txt_files = []
    for folder in folders:
        file_path = os.path.join(script_dir, folder, "_тхт.txt")
        if os.path.exists(file_path):
            txt_files.append(file_path)
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"Количество файлов: {len(txt_files)}\n")
        output_file.write("=" * 50 + "\n\n")
        
        for i, file_path in enumerate(txt_files, 1):
            try:
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    content = input_file.read()
                
                folder_name = os.path.basename(os.path.dirname(file_path))
                # output_file.write(f"{folder_name}\n")
                # output_file.write(f"Путь: {file_path}\n")
                output_file.write("-" * 30 + "\n")
                output_file.write(content)
                
                if i < len(txt_files):
                    output_file.write("\n" + "=" * 50 + "\n\n")
                    
            except Exception as e:
                print(f"Ошибка: {file_path} - {e}")
    
    
    print(f"Файл создан: {output_path}")
    print("Порядок сохранен согласно !!!ЧИСЛОВОЙ!!! сортировке папок")
    print('\n\n\n')
    print(f"Обработано файлов: {len(txt_files)}")

if __name__ == "__main__":
    collect_text_files_natural_order()