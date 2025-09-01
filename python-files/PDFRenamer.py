import os
import re
import time
import json
from datetime import datetime
from PyPDF2 import PdfReader

APPDATA_FOLDER = os.path.join(os.getenv("APPDATA"), "PDFRenamer")
CONFIG_FILE = os.path.join(APPDATA_FOLDER, "config.json")
CHECK_INTERVAL = 120

def ensure_config():
    if not os.path.exists(APPDATA_FOLDER):
        os.makedirs(APPDATA_FOLDER)
    if not os.path.exists(CONFIG_FILE):
        paths = []
        while True:
            path = input("Ordnerpfad eingeben (oder leer lassen zum Beenden): ").strip()
            if not path:
                break
            if os.path.isdir(path):
                paths.append(path)
        if not paths:
            exit()
        save_config(paths)

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("paths", [])

def save_config(paths):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"paths": paths}, f, indent=4, ensure_ascii=False)

def extract_text_from_pdf(filepath):
    try:
        reader = PdfReader(filepath)
        return reader.pages[0].extract_text() if reader.pages else ""
    except:
        return ""

def clean_name(text):
    # Entfernt genau diese BICs
    for bic in ["WELADE3LXXX", "DGPBDE3MXXX", "DAAEDEDDXXX", "Casinogarten"]:
        text = text.replace(bic, "")
    # Entfernt generelle IBAN/BIC-Muster
    text = re.sub(r"\b(BIC|IBAN)[^\s]*", "", text, flags=re.IGNORECASE)
    return text.strip()


def parse_invoice_details(text):
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
    if not date_match:
        return None
    date_obj = datetime.strptime(date_match.group(1), "%d.%m.%Y")
    months_de = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    month_de = months_de[date_obj.month-1]
    if "Rechnungsübersicht" in text:
        company_match = re.search(r"(CSW-?\s?[\w-]+)", text)
        company = company_match.group(0) if company_match else "Unbekannt"
        return f"Rechnungsübersicht {company} {month_de} {date_obj.year}"
    elif "Rechnung für:" in text:
        name_match = re.search(r"Rechnung für:\s*(Herr|Frau)?\s*(.+)", text)
        customer = name_match.group(2).strip() if name_match else "Unbekannt"
        customer = clean_name(customer)
        return f"Rechnung {customer} {month_de} {date_obj.year}"
    elif "Rechnung" in text:
        address_pattern = r"([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*)\s+([A-ZÄÖÜa-zäöüß\.\s\d]+)\s+(\d{5}\s+[A-ZÄÖÜa-zäöüß\s]+)(?=\s+Rechnung)"
        address_match = re.search(address_pattern, text)
        if not address_match:
            parts = text.splitlines()
            for i, line in enumerate(parts):
                if line.strip().startswith("Rechnung") and i >= 3:
                    potential_name = parts[i-3].strip()
                    street = parts[i-2].strip()
                    plz_ort = parts[i-1].strip()
                    address_match = (potential_name, street, plz_ort)
                    break
        if address_match:
            if isinstance(address_match, tuple):
                potential_name, street, plz_ort = address_match
            else:
                potential_name = address_match.group(1).strip()
                street = address_match.group(2).strip()
                plz_ort = address_match.group(3).strip()
            potential_name = clean_name(potential_name)
            if (not any(word in potential_name.lower() for word in ['apotheke','gmbh','kg','ag','deutschland','bank'])
                and re.match(r'\d{5}', plz_ort)
                and not any(keyword in street.lower() for keyword in ['iban','bic','bank'])):
                name_parts = potential_name.split()
                if len(name_parts) >= 2:
                    formatted_name = f"{name_parts[-1]}, {' '.join(name_parts[:-1])}"
                    return f"Rechnung {formatted_name} {month_de} {date_obj.year}"

    return None

def try_rename(filepath):
    text = extract_text_from_pdf(filepath)
    new_name = parse_invoice_details(text)
    if new_name:
        folder = os.path.dirname(filepath)
        new_path = os.path.join(folder, f"{new_name}.pdf")
        if not os.path.exists(new_path):
            os.rename(filepath, new_path)
            print(f"✅ Umbenannt: {os.path.basename(filepath)} ➝ {os.path.basename(new_path)}")
    else:
        print(f"⚠️ Keine Infos gefunden für {os.path.basename(filepath)}")

def watch_folders(paths):
    while True:
        for folder in paths:
            if not os.path.exists(folder):
                continue
            for file in os.listdir(folder):
                if file.lower().endswith(".pdf") and "umgeleitet" in file.lower():
                    full_path = os.path.join(folder, file)
                    try_rename(full_path)
        time.sleep(CHECK_INTERVAL)

def main():
    ensure_config()
    paths = load_config()
    if not paths:
        return
    watch_folders(paths)

if __name__ == "__main__":
    main()