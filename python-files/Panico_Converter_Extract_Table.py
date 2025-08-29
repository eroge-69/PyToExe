import camelot
import pandas as pd
import os

def converti_pdf_in_excel(file_pdf, file_excel):
    """
    Converte una tabella da un file PDF a un file Excel.

    Args:
        file_pdf (str): Il percorso del file PDF di input.
        file_excel (str): Il percorso del file Excel di output.
    """
    try:
        # Estrae le tabelle dal PDF
        tabelle = camelot.read_pdf(file_pdf, pages='3', flavor='lattice')

        if tabelle:
            # Seleziona la prima tabella trovata
            df = tabelle[0].df

            # Controlla se la tabella ha più di una riga (per evitare errori se c'è solo l'intestazione)
            if len(df) > 1:
                # Imposta la prima riga come intestazione del DataFrame
                df.columns = df.iloc[0]
                
                # Rimuove la riga dell'intestazione dal corpo del DataFrame
                df = df[1:].copy()
                
                # Rinomina le colonne con nomi più descrittivi
                df = df.rename(columns={
                    df.columns[0]: 'Data Operazione',
                    df.columns[1]: 'Codice di Riferimento',
                    df.columns[2]: 'Descrizione delle operazioni',
                    df.columns[3]: 'Importo divisa Estera',
                    df.columns[4]: 'Euro'
                })

                # Salva il DataFrame in un nuovo file Excel
                df.to_excel(file_excel, index=False)
                print(f" File Excel '{file_excel}' creato con successo!")
            else:
                print(f" File '{file_pdf}': la tabella non ha dati da convertire.")

        else:
            print(f" File '{file_pdf}': nessuna tabella trovata.")

    except Exception as e:
        print(f" Si è verificato un errore durante l'elaborazione del file '{file_pdf}': {e}")


if __name__ == "__main__":
    # Ottieni la directory corrente
    cartella_corrente = os.getcwd()

    # Itera su tutti i file nella cartella
    for nome_file in os.listdir(cartella_corrente):
        # Controlla se il file è un PDF
        if nome_file.endswith('.pdf'):
            # Costruisci il percorso completo del file PDF di input
            nome_file_pdf = os.path.join(cartella_corrente, nome_file)
            
            # Crea il nome del file Excel di output sostituendo '.pdf' con '.xlsx'
            nome_file_excel = os.path.splitext(nome_file)[0] + '.xlsx'
            
            print(f"\n--- Elaborazione del file: {nome_file} ---")
            
            # Chiama la funzione per convertire il PDF in Excel
            converti_pdf_in_excel(nome_file_pdf, nome_file_excel)