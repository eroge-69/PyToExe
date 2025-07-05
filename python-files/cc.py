import socket
import platform
import datetime
import requests

# Configuración
SERVER_URL = "http://localhost/registrar_encendido.php"  # Cambia esto a tu servidor real

def enviar_registro():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        nombre_pc = platform.node()
        fecha = datetime.date.today().isoformat()
        hora = datetime.datetime.now().strftime("%H:%M:%S")

        data = {
            "ip": ip,
            "nombre_pc": nombre_pc,
            "fecha": fecha,
            "hora_encendido": hora
        }
        response = requests.post(SERVER_URL, data=data)
        print(response.text)
    except Exception as e:
        with open("C:\\log_error_monitor.txt", "a") as f:
            f.write(str(e) + "\n")

if __name__ == "__main__":
    enviar_registro()
