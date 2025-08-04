from datetime import datetime, timedelta
import investpy
import pandas as pd
import os

# Percorso del file CSV nella stessa cartella
csv_file = os.path.join(os.path.dirname(__file__), 'ftse_banks_daily.csv')

# Oggi in formato DD/MM/YYYY
oggi = datetime.today().strftime('%d/%m/%Y')
oggi_dt = datetime.today()

# Leggi il file CSV o crealo se non esiste
if os.path.exists(csv_file):
    dati = pd.read_csv(csv_file)
    ultima_data_str = dati['Date'].iloc[-1]
    ultima_data_dt = datetime.strptime(ultima_data_str, '%d/%m/%Y') + timedelta(days=1)
else:
    dati = pd.DataFrame(columns=['Date', 'Close'])
    ultima_data_dt = datetime.strptime('01/01/2024', '%d/%m/%Y')  # Prima data arbitraria

# Ciclo per ogni giorno mancante
data_corrente = ultima_data_dt

while data_corrente <= oggi_dt:
    data_str = data_corrente.strftime('%d/%m/%Y')
    try:
        data = investpy.get_index_historical_data(
            index='FTSE Italia All Share Banks',
            country='italy',
            from_date=data_str,
            to_date=data_str
        )
        close_value = data['Close'].iloc[0]
        nuova_riga = pd.DataFrame([[data_str, close_value]], columns=['Date', 'Close'])
        nuova_riga.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
        print(f"Aggiunto {data_str}: {close_value:.2f}")
    except Exception as e:
        print(f"Nessun dato per {data_str} - mercato chiuso?")
    data_corrente += timedelta(days=1)

print("Aggiornamento completato ✅")
input("Premi Invio per chiudere...")
