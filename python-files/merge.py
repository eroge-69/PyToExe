import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from io import BytesIO

# ---- Configuration ----
TITLE = "Rockin' 1000 Leiria 2025 Backing Vocal 1"
OUTPUT_FILE = "merged_with_index.pdf"

# ---- Helper functions ----
def human_readable(name):
    base = os.path.splitext(name)[0]
    base = base.replace("_", " ").replace("-", " ")
    return base

def create_index_pdf(file_names):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height-50, TITLE)

    # Bullet points
    c.setFont("Helvetica", 14)
    y = height - 100
    for i, fname in enumerate(file_names):
        display_name = human_readable(fname)
        c.drawString(50, y, f"• {display_name}")
        # Add clickable link (we'll link via bookmarks later)
        # We'll create named destinations with PyPDF2
        c.linkAbsolute("", f"DEST_{i}", Rect=(50, y-2, width-50, y+12))
        y -= 25
        if y < 50:  # simple page break if too long
            c.showPage()
            y = height - 50

    c.save()
    packet.seek(0)
    return PdfReader(packet)

# ---- Main processing ----
def main():
    # Get all PDFs in current folder
    pdf_files = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    pdf_files.sort(key=lambda s: s.lower())

    if not pdf_files:
        print("No PDF files found in this folder.")
        return

    writer = PdfWriter()

    # Create index page
    index_pdf = create_index_pdf(pdf_files)
    writer.add_page(index_pdf.pages[0])

    # Add PDFs and bookmarks
    page_offset = 1  # index page counts as page 0
    for i, pdf_file in enumerate(pdf_files):
        reader = PdfReader(pdf_file)
        writer.add_bookmark(human_readable(pdf_file), page_offset, parent=None, key=f"DEST_{i}")

        for page in reader.pages:
            writer.add_page(page)
        # Add "Índice" link at bottom of last page
        last_page = writer.pages[-1]
        last_page.add_annotation({
            "/Type": "/Annot",
            "/Subtype": "/Link",
            "/Rect": [450, 20, 520, 40],
            "/Border": [0, 0, 0],
            "/A": {
                "/S": "/GoTo",
                "/D": 0  # first page
            }
        })

        page_offset += len(reader.pages)

    # Write output
    with open(OUTPUT_FILE, "wb") as f:
        writer.write(f)

    print(f"Merged PDF created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
