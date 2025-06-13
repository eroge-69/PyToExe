import socket
import struct
import tkinter as tk
from tkinter import ttk

# Dirección IP y puerto del adaptador RS485-Ethernet
IP = '10.60.3.134'
PORT = 26

# Comando para leer información básica (0x03)
# DD A5 03 00 FF FD 77
READ_BASIC_INFO = bytes([0xDD, 0xA5, 0x03, 0x00, 0xFF, 0xFD, 0x77])

def checksum(data):
    s = sum(data)
    chk = (~s + 1) & 0xFFFF
    return chk.to_bytes(2, byteorder='big')

def parse_basic_info(data):
    # Evita los primeros 4 bytes y últimos 3 (cabecera y pie)
    raw = data[4:-3]

    # Extrae valores
    total_voltage = int.from_bytes(raw[0:2], 'big') * 0.01  # en V
    current_raw = int.from_bytes(raw[2:4], 'big')
    current = (current_raw - 65536) * 0.01 if current_raw > 32767 else current_raw * 0.01
    residual_capacity = int.from_bytes(raw[4:6], 'big') * 0.01
    nominal_capacity = int.from_bytes(raw[6:8], 'big') * 0.01
    cycle_life = int.from_bytes(raw[8:10], 'big')

    year = 2000 + (raw[10] >> 1)
    month = ((raw[10] & 0x01) << 3) | (raw[11] >> 5)
    day = raw[11] & 0x1F

    version = raw[18]
    rsoc = raw[19]
    mos_status = raw[20]
    cell_series = raw[21]
    ntc_num = raw[22]

    temps = []
    for i in range(ntc_num):
        temp = int.from_bytes(raw[23 + i * 2:25 + i * 2], 'big')
        temps.append((temp - 2731) * 0.1)

    return {
        'Tensión Total (V)': total_voltage,
        'Corriente (A)': current,
        'Capacidad Residual (Ah)': residual_capacity,
        'Capacidad Nominal (Ah)': nominal_capacity,
        'Ciclos': cycle_life,
        'Fecha Fabricación': f"{year}-{month:02d}-{day:02d}",
        'Versión': f"{version / 10:.1f}",
        'SOC (%)': rsoc,
        'MOS': bin(mos_status),
        'Celdas en Serie': cell_series,
        'Temperaturas (°C)': temps
    }

def get_battery_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((IP, PORT))
        s.sendall(READ_BASIC_INFO)
        data = s.recv(1024)
    return parse_basic_info(data)

def actualizar_datos():
    try:
        info = get_battery_data()
        for key, value in info.items():
            if isinstance(value, list):
                value = ', '.join(f"{v:.2f}" for v in value)
            etiquetas[key].config(text=f"{key}: {value}")
    except Exception as e:
        for lbl in etiquetas.values():
            lbl.config(text="Error de lectura")
        print(f"Error: {e}")
    root.after(3000, actualizar_datos)

# GUI con Tkinter
root = tk.Tk()
root.title("Monitor de Batería BMS")

etiquetas = {}
for campo in ['Tensión Total (V)', 'Corriente (A)', 'Capacidad Residual (Ah)', 'Capacidad Nominal (Ah)',
              'Ciclos', 'Fecha Fabricación', 'Versión', 'SOC (%)', 'MOS', 'Celdas en Serie', 'Temperaturas (°C)']:
    etiquetas[campo] = ttk.Label(root, text=f"{campo}: --", font=("Arial", 12))
    etiquetas[campo].pack(anchor='w', padx=10, pady=2)

root.after(1000, actualizar_datos)
root.mainloop()