
import fitz  # PyMuPDF
import os
import win32print
import win32api
import time

INPUT_FOLDER = "input"
TEMP_CROP_PDF = "cropped_awb.pdf"

# Dimensiuni AWB 100x150mm în puncte
CROP_WIDTH = 283.5
CROP_HEIGHT = 425.2

if not os.path.exists(INPUT_FOLDER):
    os.makedirs(INPUT_FOLDER)
    print(f"Am creat folderul '{INPUT_FOLDER}'. Pune PDF-urile acolo.")
    input("Apasă ENTER pentru a închide...")
    exit()

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".pdf"):
        full_path = os.path.join(INPUT_FOLDER, filename)
        print(f"Procesez: {filename}")

        doc = fitz.open(full_path)
        page = doc.load_page(0)

        rect = fitz.Rect(0, page.rect.height - CROP_HEIGHT, CROP_WIDTH, page.rect.height)
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=CROP_WIDTH, height=CROP_HEIGHT)
        new_page.show_pdf_page(new_page.rect, doc, 0, clip=rect)

        new_doc.save(TEMP_CROP_PDF)
        new_doc.close()
        doc.close()

        printer_name = win32print.GetDefaultPrinter()
        win32api.ShellExecute(
            0,
            "printto",
            TEMP_CROP_PDF,
            f'"{printer_name}"',
            ".",
            0
        )

        time.sleep(5)

        os.remove(full_path)
        os.remove(TEMP_CROP_PDF)

        print("Printat și șters:", filename)

print("GATA. Toate AWB-urile au fost procesate.")
input("Apasă ENTER pentru a ieși...")
