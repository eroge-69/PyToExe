import os
import shutil
import psutil
import time

# Ruta local del archivo que se quiere reemplazar
ruta_local = r"C:\JARBSALUD\HistoriaEstacion.accdb"

# Ruta de red compartida donde está el archivo actualizado
ruta_compartida = r"\\192.168.0.242\compartida\HistoriaEstacion.accdb"

def cerrar_programa_abierto(nombre_archivo):
    """Busca procesos que usen el archivo y los cierra"""
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            archivos_abiertos = proc.info['open_files']
            if archivos_abiertos:
                for archivo in archivos_abiertos:
                    if nombre_archivo.lower() in archivo.path.lower():
                        print(f"Cerrando proceso {proc.pid} ({proc.name()}) que tiene abierto el archivo...")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def reemplazar_archivo(origen, destino):
    """Copia el archivo desde la red y reemplaza el existente"""
    if not os.path.exists(origen):
        print(f"El archivo de origen no existe: {origen}")
        return False
    try:
        # Borra el archivo destino si existe
        if os.path.exists(destino):
            os.remove(destino)
        # Copia el nuevo archivo
        shutil.copy2(origen, destino)
        print("Archivo reemplazado con éxito.")
        return True
    except Exception as e:
        print(f"Error al copiar el archivo: {e}")
        return False

def main():
    print("Buscando procesos que usen el archivo...")
    cerrado = cerrar_programa_abierto("HistoriaEstacion.accdb")
    if cerrado:
        print("Proceso cerrado correctamente.")
    else:
        print("No se encontró un proceso que tuviera el archivo abierto o ya estaba cerrado.")

    print("Esperando un momento antes de reemplazar...")
    time.sleep(2)

    print("Reemplazando el archivo...")
    reemplazar_archivo(ruta_compartida, ruta_local)

if __name__ == "__main__":
    main()
