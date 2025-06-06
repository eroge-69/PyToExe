
import random

# ----------------------------------------
# Basisklasse für Rätsel
# ----------------------------------------
class Raetsel:
    def __init__(self, frage, antwort, position):
        self.frage = frage
        self.antwort = str(antwort).lower()
        self.position = position

    def pruefe_loesung(self, nutzerantwort):
        return str(nutzerantwort).lower() == self.antwort


# ----------------------------------------
# Abgeleitete Rätselklassen
# ----------------------------------------

class MatheRaetsel(Raetsel):
    pass

class LogikRaetsel(Raetsel):
    pass

class WortRaetsel(Raetsel):
    pass


# ----------------------------------------
# Klasse Hinweis
# ----------------------------------------
class Hinweis:
    def __init__(self, beschreibung, position):
        self.beschreibung = beschreibung
        self.position = position


# ----------------------------------------
# Klasse Schatz
# ----------------------------------------
class Schatz:
    def __init__(self, beschreibung, position):
        self.beschreibung = beschreibung
        self.position = position


# ----------------------------------------
# Klasse Schatzsucher
# ----------------------------------------
class Schatzsucher:
    def __init__(self, name):
        self.name = name
        self.gesammelte_hinweise = []
        self.position = 0  # Startposition

    def sammle_hinweis(self, hinweis):
        self.gesammelte_hinweise.append(hinweis)

    def zeige_hinweise(self):
        print(f"\nHinweise für {self.name}:")
        for h in self.gesammelte_hinweise:
            print(f"- {h.beschreibung}")

    def fortschritt(self, gesamtanzahl_hinweise):
        return len(self.gesammelte_hinweise) / gesamtanzahl_hinweise * 100


# ----------------------------------------
# Klasse Schatzsuche (Verwaltung)
# ----------------------------------------
class Schatzsuche:
    def __init__(self):
        self.raetsel_liste = []
        self.hinweis_liste = []
        self.schatz = None
        self.schatzsucher = None
        self.grid_size = 5  # 5x5 Karte

    def setze_schatzsucher(self, schatzsucher):
        self.schatzsucher = schatzsucher

    def hinzufuegen_raetsel(self, raetsel):
        self.raetsel_liste.append(raetsel)

    def hinzufuegen_hinweis(self, hinweis):
        self.hinweis_liste.append(hinweis)

    def setze_schatz(self, schatz):
        self.schatz = schatz

    def zeige_karte(self, show_schatz=False):
        print("\n📜 Schatzkarte:")
        for y in range(self.grid_size):
            zeile = ""
            for x in range(self.grid_size):
                pos = y * self.grid_size + x
                symbol = "."
                if pos == self.schatzsucher.position:
                    symbol = "S"
                elif any(r.position == pos for r in self.raetsel_liste):
                    symbol = "R"
                elif any(h.position == pos for h in self.schatzsucher.gesammelte_hinweise):
                    symbol = "H"
                elif show_schatz and pos == self.schatz.position:
                    symbol = "X"
                zeile += f"{symbol} "
            print(zeile)
        print()

    def starte_spiel(self):
        print(f"Willkommen, {self.schatzsucher.name}! Die Schatzsuche beginnt...\n")

        for raetsel in self.raetsel_liste:
            self.schatzsucher.position = raetsel.position
            self.zeige_karte()

            print(f"Du erreichst Position {raetsel.position}.")
            print("Rätsel:", raetsel.frage)
            antwort = input("Deine Antwort: ")

            if raetsel.pruefe_loesung(antwort):
                print("Richtig gelöst!")
                hinweis = next((h for h in self.hinweis_liste if h.position == raetsel.position), None)
                if hinweis:
                    self.schatzsucher.sammle_hinweis(hinweis)
                    print(f"Du erhältst einen Hinweis: {hinweis.beschreibung}\n")
            else:
                print("Leider falsch.\n")

        self.schatzsucher.zeige_hinweise()
        print(f"\nDein Fortschritt: {self.schatzsucher.fortschritt(len(self.hinweis_liste)):.2f}%")

        if self.schatzsucher.fortschritt(len(self.hinweis_liste)) == 100:
            self.schatzsucher.position = self.schatz.position
            self.zeige_karte(show_schatz=True)
            print(f"\n🎉 Glückwunsch, {self.schatzsucher.name}! Du hast den Schatz gefunden!")
            print(f"Er liegt bei Position {self.schatz.position}: {self.schatz.beschreibung}")
        else:
            print("\nDu hast nicht alle Hinweise gefunden. Der Schatz bleibt verborgen...")


# ----------------------------------------
# Hilfsfunktion: Geheimcode generieren
# ----------------------------------------
def generiere_geheimcode(length):
    return ''.join(map(str, random.sample(range(10), length)))


# ----------------------------------------
# Hauptprogramm
# ----------------------------------------
if __name__ == "__main__":
    spiel = Schatzsuche()

    name = input("Gib deinen Schatzsucher-Namen ein: ")
    sucher = Schatzsucher(name)
    spiel.setze_schatzsucher(sucher)

    spiel.hinzufuegen_raetsel(MatheRaetsel("Was ist 7 + 5?", "12", 6))
    spiel.hinzufuegen_hinweis(Hinweis("Der Schatz liegt nicht im Norden.", 6))

    spiel.hinzufuegen_raetsel(WortRaetsel("Welches Wort ergibt rückwärts gelesen 'Regal'?", "lager", 12))
    spiel.hinzufuegen_hinweis(Hinweis("Er könnte vergraben sein.", 12))

    geheimcode = generiere_geheimcode(5)
    spiel.hinzufuegen_raetsel(LogikRaetsel(f"Merke dir diesen geheimen Zahlencode: {geheimcode}. Was ist die 3. Ziffer?", geheimcode[2], 18))
    spiel.hinzufuegen_hinweis(Hinweis("Die genaue Position ist 24!", 18))

    spiel.setze_schatz(Schatz("Eine Truhe voller Gold und alter Grog-Rezepte.", 24))

    spiel.starte_spiel()
