import os
import shutil

def carica_lista_file(file_input):
    try:
        with open(file_input, 'r', encoding='utf-8') as f:
            nomi_file = [line.strip() for line in f if line.strip()]
        return nomi_file
    except FileNotFoundError:
        print(f"File '{file_input}' non trovato.")
        return []

def cerca_e_copia_file(cartella_origine, cartella_destinazione, nomi_file):
    trovati = 0
    if not os.path.exists(cartella_destinazione):
        os.makedirs(cartella_destinazione)

    for root, _, files in os.walk(cartella_origine):
        for nome in files:
            if nome in nomi_file:
                sorgente = os.path.join(root, nome)
                destinazione = os.path.join(cartella_destinazione, nome)

                try:
                    shutil.copy2(sorgente, destinazione)
                    print(f"✔️ Copiato: {sorgente} ➡ {destinazione}")
                    trovati += 1
                except Exception as e:
                    print(f"Errore nella copia di {nome}: {e}")

    print(f"\nTotale file trovati e copiati: {trovati} su {len(nomi_file)}")

def main():
    print("=== Programma di Ricerca e Copia File ===")

    cartella_origine = input("Inserisci il percorso della cartella di origine: ").strip('" ')
    cartella_destinazione = input("Inserisci il percorso della cartella di destinazione: ").strip('" ')
    file_lista = input("Inserisci il percorso del file con la lista dei file (es. lista.txt): ").strip('" ')

    nomi_file = carica_lista_file(file_lista)

    if not nomi_file:
        print("Nessun file da cercare. Assicurati che il file sia corretto.")
        return

    cerca_e_copia_file(cartella_origine, cartella_destinazione, nomi_file)

if __name__ == "__main__":
    main()
