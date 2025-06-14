from tkinter import *
import subprocess

window = Tk()
window.title("VLESS Launcher")
window.geometry("300x200")
window.resizable(False, False)

status_label = Label(window, text="Статус: отключено", fg="red", font=("Arial", 12))
status_label.pack(pady=20)

def start_vless():
    status_label.config(text="Статус: подключено", fg="green")

def stop_vless():
    status_label.config(text="Статус: отключено", fg="red")

start_button = Button(window, text="Включить обход", command=start_vless, bg="lightgreen", width=20)
start_button.pack(pady=10)

stop_button = Button(window, text="Выключить обход", command=stop_vless, bg="lightcoral", width=20)
stop_button.pack(pady=10)

window.mainloop()
