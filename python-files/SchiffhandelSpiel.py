import random

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
        self.npc_händler = []   # Initialisiere leere NPC Liste
        self.npc_init()         # Erstelle NPC Händler direkt beim Start

        print(f"Spiel gestartet von {self.name} – {SCHWIERIGKEITSGRADE.get(schwierigkeit, 'Mittel')} – Startkapital: {self.geld} Gold.")
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
                    print("Nicht genug Lagerplatz!")
                else:
                    self.geld -= kosten
                    self.lager[ware_id] += menge
                    print(f"{menge} {WAREN[ware_id]} gekauft für {kosten} Gold.")
            else:
                print("Nicht genug Geld oder ungültige Menge.")
        except ValueError:
            print("Ungültige Eingabe!")

    def verkaufen(self):
        self.zeige_standort_und_geld()
        print("\n📦 Lagerbestand zum Verkauf:")
        for ware, menge in self.lager.items():
            if menge > 0:
                preis = self.get_aktueller_preis(self.position, ware)
                print(f" {ware}: {WAREN[ware]} – {menge} Stück – Aktueller Preis: {preis} Gold")

        try:
            ware_id = int(input("Welche Ware verkaufen? (ID): "))
            menge = int(input("Wie viel verkaufen?: "))
            if menge <= 0 or menge > self.lager.get(ware_id, 0):
                print("Ungültige Menge.")
                return

            preis = self.get_aktueller_preis(self.position, ware_id)
            verkaufserlös = preis * menge
            verkaufserlös = int(verkaufserlös * (1 + self.schiff_upgrades["verkaufsbonus"]))

            self.lager[ware_id] -= menge
            self.geld += verkaufserlös
            print(f"{menge} {WAREN[ware_id]} verkauft für {verkaufserlös} Gold.")

            # Aufträge erfüllen
            rest = menge
            for auftrag in self.aufträge[:]:
                if auftrag['ware'] == ware_id and auftrag['stadt'] == self.position and rest >= auftrag['menge']:
                    self.geld += auftrag['belohnung']
                    rest -= auftrag['menge']
                    print(f"Auftrag erfüllt: {auftrag['menge']} {WAREN[ware_id]} nach {STÄDTE[self.position]}! Belohnung: {auftrag['belohnung']} Gold.")
                    self.aufträge.remove(auftrag)
                if rest <= 0:
                    break
        except ValueError:
            print("Ungültige Eingabe!")

    def schiff_upgrade_kaufen(self):
        max_upgrades = 5
        aktuell = sum(self.schiff_upgrades.values())
        frei = max_upgrades - aktuell
        if frei <= 0:
            print("Keine Upgrade-Slots mehr frei!")
            return
        print(f"\n🚢 Schiff-Upgrades kaufen (noch {frei} Slots frei):")
        print(" 1: Lager +50 (1000 Gold)")
        print(" 2: Geschwindigkeit +1 (1500 Gold)")
        print(" 3: Piratenschutz +1 (2000 Gold)")
        print(" 4: Verkaufsbonus +5% (1200 Gold)")

        try:
            wahl = int(input("Upgrade wählen: "))
            kosten = {1: 1000, 2: 1500, 3: 2000, 4: 1200}.get(wahl, None)
            if kosten is None:
                print("Ungültige Wahl.")
                return
            if self.geld < kosten:
                print("Nicht genug Gold.")
                return
            if wahl == 1:
                self.schiff_upgrades["lager"] += 1
                self.max_lager += 50
            elif wahl == 2:
                self.schiff_upgrades["schnelligkeit"] += 1
            elif wahl == 3:
                self.schiff_upgrades["piratenschutz"] += 1
            elif wahl == 4:
                self.schiff_upgrades["verkaufsbonus"] += 0.05
            self.geld -= kosten
            print("Upgrade gekauft!")
        except ValueError:
            print("Ungültige Eingabe!")

    def ereignis_auslösen(self):
        ereignis = random.choice(self.meldungen)
        print(f"\n⚠️ Ereignis: {ereignis}")

        if "Sturm" in ereignis:
            verlust = max(0, 5 - self.schiff_upgrades["piratenschutz"] * 3)
            for ware in list(self.lager):
                if self.lager[ware] > 0:
                    verloren = min(self.lager[ware], verlust)
                    self.lager[ware] -= verloren
                    if verloren > 0:
                        print(f"Durch Sturm verloren: {verloren} {WAREN[ware]}")
        elif "Piratenangriff" in ereignis:
            verlust = max(0, 3 - self.schiff_upgrades["piratenschutz"])
            for ware in list(self.lager):
                if self.lager[ware] > 0:
                    verloren = min(self.lager[ware], verlust)
                    self.lager[ware] -= verloren
                    if verloren > 0:
                        print(f"Piraten haben {verloren} {WAREN[ware]} gestohlen!")
        elif "günstige" in ereignis.lower():
            bonus = 0.2
            print(f"Die Preise in {STÄDTE[self.position]} sind heute um {int(bonus*100)}% günstiger.")
            for ware in WAREN:
                basis_preise[self.position][ware] = int(basis_preise[self.position][ware] * (1 - bonus))
        # Weitere Ereignisse können ergänzt werden

    def npc_init(self):
        self.npc_händler.clear()
        for _ in range(random.randint(3, 8)):
            stadt = random.choice(list(STÄDTE.keys()))
            ware = random.choice(list(WAREN.keys()))
            preis_modifikator = round(random.uniform(-0.3, 0.3), 2)
            self.npc_händler.append({"stadt": stadt, "ware": ware, "preis_modifikator": preis_modifikator})

    def spiel_starten(self):
        while self.runde < self.max_runden or self.max_runden == 0:
            self.runde += 1
            print(f"\n=== Runde {self.runde} ===")
            self.zeige_status()

            print("\nAktionen: 1) Reisen 2) Kaufen 3) Verkaufen 4) Aufträge ansehen 5) Ende")
            try:
                wahl = int(input("Was möchtest du tun? "))
            except ValueError:
                print("Ungültige Eingabe!")
                continue

            if wahl == 1:
                self.reise()
            elif wahl == 2:
                self.kaufen()
            elif wahl == 3:
                self.verkaufen()
            elif wahl == 4:
                print("\n📜 Deine Aufträge:")
                for auftrag in self.aufträge:
                    print(f"- {auftrag['menge']} {WAREN[auftrag['ware']]} nach {STÄDTE[auftrag['stadt']]} (Belohnung: {auftrag['belohnung']} Gold)")
            elif wahl == 5:
                print("Spiel wird beendet.")
                break
            else:
                print("Ungültige Wahl.")

        print(f"\nSpiel beendet! Du hast {self.geld} Gold.")

# Beispiel-Spielstart:
if __name__ == "__main__":
    print("Willkommen zum Schiffhandel!")
    name = input("Gib deinen Namen ein: ")
    schwierigkeit = 0
    while schwierigkeit not in [1, 2, 3]:
        try:
            schwierigkeit = int(input("Wähle Schwierigkeit (1=Einfach, 2=Mittel, 3=Schwer): "))
        except ValueError:
            pass
    max_runden = 0
    while True:
        try:
            max_runden = int(input("Maximale Runden (0 für unendlich): "))
            if max_runden >= 0:
                break
        except ValueError:
            pass

    spiel = SchiffhandelSpiel(schwierigkeit, max_runden, name)
    spiel.spiel_starten()
