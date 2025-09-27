#!/usr/bin/env python3
"""
merge_add_bangla_pagenumbers.py

মানুষ যে স্ক্রিপ্টটা চালাবে তা: কয়েকটি PDF ফাইলকে একত্রে মিলিয়ে দিবে (merge)
এবং প্রতিটি পৃষ্ঠার উপরের ডান কোনে বাংলা সংখ্যায় পৃষ্ঠা নম্বর বসিয়ে একটি নতুন PDF আউটপুট করবে।

ব্যবহার:
    python merge_add_bangla_pagenumbers.py output.pdf input1.pdf input2.pdf ...

প্রয়োজনীয় প্যাকেজ:
    pip install PyPDF2 reportlab

টীকা:
 - সুন্দর বাংলা ফন্ট দেখাতে আপনার সিস্টেমে কোনো বাংলাসমর্থিত TTF ফন্ট থাকতে হবে।
   স্ক্রিপ্টটি DejaVuSans.ttf এর ডিফল্ট লোকেশনগুলো চেক করে — না পেলে আপনি নিজের .ttf ফাইলের
   পথ `BENGALI_FONT_PATH` পরিবর্তন করে দিতে পারবেন।

"""
import sys
import io
import os
from typing import List

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# --- সেটিংস ---
# যদি আপনার কাছে বাংলা সমর্থিত TTF ফন্ট আছে, এখানে সেই ফাইলের পাথ দিন।
# উদাহরণ: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" বা "C:\\Windows\\Fonts\\DejaVuSans.ttf"
BENGALI_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "C:\\Windows\\Fonts\\DejaVuSans.ttf",
    "./DejaVuSans.ttf",
]
FALLBACK_FONT_NAME = "Helvetica"  # যদি বাংলা ফন্ট না পাওয়া যায়, এটাই ইউজ হবে (বর্ণ দেখাবে না)
FONT_REG_NAME = "BanglaFont"
FONT_SIZE = 12  # পৃষ্ঠা নম্বর ফন্ট সাইজ (প্রয়োজনে অ্যাডজাস্ট করুন)
TOP_MARGIN = 20  # পয়েন্টে উপরের মার্জিন থেকে দূরত্ব
RIGHT_MARGIN = 20  # ডানদিকে মার্জিন

# বাংলা সংখ্যায় রূপান্তর
BENGALI_DIGITS = {
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
}

def to_bengali_number(n: int) -> str:
    s = str(n)
    return ''.join(BENGALI_DIGITS.get(ch, ch) for ch in s)


def find_font_path() -> str:
    for p in BENGALI_FONT_PATHS:
        if os.path.isfile(p):
            return p
    return ""


def make_page_number_overlay(page_width: float, page_height: float, text: str, font_name: str) -> bytes:
    """
    একটি ছোট PDF (Bytes) তৈরি করবে যার মধ্যে নির্দিষ্ট সাইজের এক পৃষ্ঠায় উপরের ডান কোণে `text` থাকবে।
    এরপর এই Bytes-টাই PyPDF2 দিয়ে মূল পৃষ্ঠার উপরে ওভারলে করা হবে।
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # রিপোর্টল্যাবের টেক্সটের প্রস্থ জানবো যাতে ডান থেকে মার্জিন করে সঠিক অবস্থানে বসাতে পারি
    text_width = stringWidth(text, font_name, FONT_SIZE)
    x = page_width - RIGHT_MARGIN - text_width
    y = page_height - TOP_MARGIN - FONT_SIZE/2

    c.setFont(font_name, FONT_SIZE)
    c.drawString(x, y, text)
    c.save()

    packet.seek(0)
    return packet.read()


def merge_pdfs_with_bangla_numbers(output_path: str, input_paths: List[str]):
    if not input_paths:
        raise ValueError("কমপক্ষে একটি ইনপুট PDF দিন।")

    # প্রথমে সব পিডিএফকে একটিতে মিলিয়ে নেবো (অর্থাৎ পৃষ্ঠাগুলো ধারাবাহিকভাবে এক করে)
    writer = PdfWriter()

    total_pages = 0
    readers = []
    for p in input_paths:
        r = PdfReader(p)
        readers.append(r)
        total_pages += len(r.pages)

    # ফন্ট সেটআপ: যদি বাংলা TTF পাওয়া যায় তবে সেটি রেজিস্টার করবো
    font_path = find_font_path()
    using_font = FALLBACK_FONT_NAME
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont(FONT_REG_NAME, font_path))
            using_font = FONT_REG_NAME
            print(f"ব্যবহৃত ফন্ট: {font_path}")
        except Exception as e:
            print("ফন্ট রেজিস্টার করতে সমস্যা হয়েছে, ফুলব্যাক ফন্ট ব্যবহার করা হবে:", e)
            using_font = FALLBACK_FONT_NAME
    else:
        print("কোনো বাংলা/ট্রুটিফন্ট ফাইল পাওয়া যায়নি — বাংলা সংখ্যার সঠিক রেন্ডার নাও হতে পারে।")

    # এখন প্রত্যেকটি পৃষ্ঠা নিয়ে তার উপর ওভারলে করে লেখবো
    page_counter = 1
    for r in readers:
        for p in r.pages:
            # পেইজ সাইজ পান (points)
            try:
                media = p.mediabox
                w = float(media.width)
                h = float(media.height)
            except Exception:
                # fallback A4
                w, h = 595.276, 841.89

            # বাংলা সংখ্যা
            bengali_num = to_bengali_number(page_counter)

            overlay_pdf_bytes = make_page_number_overlay(w, h, bengali_num, using_font)

            # ওভারলে পিডিএফকে রিড করে মার্জ করে দেব
            overlay_reader = PdfReader(io.BytesIO(overlay_pdf_bytes))
            overlay_page = overlay_reader.pages[0]

            try:
                # PyPDF2 merging
                p.merge_page(overlay_page)
            except Exception:
                # কিছু PyPDF2 ভার্সনে merge_page এর জায়গায় merge_page আছে বা অন্য নামে হতে পারে
                try:
                    p.merge_page(overlay_page)
                except Exception as e:
                    print("পৃষ্ঠায় ওভারলে করা গেল না:", e)

            writer.add_page(p)
            page_counter += 1

    # শেষে লেখে ফেলি
    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"সফল হয়েছে — আউটপুট: {output_path} (মোট পৃষ্ঠা: {page_counter - 1})")


def main():
    if len(sys.argv) < 3:
        print("ব্যবহার: python merge_add_bangla_pagenumbers.py output.pdf input1.pdf [input2.pdf ...]")
        sys.exit(1)

    output = sys.argv[1]
    inputs = sys.argv[2:]

    # ইনপুট ফাইল চেক
    for ip in inputs:
        if not os.path.isfile(ip):
            print(f"ইনপুট ফাইল নেই: {ip}")
            sys.exit(1)

    merge_pdfs_with_bangla_numbers(output, inputs)


if __name__ == '__main__':
    main()
