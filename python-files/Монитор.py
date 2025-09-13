import tkinter as tk
from tkinter import messagebox
import os
import platform
import subprocess
import time

def put_monitor_to_sleep():
    try:
        system = platform.system()
        
        if system == "Windows":
            # Для Windows
            import ctypes
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            
        elif system == "Darwin":  # macOS
            # Для macOS
            subprocess.run(["pmset", "displaysleepnow"])
            
        elif system == "Linux":
            # Для Linux (работает с X11)
            try:
                subprocess.run(["xset", "dpms", "force", "off"])
            except:
                # Альтернативный способ для Linux
                subprocess.run(["vbetool", "dpms", "off"])
                
        else:
            messagebox.showwarning("Предупреждение", 
                                  f"Неизвестная операционная система: {system}\n"
                                  "Функция перевода монитора в спящий режим может не работать.")
            
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось перевести монитор в спящий режим:\n{str(e)}")

# Создаем главное окно
root = tk.Tk()
root.title("Перевод монитора в спящий режим")
root.geometry("600x400")
root.configure(bg='white')

# Центрируем окно на экране
root.eval('tk::PlaceWindow . center')

# Добавляем заголовок
title_label = tk.Label(root, 
                      text="Управление монитором",
                      font=("Arial", 24, "bold"),
                      fg='black',
                      bg='white')
title_label.pack(pady=30)

# Добавляем описание
desc_label = tk.Label(root, 
                     text="Нажмите кнопку ниже, чтобы перевести монитор в спящий режим",
                     font=("Arial", 14),
                     fg='gray',
                     bg='white',
                     wraplength=400)
desc_label.pack(pady=20)

# Добавляем кнопку для перевода монитора в спящий режим
sleep_button = tk.Button(root,
                        text="🖥️ Перевести монитор в спящий режим",
                        font=("Arial", 16, "bold"),
                        fg='white',
                        bg='#2E86AB',
                        activebackground='#1C6B8C',
                        activeforeground='white',
                        relief='flat',
                        padx=30,
                        pady=15,
                        command=put_monitor_to_sleep)
sleep_button.pack(pady=40)

# Добавляем информацию о системе
system_info = f"ОС: {platform.system()} {platform.release()}"
system_label = tk.Label(root,
                       text=system_info,
                       font=("Arial", 10),
                       fg='darkgray',
                       bg='white')
system_label.pack(side='bottom', pady=10)

# Предупреждение
warning_label = tk.Label(root,
                        text="⚠️ Не забудьте сохранить все важные данные перед использованием",
                        font=("Arial", 9),
                        fg='orange',
                        bg='white')
warning_label.pack(side='bottom', pady=5)

# Запускаем главный цикл
root.mainloop()