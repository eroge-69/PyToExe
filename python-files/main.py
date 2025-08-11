import random
import json
import os

# --- Konstanten ---

WAREN = {
    0: "Holz", 1: "Wein", 2: "Gewürze", 3: "Stoffe", 4: "Eisen",
    5: "Salz", 6: "Fische", 7: "Getreide", 8: "Gold", 9: "Keramik"
}

STÄDTE = {
    0: "München", 1: "Hamburg", 2: "Berlin", 3: "Köln", 4: "Frankfurt",
    5: "Dresden", 6: "Leipzig", 7: "Stuttgart", 8: "Bremen", 9: "Nürnberg"
}

STADT_BONI = {
    2: {3: 0.10}  # Berlin gibt 10% mehr für Stoffe (ware 3)
}

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

while len(MELDUNGEN) < 50:
    MELDUNGEN.append(f"Zufälliges Ereignis Nummer {len(MELDUNGEN) + 1}")

AUFTRÄGE = [
    {"ware": 0, "menge": 50, "stadt": 1, "belohnung": 500},
    {"ware": 4, "menge": 30, "stadt": 3, "belohnung": 700},
    {"ware": 2, "menge": 20, "stadt": 5, "belohnung": 600},
    {"ware": 9, "menge": 10, "stadt": 0, "belohnung": 1000},
    {"ware": 1, "menge": 40, "stadt": 7, "belohnung": 450},
]

while len(AUFTRÄGE) < 50:
    AUFTRÄGE.append({
        "ware": random.randint(0, 9),
        "menge": random.randint(10, 60),
        "stadt": random.randint(0, 9),
        "belohnung": random.randint(100, 1200)
    })

SCHWIERIGKEITSGRADE = {1: "Einfach", 2: "Mittel", 3: "Schwer"}

def get_startkapital(schwierigkeit):
    return {1: 5000, 2: 3000, 3: 1500}.get(schwierigkeit, 3000)

def get_preisschwankung(schwierigkeit):
    return {1: 0.1, 2: 0.25, 3: 0.5}.get(schwierigkeit, 0.25)

basis_preise = {
    stadt: {ware: random.randint(10, 100) for ware in WAREN}
    for stadt in STÄDTE
}

# --- Spielklasse beginnt hier ---
class SchiffhandelSpiel:
    def __init__(self, schwierigkeit, max_runden, name):
        self.name = name
        self.schwierigkeit = schwierigkeit
        self.max_runden = max_runden
        self.runde = 0
        self.geld = get_startkapital(schwierigkeit)
        self.max_lager = 100
        self.lager = {ware: 0 for ware in WAREN}
        self.position = 0
        self.aufträge = random.sample(AUFTRÄGE, 5)
        self.meldungen = MELDUNGEN
        self.preisverlauf = {
            stadt: {ware: [] for ware in WAREN}
            for stadt in STÄDTE
        }
        self.schiff_upgrades = {
            "lager": 0,
            "schnelligkeit": 0,
            "piratenschutz": 0,
            "verkaufsbonus": 0
        }
        print(f"Spiel gestartet von {self.name} – {SCHWIERIGKEITSGRADE[schwierigkeit]} – Startkapital: {self.geld} Gold.")
        print(f"Startort: {STÄDTE[self.position]}")

    def get_aktueller_preis(self, stadt, ware):
        basis = basis_preise[stadt][ware]
        schwankung = get_preisschwankung(self.schwierigkeit)
        faktor = 1 + random.uniform(-schwankung, schwankung)
        
        # Einfluss von NPC-Händlern auf Preise:
        npc_einfluss = self.npc_preise_einfluss(stadt, ware)
        faktor *= (1 + npc_einfluss)

        preis = max(int(basis * faktor), 1)
        verlauf = self.preisverlauf[stadt][ware]
        verlauf.append(preis)
        if len(verlauf) > 5:
            verlauf.pop(0)
        return preis

    def npc_preise_einfluss(self, stadt, ware):
        # NPC Händler beeinflussen Preis zwischen -10% und +10%
        einfluss = 0
        for npc in self.npc_händler:
            if npc["stadt"] == stadt and npc["ware"] == ware:
                einfluss += npc["preis_modifikator"]
        return einfluss

    def aktueller_lagerplatz(self):
        return sum(self.lager.values())

    def zeige_standort_und_geld(self):
        print(f"\n📍 Aktueller Ort: {STÄDTE[self.position]} | 💰 Geld: {self.geld} Gold | 🚢 Lagerplatz: {self.aktueller_lagerplatz()}/{self.max_lager}")

    def zeige_status(self):
        print(f"\n👤 Spieler: {self.name}")
        print(f"📦 Runde {self.runde}/{self.max_runden if self.max_runden else '∞'}")
        print(f"🏙️  Stadt: {STÄDTE[self.position]}")
        print(f"💰 Geld: {self.geld} Gold")
        print(f"📦 Lagerplatz: {self.aktueller_lagerplatz()}/{self.max_lager}")
        print(f"🚢 Schiff-Upgrades: Lager +{self.schiff_upgrades['lager']*50}, Geschwindigkeit +{self.schiff_upgrades['schnelligkeit']}, Piratenschutz +{self.schiff_upgrades['piratenschutz']}, Verkaufsbonus +{int(self.schiff_upgrades['verkaufsbonus']*100)}%")
        print("📦 Lagerbestand:")
        for ware, menge in self.lager.items():
            if menge > 0:
                print(f"  - {WAREN[ware]}: {menge}")
        print("\n📜 Aufträge:")
        for i, auftrag in enumerate(self.aufträge):
            print(f" {i}: {auftrag['menge']} {WAREN[auftrag['ware']]} nach {STÄDTE[auftrag['stadt']]} (Belohnung: {auftrag['belohnung']} Gold)")
        upgrade_slots = max(0, 5 - sum(self.schiff_upgrades.values()))
        print(f"\n🔧 Verfügbare Schiff-Upgrades: {upgrade_slots} (jeweils +50 Lagerplatz, +1 Geschwindigkeit, +1 Piratenschutz, +5% Verkaufsbonus)")
        print(f"   Kosten: Lager 1000 Gold, Geschwindigkeit 1500 Gold, Piratenschutz 2000 Gold, Verkaufsbonus 1200 Gold")

    def zeige_karte(self):
        print("\n🗺️ Minikarte:")
        for stadt_id, name in STÄDTE.items():
            marker = "🛳️" if stadt_id == self.position else "   "
            print(f"{marker} {stadt_id}: {name}")

    def zeige_handelsübersicht(self):
        print("\n📊 Handelsübersicht:")
        for ware, name in WAREN.items():
            verlauf = self.preisverlauf[self.position][ware]
            if verlauf:
                verlauf_str = " → ".join(str(p) for p in verlauf)
                print(f"{name}: {verlauf_str}")

    def reise(self):
        self.zeige_standort_und_geld()
        self.zeige_karte()
        try:
            ziel = int(input("Wohin möchtest du reisen? (ID): "))
            if ziel in STÄDTE and ziel != self.position:
                reisen_runden = max(1, 2 - self.schiff_upgrades["schnelligkeit"])  # Schnellere Schiffe brauchen weniger Runden
                self.runde += reisen_runden
                self.position = ziel
                print(f"{self.name} ist angekommen in {STÄDTE[self.position]} nach {reisen_runden} Runde(n).")
                self.ereignis_auslösen()
            else:
                print(f"{self.name}, ungültiges Ziel oder du bist bereits dort.")
        except ValueError:
            print("Bitte gültige Zahl eingeben.")

    def kaufen(self):
        self.zeige_standort_und_geld()
        print("\n🛒 Waren zum Kauf:")
        for ware in WAREN:
            preis = self.get_aktueller_preis(self.position, ware)
            print(f" {ware}: {WAREN[ware]} – {preis} Gold")
        print(" 99: Schiff-Upgrades kaufen")
        try:
            ware_id = int(input("Welche Ware kaufen? (ID): "))
            if ware_id == 99:
                self.schiff_upgrade_kaufen()
                return
            menge = int(input("Wie viel kaufen?: "))
            preis = self.get_aktueller_preis(self.position, ware_id)
            kosten = preis * menge
            if menge > 0 and self.geld >= kosten:
                if self.aktueller_lagerplatz() + menge > self.max_lager:
                    print(f"{self.name}, nicht genug Platz im Lager!")
                    return
                self.geld -= kosten
                self.lager[ware_id] += menge
                print(f"{self.name} hat {menge} {WAREN[ware_id]} für {kosten} Gold gekauft.")
            else:
                print(f"{self.name}, nicht genug Geld oder ungültige Menge.")
        except ValueError:
            print("Ungültige Eingabe.")

    def schiff_upgrade_kaufen(self):
        print("\n🚢 Schiff-Upgrades:")
        print(" 1: Lager +50 Platz (1000 Gold)")
        print(" 2: Schnellere Reise (1500 Gold)")
        print(" 3: Piratenschutz (2000 Gold)")
        print(" 4: Verkaufsbonus +5% (1200 Gold)")
        print(" 0: Abbrechen")
        try:
            wahl = int(input("Upgrade wählen: "))
            if wahl == 0:
                print("Upgrade abgebrochen.")
                return
            kosten_map = {1:1000, 2:1500, 3:2000, 4:1200}
            key_map = {1:"lager", 2:"schnelligkeit", 3:"piratenschutz", 4:"verkaufsbonus"}
            if wahl in kosten_map:
                if sum(self.schiff_upgrades.values()) >= 5:
                    print("Maximale Anzahl an Upgrades erreicht!")
                    return
                kosten = kosten_map[wahl]
                if self.geld >= kosten:
                    self.geld -= kosten
                    self.schiff_upgrades[key_map[wahl]] += 1
                    if key_map[wahl] == "lager":
                        self.max_lager += 50
                    print(f"{self.name} hat Upgrade {key_map[wahl]} gekauft!")
                else:
                    print("Nicht genug Gold für dieses Upgrade.")
            else:
                print("Ungültige Auswahl.")
        except ValueError:
            print("Ungültige Eingabe.")

    def verkaufen(self):
        self.zeige_standort_und_geld()
        print("\n💸 Waren zum Verkauf:")
        for ware in WAREN:
            if self.lager[ware] > 0:
                preis = self.get_aktueller_preis(self.position, ware)
                print(f" {ware}: {WAREN[ware]} – {preis} Gold, Lager: {self.lager[ware]}")
        try:
            ware_id = int(input("Welche Ware verkaufen? (ID): "))
            menge = int(input("Wie viel verkaufen?: "))
            if 0 < menge <= self.lager[ware_id]:
                rest = menge
                erfüllte = []
                for auftrag in self.aufträge:
                    if auftrag['ware'] == ware_id and auftrag['stadt'] == self.position and rest >= auftrag['menge']:
                        print(f"✅ {self.name} hat einen Auftrag erfüllt und {auftrag['belohnung']} Gold erhalten!")
                        self.geld += auftrag['belohnung']
                        self.lager[ware_id] -= auftrag['menge']
                        rest -= auftrag['menge']
                        erfüllte.append(auftrag)
                for a in erfüllte:
                    self.aufträge.remove(a)
                    self.aufträge.append(random.choice(AUFTRÄGE))
                if rest > 0:
                    preis = self.get_aktueller_preis(self.position, ware_id)
                    bonus = STADT_BONI.get(self.position, {}).get(ware_id, 0) + self.schiff_upgrades["verkaufsbonus"]*0.05
                    einnahmen = int(preis * rest * (1 + bonus))
                    self.geld += einnahmen
                    self.lager[ware_id] -= rest
                    print(f"{self.name} hat {rest} {WAREN[ware_id]} für {einnahmen} Gold verkauft (inkl. Bonus {int(bonus*100)}%).")
            else:
                print(f"{self.name}, ungültige Menge.")
        except (ValueError, KeyError):
            print("Ungültige Eingabe.")

    def ereignis_auslösen(self):
        meldung = random.choice(self.meldungen)
        print(f"\n📣 Ereignis für {self.name}: {meldung}")
        if "Sturm" in meldung:
            verlust = 5 + self.schiff_upgrades["piratenschutz"] * -3
            verlust = max(0, verlust)
            for ware in self.lager:
                if self.lager[ware] > 0:
                    verloren = min(self.lager[ware], verlust)
                    self.lager[ware] -= verloren
                    print(f"⛈️ Verlust von {verloren} {WAREN[ware]} durch Sturm.")
        elif "Piratenangriff" in meldung:
            if self.schiff_upgrades["piratenschutz"] > 0:
                print("🚨 Piratenschutz verhindert Verluste!")
            else:
                verlust = 10
                for ware in self.lager:
                    if self.lager[ware] > 0:
                        verloren = min(self.lager[ware], verlust)
                        self.lager[ware] -= verloren
                        print(f"🏴‍☠️ Verlust von {verloren} {WAREN[ware]} durch Piraten!")
        elif "Günstige Handelsbedingungen" in meldung:
            bonus = 0.10
            self.geld += int(self.geld * bonus)
            print(f"💵 Geld durch günstige Bedingungen um {int(bonus*100)}% erhöht.")
        # Hier kannst du weitere Event-Entscheidungen einbauen

    def npc_händler_bewegen(self):
        # Beispiel: NPC Händler ändern zufällig Stadt & Preise modifizieren
        for npc in self.npc_händler:
            alt_stadt = npc["stadt"]
            neu_stadt = random.choice(list(STÄDTE.keys()))
            npc["stadt"] = neu_stadt
            # Preismodifikator zwischen -0.1 und 0.1
            npc["preis_modifikator"] = random.uniform(-0.1, 0.1)
            if neu_stadt != alt_stadt:
                print(f"NPC-Händler zieht von {STÄDTE[alt_stadt]} nach {STÄDTE[neu_stadt]}")

    def npc_init(self):
        # Erstelle NPC Händler mit zufälligen Städten und Waren
        self.npc_händler = []
        for _ in range(5):
            npc = {
                "stadt": random.choice(list(STÄDTE.keys())),
                "ware": random.choice(list(WAREN.keys())),
                "preis_modifikator": random.uniform(-0.1, 0.1)
            }
            self.npc_händler.append(npc)

    def spielzug(self):
        self.zeige_status()
        self.zeige_karte()
        print("\nAktionen:")
        print(" 1: Reisen")
        print(" 2: Kaufen")
        print(" 3: Verkaufen")
        print(" 4: Lager & Aufträge anzeigen")
        print(" 5: Schiff-Upgrades kaufen")
        print(" 0: Spiel beenden")
        try:
            wahl = int(input("Deine Wahl: "))
            if wahl == 1:
                self.reise()
            elif wahl == 2:
                self.kaufen()
            elif wahl == 3:
                self.verkaufen()
            elif wahl == 4:
                self.zeige_status()
            elif wahl == 5:
                self.schiff_upgrade_kaufen()
            elif wahl == 0:
                print(f"{self.name} beendet das Spiel.")
                return False
            else:
                print("Ungültige Eingabe.")
        except ValueError:
            print("Ungültige Eingabe.")
        # NPC Händler bewegen sich nach jedem Zug
        self.npc_händler_bewegen()
        self.runde += 1
        if self.max_runden and self.runde >= self.max_runden:
            print("Maximale Rundenzahl erreicht. Spiel endet.")
            return False
        if self.geld <= 0:
            print("Kein Geld mehr. Spiel endet.")
            return False
        return True

# --- Spielstart ---

def spiel_starten():
    print("🎲 Willkommen zum Schiffhandel-Spiel!")
    name = input("Wie heißt du? ")
    print("Wähle Schwierigkeitsgrad: 1=Einfach, 2=Mittel, 3=Schwer")
    try:
        schwierigkeit = int(input("Schwierigkeitsgrad: "))
        max_runden = int(input("Maximale Runden (0 = unbegrenzt): "))
        spiel = SchiffhandelSpiel(schwierigkeit, max_runden, name)
        spiel.npc_init()
        running = True
        while running:
            running = spiel.spielzug()
    except ValueError:
        print("Ungültige Eingabe. Spiel beendet.")

if __name__ == "__main__":
    spiel_starten()
