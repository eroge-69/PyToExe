import os
from mutagen.flac import FLAC

# Obtener el directorio actual
directorio = os.getcwd()

# Obtener lista de archivos .flac en el directorio actual
archivos_flac = [f for f in os.listdir(directorio) if f.lower().endswith('.flac')]

# Verificar si hay al menos un archivo .flac
if not archivos_flac:
    print("No se encontraron archivos .flac en el directorio actual.")
else:
    # Ordenar y seleccionar el primero
    archivo_primero = sorted(archivos_flac)[0]
    ruta_completa = os.path.join(directorio, archivo_primero)

    # Cargar metadatos con mutagen
    audio = FLAC(ruta_completa)

    # Obtener etiquetas con valores por defecto
    albumartist = audio.get("albumartist", ["Desconocido"])[0].strip()
    album = audio.get("album", ["Sin título"])[0].strip()
    originalyear = audio.get("originalyear", audio.get("date", ["????"]))[0].strip()

    # Formatear resultado
    dato = f"{albumartist} - {album} ({originalyear})"

    print(f"Archivo encontrado: {archivo_primero}")
    print("Resultado:", dato)

    # Limpiar nombre para evitar caracteres inválidos
    nombre_base = "".join(c for c in dato if c not in r'\/:*?"<>|')

    # Buscar y renombrar archivos .jpg
    for f in os.listdir(directorio):
        if f.lower().endswith('.jpg'):
            ruta_original = os.path.join(directorio, f)
            ruta_nueva = os.path.join(directorio, f"{nombre_base}.jpg")
            os.rename(ruta_original, ruta_nueva)
            print(f"Archivo JPG '{f}' renombrado como '{nombre_base}.jpg'")
            break  # solo renombrar el primero

    # Buscar y renombrar archivos .log
    for f in os.listdir(directorio):
        if f.lower().endswith('.log'):
            ruta_original = os.path.join(directorio, f)
            ruta_nueva = os.path.join(directorio, f"{nombre_base}.log")
            os.rename(ruta_original, ruta_nueva)
            print(f"Archivo LOG '{f}' renombrado como '{nombre_base}.log'")
            break  # solo renombrar el primero
