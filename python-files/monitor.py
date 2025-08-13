import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import datetime

# Create Tkinter Window
root = tk.Tk()
root.title("Embedded System Dashboard")
root.geometry("900x700")
root.configure(bg="#f4f4f4")

# ---------------- HEADER SECTION ----------------
header_frame = tk.Frame(root, bg="#344955", height=60)
header_frame.pack(fill="x")

# Load and display logo (Top Left)
logo_image = Image.open("C:/Users/ASPL-PC5/Desktop/logo.png")
logo_image = logo_image.resize((100, 40), Image.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(header_frame, image=logo_tk, bg="#344955")
logo_label.pack(side="left", padx=15)

# Title Label (Dynamically changes based on screen)
title_label = tk.Label(header_frame, text="HOME SCREEN", 
                       font=("Arial", 18, "bold"), fg="white", bg="#344955")
title_label.pack(side="left", expand=True)

# Date & Time Label
time_label = tk.Label(header_frame, font=("Arial", 12), fg="white", bg="#344955")
time_label.pack(side="right", padx=15)

def update_time():
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label.config(text=current_time)
        time.sleep(1)

threading.Thread(target=update_time, daemon=True).start()

# Start/Stop Buttons (Only for Dashboard)
button_frame = tk.Frame(header_frame, bg="#344955")

start_btn = ttk.Button(button_frame, text="Start")
stop_btn = ttk.Button(button_frame, text="Stop")

# Function to switch screens
def show_screen(screen_name):
    for frame in (home_screen, dashboard_screen):
        frame.pack_forget()
    screens[screen_name].pack(fill="both", expand=True)
    title_label.config(text=screen_name.upper() + " SCREEN")
    
    if screen_name == "Dashboard":
        button_frame.pack(side="right", padx=10)
        start_btn.pack(side="left", padx=5)
        stop_btn.pack(side="left", padx=5)
    else:
        button_frame.pack_forget()

# ---------------- MAIN SECTION ----------------
main_frame = tk.Frame(root, bg="white", height=400)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Left Panel: Navigation Menu
menu_frame = tk.Frame(main_frame, bg="#e0e0e0", width=150)
menu_frame.pack(side="left", fill="y")

home_btn = ttk.Button(menu_frame, text="Home", command=lambda: show_screen("Home"))
home_btn.pack(pady=10)
dashboard_btn = ttk.Button(menu_frame, text="Dashboard", command=lambda: show_screen("Dashboard"))
dashboard_btn.pack(pady=10)

# ---------------- HOME SCREEN ----------------
home_screen = tk.Frame(main_frame, bg="white")

home_label = tk.Label(home_screen, text="Welcome to Home Screen", 
                      font=("Arial", 16, "bold"), fg="black", bg="white")
home_label.pack(pady=20)

# ---------------- DASHBOARD SCREEN ----------------
dashboard_screen = tk.Frame(main_frame, bg="white")

# Data Receive Section
data_receive_frame = tk.Frame(dashboard_screen, bg="#e3f2fd", width=400, height=300)
data_receive_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

data_receive_label = tk.Label(data_receive_frame, text="Data Receiving", font=("Arial", 14, "bold"), bg="#e3f2fd")
data_receive_label.pack(pady=10)

# Data Calculation Section
data_calculation_frame = tk.Frame(dashboard_screen, bg="#ffccbc", width=400, height=300)
data_calculation_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

data_calculation_label = tk.Label(data_calculation_frame, text="Data Calculation", font=("Arial", 14, "bold"), bg="#ffccbc")
data_calculation_label.pack(pady=10)

# Dictionary to manage screens
screens = {"Home": home_screen, "Dashboard": dashboard_screen}

# Show home screen by default
show_screen("Home")

# ---------------- FOOTER SECTION ----------------
footer_frame = tk.Frame(root, bg="#344955", height=50)
footer_frame.pack(side="bottom", fill="x")

# Footer Content Frame
footer_content = tk.Frame(footer_frame, bg="#344955")
footer_content.pack(fill="x")

# Company Logo (Right Side)
company_logo_label = tk.Label(footer_content, image=logo_tk, bg="#344955")
company_logo_label.pack(side="right", padx=15, pady=10)

# Run the Tkinter Loop
root.mainloop()