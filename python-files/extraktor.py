import os
import re
import fitz  # PyMuPDF
import pandas as pd

def extract_items_from_text(text, doc_id):
    items = []
    pattern = re.compile(
        r"Položka č\.\s*(\d+).*?Název\s*-\s*popis\s*(.*?)\s*Množství\s*(\d+)\s*ks.*?Cena s DPH za jednotku\s*([\d\s]+,\d{2})\s*Kč",
        re.DOTALL
    )
    matches = pattern.findall(text)
    for match in matches:
        item_number, description, quantity, price = match
        items.append({
            "Č.pož./rok": doc_id,
            "Položka č.": item_number.strip(),
            "Název a popis": description.strip().replace("\n", " "),
            "Počet kusů": quantity.strip(),
            "Cena": price.strip().replace("\xa0", " ")
        })
    return items

def process_pdf_file(filepath):
    doc_id = os.path.splitext(os.path.basename(filepath))[0]
    with fitz.open(filepath) as doc:
        full_text = ""
        for page in doc:
            full_text += page.get_text()
    return extract_items_from_text(full_text, doc_id)

def main():
    all_items = []
    for filename in os.listdir():
        if filename.lower().endswith(".pdf"):
            print(f"Zpracovávám: {filename}")
            items = process_pdf_file(filename)
            all_items.extend(items)

    if all_items:
        df = pd.DataFrame(all_items)
        df.to_excel("vystupni_polozky.xlsx", index=False)
        print("Hotovo! Výstupní soubor: vystupni_polozky.xlsx")
    else:
        print("Nebyly nalezeny žádné položky.")

if __name__ == "__main__":
    main()
