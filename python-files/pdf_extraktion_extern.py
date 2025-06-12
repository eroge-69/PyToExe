
import os
import fitz  # PyMuPDF
import pandas as pd

def lade_begriffe(dateiname="begriffe.txt"):
    if not os.path.exists(dateiname):
        print(f"❌ Datei {dateiname} nicht gefunden.")
        return []
    with open(dateiname, "r", encoding="utf-8") as f:
        return [zeile.strip() for zeile in f if zeile.strip()]

def extract_data_from_pdf(path, suchbegriffe):
    text_data = {"Datei": os.path.basename(path)}
    for begriff in suchbegriffe:
        text_data[begriff] = ""
    try:
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        lines = full_text.splitlines()

        for i, line in enumerate(lines):
            for begriff in suchbegriffe:
                if begriff in line and not text_data[begriff]:
                    nach_wert = line.split(begriff, 1)[1].strip()
                    if nach_wert:
                        text_data[begriff] = nach_wert
                    elif i + 1 < len(lines):
                        naechste_zeile = lines[i + 1].strip()
                        if naechste_zeile:
                            text_data[begriff] = naechste_zeile
    except Exception as e:
        print(f"⚠️ Fehler bei Datei {path}: {e}")
    return text_data

def scan_folder_for_pdfs(root_folder, suchbegriffe):
    data = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                result = extract_data_from_pdf(full_path, suchbegriffe)
                data.append(result)
    return data

if __name__ == "__main__":
    suchbegriffe = lade_begriffe()
    if not suchbegriffe:
        print("Keine gültigen Suchbegriffe gefunden. Bitte 'begriffe.txt' prüfen.")
        input("Beenden mit Enter...")
        exit()

    ordner = input("📁 Bitte gib den Pfad zum Ordner mit PDFs ein:\n> ")
    if not os.path.exists(ordner):
        print("❌ Ordner nicht gefunden.")
        input("Beenden mit Enter...")
        exit()

    ergebnisse = scan_folder_for_pdfs(ordner, suchbegriffe)
    df = pd.DataFrame(ergebnisse)

    excel_datei = "extraktion_ergebnis.xlsx"
    df.to_excel(excel_datei, index=False)
    print(f"✅ Fertig! Excel-Datei gespeichert als: {excel_datei}")
    input("Beenden mit Enter...")
