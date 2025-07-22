import os
import sys
import time
import random
import ctypes
import subprocess
import shutil
from ctypes import wintypes

# Конфигурация
IDLE_TIME_LIMIT = 2 # 10 минут в секундах
CHECK_INTERVAL = 0  # Проверка бездействия каждые 5 секунд
SCREENSAVERS_DIR = "screensavers"


def get_idle_time():
    """Возвращает время бездействия пользователя в секундах"""

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("dwTime", ctypes.c_uint)
        ]

    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))

    current_time = ctypes.windll.kernel32.GetTickCount()
    idle_time = (current_time - last_input_info.dwTime) // 1000
    return idle_time


def show_screensaver(image_path):
    """Показывает изображение как скринсейвер используя системную программу"""
    try:
        # Используем стандартную программу просмотра изображений Windows
        subprocess.Popen(
            ['rundll32.exe',
             'shimgvw.dll,ImageView_Fullscreen',
             image_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        print(f"Ошибка показа скринсейвера: {e}")
        return False


def add_to_startup():
    """Добавляет программу в автозагрузку простым копированием"""
    try:
        # Определяем путь к папке автозагрузки
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )

        # Создаем копию программы в автозагрузке
        script_path = os.path.abspath(__file__)
        startup_exe = os.path.join(startup_path, "RandomScreensaver.exe")

        # Если мы не exe-файл, пытаемся создать exe-копию
        if not script_path.lower().endswith('.exe'):
            # Пытаемся найти PyInstaller или создаем простую копию
            if shutil.which('pyinstaller'):
                # Создаем exe-версию
                subprocess.run([
                    'pyinstaller',
                    '--onefile',
                    '--windowed',
                    '--name', 'RandomScreensaver',
                    script_path
                ], check=True)
                exe_src = os.path.join('dist', 'RandomScreensaver.exe')
                shutil.copy(exe_src, startup_exe)
            else:
                # Просто копируем скрипт
                shutil.copy(script_path, os.path.join(startup_path, "RandomScreensaver.py"))
        else:
            shutil.copy(script_path, startup_exe)

        return True
    except Exception as e:
        print(f"Ошибка добавления в автозагрузку: {e}")
        return False


def ensure_screensavers_dir():
    """Создает папку для скринсейверов если нужно"""
    if not os.path.exists(SCREENSAVERS_DIR):
        os.makedirs(SCREENSAVERS_DIR)
        print(f"Создана папка {SCREENSAVERS_DIR}. Добавьте в нее изображения для скринсейверов.")
        return False
    return True


def main():
    # Проверяем и создаем папку для скринсейверов
    if not ensure_screensavers_dir():
        return

    # Добавляем в автозагрузку (только при первом запуске)
    if '--first-run' in sys.argv:
        add_to_startup()

    # Основной цикл программы
    last_screensaver_time = 0
    active_screensaver = None

    while True:
        idle_time = get_idle_time()

        # Проверяем время бездействия
        if idle_time >= IDLE_TIME_LIMIT:
            # Получаем список скринсейверов
            try:
                screensavers = [
                    f for f in os.listdir(SCREENSAVERS_DIR)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
                ]

                if screensavers:
                    # Выбираем случайный скринсейвер
                    chosen = random.choice(screensavers)
                    image_path = os.path.join(SCREENSAVERS_DIR, chosen)

                    # Закрываем предыдущий скринсейвер
                    if active_screensaver:
                        try:
                            active_screensaver.terminate()
                        except:
                            pass

                    # Показываем новый скринсейвер
                    active_screensaver = show_screensaver(image_path)
                    last_screensaver_time = time.time()

            except Exception as e:
                print(f"Ошибка: {e}")

        # Закрываем скринсейвер при активности пользователя
        if active_screensaver and idle_time < 5:
            try:
                # Закрываем все окна просмотра изображений
                os.system('taskkill /f /im rundll32.exe > nul 2>&1')
                active_screensaver = None
            except:
                pass

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    # Скрываем консольное окно
    if sys.platform == 'win32':
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Запускаем основную программу в фоне
    main()