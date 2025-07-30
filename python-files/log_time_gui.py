
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

EPOCH_START = datetime(6600, 1, 1)

TICK_LENGTH_SECONDS = 0.6  # Each tick is 0.6 seconds
TICKS_PER_MINUTE = 100
TICKS_PER_HOUR = TICKS_PER_MINUTE * 100
TICKS_PER_DAY = TICKS_PER_HOUR * 100

def gregorian_to_log(gregorian_dt):
    delta = gregorian_dt - EPOCH_START
    total_seconds = delta.total_seconds()
    ticks = round(total_seconds / TICK_LENGTH_SECONDS)
    hours = ticks // TICKS_PER_HOUR
    minutes = (ticks % TICKS_PER_HOUR) // TICKS_PER_MINUTE
    seconds = ticks % TICKS_PER_MINUTE
    return f"[{hours}:{minutes:02d}]:{seconds:02d}"

def log_to_gregorian(log_string):
    try:
        part1, part2 = log_string.strip().split("]:")
        part1 = part1.strip("[")
        hours, minutes = map(int, part1.split(":"))
        seconds = int(part2)
        total_ticks = hours * TICKS_PER_HOUR + minutes * TICKS_PER_MINUTE + seconds
        total_seconds = total_ticks * TICK_LENGTH_SECONDS
        return EPOCH_START + timedelta(seconds=total_seconds)
    except Exception:
        raise ValueError("Invalid log time format. Expected format: [H:MM]:SS")

class LogTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Time ↔ Gregorian Converter")

        self.input_label = ttk.Label(root, text="Enter Gregorian (YYYY-MM-DD HH:MM:SS) or Log Time ([H:MM]:SS):")
        self.input_label.pack(pady=5)

        self.input_entry = ttk.Entry(root, width=50)
        self.input_entry.pack(pady=5)

        self.convert_button = ttk.Button(root, text="Convert", command=self.convert)
        self.convert_button.pack(pady=10)

        self.output_label = ttk.Label(root, text="")
        self.output_label.pack(pady=10)

    def convert(self):
        user_input = self.input_entry.get()
        try:
            if "[" in user_input and "]" in user_input:
                # Assume it's log time
                result = log_to_gregorian(user_input)
                self.output_label.config(text=f"Gregorian: {result}")
            else:
                dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
                result = gregorian_to_log(dt)
                self.output_label.config(text=f"Log Time: {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogTimeApp(root)
    root.mainloop()
