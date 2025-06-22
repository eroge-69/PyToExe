import sys
import csv

def verwerk_csv(pad_naar_bestand):
    try:
        with open(pad_naar_bestand, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            print(f"Verwerken van: {pad_naar_bestand}")
            for i, rij in enumerate(reader):
                print(f"Rij {i+1}: {rij}")
                if i >= 4:  # Stop na 5 rijen
                    break
    except Exception as e:
        print(f"Fout bij het verwerken van het bestand: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sleep een CSV-bestand op dit script om het te verwerken.")
    else:
        bestandspad = sys.argv[1]
        verwerk_csv(bestandspad)