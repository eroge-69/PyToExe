import re
import tkinter as tk
from tkinter import filedialog
import os
import xlwt

# --- Finestra per selezione file ---
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Seleziona il file CAPTURE.TXT",
    filetypes=[("File di testo", "*.txt")],
)

if not file_path:
    print("❌ Nessun file selezionato. Operazione annullata.")
    exit()

# --- Legge il contenuto del file selezionato ---
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# --- Estrai blocchi evento ---
pattern = r"Evento\s+(\d+)/\d+\n(\d{2}:\d{2})\s+(\d{1,2}\.\d{1,2}\.\d{4})\nCentrale[^\n]*\n(.*?)(?=\nEvento|\Z)"
matches = re.findall(pattern, text, re.DOTALL)

# --- Prepara dati ---
header = ["Evento", "Data", "Ora", "Zona", "Indirizzo", "Descrizione"]
rows = []

for event_id, ora, data_evento, corpo in matches:
    zona = ""
    indirizzi = []
    descrizione_lines = []

    for line in corpo.strip().splitlines():
        original_line = line.strip()
        if not original_line:
            continue

        if not zona:
            zona_match = re.search(r"z:(\d+)", original_line)
            if zona_match:
                zona = zona_match.group(1)

        indir_matches = re.findall(r"(?:ind\.:?|ad\.:?|indirizzo)\s*(\d+\.\d+)", original_line)
        indirizzi.extend(indir_matches)

        clean_line = re.sub(r"z:\d+", "", original_line)
        clean_line = re.sub(r"(ind\.:?|ad\.:?|indirizzo)\s*\d+\.\d+", "", clean_line)
        clean_line = re.sub(r"\bguasto\s+\d+\b", "guasto", clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r"\bmanut\.ind\.\s+\d+\b", "Manutenzione", clean_line, flags=re.IGNORECASE)

        clean_line = clean_line.strip()
        if clean_line:
            descrizione_lines.append(clean_line)

    indirizzo = " | ".join(indirizzi)
    descrizione = " ".join(descrizione_lines)

    rows.append([event_id, data_evento, ora, zona, indirizzo, descrizione])

# --- Scrive file .xls ---
wb = xlwt.Workbook()
ws = wb.add_sheet('Eventi')

# Stile intestazioni
style_header = xlwt.easyxf('font: bold on; pattern: pattern solid, fore_colour gray25; align: horiz center')

# Scrivi intestazione
for col, col_name in enumerate(header):
    ws.write(0, col, col_name, style_header)

# Scrivi righe
for row_num, row_data in enumerate(rows, start=1):
    for col_num, cell in enumerate(row_data):
        ws.write(row_num, col_num, cell)

# Salva file
output_path = os.path.join(os.path.dirname(file_path), "eventi_strutturati.xls")
wb.save(output_path)

print(f"✅ File .xls generato correttamente: {output_path}")
