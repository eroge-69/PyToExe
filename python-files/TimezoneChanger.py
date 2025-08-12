import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

# Predefined city timezones (Windows tzutil names)
CITY_TIMEZONES = {
    "San Diego, USA": "Pacific Standard Time",
    "Paris, France": "Romance Standard Time",
    "London, England": "GMT Standard Time",
    "Shanghai, China": "China Standard Time",
    "Tokyo, Japan": "Tokyo Standard Time",
}

# Common Windows timezone names list (partial for demo)
ALL_TIMEZONES = [
    "Dateline Standard Time",
    "UTC-11",
    "Aleutian Standard Time",
    "Hawaiian Standard Time",
    "Alaskan Standard Time",
    "Pacific Standard Time",
    "Mountain Standard Time",
    "Central Standard Time",
    "Eastern Standard Time",
    "Atlantic Standard Time",
    "GMT Standard Time",
    "Romance Standard Time",
    "Central Europe Standard Time",
    "E. Europe Standard Time",
    "Egypt Standard Time",
    "South Africa Standard Time",
    "Russian Standard Time",
    "Arabian Standard Time",
    "Afghanistan Standard Time",
    "Pakistan Standard Time",
    "India Standard Time",
    "China Standard Time",
    "Tokyo Standard Time",
    "AUS Eastern Standard Time",
    "New Zealand Standard Time",
]

def set_timezone(tz_name):
    try:
        subprocess.run(["tzutil", "/s", tz_name], check=True)
        messagebox.showinfo("Success", f"Timezone set to: {tz_name}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to set timezone.\n{e}")

def on_ok():
    if selected_timezone.get():
        set_timezone(selected_timezone.get())
    else:
        messagebox.showwarning("No Selection", "Please select a timezone.")

def on_cancel():
    root.destroy()

root = tk.Tk()
root.title("Windows Timezone Changer")
root.geometry("420x420")
selected_timezone = tk.StringVar()

# Radio buttons for quick cities
tk.Label(root, text="Quick Select:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
for city, tz in CITY_TIMEZONES.items():
    tk.Radiobutton(root, text=city, variable=selected_timezone, value=tz).pack(anchor="w")

# Dropdown for all Windows timezones
tk.Label(root, text="All Timezones:", font=("Arial", 12, "bold")).pack(anchor="w", pady=10)
all_tz_dropdown = ttk.Combobox(root, values=ALL_TIMEZONES, textvariable=selected_timezone)
all_tz_dropdown.pack(fill="x", padx=5)

# Buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=20)
tk.Button(frame_buttons, text="OK", command=on_ok, width=10).grid(row=0, column=0, padx=10)
tk.Button(frame_buttons, text="Cancel", command=on_cancel, width=10).grid(row=0, column=1, padx=10)

root.mainloop()
