import pdfplumber
import os
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox

# === Ask user to select PDF folder ===
root = tk.Tk()
root.withdraw()
folder = filedialog.askdirectory(title="Select Folder Containing PDF Files")
if not folder:
    messagebox.showinfo("Cancelled", "No folder selected. Exiting.")
    exit()

# === Prepare Excel file ===
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["File Name", "Interface Title", "Cluster", "Discipline", "Coordinates", "Originator", "Interface Partner", "Issue Date"])

def get_between(txt, start, end):
    try:
        s = txt.index(start) + len(start)
        e = txt.index(end, s)
        return txt[s:e].strip()
    except ValueError:
        return ""

# === Loop through PDFs ===
for filename in os.listdir(folder):
    if filename.lower().endswith(".pdf"):
        path = os.path.join(folder, filename)
        with pdfplumber.open(path) as pdf:
            text = ""
            # Read only first 5 pages
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"

        ws.append([
            filename,
            get_between(text, "Interface Title:", "Region"),
            get_between(text, "Cluster:", "Partner Cluster:"),
            get_between(text, "Discipline:", "Current Project Stage:"),
            get_between(text, "Identify Stage:", "Interface Leader:"),
            get_between(text, "Originator/Leader:", "Interface Partner:"),
            get_between(text, "Interface Partner:", "Issue Date:"),
            get_between(text, "Issue Date:", "Revision:")
        ])

# === Save output Excel in same folder ===
output_path = os.path.join(folder, "Extracted_PDF_Data.xlsx")
wb.save(output_path)

messagebox.showinfo("Done", f"Data extraction complete!\nSaved to:\n{output_path}")