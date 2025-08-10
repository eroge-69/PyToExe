import pyautogui
import random
import time
import threading
import keyboard
import tkinter as tk
from tkinter import messagebox

running = False

def random_sequence(seq_min, seq_max):
    keys = ['w', 'a', 's', 'd', 'space']
    length = random.randint(seq_min, seq_max)
    return [random.choice(keys) for _ in range(length)]

def macro_loop(min_delay, max_delay, seq_min, seq_max, status_label):
    global running
    while running:
        delay = random.randint(min_delay * 60, max_delay * 60)
        status_label.config(text=f"Waiting {delay//60} min {delay%60} sec...")
        
        for _ in range(delay):  # check every second so ESC works fast
            if not running or keyboard.is_pressed("esc"):
                status_label.config(text="Stopped.")
                running = False
                return
            time.sleep(1)
        
        seq = random_sequence(seq_min, seq_max)
        status_label.config(text=f"Pressing: {' '.join(seq)}")
        for key in seq:
            if not running:
                break
            pyautogui.press(key)
            time.sleep(random.uniform(0.1, 0.4))

    status_label.config(text="Stopped.")

def start_macro(min_delay_entry, max_delay_entry, seq_min_entry, seq_max_entry, status_label):
    global running
    if running:
        messagebox.showinfo("Info", "Macro is already running!")
        return

    try:
        min_delay = int(min_delay_entry.get())
        max_delay = int(max_delay_entry.get())
        seq_min = int(seq_min_entry.get())
        seq_max = int(seq_max_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers!")
        return
    
    if min_delay <= 0 or max_delay <= 0 or seq_min <= 0 or seq_max <= 0:
        messagebox.showerror("Error", "All numbers must be positive!")
        return
    if min_delay > max_delay or seq_min > seq_max:
        messagebox.showerror("Error", "Minimum values must be <= maximum values!")
        return

    running = True
    threading.Thread(target=macro_loop, args=(min_delay, max_delay, seq_min, seq_max, status_label), daemon=True).start()

def stop_macro():
    global running
    running = False

# GUI setup
root = tk.Tk()
root.title("Random WASD + Space Macro")
root.geometry("350x300")

tk.Label(root, text="Min Delay (minutes):").pack()
min_delay_entry = tk.Entry(root)
min_delay_entry.insert(0, "10")
min_delay_entry.pack()

tk.Label(root, text="Max Delay (minutes):").pack()
max_delay_entry = tk.Entry(root)
max_delay_entry.insert(0, "15")
max_delay_entry.pack()

tk.Label(root, text="Min Sequence Length:").pack()
seq_min_entry = tk.Entry(root)
seq_min_entry.insert(0, "5")
seq_min_entry.pack()

tk.Label(root, text="Max Sequence Length:").pack()
seq_max_entry = tk.Entry(root)
seq_max_entry.insert(0, "15")
seq_max_entry.pack()

status_label = tk.Label(root, text="Stopped.", fg="blue")
status_label.pack(pady=10)

start_button = tk.Button(root, text="Start Macro", command=lambda: start_macro(min_delay_entry, max_delay_entry, seq_min_entry, seq_max_entry, status_label))
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Macro", command=stop_macro)
stop_button.pack(pady=5)

tk.Label(root, text="Press ESC anytime to stop").pack(pady=10)

root.mainloop()
