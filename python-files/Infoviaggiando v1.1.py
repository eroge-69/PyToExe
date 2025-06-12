"""
Script: Infoviaggiando

Descrizione:
Questo script scarica e analizza in tempo reale il contenuto della sezione "Traffico in tempo reale" del sito https://infoviaggiando.it/it,
relativa alla situazione del traffico autostradale.

Lo script:
- Estrae tutte le notizie contenute nel sito
- Corregge automaticamente le diciture errate di tratta "A4 TORINO - TRIESTE" in base agli svincoli presenti nel testo
- Riclassifica correttamente i tratti A4 come:
    - A4 BRESCIA - PADOVA
    - A4 PADOVA - VENEZIA
    - A4 PASSANTE DI MESTRE
    - A4 VENEZIA - TRIESTE (default se non riconosciuto alcuno svincolo noto)
- Corregge le direzioni errate in:
    - MILANO (anziché Torino)
    - VENEZIA (anziché Torino, per la VENEZIA - TRIESTE)
    - TRIESTE (rimane invariata)
- Supporta due modalità di esecuzione selezionabili con la variabile `modalita`:
    - `modalita = 0` → stampa tutte le notizie corrette normalmente
    - `modalita = 1` → separa le notizie in:
        • TEMPO REALE (es. Incidente, Code, Panne, ecc.)
        • NON TEMPO REALE (es. lavori, vento forte, ecc.)
      e le ordina secondo una priorità:

Priorità "Tempo reale" per tipo evento (ordine decrescente):
    1. Incidente
    2. Panne (veicolo o mezzo pesante)
    3. Avaria (veicolo o mezzo pesante)
    4. Lavori
    5. Traffico
    6. Notizie generiche senza causa chiara

Priorità descrittiva all'interno del tipo evento:
    1. Tratto chiuso
    2. Svincolo chiuso
    3. Code
    4. Code, in uscita
    5. Code, in entrata
    6. Code a tratti
    7. Rallentato con code
    8. Rallentato
    9. Altro

Lo script può essere esteso per salvare i risultati su file o esportarli in formato strutturato (CSV/JSON).
"""


import requests
import re
from bs4 import BeautifulSoup

# Modalità di esecuzione:
# 0 = stampa tutto normalmente
# 1 = separazione 'tempo reale'
modalita = 1

svincolo_tratte = {
    "BRESCIA EST": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "BRESCIA CENTRO": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "DESENZANO": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "SIRMIONE": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "PESCHIERA": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "SOMMACAMPAGNA": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "ALLACCIAMENTO A22 BRENNERO-MODENA": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "VERONA SUD": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "VERONA EST": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "SOAVE": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "MONTEBELLO": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "MONTECCHIO": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "VICENZA OVEST": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "VICENZA EST": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "ALLACCIAMENTO A31 VICENZA-PIOVENE R.": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "GRISIGNANO": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "PADOVA OVEST": ("A4 BRESCIA - PADOVA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "PADOVA EST": ("A4 PADOVA - VENEZIA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "DOLO": ("A4 PADOVA - VENEZIA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
    "MIRANO": ("A4 PADOVA - VENEZIA", {"Torino": "MILANO", "Trieste": "VENEZIA"}),
}

svincoli_passante = [
    "A4/A57 OVEST", "SPINEA", "MARTELLAGO SCORZE'", "PREGANZIOL", "A4/A57 EST"
]

def correggi_titolo(testo):
    if not testo.startswith("A4 TORINO - TRIESTE"):
        return testo
    direzione_originale = None
    if "direzione Torino" in testo:
        direzione_originale = "Torino"
    elif "direzione Trieste" in testo:
        direzione_originale = "Trieste"
    for svincolo in svincoli_passante:
        if svincolo in testo:
            testo = testo.replace("A4 TORINO - TRIESTE", "A4 PASSANTE DI MESTRE")
            testo = re.sub(r"direzione\s+est", "direzione TRIESTE", testo, flags=re.IGNORECASE)
            testo = re.sub(r"direzione\s+ovest", "direzione MILANO", testo, flags=re.IGNORECASE)
            if direzione_originale:
                nuova = "MILANO" if direzione_originale == "Torino" else "TRIESTE"
                testo = re.sub(rf"direzione\s+{direzione_originale}", f"direzione {nuova}", testo, flags=re.IGNORECASE)
            return testo
    for svincolo, (tratta, direzioni) in svincolo_tratte.items():
        if svincolo in testo:
            nuova = direzioni.get(direzione_originale, direzione_originale)
            testo = testo.replace("A4 TORINO - TRIESTE", tratta)
            if direzione_originale and nuova:
                testo = re.sub(rf"direzione\s+{direzione_originale}", f"direzione {nuova}", testo, flags=re.IGNORECASE)
            return testo
    testo = testo.replace("A4 TORINO - TRIESTE", "A4 VENEZIA - TRIESTE")
    testo = re.sub(r"direzione\s+torino", "direzione VENEZIA", testo, flags=re.IGNORECASE)
    testo = re.sub(r"direzione\s+trieste", "direzione TRIESTE", testo, flags=re.IGNORECASE)
    return testo

def priorita(testo):
    testo_l = testo.lower()

    if "incidente" in testo_l:
        categoria = 1
    elif "in panne" in testo_l or "in avaria" in testo_l:
        categoria = 2
    elif "code" in testo_l:
        categoria = 3
    elif "traffico" in testo_l:
        categoria = 4
    elif "lavori" in testo_l:
        categoria = 5
    else:
        categoria = 6

    if "tratto chiuso" in testo_l:
        sotto = 1
    elif "svincolo chiuso" in testo_l:
        sotto = 2
    elif "code" in testo_l and "in uscita" not in testo_l and "in entrata" not in testo_l and "a tratti" not in testo_l and "rallentato" not in testo_l:
        sotto = 3
    elif "code, in uscita" in testo_l:
        sotto = 4
    elif "code, in entrata" in testo_l:
        sotto = 5
    elif "code a tratti" in testo_l:
        sotto = 6
    elif "rallentato con code" in testo_l:
        sotto = 7
    elif "traffico intenso" in testo_l:
        sotto = 8
    elif "rallentato" in testo_l:
        sotto = 9
    else:
        sotto = 10

    return (categoria, sotto)

url = "https://infoviaggiando.it/it"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
ticker_div = soup.find("div", class_="c-cartografia_panel c-cartografia_panel--center c-cartografia_panel--green c-newsticker js-newstickereventi")

if ticker_div:
    items = ticker_div.find_all("span", class_="c-newsticker__item")
    if modalita == 0:
        for item in items:
            testo = item.get_text(strip=True)
            print(correggi_titolo(testo))
    else:
        tempo_reale, non_tempo = [], []
        chiavi = ["traffico rallentato con code", "traffico rallentato", "traffico intenso",
                  "code", "incidente", "veicolo in panne", "mezzo pesante in panne",
                  "veicolo in avaria", "mezzo pesante in avaria"]
        for item in items:
            testo = correggi_titolo(item.get_text(strip=True))
            if any(k in testo.lower() for k in chiavi):
                tempo_reale.append(testo)
            else:
                non_tempo.append(testo)
        print("=== TEMPO REALE ===")
        for r in sorted(tempo_reale, key=priorita): print(r)
        print("\n=== NON TEMPO REALE ===")
        for r in non_tempo: print(r)
else:
    print("Blocco ticker non trovato.")
