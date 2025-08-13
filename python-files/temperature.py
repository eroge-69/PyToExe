import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = None
reading = False
temps, hums = [], []

def find_first_port():
    """Return the first available COM port."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        return None
    return ports[0].device  # Take first port found

def start_reading():
    global ser, reading
    if reading:
        return  # Already reading
    port_name = find_first_port()
    if not port_name:
        label_temp.config(text="No device found")
        return
    ser = serial.Serial(port_name, 9600, timeout=2)
    print(f"Using port: {port_name}")
    reading = True
    update_data()

def stop_reading():
    global reading, ser
    reading = False
    if ser and ser.is_open:
        ser.close()
    print("Stopped reading")

def update_data():
    global temps, hums
    if not reading:
        return
    try:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            print("Received:", line)
            parts = line.replace(" ", "").split(",")
            if len(parts) == 2:
                try:
                    t = float(parts[0])
                    h = float(parts[1])
                    temps.append(t)
                    hums.append(h)
                    if len(temps) > 50:
                        temps = temps[-50:]
                        hums = hums[-50:]
                    label_temp.config(text=f"Temperature: {t:.1f} °C")
                    label_hum.config(text=f"Humidity: {h:.1f} %")
                    line1.set_data(range(len(temps)), temps)
                    line2.set_data(range(len(hums)), hums)
                    ax.set_xlim(0, max(50, len(temps)))
                    canvas.draw()
                except ValueError:
                    pass
    except Exception as e:
        print("Error reading data:", e)
    root.after(1000, update_data)

# GUI Setup
root = tk.Tk()
root.title("Temperature & Humidity Monitor")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

label_temp = ttk.Label(frame, text="Temperature: -- °C", font=("Arial", 14))
label_temp.pack(pady=5)

label_hum = ttk.Label(frame, text="Humidity: -- %", font=("Arial", 14))
label_hum.pack(pady=5)

# Buttons
btn_frame = ttk.Frame(frame)
btn_frame.pack(pady=10)

btn_start = ttk.Button(btn_frame, text="Start", command=start_reading)
btn_start.grid(row=0, column=0, padx=5)

btn_stop = ttk.Button(btn_frame, text="Stop", command=stop_reading)
btn_stop.grid(row=0, column=1, padx=5)

# Plot
fig, ax = plt.subplots(figsize=(5, 3))
line1, = ax.plot([], [], label="Temp (°C)")
line2, = ax.plot([], [], label="Hum (%)")
ax.set_xlim(0, 50)
ax.set_ylim(0, 100)
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().pack()

root.mainloop()
