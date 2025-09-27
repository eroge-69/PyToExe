#!/usr/bin/env python3
"""
merge_add_bangla_pagenumbers_gui.py

এই GUI ভার্সন সফটওয়্যার:
 - একাধিক PDF ফাইল সিলেক্ট করতে পারবেন।
 - Merge করবে।
 - প্রতিটি পৃষ্ঠার উপরের ডান কোণে বাংলা সংখ্যায় পৃষ্ঠা নম্বর বসাবে।
 - একটি আউটপুট ফাইল নাম সিলেক্ট করার অপশন থাকবে।

ব্যবহার:
   python merge_add_bangla_pagenumbers_gui.py

.exe বানাতে:
   pip install pyinstaller reportlab PyPDF2 tk
   pyinstaller --onefile merge_add_bangla_pagenumbers_gui.py

তারপর dist ফোল্ডারে exe পাবেন।
"""
import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# --- সেটিংস ---
BENGALI_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "C:\\Windows\\Fonts\\DejaVuSans.ttf",
    "./DejaVuSans.ttf",
]
FALLBACK_FONT_NAME = "Helvetica"
FONT_REG_NAME = "BanglaFont"
FONT_SIZE = 12
TOP_MARGIN = 20
RIGHT_MARGIN = 20

BENGALI_DIGITS = {
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
}

def to_bengali_number(n: int) -> str:
    return ''.join(BENGALI_DIGITS.get(ch, ch) for ch in str(n))

def find_font_path() -> str:
    for p in BENGALI_FONT_PATHS:
        if os.path.isfile(p):
            return p
    return ""

def make_page_number_overlay(page_width: float, page_height: float, text: str, font_name: str) -> bytes:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    text_width = stringWidth(text, font_name, FONT_SIZE)
    x = page_width - RIGHT_MARGIN - text_width
    y = page_height - TOP_MARGIN - FONT_SIZE/2
    c.setFont(font_name, FONT_SIZE)
    c.drawString(x, y, text)
    c.save()
    packet.seek(0)
    return packet.read()

def merge_pdfs_with_bangla_numbers(output_path: str, input_paths):
    if not input_paths:
        raise ValueError("কমপক্ষে একটি ইনপুট PDF দিন।")

    writer = PdfWriter()

    readers = []
    for p in input_paths:
        r = PdfReader(p)
        readers.append(r)

    font_path = find_font_path()
    using_font = FALLBACK_FONT_NAME
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont(FONT_REG_NAME, font_path))
            using_font = FONT_REG_NAME
        except:
            using_font = FALLBACK_FONT_NAME

    page_counter = 1
    for r in readers:
        for p in r.pages:
            media = p.mediabox
            w = float(media.width)
            h = float(media.height)

            bengali_num = to_bengali_number(page_counter)
            overlay_pdf_bytes = make_page_number_overlay(w, h, bengali_num, using_font)

            overlay_reader = PdfReader(io.BytesIO(overlay_pdf_bytes))
            overlay_page = overlay_reader.pages[0]
            try:
                p.merge_page(overlay_page)
            except Exception:
                pass

            writer.add_page(p)
            page_counter += 1

    with open(output_path, 'wb') as f:
        writer.write(f)

# --- GUI ---
def run_gui():
    root = tk.Tk()
    root.title("PDF Merge + Bangla Page Number")
    root.geometry("500x300")

    selected_files = []

    def select_files():
        nonlocal selected_files
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            selected_files = list(files)
            files_list.delete(0, tk.END)
            for f in selected_files:
                files_list.insert(tk.END, f)

    def merge_action():
        if not selected_files:
            messagebox.showerror("Error", "কোনো PDF ফাইল সিলেক্ট করা হয়নি।")
            return
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output:
            return
        try:
            merge_pdfs_with_bangla_numbers(output, selected_files)
            messagebox.showinfo("Success", f"সফল হয়েছে! আউটপুট: {output}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Select PDF Files", command=select_files).pack(pady=10)
    files_list = tk.Listbox(root, width=60, height=8)
    files_list.pack(pady=5)
    tk.Button(root, text="Merge & Add Bangla Numbers", command=merge_action).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
