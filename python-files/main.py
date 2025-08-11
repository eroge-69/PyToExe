import random

# Waren (ID: Name)
WAREN = {
    0: "Holz",
    1: "Wein",
    2: "Gewürze",
    3: "Stoffe",
    4: "Eisen",
    5: "Salz",
    6: "Fische",
    7: "Getreide",
    8: "Gold",
    9: "Keramik"
}

# Städte (ID: Name)
STÄDTE = {
    0: "München",
    1: "Hamburg",
    2: "Berlin",
    3: "Köln",
    4: "Frankfurt",
    5: "Dresden",
    6: "Leipzig",
    7: "Stuttgart",
    8: "Bremen",
    9: "Nürnberg"
}

# Meldungen (Beispielhafte Events)
MELDUNGEN = [
    "Starker Sturm verzögert die Reise.",
    "Günstige Handelsbedingungen in der Stadt.",
    "Piratenangriff! Einige Waren gehen verloren.",
    "Markt ist überfüllt, Preise sinken.",
    "Gute Ernte, Preise für Getreide fallen.",
    "Seuchenwarnung! Handel eingeschränkt.",
    "Neue Handelsroute eröffnet.",
    "Preise für Gewürze steigen.",
    "Zoll erhöht, Handel wird teurer.",
    "Lagerfeuer am Hafen bringt Glück.",
    # ... bis 50 Meldungen
]
# Für die Demo fülle ich 50 Meldungen mit Variationen
while len(MELDUNGEN) < 50:
    MELDUNGEN.append(f"Zufälliges Ereignis Nummer {len(MELDUNGEN)+1}")

# Aufträge (Missionen)
AUFTRÄGE = [
    {"ware": 0, "menge": 50, "stadt": 1, "belohnung": 500},
    {"ware": 4, "menge": 30, "stadt": 3, "belohnung": 700},
    {"ware": 2, "menge": 20, "stadt": 5, "belohnung": 600},
    {"ware": 9, "menge": 10, "stadt": 0, "belohnung": 1000},
    {"ware": 1, "menge": 40, "stadt": 7, "belohnung": 450},
    # ... bis 50 Aufträge
]

# Für Demo füllen wir 50 Aufträge mit Zufallsdaten
while len(AUFTRÄGE) < 50:
    ware = random.randint(0, 9)
    menge = random.randint(10, 60)
    stadt = random.randint(0, 9)
    belohnung = menge * random.randint(8, 20)
    AUFTRÄGE.append({"ware": ware, "menge": menge, "stadt": stadt, "belohnung": belohnung})

# Schwierigkeitsgrade
SCHWIERIGKEITSGRADE = {
    1: "Einfach",
    2: "Mittel",
    3: "Schwer"
}

# Spielparameter basierend auf Schwierigkeitsgrad
def get_startkapital(schwierigkeit):
    if schwierigkeit == 1:
        return 5000
    elif schwierigkeit == 2:
        return 3000
    else:
        return 1500

def get_preisschwankung(schwierigkeit):
    if schwierigkeit == 1:
        return 0.1
    elif schwierigkeit == 2:
        return 0.25
    else:
        return 0.5

# Startpreise für Waren in jeder Stadt (Basispreis)
basis_preise = {}
for stadt in STÄDTE.keys():
    basis_preise[stadt] = {}
    for ware in WAREN.keys():
        basis_preise[stadt][ware] = random.randint(10, 100)

# Preise aktuell mit Schwankungen
def get_aktueller_preis(stadt, ware, schwierigkeit):
    basis = basis_preise[stadt][ware]
    schwankung = get_preisschwankung(schwierigkeit)
    faktor = 1 + random.uniform(-schwankung, schwankung)
    preis = int(basis * faktor)
    return max(preis, 1)

# Spielklasse
class SchiffhandelSpiel:
    def __init__(self, schwierigkeit, max_runden):
        self.schwierigkeit = schwierigkeit
        self.max_runden = max_runden
        self.runde = 0
        self.geld = get_startkapital(schwierigkeit)
        self.lager = {ware: 0 for ware in WAREN}
        self.position = 0  # Startstadt München
        self.aufträge = random.sample(AUFTRÄGE, 5)  # 5 zufällige Aufträge
        self.meldungen = MELDUNGEN
        print(f"Spiel gestartet mit Schwierigkeitsgrad {SCHWIERIGKEITSGRADE[schwierigkeit]} und Startkapital {self.geld} Gold.")
        print(f"Start in Stadt: {STÄDTE[self.position]}")

    def zeige_status(self):
        print(f"\nRunde {self.runde}/{self.max_runden if self.max_runden else '∞'}")
        print(f"Stadt: {STÄDTE[self.position]}")
        print(f"Geld: {self.geld} Gold")
        print("Lagerbestand:")
        for ware, menge in self.lager.items():
            if menge > 0:
                print(f"  {WAREN[ware]}: {menge}")
        print("\nAktuelle Aufträge:")
        for i, auftrag in enumerate(self.aufträge):
            print(f" {i}: {auftrag['menge']} {WAREN[auftrag['ware']]} nach {STÄDTE[auftrag['stadt']]} (Belohnung: {auftrag['belohnung']} Gold)")

    def reise(self):
        print("\nMögliche Reiseziele:")
        for stadt_id, name in STÄDTE.items():
            if stadt_id != self.position:
                print(f" {stadt_id}: {name}")
        try:
            ziel = int(input("Wohin möchtest du reisen? (Stadt-ID): "))
            if ziel in STÄDTE and ziel != self.position:
                self.position = ziel
                self.runde += 1
                print(f"Du bist jetzt in {STÄDTE[self.position]}.")
                self.ereignis_auslösen()
            else:
                print("Ungültiges Ziel.")
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")

    def kaufen(self):
        print("\nWaren zum Kauf:")
        for ware, name in WAREN.items():
            preis = get_aktueller_preis(self.position, ware, self.schwierigkeit)
            print(f" {ware}: {name} - Preis: {preis} Gold")
        try:
            ware_id = int(input("Welche Ware möchtest du kaufen? (ID): "))
            if ware_id in WAREN:
                preis = get_aktueller_preis(self.position, ware_id, self.schwierigkeit)
                menge = int(input("Wie viel möchtest du kaufen?: "))
                kosten = preis * menge
                if menge > 0 and self.geld >= kosten:
                    self.geld -= kosten
                    self.lager[ware_id] += menge
                    print(f"{menge} {WAREN[ware_id]} gekauft für {kosten} Gold.")
                else:
                    print("Nicht genügend Geld oder ungültige Menge.")
            else:
                print("Ungültige Ware.")
        except ValueError:
            print("Bitte gültige Zahlen eingeben.")

    def verkaufen(self):
        print("\nWaren zum Verkauf:")
        for ware, name in WAREN.items():
            if self.lager[ware] > 0:
                preis = get_aktueller_preis(self.position, ware, self.schwierigkeit)
                print(f" {ware}: {name} - Preis: {preis} Gold, Lager: {self.lager[ware]}")
        try:
            ware_id = int(input("Welche Ware möchtest du verkaufen? (ID): "))
            if ware_id in WAREN and self.lager[ware_id] > 0:
                preis = get_aktueller_preis(self.position, ware_id, self.schwierigkeit)
                menge = int(input("Wie viel möchtest du verkaufen?: "))
                if 0 < menge <= self.lager[ware_id]:
                    einnahmen = preis * menge
                    self.geld += einnahmen
                    self.lager[ware_id] -= menge
                    print(f"{menge} {WAREN[ware_id]} verkauft für {einnahmen} Gold.")
                    self.prüfe_auftrag(ware_id)
                else:
                    print("Ungültige Menge.")
            else:
                print("Ungültige Ware oder nichts auf Lager.")
        except ValueError:
            print("Bitte gültige Zahlen eingeben.")

    def prüfe_auftrag(self, ware_id):
        erfüllte_aufträge = []
        for auftrag in self.aufträge:
            if (auftrag['ware'] == ware_id and
                auftrag['stadt'] == self.position and
                self.lager[ware_id] >= auftrag['menge']):
                # Auftrag erfüllt
                print(f"Auftrag erfüllt! Du bekommst {auftrag['belohnung']} Gold.")
                self.geld += auftrag['belohnung']
                self.lager[ware_id] -= auftrag['menge']
                erfüllte_aufträge.append(auftrag)
        for a in erfüllte_aufträge:
            self.aufträge.remove(a)
            # neuen Auftrag hinzufügen
            neuer_auftrag = random.choice(AUFTRÄGE)
            self.aufträge.append(neuer_auftrag)

    def ereignis_auslösen(self):
        meldung = random.choice(self.meldungen)
        print(f"Ereignis: {meldung}")
        # Einfache Umsetzung einiger Ereignisse:
        if "Piratenangriff" in meldung:
            verlust_ware = random.choice(list(WAREN.keys()))
            verlust_menge = min(self.lager[verlust_ware], random.randint(1,5))
            self.lager[verlust_ware] -= verlust_menge
            print(f"Du hast {verlust_menge} {WAREN[verlust_ware]} durch Piraten verloren.")
        elif "Sturm" in meldung:
            self.runde += 1  # zusätzliche Runde verloren
            print("Der Sturm hat deine Reise verzögert.")
        elif "Preise für Gewürze steigen" in meldung:
            # Gewürze teurer, erhöhe Basispreis an diesem Ort temporär
            basis_preise[self.position][2] = int(basis_preise[self.position][2] * 1.5)
            print("Gewürze sind jetzt teurer!")

    def spielzug(self):
        self.zeige_status()
        print("\nAktionen:")
        print(" 1: Reisen")
        print(" 2: Kaufen")
        print(" 3: Verkaufen")
        print(" 4: Beenden")
        wahl = input("Was möchtest du tun? ")
        if wahl == "1":
            self.reise()
        elif wahl == "2":
            self.kaufen()
        elif wahl == "3":
            self.verkaufen()
        elif wahl == "4":
            self.runde = self.max_runden  # Spiel beenden
        else:
            print("Ungültige Eingabe.")

    def spiel_läuft(self):
        if self.max_runden == 0:
            return True
        return self.runde < self.max_runden

def spiel_starten():
    print("Willkommen zum Schiffhandelsspiel!")
    print("Schwierigkeitsgrade:")
    for key, val in SCHWIERIGKEITSGRADE.items():
        print(f" {key}: {val}")
    schwierigkeit = 0
    while schwierigkeit not in SCHWIERIGKEITSGRADE:
        try:
            schwierigkeit = int(input("Wähle Schwierigkeitsgrad (1-3): "))
        except ValueError:
            pass
    print("Spielmodi:")
    print(" 1: 100 Runden")
    print(" 2: 500 Runden")
    print(" 3: Endlos")
    modus = 0
    while modus not in [1,2,3]:
        try:
            modus = int(input("Wähle Spielmodus: "))
        except ValueError:
            pass
    max_runden = {1: 100, 2: 500, 3: 0}[modus]
    spiel = SchiffhandelSpiel(schwierigkeit, max_runden)

    while spiel.spiel_läuft():
        spiel.spielzug()

    print("\nSpiel beendet!")
    print(f"Endkapital: {spiel.geld} Gold")
    print("Danke fürs Spielen!")

if __name__ == "__main__":
    spiel_starten()
