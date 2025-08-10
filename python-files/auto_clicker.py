import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import keyboard  # NEW

click_positions = []
clicking = False

def record_position():
    messagebox.showinfo("Position", "Hover your mouse where you want to click and press OK.")
    pos = pyautogui.position()
    click_positions.append(pos)
    pos_label.config(text=f"Positions recorded: {len(click_positions)}")

def start_clicking():
    global clicking
    if not click_positions:
        messagebox.showwarning("Warning", "No click positions recorded.")
        return

    try:
        delay = float(delay_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid delay value.")
        return

    clicking = True
    threading.Thread(target=click_loop, args=(delay,), daemon=True).start()
    threading.Thread(target=listen_for_stop, daemon=True).start()  # NEW

def stop_clicking():
    global clicking
    clicking = False
    print("Auto clicker stopped.")

def listen_for_stop():
    keyboard.wait('F8')  # Listen for F8 key globally
    stop_clicking()
    messagebox.showinfo("Stopped", "Auto clicker has been stopped (F8 pressed).")

def click_loop(delay):
    while clicking:
        for pos in click_positions:
            if not clicking:
                break
            pyautogui.click(pos)
            time.sleep(delay)

def clear_positions():
    click_positions.clear()
    pos_label.config(text="Positions recorded: 0")

# --- GUI Setup ---
root = tk.Tk()
root.title("Auto Clicker")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Click Delay (seconds):").grid(row=0, column=0, sticky="e")
delay_entry = tk.Entry(frame)
delay_entry.insert(0, "0.5")
delay_entry.grid(row=0, column=1)

record_btn = tk.Button(frame, text="Record Position", command=record_position)
record_btn.grid(row=1, column=0, columnspan=2, pady=5)

pos_label = tk.Label(frame, text="Positions recorded: 0")
pos_label.grid(row=2, column=0, columnspan=2)

start_btn = tk.Button(frame, text="Start Clicking", bg="green", fg="white", command=start_clicking)
start_btn.grid(row=3, column=0, pady=10)

stop_btn = tk.Button(frame, text="Stop Clicking", bg="red", fg="white", command=stop_clicking)
stop_btn.grid(row=3, column=1)

clear_btn = tk.Button(frame, text="Clear Positions", command=clear_positions)
clear_btn.grid(row=4, column=0, columnspan=2, pady=5)

tk.Label(frame, text="Press F8 to stop from anywhere.").grid(row=5, column=0, columnspan=2, pady=5)

root.mainloop()
