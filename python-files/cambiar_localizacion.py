
import tkinter as tk
from tkinter import filedialog, messagebox
import os

config_file = "config_ruta.txt"

def guardar_ruta(ruta):
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(ruta)

def cargar_ruta():
    if os.path.isfile(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def modificar_xml(ruta, nueva_localizacion):
    try:
        with open(ruta, "r", encoding="utf-8") as file:
            contenido = file.read()
        contenido_modificado = contenido.replace("<Val>+&amp", f"<Val>{nueva_localizacion}&amp")
        with open(ruta, "w", encoding="utf-8") as file:
            file.write(contenido_modificado)
        guardar_ruta(os.path.dirname(ruta))
        messagebox.showinfo("Proceso completado", f"Archivo modificado correctamente:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def seleccionar_archivo():
    ruta_inicial = cargar_ruta()
    archivo = filedialog.askopenfilename(
        title="Selecciona archivo XML",
        filetypes=[("Archivos XML", "*.xml")],
        initialdir=ruta_inicial if os.path.isdir(ruta_inicial) else os.getcwd()
    )
    if archivo:
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, archivo)

def ejecutar():
    ruta = entry_ruta.get()
    loc = entry_localizacion.get()
    if not ruta or not os.path.isfile(ruta):
        messagebox.showerror("Error", "Selecciona un archivo XML válido.")
        return
    if not loc.startswith("+"):
        messagebox.showerror("Error", "La localización debe comenzar con '+'.")
        return
    modificar_xml(ruta, loc)

root = tk.Tk()
root.title("Cambiar Localización en XML EPLAN")
root.geometry("500x200")

tk.Label(root, text="Archivo XML:").pack(pady=(10,0))
frame_ruta = tk.Frame(root)
entry_ruta = tk.Entry(frame_ruta, width=50)
btn_buscar = tk.Button(frame_ruta, text="Buscar", command=seleccionar_archivo)
entry_ruta.pack(side=tk.LEFT, padx=(0,5))
btn_buscar.pack(side=tk.LEFT)
frame_ruta.pack(pady=5)

tk.Label(root, text="Nueva Localización (ej. +A01):").pack(pady=(10,0))
entry_localizacion = tk.Entry(root, width=20)
entry_localizacion.pack()

btn_ejecutar = tk.Button(root, text="Modificar XML", command=ejecutar, bg="#4CAF50", fg="white")
btn_ejecutar.pack(pady=20)

root.mainloop()
