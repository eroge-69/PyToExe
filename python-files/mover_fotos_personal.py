
import os
import shutil
import pandas as pd
from unidecode import unidecode

EXCEL_FILE = 'Lista de personal AGO25.xlsx'
BASE_DIR = r'Q:\Grupos\RT1-FOTOS-INSTITUCIONALES'
FUERA_DIR = os.path.join(BASE_DIR, 'Fuera')
EXTENSION = '.jpg'

df = pd.read_excel(EXCEL_FILE)
df['NombreCompleto'] = (df['Nombre'].astype(str) + ' ' + df['Apellidos'].astype(str)).apply(
    lambda x: unidecode(x.strip().upper()) + EXTENSION
)

nombres_validos = set(df['NombreCompleto'])
destinos = dict(zip(df['NombreCompleto'], df['COMPAÑIA']))

movidos = []
no_encontrados = []
ya_correctos = []

for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if not file.lower().endswith('.jpg'):
            continue

        nombre_normalizado = unidecode(file.strip().upper())
        ruta_actual = os.path.join(root, file)

        if nombre_normalizado in nombres_validos:
            nueva_carpeta = destinos[nombre_normalizado]
            ruta_destino = os.path.join(BASE_DIR, nueva_carpeta, file)

            if os.path.abspath(ruta_actual) != os.path.abspath(ruta_destino):
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                shutil.move(ruta_actual, ruta_destino)
                movidos.append((file, nueva_carpeta))
            else:
                ya_correctos.append(file)
        else:
            ruta_fuera = os.path.join(FUERA_DIR, file)
            os.makedirs(FUERA_DIR, exist_ok=True)
            if os.path.abspath(ruta_actual) != os.path.abspath(ruta_fuera):
                shutil.move(ruta_actual, ruta_fuera)
                movidos.append((file, 'Fuera'))

fotos_en_carpeta = {
    unidecode(f.strip().upper()) for _, _, f_list in os.walk(BASE_DIR) for f in f_list if f.lower().endswith('.jpg')
}
faltantes = nombres_validos - fotos_en_carpeta

with open("RESULTADO.txt", "w", encoding="utf-8") as f:
    f.write("✅ MOVIMIENTOS REALIZADOS:\n")
    for nombre, destino in movidos:
        f.write(f"  → {nombre} → {destino}\n")

    f.write("\n🔍 NO ENCONTRADOS (no tienen foto):\n")
    for nombre in sorted(faltantes):
        f.write(f"  ✖ {nombre}\n")

    f.write(f"\n📁 YA ESTABAN CORRECTOS: {len(ya_correctos)}\n")
    f.write("\n✅ TODO COMPLETADO.\n")
