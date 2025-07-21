
import struct
from tkinter import filedialog, Tk, simpledialog, messagebox

def leer_valor(data, offset, length, endian='little'):
    return int.from_bytes(data[offset:offset+length], endian)

def escribir_valor(data, offset, length, valor, endian='little'):
    valor_bytes = valor.to_bytes(length, endian)
    data[offset:offset+length] = valor_bytes

# Configuración de offsets conocidos
offsets_kilometros = [(678, 3), (1523, 3)]
offsets_horas = [(672, 2)]

# Interfaz
Tk().withdraw()
ruta = filedialog.askopenfilename(title="Seleccionar archivo binario", filetypes=[("Archivos bin", "*.bin")])
if not ruta:
    exit("No se seleccionó archivo.")

with open(ruta, "rb") as f:
    data = bytearray(f.read())

valores_km = [leer_valor(data, offset, length) for offset, length in offsets_kilometros]
valores_hr = [leer_valor(data, offset, length) for offset, length in offsets_horas]

mensaje = "\n".join([f"Kilómetros en {offset}: {val}" for (offset, _), val in zip(offsets_kilometros, valores_km)])
mensaje += "\n" + "\n".join([f"Horas motor en {offset}: {val}" for (offset, _), val in zip(offsets_horas, valores_hr)])
messagebox.showinfo("Valores actuales", mensaje)

nuevo_km = simpledialog.askstring("Modificar kilómetros", "Nuevo valor de kilómetros (Enter para no cambiar):")
if nuevo_km and nuevo_km.strip().isdigit():
    nuevo_km = int(nuevo_km)
    for offset, length in offsets_kilometros:
        escribir_valor(data, offset, length, nuevo_km)

nuevo_hr = simpledialog.askstring("Modificar horas motor", "Nuevo valor de horas motor (Enter para no cambiar):")
if nuevo_hr and nuevo_hr.strip().isdigit():
    nuevo_hr = int(nuevo_hr)
    for offset, length in offsets_horas:
        escribir_valor(data, offset, length, nuevo_hr)

ruta_guardado = filedialog.asksaveasfilename(title="Guardar como", defaultextension=".bin", filetypes=[("Archivos bin", "*.bin")])
if ruta_guardado:
    with open(ruta_guardado, "wb") as f:
        f.write(data)
    messagebox.showinfo("Éxito", f"Archivo guardado como: {ruta_guardado}")
