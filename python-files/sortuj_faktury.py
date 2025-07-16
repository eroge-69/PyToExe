
import os
import fitz  # PyMuPDF
import re
import shutil
import sys

def extract_country_and_vat(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        country_match = re.search(r"\b([A-Z]{2})\b\s*$", text, re.MULTILINE)
        country = country_match.group(1) if country_match else "UNKNOWN"

        vat_match = re.search(r"(\d{1,2})\s*%", text)
        vat_rate = vat_match.group(1) if vat_match else "UNKNOWN"

        return country, vat_rate
    except Exception as e:
        print(f"Błąd przy pliku {pdf_path}: {e}")
        return "ERROR", "ERROR"

def sort_pdfs_by_country_and_vat(base_folder):
    for filename in os.listdir(base_folder):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(base_folder, filename)
            country, vat = extract_country_and_vat(full_path)

            if country == "ERROR":
                continue

            target_folder = os.path.join(base_folder, country, vat)
            os.makedirs(target_folder, exist_ok=True)

            shutil.move(full_path, os.path.join(target_folder, filename))
            print(f"Przeniesiono {filename} → {country}/{vat}/")

if __name__ == "__main__":
    folder_path = os.getcwd()
    sort_pdfs_by_country_and_vat(folder_path)
    print("\nGotowe. Możesz zamknąć to okno.")
    input("Naciśnij Enter...")
