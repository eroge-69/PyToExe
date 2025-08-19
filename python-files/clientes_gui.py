import tkinter as tk
from tkinter import messagebox
import csv
import os

archivo_csv = "clientes.csv"

# Crear archivo si no existe
if not os.path.exists(archivo_csv):
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["Nombre", "RTN"])

# Función para agregar cliente
def agregar_cliente():
    nombre = entrada_nombre.get()
    rtn = entrada_rtn.get()

    if not nombre or not rtn:
        messagebox.showwarning("Campos vacíos", "Por favor ingrese nombre y RTN.")
        return

    with open(archivo_csv, mode='a', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([nombre, rtn])
    messagebox.showinfo("Éxito", "Cliente agregado exitosamente.")
    entrada_nombre.delete(0, tk.END)
    entrada_rtn.delete(0, tk.END)

# Función para consultar cliente
def consultar_cliente():
    buscar = entrada_buscar.get().lower()
    resultados = []

    with open(archivo_csv, mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            if buscar in fila["Nombre"].lower() or buscar in fila["RTN"]:
                resultados.append(f"{fila['Nombre']} - RTN: {fila['RTN']}")

    if resultados:
        resultado_texto.set("\n".join(resultados))
    else:
        resultado_texto.set("Cliente no encontrado.")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Gestión de Clientes")

# Sección agregar
tk.Label(ventana, text="Nombre:").grid(row=0, column=0)
entrada_nombre = tk.Entry(ventana)
entrada_nombre.grid(row=0, column=1)

tk.Label(ventana, text="RTN:").grid(row=1, column=0)
entrada_rtn = tk.Entry(ventana)
entrada_rtn.grid(row=1, column=1)

tk.Button(ventana, text="Agregar Cliente", command=agregar_cliente).grid(row=2, column=0, columnspan=2, pady=5)

# Sección consultar
tk.Label(ventana, text="Buscar por nombre o RTN:").grid(row=3, column=0)
entrada_buscar = tk.Entry(ventana)
entrada_buscar.grid(row=3, column=1)

tk.Button(ventana, text="Consultar Cliente", command=consultar_cliente).grid(row=4, column=0, columnspan=2, pady=5)

resultado_texto = tk.StringVar()
tk.Label(ventana, textvariable=resultado_texto, fg="blue", wraplength=300).grid(row=5, column=0, columnspan=2)

ventana.mainloop()