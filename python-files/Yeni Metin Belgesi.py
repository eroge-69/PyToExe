# -*- coding: utf-8 -*-
"""
PDF tarayıp:
  1) İçeriğinde "Bilgi için:Umut KURT" ibaresi olan dosyaları bulur,
  2) "Sayı : E-..." ifadesinin son '-' sonrasındaki sayıyı çıkarır,
  3) Sonuçları Excel'e yazar (xlsx).

Çift tıklama ile çalışacak şekilde sabit klasör:
    Aranan klasör: D:\MAHKEME YAZILARI
    Çıktı: D:\MAHKEME YAZILARI\sonuclar.xlsx

Gerekli paketler:
    pip install pypdf pandas openpyxl
"""

import os
import re
import pandas as pd
from pypdf import PdfReader

# ---------- Ayarlar ----------
ROOT_FOLDER = r"D:\MAHKEME YAZILARI"
OUTPUT_FILE = os.path.join(ROOT_FOLDER, "sonuclar.xlsx")
# ------------------------------

def pdf_to_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        texts.append(t)
    return "\n".join(texts)


def contains_target_phrase(text: str) -> bool:
    return "Bilgi için:Umut KURT" in text


def extract_last_hyphen_number(text: str):
    pattern = re.compile(r"Sayı\s*:\s*E-([0-9.\-]+)", re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        return None

    token = m.group(1)
    full_expr = f"E-{token}"
    last_part = token.split("-")[-1]
    last_digits = re.sub(r"\D+", "", last_part)

    if not last_digits:
        return None

    return full_expr, last_digits


def walk_pdfs(root: str):
    for r, _dirs, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                yield os.path.join(r, fn)


def main():
    records = []
    scanned = 0
    matched = 0

    for pdf_path in walk_pdfs(ROOT_FOLDER):
        scanned += 1
        try:
            text = pdf_to_text(pdf_path)
            if not text.strip():
                continue

            if not contains_target_phrase(text):
                continue

            res = extract_last_hyphen_number(text)
            if not res:
                continue

            full_expr, number = res
            matched += 1

            records.append({
                "FolderPath": os.path.dirname(pdf_path),
                "FileName": os.path.basename(pdf_path),
                "ExtractedNumber": number,
                "FullSayiExpr": full_expr,
            })

        except Exception as e:
            print(f"Hata: {pdf_path} -> {e}")

    if not records:
        df = pd.DataFrame(columns=["FolderPath", "FileName", "ExtractedNumber", "FullSayiExpr"])
    else:
        df = pd.DataFrame.from_records(records, columns=["FolderPath", "FileName", "ExtractedNumber", "FullSayiExpr"])

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Tamamlandı. {scanned} PDF incelendi, {matched} eşleşme bulundu.")
    print(f"Excel dosyası yazıldı: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
