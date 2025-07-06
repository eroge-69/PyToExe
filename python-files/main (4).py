import tkinter as tk
import random
import threading
import time

def show_window(text, delay=0):
    def run():
        time.sleep(delay)
        win = tk.Tk()
        win.title("Ошибка")
        width, height = 300, 100
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = random.randint(0, screen_width - width)
        y = random.randint(0, screen_height - height)
        win.geometry(f"{width}x{height}+{x}+{y}")
        tk.Label(win, text=text, font=("Arial", 12), fg="red").pack(expand=True)
        win.after(3000, win.destroy)
        win.mainloop()
    threading.Thread(target=run).start()

total_windows = 3000
batch_size = 150
delay_between_batches = 5  # секунд

for batch_start in range(0, total_windows, batch_size):
    for i in range(batch_start, min(batch_start + batch_size, total_windows)):
        show_window("ЯРИК ТЫ БЫЛ ВЗЛОМАН", delay=(i - batch_start) * 0.05)
    time.sleep(delay_between_batches)
