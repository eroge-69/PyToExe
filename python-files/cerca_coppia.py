import pandas as pd
import os

# Percorso del file Excel sulla rete
percorso_rete = r"\\172.25.0.108\FTP_Serraggi\varie\Nuova cartella (3)\tabella.xlsx"

# Verifica se il file esiste
if not os.path.exists(percorso_rete):
    print("⚠️ File non trovato. Controlla il percorso.")
    exit()

# Leggi il file Excel
try:
    df = pd.read_excel(percorso_rete)
except Exception as e:
    print(f"Errore nella lettura del file: {e}")
    exit()

# Pulisci le colonne da eventuali spazi indesiderati
df = df.applymap(lambda x: str(x).strip() if pd.notna(x) else "")

# Verifica colonne necessarie
if 'Chiave' not in df.columns or 'Coppia' not in df.columns:
    print("⚠️ Colonne 'Chiave' o 'Coppia' mancanti.")
    exit()

# Rimuovi spazi nella colonna chiave
df['Chiave'] = df['Chiave'].str.replace(" ", "")

# Estrazione automatica della classe di resistenza completa
def trova_classe_completa(input_num, df):
    input_num = input_num.strip()
    # Estrai tutte le classi nel formato "X,Y / Z" dalla colonna Chiave
    classi_presenti = df['Chiave'].str.extract(r'^([^/]+/[^\d]*)')[0].dropna().unique()
    for classe in classi_presenti:
        parte_intera = classe.split(',')[0]
        if parte_intera == input_num:
            return classe.strip()
    return input_num  # Se non trova nulla, restituisce l’input originale

print("✅ File caricato correttamente.\n")

# Ciclo infinito finché l'utente non vuole uscire
while True:
    print(">>> Inserisci i valori per la ricerca (scrivi 'exit' per uscire):")

    classe_resistenza = input("Classe di resistenza (che sia un dado o vite scrivere sempre es. 4,8 / 5,8 / 6,8 / 8,8 / 10,9 / 12,9): ").strip()
    if classe_resistenza.lower() == 'exit':
        break

    categoria = input("Categoria (es. 1, 2, 3): ").strip()
    if categoria.lower() == 'exit':
        break

    filetto = input("Filetto (es. 8x1,00): ").strip()
    if filetto.lower() == 'exit':
        break

    attrito = input("Attrito (es. II, VI, VII oppure lascia vuoto): ").strip()
    if attrito.lower() == 'exit':
        break

    # Applica conversione classe (es. "10" → "10,9 / 10")
    classe_resistenza = trova_classe_completa(classe_resistenza, df)
    print(f"[DEBUG] Classe interpretata: {classe_resistenza}")

    # Costruzione chiave finale
    chiave = (classe_resistenza + categoria + filetto + attrito).replace(" ", "")
    print(f"[DEBUG] Chiave generata: {chiave}")

    # Ricerca della chiave
    riga = df[df['Chiave'] == chiave]

    if not riga.empty:
        coppia = riga.iloc[0]['Coppia']
        print(f"✅ Coppia trovata: {coppia} Nm\n")
    else:
        print("❌ Nessuna corrispondenza trovata. Controlla i dati inseriti.\n")
