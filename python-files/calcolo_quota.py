import time

def calcola_nuovo_valore():
    quota_desiderata = float(input("Valore a cui deve essere la quota: "))
    quota_rilevata = float(input("Valore della quota rilevata: "))
    valore_pratico_attuale = float(input("Valore pratico attuale: "))

    differenza = quota_desiderata - quota_rilevata
    correzione = differenza / 2
    nuovo_valore = valore_pratico_attuale + correzione

    print(f"\nIl nuovo valore pratico corretto è: {nuovo_valore}")
    print("\nIl programma si chiuderà tra 10 secondi...")
    time.sleep(10)

calcola_nuovo_valore()
