import os
import subprocess
import ctypes

def run_cmd(command):
    """
    Exécute une commande système avec privilèges admin.
    """
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"[OK] {command}")
    except subprocess.CalledProcessError:
        print(f"[ERREUR] Impossible d'exécuter : {command}")

def is_admin():
    """
    Vérifie si le script est exécuté en mode administrateur.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def optimize_system():
    print("=== Windows Gaming Global Optimizer ===")

    # ---- Optimisation des timers système ----
    print("\n[+] Optimisation des timers système...")
    run_cmd("bcdedit /set useplatformclock false")
    run_cmd("bcdedit /set disabledynamictick yes")
    run_cmd("bcdedit /set useplatformtick yes")

    # ---- Désactivation de services inutiles ----
    print("\n[+] Désactivation de services non essentiels pour le gaming...")
    run_cmd("sc stop Spooler")                  # Service d’impression
    run_cmd("sc config Spooler start= disabled")
    run_cmd("sc stop DiagTrack")                # Service de télémétrie
    run_cmd("sc config DiagTrack start= disabled")

    # ---- Activation du mode Performances élevées ----
    print("\n[+] Activation du mode Performances élevées...")
    run_cmd("powercfg -setactive SCHEME_MIN")

    print("\n✅ Optimisation terminée !")
    print("➡️ Redémarre ton PC pour appliquer tous les changements.")

if __name__ == "__main__":
    if is_admin():
        optimize_system()
    else:
        print("❌ Ce script doit être lancé en tant qu'administrateur !")
        input("Appuie sur Entrée pour quitter...")
