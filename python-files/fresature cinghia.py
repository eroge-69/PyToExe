import pandas as pd

def calcola_fresature(diametro_puleggia, spessore_cinghia, modulo_gomma, spessore_gomma_dorso=17):
    R = diametro_puleggia / spessore_cinghia

    # Configurazioni fresature possibili
    configurazioni = [
        {"Passo (mm)": 12, "Profondit� (mm)": 10, "Larghezza (mm)": 3},
        {"Passo (mm)": 20, "Profondit� (mm)": 10, "Larghezza (mm)": 4},
        {"Passo (mm)": 35, "Profondit� (mm)": 10, "Larghezza (mm)": 6},
        {"Passo (mm)": 15, "Profondit� (mm)": 8,  "Larghezza (mm)": 3},
        {"Passo (mm)": 25, "Profondit� (mm)": 9,  "Larghezza (mm)": 5},
    ]

    def momento_inerzia_medio(h_d, h_f, w_f, p):
        # Sezione unit width 1 mm
        I_pieno = (1 * h_d**3) / 12
        fraz_fresata = w_f / p
        I_fresato = (1 * (h_d - h_f)**3) / 12
        I_medio = (1 - fraz_fresata) * I_pieno + fraz_fresata * I_fresato
        return I_medio, I_pieno

    risultati = []
    for conf in configurazioni:
        I_medio, I_pieno = momento_inerzia_medio(spessore_gomma_dorso, conf["Profondit� (mm)"], conf["Larghezza (mm)"], conf["Passo (mm)"])
        miglioramento = I_medio / I_pieno
        E_eff = modulo_gomma * miglioramento
        ris = conf.copy()
        ris["Momento d'inerzia medio (mm^4)"] = round(I_medio, 2)
        ris["Momento d'inerzia pieno (mm^4)"] = round(I_pieno, 2)
        ris["Rapporto I_medio / I_pieno"] = round(miglioramento, 3)
        ris["Modulo elastico effettivo (MPa)"] = round(E_eff, 3)
        ris["Rapporto puleggia/spessore (D/t)"] = round(R, 2)
        ris["Spessore gomma dorso (mm)"] = spessore_gomma_dorso
        ris["Modulo elastico gomma (MPa)"] = modulo_gomma
        risultati.append(ris)

    df = pd.DataFrame(risultati)
    return df

if __name__ == "__main__":
    # Inserisci i tuoi valori qui
    diametro = 200         # mm
    spessore = 25          # mm
    modulo_gomma = 5       # MPa

    df_risultati = calcola_fresature(diametro, spessore, modulo_gomma)
    print(df_risultati)
