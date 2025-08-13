import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import datetime
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize Serial Port
ser = None
serial_thread = None
running = False

# Create Tkinter Window
root = tk.Tk()
root.title("Embedded System Dashboard")
root.geometry("900x700")
root.configure(bg="#f4f4f4")

# Load and display logo once
try:
    logo_image = Image.open("C:/Users/ASPL-PC5/Desktop/logo.png")
    logo_image = logo_image.resize((100, 40), Image.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_image)
except Exception as e:
    print(f"Logo Load Error: {e}")
    logo_tk = None

# ---------------- HEADER SECTION ----------------
header_frame = tk.Frame(root, bg="#344955", height=60)
header_frame.pack(fill="x")

# Logo in Header (Left Side)
if logo_tk:
    logo_label_header = tk.Label(header_frame, image=logo_tk, bg="#344955")
    logo_label_header.pack(side="left", padx=15)

# Title Label
title_label = tk.Label(header_frame, text="HOME SCREEN", font=("Arial", 18, "bold"), fg="white", bg="#344955")
title_label.pack(side="left", expand=True)

 # Date & Time Label
time_label = tk.Label(header_frame, font=("Arial", 12), fg="white", bg="#344955")
time_label.pack(side="right", padx=15)

def update_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

update_time()

# ---------------- BUTTON FRAME ----------------
button_frame = tk.Frame(header_frame, bg="#344955")

start_btn = ttk.Button(button_frame, text="Start", command=lambda: start_serial())
stop_btn = ttk.Button(button_frame, text="Stop", command=lambda: stop_serial())
clear_btn = ttk.Button(button_frame, text="Clear", command=lambda: clear_data())

for btn in [start_btn, stop_btn, clear_btn]:
    btn.pack(side="left", padx=5)

# ---------------- SCREEN SWITCHING FUNCTION ----------------
def show_screen(screen_name):
    for frame in (home_screen, dashboard_screen):
        frame.pack_forget()
    
    screens[screen_name].pack(fill="both", expand=True)
    title_label.config(text=screen_name.upper() + " SCREEN")
    
    if screen_name == "Dashboard":
        button_frame.pack(side="right", padx=10)
        test_ok_label.pack(side="top", pady=5)
        footer_content.pack(fill="x")
    else:
        button_frame.pack_forget()
        test_ok_label.pack_forget()
        footer_content.pack_forget()

# ---------------- MAIN SECTION ----------------
main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Left Panel: Navigation Menu
menu_frame = tk.Frame(main_frame, bg="#e0e0e0", width=150)
menu_frame.pack(side="left", fill="y")

# Load Icons for Buttons
try:
    home_icon = Image.open("C:/Users/ASPL-PC5/Desktop/home.png").resize((40, 40), Image.LANCZOS)
    home_icon_tk = ImageTk.PhotoImage(home_icon)

    dashboard_icon = Image.open("C:/Users/ASPL-PC5/Desktop/dashboard.png").resize((40, 40), Image.LANCZOS)
    dashboard_icon_tk = ImageTk.PhotoImage(dashboard_icon)
except Exception as e:
    print(f"Icon Load Error: {e}")
    home_icon_tk = None
    dashboard_icon_tk = None

# Create Navigation Buttons with Color Indication
def on_enter(e): e.widget.config(bg="#d1d1d1")
def on_leave(e): e.widget.config(bg="#e0e0e0")

home_btn = tk.Button(menu_frame, image=home_icon_tk, bg="#e0e0e0", bd=0, command=lambda: show_screen("Home"))
home_btn.pack(pady=10)
home_btn.bind("<Enter>", on_enter)
home_btn.bind("<Leave>", on_leave)

dashboard_btn = tk.Button(menu_frame, image=dashboard_icon_tk, bg="#e0e0e0", bd=0, command=lambda: show_screen("Dashboard"))
dashboard_btn.pack(pady=10)
dashboard_btn.bind("<Enter>", on_enter)
dashboard_btn.bind("<Leave>", on_leave)

# ---------------- HOME SCREEN ----------------

home_screen = tk.Frame(main_frame, bg="white")
home_label = tk.Label(home_screen, text="Welcome to Home Screen", font=("Arial", 16, "bold"), fg="black", bg="white")
home_label.pack(pady=20)

# ---------------- DASHBOARD SCREEN ----------------
dashboard_screen = tk.Frame(main_frame, bg="white")



# Data Receive Section
data_receive_frame = tk.Frame(dashboard_screen, bg="#e3f2fd")
data_receive_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Table Section
table_frame = tk.Frame(data_receive_frame, bg="#bbdefb")
table_frame.pack(fill="x", padx=5, pady=5)

tree = ttk.Treeview(table_frame, columns=("Time", "Temperature", "Humidity"), show="headings")
tree.heading("Time", text="Time")
tree.heading("Temperature", text="Temperature (°C)")
tree.heading("Humidity", text="Humidity (%)")
tree.pack(fill="x", padx=10, pady=5)

# Graph Section
graph_frame = tk.Frame(data_receive_frame, bg="#90caf9")
graph_frame.pack(fill="both", expand=True, padx=3, pady=3)

fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)
ax2 = ax.twinx()

temp_data, hum_data, time_data = [], [], []

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

def update_graph():
    ax.clear()
    ax2.clear()

    # Plot Data
    ax.plot(time_data, hum_data, 'bo-', label="Humidity")
    ax.set_ylabel("Humidity [%]", color='blue')

   # Plot Temperature (Red - Right Axis)
    ax2.plot(time_data, temp_data, 'rs-', label="Temperature")
    ax2.set_ylabel("Temperature [°C]", color='red')

    ax.set_xlabel("Time") 
    ax.set_title("Temperature & Humidity Over Time")
    ax.grid(True)

    # Rotate X-axis labels for better readability
    ax.set_xticks(time_data)
    ax.set_xticklabels(time_data, rotation=45, ha="right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # Adjust legends and position
    ax.legend(["Humidity"], loc='upper left', fontsize=10)
    ax2.legend(["Temperature"], loc='upper right', fontsize=10)

    canvas.draw()
#time_label.pack(side="right",padx=15)
def update_ui(time_str, temp, hum):
    tree.insert("", "end", values=(time_str, temp, hum))
    
    if len(time_data) > 20:
        time_data.pop(0)
        temp_data.pop(0)
        hum_data.pop(0)
    
    time_data.append(time_str)
    temp_data.append(temp)
    hum_data.append(hum)
    
    update_graph()

def read_serial_data():  
    global running
    while running:
        if ser and ser.is_open:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    temp, hum = map(float, line.split(","))
                    root.after(0, lambda: update_ui(current_time, temp, hum))
            except Exception as e:
                print(f"Serial Read Error: {e}")

def start_serial():
    global ser, running
    try:
        ser = serial.Serial("COM3", 9600, timeout=1)
        running = True
        threading.Thread(target=read_serial_data, daemon=True).start()
    except Exception as e:
        print(f"Serial Error: {e}")

def stop_serial():
    global running
    running = False
    if ser:
        ser.close()

def clear_data():
    time_data.clear()
    temp_data.clear()
    hum_data.clear()
    update_graph()

# ---------------- DATA CALCULATION SECTION ----------------
data_calculation_frame = tk.Frame(dashboard_screen, bg="#ffccbc", width=400, height=300)
data_calculation_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

data_calculation_label = tk.Label(data_calculation_frame, text="Data Calculation", font=("Arial", 14, "bold"), bg="#ff7043", fg="white")
data_calculation_label.pack(pady=10)

# Labels for Min, Max, and Average Values
min_label = tk.Label(data_calculation_frame, text="Min Value: --", font=("Arial", 12), bg="#ffccbc")
min_label.pack(pady=5)

max_label = tk.Label(data_calculation_frame, text="Max Value: --", font=("Arial", 12), bg="#ffccbc")
max_label.pack(pady=5)

avg_label = tk.Label(data_calculation_frame, text="Avg Value: --", font=("Arial", 12), bg="#ffccbc")
avg_label.pack(pady=5)

# Function to Update Calculations
def update_calculations():
    if y_data:
        min_value = min(y_data)
        max_value = max(y_data)
        avg_value = sum(y_data) / len(y_data)

        min_label.config(text=f"Min Value: {min_value:.2f}"),
        max_label.config(text=f"Max Value: {max_value:.2f}"),
        avg_label.config(text=f"Avg Value: {avg_value:.2f}"),

# Modify read_serial_data() to update calculations
def read_serial_data():
    global running
    while running:
        if ser and ser.is_open:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Split the received data into two values (Temperature and Humidity)
                    temp_str, hum_str = line.split(",")  
                    temp = float(temp_str)  # Convert Temperature
                    hum = float(hum_str)    # Convert Humidity

                    # Update UI with the extracted values
                    root.after(0, lambda: update_ui(current_time, temp, hum))
            except ValueError as e:
                print(f"Data Format Error: {e}, Received: {line}")
            except Exception as e:
                print(f"Serial Read Error: {e}")


# Footer Section
footer_frame = tk.Frame(root, bg="purple", height=50)
footer_frame.pack(side="bottom", fill="x")

test_ok_label = tk.Label(footer_frame, text="TEST OK", font=("Arial", 16, "bold"), fg="white", bg="#344955")
footer_content = tk.Frame(footer_frame, bg="purple")

if logo_tk:
    logo_label_footer = tk.Label(footer_frame, image=logo_tk, bg="#344955")
    logo_label_footer.pack(side="right", padx=15)
# Dictionary to manage screens
screens = {"Home": home_screen, "Dashboard": dashboard_screen}
show_screen("Home")

root.mainloop()   




