import tkinter as tk
import os
import sys

def block_input(event=None):
    return "break"  # Блокирует любые нажатия клавиш

def disable_close():
    pass  # Игнорирует попытки закрыть окно

# Создаём окно
root = tk.Tk()
root.attributes("-fullscreen", True)  # Полный экран
root.configure(bg="#0078D7")  # Цвет BSOD в Windows 10/11
root.title("Windows")
root.protocol("WM_DELETE_WINDOW", disable_close)  # Отключаем кнопку закрытия
root.overrideredirect(True)  # Убираем рамки окна

# Блокируем Win, Alt+Tab, Ctrl+Alt+Del и другие комбинации
root.bind_all("<KeyPress>", block_input)
root.bind_all("<Button-1>", block_input)
root.bind_all("<Button-2>", block_input)
root.bind_all("<Button-3>", block_input)

# Текст BSOD
message = """
:(

Your PC ran into a problem and needs to restart.
We're just collecting some error info, and then we'll restart for you.

0% complete

For more information about this issue and possible fixes,
visit https://windows.com/stopcode

If you call a support person, give them this info:
Stop code: KERNEL_MODE_EXCEPTION_NOT_HANDLED

...or just press Ctrl+Alt+Del to wake me up 😉
"""

label = tk.Label(
    root,
    text=message,
    bg="#0078D7",
    fg="white",
    font=("Consolas", 16),
    justify="left",
    wraplength=root.winfo_screenwidth() - 100
)
label.pack(expand=True)

# Чтобы выйти — нажать Ctrl+Alt+Del (на самом деле просто Escape или клик мышкой)
def exit_bsod(event=None):
    root.destroy()
    sys.exit()

# Разрешаем выход только по Escape (можно заменить на любую другую комбинацию)
root.bind_all("<Escape>", exit_bsod)
root.bind_all("<Button-1>", exit_bsod)  # Клик мышкой — тоже выход

# Запуск
root.mainloop()