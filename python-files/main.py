import tkinter as tk
from tkinter import filedialog, messagebox
import pytesseract
from PIL import Image
import pdfplumber
import pandas as pd
import re
import os

# Set path to Tesseract (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Excel file to store extracted invoices
EXCEL_FILE = "invoices.xlsx"

def extract_text_from_file(filepath):
    text = ""
    if filepath.lower().endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    else:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
    return text

def parse_invoice(text):
    data = {}

    # Extract fields using regex
    data["Invoice Number"] = re.search(r"Invoice Number:\s*(\S+)", text).group(1) if re.search(r"Invoice Number:\s*(\S+)", text) else ""
    data["Date of Issue"] = re.search(r"Date of Issue:\s*([\d-]+)", text).group(1) if re.search(r"Date of Issue:\s*([\d-]+)", text) else ""

    seller_match = re.search(r"Seller:\s*(.*?)Buyer:", text, re.S)
    data["Seller Info"] = seller_match.group(1).strip() if seller_match else ""

    buyer_match = re.search(r"Buyer:\s*(.*?)(Qty|Subtotal)", text, re.S)
    data["Buyer Info"] = buyer_match.group(1).strip() if buyer_match else ""

    data["Subtotal"] = re.search(r"Subtotal:\s*\$([\d.]+)", text).group(1) if re.search(r"Subtotal:\s*\$([\d.]+)", text) else ""
    data["Taxes"] = re.search(r"Taxes.*\s*\$([\d.]+)", text).group(1) if re.search(r"Taxes.*\s*\$([\d.]+)", text) else ""
    data["Total Amount Due"] = re.search(r"Total Amount Due:\s*\$([\d.]+)", text).group(1) if re.search(r"Total Amount Due:\s*\$([\d.]+)", text) else ""
    data["Payment Terms"] = re.search(r"Payment Terms:\s*(.*)", text).group(1) if re.search(r"Payment Terms:\s*(.*)", text) else ""

    # Extract table rows (Qty, Unit Price, Subtotal)
    table_rows = re.findall(r"(\d+)\s+\$?(\d+)\s+\$?(\d+)", text)
    data["Items"] = table_rows

    return data

def save_to_excel(data):
    # Prepare flat record for Excel
    record = {
        "Invoice Number": data["Invoice Number"],
        "Date of Issue": data["Date of Issue"],
        "Seller Info": data["Seller Info"],
        "Buyer Info": data["Buyer Info"],
        "Subtotal": data["Subtotal"],
        "Taxes": data["Taxes"],
        "Total Amount Due": data["Total Amount Due"],
        "Payment Terms": data["Payment Terms"]
    }

    # Save items as separate rows
    rows = []
    for qty, unit_price, subtotal in data["Items"]:
        row = record.copy()
        row.update({
            "Quantity": qty,
            "Unit Price": unit_price,
            "Line Subtotal": subtotal
        })
        rows.append(row)

    df = pd.DataFrame(rows)

    if os.path.exists(EXCEL_FILE):
        existing = pd.read_excel(EXCEL_FILE)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_excel(EXCEL_FILE, index=False)

def process_file():
    filepath = filedialog.askopenfilename(filetypes=[("Invoice Files", "*.pdf;*.png;*.jpg;*.jpeg")])
    if not filepath:
        return

    text = extract_text_from_file(filepath)
    data = parse_invoice(text)

    if not data["Invoice Number"]:
        messagebox.showerror("Error", "Failed to extract invoice data!")
        return

    save_to_excel(data)
    messagebox.showinfo("Success", f"Invoice {data['Invoice Number']} saved to {EXCEL_FILE}")

# GUI
root = tk.Tk()
root.title("Invoice Data Extractor")
root.geometry("400x200")

label = tk.Label(root, text="Upload Invoice (PDF/Image) to Extract Data", font=("Arial", 12))
label.pack(pady=20)

upload_btn = tk.Button(root, text="Upload Invoice", command=process_file, font=("Arial", 12), bg="blue", fg="white")
upload_btn.pack(pady=10)

exit_btn = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12), bg="red", fg="white")
exit_btn.pack(pady=10)

root.mainloop()
