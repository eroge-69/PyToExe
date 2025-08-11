from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import os

# --- USTAWIENIA ---
page_width, page_height = A4
margin = 30  # margines strony
cols = 3
rows = 2
box_size = (page_width - 2*margin) / cols  # kwadratowe pola
font_path = "SpecialElite.ttf"
font_name = "SpecialElite"
output_file = "karteczki_test.pdf"
website_text = "www.punktwymianypoezji.pl"

# Rejestracja czcionki
pdfmetrics.registerFont(TTFont(font_name, font_path))

def draw_wrapped_text(c, text, x, y, width, height, font, max_font_size):
    """
    Rysuje tekst dopasowany do pola, zmniejszając czcionkę, jeśli trzeba.
    """
    font_size = max_font_size
    lines = []
    while font_size > 6:
        c.setFont(font, font_size)
        wrapper = textwrap.TextWrapper(width=int(width/(font_size*0.6)))
        lines = wrapper.wrap(text)
        text_height = len(lines) * (font_size + 2)
        if text_height <= height - 10:
            break
        font_size -= 1
    text_y = y + (height - text_height) / 2
    for line in lines:
        text_width = c.stringWidth(line, font, font_size)
        c.drawString(x + (width - text_width) / 2, text_y, line)
        text_y -= font_size + 2

def create_pdf(verses, images):
    c = canvas.Canvas(output_file, pagesize=A4)

    # STRONA 1 - WIERSZE
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            x = margin + col * box_size
            y = page_height - margin - (row + 1) * box_size
            c.rect(x, y, box_size, box_size)
            draw_wrapped_text(c, verses[idx], x + 5, y + 5, box_size - 10, box_size - 10, font_name, 18)
    c.showPage()

    # STRONA 2 - GRAFIKI
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            x = margin + col * box_size
            y = page_height - margin - (row + 1) * box_size
            c.rect(x, y, box_size, box_size)
            img = ImageReader(images[idx])
            img_w, img_h = img.getSize()
            scale = min(box_size / img_w, box_size / img_h)
            img_x = x + (box_size - img_w * scale) / 2
            img_y = y + (box_size - img_h * scale) / 2
            c.drawImage(img, img_x, img_y, img_w * scale, img_h * scale)
            # Adres strony na dole
            c.setFont(font_name, 10)
            text_width = c.stringWidth(website_text, font_name, 10)
            c.drawString(x + (box_size - text_width) / 2, y + 5, website_text)
    c.save()

if __name__ == "__main__":
    verses = []
    images = []
    for i in range(1, 7):
        with open(f"verse{i}.txt", "r", encoding="utf-8") as f:
            verses.append(f.read().strip())
        images.append(f"img{i}.jpg")  # zmień rozszerzenie jeśli PNG

    create_pdf(verses, images)
    print(f"✅ Zapisano {output_file}")