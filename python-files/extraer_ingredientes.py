import xml.etree.ElementTree as ET
import pandas as pd
import glob
import os

# Carpeta donde están los XML
carpeta = "Y:\Path\Out"   # Cambiá por la ruta de tu carpeta

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
df.to_excel("ingredientes_mibMix.xlsx", index=False)

print("✅ Listo: ingredientes_todos.xlsx creado con", len(df), "ingredientes")
