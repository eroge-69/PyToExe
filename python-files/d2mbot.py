import configparser
import time
import requests
import re
import os
import sys
import traceback
import ctypes

# Leer configuración desde d2mbot.ini
def cargar_configuracion(config_path="d2mbot.ini"):
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return {
        "discord_webhook": config.get("SETTINGS", "discord"),
        "message_template_game": config.get("SETTINGS", "messagecreate"),
        "message_template_player": config.get("SETTINGS", "messageplayer"),
        "message_template_leave": config.get("SETTINGS", "messagetoleave"),
        "message_template_connect": config.get("SETTINGS", "messagetoconnect"),
        "bot_console": config.getint("SETTINGS", "bot_console", fallback=0),
        "titulo": config.get("SETTINGS", "Nombre", fallback="Monitoreo Log")
    }

# Establecer título de la ventana CMD
def configurar_titulo(titulo):
    ctypes.windll.kernel32.SetConsoleTitleW(titulo)

# Redirigir la salida de la consola a un archivo si está activado en d2mbot.ini
def configurar_registro_consola():
    if config["bot_console"] == 1:
        log_file = "bot_console.log"
        sys.stdout = open(log_file, "a")  # Modo append para no sobrescribir
        sys.stderr = sys.stdout
        print("Registro de la consola activado. Guardando en 'bot_console.log'")

# Enviar mensaje al webhook de Discord
def enviar_webhook(webhook_url, mensaje):
    try:
        response = requests.post(webhook_url, json={"content": mensaje})
        if response.status_code != 204:
            print(f"Error al enviar al webhook: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error al enviar el mensaje al webhook: {e}")
        traceback.print_exc()

# Verificar si el archivo de log existe antes de iniciar
def verificar_log_existe(ruta_log):
    if not os.path.exists(ruta_log):
        print(f"Error: El archivo de log '{ruta_log}' no existe. Verifique la configuración.")
        input("Presione Enter para salir...")
        exit(1)

# Leer el archivo log de manera continua
def monitorear_log(ruta_log, config):
    try:
        with open(ruta_log, "r") as archivo:
            archivo.seek(0, 2)  # Ir al final del archivo
            while True:
                try:
                    linea = archivo.readline()
                    if not linea:
                        time.sleep(0.1)
                        continue
                    procesar_linea(linea, config)
                except Exception as e:
                    print(f"Error al leer línea del log: {e}")
                    traceback.print_exc()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_log}")
        input("Presione Enter para salir...")
    except Exception as e:
        print(f"Error al monitorear el log: {e}")
        traceback.print_exc()
        input("Presione Enter para salir...")

# Procesar cada línea del log
def procesar_linea(linea, config):
    try:
        match_game = re.search(r"creating game \[(.*)\]", linea)
        if match_game:
            nombre_partida = match_game.group(1)
            mensaje = config["message_template_game"].replace("{game_name}", nombre_partida)
            enviar_webhook(config["discord_webhook"], mensaje)

        match_player = re.search(r"player \[(.*)\|(.+?)\] joined the game", linea)
        if match_player:
            usuario = match_player.group(1)
            ip = match_player.group(2)
            mensaje = config["message_template_player"].replace("{user}", usuario).replace("{ip}", ip)
            enviar_webhook(config["discord_webhook"], mensaje)

        match_leave = re.search(r"deleting player \[(.*)\]:", linea)
        if match_leave:
            usuario = match_leave.group(1)
            mensaje = config["message_template_leave"].replace("{user}", usuario)
            enviar_webhook(config["discord_webhook"], mensaje)

        match_chat = re.search(r"\[Lobby\] (.+)", linea)
        if match_chat:
            mensaje_chat = match_chat.group(0)
            enviar_webhook(config["discord_webhook"], mensaje_chat)

        match_connect = re.search(r"connecting to server \[(.*?)\]", linea)
        if match_connect:
            servidor = match_connect.group(1)
            mensaje = config["message_template_connect"].replace("{SERVIDOR}", servidor)
            enviar_webhook(config["discord_webhook"], mensaje)
    except Exception as e:
        print(f"Error procesando línea del log: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    ruta_log = "Z:/Servidores/acc.d2fbot/logs/d2mbot.log"
    config_path = "d2mbot.ini"

    config = cargar_configuracion(config_path)
    configurar_titulo(config["titulo"])  # Configurar el título de la ventana CMD
    print("Iniciando bot de monitoreo...")
    verificar_log_existe(ruta_log)
    configurar_registro_consola()
    print("Iniciando monitoreo del log...")
    monitorear_log(ruta_log, config)
    input("Presione Enter para salir...")
