import os
import pyautogui
import requests
from datetime import datetime

# Укажите путь для сохранения скриншота на диск C
path = r'C:\11234'

# Создайте папку, если она не существует
if not os.path.exists(path):
    os.makedirs(path)

# Захватите скриншот
screenshot = pyautogui.screenshot()

# Сформируйте имя файла с текущей датой и временем
filename = os.path.join(path, f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')

# Сохраните скриншот
screenshot.save(filename)

print(f"Скриншот сохранен по пути: {filename}")

# Загружаем файл на Workupload
url = 'https://workupload.com/upload'  # URL для загрузки
files = {'file': open(filename, 'rb')}  # Открываем файл для чтения в бинарном режиме

# Отправляем POST-запрос
response = requests.post(url, files=files)

# Проверяем статус ответа
if response.status_code == 200:
    print("Файл успешно загружен!")
    print("Ответ от сервера:", response.text)  # Выводим ответ сервера
else:
    print("Ошибка при загрузке файла:", response.status_code)

