import os
import shutil

VALID_EXTENSIONS = ['.jpg', '.jpeg']

def pulisci_cartella(cartella):
    nomi_base_valide = set()

    # Salta la cartella _CANCELLARE
    if os.path.basename(cartella).lower() == "_cancellare":
        return

    # Crea cartella _CANCELLARE se non esiste
    cartella_cancellare = os.path.join(cartella, "_CANCELLARE")
    os.makedirs(cartella_cancellare, exist_ok=True)

    # Primo passaggio: raccoglie i nomi base dei file .jpg/.jpeg
    for file in os.listdir(cartella):
        percorso = os.path.join(cartella, file)
        if os.path.isfile(percorso):
            nome, est = os.path.splitext(file)
            if est.lower() in VALID_EXTENSIONS:
                nomi_base_valide.add(nome.lower())

    # Secondo passaggio: sposta file non validi
    for file in os.listdir(cartella):
        percorso = os.path.join(cartella, file)
        if os.path.isfile(percorso):
            nome, est = os.path.splitext(file)
            if est.lower() not in VALID_EXTENSIONS and nome.lower() not in nomi_base_valide:
                destinazione = os.path.join(cartella_cancellare, file)
                print(f"Sposto: {file} → _CANCELLARE")
                shutil.move(percorso, destinazione)

def esegui_su_cartelle(path_radice):
    for radice, cartelle, _ in os.walk(path_radice):
        # Ignora la cartella _CANCELLARE
        cartelle[:] = [c for c in cartelle if c.lower() != "_cancellare"]
        pulisci_cartella(radice)

if __name__ == "__main__":
    percorso_base = input("Inserisci il percorso della cartella da analizzare: ").strip()
    if os.path.isdir(percorso_base):
        esegui_su_cartelle(percorso_base)
        print("\n✔️ Operazione completata.")
    else:
        print("❌ Percorso non valido.")
