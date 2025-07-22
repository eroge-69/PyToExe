
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import fitz  # PyMuPDF
import re

EXCEL_FILENAME = "datos_docentes.xlsx"

COLUMNAS = [
    "Nro de expediente", "Nro. Doc", "Apellido", "Nombre", "Número de solicitud",
    "cargo 1", "porcentaje 1", "repartición 1", "Descripción del cargo 1",
    "cargo 2", "porcentaje 2", "repartición 2", "Descripción del cargo 2",
    "cargo 3", "porcentaje 3", "repartición 3", "Descripción del cargo 3",
    "antigüedad"
]

def extraer_datos_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texto = ""
    for page in doc:
        texto += page.get_text()

    texto = ' '.join(texto.split())  # limpiar espacios

    datos = {col: "" for col in COLUMNAS}

    # Expediente
    expediente = re.search(r'Expediente:\s*(\S+)', texto)
    if not expediente:
        expediente = re.search(r'Nro\. de Expediente:\s*(\S+)', texto)
    datos["Nro de expediente"] = expediente.group(1) if expediente else ""

    # DNI
    dni = re.search(r'Nro\. Doc:\s*(\d+)', texto)
    datos["Nro. Doc"] = dni.group(1) if dni else ""

    # Apellido y Nombre
    apellido = re.search(r'Apellido:\s*([A-ZÁÉÍÓÚÑ]+)', texto)
    nombre = re.search(r'Nombre:\s*([A-ZÁÉÍÓÚÑ ]+)', texto)
    datos["Apellido"] = apellido.group(1).title() if apellido else ""
    datos["Nombre"] = nombre.group(1).title() if nombre else ""

    # Solicitud
    solicitud = re.search(r'Nro de Solicitud:\s*(\d+)', texto)
    if not solicitud:
        solicitud = re.search(r'Número:\s*(\d+)\s*Tipo:', texto)
    datos["Número de solicitud"] = solicitud.group(1) if solicitud else ""

    # Cargo 1
    tipo_cargo = re.search(r'TIPO DE CARGO:\s*([A-Z ]+)', texto)
    datos["cargo 1"] = tipo_cargo.group(1).strip().title() if tipo_cargo else ""

    porcentaje = re.search(r'PORCENTAJE:\s*(\d+)', texto)
    datos["porcentaje 1"] = porcentaje.group(1) if porcentaje else ""

    reparticion = re.search(r'Repartición:\s*([A-Z ]+)', texto)
    datos["repartición 1"] = reparticion.group(1).strip().title() if reparticion else ""

    descripcion = re.search(r'Descripción del Cargo:\s*(.+?)\s*-', texto)
    datos["Descripción del cargo 1"] = descripcion.group(1).strip().title() if descripcion else ""

    # Antigüedad
    antig = re.search(r'Antiguedad:\s*([\d\-]+)', texto)
    datos["antigüedad"] = antig.group(1) if antig else ""

    return datos

def guardar_en_excel(datos_dict):
    nuevo_dato = pd.DataFrame([datos_dict])
    if os.path.exists(EXCEL_FILENAME):
        df_existente = pd.read_excel(EXCEL_FILENAME)
        df_actualizado = pd.concat([df_existente, nuevo_dato], ignore_index=True)
    else:
        df_actualizado = nuevo_dato
    df_actualizado.to_excel(EXCEL_FILENAME, index=False)
    messagebox.showinfo("Éxito", f"Datos cargados en '{EXCEL_FILENAME}'.")

def cargar_pdf():
    pdf_path = filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("Archivos PDF", "*.pdf")])
    if not pdf_path:
        return
    try:
        datos = extraer_datos_pdf(pdf_path)
        guardar_en_excel(datos)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

ventana = tk.Tk()
ventana.title("Cargar planilla de docentes")

btn_cargar = tk.Button(ventana, text="Cargar en Excel (datos_docentes.xlsx)", command=cargar_pdf, padx=20, pady=10, bg="#4CAF50", fg="white")
btn_cargar.pack(pady=30)

ventana.mainloop()
