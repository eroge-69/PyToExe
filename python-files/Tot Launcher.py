import minecraft_launcher_lib
import os
import uuid
import tkinter as tk
from tkinter import messagebox

# Папка, где будут все файлы игры
minecraft_directory = os.path.join(os.getcwd(), "minecraft_data")

# Версия игры
version = "1.16.5"

def launch_game():
    username = entry.get()
    if not username.strip():
        messagebox.showerror("Ошибка", "Введите ник!")
        return

    # Создаем постоянный UUID из ника
    player_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))

    # Если версия не установлена — установим
    if not minecraft_launcher_lib.utils.is_version_installed(version, minecraft_directory):
        minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_directory)

    # Настройки запуска
    options = {
        "username": username,
        "uuid": player_uuid,
        "token": "0",  # 0 — означает оффлайн режим
        "jvmArguments": ["-Xmx2G"]  # 2 ГБ RAM
    }

    # Команда запуска
    command = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_directory, options)

    # Запуск
    os.system(" ".join(command))

# Интерфейс
root = tk.Tk()
root.title("Оффлайн Minecraft LAN Launcher")
root.geometry("300x150")

label = tk.Label(root, text="Введите ник:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Играть", command=launch_game)
button.pack(pady=20)

root.mainloop()
