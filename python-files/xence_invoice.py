
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def create_invoice():
    print("Welcome to Xence Invoice Generator\n")
    company_name = input("Your company name: ")
    client_name = input("Client name: ")
    invoice_number = input("Invoice number: ")
    service_desc = input("Service description: ")
    quantity = int(input("Quantity: "))
    unit_price = float(input("Unit price ($): "))
    tax_rate = float(input("Tax rate (%): "))
    currency = "$"

    subtotal = quantity * unit_price
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    today = datetime.today().strftime('%Y-%m-%d')

    filename = f"invoice_{invoice_number}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"Invoice #{invoice_number}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Date: {today}")
    c.drawString(50, height - 120, f"From: {company_name}")
    c.drawString(50, height - 140, f"To: {client_name}")

    c.drawString(50, height - 180, f"Description: {service_desc}")
    c.drawString(50, height - 200, f"Quantity: {quantity}")
    c.drawString(50, height - 220, f"Unit Price: {unit_price:.2f}{currency}")
    c.drawString(50, height - 240, f"Subtotal: {subtotal:.2f}{currency}")
    c.drawString(50, height - 260, f"Tax ({tax_rate}%): {tax_amount:.2f}{currency}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 290, f"TOTAL: {total:.2f}{currency}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Generated with Xence - Invoice Tool")

    c.save()
    print(f"\n✅ Invoice saved as '{filename}'")

create_invoice()
