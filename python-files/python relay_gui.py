import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports

# Global serial object
ser = None

# Relay states
relay1_state = False  # DTR
relay2_state = False  # RTS

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def open_serial():
    global ser
    port = com_port_var.get()
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        status_label.config(text=f"Connected to {port}", fg="green")
        open_button.config(state="disabled")
        close_button.config(state="normal")
        toggle1_button.config(state="normal")
        toggle2_button.config(state="normal")
    except serial.SerialException as e:
        messagebox.showerror("Serial Error", f"Failed to open {port}:\n{e}")

def close_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
    status_label.config(text="Disconnected", fg="red")
    open_button.config(state="normal")
    close_button.config(state="disabled")
    toggle1_button.config(state="disabled")
    toggle2_button.config(state="disabled")
    update_relay_indicator(1, False)
    update_relay_indicator(2, False)

def toggle_relay(relay_num):
    global relay1_state, relay2_state
    if relay_num == 1:
        relay1_state = not relay1_state
        ser.dtr = relay1_state
        update_relay_indicator(1, relay1_state)
    elif relay_num == 2:
        relay2_state = not relay2_state
        ser.rts = relay2_state
        update_relay_indicator(2, relay2_state)

def update_relay_indicator(relay_num, state):
    color = "green" if state else "red"
    text = "ON" if state else "OFF"
    if relay_num == 1:
        relay1_indicator.config(bg=color, text=f"Relay 1 (DTR): {text}")
    elif relay_num == 2:
        relay2_indicator.config(bg=color, text=f"Relay 2 (RTS): {text}")

# UI setup
root = tk.Tk()
root.title("Relay Controller (RS-232 DTR/RTS)")

tk.Label(root, text="Select COM Port:").pack(pady=5)
com_port_var = tk.StringVar()
com_ports = list_serial_ports()
com_port_menu = ttk.Combobox(root, textvariable=com_port_var, values=com_ports, state="readonly")
com_port_menu.pack()

open_button = tk.Button(root, text="Open Port", command=open_serial)
open_button.pack(pady=5)

close_button = tk.Button(root, text="Close Port", command=close_serial, state="disabled")
close_button.pack(pady=5)

relay1_indicator = tk.Label(root, text="Relay 1 (DTR): OFF", bg="red", fg="white", width=20)
relay1_indicator.pack(pady=5)
toggle1_button = tk.Button(root, text="Toggle Relay 1", command=lambda: toggle_relay(1), state="disabled")
toggle1_button.pack()

relay2_indicator = tk.Label(root, text="Relay 2 (RTS): OFF", bg="red", fg="white", width=20)
relay2_indicator.pack(pady=5)
toggle2_button = tk.Button(root, text="Toggle Relay 2", command=lambda: toggle_relay(2), state="disabled")
toggle2_button.pack()

status_label = tk.Label(root, text="Disconnected", fg="red")
status_label.pack(pady=10)

def on_exit():
    close_serial()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
