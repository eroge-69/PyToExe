import subprocess
import os
from datetime import datetime
import time

log_dir = r"C:\suporte_ial\log_restart"
log_file = os.path.join(log_dir, "linx_nfeproc_restart.log")
os.makedirs(log_dir, exist_ok=True)

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")

def restart_service(service):
    log(f"Iniciando reinício do serviço {service}...")
    subprocess.run(f'net stop {service}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    subprocess.run(f'net start {service}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("Reinício do serviço finalizado.")

if __name__ == "__main__":
    restart_service("Linx_NfeProc")