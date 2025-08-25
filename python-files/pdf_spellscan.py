import fitz  # PyMuPDF
import re
from spellchecker import SpellChecker

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def is_abbreviation(word):
    if word.isupper():
        return True
    if any(char.isdigit() for char in word):
        return True
    if len(word) <= 2 and word.lower() not in {"an", "is", "to", "in", "on", "at", "by", "of"}:
        return True
    if any(char in word for char in {'Ø', '/', '-', '_'}):
        return True
    if re.match(r'^[A-Za-z]+\d+|\d+[A-Za-z]+$', word):
        return True
    return False

def check_spelling(words):
    spell = SpellChecker()
    misspelled = spell.unknown(words)
    report = []
    for word in misspelled:
        suggestion = spell.correction(word)
        report.append((word, suggestion, "Misspelt"))
    return report

def save_report(report, output_path="spellcheck_report.txt"):
    with open(output_path, "w") as f:
        f.write("Word Found\tSuggestion\tStatus\n")
        for word, suggestion, status in report:
            f.write(f"{word}\t{suggestion}\t{status}\n")
    print(f"✅ Report saved to {output_path}")

def scan_pdf_for_spelling(pdf_path):
    print(f"🔍 Scanning: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    words = raw_text.split()
    words_to_check = [w for w in words if not is_abbreviation(w)]
    report = check_spelling(words_to_check)
    save_report(report)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_spellscan.py <path_to_pdf>")
    else:
        scan_pdf_for_spelling(sys.argv[1])