import xml.etree.ElementTree as ET
import pandas as pd
import glob
import os
import tkinter as tk
from tkinter import filedialog

# Ocultar la ventana principal de Tkinter
root = tk.Tk()
root.withdraw()

# Pedir al usuario la carpeta donde están los XML
carpeta = filedialog.askdirectory(title="Selecciona la carpeta con archivos .CprSave")

if not carpeta:
    print("❌ No se seleccionó ninguna carpeta. Saliendo...")
    exit()

# Lista para acumular todos los ingredientes
todos_ingredientes = []

# Buscar todos los archivos XML en la carpeta
for archivo in glob.glob(os.path.join(carpeta, "*.CprSave")):
    tree = ET.parse(archivo)
    root = tree.getroot()

    # Extraer nombre del archivo (por si querés identificarlo después)
    nombre_archivo = os.path.basename(archivo)

    # Recorrer todos los <Ingredient>
    for ing in root.findall(".//Ingredient"):
        todos_ingredientes.append({
            "Archivo": nombre_archivo,
            "JobID": ing.findtext("JobID"),
            "IngredID": ing.findtext("IngredID"),
            "IngredName": ing.findtext("IngredName"),
            "Volume": ing.findtext("Volume"),
            "Density": ing.findtext("Density"),
            "Weight": ing.findtext("Weight"),
            "CprChannel": ing.findtext("CprChannel"),
            "CprSequence": ing.findtext("CprSequence"),
            "SpeedLevel": ing.findtext("SpeedLevel")
        })

# Convertir a DataFrame y exportar a Excel
df = pd.DataFrame(todos_ingredientes)
salida = os.path.join(carpeta, "ingredientes_mibMix.xlsx")
df.to_excel(salida, index=False)

print(f"✅ Listo: {salida} creado con {len(df)} ingredientes")
