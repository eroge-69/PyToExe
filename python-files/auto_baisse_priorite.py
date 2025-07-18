
import psutil
import time

def est_processus_critique(nom):
    noms_critiques = [
        "System", "Idle", "wininit.exe", "csrss.exe", "services.exe",
        "lsass.exe", "smss.exe", "svchost.exe", "explorer.exe"
    ]
    return nom in noms_critiques

def baisser_priorite_auto(cpu_seuil=10.0):
    print("🔍 Analyse des processus consommateurs de CPU...
")
    time.sleep(1)
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            nom = proc.info['name']
            cpu = proc.info['cpu_percent']
            pid = proc.info['pid']

            if cpu > cpu_seuil and not est_processus_critique(nom):
                p = psutil.Process(pid)
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                print(f"✅ {nom} (PID {pid}) - CPU: {cpu}% → priorité réduite.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

if __name__ == "__main__":
    print("📉 Script d’optimisation automatique des processus")
    baisser_priorite_auto()
    print("\n✅ Terminé.")
