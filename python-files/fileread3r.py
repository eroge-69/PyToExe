import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import re
import os

def extract_invoice_data(pdf_path)
    with fitz.open(pdf_path) as doc
        text = 
        for page in doc
            text += page.get_text()

    date_match = re.search(rTeljesítés.(d{4}[.-]d{2}[.-]d{2}), text, re.IGNORECASE)
    date = date_match.group(1).replace(., -) if date_match else nincs_datum

    company_match = re.search(rSzállítós+(.)n, text, re.IGNORECASE)
    if not company_match
        company_match = re.search(r([A-Z][a-zA-Z&s]+sKft.Zrt.Bt.), text)
    company = company_match.group(1).strip().replace( , _) if company_match else ismeretlen_ceg

    invoice_match = re.search(
        r(Számlas+sorszámIkt.sz.Számlaszám)[^dA-Z](w+[-]w+w),
        text, re.IGNORECASE)
    if not invoice_match
        invoice_match = re.search(rbOCd{6}d{4}b, text)
    invoice_number = invoice_match.group(2) if invoice_match else nincs_szamlaszam
    invoice_number = invoice_number.replace(, -)

    return date, company, invoice_number

def rename_invoice(pdf_path)
    try
        date, company, invoice_number = extract_invoice_data(pdf_path)
        directory = os.path.dirname(pdf_path)
        ext = os.path.splitext(pdf_path)[1]
        new_filename = f{date}_{company}_{invoice_number}{ext}
        new_path = os.path.join(directory, new_filename)

        os.rename(pdf_path, new_path)
        return new_path
    except Exception as e
        return fHiba {e}

def select_file()
    filepath = filedialog.askopenfilename(
        title=Válassz egy PDF számlát,
        filetypes=[(PDF fájlok, .pdf)]
    )
    if filepath
        result = rename_invoice(filepath)
        if os.path.exists(result)
            messagebox.showinfo(Siker, fÁtnevezven{result})
        else
            messagebox.showerror(Hiba, result)

# === GUI ===
root = tk.Tk()
root.title(Számla Átnevező)

root.geometry(400x200)
root.resizable(False, False)

label = tk.Label(root, text=Húzd ide a PDF számlát vagy nyomd meg a gombot, pady=20)
label.pack()

btn = tk.Button(root, text=PDF kiválasztása, command=select_file, width=25, height=2)
btn.pack()

root.mainloop()
