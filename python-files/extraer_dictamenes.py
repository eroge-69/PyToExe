import os
import re
import pandas as pd
import fitz  # PyMuPDF

# === Ruta de la carpeta de dictámenes en el escritorio ===
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
carpeta_dictamenes = os.path.join(desktop, "Dictamenes 2025")

# === Lista para guardar los datos extraídos ===
datos = []

# === Expresiones regulares para buscar cada campo ===
patrones = {
    "modelo": re.compile(r"modelo\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "numero_serie": re.compile(r"n[úu]mero\s+de\s+serie\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "numero_inventario": re.compile(r"n[úu]mero\s+de\s+inventario\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "conclusion": re.compile(r"(conclusi[oó]n|recomendaci[oó]n)\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "nota": re.compile(r"nota\s*[:\-]?\s*(.+)", re.IGNORECASE)
}

# === Recorrer cada PDF en la carpeta ===
for archivo in os.listdir(carpeta_dictamenes):
    if archivo.lower().endswith(".pdf"):
        ruta_pdf = os.path.join(carpeta_dictamenes, archivo)

        # Abrir PDF y extraer texto
        texto = ""
        with fitz.open(ruta_pdf) as doc:
            for pagina in doc:
                texto += pagina.get_text()

        # Diccionario para los datos del archivo actual
        fila = {
            "modelo": "",
            "numero_serie": "",
            "numero_inventario": "",
            "conclusion_recomendacion": "",
            "nota": ""
        }

        # Buscar cada campo
        for campo, patron in patrones.items():
            match = patron.search(texto)
            if match:
                # Si el patrón tiene más de un grupo, tomamos el último
                fila[campo if campo != "conclusion" else "conclusion_recomendacion"] = match.groups()[-1].strip()

        datos.append(fila)

# === Crear DataFrame y guardar en Excel ===
df = pd.DataFrame(datos)
ruta_excel = os.path.join(desktop, "info_dictamenes.xlsx")
df.to_excel(ruta_excel, index=False)

print(f"Archivo generado en: {ruta_excel}")
input("Presiona Enter para salir...")
