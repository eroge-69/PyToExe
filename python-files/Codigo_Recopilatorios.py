import os
import pandas as pd
import shutil
from pathlib import Path
import tkinter as tk
import datetime
from tkinter import filedialog, messagebox

def crear_directorio_playlist(ruta_archivo_playlist):
    """Crea el directorio con el mismo nombre del archivo playlist en su misma ubicación"""
    ruta_archivo = Path(ruta_archivo_playlist)
    nombre_sin_extension = ruta_archivo.stem
    directorio_padre = ruta_archivo.parent
    directorio_destino = directorio_padre / nombre_sin_extension

    directorio_destino.mkdir(parents=True, exist_ok=True)
    print(f"Directorio creado: {directorio_destino}")
    return directorio_destino

def seleccionar_archivo_canciones():
    """Abre un cuadro de diálogo para seleccionar el archivo con la lista de canciones"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal

    archivo_canciones = filedialog.askopenfilename(
        title="Selecciona el archivo con la lista de reproducción",
        filetypes=[
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Archivos CSV", "*.csv"),
            ("Todos los archivos", "*.*")
        ]
    )

    root.destroy()
    return archivo_canciones

def leer_tabla_canciones(ruta_archivo):
    """Lee la tabla de canciones desde un archivo CSV o Excel"""
    try:
        if ruta_archivo.lower().endswith('.csv'):
            df = pd.read_csv(ruta_archivo)
            print(f"Archivo CSV cargado exitosamente: {ruta_archivo}")
        else:
            df = pd.read_excel(ruta_archivo)
            print(f"Archivo Excel cargado exitosamente: {ruta_archivo}")

            # Forzar columna Duración a formato texto mm:ss
        if 'Duración' in df.columns: df['Duración'] = df['Duración'].apply(formatear_duracion_texto)

        # Verificar que el archivo tiene las columnas necesarias (estructura completa)
        columnas_requeridas = ['#', 'Artista', 'Canción', 'Género', 'Año', 'Duración']
        columnas_faltantes = []

        for col in columnas_requeridas:
            if col not in df.columns:
                # Intentar buscar variaciones comunes de nombres de columnas
                variaciones = {
                    '#': ['numero', 'Numero', 'No', 'N'],
                    'Artista': ['Artist', 'artista', 'ARTISTA', 'NOMBRE'],
                    'Canción': ['Cancion', 'Song', 'cancion', 'CANCION', 'Título', 'Titulo'],
                    'Género': ['Genero', 'Genre', 'genero', 'GENERO', 'GÉNERO'],
                    'Año': ['Year', 'año', 'AÑO', 'Anno'],
                    'Duración': ['Duracion', 'Duration', 'duracion', 'DURACION', 'Tiempo']
                }

                encontrada = False
                if col in variaciones:
                    for variacion in variaciones[col]:
                        if variacion in df.columns:
                            df = df.rename(columns={variacion: col})
                            encontrada = True
                            break

                if not encontrada:
                    columnas_faltantes.append(col)

        if columnas_faltantes:
            raise ValueError(f"Faltan las siguientes columnas: {', '.join(columnas_faltantes)}")

        print(f"Tabla cargada correctamente. Canciones encontradas: {len(df)}")
        print(f"Columnas: {list(df.columns)}")

        return df

    except Exception as e:
        print(f"Error al leer el archivo de canciones: {e}")
        messagebox.showerror("Error", f"Error al leer el archivo de canciones:\n{e}")
        return None

def leer_excel_musica(ruta_excel):
    """Lee el archivo Excel con la base de datos de música"""
    try:
        df = pd.read_excel(ruta_excel)
        if 'Duración' in df.columns: df['Duración'] = df['Duración'].apply(formatear_duracion_texto)
        print(f"Base de datos cargada exitosamente. Filas: {len(df)}")
        print(f"Columnas en base de datos: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        messagebox.showerror("Error", f"Error al leer el archivo Excel:\n{e}")
        return None

def normalizar_texto(texto):
    """Normaliza texto para comparación exacta (elimina espacios extra, convierte a minúsculas)"""
    return str(texto).strip().lower()

def normalizar_duracion(duracion_str):
    """Normaliza duración para comparación exacta"""
    duracion_str = str(duracion_str).strip()

    # Si ya está en formato MM:SS, mantenerlo
    if ':' in duracion_str:
        partes = duracion_str.split(':')
        if len(partes) == 2:
            try:
                minutos = int(partes[0])
                segundos = int(partes[1])
                return f"{minutos}:{segundos:02d}"
            except:
                pass
    duracion_str = str(duracion_str).strip()
    return formatear_duracion_texto(duracion_str)

def formatear_duracion_texto(valor):
    """
    Convierte un valor de duración a texto formato m:ss igual que en la base de datos.
    - Interpreta correctamente los valores Excel datetime.time de playlist como m:ss,
      trasladando la hora a minutos (sin sumar como horas).
    """
    import datetime
    import pandas as pd

    if pd.isna(valor):
        return "0:00"

    if isinstance(valor, datetime.time):
        minutos = valor.hour  # Aquí tratamos la hora como minutos
        segundos = valor.minute  # Y los minutos como segundos
        # Pero en tus datos de duración real, los minutos deben estar en valor.hour y segundos en valor.minute
        # Como tus ejemplos indican "03:27:00" es 3 minutos 27 segundos, entonces:
        # corregimos la asignación como:
        minutos = valor.hour
        segundos = valor.minute
        return f"{minutos}:{segundos:02d}"

    elif isinstance(valor, datetime.timedelta):
        total_segundos = int(valor.total_seconds())
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        return f"{minutos}:{segundos:02d}"

    elif isinstance(valor, (int, float)):
        if 0 < valor < 1:
            total_segundos = int(round(valor * 24 * 3600))
        else:
            total_segundos = int(valor)
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        return f"{minutos}:{segundos:02d}"

    else:
        try:
            partes = str(valor).strip().split(":")
            if len(partes) == 3:
                # Aquí también interpretamos solo minutos y segundos ignorando horas porque la base no tiene horas
                minutos = int(partes[0])
                segundos = int(partes[1])
                # O ajusta según si la base tiene solo mm:ss y la playlist aporta hh:mm:ss con horas a ignorar
                # Asumiendo parte[0]=minutos, parte[1]=segundos y parte[2]=always 0
                return f"{minutos}:{segundos:02d}"
            elif len(partes) == 2:
                minutos = int(partes[0])
                segundos = int(partes[1])
                return f"{minutos}:{segundos:02d}"
            else:
                return str(valor)
        except Exception:
            return str(valor)

def buscar_coincidencias_exactas(df_excel, artista, cancion, duracion):
    """
    Busca coincidencias EXACTAS (100%) en la base de datos
    - Columna A (índice 0): NOMBRE vs Artista
    - Columna B (índice 1): CANCION vs Canción
    - Columna F (índice 5): DURACION vs Duración
    """

    # Normalizar valores de búsqueda
    artista_norm = normalizar_texto(artista)
    cancion_norm = normalizar_texto(cancion)
    duracion_norm = normalizar_duracion(duracion)

    print(f"Buscando: Artista='{artista_norm}', Canción='{cancion_norm}', Duración='{duracion_norm}'")

    # Buscar coincidencias exactas
    coincidencias = []
    for idx, row in df_excel.iterrows():
        nombre_bd = normalizar_texto(row.iloc[0])    # Columna A: NOMBRE
        cancion_bd = normalizar_texto(row.iloc[1])   # Columna B: CANCION
        duracion_bd = normalizar_duracion(row.iloc[5])  # Columna F: DURACION

        if (artista_norm == nombre_bd and
            cancion_norm == cancion_bd and
            duracion_norm == duracion_bd):
            coincidencias.append(row)
            print(f"✓ Coincidencia exacta encontrada: {row.iloc[0]} - {row.iloc[1]}")

    if len(coincidencias) == 0:
        print(f"✗ No se encontró coincidencia exacta")
        return None
    elif len(coincidencias) == 1:
        return coincidencias[0]
    else:
        print(f"⚠ Se encontraron {len(coincidencias)} coincidencias exactas, usando la primera")
        return coincidencias[0]

def copiar_y_renombrar_archivo(ruta_origen, directorio_destino, numero, artista, cancion):
    """Copia el archivo al directorio destino y lo renombra según el patrón"""
    try:
        ruta_origen = Path(ruta_origen)
        if not ruta_origen.exists():
            print(f"Archivo no encontrado: {ruta_origen}")
            return False

        # Obtener extensión del archivo original
        extension = ruta_origen.suffix

        # Crear nombre nuevo según patrón: #. Artista - Canción
        nombre_nuevo = f"{numero}. {artista} - {cancion}{extension}"
        # Limpiar caracteres no válidos para nombres de archivo
        caracteres_invalidos = '<>:"/\\|?*'
        for char in caracteres_invalidos:
            nombre_nuevo = nombre_nuevo.replace(char, '_')

        ruta_destino = directorio_destino / nombre_nuevo

        # Copiar archivo
        shutil.copy2(ruta_origen, ruta_destino)
        print(f"✓ Archivo copiado: {nombre_nuevo}")
        return True

    except Exception as e:
        print(f"✗ Error al copiar archivo: {e}")
        return False

def procesar_lista_reproduccion(ruta_excel):
    """Función principal que procesa la lista de reproducción"""

    print("=== CREADOR DE LISTAS DE REPRODUCCIÓN ===")
    print(f"Base de datos musical: {ruta_excel}")

    # Verificar que el archivo Excel de base de datos existe
    if not os.path.exists(ruta_excel):
        error_msg = f"No se encontró el archivo de base de datos en: {ruta_excel}"
        print(f"ERROR: {error_msg}")
        messagebox.showerror("Error", error_msg)
        return

    # Seleccionar archivo con lista de reproducción
    print("\n1. Seleccionando archivo con lista de reproducción...")
    archivo_playlist = seleccionar_archivo_canciones()

    if not archivo_playlist:
        print("No se seleccionó archivo de playlist. Operación cancelada.")
        return

    # Leer tabla de canciones
    df_playlist = leer_tabla_canciones(archivo_playlist)
    if df_playlist is None:
        return

    # Leer Excel con base de datos
    print(f"\n2. Cargando base de datos musical: {ruta_excel}")
    df_excel = leer_excel_musica(ruta_excel)
    if df_excel is None:
        return

    # Crear directorio destino con el nombre del archivo playlist
    print(f"\n3. Creando directorio destino...")
    directorio_destino = crear_directorio_playlist(archivo_playlist)

    # Contadores
    procesadas = 0
    exitosas = 0
    no_encontradas = []

    # Procesar cada canción de la playlist
    print(f"\n4. Procesando canciones...")
    for idx, row in df_playlist.iterrows():
        numero = row['#']
        artista = row['Artista']
        cancion = row['Canción']
        duracion = str(row['Duración'])

        print(f"\n--- Procesando #{numero}: {artista} - {cancion} ---")

        # Buscar coincidencia exacta en la base de datos
        coincidencia = buscar_coincidencias_exactas(df_excel, artista, cancion, duracion)

        if coincidencia is not None:
            # Obtener ruta del archivo (Columna G - índice 6: RUTA_ARCHIVO)
            ruta_archivo = coincidencia.iloc[6] if len(coincidencia) > 6 else None

            if ruta_archivo and pd.notna(ruta_archivo):
                # Copiar y renombrar archivo
                exito = copiar_y_renombrar_archivo(
                    ruta_archivo,
                    directorio_destino,
                    numero,
                    artista,
                    cancion
                )
                if exito:
                    exitosas += 1
            else:
                print(f"✗ Ruta de archivo no encontrada en columna RUTA_ARCHIVO")
                no_encontradas.append(f"#{numero} {artista} - {cancion} (Sin ruta)")
        else:
            print(f"✗ No se encontró coincidencia exacta en la base de datos")
            no_encontradas.append(f"#{numero} {artista} - {cancion}")

        procesadas += 1

    # Mostrar resumen
    print(f"\n=== RESUMEN ===")
    print(f"Canciones procesadas: {procesadas}")
    print(f"Archivos copiados exitosamente: {exitosas}")
    print(f"Canciones no encontradas: {len(no_encontradas)}")
    print(f"Directorio destino: {directorio_destino}")

    if no_encontradas:
        print(f"\nCanciones no encontradas:")
        for cancion in no_encontradas:
            print(f"  - {cancion}")

    # Mostrar mensaje final
    mensaje_final = f"Proceso completado:\n"
    mensaje_final += f"• Canciones procesadas: {procesadas}\n"
    mensaje_final += f"• Archivos copiados: {exitosas}\n"
    mensaje_final += f"• No encontradas: {len(no_encontradas)}\n"
    mensaje_final += f"• Directorio: {directorio_destino}"

    messagebox.showinfo("Proceso Completado", mensaje_final)

# Función principal para ejecutar el programa
def main():
    """Función principal - Ejecuta el procesamiento con la base de datos predefinida"""

    # CONFIGURACIÓN: Ruta fija de la base de datos musical
    RUTA_EXCEL = r"C:\MP3 ALFABETICO\Listado_MP3.xlsx"

    try:
        # Ejecutar procesamiento
        procesar_lista_reproduccion(RUTA_EXCEL)

    except Exception as e:
        error_msg = f"Error durante la ejecución: {str(e)}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    main()