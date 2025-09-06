import os
import psutil
import telepot
import time
import re

# === CONFIGURACIÓN VANILLE === #
BOT_TOKEN = '8052110332:AAHS92lxBknRh9mI95Z5mp_LvEwrsCz3ZdY'
OWNER_ID = 7694834936
CHECK_INTERVAL = 30  # segundos
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos entre intentos

# === INICIALIZACIÓN === #
bot = telepot.Bot(BOT_TOKEN)
alertado_ips = set()
alertado_proc = set()

def enviar_alerta(mensaje):
    for intento in range(1, MAX_RETRIES + 1):
        try:
            bot.sendMessage(OWNER_ID, f"⚠️ *CENTINELA*: {mensaje}", parse_mode='Markdown')
            print(f"[+] Alerta enviada: {mensaje}")
            return
        except Exception as e:
            print(f"[!] Error al enviar alerta (intento {intento}): {e}")
            if intento < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print("[!] Falló el envío después de varios intentos.")

def revisar_procesos():
    procesos_sospechosos = ["nmap", "hydra", "john", "aircrack", "sqlmap"]
    for proc in psutil.process_iter(['pid', 'name']):
        nombre = proc.info['name']
        if nombre and any(p in nombre.lower() for p in procesos_sospechosos):
            if nombre not in alertado_proc:
                enviar_alerta(f"Proceso sospechoso detectado: `{nombre}` (PID {proc.info['pid']})")
                alertado_proc.add(nombre)

def revisar_conexiones():
    conexiones = psutil.net_connections()
    for conn in conexiones:
        if conn.status == 'ESTABLISHED' and conn.raddr:
            ip = conn.raddr.ip
            if ip not in alertado_ips and not ip.startswith("192.168") and not ip.startswith("127."):
                enviar_alerta(f"Conexión activa detectada con IP externa: {ip}")
                alertado_ips.add(ip)

def loop_centinela():
    while True:
        revisar_logs_ssh()
        revisar_procesos()
        revisar_conexiones()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    enviar_alerta("🟢 CENTINELA INICIADO: Vigilancia activa en el nodo.")
    loop_centinela()
