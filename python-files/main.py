import os

# Укажите путь к папке
folder_path = r"C:\Users\Public\Documents"

# Получаем список файлов
for file_name in os.listdir(folder_path):
    full_path = os.path.join(folder_path, file_name)
    if os.path.isfile(full_path):
        print(f"Имя файла: {file_name}")
        print(f"Ссылка: {full_path}")
        print("-----------------------------")
