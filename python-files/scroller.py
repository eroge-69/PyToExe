import tkinter as tk
from tkinter import scrolledtext
import time
import datetime
from threading import Thread, Event
from pynput.keyboard import Key, Controller

# Настройки
interval_seconds = 2
log_file = "unfollow_log.txt"

keyboard = Controller()
stop_event = Event()
unfollow_count = 0

# GUI
root = tk.Tk()
root.title("📉 TikTok Unfollow Logger")
root.geometry("500x420")
root.resizable(False, False)

# Заголовок
header = tk.Label(root, text="📋 Список отписок", font=("Segoe UI", 12, "bold"))
header.pack(pady=5)

# Окно лога
log_box = scrolledtext.ScrolledText(root, state="disabled", wrap="word", height=18)
log_box.pack(padx=10, fill="both", expand=True)

# Нижняя панель
footer = tk.Frame(root)
footer.pack(pady=8)

count_label = tk.Label(footer, text="Всего: 0", font=("Segoe UI", 10))
count_label.pack(side="left", padx=10)

clear_btn = tk.Button(footer, text="🧹 Очистить", command=lambda: clear_log())
clear_btn.pack(side="right", padx=10)

# Функции
def write_log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}\n"

    # Добавить в GUI
    log_box.configure(state="normal")
    log_box.insert("end", full_msg)
    log_box.see("end")
    log_box.configure(state="disabled")

    # Сохраняем в файл
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(full_msg)

def scroll_loop():
    global unfollow_count
    while not stop_event.is_set():
        keyboard.press(Key.page_down)
        keyboard.release(Key.page_down)
        unfollow_count += 1
        write_log(f"Unfollowed user #{unfollow_count}")
        count_label.config(text=f"Всего: {unfollow_count}")
        time.sleep(interval_seconds)

def clear_log():
    global unfollow_count
    log_box.configure(state="normal")
    log_box.delete("1.0", "end")
    log_box.configure(state="disabled")
    open(log_file, "w", encoding="utf-8").close()
    unfollow_count = 0
    count_label.config(text="Всего: 0")

def on_close():
    stop_event.set()
    root.destroy()

# Запуск
root.protocol("WM_DELETE_WINDOW", on_close)
Thread(target=scroll_loop, daemon=True).start()
root.mainloop()
