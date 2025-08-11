import os
import requests
import docx
import re

# ==== KONFIGURACJA ====
ONEDRIVE_FOLDER = r"C:\Users\TwojaNazwa\OneDrive\Dokumenty"  # tu wpisz swoją ścieżkę
API_KEY = "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"
MODEL = "openai/gpt-oss-20b:free"

# ==== FUNKCJE ====
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def suggest_filename_via_ai(text):
    prompt = f"""Przeczytaj ten tekst dokumentu i zaproponuj krótki, zwięzły tytuł pliku (bez polskich znaków, bez spacji, zamiast spacji myślniki, max 50 znaków, bez rozszerzenia).
Tekst dokumentu:
{text[:3000]}"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Jesteś asystentem do nadawania nazw plikom."},
            {"role": "user", "content": prompt}
        ]
    }
    
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    r.raise_for_status()
    name = r.json()["choices"][0]["message"]["content"]
    name = re.sub(r'[^\w\-]', '', name)  # usuń niedozwolone znaki
    return name

def rename_docx_files():
    for filename in os.listdir(ONEDRIVE_FOLDER):
        if filename.lower().endswith(".docx"):
            full_path = os.path.join(ONEDRIVE_FOLDER, filename)
            print(f"Przetwarzam: {filename}")
            try:
                text = extract_text_from_docx(full_path)
                new_name = suggest_filename_via_ai(text)
                new_path = os.path.join(ONEDRIVE_FOLDER, f"{new_name}.docx")
                os.rename(full_path, new_path)
                print(f"Zmieniono nazwę na: {new_name}.docx")
            except Exception as e:
                print(f"Błąd dla {filename}: {e}")

if __name__ == "__main__":
    rename_docx_files()
