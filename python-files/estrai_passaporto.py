import sys
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from passporteye import read_mrz
import os

# Imposta qui il percorso di tesseract se serve (modifica in base alla tua installazione)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def estrai_dati(pdf_path):
    try:
        immagini = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
        img_path = "temp_img.png"
        immagini[0].save(img_path)
        mrz = read_mrz(img_path)
        testo_ocr = pytesseract.image_to_string(Image.open(img_path))
        os.remove(img_path)
        if mrz:
            mrz_dati = mrz.to_dict()
        else:
            mrz_dati = {}
        return mrz_dati, testo_ocr
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python estrai_passaporto.py percorso_del_pdf")
        sys.exit(1)
    pdf_path = sys.argv[1]
    mrz, ocr = estrai_dati(pdf_path)
    if mrz is None:
        print(f"Errore durante l'estrazione: {ocr}")
    else:
        print("Dati MRZ estratti:")
        for k, v in mrz.items():
            print(f"{k}: {v}")
        print("\nTesto OCR completo:")
        print(ocr)