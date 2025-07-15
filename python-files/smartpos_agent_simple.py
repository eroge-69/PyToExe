#!/usr/bin/env python3
"""
SmartPOS Agent - Version Simplifiée pour .exe autonome
Version optimisée pour fonctionner comme un exécutable standalone
avec démarrage automatique via le dossier Startup Windows.
"""

import json
import os
import requests
import socket
import time
import threading
import queue
from datetime import datetime
from ping3 import ping
import win32print
import sys
import logging
from logging.handlers import RotatingFileHandler
import base64

# --------------------------------------------
# Configuration
# --------------------------------------------
BASE_URL = "https://pos.otix.agency"
AGENT_CONFIG_FILE = "agent_config.json"
PRINTER_CONFIG_FILE = "printer_config.json"
AGENT_VERSION = "2.5.1"
MAX_RETRIES = 3

# Configuration des logs
LOG_FILE = "smartpos_agent.log"
logger = logging.getLogger("smartpos_agent")
logger.setLevel(logging.INFO)

# Handler de rotation automatique : 5 Mo max, 3 sauvegardes
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Affichage dans la console (optionnel pour .exe)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# --------------------------------------------
# Chargement de la configuration
# --------------------------------------------
def load_config():
    """Charge la configuration de l'agent"""
    if not os.path.exists(AGENT_CONFIG_FILE):
        logger.error(f"❌ {AGENT_CONFIG_FILE} non trouvé")
        return None, None, None
    
    try:
        with open(AGENT_CONFIG_FILE, "r", encoding="utf-8") as f:
            agent_config = json.load(f)
        
        token = agent_config.get("token")
        branch_id = agent_config.get("branch_id")
        
        if not token or not branch_id:
            logger.error("❌ Configuration incomplète (token ou branch_id manquant)")
            return None, None, None
        
        # Charger la config imprimante
        if not os.path.exists(PRINTER_CONFIG_FILE):
            logger.error(f"❌ {PRINTER_CONFIG_FILE} non trouvé")
            return None, None, None
        
        with open(PRINTER_CONFIG_FILE, "r", encoding="utf-8") as f:
            printer_config = json.load(f)
        
        headers = {
            "X-Restaurant-Token": token,
            "X-Branch-ID": str(branch_id),
            "Accept": "application/json",
        }
        
        logger.info("✅ Configuration chargée avec succès")
        return headers, printer_config, branch_id
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement de la config: {e}")
        return None, None, None

# --------------------------------------------
# Fonctions utilitaires
# --------------------------------------------
def list_installed_printers():
    """Retourne la liste des imprimantes installées"""
    try:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags)
        return [info[2] for info in printers]
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'énumération des imprimantes: {e}")
        return []

def ping_ip(host):
    """Ping rapide vers une adresse IP"""
    try:
        return ping(host, timeout=2) is not None
    except Exception:
        return False

def find_printer(printer_id, printer_config):
    """Trouve une imprimante par son ID"""
    for printer in printer_config.get("printers", []):
        if printer.get("id") == printer_id:
            return printer
    return None

# --------------------------------------------
# Fonctions d'impression
# --------------------------------------------
def send_escpos_to_ip_printer(escpos_bytes, ip_address, printer_name):
    """Envoie ESC/POS à une imprimante IP"""
    try:
        host, port = (ip_address.split(":") + ["9100"])[:2]
        port = int(port)

        # Ping rapide avant envoi
        for attempt in range(2):
            if ping_ip(host):
                break
            logger.warning(f"⚠️ {printer_name} ({host}) non joignable, essai {attempt + 1}/2...")
            time.sleep(1)
        else:
            logger.error(f"❌ {printer_name} pas joignable après deux tentatives.")
            return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))

        sock.sendall(escpos_bytes)
        cut_sequence = b"\n" * 5 + b"\x1d\x56\x01"  # Coupe partielle
        sock.sendall(cut_sequence)
        sock.close()
        
        logger.info(f"✅ Printed ESC/POS to IP printer {printer_name}.")
        return True
    except Exception as e:
        logger.error(f"❌ Error printing ESC/POS to {printer_name}: {e}")
        return False

def send_escpos_to_usb_printer(escpos_bytes, printer_name):
    """Envoie ESC/POS à une imprimante USB"""
    try:
        logger.info(f"🖨️ Impression ESC/POS sur USB printer {printer_name}…")

        data = escpos_bytes + b"\n" * 5 + b"\x1d\x56\x01"  # Coupe partielle

        handle = win32print.OpenPrinter(printer_name)
        job_id = win32print.StartDocPrinter(handle, 1, ("SmartPOS Text", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)

        logger.info(f"🧾 Started USB ESC/POS job {job_id}")
        logger.info(f"✅ Printed ESC/POS to USB printer {printer_name}")
        return True
    except Exception as e:
        logger.error(f"❌ USB Print Error (ESC/POS) for {printer_name}: {e}")
        return False

# --------------------------------------------
# Gestion des jobs
# --------------------------------------------
def fetch_pending_jobs(headers):
    """Récupère les jobs en attente"""
    try:
        resp = requests.get(f"{BASE_URL}/api/agent/print-jobs/pending-all", headers=headers)
        return resp.json().get("data", []) if resp.status_code == 200 else []
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {e}")
        return []

def complete_job(job_id, headers):
    """Marque un job comme terminé"""
    try:
        resp = requests.post(f"{BASE_URL}/api/agent/print-jobs/{job_id}/printed", headers=headers)
        if resp.status_code == 200:
            logger.info("✅ Job marked printed.")
        else:
            logger.warning(f"⚠️ Job {job_id} not updated (HTTP {resp.status_code}).")
    except Exception as e:
        logger.error(f"❌ Job complete error: {e}")

# --------------------------------------------
# Worker thread
# --------------------------------------------
def worker(job_queue, headers, printer_config):
    """Thread worker pour traiter les jobs"""
    while True:
        job = job_queue.get()
        if job is None:
            break

        printer = find_printer(job.get("printer_id"), printer_config)
        if not printer:
            logger.warning(f"⚠️ Unknown printer ID {job.get('printer_id')}.")
            job_queue.task_done()
            continue

        payload = job.get("payload", {})
        template = job.get("template", "")
        printer_label = printer.get("name")
        connection = printer.get("connection")
        conn_type = printer.get("connection_type")
        retries = job.get("retries", 0)
        success = False

        logger.info(f"🧾 Processing job {job.get('id')} (tentative {retries}/{MAX_RETRIES}) sur {printer_label}")

        try:
            if template == "prints.kot":
                if payload.get("escpos"):
                    escpos_bytes = base64.b64decode(payload.get("escpos"))
                    if conn_type == "usb":
                        success = send_escpos_to_usb_printer(escpos_bytes, connection)
                    elif conn_type == "ip":
                        success = send_escpos_to_ip_printer(escpos_bytes, connection, printer_label)
                    else:
                        logger.warning(f"⚠️ connection_type inconnu '{conn_type}' pour job {job.get('id')}")
                else:
                    logger.warning(f"⚠️ prints.kot sans champ escpos pour job {job.get('id')}")
            else:
                logger.warning(f"⚠️ Template inconnu '{template}' pour job {job.get('id')}")

        except Exception as e:
            logger.error(f"❌ Error printing job {job.get('id')}: {e}")
            success = False

        if success:
            complete_job(job.get("id"), headers)
        else:
            if retries < MAX_RETRIES:
                job["retries"] = retries + 1
                logger.warning(f"Job {job.get('id')} échoué, tentative {retries + 1}/{MAX_RETRIES}, on retente plus tard.")
                job_queue.put(job)
            else:
                logger.error(f"Job {job.get('id')} a échoué {MAX_RETRIES} fois, on l'abandonne.")

        job_queue.task_done()

# --------------------------------------------
# Fonction principale
# --------------------------------------------
def main():
    """Fonction principale de l'agent"""
    logger.info(f"🚀 SmartPOS Agent started (v{AGENT_VERSION})...")
    
    # Charger la configuration
    headers, printer_config, branch_id = load_config()
    if not headers or not printer_config:
        logger.error("❌ Impossible de charger la configuration. Arrêt.")
        input("Appuyez sur Entrée pour fermer...")
        return
    
    # Vérifier les imprimantes USB installées
    installed = list_installed_printers()
    for pr in printer_config.get("printers", []):
        if pr.get("connection_type") == "usb":
            win_name = pr.get("connection")
            if win_name not in installed:
                logger.warning(f"❌ Warning: l'imprimante USB « {win_name} » n'est pas installée sur cette machine.")
    
    # Créer la queue et les workers
    job_queue = queue.Queue()
    for _ in range(3):
        threading.Thread(target=worker, args=(job_queue, headers, printer_config), daemon=True).start()
    
    logger.info("✅ Workers démarrés, début de la surveillance des jobs...")
    
    # Boucle principale
    try:
        while True:
            jobs = fetch_pending_jobs(headers)
            for job in jobs:
                job_queue.put(job)
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("🛑 Agent arrêté manuellement.")
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
    
    logger.info("🛑 Agent arrêté.")

if __name__ == "__main__":
    main() 