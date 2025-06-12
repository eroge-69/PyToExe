import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import pandas as pd
import csv
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
import re

version = "v1.2" #current RTLCcontrol version
current_datetime = time.localtime()
default_batch = f"{current_datetime.tm_mday:02d}{current_datetime.tm_mon:02d}{current_datetime.tm_year % 100:02d}RF"

def list_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def send_data():
    """Sends acquisition parameters through serial port, reads results and updates the graph."""
    global ser, positions, counts

    batch = entry_batch.get()
    operator = entry_operator.get()
    distance = entry_distance.get()
    origin = entry_origin.get()
    front = entry_front.get()
    acq_time = entry_acq_time.get()
    port = combobox_ports.get()

    # Field validation
    if not batch:
        messagebox.showerror("Error", "Fill batch.")
        return
    if not operator.isalpha():
        messagebox.showerror("Error", "Operator must only contain letters.")
        return
    if not distance.isdigit() or not (10 <= int(distance) <= 120):
        messagebox.showerror("Error", "Distance must be between 10 and 120 mm.")
        return
    if not origin.isdigit() or not (1 <= int(origin) <= 120):
        messagebox.showerror("Error", "Solvent origin must be between 1 and 120 mm.")
        return
    if not front.isdigit() or not (1 <= int(front) <= 120):
        messagebox.showerror("Error", "Solvent front must be between 1 and 120 mm.")
        return    
    if not acq_time.isdigit() or int(acq_time) < 1:
        messagebox.showerror("Error", "Time must be at least 1 minute.")
        return
    if not port:
        messagebox.showerror("Error", "Select a valid COM port.")
        return

    try:
        # Serial port settings
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        data = f"{batch},{operator},{distance},{acq_time}\n"
        ser.write(data.encode())  
        ser.flush()

        # Graph settings
        ax.clear()
        ax.set_xlabel("Position (mm)")
        ax.set_ylabel("counts")
        fig.tight_layout()
        canvas.draw()

        positions = []
        counts = []

        btn_run.config(text="MEASURING", state="disabled")

        root.update()

        def end_acquisition():
            #Ends acquisition and saves results.       
            if ser and ser.is_open:
                ser.close()

            # Saves results in CSV
            data = {"Position": positions, "counts": counts}
            df = pd.DataFrame(data)
            csv_name = f"{batch}.csv"
            df['Position'] = df['Position'].apply(lambda x: f"{x:.1f}".replace('.', ','))
            df.to_csv(csv_name, index=False, sep=';')
            
            # Adds variables as metadata
            with open(csv_name, mode='a', encoding='utf-8') as archive:
                archive.write(f"Batch:;{batch}\nOperator:;{operator}\nRange:;{distance} mm\nSolvent origin:;{origin} mm\nSolvent front:;{front} mm\nAcquisition time:;{acq_time} min\nDevice:;{deviceID}\nFirmware:;{firmware}\nRTLC Control version:;{version}\n")
                archive.write(f"Date:;{time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime())}\n")

            # Adds hash to CSV
            with open(csv_name, "rb") as archive:
                hash_sha256 = hashlib.sha256()
                for line in archive:
                    hash_sha256.update(line)
                hash=hash_sha256.hexdigest()
                
            with open(csv_name, mode='a', encoding='utf-8') as archive:
                archive.write(f"SHA256 footprint:;{hash}")
                
            btn_run.config(text="START", state="normal")

        def read_port():
            #Reads serial port and updates graph.
            global firmware, deviceID
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("end_"):
                        try:
                            firmware, deviceID = line[4:].split("_",1)
                        except:
                            pass
                        end_acquisition()
                        return
                    if line:
                        position, count = map(int, line.split(";"))
                        positions.append(position/10)
                        counts.append(count)
                        # Updates graph
                        ax.clear()
                        ax.plot(positions, counts, marker="o", markersize=0.1, linestyle="-", color="blue")
                        ax.set_xlabel("Position (mm)")
                        ax.set_ylabel("Counts")
                        ax.set_xlim(0, float(distance))
                        ax.set_ylim(0,)
                        fig.tight_layout()
                        canvas.draw()
                except ValueError:
                    pass

            root.after(100, read_port)

        read_port()

    except serial.SerialException as e:
        messagebox.showerror("Error", f"Couldn't open serial port: {e}")
        btn_run.config(text="START", state="normal")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        btn_run.config(text="START", state="normal")

root = tk.Tk()
root.title(f"RTLC Control {version}")

# Labels and data entry
tk.Label(root, text="Batch:", anchor="e").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_batch = tk.Entry(root)
entry_batch.insert(0, default_batch)
entry_batch.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Operator:", anchor="e").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_operator = tk.Entry(root)
entry_operator.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Range (mm):", anchor="e").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_distance = tk.Entry(root)
entry_distance.insert(0, 120)
entry_distance.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Solvent origin (mm):", anchor="e").grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_origin = tk.Entry(root)
entry_origin.insert(0, 10)
entry_origin.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Solvent front (mm):", anchor="e").grid(row=4, column=0, padx=10, pady=5, sticky="e")
entry_front = tk.Entry(root)
entry_front.insert(0, 90)
entry_front.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Time (min):", anchor="e").grid(row=5, column=0, padx=10, pady=5, sticky="e")
entry_acq_time = tk.Entry(root)
entry_acq_time.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="COM port:", anchor="e").grid(row=6, column=0, padx=10, pady=5, sticky="e")
ports = list_ports()
combobox_ports = ttk.Combobox(root, values=ports, state="readonly")
combobox_ports.grid(row=6, column=1, padx=10, pady=5)

btn_run = tk.Button(root, text="START", command=send_data, font=("Helvetica", 15, "bold"))
btn_run.grid(row=8, column=0, columnspan=2, pady=20, sticky="ew")

# Graph area
fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=10, column=0, columnspan=2, pady=10)


root.mainloop()
