import sys
import webbrowser

def main():
    if len(sys.argv) != 2:
        print("Verwendung: python script.py <Telefonnummer>")
        sys.exit(1)

    phone_number = sys.argv[1]

    # Prüfen, ob die Nummer mit '0' beginnt
    if not phone_number.startswith("0"):
        print("Die Telefonnummer muss mit einer 0 beginnen. Kein Webseitenaufruf.")
        sys.exit(1)

    # Erste Ziffer entfernen
    modified_number = phone_number[1:]

    # URL zusammenbauen
    url = f"https://www.tellows.de/num/{modified_number}"

    # Webseite im Standardbrowser öffnen
    webbrowser.open(url)

if __name__ == "__main__":
    main()
