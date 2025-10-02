
import pandas as pd
from datetime import datetime

def verifica_consistenza(fatture):
    errori = []
    codice_sicurezza = []
    num_prev = 0
    data_prev = datetime.strptime("01/01/2024", "%d/%m/%Y")
    for i, f in enumerate(fatture):
        num_corr = int(f["Numero Fattura"])
        data_corr = datetime.strptime(f["Data"], "%d/%m/%Y")
        if num_corr <= num_prev:
            errori.append(f"Incoerenza numero fattura alla riga {i+1}: {num_corr} <= {num_prev}")
            codice_sicurezza.append("ERRORE_NUM")
        num_prev = num_corr
        if data_corr < data_prev:
            errori.append(f"Incoerenza data alla riga {i+1}: {data_corr.strftime('%d/%m/%Y')} < {data_prev.strftime('%d/%m/%Y')}")
            codice_sicurezza.append("ERRORE_DATA")
        data_prev = data_corr
    return errori, codice_sicurezza

def crea_dataframe_fatture(lista_fatture):
    df = pd.DataFrame(lista_fatture)
    errori, codici = verifica_consistenza(lista_fatture)
    if errori:
        print("❌ ERRORI DI CONSISTENZA RILEVATI:")
        for e in errori:
            print(" -", e)
    else:
        print("✅ Nessun errore nei numeri o nelle date delle fatture.")
    return df

# Esempio di utilizzo (aggiungi qui le fatture da tutti i mesi man mano)
fatture = [
    {
        "Numero Fattura": "000001",
        "Data": "05/01/2024",
        "Cliente": "TERENZI CASHMERE",
        "Importo Totale": 180.01,
        "Imponibile": 147.55,
        "IVA": 32.46,
        "Articoli": ["NOLEGGIO"]
    },
    # ... continua con gli altri mesi/fatture
]

df_fatture = crea_dataframe_fatture(fatture)
print(df_fatture)
