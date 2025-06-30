
import pandas as pd
from datetime import datetime

# Carica il file Excel
file_path = "dati_completi.xlsx"
df = pd.read_excel(file_path)

# Rimuove eventuali caratteri errati e converte le virgole in punti per i numeri
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(',', '.').str.extract(r'([\d\.Ee+-]+)', expand=False)

# Conversione dei campi numerici dove possibile
df = df.apply(pd.to_numeric, errors='ignore')

# Calcolo dei valori medi per FileOrigine
df_mean = df.groupby("FileOrigine").mean(numeric_only=True).reset_index()

# Calcolo delle formule con i riferimenti ai campi
results = pd.DataFrame()
results["FileOrigine"] = df_mean["FileOrigine"]
results["Heff"] = df_mean.get("Meng_180_400")
results["HUVA"] = df_mean.get("Meng_315_400")
results["LB"] = df_mean.get("Meng_300_700")
results["EB"] = df_mean.get("Meng_300_700")
results["LR"] = df_mean.get("Meng_380_1400")
results["ER"] = df_mean.get("Meng_780_1400")
results["Hskin"] = df_mean.get("Meng_380_3000")

# Limiti di legge
limiti_legge = {
    "Heff": 30,
    "HUVA": 10000,
    "LB": 10000000,
    "EB": 100,
    "LR": 1000000,
    "ER": 100,
    "Hskin": 10000
}

# Aggiunge confronto con limiti
for col, limite in limiti_legge.items():
    results[f"{col}_limite"] = limite
    results[f"{col}_supera_limite"] = results[col] > limite

# Informazioni Lux
df_lux = df[["FileOrigine", "DATE", "Meng0", "UMeng0"]].copy()
df_lux.dropna(subset=["Meng0", "DATE"], inplace=True)
df_lux["Meng0"] = pd.to_numeric(df_lux["Meng0"], errors="coerce")
df_lux["DATE"] = pd.to_datetime(df_lux["DATE"], errors="coerce", dayfirst=True)

lux_info = df_lux.groupby("FileOrigine").agg(
    DataOraInizio=("DATE", "min"),
    LuxMedio=("Meng0", "mean"),
    UnitaLux=("UMeng0", lambda x: x.dropna().iloc[0] if not x.dropna().empty else None)
).reset_index()

# Unione dei dati
results = pd.merge(results, lux_info, on="FileOrigine", how="left")

# Estrae unità di misura aggiuntive
unit_columns = [col for col in df.columns if col.startswith("UMeng_") or col.startswith("UMeng")]
unit_info = df[["FileOrigine"] + unit_columns].copy()
unit_info_grouped = unit_info.groupby("FileOrigine").agg(
    {col: lambda x: x.dropna().iloc[0] if not x.dropna().empty else None for col in unit_columns}
).reset_index()

results = pd.merge(results, unit_info_grouped, on="FileOrigine", how="left")

# Salva il file finale
results.to_excel("risultati_completi_con_unita.xlsx", index=False)
print("✅ File salvato: risultati_completi_con_unita.xlsx")
