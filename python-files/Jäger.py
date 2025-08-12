import random
import pickle

# --- Klassen ---

class Spieler:
    def __init__(self):
        self.geld = 100
        self.ausruestung = []
        self.tiere = []
        self.auftraege = []

    def kaufen(self, ausruestung):
        if self.geld >= ausruestung.preis:
            self.geld -= ausruestung.preis
            self.ausruestung.append(ausruestung)
            print(f"{ausruestung.name} gekauft.")
        else:
            print("Du hast nicht genug Geld.")

    def verkaufen(self, tier):
        if tier in self.tiere:
            self.tiere.remove(tier)
            self.geld += tier.preis
            print(f"{tier.name} verkauft.")
        else:
            print("Dieses Tier besitzt du nicht.")

    def auftrag_erfuellen(self, auftrag):
        if auftrag in self.auftraege:
            for tier in self.tiere:
                if tier.name == auftrag.ziel_tier:
                    self.tiere.remove(tier)
                    self.geld += auftrag.belohnung
                    self.auftraege.remove(auftrag)
                    print(f"Auftrag '{auftrag}' erfüllt!")
                    return True
            print("Auftrag nicht erfüllt: Tier nicht gefunden.")
        else:
            print("Dieser Auftrag ist nicht mehr aktiv.")
        return False

    def repariere_ausruestung(self):
        for a in self.ausruestung:
            if a.haltbarkeit < a.max_haltbarkeit:
                reparatur_kosten = 10
                if self.geld >= reparatur_kosten:
                    self.geld -= reparatur_kosten
                    a.haltbarkeit = a.max_haltbarkeit
                    print(f"{a.name} repariert.")
                else:
                    print("Nicht genug Geld zum Reparieren.")
            else:
                print(f"{a.name} ist bereits in gutem Zustand.")


class Ausruestung:
    def __init__(self, name, preis, staerke, haltbarkeit, verbrauch=1):
        self.name = name
        self.preis = preis
        self.staerke = staerke
        self.haltbarkeit = haltbarkeit
        self.max_haltbarkeit = haltbarkeit
        self.verbrauch = verbrauch

    def __str__(self):
        return f"{self.name} (Preis: {self.preis}, Haltbarkeit: {self.haltbarkeit})"


class Tier:
    def __init__(self, name, preis, staerke, groesse, groessenklasse):
        self.name = name
        self.preis = preis
        self.staerke = staerke
        self.groesse = groesse
        self.groessenklasse = groessenklasse

    def __str__(self):
        return f"{self.name} (Preis: {self.preis}, Größe: {self.groessenklasse})"


class Auftrag:
    def __init__(self, ziel_tier, belohnung, frist=5):
        self.ziel_tier = ziel_tier
        self.belohnung = belohnung
        self.frist = frist

    def __str__(self):
        return f"Fange ein {self.ziel_tier} (Belohnung: {self.belohnung} Geld, Frist: {self.frist} Runden)"


# --- Funktionen ---

def laden():
    try:
        with open("spielstand.sav", "rb") as f:
            spieler = pickle.load(f)
            print("Spiel geladen.")
            return spieler
    except FileNotFoundError:
        print("Keine gespeicherte Datei gefunden.")
        return None

def speichern(spieler):
    with open("spielstand.sav", "wb") as f:
        pickle.dump(spieler, f)
    print("Spiel gespeichert.")

def erstelle_auftraege(tiere, schwierigkeit):
    auftraege = []
    while len(auftraege) < 3:
        tier = random.choice(tiere)
        if schwierigkeit == "leicht":
            belohnung = random.randint(40, 100)
            frist = random.randint(6, 10)
        elif schwierigkeit == "mittel":
            belohnung = random.randint(50, 150)
            frist = random.randint(4, 7)
        elif schwierigkeit == "schwer":
            belohnung = random.randint(80, 200)
            frist = random.randint(3, 5)
        else:
            belohnung = random.randint(50, 150)
            frist = random.randint(4, 7)

        neuer_auftrag = Auftrag(tier.name, belohnung, frist)
        auftraege.append(neuer_auftrag)
    return auftraege

def preise_aktualisieren(tiere, spieler):
    for tier in tiere:
        schwankung = random.randint(-5, 5)
        tier.preis = max(10, tier.preis + schwankung)

def auftraege_aktualisieren(auftraege, spieler, tiere, schwierigkeit):
    while len(auftraege) < 3:
        tier = random.choice(tiere)
        if schwierigkeit == "leicht":
            belohnung = random.randint(40, 100)
            frist = random.randint(6, 10)
        elif schwierigkeit == "mittel":
            belohnung = random.randint(50, 150)
            frist = random.randint(4, 7)
        elif schwierigkeit == "schwer":
            belohnung = random.randint(80, 200)
            frist = random.randint(3, 5)
        else:
            belohnung = random.randint(50, 150)
            frist = random.randint(4, 7)

        neuer_auftrag = Auftrag(tier.name, belohnung, frist)
        auftraege.append(neuer_auftrag)
        print(f"Neuer Auftrag hinzugefügt: {neuer_auftrag}")

def auftraege_frist_aktualisieren(spieler):
    abgelaufene = []
    for auftrag in spieler.auftraege:
        auftrag.frist -= 1
        if auftrag.frist <= 0:
            abgelaufene.append(auftrag)
    for auftrag in abgelaufene:
        spieler.auftraege.remove(auftrag)
        print(f"Auftrag '{auftrag}' ist abgelaufen und wurde entfernt.")

def print_status(spieler):
    print(f"\nGeld: {spieler.geld} | Tiere: {len(spieler.tiere)} | Ausrüstung: {len(spieler.ausruestung)}")
    if spieler.auftraege:
        print("Aktuelle Aufträge:")
        for a in spieler.auftraege:
            print(f" - {a}")

def safari_jagd(spieler, tier, schwierigkeit):
    ausruestung = next((a for a in spieler.ausruestung if a.haltbarkeit > 0), None)
    if not ausruestung:
        print("Keine funktionierende Ausrüstung vorhanden.")
        return

    erfolgschance = 50 + ausruestung.staerke * 5 - tier.staerke * 5
    if schwierigkeit == "leicht":
        erfolgschance += 20
    elif schwierigkeit == "schwer":
        erfolgschance -= 20

    erfolg = random.randint(1, 100) <= erfolgschance

    ausruestung.haltbarkeit -= ausruestung.verbrauch
    if ausruestung.haltbarkeit < 0:
        ausruestung.haltbarkeit = 0

    if erfolg:
        spieler.tiere.append(tier)
        print(f"Du hast das Tier '{tier.name}' gefangen!")
    else:
        print(f"Das Tier '{tier.name}' ist entkommen.")

# --- Ereignisse ---

ereignisse = [
    "Ein seltener Leopard wurde in der Nähe des Flusses gesichtet.",
    "Eine Gruppe Wilderer wurde vom Parkpersonal gefasst.",
    "Das Wetter verschlechtert sich: Sturmwarnung für die Safari-Region.",
    "Ein verletztes Tier wurde erfolgreich behandelt und freigelassen.",
    "Die Preise für Ausrüstung sind wegen hoher Nachfrage gestiegen.",
    "Ein neues Naturschutzgebiet wurde eröffnet.",
    "Ein Löwe hat eine Herde Zebras angegriffen.",
    "Die Bevölkerung fordert mehr Schutzmaßnahmen für Elefanten.",
    "Die Touristenbesuche nehmen in der Saison zu.",
    "Eine Expedition entdeckte neue Tierarten im Dschungel.",
    "Ein seltenes Flamingo-Paar wurde bei der Brut beobachtet.",
    "Eine Beruhigungspistole wurde gestohlen.",
    "Ein Nashorn wurde bei der Wanderung verletzt gefunden.",
    "Die lokale Regierung erhöht das Budget für die Wildtierüberwachung.",
    "Fallen wurden erfolgreich platziert, um invasive Arten zu fangen.",
    "Die Preise für Nashorn-Hörner auf dem Schwarzmarkt sinken.",
    "Ein Rekord-Erfolg bei der Safari-Jagd wurde gemeldet.",
    "Der Schutzzaun wurde repariert, um Tiere fernzuhalten.",
    "Ein neues Safari-Camp öffnet nächste Woche.",
    "Die Bevölkerung klagt über zunehmende Wilderei.",
    "Ein Elefant hat einen Baum gefällt.",
    "Die Vogelpopulation wächst dank besserer Bedingungen.",
    "Eine Gruppe Safari-Jäger verlor sich im Wald, wurde aber gefunden.",
    "Die Gesundheitsbehörde warnt vor einer neuen Tierkrankheit.",
    "Der Preis für Gazellenfleisch ist stark gefallen.",
    "Ein Berichterstatter veröffentlichte eine Dokumentation über die Safari.",
    "Ein seltenes Zebra wurde verkauft.",
    "Das Safari-Team bekommt neue Ausrüstung gespendet.",
    "Die Wartung der Fahrzeuge verzögert sich wegen Ersatzteilmangel.",
    "Ein Diebstahl von Ausrüstung wurde gemeldet.",
    "Eine Tiermutter schützt ihre Jungen vor Eindringlingen.",
    "Neue Regeln für Safari-Jäger werden eingeführt."
]

def ereignis_anzeigen():
    meldung = random.choice(ereignisse)
    print(f"\n[Zeitungsmeldung] {meldung}\n")

# --- Hauptprogramm ---

def main():
    print("Willkommen bei Safari Jäger!")

    spieler = None
    while True:
        print("\n1) Neues Spiel starten")
        print("2) Spiel laden")
        print("3) Beenden")
        wahl = input("Deine Wahl: ")
        if wahl == "1":
            spieler = Spieler()
            schwierigkeit = input("Wähle Schwierigkeit (leicht/mittel/schwer): ").lower()
            if schwierigkeit not in ["leicht", "mittel", "schwer"]:
                schwierigkeit = "mittel"
            break
        elif wahl == "2":
            spieler = laden()
            if spieler:
                schwierigkeit = input("Wähle Schwierigkeit (leicht/mittel/schwer): ").lower()
                if schwierigkeit not in ["leicht", "mittel", "schwer"]:
                    schwierigkeit = "mittel"
                break
        elif wahl == "3":
            print("Spiel beendet.")
            return
        else:
            print("Ungültige Eingabe.")

    tiere = [
        Tier("Löwe", 100, 8, 2.5, "Groß"),
        Tier("Elefant", 150, 10, 3.0, "Sehr Groß"),
        Tier("Gazelle", 40, 4, 1.2, "Mittel"),
        Tier("Zebra", 60, 5, 1.5, "Mittel"),
        Tier("Leopard", 80, 7, 2.0, "Groß"),
    ]

    ausruestungen = [
        Ausruestung("Beruhigungspistole", 50, 5, 10),
        Ausruestung("Netz", 30, 3, 15),
        Ausruestung("Scharfes Messer", 40, 6, 8),
    ]

    spieler.auftraege = erstelle_auftraege(tiere, schwierigkeit)
    runde = 1

    while True:
        print(f"\n--- Runde {runde} ---")
        ereignis_anzeigen()

        preise_aktualisieren(tiere, spieler)
        auftraege_aktualisieren(spieler.auftraege, spieler, tiere, schwierigkeit)
        auftraege_frist_aktualisieren(spieler)
        print_status(spieler)

        print("\nOptionen:")
        print("1) Tier fangen")
        print("2) Ausrüstung kaufen")
        print("3) Tier verkaufen")
        print("4) Auftrag erfüllen")
        print("5) Ausrüstung reparieren")
        print("6) Spiel speichern")
        print("7) Spiel beenden")

        wahl = input("Deine Wahl: ")

        if wahl == "1":
            print("Verfügbare Tiere:")
            for i, tier in enumerate(tiere):
                print(f"{i + 1}) {tier}")
            try:
                auswahl = int(input("Welches Tier willst du fangen? "))
                if 1 <= auswahl <= len(tiere):
                    tier = tiere[auswahl - 1]
                    safari_jagd(spieler, tier, schwierigkeit)
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                print("Ungültige Eingabe.")

        elif wahl == "2":
            print("Verfügbare Ausrüstung:")
            for i, ausr in enumerate(ausruestungen):
                print(f"{i + 1}) {ausr}")
            try:
                auswahl = int(input("Welche Ausrüstung willst du kaufen? "))
                if 1 <= auswahl <= len(ausruestungen):
                    spieler.kaufen(ausruestungen[auswahl - 1])
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                print("Ungültige Eingabe.")

        elif wahl == "3":
            if not spieler.tiere:
                print("Du besitzt keine Tiere.")
                continue
            print("Deine Tiere:")
            for i, tier in enumerate(spieler.tiere):
                print(f"{i + 1}) {tier}")
            try:
                auswahl = int(input("Welches Tier willst du verkaufen? "))
                if 1 <= auswahl <= len(spieler.tiere):
                    spieler.verkaufen(spieler.tiere[auswahl - 1])
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                print("Ungültige Eingabe.")

        elif wahl == "4":
            if not spieler.auftraege:
                print("Keine Aufträge verfügbar.")
                continue
            print("Deine Aufträge:")
            for i, auftrag in enumerate(spieler.auftraege):
                print(f"{i + 1}) {auftrag}")
            try:
                auswahl = int(input("Welchen Auftrag willst du erfüllen? "))
                if 1 <= auswahl <= len(spieler.auftraege):
                    spieler.auftrag_erfuellen(spieler.auftraege[auswahl - 1])
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                print("Ungültige Eingabe.")

        elif wahl == "5":
            spieler.repariere_ausruestung()

        elif wahl == "6":
            speichern(spieler)

        elif wahl == "7":
            print("Spiel beendet.")
            break

        else:
            print("Ungültige Eingabe.")

        runde += 1

if __name__ == "__main__":
    main()
