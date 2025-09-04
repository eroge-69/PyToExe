from collections import defaultdict

def parse_input(): # funktion um die eingegebenen daten zu parsen (zeilenweise auslesen)
    n = int(input("Copy & Paste jetzt oder fange mit der Anzahl der Einträge an (also einfach nur eine zahl): "))
    data = []
    for _ in range(n):
        line = input()
        parts = line.split()
        tag = parts[1]
        start = int(parts[2])
        ende = int(parts[3])
        staerke = int(parts[4])
        data.append((tag, start, ende, staerke))
    return data



def find_max_balls(data):                   # funktion um die maximale Anzahl der gleichzeitig benötigten medizinbälle zu finden
    stunden = defaultdict(int)
    for tag, start, ende, staerke in data:
        for stunde in range(start, ende):
            stunden[(tag, stunde)] += staerke
    max_balls = 0
    max_zeit = None
    for zeit, anzahl in stunden.items():
        if anzahl > max_balls:
            max_balls = anzahl
            max_zeit = zeit
    return max_balls, max_zeit



if __name__ == "__main__": # Hauptprogramm
    print("\nWICHTIG: So gibst du die Daten ein!")
    print("1. Zuerst gibst du die Anzahl der Einträge ein (also wie viele Zeilen du hast).")
    print("2. Dann gibst du für jede Zeile die Daten einzeln ein, z.B.:")
    print("   5a Montag 10 11 30")
    print("   (Klasse, Wochentag, Startzeit, Endzeit, Anzahl Schüler)")
    print("Drücke nach jeder Zeile ENTER.")
    print("Du kannst die Daten auch aus einer Liste kopieren und Zeile für Zeile einfügen.")
    print("Beispiel für 2 Einträge:")
    print("2")
    print("5a Montag 10 11 30")
    print("5b Dienstag 9 10 25\n")
    data = parse_input()
    max_balls, (tag, stunde) = find_max_balls(data)
    print(f"\nMaximal werden {max_balls} Medizinbälle gleichzeitig benötigt, nämlich am {tag} um {stunde} Uhr.")