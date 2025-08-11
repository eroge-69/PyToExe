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

# Meldungen
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
]

# Fülle auf 50 Meldungen auf
while len(MELDUNGEN) < 50:
    MELDUNGEN.append(f"Zufälliges Ereignis Nummer {len(MELDUNGEN) + 1}")

# Aufträge
AUFTRÄGE = [
    {"ware": 0, "menge": 50, "stadt": 1, "belohnung": 500},
    {"ware": 4, "menge": 30, "stadt": 3, "belohnung": 700},
    {"ware": 2, "menge": 20, "stadt": 5, "belohnung": 600},
    {"ware": 9, "menge": 10, "stadt": 0, "belohnung": 1000},
    {"ware": 1, "menge": 40, "stadt": 7, "belohnung": 450},
]

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

def get_startkapital(schwierigkeit):
    return {1: 5000, 2: 3000, 3: 1500}.get(schwierigkeit, 3000)

def get_preisschwankung(schwierigkeit):
    return {1: 0.1, 2: 0.25, 3: 0.5}.get(schwierigkeit, 0.25)

# Basispreise
basis_preise = {
    stadt: {ware: random.randint(10, 100) for ware in WAREN}
    for stadt in STÄDTE
}

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
        self.max_lager = 100
        self.lager = {ware: 0 for ware in WAREN}
        self.position = 0
        self.aufträge = random.sample(AUFTRÄGE, 5)
        self.meldungen = MELDUNGEN
        print(f"Spiel gestartet – {SCHWIERIGKEITSGRADE[schwierigkeit]} – Startkapital: {self.geld} Gold.")
        print(f"Startort: {STÄDTE[self.position]}")

    def aktueller_lagerplatz(self):
        return sum(self.lager.values())

    def zeige_status(self):
        print(f"\n📦 Runde {self.runde}/{self.max_runden if self.max_runden else '∞'}")
        print(f"🏙️  Stadt: {STÄDTE[self.position]}")
        print(f"💰 Geld: {self.geld} Gold")
        print(f"📦 Lagerplatz: {self.aktueller_lagerplatz()}/{self.max_lager}")
        print("📦 Lagerbestand:")
        for ware, menge in self.lager.items():
            if menge > 0:
                print(f"  - {WAREN[ware]}: {menge}")
        print("\n📜 Aufträge:")
        for i, auftrag in enumerate(self.aufträge):
            print(f" {i}: {auftrag['menge']} {WAREN[auftrag['ware']]} nach {STÄDTE[auftrag['stadt']]} (Belohnung: {auftrag['belohnung']} Gold)")

    def reise(self):
        print("\n🚢 Reiseziele:")
        for stadt_id, name in STÄDTE.items():
            if stadt_id != self.position:
                print(f" {stadt_id}: {name}")
        try:
            ziel = int(input("Wohin möchtest du reisen? (ID): "))
            if ziel in STÄDTE and ziel != self.position:
                self.position = ziel
                self.runde += 1
                print(f"Angekommen in {STÄDTE[self.position]}.")
                self.ereignis_auslösen()
            else:
                print("Ungültiges Ziel.")
        except ValueError:
            print("Bitte gültige Zahl eingeben.")

    def kaufen(self):
        print("\n🛒 Waren zum Kauf:")
        for ware, name in WAREN.items():
            preis = get_aktueller_preis(self.position, ware, self.schwierigkeit)
            print(f" {ware}: {name} – {preis} Gold")
        try:
            ware_id = int(input("Welche Ware kaufen? (ID): "))
            if ware_id in WAREN:
                preis = get_aktueller_preis(self.position, ware_id, self.schwierigkeit)
                menge = int(input("Wie viel kaufen?: "))
                kosten = preis * menge
                if menge > 0 and self.geld >= kosten:
                    if self.aktueller_lagerplatz() + menge > self.max_lager:
                        print("❌ Nicht genug Platz im Lager!")
                        return
                    self.geld -= kosten
                    self.lager[ware_id] += menge
                    print(f"{menge} {WAREN[ware_id]} gekauft für {kosten} Gold.")
                else:
                    print("Ungültige Menge oder nicht genug Geld.")
            else:
                print("Ungültige Ware.")
        except ValueError:
            print("Bitte gültige Zahlen eingeben.")

    def verkaufen(self):
        print("\n💸 Waren zum Verkauf:")
        for ware, name in WAREN.items():
            if self.lager[ware] > 0:
                preis = get_aktueller_preis(self.position, ware, self.schwierigkeit)
                print(f" {ware}: {name} – {preis} Gold, Lager: {self.lager[ware]}")
        try:
            ware_id = int(input("Welche Ware verkaufen? (ID): "))
            if ware_id in WAREN and self.lager[ware_id] > 0:
                menge = int(input("Wie viel verkaufen?: "))
                if 0 < menge <= self.lager[ware_id]:
                    erfüllte_aufträge = []
                    rest_menge = menge
                    for auftrag in self.aufträge:
                        if (auftrag['ware'] == ware_id and
                            auftrag['stadt'] == self.position and
                            rest_menge >= auftrag['menge']):
                            print(f"✅ Auftrag erfüllt! +{auftrag['belohnung']} Gold.")
                            self.geld += auftrag['belohnung']
                            self.lager[ware_id] -= auftrag['menge']
                            rest_menge -= auftrag['menge']
                            erfüllte_aufträge.append(auftrag)
                    for a in erfüllte_aufträge:
                        self.aufträge.remove(a)
                        neuer_auftrag = random.choice(AUFTRÄGE)
                        self.aufträge.append(neuer_auftrag)
                    if rest_menge > 0:
                        preis = get_aktueller_preis(self.position, ware_id, self.schwierigkeit)
                        einnahmen = preis * rest_menge
                        self.geld += einnahmen
                        self.lager[ware_id] -= rest_menge
                        print(f"{rest_menge} {WAREN[ware_id]} verkauft für {einnahmen} Gold.")
                else:
                    print("Ungültige Menge.")
            else:
                print("Ungültige Ware oder leer.")
        except ValueError:
            print("Bitte gültige Zahlen eingeben.")

    def ereignis_auslösen(self):
        meldung = random.choice(self.meldungen)
        print(f"📣 Ereignis: {meldung}")
        if "Piratenangriff" in meldung:
            verlust_ware = random.choice(list(WAREN.keys()))
            verlust_menge = min(self.lager[verlust_ware], random.randint(1, 5))
            self.lager[verlust_ware] -= verlust_menge
            print(f"⚠️ {verlust_menge} {WAREN[verlust_ware]} durch Piraten verloren.")
        elif "Sturm" in meldung:
            self.runde += 1
            print("🌪️ Der Sturm hat deine Reise verzögert.")
        elif "Gewürze steigen" in meldung:
            basis_preise[self.position][2] = int(basis_preise[self.position][2] * 1.5)
            print("📈 Gewürzpreise steigen!")

    def spielzug(self):
        self.zeige_status()
        print("\n🎮 Aktionen:")
        print(" 1: Reisen")
        print(" 2: Kaufen")
        print(" 3: Verkaufen")
        print(" 4: Beenden")
        wahl = input("Aktion wählen: ")
        if wahl == "1":
            self.reise()
        elif wahl == "2":
            self.kaufen()
        elif wahl == "3":
            self.verkaufen()
        elif wahl == "4":
            self.runde = self.max_runden
        else:
            print("Ungültige Eingabe.")

    def spiel_läuft(self):
        return self.max_runden == 0 or self.runde < self.max_runden

def spiel_starten():
    print("⚓ Willkommen zum Schiffhandelsspiel!")
    print("Schwierigkeitsgrade:")
    for key, val in SCHWIERIGKEITSGRADE.items():
        print(f" {key}: {val}")
    schwierigkeit = 0
    while schwierigkeit not in SCHWIERIGKEITSGRADE:
        try:
            schwierigkeit = int(input("Wähle Schwierigkeitsgrad (1–3): "))
        except ValueError:
            pass
    print("Spielmodi:")
    print(" 1: 100 Runden")
    print(" 2: 500 Runden")
    print(" 3: Endlos")
    modus = 0
    while modus not in [1, 2, 3]:
        try:
            modus = int(input("Wähle Modus: "))
        except ValueError:
            pass
    max_runden = {1: 100, 2: 500, 3: 0}[modus]
    spiel = SchiffhandelSpiel(schwierigkeit, max_runden)
    while spiel.spiel_läuft():
        spiel.spielzug()
    print("\n🏁 Spiel beendet!")
    print(f"💰 Endkapital: {spiel.geld} Gold")
    print("🎉 Danke fürs Spielen!")

if __name__ == "__main__":
    spiel_starten()
