import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import psutil
import json

def save_paths(majestic_path, redux_path):
    """Сохранение путей и истории в JSON файл"""
    try:
        # Загрузка текущей конфигурации
        if os.path.exists("paths_config.json"):
            with open("paths_config.json", "r") as f:
                config = json.load(f)
        else:
            config = {"majestic_history": [], "redux_history": [], "last_majestic": "", "last_redux": ""}

        # Обновление истории для Majestic Launcher
        if majestic_path and majestic_path not in config["majestic_history"]:
            config["majestic_history"].insert(0, majestic_path)
            config["majestic_history"] = config["majestic_history"][:5]  # Ограничение до 5 путей
        config["last_majestic"] = majestic_path

        # Обновление истории для файла редукс
        if redux_path and redux_path not in config["redux_history"]:
            config["redux_history"].insert(0, redux_path)
            config["redux_history"] = config["redux_history"][:5]  # Ограничение до 5 путей
        config["last_redux"] = redux_path

        # Сохранение конфигурации
        with open("paths_config.json", "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить пути: {str(e)}")

def load_paths():
    """Загрузка путей и истории из JSON файла"""
    try:
        if os.path.exists("paths_config.json"):
            with open("paths_config.json", "r") as f:
                config = json.load(f)
                # Поддержка старого формата (если есть только пути без истории)
                majestic_history = config.get("majestic_history", [config.get("majestic_path", "")] if config.get("majestic_path") else [])
                redux_history = config.get("redux_history", [config.get("redux_path", "")] if config.get("redux_path") else [])
                last_majestic = config.get("last_majestic", config.get("majestic_path", ""))
                last_redux = config.get("last_redux", config.get("redux_path", ""))
                return majestic_history, redux_history, last_majestic, last_redux
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить пути: {str(e)}")
    return [], [], "", ""

def select_file():
    """Выбор файла редукс"""
    file_path = filedialog.askopenfilename(title="Выберите файл редукс", filetypes=[("Все файлы", "*.*")])
    if file_path:
        redux_var.set(file_path)
        save_paths(majestic_var.get(), file_path)
        update_redux_menu()

def select_majestic_launcher():
    """Выбор пути к Majestic Launcher"""
    file_path = filedialog.askopenfilename(title="Выберите Majestic Launcher", filetypes=[("Исполняемые файлы", "*.exe")])
    if file_path:
        majestic_var.set(file_path)
        save_paths(file_path, redux_var.get())
        update_majestic_menu()

def update_majestic_menu():
    """Обновление выпадающего меню для Majestic Launcher"""
    menu = majestic_menu["menu"]
    menu.delete(0, "end")
    for path in majestic_history:
        menu.add_command(label=path, command=lambda p=path: majestic_var.set(p))
    if not majestic_history:
        menu.add_command(label="Выберите путь", command=lambda: None)

def update_redux_menu():
    """Обновление выпадающего меню для файла редукс"""
    menu = redux_menu["menu"]
    menu.delete(0, "end")
    for path in redux_history:
        menu.add_command(label=path, command=lambda p=path: redux_var.set(p))
    if not redux_history:
        menu.add_command(label="Выберите путь", command=lambda: None)

def is_process_running(process_name):
    """Проверка, запущен ли процесс"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            return True
    return False

def wait_for_majestic_verification():
    """Ожидание завершения проверки файлов Majestic Launcher"""
    messagebox.showinfo("Ожидание", "Пожалуйста, выберите сервер 'Заходили в последний раз' и дождитесь завершения проверки файлов. Нажмите ОК, когда проверка завершена.")
    return True

def run_majestic_and_copy_redux():
    """Запуск Majestic Launcher, ожидание проверки, копирование редукса и запуск Rockstar"""
    majestic_path = majestic_var.get()
    redux_path = redux_var.get()
    
    # Путь к папке backup
    appdata_path = os.path.expandvars(r'%APPDATA%\..\Local\altv-majestic\backup')
    
    # Проверка путей
    if not all([majestic_path, redux_path]):
        messagebox.showerror("Ошибка", "Укажите пути к Majestic Launcher и файлу редукс!")
        return

    if not os.path.exists(majestic_path):
        messagebox.showerror("Ошибка", "Majestic Launcher не найден!")
        return

    if not os.path.exists(redux_path):
        messagebox.showerror("Ошибка", "Файл редукс не найден!")
        return

    if not os.path.exists(appdata_path):
        messagebox.showerror("Ошибка", "Папка \\AppData\\Local\\altv-majestic\\backup не найдена!")
        return

    try:
        # Запуск Majestic Launcher
        subprocess.Popen([majestic_path], shell=True)
        messagebox.showinfo("Инструкция", "Выберите сервер 'Заходили в последний раз' в Majestic Launcher и дождитесь завершения проверки файлов.")

        # Ожидание подтверждения завершения проверки
        if not wait_for_majestic_verification():
            messagebox.showerror("Ошибка", "Проверка файлов не завершена!")
            return

        # Копирование файла редукс
        shutil.copy2(redux_path, appdata_path)
        messagebox.showinfo("Успех", "Файл редукс успешно скопирован в \\AppData\\Local\\altv-majestic\\backup!")

        # Запуск Rockstar Games Launcher
        rockstar_exe = os.path.join(appdata_path, "GTA5.exe")
        if os.path.exists(rockstar_exe):
            subprocess.run([rockstar_exe])
        else:
            messagebox.showwarning("Предупреждение", "GTA5.exe не найден, но файл редукс скопирован!")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

# Создание GUI
root = tk.Tk()
root.title("Majestic Redux Launcher")
root.geometry("400x200")

# Загрузка сохраненных путей и истории
majestic_history, redux_history, last_majestic, last_redux = load_paths()

# Переменные для хранения выбранных путей
majestic_var = tk.StringVar(value=last_majestic)
redux_var = tk.StringVar(value=last_redux)

# Поле для пути к Majestic Launcher
tk.Label(root, text="Путь к Majestic Launcher:").pack(pady=5)
majestic_menu = tk.OptionMenu(root, majestic_var, *majestic_history)
majestic_menu.config(width=37)
majestic_menu.pack()
tk.Button(root, text="Обзор...", command=select_majestic_launcher).pack()

# Поле для пути к файлу редукс
tk.Label(root, text="Путь к файлу редукс:").pack(pady=5)
redux_menu = tk.OptionMenu(root, redux_var, *redux_history)
redux_menu.config(width=37)
redux_menu.pack()
tk.Button(root, text="Обзор...", command=select_file).pack()

# Кнопка запуска
tk.Button(root, text="Запустить Majestic и скопировать редукс", command=run_majestic_and_copy_redux).pack(pady=20)

# Обновление выпадающих меню
update_majestic_menu()
update_redux_menu()

root.mainloop()