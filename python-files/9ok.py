import tkinter as tk
from tkinter import messagebox
import time
import datetime
import threading
import os
import sys
import subprocess
import platform

# --- Функція сповіщення ---
def show_reminder():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Хвилина мовчання 🕯️",
        "Зараз 9:00.\nВшануймо пам'ять загиблих хвилиною мовчання 🕯️"
    )
    root.destroy()

# --- Отримання шляху до Python ---
def get_python_executable():
    """
    Гарантовано повертає правильний шлях до Python,
    незалежно від 32/64 бітної версії Windows.
    """
    return os.path.abspath(sys.executable)

# --- Створення завдання у Windows Task Scheduler ---
def create_task_scheduler():
    task_name = "MinuteOfSilence"
    script_path = os.path.abspath(sys.argv[0])
    python_path = get_python_executable()

    # Перевірити, чи завдання вже існує
    try:
        check = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name],
            capture_output=True, text=True
        )
        if "ERROR:" not in check.stdout:
            print(f"Завдання '{task_name}' вже існує.")
            return
    except Exception as e:
        print("Не вдалося перевірити наявність завдання:", e)
        return

    # Створити нове завдання
    try:
        # Використовуємо /RL LIMITED для 32-біт без вимоги прав адміністратора
        subprocess.run([
            "schtasks", "/Create",
            "/SC", "ONLOGON",                # запуск при вході користувача
            "/TN", task_name,                # назва завдання
            "/TR", f'"{python_path}" "{script_path}"',  # команда
            "/RL", "LIMITED",                # рівень прав сумісний з Win7/32bit
            "/F"                             # перезапис без запиту
        ], check=True)
        print(f"✅ Завдання '{task_name}' успішно створене.")
    except Exception as e:
        print("⚠️ Не вдалося створити завдання:", e)

# --- Головна логіка нагадування ---
def schedule_reminder():
    while True:
        now = datetime.datetime.now()
        if now.hour == 9 and now.minute == 0:
            show_reminder()
            time.sleep(60)
        time.sleep(20)

# --- Основна функція ---
def main():
    print(f"Запущено 'Хвилина мовчання' ({platform.architecture()[0]} Python)")
    create_task_scheduler()

    t = threading.Thread(target=schedule_reminder, daemon=True)
    t.start()

    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
