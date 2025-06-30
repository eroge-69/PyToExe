import os
import subprocess
import win32api
import win32con
import time
import warnings

# Предупреждение
warnings.warn("Этот код может повредить вашу систему. Используйте только на тестовой машине!")

# Функция для создания пользователей
def create_users():
    try:
        for i in range(1, 21):
            username = f"Sasha_380_km_ot_vas_{i}"
            # Команда для создания пользователя
            subprocess.run(
                f"net user {username} Password123 /add",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Создан пользователь: {username}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании пользователя: {e}")

# Функция для создания виртуальных дисков (подключение папок как диски)
def create_fake_disks():
    try:
        for i in range(1, 21):
            folder_name = f"C:\\Tobi-Pisda_{i}"
            os.makedirs(folder_name, exist_ok=True)
            # Подключение папки как виртуальный диск (требует subst)
            drive_letter = chr(68 + i)  # D, E, F, ... (начинаем с D:)
            subprocess.run(
                f"subst {drive_letter}: {folder_name}",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Создан виртуальный диск: {drive_letter}: ({folder_name})")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании диска: {e}")

# Функция для имитации перезагрузки
def reboot_system():
    print("Инициируется перезагрузка системы...")
    subprocess.run("shutdown /r /t 5", shell=True)  # Перезагрузка через 5 секунд

# Основной код
if __name__ == "__main__":
    # Проверка административных прав
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        print("Ошибка: Этот скрипт требует административных прав!")
        exit(1)

    print("ВНИМАНИЕ: Этот скрипт может повредить вашу систему. Продолжайте только на тестовой машине!")
    confirm = input("Вы уверены, что хотите продолжить? (yes/no): ")
    if confirm.lower() != "yes":
        print("Операция отменена.")
        exit(0)

    create_users()
    create_fake_disks()
    reboot_system()