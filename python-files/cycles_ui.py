import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time

loading_time = 0

def open_settings():
    def save_settings():
        global loading_time
        try:
            loading_time = int(entry.get())
            settings_win.destroy()
        except:
            messagebox.showerror("Invalid Input", "Enter loading time as a number.")

    settings_win = tk.Toplevel(root)
    settings_win.title("Settings")
    settings_win.geometry("300x120")
    tk.Label(settings_win, text="Loading Time (sec):", font=("Arial", 12)).pack(pady=10)
    entry = tk.Entry(settings_win, font=("Arial", 12), justify='center')
    entry.insert(0, str(loading_time))
    entry.pack()
    tk.Button(settings_win, text="Save", command=save_settings).pack(pady=10)

def calculate():
    try:
        input_str = entry.get()
        time_part, units_str = input_str.strip().split('-')
        minutes, seconds = map(int, time_part.split('.'))
        units = int(units_str)

        total_seconds = minutes * 60 + seconds - loading_time
        if total_seconds <= 0:
            raise ValueError

        hourly = int(3600 / total_seconds)
        eight_hour = hourly * 8
        seventy_five = int(eight_hour * 0.75)
        percent = round((units / eight_hour) * 100)

        result = (
            f"Input: {minutes}m {seconds}s | Units: {units}\n"
            f"- Hourly: {hourly}\n"
            f"- 8-Hour: {eight_hour}\n"
            f"- 75%: {seventy_five}\n"
            f"- {units} is {percent}% of 8-Hour"
        )
        output.config(text=result)
    except:
        messagebox.showerror("Error", "Use format MM.SS-Units (e.g., 2.53-52)")

root = tk.Tk()
root.title("CYCLES by AIR")
root.configure(bg="#0c0c0c")
root.geometry("500x370")
root.resizable(False, False)

# Settings button
settings_btn = tk.Button(root, text="⚙", font=("Arial", 12), bg="#0c0c0c", fg="white", command=open_settings, bd=0)
settings_btn.place(x=470, y=5)

# Title & subtitle
tk.Label(root, text="KROME DISPENSE", font=("Arial", 12, "bold"), fg="red", bg="#0c0c0c").pack(pady=(10,0))
tk.Label(root, text="CYCLES by AIR", font=("Arial", 18, "bold"), fg="white", bg="#0c0c0c").pack()
tk.Label(root, text="Enter cycle time and units like 2.53-52", font=("Arial", 10), fg="#cccccc", bg="#0c0c0c").pack(pady=(0, 10))

# Entry box
entry = tk.Entry(root, font=("Arial", 14), justify="center", width=25, bg="#1c1c1c", fg="white", bd=2)
entry.insert(0, "e.g., 2.53-52")
entry.pack(pady=10)

# Buttons
btn_frame = tk.Frame(root, bg="#0c0c0c")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Use Scroll Mode", font=("Arial", 11, "bold"),
          bg="#e60000", fg="white", width=15).pack(side="left", padx=10)

tk.Button(btn_frame, text="CALCULATE", font=("Arial", 11, "bold"),
          bg="#e60000", fg="white", width=15, command=calculate).pack(side="left", padx=10)

# Output box
output = tk.Label(root, text="", font=("Courier", 10), fg="white", bg="#0c0c0c", justify="left", wraplength=460)
output.pack(pady=20)

root.mainloop()
