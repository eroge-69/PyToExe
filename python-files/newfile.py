import pandas as pd
import tkinter as tk
from tkinter import filedialog

def cargar_archivo():
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    if ruta_archivo:
        global df
        df = pd.read_excel(ruta_archivo, engine="openpyxl")
        lbl_estado.config(text=f"Archivo cargado: {ruta_archivo}")

def agregar_datos():
    if 'df' in globals():
        df["Nueva_Columna"] = "Valor predeterminado"
        nueva_fila = {"Columna1": "Nuevo dato 1", "Columna2": "Nuevo dato 2", "Nueva_Columna": "Nuevo dato"}
        df.loc[len(df)] = nueva_fila
        lbl_estado.config(text="Datos agregados correctamente")
    else:
        lbl_estado.config(text="Primero carga un archivo")

def guardar_archivo():
    if 'df' in globals():
        ruta_guardado = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos Excel", "*.xlsx")])
        if ruta_guardado:
            df.to_excel(ruta_guardado, index=False, engine="openpyxl")
            lbl_estado.config(text=f"Archivo guardado en: {ruta_guardado}")
    else:
        lbl_estado.config(text="No hay datos para guardar")

# Crear la ventana
ventana = tk.Tk()
ventana.title("Editor de Excel")

tk.Button(ventana, text="Cargar Archivo", command=cargar_archivo).pack(pady=5)
tk.Button(ventana, text="Agregar Datos", command=agregar_datos).pack(pady=5)
tk.Button(ventana, text="Guardar Archivo", command=guardar_archivo).pack(pady=5)

lbl_estado = tk.Label(ventana, text="Esperando acción...")
lbl_estado.pack(pady=5)

ventana.mainloop()