import os
import glob
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def rileva_separatore(file):
    """Prova a indovinare il separatore (virgola o punto e virgola)."""
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        prima_linea = f.readline()
        if ";" in prima_linea:
            return ";"
        return ","

def leggi_csv(file, sep, colonne=None):
    """Legge un CSV provando vari encoding."""
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    for enc in encodings:
        try:
            if colonne is None:
                return pd.read_csv(file, sep=sep, encoding=enc, engine="python")
            else:
                return pd.read_csv(file, sep=sep, skiprows=1, names=colonne, encoding=enc, engine="python")
        except Exception:
            continue
    raise ValueError(f"Impossibile leggere il file {os.path.basename(file)} con gli encoding provati.")

def main():
    print("=== MERGE FILE CSV ===")

    # Finestra per scegliere la cartella
    root = tk.Tk()
    root.withdraw()
    cartella = filedialog.askdirectory(title="Seleziona la cartella con i CSV")

    if not cartella:
        print("❌ Nessuna cartella selezionata.")
        input("Premi INVIO per uscire...")
        return

    print(f"📂 Cartella selezionata: {cartella}")

    # Trova tutti i file CSV nella cartella
    file_csv = glob.glob(os.path.join(cartella, "*.csv"))
    file_csv.sort()

    if not file_csv:
        print("❌ Nessun file CSV trovato nella cartella.")
        input("Premi INVIO per uscire...")
        return

    print("📑 File trovati:")
    for f in file_csv:
        print("   -", os.path.basename(f))

    dati = []
    colonne = None
    sep = rileva_separatore(file_csv[0])
    print(f"🔎 Separatore rilevato: '{sep}'")

    for i, file in enumerate(file_csv):
        try:
            if i == 0:
                df = leggi_csv(file, sep)
                colonne = df.columns
            else:
                df = leggi_csv(file, sep, colonne)

            # Controllo coerenza colonne
            if list(df.columns) != list(colonne):
                print(f"⚠️ ATTENZIONE: {os.path.basename(file)} ha colonne diverse!")

            dati.append(df)

        except Exception as e:
            print(f"❌ Errore nel file {os.path.basename(file)}: {e}")

    if not dati:
        print("❌ Nessun dato valido trovato.")
        input("Premi INVIO per uscire...")
        return

    # Concatena tutti i dataframe
    df_finale = pd.concat(dati, ignore_index=True)

    # Nome file con data odierna
    data_oggi = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(cartella, f"mergingcsv_{data_oggi}.csv")

    # Evita sovrascrittura
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(cartella, f"mergingcsv_{data_oggi}_{counter}.csv")
        counter += 1

    # Salva il risultato
    df_finale.to_csv(output_file, index=False, encoding="utf-8-sig", sep=sep)

    print(f"✅ Merging completato! File salvato come: {output_file}")
    input("Premi INVIO per chiudere...")

if __name__ == "__main__":
    main()


