import pytesseract
from pdf2image import convert_from_path
import pandas as pd

# PDF-Datei
pdf_path = '102500013-0_AF_03443.pdf'

# PDF in Bilder umwandeln
images = convert_from_path(pdf_path)

# OCR auf Bilder anwenden
ocr_text = [pytesseract.image_to_string(img) for img in images]

# Tabellen aus OCR-Text extrahieren
tables = []
for page in ocr_text:
    lines = page.split('\n')
    table = [line.split() for line in lines if line.strip()]
    if table:
        tables.append(table)

# Tabellen in Excel speichern
with pd.ExcelWriter('extracted_tables.xlsx', engine='openpyxl') as writer:
    for i, table in enumerate(tables):
        df = pd.DataFrame(table)
        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False, header=False)

print("✅ Tabellen wurden erfolgreich extrahiert und gespeichert.")
