
import sys, os, calendar, csv
from datetime import date

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def italian_day_name(d: date) -> str:
    giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
    return giorni[d.weekday()]

def working_days(year: int, month: int):
    _, last_day = calendar.monthrange(year, month)
    for day in range(1, last_day+1):
        d = date(year, month, day)
        if d.weekday() < 5:  # Monday=0 .. Friday=4
            yield d

def main():
    mese = int(input("Inserisci il mese (1-12): "))
    anno = int(input("Inserisci l'anno: "))
    persona1 = input("Inserisci il nome della prima persona: ")
    persona2 = input("Inserisci il nome della seconda persona: ")
    persona3 = input("Inserisci il nome della terza persona: ")
    persona4 = input("Inserisci il nome della quarta persona: ")
    persona5 = input("Inserisci il nome della quinta persona: ")
    nomi = [persona1, persona2, persona3, persona4, persona5]

    base = get_base_dir()
    out_csv = os.path.join(base, f"Calendario_{anno}_{mese:02d}_Da_Stampare.csv")

    headers = ["Data", "Giorno"]
    for n in nomi:
        headers.append(f"{n} M")
        headers.append(f"{n} P")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(headers)
        for d in working_days(anno, mese):
            row = [d.strftime("%d/%m/%Y"), italian_day_name(d)]
            row += ["", ""] * len(nomi)
            w.writerow(row)

    print("Creato file:", out_csv)
    print("Nota: è un CSV delimitato da ';'. Puoi aprirlo con Excel.")

if __name__ == "__main__":
    main()
