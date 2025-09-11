import csv
import os

# Folderul unde salvăm (Downloads)
DOWNLOADS = r"C:\daniel"
CSV_NAME = "dulap.csv"

def genereaza_dulap(lungime, adancime, inaltime, numar_usi=2, numar_polite=0, G=18):
    panouri = []
    # Partea stanga / dreapta (lungime = lungime - 18, adancime = adancime, inaltime = inaltime)
    panouri.append({"Nume": "Partea stanga", "L": lungime, "A": adancime - G, "H": inaltime - G})
    panouri.append({"Nume": "Partea dreapta", "L": lungime, "A": adancime - G, "H": inaltime - G})

    # Sus (lungime = lungime - 36)
    panouri.append({"Nume": "Sus", "L": lungime - 2*G, "A": adancime - G, "H": G})
    # Jos (lungime = lungime)
    panouri.append({"Nume": "Jos", "L": lungime, "A": adancime - G, "H": G})
    # Spate (lungime = lungime - 10, inaltime = inaltime - 10)
    panouri.append({"Nume": "Spate", "L": lungime - 10, "A": adancime, "H": inaltime - 10})

    # Polițe
    for i in range(numar_polite):
        panouri.append({
            "Nume": f"Polita {i+1}",
            "L": lungime - 2*G,
            "A": adancime - (G+10),
            "H": G
        })

    # Uși: lățime ajustată și înălțime ușă = inaltime - 4
    reducere = 4 if numar_usi == 1 else 3
    latime_usa = (lungime / numar_usi) - reducere
    inaltime_usa = inaltime - 4

    for i in range(numar_usi):
        panouri.append({
            "Nume": f"Usa {i+1}",
            "L": latime_usa,      # lățimea ușii (cu reducerea aplicată)
            "A": adancime,        # adâncimea dulapului (nu apare în CSV)
            "H": inaltime_usa,    # înălțimea ușii
        })

    return panouri

def salveaza_csv(panouri, material):
    cale = os.path.join(DOWNLOADS, CSV_NAME)
    with open(cale, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=",")
        # header exact în ordinea cerută
        writer.writerow(["Lungime", "Latime", "Cantitate", "Material", "", "", "Denumire panou"])
        for p in panouri:
            if p["Nume"].startswith("Usa"):
                lung = int(round(p["H"]))   # înălțimea ușii
                lat = int(round(p["L"]))    # lățimea ușii cu reducere
                den = p["Nume"]
            elif p["Nume"] in ["Partea stanga", "Partea dreapta"]:
                lung = int(round(p["H"]))   # înălțime dulap
                lat = int(round(p["A"]))    # adâncime
                den = p["Nume"]
            elif p["Nume"] in ["Sus", "Jos", "Polita 1", "Polita 2", "Polita 3"]:
                lung = int(round(p["L"]))   # lungimea politei sau panoului
                lat = int(round(p["A"]))    # adâncime
                den = p["Nume"]
            elif p["Nume"] == "Spate":
                lung = int(round(p["L"]))   # lungime spate
                lat = int(round(p["H"]))    # înălțime spate
                den = p["Nume"]
            else:
                lung = int(round(p["L"]))
                lat = int(round(p["A"]))
                den = p["Nume"]

            writer.writerow([lung, lat, 1, material, "", "", den])

    print(f"CSV generat corect: {cale}")

if __name__ == "__main__":
    try:
        lungime = int(input("Lungime dulap (mm): "))
        adancime = int(input("Adancime dulap (mm): "))
        inaltime = int(input("Inaltime dulap (mm): "))
        numar_usi = int(input("Numar usi (1 sau 2): "))
        numar_polite = int(input("Numar polite: "))
        material = input("Material (ex: PAL, MDF): ")

        panouri = genereaza_dulap(lungime, adancime, inaltime, numar_usi=numar_usi, numar_polite=numar_polite)
        salveaza_csv(panouri, material)

    except Exception as e:
       print("❌ Eroare:", e)

    input("Apasa Enter pentru a inchide...")

