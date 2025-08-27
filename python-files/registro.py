import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json

CONFIG_FILE = "config.json"

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)

def elegir_carpeta():
    carpeta = filedialog.askdirectory(title="Elige la carpeta donde guardar datos.txt")
    if carpeta:
        config["carpeta"] = carpeta
        guardar_config(config)
        messagebox.showinfo("Carpeta elegida", f"Los datos se guardarán en:\n{carpeta}")
    return config.get("carpeta", "")

def guardar(event=None):
    texto = entrada.get().strip()
    if texto:
        carpeta = config.get("carpeta", "")
        if not carpeta:
            carpeta = elegir_carpeta()
        if carpeta:
            ruta = os.path.join(carpeta, "datos.txt")
            with open(ruta, "a", encoding="utf-8") as f:
                f.write(texto + "\n")
            entrada.delete(0, tk.END)

# --------- INTERFAZ ----------
config = cargar_config()

root = tk.Tk()
root.title("Registro de Datos")

entrada = tk.Entry(root, font=("Arial", 18), justify="center")
entrada.pack(padx=20, pady=20)
entrada.bind("<Return>", guardar)
entrada.focus()

boton_carpeta = tk.Button(root, text="Elegir Carpeta", command=elegir_carpeta)
boton_carpeta.pack(pady=10)

root.mainloop()
