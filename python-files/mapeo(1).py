import csv
import os
from datetime import datetime
from pynput import keyboard

# Archivo CSV donde se almacenan los eventos
CSV_FILE = "eventos_flota.csv"

# Mapear teclas a eventos
TECLA_EVENTO = {
    keyboard.Key.f8: "Reclamo de clientes",
    keyboard.Key.f9: "Descarga de pagos",
    keyboard.Key.f10: "Pagos",
    keyboard.Key.f12: "Whatsapp"
}

# Inicializar archivo CSV si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Evento"])

# Función para registrar evento
def registrar_evento(evento):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, evento])
    print(f"[{timestamp}] Evento registrado: {evento}")

# Función que se llama al presionar una tecla
def on_press(key):
    if key in TECLA_EVENTO:
        evento = TECLA_EVENTO[key]
        registrar_evento(evento)

# Escuchar el teclado en segundo plano
def ejecutar_en_segundo_plano():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    print("""Escuchando teclas...
    
    F8: Relcamo de clientes
    F9: Descarga de Pagos
    F10: Pagos
    F12: Whatsapp
    
    Ejecutando en segundo plano.""")
    ejecutar_en_segundo_plano()