
from datetime import datetime
import time

def horloge():
    try:
        while True:
            maintenant = datetime.now()
            heure = maintenant.strftime("%H:%M:%S")
            print("Heure actuelle :", heure, end="\r")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nHorloge arrêtée.")

if __name__ == "__main__":
    horloge()
