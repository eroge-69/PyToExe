import tkinter as tk
from tkinter import ttk, messagebox
from pymodbus.client import ModbusSerialClient
import pandas as pd
import threading
import time
from datetime import datetime
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Globals
running = False
data_log = []

# Get available COM ports
def list_com_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

# Modbus setup
def setup_modbus(port, baudrate):
    return ModbusSerialClient(
        method='rtu',
        port=port,
        baudrate=baudrate,
        stopbits=1,
        bytesize=8,
        parity='N',
        timeout=1
    )

# Logging loop
def start_logging():
    global running, data_log
    port = port_combo.get()
    baudrate = int(baud_entry.get())
    addresses = list(map(int, register_entry.get().split(',')))
    slave_id = int(slave_entry.get())
    interval = float(interval_entry.get())

    client = setup_modbus(port, baudrate)
    if not client.connect():
        log_var.set(f"❌ Failed to connect to {port}")
        return

    running = True
    data_log = []

    while running:
        timestamp = datetime.now()
        row = {"Timestamp": timestamp}
        try:
            for addr in addresses:
                result = client.read_holding_registers(addr, 1, unit=slave_id)
                if result.isError():
                    row[f"Reg{addr}"] = None
                    log_var.set(f"❌ Error reading Reg {addr}")
                else:
                    row[f"Reg{addr}"] = result.registers[0]
                    log_var.set(f"✅ {timestamp} - Reg{addr}: {result.registers[0]}")
            data_log.append(row)
            update_chart(addresses)
        except Exception as e:
            log_var.set(f"❌ Exception: {e}")
        time.sleep(interval)
    client.close()

# Update chart
def update_chart(addresses):
    if not data_log:
        return
    df = pd.DataFrame(data_log)
    ax.clear()
    for addr in addresses:
        reg_col = f"Reg{addr}"
        if reg_col in df.columns:
            ax.plot(df["Timestamp"], df[reg_col], label=reg_col)
    ax.legend()
    ax.set_title("Real-Time Register Values")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    fig.autofmt_xdate()
    canvas.draw()

# Start logging thread
def start_thread():
    threading.Thread(target=start_logging, daemon=True).start()

# Stop logging
def stop_logging():
    global running
    running = False

# Save to Excel
def save_excel():
    if data_log:
        df = pd.DataFrame(data_log)
        df.to_excel("plc_log.xlsx", index=False)
        messagebox.showinfo("Saved", "Data saved to plc_log.xlsx")
    else:
        messagebox.showinfo("No Data", "Nothing to save!")

# GUI setup
root = tk.Tk()
root.title("Delta PLC Modbus Logger")

tk.Label(root, text="COM Port:").grid(row=0, column=0)
port_combo = ttk.Combobox(root, values=list_com_ports())
port_combo.set("COM3")
port_combo.grid(row=0, column=1)

tk.Label(root, text="Baud Rate:").grid(row=1, column=0)
baud_entry = tk.Entry(root)
baud_entry.insert(0, "9600")
baud_entry.grid(row=1, column=1)

tk.Label(root, text="Register Addresses (comma-separated):").grid(row=2, column=0)
register_entry = tk.Entry(root)
register_entry.insert(0, "0,1,2")
register_entry.grid(row=2, column=1)

tk.Label(root, text="Slave ID:").grid(row=3, column=0)
slave_entry = tk.Entry(root)
slave_entry.insert(0, "1")
slave_entry.grid(row=3, column=1)

tk.Label(root, text="Interval (s):").grid(row=4, column=0)
interval_entry = tk.Entry(root)
interval_entry.insert(0, "2")
interval_entry.grid(row=4, column=1)

log_var = tk.StringVar()
tk.Label(root, textvariable=log_var, fg="blue").grid(row=5, columnspan=2)

tk.Button(root, text="Start Logging", command=start_thread).grid(row=6, column=0)
tk.Button(root, text="Stop", command=stop_logging).grid(row=6, column=1)
tk.Button(root, text="Save to Excel", command=save_excel).grid(row=7, columnspan=2)

# Real-time chart area
fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)

root.mainloop()
