import pytesseract
from pdf2image import convert_from_path
import re
import os
from tkinter import filedialog, Tk

# ustalamy bazową ścieżkę (tam gdzie jest exe / skrypt)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ścieżki do lokalnych programów
TESSERACT_PATH = os.path.join(BASE_DIR, "tesseract", "tesseract.exe")
POPPLER_PATH = os.path.join(BASE_DIR, "poppler", "Library", "bin")

# konfiguracja pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# okienko wyboru folderu
root = Tk()
root.withdraw()
folder = filedialog.askdirectory(title="Wybierz folder ze skanami (PDF)")

if not folder:
    print("❌ Nie wybrano folderu. Program kończy działanie.")
    exit()

for filename in os.listdir(folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(folder, filename)

        try:
            # konwersja stron PDF -> obrazy
            pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

            order_number = None

            for page_img in pages:
                # wycięcie górnego-lewego rogu (40% szer., 20% wys.)
                width, height = page_img.size
                crop_area = (0, 0, width * 0.4, height * 0.2)
                cropped_img = page_img.crop(crop_area)

                # OCR
                text = pytesseract.image_to_string(cropped_img, lang="pol")

                # szukanie numeru (ciąg 5+ cyfr)
                match = re.search(r"\d{5,}", text)
                if match:
                    order_number = match.group(0)
                    break

            # nowa nazwa pliku
            if order_number:
                new_name = f"{order_number}.pdf"
            else:
                new_name = f"brak_numeru_{filename}"

            new_path = os.path.join(folder, new_name)

            # zmiana nazwy (unikamy kolizji)
            if not os.path.exists(new_path):
                os.rename(pdf_path, new_path)
                print(f"✅ {filename} → {new_name}")
            else:
                print(f"⚠️ Plik {new_name} już istnieje, pomijam.")

        except Exception as e:
            print(f"❌ Błąd przy pliku {filename}: {e}")

input("Naciśnij Enter aby zakończyć...")
