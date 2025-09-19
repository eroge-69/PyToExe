import os
import qrcode
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch

# Network path for last number
LAST_NUMBER_FILE = r"\\server1\scans\Alejandro\Shipping Labels\last_number.txt"

# PDF will stay in the current folder
PDF_FILE = "QRCodes.pdf"

# Ensure network folder exists
folder = os.path.dirname(LAST_NUMBER_FILE)
os.makedirs(folder, exist_ok=True)

# Load last number
if os.path.exists(LAST_NUMBER_FILE):
    with open(LAST_NUMBER_FILE, "r") as f:
        last_number = int(f.read().strip())
else:
    last_number = 0

# Tkinter GUI
root = Tk()
root.title("QR Label Generator")
root.geometry("400x200")

# Variables
amount_var = StringVar(value="1")
last_code_var = StringVar(value=f"Last QR code used: A{last_number:010d}")

# Functions
def generate_qr():
    global last_number
    try:
        amount = int(amount_var.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid positive number")
        return

    codes = []
    c = canvas.Canvas(PDF_FILE, pagesize=(3*inch, 3*inch))

    for i in range(1, amount + 1):
        number = last_number + i
        code = f"A{number:010d}"
        codes.append(code)

        # Generate a NEW QR code for each code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2
        )
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save temporary QR image with unique name
        temp_file = f"temp_qr_{i}.png"
        img.save(temp_file)

        # Draw QR centered
        page_width = 3*inch
        page_height = 3*inch
        qr_size = 1.5*inch
        x = (page_width - qr_size) / 2
        y = (page_height - qr_size) / 2 + 0.3*inch
        c.drawImage(temp_file, x, y, width=qr_size, height=qr_size)

        # Draw text below
        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width/2, y - 0.3*inch, code)

        # Add page
        c.showPage()

        # Remove this QR image immediately
        os.remove(temp_file)

    c.save()

    # Save last number to network path
    last_number += amount
    with open(LAST_NUMBER_FILE, "w") as f:
        f.write(str(last_number))

    last_code_var.set(f"Last QR code used: {codes[-1]}")
    messagebox.showinfo("Done", f"{PDF_FILE} generated with {amount} QR codes!")

# Widgets
Label(root, text="Number of QR codes:").pack(pady=10)
Entry(root, textvariable=amount_var).pack(pady=5)
Button(root, text="Generate QR Codes", command=generate_qr).pack(pady=10)
Label(root, textvariable=last_code_var, font=("Helvetica", 12, "bold")).pack(pady=20)

root.mainloop()
