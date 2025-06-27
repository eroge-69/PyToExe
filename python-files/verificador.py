
import os
import requests
import time
import threading
from datetime import datetime

# 🔧 CONFIGURACIÓN GLOBAL
ID_INICIAL_GLOBAL = 2148986
CANTIDAD_POR_HILO = 10         # Cuántos IDs debe revisar cada hilo
ESPERA_SEGUNDOS = 1            # Tiempo entre verificaciones

# 🗂 Crear carpeta de salida en el escritorio con la fecha de hoy
fecha_hoy = datetime.now().strftime("%Y%m%d")
escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
carpeta_base = os.path.join(escritorio, f"checkeados_{fecha_hoy}")
os.makedirs(carpeta_base, exist_ok=True)

def verificar_url(url):
    try:
        respuesta = requests.get(url, timeout=5)
        return respuesta.status_code == 200
    except requests.RequestException as e:
        print(f"⚠️ Error al verificar {url}: {e}")
        return False

def ejecutar_bot(hilo_numero, id_inicial, id_final):
    ruta_parejas = os.path.join(
        carpeta_base, f"hilo{hilo_numero}_{id_inicial}_{id_final}.txt"
    )

    url_base_back = "https://zcl3w7yytk.execute-api.us-east-1.amazonaws.com/prd/v1/JA/become/getMedia/{}/backImg"
    url_base_front = "https://zcl3w7yytk.execute-api.us-east-1.amazonaws.com/prd/v1/JA/become/getMedia/{}/frontImg"

    parejas_disponibles = []

    try:
        for i in range(id_inicial, id_final + 1):
            print(f"[Hilo {hilo_numero}] 🔍 Verificando ID {i}...")

            url_back = url_base_back.format(i)
            url_front = url_base_front.format(i)

            back_ok = verificar_url(url_back)
            front_ok = verificar_url(url_front)

            if back_ok:
                print(f"[Hilo {hilo_numero}] ✅ backImg disponible")
            else:
                print(f"[Hilo {hilo_numero}] ❌ backImg no disponible.")

            if front_ok:
                print(f"[Hilo {hilo_numero}] ✅ frontImg disponible")
            else:
                print(f"[Hilo {hilo_numero}] ❌ frontImg no disponible.")

            if back_ok and front_ok:
                parejas_disponibles.append((url_front, url_back))
                print(f"[Hilo {hilo_numero}] 💑 Pareja válida agregada.")

            time.sleep(ESPERA_SEGUNDOS)

    except Exception as e:
        print(f"[Hilo {hilo_numero}] ❌ Error: {e}")
        print(f"[Hilo {hilo_numero}] ⚠️ Guardando progreso parcial...")

    finally:
        with open(ruta_parejas, "w", encoding="utf-8") as f:
            for url_front, url_back in parejas_disponibles:
                f.write(f"{url_front}\n{url_back}\n")

        print(f"[Hilo {hilo_numero}] 📄 Guardado finalizado en: {ruta_parejas}")

# 🚀 Lanzar 4 hilos con bloques diferentes de ID
hilos = []
for n in range(4):
    bloque_inicio = ID_INICIAL_GLOBAL + (n * CANTIDAD_POR_HILO)
    bloque_final = bloque_inicio + CANTIDAD_POR_HILO - 1
    hilo = threading.Thread(target=ejecutar_bot, args=(n + 1, bloque_inicio, bloque_final))
    hilo.start()
    hilos.append(hilo)

for hilo in hilos:
    hilo.join()

print("✅ Todos los hilos han terminado.")
