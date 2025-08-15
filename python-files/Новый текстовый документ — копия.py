import webbrowser
import requests
import subprocess
import tempfile

url = "https://github.com/Fr1kse/govnocode/releases/latest/download/govnocode.exe"

# Показать пользователю информацию о файле
print(f"Скачивание программы из: {url}")
choice = input("Продолжить установку? (y/n): ")

if choice.lower() == 'y':
    try:
        # Скачать с индикацией прогресса
        response = requests.get(url, stream=True)
        temp_path = tempfile.mktemp(suffix='.exe')
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Запуск с уведомлением
        print("Запуск программы...")
        subprocess.Popen(temp_path)
    except Exception as e:
        print(f"Ошибка: {e}")
else:
    print("Установка отменена")
