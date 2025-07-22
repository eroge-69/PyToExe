
import pandas as pd
from datetime import datetime, timedelta

# --- IMPOSTAZIONI ---
# NOME DEL FILE DI INPUT: Assicurati che il tuo file CSV si chiami così
# e che si trovi nella stessa cartella di questo script.
NOME_FILE_INPUT = 'promemoria anna.xlsx - Foglio1.csv'

# NOME DEL FILE DI OUTPUT: Questo è il nome del nuovo file che verrà creato.
NOME_FILE_OUTPUT = 'scadenze_con_avvisi.csv'

# GIORNI DI PREAVVISO: Imposta quanti giorni prima della scadenza vuoi essere avvisato.
# Corrisponde a "circa un mese".
GIORNI_PREAVVISO = 30
# --------------------


def analizza_scadenze():
    """
    Legge un file CSV con una struttura a blocchi, analizza le scadenze 
    e produce un nuovo file CSV con una colonna di stato per gli avvisi.
    """
    try:
        # Legge le prime due righe per capire la struttura (aziende e header)
        with open(NOME_FILE_INPUT, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("ERRORE: Il file CSV è vuoto.")
            return

        header_aziende = lines[0].strip().split(',')
        
        # Estrae i nomi delle aziende. Si assume che ogni nome sia seguito da colonne vuote.
        nomi_aziende = [name.strip() for name in header_aziende if 'Nome Azienda' in name]
        num_blocchi = len(nomi_aziende)

        # Legge i dati principali usando pandas, saltando le prime due righe di intestazione
        df = pd.read_csv(NOME_FILE_INPUT, header=None, skiprows=2)

        lista_record = []
        # Itera su ogni blocco di dati (un blocco per ogni azienda)
        for i in range(num_blocchi):
            nome_azienda_corrente = nomi_aziende[i]
            colonna_inizio = i * 4 # Ogni blocco è largo 4 colonne

            # Seleziona le 3 colonne di dati per il blocco corrente
            df_blocco = df.iloc[:, colonna_inizio:colonna_inizio+3]
            df_blocco.columns = ['Nome corsista', 'Nome corso', 'Scadenza']
            df_blocco['Nome Azienda'] = nome_azienda_corrente
            
            # Rimuovi le righe vuote
            df_blocco.dropna(subset=['Nome corsista'], inplace=True)
            
            if not df_blocco.empty:
                lista_record.append(df_blocco)

        if not lista_record:
            print("Non sono stati trovati record validi nel file.")
            return
            
        # Unisce tutti i blocchi in un unico DataFrame
        df_finale = pd.concat(lista_record, ignore_index=True)
        
        # --- Analisi delle scadenze ---
        # Converte la colonna 'Scadenza' in formato data
        df_finale['Scadenza_dt'] = pd.to_datetime(df_finale['Scadenza'], dayfirst=True, errors='coerce')
        
        # Rimuove le righe dove la data non è valida
        df_finale.dropna(subset=['Scadenza_dt'], inplace=True)

        oggi = datetime.now()
        data_limite = oggi + timedelta(days=GIORNI_PREAVVISO)
        
        # Aggiunge la colonna 'Stato' per gli avvisi
        df_finale['Stato'] = ''
        
        # Imposta lo stato per le scadenze imminenti e quelle passate
        df_finale.loc[df_finale['Scadenza_dt'] < oggi, 'Stato'] = 'SCADUTO'
        df_finale.loc[(df_finale['Scadenza_dt'] >= oggi) & (df_finale['Scadenza_dt'] <= data_limite), 'Stato'] = 'IN SCADENZA'
        
        # Seleziona e riordina le colonne per il file finale
        output_df = df_finale[['Nome Azienda', 'Nome corsista', 'Nome corso', 'Scadenza', 'Stato']]

        # Salva il risultato in un nuovo file CSV
        output_df.to_csv(NOME_FILE_OUTPUT, index=False, encoding='utf-8-sig')
        
        print(f"Fatto! Il file '{NOME_FILE_OUTPUT}' è stato creato con successo.")

    except FileNotFoundError:
        print(f"ERRORE: File non trovato! Assicurati che '{NOME_FILE_INPUT}' sia nella stessa cartella dello script.")
    except Exception as e:
        print(f"Si è verificato un errore inaspettato: {e}")


# Esegue la funzione principale dello script
if __name__ == "__main__":
    analizza_scadenze()