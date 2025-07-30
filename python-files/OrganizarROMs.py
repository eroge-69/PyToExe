import os
import string
import tkinter as tk
from tkinter import filedialog, messagebox

# === Funcionamiento del renombrador ===
def primera_letra_valida(nombre):
    for c in nombre:
        if c.upper() in string.ascii_uppercase:
            return c.upper()
    return "~"

def renombrar_roms():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con ROMs")
    if not carpeta:
        return

    archivos = [f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]
    archivos.sort(key=lambda x: primera_letra_valida(x))

    if not archivos:
        messagebox.showwarning("Vacío", "La carpeta no contiene archivos.")
        return

    renombrados = 0

    for i, archivo in enumerate(archivos, start=1):
        nombre_original, extension = os.path.splitext(archivo)
        nuevo_nombre = f"{i}º {nombre_original}{extension}"
        origen = os.path.join(carpeta, archivo)
        destino = os.path.join(carpeta, nuevo_nombre)

        if os.path.exists(destino):
            continue

        os.rename(origen, destino)
        renombrados += 1

    messagebox.showinfo("Renombrado completo", f"{renombrados} archivos renombrados con éxito.")

# === Interfaz gráfica ===
ventana = tk.Tk()
ventana.title("Renombrador de ROMs")
ventana.geometry("300x150")
ventana.resizable(False, False)

label = tk.Label(ventana, text="Haz clic para seleccionar la carpeta con ROMs", wraplength=250, pady=20)
label.pack()

boton = tk.Button(ventana, text="Seleccionar carpeta", command=renombrar_roms)
boton.pack()

ventana.mainloop()
