import os
import shutil
import pandas as pd
import re

# ========================
# CONFIGURACIÓN (EDITAR)
# ========================
ruta_excel = r"C:\Users\g_credenciales\OneDrive - Entel\Escritorio\Fotos starlink.xlsx"        # 📌 tu archivo Excel con la lista de RUTs
columna_rut = "Rut"                      # 📌 nombre de la columna en el Excel donde están los RUTs
carpeta_imagenes = r"C:\Users\g_credenciales\OneDrive - Entel\Respaldo 21-08-24\Fotos Credenciales"   # 📌 carpeta donde están tus imágenes
carpeta_destino = r"C:\Users\g_credenciales\OneDrive - Entel\Escritorio\STARLINK" # 📌 carpeta donde copiar las imágenes
salida = r"C:\Users\g_credenciales\OneDrive - Entel\Escritorio\RESULTADOS.xlsx" # 📌 Excel de salida con el resultado

# ========================
# FUNCIONES
# ========================
def normalizar_rut(rut: str) -> str:
    rut = rut.upper().strip()
    rut = rut.replace(".", "").replace("-", "")
    # eliminar DV si es número o K
    return rut[:-1] if rut[-1].isdigit() or rut[-1] == "K" else rut

def normalizar_texto(texto: str) -> str:
    return re.sub(r"[^0-9]", "", texto)  # dejar solo números

# ========================
# PROCESO
# ========================
print("📂 Leyendo Excel:", ruta_excel)
df = pd.read_excel(ruta_excel)
df["Encontrado"] = False
df["Archivo Copiado"] = ""

# Normalizar RUTs de Excel
df["RUT_Normalizado"] = df[columna_rut].astype(str).apply(normalizar_rut)

# Crear carpeta destino si no existe
os.makedirs(carpeta_destino, exist_ok=True)

print("🔎 Buscando imágenes en:", carpeta_imagenes)
for i, rut_norm in enumerate(df["RUT_Normalizado"]):
    for root, dirs, files in os.walk(carpeta_imagenes):
        for file in files:
            file_norm = normalizar_texto(file)
            if rut_norm in file_norm:  # coincidencia tolerante
                origen = os.path.join(root, file)
                destino = os.path.join(carpeta_destino, file)
                shutil.copy2(origen, destino)
                df.at[i, "Encontrado"] = True
                df.at[i, "Archivo Copiado"] = file
                print(f"✅ Encontrado {df.at[i, columna_rut]} -> {file}")
                break
        if df.at[i, "Encontrado"]:
            break

# Guardar resultados en Excel
df.to_excel(salida, index=False)
print("\n🎉 Proceso terminado.")
print("📑 Resultados guardados en:", salida)
print("🖼️ Imágenes copiadas en:", carpeta_destino)
input("\nPresiona ENTER para salir...")
