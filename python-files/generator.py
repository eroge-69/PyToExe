import os
import sys
import shutil
import pandas as pd
from openpyxl import load_workbook
from math import ceil
from tqdm import tqdm
import logging

# --- INIZIALIZZAZIONE ---
SCRIPT_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, '_Template.xlsx')
EXCELCOOP_PATH = os.path.join(SCRIPT_DIR, 'ExcelCOOP.xlsx')
ARIANNA_PATH = os.path.join(SCRIPT_DIR, 'Arianna.xlsx')

# Log setup
log_path = os.path.join(SCRIPT_DIR, 'log_generazione.txt')
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- INPUT UTENTE ---
print("📂 Inserisci prefisso per la segnatura (es. codice fondo):")
prefix = input("> ")
print("📂 Inserisci nome cartella output (verrà creata se non esiste):")
out_folder_name = input("> ")
OUTPUT_BASE_PATH = os.path.join(SCRIPT_DIR, out_folder_name)
os.makedirs(OUTPUT_BASE_PATH, exist_ok=True)

# --- CARICAMENTO DATI ---
print("📄 Caricamento file Excel...")
try:
    df_excel = pd.read_excel(EXCELCOOP_PATH)
    df_arianna = pd.read_excel(ARIANNA_PATH, usecols=[11, 12, 13])
    df_arianna.columns = ['L', 'M', 'N']
except Exception as e:
    logging.error("Errore caricamento file Excel: %s", str(e))
    sys.exit("Errore nel caricamento dei file Excel.")

# --- CREAZIONE ESTRAZIONE ---
df_excel['concatena'] = df_excel.iloc[:, 4].astype(str) + '/' + df_excel.iloc[:, 5].astype(str)
df_unique = df_excel[['concatena']].drop_duplicates().copy()
df_unique['A4_Rif'] = df_unique['concatena'].map(dict(zip(df_arianna['L'], df_arianna['N'])))
df_unique['Segnatura'] = prefix + '_' + df_unique['concatena']
df_unique['Segnatura'] = df_unique['Segnatura'].str.replace('/', '', regex=False)

# --- DIVIDI IN BLOCCHI DA 100 ---
chunks = [df_unique[i:i + 100] for i in range(0, df_unique.shape[0], 100)]

# --- CICLO PRINCIPALE ---
for idx, chunk in enumerate(tqdm(chunks, desc="Generazione blocchi"), start=1):
    try:
        wb = load_workbook(TEMPLATE_PATH)
        collezione_ws = wb['Collezione']
        parte_ws = wb['Parte di collezione']

        for row in collezione_ws['C2:C101'] + collezione_ws['E2:E101']:
            for cell in row:
                cell.value = None
        for row in parte_ws['A2:D101']:
            for cell in row:
                cell.value = None
        parte_ws['A1'] = 'File'
        parte_ws['B1'] = "Tipologia della collezione"
        parte_ws['C1'] = "Segnatura/ID"
        parte_ws['D1'] = "Nome"

        for i, (_, row) in enumerate(chunk.iterrows(), start=2):
            collezione_ws[f"C{i}"] = row['Segnatura']
            collezione_ws[f"E{i}"] = row['A4_Rif']

        matched_rows = df_excel[df_excel['concatena'].isin(chunk['concatena'])]
        for i, (_, row) in enumerate(matched_rows.iterrows(), start=2):
            parte_ws[f"C{i}"] = prefix + '_' + row['concatena'].replace('/', '')
            parte_ws[f"D{i}"] = row.iloc[1]
            parte_ws[f"B{i}"] = "Documento d'archivio"
            parte_ws[f"A{i}"] = f"/{prefix}_{idx}/{row.iloc[1]}"

        dir_path = os.path.join(OUTPUT_BASE_PATH, f"{prefix}_{idx}")
        os.makedirs(dir_path, exist_ok=True)

        for _, row in matched_rows.iterrows():
            filename = str(row.iloc[1])
            src_folder = os.path.join(SCRIPT_DIR, filename)
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dir_path, filename)
            try:
                shutil.copy(src_path, dst_path)
            except Exception as e:
                logging.warning(f"File mancante o errore copia: {filename} - {str(e)}")

        final_name = os.path.join(OUTPUT_BASE_PATH, f"{prefix}_{idx}.xlsx")
        wb.save(final_name)
        wb.close()
        logging.info(f"Creato: {final_name}")

    except Exception as e:
        logging.error("Errore blocco %s: %s", idx, str(e))

print("✅ Operazione completata. Vedi log_generazione.txt per i dettagli.")
