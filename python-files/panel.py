import tkinter as tk
import os
import sys
from tkinter import messagebox

def shutdown():
    if not messagebox.askyesno("Подтверждение", "Вы действительно хотите выключить компьютер?"):
        return
    if sys.platform.startswith('win'):
        os.system("shutdown /s /t 0")
    elif sys.platform.startswith('linux'):
        os.system("sudo shutdown -h now")
    else:
        messagebox.showerror("Ошибка", "Неподдерживаемая платформа")

def reboot():
    if not messagebox.askyesno("Подтверждение", "Вы действительно хотите перезагрузить компьютер?"):
        return
    if sys.platform.startswith('win'):
        os.system("shutdown /r /t 0")
    elif sys.platform.startswith('linux'):
        os.system("sudo reboot")
    else:
        messagebox.showerror("Ошибка", "Неподдерживаемая платформа")

def create_gui():
    root = tk.Tk()
    root.title("Панель выключения")
    root.geometry("300x120")
    root.resizable(False, False)

    # Контейнер для размещения кнопок
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    # Кнопка «Выключить» слева
    btn_shutdown = tk.Button(
        frame, text="Выключить", width=12, command=shutdown
    )
    btn_shutdown.pack(side="left", padx=20, pady=20)

    # Кнопка «Перезагрузить» справа
    btn_reboot = tk.Button(
        frame, text="Перезагрузить", width=12, command=reboot
    )
    btn_reboot.pack(side="right", padx=20, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
