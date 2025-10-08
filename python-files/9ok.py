import tkinter as tk
from tkinter import messagebox
import time
import datetime
import threading
import os
import sys
import subprocess

# --- Функція сповіщення ---
def show_reminder():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Хвилина мовчання 🕯️",
        "Вшануймо пам'ять загиблих хвилиною мовчання."
    )
    root.destroy()

# --- Створення завдання у Task Scheduler ---
def create_task_scheduler():
    task_name = "MinuteOfSilence"
    script_path = os.path.abspath(sys.argv[0])

    # Перевірка, чи існує завдання
    try:
        check = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name],
            capture_output=True, text=True
        )
        if "ERROR:" not in check.stdout:
            print(f"Завдання '{task_name}' вже існує.")
            return
    except Exception as e:
        print("Не вдалося перевірити завдання:", e)
        return

    # Створюємо завдання
    try:
        subprocess.run([
            "schtasks", "/Create",
            "/SC", "ONLOGON",          # при вході користувача
            "/RL", "HIGHEST",          # запуск з високими правами
            "/TN", task_name,          # ім'я завдання
            "/TR", f'"{sys.executable}" "{script_path}"'  # команда запуску
        ], check=True)
        print(f"Завдання '{task_name}' успішно створене ✅")
    except Exception as e:
        print("Не вдалося створити завдання:", e)

# --- Планування нагадувань ---
def schedule_reminder():
    while True:
        now = datetime.datetime.now()
        if now.hour == 9 and now.minute == 0:
            show_reminder()
            time.sleep(60)  # чекати хвилину, щоб не дублювати сповіщення
        time.sleep(20)

# --- Головна функція ---
def main():
    print("Програма 'Хвилина мовчання' запущена.")
    # Створення завдання у Task Scheduler при першому запуску
    create_task_scheduler()

    thread = threading.Thread(target=schedule_reminder, daemon=True)
    thread.start()

    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
