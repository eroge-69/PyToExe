import os
import fitz  # PyMuPDF
from PIL import Image, ImageOps

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



WATCH_FOLDER = r"D:\meysam"
LINE_WIDTH_MM = 0.2
DPI = 300

def crop_centered_line(img, line_width_mm, dpi):
    px_width = int((line_width_mm / 25.4) * dpi)
    margin = px_width // 2
    gray = img.convert("L")
    bbox = ImageOps.invert(gray).getbbox()
    if not bbox:
        return img
    left = max(bbox[0] + margin, 0)
    top = max(bbox[1] + margin, 0)
    right = min(bbox[2] - margin, img.width)
    bottom = min(bbox[3] - margin, img.height)
    return img.crop((left, top, right, bottom))

def process_pdf(pdf_path):
    print(f"Processing {pdf_path} ...")
    doc = fitz.open(pdf_path)
    page = doc[0]  # فقط صفحه اول
    pix = page.get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    cropped = crop_centered_line(img, LINE_WIDTH_MM, DPI)
    out_path = pdf_path.replace(".pdf", ".png")
    cropped.save(out_path, "PNG")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    for fname in os.listdir(WATCH_FOLDER):
        if fname.lower().endswith(".pdf"):
            process_pdf(os.path.join(WATCH_FOLDER, fname))
