
import pandas as pd
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import inch
from bidi.algorithm import get_display
import arabic_reshaper
import win32print
import win32api

LABEL_WIDTH = 1.594 * inch
LABEL_HEIGHT = 0.984 * inch
EXCEL_FILE = "print_jobs.xlsx"

def print_label(barcode_text, product_name, quantity):
    reshaped_text = arabic_reshaper.reshape(product_name)
    bidi_text = get_display(reshaped_text)

    for _ in range(quantity):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            c = canvas.Canvas(temp_file.name, pagesize=(LABEL_WIDTH, LABEL_HEIGHT))

            c.setFont("Helvetica", 6)
            c.drawCentredString(LABEL_WIDTH / 2, LABEL_HEIGHT - 0.15 * inch, bidi_text)

            barcode = code128.Code128(barcode_text, barHeight=0.4 * inch)
            barcode.drawOn(c, (LABEL_WIDTH - barcode.width) / 2, 0.25 * inch)

            c.setFont("Helvetica", 7)
            c.drawCentredString(LABEL_WIDTH / 2, 0.15 * inch, barcode_text)

            c.showPage()
            c.save()

            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(0, "print", temp_file.name, None, ".", 0)

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Excel file '{EXCEL_FILE}' not found.")
        return

    df = pd.read_excel(EXCEL_FILE, header=0)
    for _, row in df.iterrows():
        barcode = str(row.iloc[0])
        qty = int(row.iloc[1])
        name = str(row.iloc[7])
        print_label(barcode, name, qty)

    df.iloc[0:0].to_excel(EXCEL_FILE, index=False, header=True)

if __name__ == "__main__":
    main()
