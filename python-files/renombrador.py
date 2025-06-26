
import os
import unicodedata
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def renombrar_archivos_y_carpetas(directorio):
    backup_file = os.path.join(directorio, "backup_nombres.txt")
    with open(backup_file, "w", encoding="utf-8") as backup:
        backup.write(f"Backup generado el {datetime.now()}\n\n")

        # Renombrar carpetas (de más profunda a raíz)
        for root, dirs, files in os.walk(directorio, topdown=False):
            for nombre in dirs:
                ruta_original = os.path.join(root, nombre)
                nombre_nuevo = normalizar_nombre(nombre)
                ruta_nueva = os.path.join(root, nombre_nuevo)
                if ruta_original != ruta_nueva:
                    backup.write(f"CARPETA: {ruta_original} -> {ruta_nueva}\n")
                    os.rename(ruta_original, ruta_nueva)

        # Renombrar archivos
        for root, dirs, files in os.walk(directorio):
            for nombre in files:
                ruta_original = os.path.join(root, nombre)
                nombre_nuevo = normalizar_nombre(nombre)
                ruta_nueva = os.path.join(root, nombre_nuevo)
                if ruta_original != ruta_nueva:
                    backup.write(f"ARCHIVO: {ruta_original} -> {ruta_nueva}\n")
                    os.rename(ruta_original, ruta_nueva)

    print("Renombramiento completado. Backup guardado en:", backup_file)

def normalizar_nombre(nombre):
    nombre_sin_acentos = unicodedata.normalize('NFKD', nombre)
    nombre_ascii = nombre_sin_acentos.encode('ascii', 'ignore').decode('ascii')
    caracteres_invalidos = '<>:"/\\|?*'
    nombre_final = ''.join(c if c not in caracteres_invalidos else '_' for c in nombre_ascii)
    return nombre_final

# Interfaz gráfica
root = tk.Tk()
root.withdraw()
carpeta = filedialog.askdirectory(title="Selecciona la carpeta con archivos/carpetas a renombrar")

if carpeta:
    renombrar_archivos_y_carpetas(carpeta)
else:
    print("No se seleccionó ninguna carpeta.")
