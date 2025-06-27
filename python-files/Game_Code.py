import random

geld = 1000
runde = 0

firmen = {
    "Bäckerei":       {"preis": 100,  "gewinnrate": 10, "besitz": 0, "min": 5,  "max": 20, "letzte_rate": 10},
    "Autowerkstatt":  {"preis": 500,  "gewinnrate": 15, "besitz": 0, "min": 10, "max": 25, "letzte_rate": 15},
    "IT-Firma":       {"preis": 1000, "gewinnrate": 20, "besitz": 0, "min": 15, "max": 30, "letzte_rate": 20},
    "Restaurant":     {"preis": 300,  "gewinnrate": 12, "besitz": 0, "min": 7,  "max": 22, "letzte_rate": 12},
    "Fitnessstudio":  {"preis": 700,  "gewinnrate": 18, "besitz": 0, "min": 12, "max": 28, "letzte_rate": 18},
    "Buchladen":      {"preis": 150,  "gewinnrate": 8,  "besitz": 0, "min": 5,  "max": 18, "letzte_rate": 8},
    "Kino":           {"preis": 800,  "gewinnrate": 17, "besitz": 0, "min": 10, "max": 27, "letzte_rate": 17},
    "Friseursalon":   {"preis": 200,  "gewinnrate": 9,  "besitz": 0, "min": 6,  "max": 20, "letzte_rate": 9},
    "Tanzschule":     {"preis": 400,  "gewinnrate": 14, "besitz": 0, "min": 9,  "max": 24, "letzte_rate": 14},
    "Softwarefirma":  {"preis": 1200, "gewinnrate": 22, "besitz": 0, "min": 18, "max": 32, "letzte_rate": 22},
}

def aktualisiere_gewinnraten():
    for name, info in firmen.items():
        aenderung = random.uniform(-5, 5)
        neue_rate = info["gewinnrate"] + aenderung
        neue_rate = max(info["min"], min(neue_rate, info["max"]))
        neue_rate = round(neue_rate, 2)
        info["letzte_rate"] = info["gewinnrate"]
        info["gewinnrate"] = neue_rate

def zeige_rate_aenderung(info):
    diff = info["gewinnrate"] - info["letzte_rate"]
    if diff > 0:
        return f"+{diff:.2f}% ↑"
    elif diff < 0:
        return f"{diff:.2f}% ↓"
    else:
        return "±0.00%"

def roulette_farbe(zahl):
    # Null ist grün
    if zahl == 0:
        return "grün"
    # Bei Roulette sind die roten Zahlen diese (klassisch):
    rot = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    if zahl in rot:
        return "rot"
    else:
        return "schwarz"

def spiele_roulette():
    global geld
    print("\nWillkommen beim Roulette!")
    print("Du kannst auf eine Zahl (0-36), eine Farbe (rot/schwarz) oder beides setzen.")
    print("Gewinn: Zahl trifft → 35x Einsatz, Farbe trifft → 10x Einsatz, beides trifft → 50x Einsatz.")
    print("Gib 'q' ein, um das Roulette zu verlassen.\n")

    while True:
        print(f"Aktueller Kontostand: {geld:.2f} Euro")
        einsatz = input("Wie viel möchtest du setzen? (oder 'q' zum Beenden) ").lower()
        if einsatz == 'q':
            print("Roulette beendet, zurück zum Hauptmenü.")
            break
        try:
            einsatz = float(einsatz)
            if einsatz <= 0:
                print("Bitte eine positive Zahl eingeben.")
                continue
            if einsatz > geld:
                print("Du hast nicht genug Geld.")
                continue
        except ValueError:
            print("Ungültige Eingabe.")
            continue

        zahl_eingabe = input("Wähle eine Zahl zwischen 0 und 36 (oder leer lassen, wenn keine Zahl): ").lower()
        if zahl_eingabe == 'q':
            print("Roulette beendet, zurück zum Hauptmenü.")
            break
        if zahl_eingabe == '':
            zahl = None
        else:
            try:
                zahl = int(zahl_eingabe)
                if zahl < 0 or zahl > 36:
                    print("Zahl muss zwischen 0 und 36 liegen.")
                    continue
            except ValueError:
                print("Ungültige Zahl.")
                continue

        farbe_eingabe = input("Wähle eine Farbe (rot/schwarz) oder leer lassen, wenn keine Farbe: ").lower()
        if farbe_eingabe == 'q':
            print("Roulette beendet, zurück zum Hauptmenü.")
            break
        if farbe_eingabe not in ('rot', 'schwarz', ''):
            print("Ungültige Farbe. Bitte 'rot' oder 'schwarz' eingeben oder leer lassen.")
            continue
        if farbe_eingabe == '':
            farbe = None
        else:
            farbe = farbe_eingabe

        if zahl is None and farbe is None:
            print("Du musst mindestens eine Zahl oder Farbe wählen.")
            continue

        roulette_zahl = random.randint(0,36)
        roulette_farbe_erg = roulette_farbe(roulette_zahl)

        print(f"\nRoulette dreht... Zahl ist: {roulette_zahl} ({roulette_farbe_erg})")

        gewinn = 0
        zahl_trifft = (zahl == roulette_zahl)
        farbe_trifft = (farbe == roulette_farbe_erg)

        if zahl_trifft and farbe_trifft:
            gewinn = einsatz * 50
            print(f"Super! Zahl und Farbe stimmen überein! Du gewinnst {gewinn:.2f} Euro!")
        elif zahl_trifft:
            gewinn = einsatz * 35
            print(f"Glückwunsch! Die Zahl stimmt! Du gewinnst {gewinn:.2f} Euro!")
        elif farbe_trifft:
            gewinn = einsatz * 10
            print(f"Die Farbe stimmt! Du gewinnst {gewinn:.2f} Euro!")
        else:
            geld -= einsatz
            print(f"Leider verloren. Du verlierst {einsatz:.2f} Euro.")

        if gewinn > 0:
            geld += gewinn

        if geld <= 0:
            print("Du hast kein Geld mehr. Das Spiel ist zu Ende.")
            break

print("Willkommen zum Tycoon-Spiel mit dynamischen Gewinnraten und Roulette!\n")

while True:
    print(f"\n--- Runde {runde} ---")
    print(f"Aktueller Kontostand: {geld:.2f} Euro\n")

    gesamtgewinn = 0
    for name, info in firmen.items():
        if info["besitz"] > 0:
            gewinn = info["besitz"] * info["preis"] * (info["gewinnrate"] / 100)
            gesamtgewinn += gewinn
            print(f"Deine {info['besitz']} Einheiten von {name} bringen dir {gewinn:.2f} Euro Gewinn (Rate: {info['gewinnrate']}%).")
    print(f"Gewinn dieser Runde: {gesamtgewinn:.2f} Euro")
    geld += gesamtgewinn

    aktualisiere_gewinnraten()

    while True:
        wahl = input("\nMöchtest du investieren (i), Roulette spielen (r) oder beenden (n)? ").lower()
        if wahl == 'n':
            print("Spiel beendet. Danke fürs Spielen!")
            exit()
        elif wahl == 'i':
            print("\nWillkommen im Investitionsbereich!")
            aktion = input("Willst du kaufen (k), verkaufen (v) oder zurück (b)? ").lower()
            if aktion == 'b':
                continue
            elif aktion == 'k':
                print("\nFirmen zum Kaufen:")
                for i, (name, info) in enumerate(firmen.items(), 1):
                    veränderung = zeige_rate_aenderung(info)
                    print(f"{i}. {name} - Preis: {info['preis']} Euro, Gewinnrate: {info['gewinnrate']}% ({veränderung})")

                auswahl = input("Wähle eine Firma (Nummer) oder tippe 's' zum Runden-überspringen: ").lower()
                if auswahl == 's':
                    print("Runde übersprungen, kein Kauf erfolgt.")
                    break
                try:
                    auswahl = int(auswahl)
                    if auswahl < 1 or auswahl > len(firmen):
                        print("Ungültige Auswahl.\n")
                        continue
                except ValueError:
                    print("Bitte eine Zahl eingeben.\n")
                    continue

                firmenname = list(firmen.keys())[auswahl - 1]
                info = firmen[firmenname]

                menge = input(f"Wieviele Einheiten von {firmenname} möchtest du kaufen? ")
                try:
                    menge = int(menge)
                    if menge <= 0:
                        print("Bitte eine positive Zahl eingeben.\n")
                        continue
                except ValueError:
                    print("Bitte eine Zahl eingeben.\n")
                    continue

                kosten = info["preis"] * menge
                if kosten > geld:
                    print("Nicht genug Geld für diese Investition.\n")
                    continue

                geld -= kosten
                info["besitz"] += menge
                print(f"Du hast {menge} Einheiten von {firmenname} gekauft für {kosten} Euro.")
                break

            elif aktion == 'v':
                eigene_firmen = [(name, info) for name, info in firmen.items() if info["besitz"] > 0]
                if not eigene_firmen:
                    print("Du besitzt keine Einheiten zum Verkaufen.\n")
                    continue

                print("\nDeine Firmen mit Einheiten:")
                for i, (name, info) in enumerate(eigene_firmen, 1):
                    print(f"{i}. {name} - Besitz: {info['besitz']} Einheiten, Preis: {info['preis']} Euro")

                auswahl = input("Wähle eine Firma zum Verkaufen (Nummer): ")
                try:
                    auswahl = int(auswahl)
                    if auswahl < 1 or auswahl > len(eigene_firmen):
                        print("Ungültige Auswahl.\n")
                        continue
                except ValueError:
                    print("Bitte eine Zahl eingeben.\n")
                    continue

                firmenname, info = eigene_firmen[auswahl - 1]

                menge = input(f"Wieviele Einheiten von {firmenname} möchtest du verkaufen? ")
                try:
                    menge = int(menge)
                    if menge <= 0:
                        print("Bitte eine positive Zahl eingeben.\n")
                        continue
                    if menge > info["besitz"]:
                        print(f"Du besitzt nur {info['besitz']} Einheiten von {firmenname}.\n")
                        continue
                except ValueError:
                    print("Bitte eine Zahl eingeben.\n")
                    continue

                erlös = info["preis"] * menge
                geld += erlös
                info["besitz"] -= menge
                print(f"Du hast {menge} Einheiten von {firmenname} verkauft und {erlös} Euro erhalten.")
                break
            else:
                print("Ungültige Eingabe.")
        elif wahl == 'r':
            spiele_roulette()
        else:
            print("Ungültige Eingabe. Bitte 'i', 'r' oder 'n' eingeben.")

    runde += 1
