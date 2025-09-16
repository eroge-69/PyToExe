import os
import unicodedata
import re

DRY_RUN = False

def normalizza_nome(nome, is_file=True):
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode()

    if is_file:
        if "." in nome:
            indice_punto = nome.rfind(".")
            nome_base = nome[:indice_punto]
            estensione = nome[indice_punto:]
        else:
            nome_base = nome
            estensione = ""

        nome_base = nome_base.replace(".", "")  # Rimuove punti nel nome file
        nome_base = (
            nome_base.replace(" ", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("°", "")
            .replace("+", "-")
            .replace("(", "")
            .replace(")", "")
        )

        nome_base = re.sub(r'_+', '_', nome_base)
        nome_base = nome_base.replace("_-_", "-")
        nome_base = nome_base.strip('_')

        return nome_base + estensione

    else:
        nome = nome.replace(".", "")  # Rimuove punti anche nelle cartelle
        nome = (
            nome.replace(" ", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("°", "")
            .replace("+", "-")
            .replace("(", "")
            .replace(")", "")
        )

        nome = re.sub(r'_+', '_', nome)
        nome = nome.replace("_-_", "-")
        nome = nome.strip('_')

        return nome

def genera_nome_unico(percorso_base, nome_base, estensione=""):
    """
    Genera un nuovo nome evitando conflitti.
    Se esiste già, aggiunge -2, -3, ecc.
    """
    nuovo_nome = nome_base + estensione
    contatore = 2
    while os.path.exists(os.path.join(percorso_base, nuovo_nome)):
        nuovo_nome = f"{nome_base}-{contatore}{estensione}"
        contatore += 1
    return nuovo_nome

def rinomina_cartelle_recursively(cartella_base):
    tutte_cartelle = []
    for radice, cartelle, _ in os.walk(cartella_base):
        for c in cartelle:
            percorso_attuale = os.path.join(radice, c)
            tutte_cartelle.append(percorso_attuale)

    tutte_cartelle.sort(key=lambda x: -x.count(os.sep))

    for percorso in tutte_cartelle:
        cartella_padre = os.path.dirname(percorso)
        nome_vecchio = os.path.basename(percorso)
        nome_nuovo = normalizza_nome(nome_vecchio, is_file=False)
        nuovo_percorso = os.path.join(cartella_padre, nome_nuovo)

        if nome_nuovo != nome_vecchio:
            if os.path.exists(nuovo_percorso):
                nome_unico = genera_nome_unico(cartella_padre, nome_nuovo, "")
                nuovo_percorso = os.path.join(cartella_padre, nome_unico)
                if DRY_RUN:
                    print(f"[ALERT - CONFLITTO CARTELLA] {percorso} → {nuovo_percorso}")
                else:
                    os.rename(percorso, nuovo_percorso)
                    print(f"[ALERT - CONFLITTO RISOLTO CARTELLA] {percorso} → {nuovo_percorso}")
            else:
                if DRY_RUN:
                    print(f"[DRY RUN - CARTELLA] {percorso} → {nuovo_percorso}")
                else:
                    os.rename(percorso, nuovo_percorso)
                    print(f"[CARTELLA] {percorso} → {nuovo_percorso}")

def rinomina_file_recursively(cartella_base):
    for radice, _, files in os.walk(cartella_base):
        for nome_file in files:
            percorso_attuale = os.path.join(radice, nome_file)
            nome_nuovo = normalizza_nome(nome_file, is_file=True)
            nuovo_percorso = os.path.join(radice, nome_nuovo)

            if nome_nuovo != nome_file:
                if os.path.exists(nuovo_percorso):
                    nome_base, estensione = os.path.splitext(nome_nuovo)
                    nome_unico = genera_nome_unico(radice, nome_base, estensione)
                    nuovo_percorso = os.path.join(radice, nome_unico)
                    if DRY_RUN:
                        print(f"[ALERT - CONFLITTO FILE] {percorso_attuale} → {nuovo_percorso}")
                    else:
                        os.rename(percorso_attuale, nuovo_percorso)
                        print(f"[ALERT - CONFLITTO RISOLTO FILE] {percorso_attuale} → {nuovo_percorso}")
                else:
                    if DRY_RUN:
                        print(f"[DRY RUN - FILE] {percorso_attuale} → {nuovo_percorso}")
                    else:
                        os.rename(percorso_attuale, nuovo_percorso)
                        print(f"[FILE] {percorso_attuale} → {nuovo_percorso}")

if __name__ == "__main__":
    scelta = input("Modalità simulata? (s/n): ").strip().lower()
    if scelta == "s":
        DRY_RUN = True
    else:
        DRY_RUN = False

    print(f"Modalità simulata = {DRY_RUN}\n")

    cartella_script = os.path.dirname(os.path.abspath(__file__))
    rinomina_cartelle_recursively(cartella_script)
    rinomina_file_recursively(cartella_script)
