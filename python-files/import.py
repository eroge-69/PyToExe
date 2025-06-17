import csv
import os
import shutil

csv_path = r"C:\mexal_cli\IMPORT.csv"
log_mancanti = r"C:\DISEGNI\disegni_mancanti.txt"
pdf_source_folder = r"Z:\\"
pdf_dest_folder = r"C:\DISEGNI"

# Controlla se la cartella di destinazione esiste, altrimenti la crea
if not os.path.exists(pdf_dest_folder):
    os.makedirs(pdf_dest_folder)

pdf_files = {f.lower(): f for f in os.listdir(pdf_source_folder)}

with open(csv_path, mode="r", encoding="cp1252") as csv_file, \
     open(log_mancanti, mode="w", encoding="cp1252") as mancanti_file:

    reader = csv.reader(csv_file, delimiter=";")
    next(reader)  # Salta intestazione

    for row in reader:
        if len(row) > 2:
            codice = row[2].lstrip()[:11]
            pdf_filename_lower = f"{codice}.pdf".lower()

            if pdf_filename_lower in pdf_files:
                source_path = os.path.join(pdf_source_folder, pdf_files[pdf_filename_lower])
                shutil.copy(source_path, pdf_dest_folder)
            else:
                mancanti_file.write(codice + "\n")

print("Elaborazione completata. PDF disponibili copiati, disegni mancanti registrati.")
