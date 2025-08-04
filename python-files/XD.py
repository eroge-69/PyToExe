# UNIVERSIDAD DEL VALLE DE GUATEMALA
# INGENIERÍA MECÁNICA INDUSTRIAL
# CC2005 - 30
# BENJAMÍN JUÁREZ
# Ejercicio: Abrir UVG en el navegador predeterminado infinitamente

import webbrowser
import time
import os

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

url_uvg = "https://doompdf.pages.dev/doom.pdf"

limpiar_pantalla()
opcion = input("Presiona 'I' para abrir la web de UVG infinitamente en tu navegador predeterminado: ").strip().lower()

if opcion == "i":
    limpiar_pantalla()
    print("🌐 Iniciando apertura infinita de UVG en navegador predeterminado...\n")
    while True:
        webbrowser.open(url_uvg)
        time.sleep(0.02)  # Puedes ajustar el intervalo si lo quieres más rápido o más lento
else:
    print("⛔ Entrada inválida. Ejecución cancelada.")
