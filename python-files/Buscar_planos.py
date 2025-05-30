import os
import shutil
import re

# === CONFIGURACIÓN FIJA ===
carpetas_origen = [
    r'J:\Planos\A1',
    r'J:\Planos\A2',
    r'J:\Planos\A3',
    r'J:\Planos\A4'
]

# === CREAR CARPETA DE DESTINO EN EL ESCRITORIO ===
base_nombre = 'PLANOS A IMPRIMIR'
escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
carpeta_destino = os.path.join(escritorio, base_nombre)

contador = 1
while os.path.exists(carpeta_destino):
    carpeta_destino = os.path.join(escritorio, f"{base_nombre}_{contador:02d}")
    contador += 1

os.makedirs(carpeta_destino)

# === INGRESO DE PLANOS POR CONSOLA ===
print("📝 Escribe o pega los nombres de los planos (uno por línea, con o sin punto, sin extensión).")
print("   Cuando termines, deja una línea vacía y presiona Enter.")

nombres_planos = []
while True:
    linea = input()
    if linea.strip() == "":
        break
    # ⚠️ Eliminar puntos al guardar el nombre
    nombres_planos.append(linea.strip().replace('.', ''))

# === FUNCIÓN PARA BUSCAR ARCHIVO POR NOMBRE BASE (sin punto) ===
def buscar_archivo(nombre_sin_punto):
    for carpeta in carpetas_origen:
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(".dwg"):
                nombre_archivo = os.path.splitext(archivo)[0].replace('.', '')
                if nombre_archivo == nombre_sin_punto:
                    return os.path.join(carpeta, archivo)
    return None

# === BÚSQUEDA Y COPIA ===
print("\n🔍 Buscando planos y revisiones...\n")

for nombre_plano in nombres_planos:
    match_base = re.match(r"^(\d{6})", nombre_plano)
    if not match_base:
        print(f"❌ Formato inválido: {nombre_plano}")
        continue

    base = match_base.group(1)
    revisiones_encontradas = []

    # Paso 1: Buscar archivo base sin revisión
    archivo_base = f"{base}"
    ruta_encontrada = buscar_archivo(archivo_base)
    if ruta_encontrada:
        revisiones_encontradas.append((0, ruta_encontrada))

    # Paso 2: Buscar revisiones -01, -02, ...
    for i in range(1, 100):  # hasta -99
        nombre_revision = f"{base}-{i:02d}"
        ruta_revision = buscar_archivo(nombre_revision)
        if ruta_revision:
            revisiones_encontradas.append((i, ruta_revision))
        else:
            break

    if revisiones_encontradas:
        rev_max, ruta_final = revisiones_encontradas[-1]
        shutil.copy2(ruta_final, carpeta_destino)
        rev_txt = f"-{rev_max:02d}" if rev_max > 0 else "(sin revisión)"
        print(f"✅ {base} → Copiado: revisión {rev_txt}")
    else:
        print(f"❌ NO ENCONTRADO: {base}")

print(f"\n📁 Los planos encontrados fueron copiados a: {carpeta_destino}")
input("\nPresiona Enter para salir...")

