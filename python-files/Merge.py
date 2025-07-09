import os

HEADER_LINES_TO_DELETE = [
    "LIVELLO",
    "ID",
    "OPERAZIONE"
]

HEADERS_TO_DEDUPLICATE = [
    "GRAVITA'",
    "ADESIONE",
    "ERRORE"
]

def estrai_blocco_dati(filepath):
    with open(filepath, 'r', encoding='latin-1') as f:
        righe = f.readlines()

    blocco = []
    i = 0

    while i < len(righe) and 'LIVELLO' not in righe[i]:
        i += 1

    if i >= len(righe):
        return []

    blocco.extend(righe[i:i+6])
    i += 6

    while i < len(righe):
        riga = righe[i].strip()
        if riga.startswith('*'):
            break
        if not set(riga).issubset(set('- ')):
            blocco.append(righe[i])
        i += 1

    return blocco

def pulisci_output(path_file):
    with open(path_file, 'r', encoding='latin-1') as f:
        righe = f.readlines()

    pulite = []
    intestazioni_trovate = set()

    for riga in righe:
        testo = riga.strip()

        if not testo:
            continue
        if testo.startswith('*'):
            continue
        if set(testo).issubset(set('- ')):
            continue
        if any(testo.startswith(prefix) for prefix in HEADER_LINES_TO_DELETE):
            continue
        if any(testo.startswith(h) for h in HEADERS_TO_DEDUPLICATE):
            header = next(h for h in HEADERS_TO_DEDUPLICATE if testo.startswith(h))
            if header in intestazioni_trovate:
                continue
            intestazioni_trovate.add(header)

        pulite.append(riga)

    with open(path_file, 'w', encoding='latin-1') as f:
        f.writelines(pulite)

def main():
    cartella = os.path.dirname(os.path.abspath(__file__))
    nome_output = 'output_merged.txt'
    percorso_output = os.path.join(cartella, nome_output)

    files_txt = sorted([
        f for f in os.listdir(cartella)
        if f.endswith('.txt') and f != nome_output
    ])

    risultato = []
    for file in files_txt:
        blocco = estrai_blocco_dati(os.path.join(cartella, file))
        if blocco:
            risultato.extend(blocco)
            risultato.append('\n')

    with open(percorso_output, 'w', encoding='latin-1') as f:
        f.writelines(risultato)

    pulisci_output(percorso_output)

    print(f"✅ File pronto: {percorso_output}")


if __name__ == "__main__":
    main()