import pyautogui
import os
import pygetwindow as gw
import glob
import math


def open_files():
    # Путь к директории с файлами VNC
    path = "C:\\VNC"

    # Получаем список всех .vnc файлов в директории
    file_names = glob.glob(os.path.join(path, "*.vnc"))

    if not file_names:
        print("No .vnc files found in the directory")
        return

    # Получаем ширину и высоту экрана
    screen_width, screen_height = pyautogui.size()

    # Определяем количество файлов
    num_files = len(file_names)

    # Рассчитываем оптимальное количество столбцов и строк для сетки
    # Можно задать фиксированное количество столбцов или рассчитать автоматически
    num_columns = math.ceil(math.sqrt(num_files))  # Квадратный корень для примерного баланса
    num_rows = math.ceil(num_files / num_columns)

    # Рассчитываем размер каждого окна
    window_width = int(screen_width / num_columns)
    window_height = int(screen_height / num_rows)

    # Открываем файлы и размещаем окна
    for index, file_path in enumerate(file_names):
        # Открываем файл
        os.system(f'start "" "{file_path}"')
        pyautogui.sleep(1)  # Ждем открытия окна

        # Получаем последнее активное окно
        window = gw.getActiveWindow()

        if window is not None:
            # Рассчитываем позицию окна в сетке
            col = index % num_columns
            row = index // num_columns

            x = col * window_width
            y = row * window_height

            # Изменяем размер и перемещаем окно
            window.resizeTo(window_width, window_height)
            window.moveTo(x, y)


open_files()