import os
import sys
import ctypes
import keyboard
import tkinter as tk
from tkinter import messagebox

def block_f11():
    # Блокировка F11 с помощью хука
    keyboard.block_key('f11')

def maximize_cmd():
    # Открытие cmd в полноэкранном режиме
    os.system('start /max cmd /k mode con: cols=1000 lines=1000')

def unlock(password_entry):
    # Проверка пароля
    if password_entry.get() == "12345":
        messagebox.showinfo("Успех", "Разблокировано! Выход...")
        keyboard.unhook_all()  # Разблокировать все клавиши
        sys.exit()  # Завершить программу
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")

def create_unlock_window():
    # Создание окна для ввода пароля
    root = tk.Tk()
    root.title("Разблокировка")
    root.geometry("300x150")
    root.attributes("-topmost", True)  # Поверх всех окон

    tk.Label(root, text="Введите пароль для разблокировки:").pack(pady=10)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)
    
    tk.Button(root, text="Разблокировать", command=lambda: unlock(password_entry)).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    # Проверка прав администратора (для блокировки клавиш)
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    maximize_cmd()  # Запуск cmd в полноэкранном режиме
    block_f11()     # Блокировка F11
    create_unlock_window()  # Окно разблокировки