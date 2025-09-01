import serial
import serial.tools.list_ports
import win32com.client as win32
import time

# Configuración del puerto serie
puertos = serial.tools.list_ports.comports()
if not puertos:
    print("No se encontró ningún puerto serie.")
    exit()

puerto = puertos[0].device
baudrate = 9600
ser = serial.Serial(puerto, baudrate, timeout=1)

# Conectar con Excel abierto
excel = win32.Dispatch("Excel.Application")
wb = excel.ActiveWorkbook  # Toma el libro activo
ws = wb.ActiveSheet        # Toma la hoja activa

# Encontrar la primera fila vacía en columna B
def primera_fila_vacia():
    fila = 2
    while ws.Cells(fila, 2).Value is not None:
        fila += 1
    return fila

print(f"Esperando datos en {puerto}...")

try:
    while True:
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8').strip()
            if linea:
                fila = primera_fila_vacia()
                ws.Cells(fila, 2).Value = linea
                print(f"Fila {fila} -> {linea}")
                # Opcional: guardar cambios
                wb.Save()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Lectura interrumpida por el usuario")
    ser.close()
