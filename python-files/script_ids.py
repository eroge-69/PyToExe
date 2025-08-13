import os
from datetime import datetime
folder_path = input("Введите путь к папке Steam: ") + "\\userdata"

# Проверка существования пути
if os.path.exists(folder_path):
    
    # 1. Получаем дату последнего изменения папки
    timestamp = os.path.getmtime(folder_path)
    last_modified = datetime.fromtimestamp(timestamp)
    formatted_date = last_modified.strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Получаем айди всех аккаунты в папке (файлы и папки)
    accounts = os.listdir(folder_path)
    print("========================")
    print(formatted_date)
    print("========================")
    for i in accounts:
        print(i)

else:
    print("Неверно указана папка Steam!!!")

input("Нажмите Enter для выхода.")



