import pandas as pd

def cerca_componente_in_excel(file_excel, query):
    """
    Cerca un componente in un file Excel basato su codice o descrizione.

    Args:
        file_excel (str): Il percorso del file Excel (es. 'catalogo.xlsx').
        query (str): Il termine di ricerca.

    Returns:
        pandas.DataFrame: Un DataFrame contenente i risultati della ricerca.
    """
    try:
        # Legge il file Excel in un DataFrame di pandas
        df = pd.read_excel(file_excel)

        # Converte la query in minuscolo per una ricerca case-insensitive
        query_minuscola = query.lower()

        # Funzione di ricerca che controlla se la query è nel codice o nella descrizione
        # `axis=1` applica la funzione riga per riga
        risultati = df[df.apply(
            lambda riga: query_minuscola in str(riga['Codice']).lower() or
                         query_minuscola in str(riga['Descrizione']).lower(),
            axis=1
        )]
        
        return risultati
    except FileNotFoundError:
        print(f"Errore: Il file '{file_excel}' non è stato trovato.")
        return None
    except KeyError:
        print("Errore: Assicurati che le colonne si chiamino 'Codice' e 'Descrizione'.")
        return None

# --- Esempio di utilizzo ---
if __name__ == "__main__":
    nome_file = 'catalogo_componenti.xlsx'  # Cambia con il nome del tuo file
    
    # Richiedi all'utente di inserire un termine di ricerca
    query_utente = input("Inserisci il codice o una parte della descrizione del componente: ")
    
    # Esegui la ricerca nel file Excel
    risultati_ricerca = cerca_componente_in_excel(nome_file, query_utente)
    
    # Stampa i risultati
    if risultati_ricerca is not None:
        if not risultati_ricerca.empty:
            print("\nRisultati trovati:")
            print(risultati_ricerca.to_string(index=False))  # Stampa senza l'indice
        else:
            print("\nNessun componente trovato con il termine di ricerca inserito.")