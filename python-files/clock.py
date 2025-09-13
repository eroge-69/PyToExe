import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, timezone

# Dictionary of common timezones and their UTC offsets
timezones = {
    "UTC": 0,
    "New York (EST)": -5,
    "Los Angeles (PST)": -8,
    "London": 0,
    "Paris": +1,
    "Moscow": +3,
    "Tokyo": +9,
    "Sydney": +10,
    "Dubai": +4,
    "Beijing": +8,
    "Mumbai": +5.5
}

def update_time():
    tz_name = timezone_var.get()
    offset_hours = timezones.get(tz_name, 0)
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    local_time = now_utc + timedelta(hours=offset_hours)

    # Time format
    if time_format_var.get() == "12-hour":
        time_str = local_time.strftime("%I:%M:%S %p")
    else:
        time_str = local_time.strftime("%H:%M:%S")

    date_str = local_time.strftime("%A, %B %d, %Y")

    time_label.config(text=time_str)
    day_label.config(text=date_str)

    root.after(1000, update_time)  # update every second

# --- Tkinter Window ---
root = tk.Tk()
root.title("World Clock (No pytz)")
root.geometry("400x220")

# Timezone selection
timezone_var = tk.StringVar(value="UTC")
tk.Label(root, text="Select Timezone:", font=("Arial", 10)).pack(pady=5)

timezone_combo = ttk.Combobox(root, values=list(timezones.keys()), textvariable=timezone_var, width=30)
timezone_combo.pack()

# Time format selection
time_format_var = tk.StringVar(value="12-hour")
format_frame = tk.Frame(root)
format_frame.pack(pady=5)

tk.Label(format_frame, text="Time Format:").pack(side=tk.LEFT)
tk.Radiobutton(format_frame, text="12-hour", variable=time_format_var, value="12-hour").pack(side=tk.LEFT)
tk.Radiobutton(format_frame, text="24-hour", variable=time_format_var, value="24-hour").pack(side=tk.LEFT)

# Time display
time_label = tk.Label(root, text="", font=("Arial", 30))
time_label.pack(pady=5)

# Day/date display
day_label = tk.Label(root, text="", font=("Arial", 12))
day_label.pack(pady=5)

# Start updating time
update_time()

root.mainloop()
