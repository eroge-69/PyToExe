import os

def manage_files_and_folders():
    current_directory = os.getcwd()
    
    folder_name = input("Введите имя папки (оставьте пустое поле для значения по умолчанию 'my_folder'): ").strip()
    if not folder_name:
        folder_name = "my_folder"
    
    folder_path = os.path.join(current_directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        print(f"Папка '{folder_name}' была успешно создана в {current_directory}.")
    else:
        print(f"Папка '{folder_name}' уже существует.")
    
    while True:
        action = input("\nЧто вы хотите сделать?\n"
                       "1. Сохранить данные в файл\n"
                       "2. Посмотреть существующие файлы и вывести их содержимое\n"
                       "q. Выход\n").strip().lower()
        
        if action == 'q':
            break
        
        elif action == '1':  
            filename = input("Введите имя файла (без расширения .txt): ").strip() + '.txt'
            content = input("Введите данные для сохранения: ").strip()
            
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"Данные были успешно сохранены в {file_path}.")
        
        elif action == '2':  
            files_in_folder = os.listdir(folder_path)
            text_files = [f for f in files_in_folder if f.endswith(".txt")]
            
            if text_files:
                print("Список доступных файлов:")
                for idx, file in enumerate(text_files, start=1):
                    print(f"{idx}. {file}")
                
                select_idx = int(input("Выберите индекс файла для просмотра (или 0 для отмены): "))
                if select_idx != 0 and 1 <= select_idx <= len(text_files):
                    chosen_file = text_files[select_idx - 1]
                    file_to_read = os.path.join(folder_path, chosen_file)
                    with open(file_to_read, 'r') as f:
                        print(f"Содержимое файла '{chosen_file}':\n{f.read()}")
                else:
                    print("Операция отменена.")
            else:
                print("В папке нет текстовых файлов.")
        
        else:
            print("Ошибка ввода. Повторите попытку.")

if __name__ == "__main__":
    manage_files_and_folders()