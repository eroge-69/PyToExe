import csv

# Nome del file da leggere
nome_file = 'dati.csv'

try:
    # Apre il file in modalità di lettura ('r')
    with open(nome_file, mode='r', newline='', encoding='utf-8') as file_csv:
        # Crea un oggetto lettore (reader)
        lettore_csv = csv.reader(file_csv)
        
        # Legge l'intestazione
        intestazione = next(lettore_csv)
        print("Intestazione:", intestazione)
        
        # Legge il resto delle righe
        print("\nDati:")
        for riga in lettore_csv:
            print(riga)
            
except FileNotFoundError:
    print(f"Errore: Il file '{nome_file}' non è stato trovato.")
except Exception as e:
    print(f"Si è verificato un errore: {e}")