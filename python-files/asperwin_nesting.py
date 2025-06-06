
import os
import csv

folder_putanja = r"C:\DXF"
csv_izlaz = os.path.join(folder_putanja, "lista_za_asperwin.csv")

def ukloni_kvake(tekst):
    zamene = {
        'č': 'c', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'd',
        'Č': 'C', 'Ć': 'C', 'Š': 'S', 'Ž': 'Z', 'Đ': 'D'
    }
    for slovo, zamena in zamene.items():
        tekst = tekst.replace(slovo, zamena)
    return tekst

podaci = []

for fajl in os.listdir(folder_putanja):
    if fajl.lower().endswith(".dxf"):
        ime_bez_ekstenzije = os.path.splitext(fajl)[0]
        delovi = ime_bez_ekstenzije.split("_")
        if len(delovi) >= 3:
            debljina = delovi[0]
            naziv = "_".join(delovi[1:-1])
            kolicina = delovi[-1]
            naziv = ukloni_kvake(naziv)
            naziv_fajla = ukloni_kvake(fajl)
            podaci.append([naziv_fajla, kolicina, debljina])

with open(csv_izlaz, mode='w', newline='', encoding='utf-8') as fajl:
    pisac = csv.writer(fajl, delimiter=';')
    pisac.writerow(['Naziv fajla', 'Količina', 'Debljina'])
    pisac.writerows(podaci)

print(f"✅ Gotovo! CSV fajl je snimljen kao:\n{csv_izlaz}")
input("Pritisni Enter za izlaz...")
