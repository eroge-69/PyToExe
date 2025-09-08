import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image
import pytesseract
import pandas as pd
import os
import re
import threading
import queue
import logging
from datetime import datetime

headers = ["Name", "Date", "Gross Amount", "CGST", "SGST", "IGST", "Invoice Amount", "Invoice No", "Image File"]

COMPANY_PATTERNS = {
    "GREYTIP SOFTWARE PRIVATE LIMITED": {
        "date": [
            r'invoice\s*date[\s:.\-]*([0-3]?\d[\s/.\-](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s/.\-]*\d{2,4})',
            r'invoice\s*date[\s:.\-]*([0-3]?\d[/\-][01]?\d[/\-]\d{2,4})'
        ],
        "gross": [
            r'greyhr\s*subscription\s*fees[\s:.\-]*([\d,]+\.?\d*)',
            r'total\s*:?[\s₹]*([\d,]+\.?\d*)'
        ],
        "cgst": [r'cgst\s*@?\s*9%?[\s:.\-₹]*([\d,]+\.?\d*)'],
        "sgst": [r'sgst\s*@?\s*9%?[\s:.\-₹]*([\d,]+\.?\d*)'],
        "igst": [],
        "invoice_amount": [
            r'total\s*invoice\s*value[\w\s\(\)\-\.]*([\d,]+\.?\d*)',
        ],
        "invoice_no": [
            r'invoice\s*number[\s:.\-]*([a-z0-9/\-_]+)',
            r'\b([A-Z0-9]{2,}(?:[-/][A-Z0-9]+)+)\b'
        ]
    },
    "ATRIA CONVERGENCE TECHNOLOGIES LIMITED": {
        "date": [
            r'invoice\s*date[\s:.\-]*([0-3]?\d[/\-][01]?\d[/\-]\d{2,4})',
        ],
        "gross": [
            r'total\s*charges[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "cgst": [r'cgst[\s:.\-₹]*([\d,]+\.?\d*)'],
        "sgst": [r'sgst[\s:.\-₹]*([\d,]+\.?\d*)'],
        "igst": [],
        "invoice_amount": [
            r'amount\s*payable[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "invoice_no": [
            r'invoice\s*no[\s:.\-]*([a-z0-9/\-_]+)',
            r'\b([A-Z0-9]{2,}(?:[-/][A-Z0-9]+)+)\b'
        ]
    },
    "NETLABS GLOBAL IT SERVICES PVT LTD": {
        "date": [
            r'dated[\s:.\-]*([0-3]?\d[/-](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)-\d{2,4})',
            r'dated[\s:.\-]*([0-3]?\d[/-][01]?\d[/-]\d{2,4})'
        ],
        "gross": [
            r'it\s*services[^\d]{0,20}([\d,]+\.?\d*)'
        ],
        "cgst": [r'cgst\s*@?\s*9%[\s:.\-₹]*([\d,]+\.?\d*)'],
        "sgst": [r'sgst\s*@?\s*9%[\s:.\-₹]*([\d,]+\.?\d*)'],
        "igst": [],
        "invoice_amount": [
            r'total[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "invoice_no": [
            r'invoice\s*no[\s:.\-]*([a-z0-9/\-_]+)',
            r'\b([A-Z0-9]{2,}(?:[-/][A-Z0-9]+)+)\b'
        ]
    },
    "SHYAM SPECTRA PVT. LTD.": {
        "date": [
            r'bill\s*date[\s:.\-]*([0-3]?\d[\s\-](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s,\-]*\d{4})',  # e.g. 24 August, 2025
            r'bill\s*date[\s:.\-]*([0-3]?\d[\s\-](?:january|february|march|april|may|june|july|august|september|october|november|december)[\s,\-]*\d{4})'
        ],
        "gross": [
            r'gross\s*taxable\s*value[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "gst": [
            r'gst[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "invoice_amount": [
            r'current\s*bill\s*charges[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "invoice_no": [
            r'bill\s*number[\s:.\-]*([a-z0-9/\-_]+)',
            r'\b([A-Z0-9]{2,}(?:[-/][A-Z0-9]+)+)\b'
        ]
    },
    "FRUTTA SERVICES PRIVATE LIMITED": {
        "date": [
            r'invoice\s*date[\s:.\-]*([0-3]?\d[/-][01]?\d[/-]\d{2,4})'
        ],
        "gross": [
            r'invoice\s*subtotal[\s:.\-₹]*([\d,]+\.?\d*)',
            r'subtotal[\s:.\-₹]*([\d,]+\.?\d*)'
        ],
        "cgst": [r'cgst[\s:.\-₹]*([\d,]+\.?\d*)'],
        "sgst": [r'sgst[\s:.\-₹]*([\d,]+\.?\d*)'],
        "igst": [],
        "invoice_amount": [r'total[\s:.\-₹]*([\d,]+\.?\d*)'],
        "invoice_no": [
            r'invoice\s*no[\s:.\-]*([a-z0-9/\-_]+)',
            r'\b([A-Z0-9]{2,}(?:[-/][A-Z0-9]+)+)\b'
        ]
    }
}

def extract_company_name(text):
    norm = text.upper()
    for allowed in COMPANY_PATTERNS.keys():
        if allowed in norm:
            return allowed
    if "SPECTRA" in norm:
        return "SHYAM SPECTRA PVT. LTD."
    if "ACT ENTERPRISE" in norm or "ATRIA" in norm:
        return "ATRIA CONVERGENCE TECHNOLOGIES LIMITED"
    return "N/A"

def extract_numbers_by_patterns(patterns, text):
    matches = []
    text = text.lower()
    for pat in patterns:
        matches += re.findall(pat, text, re.IGNORECASE | re.DOTALL)
    flattened = []
    for m in matches:
        if isinstance(m, tuple):
            for g in m:
                if g and re.search(r'\d', g):
                    flattened.append(g.replace(",", ""))
        elif m and re.search(r'\d', m):
            flattened.append(m.replace(",", ""))
    return [float(v) for v in flattened if v]

def extract_by_patterns(patterns, text):
    vals = extract_numbers_by_patterns(patterns, text)
    if vals:
        return f"{max(vals):.2f}"
    return "N/A"

def extract_invoice_no_by_patterns(patterns, text):
    for pat in patterns:
        m = re.findall(pat, text, re.IGNORECASE)
        for item in m:
            item = item[0] if isinstance(item, tuple) else item
            if re.search(r'[-/]', item):
                return item
    return "N/A"

def extract_date_by_patterns(patterns, text):
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            raw = raw.replace('.', '').replace(',', '').strip()
            # Try multiple formats with both abbreviated and full month names
            test_formats = [
                "%d/%m/%Y", "%d/%m/%y",
                "%d-%m-%Y", "%d-%m-%y",
                "%d %b %Y", "%d %b %y",
                "%d %B %Y", "%d %B %y"
            ]
            for fmt in test_formats:
                try:
                    dt = datetime.strptime(raw, fmt)
                    return dt.strftime("%d-%m-%Y")
                except ValueError:
                    continue
            # Try e.g. 24August2025/24August,2025
            m2 = re.match(r'([0-3]?\d)[\s\-]*(January|February|March|April|May|June|July|August|September|October|November|December)[\s\-\,]*(\d{2,4})', raw, re.IGNORECASE)
            if m2:
                d, mon, y = m2.groups()
                monnum = datetime.strptime(mon[:3], "%b").month
                y = y if len(y) == 4 else ('20' + y[-2:])
                return f"{int(d):02d}-{monnum:02d}-{y}"
    return "N/A"

def extract_invoice_fields(text, filename=""):
    company = extract_company_name(text)
    patterns = COMPANY_PATTERNS.get(company, {})
    date_val = extract_date_by_patterns(patterns.get("date", []), text)
    gross_val = extract_by_patterns(patterns.get("gross", []), text)
    inv_amt = extract_by_patterns(patterns.get("invoice_amount", []), text)
    inv_no = extract_invoice_no_by_patterns(patterns.get("invoice_no", []), text)
    cgst_val = sgst_val = igst_val = "N/A"

    if company == "SHYAM SPECTRA PVT. LTD.":
        gst_vals = extract_numbers_by_patterns(patterns.get("gst", []), text)
        if gst_vals:
            g = max(gst_vals)
            cgst_val = sgst_val = f"{g/2:.2f}"
    elif company == "GREYTIP SOFTWARE PRIVATE LIMITED":
        cgst_val = extract_by_patterns(patterns.get("cgst", []), text)
        sgst_val = extract_by_patterns(patterns.get("sgst", []), text)
    elif "cgst" in patterns and "sgst" in patterns:
        cgst_val = extract_by_patterns(patterns.get("cgst", []), text)
        sgst_val = extract_by_patterns(patterns.get("sgst", []), text)

    return {
        "Name": company,
        "Date": date_val,
        "Gross Amount": gross_val,
        "CGST": cgst_val,
        "SGST": sgst_val,
        "IGST": igst_val,
        "Invoice Amount": inv_amt,
        "Invoice No": inv_no,
        "Image File": filename
    }

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    def emit(self, record):
        self.log_queue.put(record)

class OCRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invoice OCR - Date Robust Extractor")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.image_path = None
        self.extracted_data = {}
        self.ocr_text = ""
        ttk.Button(self, text="Select Invoice Image", command=self.select_image).pack(pady=10)
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=5)
        frame = ttk.LabelFrame(self, text="OCR Output & Extracted Data")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.output = ScrolledText(frame, height=18)
        self.output.pack(fill="both", expand=True)
        log_frame = ttk.LabelFrame(self, text="Logs")
        log_frame.pack(fill="x", padx=10, pady=5)
        self.log_text = ScrolledText(log_frame, height=5, state='disabled')
        self.log_text.pack(fill="x", expand=True)
        ttk.Button(self, text="Extract & Save", command=self.run_ocr).pack(pady=8)
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.queue_handler)
        self.after(100, self.poll_log_queue)

    def poll_log_queue(self):
        try:
            while True:
                record = self.log_queue.get(block=False)
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, self.queue_handler.format(record) + "\n")
                self.log_text.configure(state='disabled')
                self.log_text.yview(tk.END)
        except queue.Empty:
            pass
        self.after(100, self.poll_log_queue)

    def select_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        filepath = filedialog.askopenfilename(title="Select Invoice Image", filetypes=filetypes)
        if filepath:
            self.image_path = filepath
            self.logger.info(f"Selected image: {os.path.basename(filepath)}")

    def run_ocr(self):
        if not self.image_path:
            messagebox.showwarning("No Image Selected", "Please select an invoice image first.")
            return
        threading.Thread(target=self.ocr_task, daemon=True).start()
        self.progress.start(10)

    def ocr_task(self):
        try:
            self.logger.info("OCR started...")
            img = Image.open(self.image_path)
            text = pytesseract.image_to_string(img, config='--psm 6')
            self.ocr_text = text.strip()
            self.logger.info(f"OCR finished (first 300 chars): {self.ocr_text[:300]}")
            fields = extract_invoice_fields(self.ocr_text, os.path.basename(self.image_path))
            self.extracted_data = fields
            self.logger.info(f"Extraction complete: {fields}")
            self.after(0, self.show_result)
            self.after(0, self.save_to_excel)
        except Exception as e:
            self.logger.error(f"OCR/Extraction failed: {e}")
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, self.progress.stop)

    def show_result(self):
        self.output.delete(1.0, tk.END)
        text = "Extracted fields for this invoice:\n"
        for k, v in self.extracted_data.items():
            text += f"{k}: {v}\n"
        text += "\nOCR Text Preview (first 400 chars):\n" + self.ocr_text[:400]
        self.output.insert(tk.END, text)

    def save_to_excel(self):
        try:
            file = "invoices_combined.xlsx"
            cols = headers
            new_entry = pd.DataFrame([self.extracted_data], columns=cols)
            if os.path.exists(file):
                old = pd.read_excel(file, engine="openpyxl")
                df = pd.concat([old, new_entry], ignore_index=True)
            else:
                df = new_entry
            df.to_excel(file, index=False, engine="openpyxl")
            self.logger.info(f"Saved extracted data to {file}")
            messagebox.showinfo("Success", f"Invoice data saved to {file}")
        except Exception as e:
            self.logger.error(f"Excel save failed: {e}")
            messagebox.showerror("Save Error", str(e))

if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()
