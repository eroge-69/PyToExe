import subprocess
import time
from datetime import datetime

def main():
    try:
        ip_address = input("Entrez l'adresse IP à tester : ")
        duration = int(input("Entrez la durée du test en secondes : "))
    except ValueError:
        print("Durée invalide. Veuillez entrer un nombre entier.")
        return

    print(f"Début du test de ping vers {ip_address} pendant {duration} secondes...\n")

    start_time = time.time()
    end_time = start_time + duration
    total_pings = 0
    failed_pings = 0
    results = []

    try:
        while time.time() < end_time:
            total_pings += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                output = subprocess.run(["ping", "-c", "1", ip_address], stdout=subprocess.DEVNULL)
                if output.returncode == 0:
                    print(f"[{timestamp}] Ping {total_pings}: Réussi")
                    results.append(f"[{timestamp}] Ping {total_pings}: Réussi")
                else:
                    print(f"[{timestamp}] Ping {total_pings}: Échec")
                    results.append(f"[{timestamp}] Ping {total_pings}: Échec")
                    failed_pings += 1
            except Exception as e:
                print(f"[{timestamp}] Ping {total_pings}: Erreur - {e}")
                results.append(f"[{timestamp}] Ping {total_pings}: Erreur - {e}")
                failed_pings += 1

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTest interrompu par l'utilisateur.")

    # Génération du rapport
    with open("ping_report.txt", "w") as report:
        report.write(f"Rapport de test de ping vers {ip_address}\n")
        report.write(f"Durée du test : {int(time.time() - start_time)} secondes\n")
        report.write(f"Nombre total de pings : {total_pings}\n")
        report.write(f"Nombre de pings échoués : {failed_pings}\n\n")
        report.write("Détails des pings :\n")
        report.write("\n".join(results))

    print(f"\nTest terminé. Rapport généré dans 'ping_report.txt'.")

if __name__ == "__main__":
    main()
