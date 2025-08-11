import requests
import pandas as pd
import numpy as np
from collections import Counter

# --- Daten herunterladen und einlesen ---
url = "https://www.lottozahlenonline.com/eurojackpot/eurojackpot_archiv.csv"
filename = "eurojackpot_archiv.csv"

response = requests.get(url)
with open(filename, "wb") as f:
    f.write(response.content)

df = pd.read_csv(filename, sep=",", header=None)
df = df.iloc[:, 1:-2]

# --- Spalten splitten und umbenennen ---
df_neu = df.copy()
df_neu[[f"Zahl {i+1}" for i in range(5)]] = df_neu.iloc[:, 0].str.split("-", expand=True)
df_neu = df_neu.drop(df_neu.columns[0], axis=1)
df_neu[[f"SuperZahl {i+1}" for i in range(2)]] = df_neu.iloc[:, 0].str.split("-", expand=True)
df_neu = df_neu.drop(df_neu.columns[0], axis=1)

for i in range(5):
    df_neu[f"Zahl {i+1}"] = pd.to_numeric(df_neu[f"Zahl {i+1}"])
for i in range(2):
    col = f"SuperZahl {i+1}"
    if col in df_neu.columns:
        df_neu[col] = pd.to_numeric(df_neu[col])

# --- Statistiken berechnen ---
df_stats = df_neu.drop(df_neu.columns[-2:], axis=1)
zeilensummen = df_stats.sum(axis=1)
mittelwert = zeilensummen.mean()
stdabw = zeilensummen.std()

df_stats2 = df_neu.drop(df_neu.columns[0:5], axis=1)
zeilensummen2 = df_stats2.sum(axis=1)
mittelwert2 = zeilensummen2.mean()
stdabw2 = zeilensummen2.std()
# --- Statistiken ausgeben ---
print("=== Statistiken der Hauptzahlen ===")
print(f"Durchschnitt der Zeilensummen: {mittelwert:.2f}")
print(f"Standardabweichung der Zeilensummen: {stdabw:.2f}")
print()
print("=== Statistiken der Superzahlen ===")
print(f"Durchschnitt der Zeilensummen: {mittelwert2:.2f}")
print(f"Standardabweichung der Zeilensummen: {stdabw2:.2f}")
print()
print("=== Erste 4 Zeilen des DataFrames ===")
print(df_neu.head(4))
print()
# --- Funktionen ---
def ziehe_eurojackpot():
    zahlen_spalten = [f"Zahl {i+1}" for i in range(5)]
    super_spalten = [f"SuperZahl {i+1}" for i in range(2)]
    zufallszahlen = np.sort(np.random.choice(range(1, 51), 5, replace=False))
    superzahlen = np.sort(np.random.choice(range(1, 13), 2, replace=False))
    df_zufall = pd.DataFrame([list(zufallszahlen) + list(superzahlen)], columns=zahlen_spalten + super_spalten)
    return df_zufall

def hat_nachbarn(zahlen):
    zahlen = sorted(zahlen)
    for i in range(len(zahlen) - 1):
        if zahlen[i+1] - zahlen[i] == 1:
            return True
    return False

def kombi_schon_gezogen(df, zahlen_liste):
    gezogene_kombi = sorted(zahlen_liste)
    mask = df[[f"Zahl {i+1}" for i in range(5)]].apply(lambda row: sorted(row.tolist()) == gezogene_kombi, axis=1)
    return mask.any()

def ist_statistisch_passend(zahlen_liste, mittelwert, stdabw, toleranz=1):
    ziehung_summe = sum(zahlen_liste)
    untere_grenze = mittelwert - toleranz * stdabw
    obere_grenze = mittelwert + toleranz * stdabw
    return untere_grenze <= ziehung_summe <= obere_grenze

def ist_statistisch_passend2(zahlen_liste, mittelwert, stdabw, toleranz=1):
    ziehung_summe = sum(zahlen_liste)
    untere_grenze = mittelwert - toleranz * stdabw
    obere_grenze = mittelwert + toleranz * stdabw
    return untere_grenze <= ziehung_summe <= obere_grenze

def zahl_in_letzten_drei(df, zahlen_liste):
    letzte_drei = df.head(4)
    gezogene_zahlen = set(zahlen_liste)
    gezogene_alt = set()
    for i in range(5):
        gezogene_alt.update(letzte_drei[f"Zahl {i+1}"].tolist())
    return len(gezogene_zahlen & gezogene_alt) > 0

def Superzahl_in_letzten_drei(df, zahlen_liste):
    letzte_drei = df.head(3)
    gezogene_zahlen = set(zahlen_liste)
    gezogene_alt = set()
    for i in range(2):
        gezogene_alt.update(letzte_drei[f"SuperZahl {i+1}"].tolist())
    return len(gezogene_zahlen & gezogene_alt) > 0

def finde_passende_kombi(df_neu, mittelwert, stdabw, mittelwert2, stdabw2, toleranz=1):
    versuche = 0
    while True:
        versuche += 1
        df_zufall = ziehe_eurojackpot()
        zahlen_liste = df_zufall[[f"Zahl {i+1}" for i in range(5)]].iloc[0].tolist()
        super_liste = df_zufall[[f"SuperZahl {i+1}" for i in range(2)]].iloc[0].tolist()
        
        if hat_nachbarn(zahlen_liste):
            continue
        if zahl_in_letzten_drei(df_neu, zahlen_liste):
            continue
        if Superzahl_in_letzten_drei(df_neu, super_liste):
            continue
        if not ist_statistisch_passend(zahlen_liste, mittelwert, stdabw, toleranz):
            continue
        if not ist_statistisch_passend2(super_liste, mittelwert2, stdabw2, toleranz):
            continue
        if kombi_schon_gezogen(df_neu, zahlen_liste):
            continue
        print(f"Gefunden nach {versuche} Versuchen.")
        return df_zufall

# --- Beispielaufruf ---
if __name__ == "__main__":
    passende_kombi = finde_passende_kombi(df_neu, mittelwert, stdabw, mittelwert2, stdabw2, toleranz=1)
    print("Gefundene passende Kombination:")
    print(passende_kombi)