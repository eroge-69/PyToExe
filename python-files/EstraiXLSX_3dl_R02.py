import os
import re
import pandas as pd
import xlrd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Cartella di lavoro
folder_path = os.path.dirname(os.path.abspath(__file__))

# Trova tutti i file .xls
xls_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".xls")]

# Dati accumulati
data_combined = pd.DataFrame()
header_rows = []

# Estrazione da ciascun file
for filename in xls_files:
    file_path = os.path.join(folder_path, filename)

    try:
        wb = xlrd.open_workbook(file_path)
        sheet = wb.sheet_by_index(0)
        def get_cell_value(row, col): return sheet.cell_value(row-1, col-1)

        tipo_cem = get_cell_value(13, 2)     # B13
        raw_idmis = str(get_cell_value(39, 2))  # B39
        start = get_cell_value(42, 2)        # B42
        durata = get_cell_value(43, 2)       # B43
        numsample = get_cell_value(41, 2)    # B41

        # Pulisci IDMisStrum (solo numero, no #, no testo, no zeri iniziali)
        idmis_match = re.findall(r"\d+", raw_idmis)
        idmis_clean = str(int(idmis_match[0])) if idmis_match else "0"

        header_rows.append([tipo_cem, idmis_clean, start, durata, numsample])

        # Leggi foglio Data
        df = pd.read_excel(file_path, sheet_name="Data", engine="xlrd")
        df.insert(0, "IDMisStrum", idmis_clean)
        data_combined = pd.concat([data_combined, df], ignore_index=True)

    except Exception as e:
        print(f"Errore in {filename}: {e}")

# Timestamp per nome file
timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
output_filename = f"Excel_Accodato_{timestamp}.xlsx"
output_path = os.path.join(folder_path, output_filename)

# Scrittura file Excel
wb_out = Workbook()

# Foglio Data
ws_data = wb_out.active
ws_data.title = "Data"
for row in dataframe_to_rows(data_combined, index=False, header=True):
    ws_data.append(row)

# Foglio Header con intestazioni
ws_header = wb_out.create_sheet("Header")
ws_header.append(["TipoCEM", "IDMisStrum", "Start", "Durata", "NumSample"])
for row in header_rows:
    ws_header.append(row)

wb_out.save(output_path)
print(f"✅ File creato: {output_path}")
