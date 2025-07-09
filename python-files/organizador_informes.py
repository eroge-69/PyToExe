
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import re
from datetime import datetime

DESTINO_BASE = r"\\10.112.0.30\dfs\Spagna\Operaciones\11-Informes Calidad"

MAPEO_CARPETAS = {
    "CONTROL LONGITUD AZUL": ["Linea Azul", "Cortadora", "Control de Longitud"],
    "CONTROL LONGITUD VERDE": ["Linea Verde", "Cortadora", "Control de Longitud"],
    "CONTROL CALIDAD AZUL": ["Linea Azul", "Espumadora", "Control de Calidad"],
    "CONTROL CALIDAD VERDE": ["Linea Verde", "Espumadora", "Control de Calidad"],
    "CONTROL ACERO AZUL": ["Linea Azul", "Perfiladora", "Control de Acero"],
    "CONTROL ACERO VERDE": ["Linea Verde", "Perfiladora", "Control de Acero"],
    "CONTROL LONGITUD EMBALADORA": ["Embaladora", "Control de Longitud"],
}

def extraer_info(nombre_archivo):
    nombre_sin_ext = os.path.splitext(nombre_archivo)[0]
    match = re.match(r"(.+?)_(\d{8})", nombre_sin_ext)
    if not match:
        return None, None
    clave, fecha_str = match.groups()
    clave = clave.strip().upper()
    try:
        fecha = datetime.strptime(fecha_str, "%Y%m%d")
    except ValueError:
        return clave, None
    return clave, fecha

def organizar_archivos(origen, estado_label):
    archivos = [f for f in os.listdir(origen) if f.lower().endswith(".pdf")]
    if not archivos:
        estado_label.config(text="No hay archivos PDF en la carpeta seleccionada.")
        return

    for archivo in archivos:
        clave, fecha = extraer_info(archivo)
        if clave not in MAPEO_CARPETAS or fecha is None:
            estado_label.config(text=f"Archivo ignorado: {archivo}")
            continue

        ruta_destino = os.path.join(DESTINO_BASE, *MAPEO_CARPETAS[clave], str(fecha.year), fecha.strftime("%B"))
        os.makedirs(ruta_destino, exist_ok=True)

        origen_path = os.path.join(origen, archivo)
        destino_path = os.path.join(ruta_destino, archivo)
        try:
            shutil.move(origen_path, destino_path)
        except Exception as e:
            estado_label.config(text=f"Error moviendo {archivo}: {str(e)}")
            continue

    estado_label.config(text="Archivos organizados correctamente.")

def seleccionar_carpeta(entrada):
    ruta = filedialog.askdirectory()
    if ruta:
        entrada.delete(0, tk.END)
        entrada.insert(0, ruta)

def main():
    ventana = tk.Tk()
    ventana.title("Organizador de Informes PDF")
    ventana.geometry("500x200")

    tk.Label(ventana, text="Carpeta de origen:").pack(pady=5)
    entrada = tk.Entry(ventana, width=50)
    entrada.pack(pady=5)

    btn_buscar = tk.Button(ventana, text="Seleccionar carpeta", command=lambda: seleccionar_carpeta(entrada))
    btn_buscar.pack(pady=5)

    estado = tk.Label(ventana, text="", fg="blue")
    estado.pack(pady=5)

    btn_organizar = tk.Button(ventana, text="Organizar archivos", command=lambda: organizar_archivos(entrada.get(), estado))
    btn_organizar.pack(pady=10)

    ventana.mainloop()

if __name__ == "__main__":
    main()
