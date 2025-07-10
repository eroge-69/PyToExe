import os
import subprocess
import time
import sys

# --- Настройки ---
# Укажите URL-адрес, который должен открываться при запуске.
TARGET_URL = "http://contacts.nssz.local/"

# --- Укажите полный путь к исполняемому файлу chrome.exe ---
# Скрипт попытается найти его в стандартных папках.
# Если ваш браузер установлен в другом месте, укажите правильный путь вручную.

CHROME_PATHS = [
    os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
    os.path.join(os.environ.get("LocalAppData", ""), "Google", "Chrome", "Application", "chrome.exe"),
]

BROWSER_EXECUTABLE = None
for path in CHROME_PATHS:
    if os.path.exists(path):
        BROWSER_EXECUTABLE = path
        break

# --- Логика скрипта ---
print("Запуск стандартного браузера Google Chrome...")
print()
print(f"URL: {TARGET_URL}")
print()

# Проверяем, удалось ли найти исполняемый файл браузера.
if BROWSER_EXECUTABLE is None:
    print("Ошибка: Не удалось автоматически найти chrome.exe.")
    print("Пожалуйста, найдите ярлык Google Chrome, откройте его свойства")
    print("и скопируйте путь из поля 'Объект' в переменную BROWSER_EXECUTABLE в этом скрипте.")
    print()
    # В оригинальном скрипте здесь была пауза. В Python можно просто выйти.
    sys.exit(1)

print(f"Найден браузер: {BROWSER_EXECUTABLE}")
print()

# Запускаем браузер с флагом --app, чтобы открыть URL в режиме приложения, а также с дополнительными параметрами.
try:
    command = [
        BROWSER_EXECUTABLE,
        f"--app={TARGET_URL}",
        "--allow-running-insecure-content",
        "--disable-field-trial-config"
    ]
    # Используем subprocess.Popen для запуска приложения без ожидания его завершения.
    subprocess.Popen(command)
    print("Браузер запущен.")
except FileNotFoundError:
    print(f"Ошибка: Исполняемый файл браузера не найден по пути: {BROWSER_EXECUTABLE}")
    sys.exit(1)
except Exception as e:
    print(f"Произошла ошибка при запуске браузера: {e}")
    sys.exit(1)

# Закомментируйте строку ниже, если не хотите, чтобы окно консоли закрывалось.
# В Python аналог timeout - это time.sleep().
time.sleep(2)
# sys.exit() # Необязательно, скрипт завершится сам.