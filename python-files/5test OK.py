
import os
import subprocess
import time

def lire_valeur_milieu():
    fichier = os.path.join(os.path.dirname(__file__), "bdi_output.txt")

    if not os.path.exists(fichier):
        print(f"Fichier {fichier} introuvable.")
        return None

    # Lire toutes les lignes en ignorant la première
    with open(fichier, "r", encoding="utf-8") as f:
        lignes = [line.split() for line in f.readlines()[1:]]

    if not lignes:
        print("Fichier vide ou sans données exploitables.")
        return None

    mid = len(lignes) // 2
    return lignes[mid][2] if len(lignes[mid]) >= 3 else None


# Initialisation
initial_battery_charge = 100

# Demande de tension
voltage = input("Voltage 24/48 (defaut 24V) : ")
volt = "48" if voltage.strip() == "48" else "24"
print(f"Voltage : {volt}")

# Demande des valeurs de démarrage
bat_star_min = input("STARTUP_MIN : ")
bat_star_max = input("STARTUP_MAX : ")

# Boucles pour les valeurs de BAT_MIN_ADJ et BAT_MAX_ADJ
for bat_min_adj in range(5, 65, 5):
    for bat_max_adj in range(5, 65, 5):
        # Création du fichier de configuration
        with open("bdi_configuration.txt", "w") as config:
            config.write(f"Nominal voltage = {volt}\n")
            config.write(f"BAT. MAX ADJ. = {bat_max_adj}\n")
            config.write(f"BAT. MIN ADJ. = {bat_min_adj}\n")
            config.write(f"BDI ADJ STAR.MAX = {bat_star_max}\n")
            config.write(f"BDI ADJ STAR.MIN = {bat_star_min}\n")
            config.write("BDI RESET = 30\n")
            config.write("BDI REL. 100 OLD = 20\n")
            config.write("BDI REL. 100 NEW = 90\n")

        # Exécution de la simulation
        result = subprocess.run(["bdi_simulation.exe", str(initial_battery_charge)], capture_output=True)
        battery_percentage = result.returncode
        print(f"Test  MinADJ : {bat_min_adj}  MaxADJ : {bat_max_adj}     ==>  End SOC: {battery_percentage}")

        # Vérification du pourcentage SOC
        if 19 <= battery_percentage <= 21:
            if os.path.exists("bdi_output.txt"):
                valeur_milieu = lire_valeur_milieu()
                print(f"    Middle SOC : {valeur_milieu}")
                valeur_milieu = int(valeur_milieu)
                if 59 <= valeur_milieu <= 61 :
                    output_file = (f"MinADJ.{bat_min_adj}__MaxADJ.{bat_max_adj}__STARMin.{bat_star_min}__STARMax.{bat_star_max}__MiddleSOC.{valeur_milieu}__EndSOC.{battery_percentage}.txt")
                    os.rename("bdi_output.txt", output_file)
                    print("    Match !")
                    print(f"    Renamed bdi_output.txt to {output_file}")

# Nettoyage
for file in ["bdi_output.txt", "bdi_configuration.txt"]:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
