import threading
import time
import pyautogui
import tkinter as tk
from tkinter import messagebox
import keyboard

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоклікер")

        # Змінні для параметрів кліка
        self.clicks = tk.IntVar(value=990)
        self.interval = tk.DoubleVar(value=0.03)  # сек
        self.wait_minutes = tk.IntVar(value=60)
        self.x = tk.IntVar(value=800)
        self.y = tk.IntVar(value=450)

        # Змінні для гарячих клавіш (рядки)
        self.start_key = tk.StringVar(value='s')
        self.pause_key = tk.StringVar(value='p')
        self.stop_key = tk.StringVar(value='q')

        self.is_running = False
        self.is_paused = False
        self.thread = None

        # Створюємо інтерфейс
        self.create_widgets()

        # Запускаємо слухач гарячих клавіш у фоновому потоці
        threading.Thread(target=self.listen_hotkeys, daemon=True).start()

    def create_widgets(self):
        tk.Label(self.root, text="X:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.x, width=10).grid(row=0, column=1)

        tk.Label(self.root, text="Y:").grid(row=1, column=0)
        tk.Entry(self.root, textvariable=self.y, width=10).grid(row=1, column=1)

        tk.Label(self.root, text="Кількість кліків:").grid(row=2, column=0)
        tk.Entry(self.root, textvariable=self.clicks, width=10).grid(row=2, column=1)

        tk.Label(self.root, text="Інтервал (сек):").grid(row=3, column=0)
        tk.Entry(self.root, textvariable=self.interval, width=10).grid(row=3, column=1)

        tk.Label(self.root, text="Час очікування (хв):").grid(row=4, column=0)
        tk.Entry(self.root, textvariable=self.wait_minutes, width=10).grid(row=4, column=1)

        # Гарячі клавіші
        tk.Label(self.root, text="Гарячі клавіші (латиниця)").grid(row=5, column=0, columnspan=2)

        tk.Label(self.root, text="Старт:").grid(row=6, column=0)
        tk.Entry(self.root, textvariable=self.start_key, width=10).grid(row=6, column=1)

        tk.Label(self.root, text="Пауза/Продовження:").grid(row=7, column=0)
        tk.Entry(self.root, textvariable=self.pause_key, width=10).grid(row=7, column=1)

        tk.Label(self.root, text="Стоп:").grid(row=8, column=0)
        tk.Entry(self.root, textvariable=self.stop_key, width=10).grid(row=8, column=1)

        # Кнопки
        self.status_label = tk.Label(self.root, text="Статус: Очікую")
        self.status_label.grid(row=9, column=0, columnspan=2)

        tk.Button(self.root, text="Старт", command=self.start).grid(row=10, column=0)
        tk.Button(self.root, text="Пауза/Продовження", command=self.pause).grid(row=10, column=1)
        tk.Button(self.root, text="Стоп", command=self.stop).grid(row=11, column=0, columnspan=2)

    def listen_hotkeys(self):
        # Знімаємо старі гарячі клавіші, якщо були
        keyboard.unhook_all_hotkeys()

        # Прив’язуємо гарячі клавіші динамічно
        keyboard.add_hotkey(self.start_key.get(), self.start)
        keyboard.add_hotkey(self.pause_key.get(), self.pause)
        keyboard.add_hotkey(self.stop_key.get(), self.stop)

        # Щоб не завершувалась функція
        keyboard.wait()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.status_label.config(text="Статус: Запущено")
            self.thread = threading.Thread(target=self.run_clicker, daemon=True)
            self.thread.start()

    def pause(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            status = "Пауза" if self.is_paused else "Запущено"
            self.status_label.config(text=f"Статус: {status}")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self.status_label.config(text="Статус: Зупинено")

    def run_clicker(self):
        time.sleep(5)  # час на підготовку
        while self.is_running:
            self.status_label.config(text="Клікаю...")
            for _ in range(self.clicks.get()):
                if not self.is_running:
                    break
                while self.is_paused:
                    time.sleep(0.1)
                pyautogui.click(self.x.get(), self.y.get())
                time.sleep(self.interval.get())
            if not self.is_running:
                break
            self.status_label.config(text=f"Очікую {self.wait_minutes.get()} хвилин...")
            wait_sec = self.wait_minutes.get() * 60
            waited = 0
            while waited < wait_sec:
                if not self.is_running:
                    break
                while self.is_paused:
                    time.sleep(0.1)
                time.sleep(1)
                waited += 1
        self.status_label.config(text="Завершено")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
