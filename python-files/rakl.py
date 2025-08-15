import pygetwindow as gw
import time
import threading
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image
import os


# Функция для сворачивания всех окон
def minimize_all_windows():
    while not exit_flag.is_set():
        try:
            windows = gw.getAllWindows()
            for window in windows:
                if window.isMinimized is False:
                    window.minimize()
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(10)


# Функция для выхода из программы
def exit_program(icon, item):
    exit_flag.set()
    icon.stop()
    os._exit(0)


# Функция для создания иконки в трее
def setup_tray_icon():
    # Создаем изображение для иконки (просто черный квадрат)
    image = Image.new('RGB', (16, 16), color='black')

    menu = Menu(
        MenuItem('Выход', exit_program)
    )

    icon = Icon("Window Minimizer", image, "Window Minimizer", menu)
    icon.run()


if __name__ == "__main__":
    exit_flag = threading.Event()

    # Запускаем поток для сворачивания окон
    threading.Thread(target=minimize_all_windows, daemon=True).start()

    # Запускаем иконку в трее
    setup_tray_icon()