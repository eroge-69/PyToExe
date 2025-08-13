import customtkinter as ctk
from PIL import Image
import os
import subprocess
from tkinter import messagebox

# Настройка темы
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Пути
preconfigs_path = os.path.join(os.path.expanduser("~/Desktop/AllFix/pre-configs"))
icons_path = os.path.join(os.path.expanduser("~/Desktop/AllFix/icons"))

# Центрирование окна
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# Запуск .bat файла
def run_bat(file_name):
    bat_path = os.path.join(preconfigs_path, file_name)
    if os.path.exists(bat_path):
        subprocess.Popen([bat_path], shell=True)
    else:
        messagebox.showerror("Ошибка", f"Файл не найден:\n{bat_path}")

# Универсальное окно выбора
def choice_window(title, options):
    win = ctk.CTkToplevel(root)
    win.title(title)
    center_window(win, 260, 150)

    for text, file_name in options:
        ctk.CTkButton(
            win,
            text=text,
            corner_radius=15,
            width=200,
            height=35,
            command=lambda f=file_name: (run_bat(f), win.destroy())
        ).pack(pady=10)

# Функции
def discord_fix():
    choice_window("Обход Discord", [
        ("Ростелеком / Билайн", "DiscordFix (для Билайн, Ростелеком, Инфолинк).bat"),
        ("Общее", "DiscordFix.bat")
    ])

def youtube_fix():
    choice_window("Обход YouTube", [
        ("Ростелеком / Билайн", "YouTubeFix.bat"),
        ("Общее", "YoutubeFix_ALT.bat")
    ])

def ultimate_fix():
    choice_window("Все сразу", [
        ("Ростелеком / Билайн", "UltimateFix_ALT (для Билайна и Ростелеком).bat"),
        ("Общее", "UltimateFix.bat")
    ])

# Главное окно
root = ctk.CTk()
root.title("AllFix")
center_window(root, 340, 330)

# Загружаем иконки
discord_icon = ctk.CTkImage(light_image=Image.open(os.path.join(icons_path, "discord.png")), size=(24, 20))
youtube_icon = ctk.CTkImage(light_image=Image.open(os.path.join(icons_path, "youtube.png")), size=(20, 20))

# Создаём комбинированную иконку для "Все сразу"
try:
    img1 = Image.open(os.path.join(icons_path, "discord.png")).resize((24, 20))
    img2 = Image.open(os.path.join(icons_path, "youtube.png")).resize((20, 20))
    img3 = Image.open(os.path.join(icons_path, "all.png")).resize((20, 20))

    total_width = img1.width + img2.width + img3.width + 4  # +4 px отступа
    combined_img = Image.new("RGBA", (total_width, img1.height), (255, 255, 255, 0))
    combined_img.paste(img1, (0, 0))
    combined_img.paste(img2, (img1.width + 2, 0))
    combined_img.paste(img3, (img1.width + img2.width + 4, 0))

    all_icons_combined = ctk.CTkImage(light_image=combined_img, size=(total_width, 20))
except FileNotFoundError:
    messagebox.showerror("Ошибка", "Не найдены все иконки (discord.png, youtube.png, all.png) в папке icons")
    all_icons_combined = None

# Кнопки
ctk.CTkButton(root, text="  Обход Discord", image=discord_icon, compound="left",
              corner_radius=15, height=40, command=discord_fix).pack(pady=8, padx=20, fill="x")

ctk.CTkButton(root, text="  Обход YouTube", image=youtube_icon, compound="left",
              corner_radius=15, height=40, command=youtube_fix).pack(pady=8, padx=20, fill="x")

ctk.CTkButton(root, text="  Все сразу", image=all_icons_combined, compound="left",
              fg_color="#66ccff", hover_color="#33bbff",
              corner_radius=15, height=40, command=ultimate_fix).pack(pady=8, padx=20, fill="x")

ctk.CTkButton(root, text="Выход", fg_color="#ff6666", hover_color="#ff4d4d",
              corner_radius=15, height=40, command=root.quit).pack(pady=8, padx=20, fill="x")

# Подпись
label = ctk.CTkLabel(root, text="Made by Millifaro", font=("Arial", 10))
label.pack(side="bottom", pady=5)

root.mainloop()
