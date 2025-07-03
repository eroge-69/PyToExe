import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime

active_stations = {}

def toggle_station(station_name):
    if station_name in active_stations:
        active_stations[station_name].destroy()
        del active_stations[station_name]
        status_var.set(f"{station_name} cleared from dashboard.")
    else:
        timestamp = datetime.now().strftime('%H:%M:%S')
        label_text = f"{station_name}  •  {timestamp}"
        label = ttk.Label(dashboard_frame, text=label_text, style="Dashboard.TLabel")
        label.pack(anchor='w', pady=4)
        active_stations[station_name] = label
        status_var.set(f"{station_name} added to dashboard.")

# === Main Window Setup ===
root = tk.Tk()
root.title("Station Control Panel")
root.geometry("300x400+100+100")
root.configure(bg="#f7f7f7")

# === Styling ===
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Segoe UI", 12), padding=6)
style.configure("Dashboard.TLabel", font=("Consolas", 13), background="#ffffff")
style.configure("TFrame", background="#f7f7f7")

# === Load Image from User-Provided Path ===
image_path = "C:/Users/o'Shit/PycharmProjects/FastAPIProject/Logo/download.png"

try:
    logo_image = Image.open(image_path)
    logo_image = logo_image.resize((250, 60), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
except Exception as e:
    logo_photo = None
    print(f"Failed to load image: {e}")

# === Add Logo to Main Window ===
if logo_photo:
    logo_label_main = tk.Label(root, image=logo_photo, bg="#f7f7f7")
    logo_label_main.image = logo_photo
    logo_label_main.pack(pady=(10, 0))

# === Station Buttons ===
button_frame = ttk.Frame(root)
button_frame.pack(padx=20, pady=20, fill='both', expand=True)

stations = ["Station A", "Station B", "Station C", "Station D"]
for station in stations:
    btn = ttk.Button(button_frame, text=station, command=lambda s=station: toggle_station(s))
    btn.pack(fill='x', pady=6)

# === Status Bar ===
status_var = tk.StringVar(value="Click a station button to toggle it on the dashboard.")
status_bar = ttk.Label(root, textvariable=status_var, relief='sunken', anchor='w', padding=4)
status_bar.pack(fill='x', side='bottom')

# === Dashboard Window Setup ===
dashboard = tk.Toplevel(root)
dashboard.title("Live Dashboard")
dashboard.geometry("500x400+1200+100")
dashboard.configure(bg="#ffffff")

# === Add Logo to Dashboard ===
if logo_photo:
    logo_label_dash = tk.Label(dashboard, image=logo_photo, bg="#ffffff")
    logo_label_dash.image = logo_photo
    logo_label_dash.pack(pady=(10, 0))

# === Dashboard Title ===
ttk.Label(dashboard, text="Live Dashboard", font=("Segoe UI", 16, "bold"), background="#ffffff").pack(pady=(10, 10))

# === Dashboard Content Frame ===
dashboard_frame = ttk.Frame(dashboard)
dashboard_frame.pack(fill='both', expand=True, padx=20, pady=10)

# === Start GUI ===
root.mainloop()
