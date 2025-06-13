import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Controller
import threading
import time
import keyboard

keyboard_controller = Controller()
stop_event = threading.Event()  # безопасный флаг остановки

def start_clicking(keys, interval_ms):
    if not stop_event.is_set():  # уже запущен
        return

    stop_event.clear()
    update_status("Работает", "green")
    interval = interval_ms / 1000.0

    def click_loop():
        while not stop_event.is_set():
            for key in keys:
                if stop_event.is_set():
                    break
                try:
                    keyboard_controller.press(key)
                    time.sleep(0.05)
                    keyboard_controller.release(key)
                    print(f"Нажатие: {key}")
                except Exception as e:
                    print(f"Ошибка: {e}")

                # гибкий интервал
                elapsed = 0
                step = 0.01
                while elapsed < interval:
                    if stop_event.is_set():
                        break
                    time.sleep(step)
                    elapsed += step
        update_status("Остановлен", "red")

    thread = threading.Thread(target=click_loop)
    thread.daemon = True
    thread.start()

def stop_clicking():
    stop_event.set()
    print("Остановка запрошена")

def on_start():
    keys = entry_keys.get().split(',')
    keys = [k.strip() for k in keys if k.strip()]
    try:
        interval_ms = int(entry_interval.get())
        if interval_ms < 0:
            raise ValueError
        start_clicking(keys, interval_ms)
    except ValueError:
        messagebox.showerror("Ошибка", "Интервал должен быть положительным числом в миллисекундах.")

def on_stop():
    stop_clicking()

# === Индикатор статуса ===
def update_status(text, color):
    status_label.config(text=f"Статус: {text}", fg=color)

# === Горячие клавиши ===
def hotkey_listener():
    keyboard.add_hotkey("F6", on_start)
    keyboard.add_hotkey("F7", on_stop)
    keyboard.wait()

hotkey_thread = threading.Thread(target=hotkey_listener)
hotkey_thread.daemon = True
hotkey_thread.start()

# === GUI ===
root = tk.Tk()
root.title("Автокликер клавиш")

tk.Label(root, text="Клавиши (через запятую):").pack()
entry_keys = tk.Entry(root, width=30)
entry_keys.insert(0, "a,b")
entry_keys.pack()

tk.Label(root, text="Интервал (в мс,от 20мс):").pack()
entry_interval = tk.Entry(root, width=10)
entry_interval.insert(0, "1000")
entry_interval.pack()

tk.Button(root, text="Старт (F6)", command=on_start, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Стоп (F7)", command=on_stop, bg="red", fg="white").pack()

status_label = tk.Label(root, text="Статус: Остановлен", fg="red", font=("Arial", 12, "bold"))
status_label.pack(pady=10)

root.mainloop()
