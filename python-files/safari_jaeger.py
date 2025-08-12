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
        reparatur_kosten = 10
        repariert = False
        for a in self.ausruestung:
            if a.haltbarkeit < a.max_haltbarkeit:
                if self.geld >= reparatur_kosten:
                    self.geld -= reparatur_kosten
                    a.haltbarkeit = a.max_haltbarkeit
                    print(f"{a.name} repariert.")
                    repariert = True
                else:
                    print("Nicht genug Geld für weitere Reparaturen.")
                    break
        if not repariert:
            print("Keine Ausrüstung muss repariert werden.")


class Ausruestung:
    def __init__(self, name, preis, staerke, haltbarkeit, verbrauch=1):
        self.name = name
        self.preis = preis
        self.staerke = staerke
        self.haltbarkeit = haltbarkeit
        self.max_haltbarkeit = haltbarkeit
        self.verbrauch = verbrauch

    def __str__(self):
        return f"{self.name} (Stärke: {self.staerke}, Haltbarkeit: {self.haltbarkeit}/{self.max_haltbarkeit})"


class Tier:
    def __init__(self, name, preis, staerke, groesse, groessenklasse):
        self.name = name
        self.preis = preis
        self.staerke = staerke
        self.groesse = groesse
        self.groessenklasse = groessenklasse

    def __str__(self):
        return f"{self.name} (Preis: {self.preis}, Stärke: {self.staerke}, Größe: {self.groessenklasse})"


class Auftrag:
    def __init__(self, ziel_tier, belohnung, frist=5):
        self.ziel_tier = ziel_tier
        self.belohnung = belohnung
        self.frist = frist

    def __str__(self):
        return f"Fange ein {self.ziel_tier} (Belohnung: {self.belohnung} Geld, Frist: {self.frist} Runden)"

# --- Speicherfunktionen ---

def speichern(spieler, schwierigkeit):
    with open("spielstand.sav", "wb") as f:
        pickle.dump({"spieler": spieler, "schwierigkeit": schwierigkeit}, f)
    print("Spiel gespeichert.")

def laden():
    try:
        with open("spielstand.sav", "rb") as f:
            daten = pickle.load(f)
            print("Spiel geladen.")
            return daten["spieler"], daten.get("schwierigkeit", "mittel")
    except FileNotFoundError:
        print("Keine gespeicherte Datei gefunden.")
        return None, None

# --- Spielmechaniken ---

def erstelle_auftraege(tiere, schwierigkeit):
    auftraege = []
    ausgewaehlte_tiere = set()
    while len(auftraege) < 3 and len(ausgewaehlte_tiere) < len(tiere):
        tier = random.choice(tiere)
        if tier.name in ausgewaehlte_tiere:
            continue
        ausgewaehlte_tiere.add(tier.name)

        belohnung, frist = auftrag_daten(schwierigkeit)
        auftraege.append(Auftrag(tier.name, belohnung, frist))
    return auftraege

def auftraege_aktualisieren(auftraege, spieler, tiere, schwierigkeit):
    vorhandene_tiere = {a.ziel_tier for a in auftraege}
    while len(auftraege) < 3 and len(vorhandene_tiere) < len(tiere):
        tier = random.choice(tiere)
        if tier.name in vorhandene_tiere:
            continue
        vorhandene_tiere.add(tier.name)
        belohnung, frist = auftrag_daten(schwierigkeit)
        neuer_auftrag = Auftrag(tier.name, belohnung, frist)
        auftraege.append(neuer_auftrag)
        print(f"Neuer Auftrag hinzugefügt: {neuer_auftrag}")

def auftrag_daten(schwierigkeit):
    if schwierigkeit == "leicht":
        return random.randint(40, 100), random.randint(6, 10)
    elif schwierigkeit == "mittel":
        return random.randint(50, 150), random.randint(4, 7)
    elif schwierigkeit == "schwer":
        return random.randint(80, 200), random.randint(3, 5)
    return 50, 5

def auftraege_frist_aktualisieren(spieler):
    abgelaufene = []
    for auftrag in spieler.auftraege:
        auftrag.frist -= 1
        if auftrag.frist <= 0:
            abgelaufene.append(auftrag)
    for auftrag in abgelaufene:
        spieler.auftraege.remove(auftrag)
        print(f"Auftrag '{auftrag}' ist abgelaufen und wurde entfernt.")

def preise_aktualisieren(tiere, spieler):
    for tier in tiere:
        schwankung = random.randint(-5, 5)
        tier.preis = max(10, tier.preis + schwankung)

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
    "Eine Beruhigungspistole wurde gestohlen.",
    "Die Preise für Ausrüstung sind wegen hoher Nachfrage gestiegen.",
]

def ereignis_anzeigen(spieler):
    meldung = random.choice(ereignisse)
    print(f"\n[Zeitungsmeldung] {meldung}\n")

    if "Ausrüstung" in meldung and "gestiegen" in meldung:
        for a in spieler.ausruestung:
            a.preis += 5
        print("💡 Ausrüstungen sind nun teurer.")
    elif "gestohlen" in meldung and spieler.ausruestung:
        gestohlen = random.choice(spieler.ausruestung)
        spieler.ausruestung.remove(gestohlen)
        print(f"⚠️ Deine Ausrüstung '{gestohlen.name}' wurde gestohlen!")

# --- Statusanzeige ---

def print_status(spieler):
    print(f"\n💰 Geld: {spieler.geld}")
    print("📦 Tiere:")
    for tier in spieler.tiere:
        print(f" - {tier}")
    print("🧰 Ausrüstung:")
    for a in spieler.ausruestung:
        print(f" - {a}")
    print("📜 Aufträge:")
    for a in spieler.auftraege:
        print(f" - {a}")

# --- Hauptspiel ---

def main():
    print("🐘 Willkommen bei Safari Jäger!")

    spieler = None
    schwierigkeit = "mittel"

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
            spieler, schwierigkeit = laden()
            if spieler:
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

    if not spieler.auftraege:
        spieler.auftraege = erstelle_auftraege(tiere, schwierigkeit)

    runde = 1
    while True:
        print(f"\n📅 --- Runde {runde} ---")
        ereignis_anzeigen(spieler)
        preise_aktualisieren(tiere, spieler)
        auftraege_aktualisieren(spieler.auftraege, spieler, tiere, schwierigkeit)
        auftraege_frist_aktualisieren(spieler)
        print_status(spieler)

        print("\n🔧 Optionen:")
        print("1) Tier fangen")
        print("2) Ausrüstung kaufen")
        print("3) Tier verkaufen")
        print("4) Auftrag erfüllen")
        print("5) Ausrüstung reparieren")
        print("6) Spiel speichern")
        print("7) Spiel beenden")

        wahl = input("Deine Wahl: ")

        if wahl == "1":
            print("\nVerfügbare Tiere:")
            for i, tier in enumerate(tiere):
                print(f"{i + 1}) {tier}")
            try:
                auswahl = int(input("Welches Tier willst du fangen? "))
                if 1 <= auswahl <= len(tiere):
                    safari_jagd(spieler, tiere[auswahl - 1], schwierigkeit)
                else:
                    print("Ungültige Auswahl.")
            except ValueError:
                print("Ungültige Eingabe.")

        elif wahl == "2":
            print("\nVerfügbare Ausrüstung:")
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
            speichern(spieler, schwierigkeit)

        elif wahl == "7":
            print("🛑 Spiel beendet.")
            break

        else:
            print("Ungültige Eingabe.")

        runde += 1

# --- Startpunkt ---

if __name__ == "__main__":
    main()
