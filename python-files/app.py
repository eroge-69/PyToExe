import tkinter as tk
import subprocess
import sys

def open_apps():
    # Открываем Блокнот
    subprocess.Popen(["notepad.exe"])
    
    # Открываем Paint
    subprocess.Popen(["mspaint.exe"])

# Создаем главное окно
root = tk.Tk()
root.title("Открыть Блокнот и Paint")
root.geometry("300x150")

# Создаем кнопку
button = tk.Button(
    root,
    text="Открыть Блокнот и Paint",
    command=open_apps,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 14),
    padx=20,
    pady=10,
    relief="raised",
    borderwidth=3
)
button.pack(pady=40)

# Запускаем главный цикл
root.mainloop()