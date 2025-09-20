import tkinter as tk
from tkinter import messagebox
import os
import platform

# Глобальная переменная для хранения ID события после root.after
shutdown_timer_id = None


def shutdown_computer():
    system = platform.system()
    try:
        if system == "Windows":
            os.system("shutdown /s /t 0")
        elif system == "Linux" or system == "Darwin":  # Darwin - macOS
            os.system("shutdown -h now")
        else:
            messagebox.showerror("Ошибка", f"Ваша ОС ({system}) не поддерживается.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить выключение: {e}")


def start_shutdown():
    global shutdown_timer_id

    # Если таймер уже запущен — предупредим пользователя
    if shutdown_timer_id is not None:
        messagebox.showinfo("Информация", "Таймер уже запущен. Отмените текущий перед запуском нового.")
        return

    try:
        minutes = int(entry.get())
        if minutes < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное положительное целое число.")
        return

    seconds = minutes * 60
    # Запускаем функцию shutdown_computer через заданное время
    shutdown_timer_id = root.after(seconds * 1000, shutdown_computer)
    messagebox.showinfo("Информация", f"Компьютер выключится через {minutes} минут.")


def cancel_shutdown():
    global shutdown_timer_id
    if shutdown_timer_id is not None:
        root.after_cancel(shutdown_timer_id)
        shutdown_timer_id = None
        messagebox.showinfo("Отмена", "Таймер выключения отменён.")
    else:
        messagebox.showinfo("Отмена", "Таймер не был запущен.")


# Создание окна
root = tk.Tk()
root.title("Таймер выключения компьютера")
root.geometry("300x180")

label = tk.Label(root, text="Введите время до выключения (минуты):")
label.pack(pady=10)

entry = tk.Entry(root, width=10)
entry.pack()

button_start = tk.Button(root, text="Запустить таймер", command=start_shutdown)
button_start.pack(pady=5)

button_cancel = tk.Button(root, text="Отмена таймера", command=cancel_shutdown)
button_cancel.pack(pady=5)

root.mainloop()