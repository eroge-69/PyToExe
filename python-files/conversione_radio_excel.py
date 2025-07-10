
import pandas as pd
import os

EXCEL_FILE = "DATA STATS.xlsx"
CSV_FILE = "data.csv"

if not os.path.exists(EXCEL_FILE):
    print(f"File '{EXCEL_FILE}' non trovato nella cartella corrente.")
    input("Premi INVIO per uscire.")
    exit()

try:
    df = pd.read_excel(EXCEL_FILE, sheet_name="Foglio1", skiprows=2)
    blocchi = []
    for i in range(0, df.shape[1], 5):
        if pd.isna(df.iloc[0, i]): continue
        blocco = df.iloc[:, i:i+5].copy()
        blocco.columns = ['Ora','Ascolti **','VAR','SHOW','Data']
        blocco['Giorno'] = df.iloc[0, i]
        blocchi.append(blocco)
    df_finale = pd.concat(blocchi, ignore_index=True)
    df_finale[['Ora','Ascolti **','VAR','SHOW','Giorno']].dropna().to_csv(CSV_FILE, index=False)
    print(f"Conversione completata con successo. File generato: {CSV_FILE}")
except Exception as e:
    print("Errore durante la conversione:", e)

input("Premi INVIO per uscire.")
