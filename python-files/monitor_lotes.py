
import os
import shutil
import time

base_dir = r"C:\Users\mmarinp\Desktop\Lotes"
avisos_dir = os.path.join(base_dir, "Lotes con Aviso")
scar_dir = os.path.join(base_dir, "Lotes con SCAR")

os.makedirs(avisos_dir, exist_ok=True)
os.makedirs(scar_dir, exist_ok=True)

def detectar_proveedor(archivo_aviso):
    try:
        with open(archivo_aviso, 'r', encoding='utf-8') as f:
            for linea in f:
                if "Proveedor" in linea:
                    return linea.split("Proveedor")[1].strip(": ").strip()
    except Exception as e:
        print(f"Error leyendo aviso: {e}")
    return "Desconocido"

def procesar_carpeta(carpeta):
    carpeta_path = os.path.join(base_dir, carpeta)
    archivos = os.listdir(carpeta_path)

    for archivo in archivos:
        archivo_path = os.path.join(carpeta_path, archivo)

        if archivo.lower().startswith("aviso"):
            proveedor = detectar_proveedor(archivo_path)
            destino_proveedor = os.path.join(avisos_dir, proveedor)
            os.makedirs(destino_proveedor, exist_ok=True)
            shutil.move(carpeta_path, os.path.join(destino_proveedor, carpeta))
            print(f"Movido {carpeta} a {destino_proveedor}")
            return

        elif archivo.lower() == "scar":
            shutil.move(carpeta_path, os.path.join(scar_dir, carpeta))
            print(f"Movido {carpeta} a {scar_dir}")
            return

def monitorear():
    print("Monitoreando carpeta 'Lotes'...")
    while True:
        try:
            carpetas = [f for f in os.listdir(base_dir) if f.startswith("IN-") and os.path.isdir(os.path.join(base_dir, f))]
            for carpeta in carpetas:
                procesar_carpeta(carpeta)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    monitorear()
