import serial
import time
import tkinter as tk
import re  # For regex filtering

# --- Serial Setup ---
PORT = 'COM1'  # Change to your port
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD, timeout=0)
    time.sleep(2)  # Allow device reset
except serial.SerialException as e:
    print(f"Error opening {PORT}: {e}")
    ser = None

# --- GUI Setup ---
root = tk.Tk()
root.title("COM Port Data Viewer")
root.geometry("300x150")

label = tk.Label(root, text="Waiting for data...", font=("Arial", 24))
label.pack(expand=True)

def read_serial():
    """Read from serial, filter numbers, and update display."""
    if ser and ser.in_waiting > 0:
        try:
            raw_data = ser.readline().decode('utf-8', errors='replace').strip()
            # Keep only numbers, decimal points, and minus signs
            clean_data = re.sub(r"[^0-9.\-]", "", raw_data)
            if clean_data:
                label.config(text=f"{clean_data} T")
        except serial.SerialException as e:
            label.config(text=f"Error: {e}")
    root.after(50, read_serial)

root.after(50, read_serial)

try:
    root.mainloop()
except KeyboardInterrupt:
    pass
finally:
    if ser:
        ser.close()
