#!/usr/bin/env python3
"""
Entry Permit PDF Extractor
--------------------------
Double-click to run (if Python is installed) or use instructions in README to build an EXE.

What it does:
- Prompts you to choose a folder containing PDFs named like: 83056_EP.pdf (employeeID_EP.pdf)
- Extracts fields from each PDF (text-based PDFs, not images/scan-only)
- Produces EntryPermitData.xlsx in the same folder with one row per PDF

Dependencies (for running the script directly):
- Python 3.8+
- PyPDF2
- openpyxl
- tkinter (standard with most Windows Python installs)

To create an EXE (optional):
- Install PyInstaller and run:
    pyinstaller --onefile extractor.py
  (See README.txt included in the package for details.)

Fields extracted (best-effort): EmployeeID, EntryPermitNo, DatePlaceIssue, ValidUntil,
UID, FullName, Nationality, PlaceOfBirth, DateOfBirth, PassportNo, Profession, EmployerName

"""

import os, re, sys
from pathlib import Path
try:
    from PyPDF2 import PdfReader
except Exception as e:
    print("Missing dependency: PyPDF2. Install with: pip install PyPDF2")
    raise SystemExit(1)

try:
    from openpyxl import Workbook
except Exception as e:
    print("Missing dependency: openpyxl. Install with: pip install openpyxl")
    raise SystemExit(1)

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception as e:
    print("tkinter is required (should come with standard Python on Windows).")
    raise SystemExit(1)

# regex helper list
REGEXES = {
    'entry_permit_no': [
        r'ENTRY\s*PERMIT\s*NO[\s:–-]*([0-9/]+)',
        r'Entry Permit No[\s:–-]*([0-9/]+)',
    ],
    'date_place_issue': [
        r'Date\s*&\s*Place\s*of\s*Issue\s*[:\-–]*\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})\s*,?\s*([A-Za-z\u0600-\u06FF ]+)?',
        r'Date\s*&\s*Place\s*of\s*Issue\s*[:\-–]*\s*([0-9\/\-]{6,10})\s+([A-Za-z\u0600-\u06FF ]+)'
    ],
    'valid_until': [
        r'Valid\s*Until\s*[:\-–]*\s*([0-9\/\-]{6,10})',
        r'تاريخ صلاحية الدخول\s*[:\-–]*\s*([0-9\/\-]{6,10})'
    ],
    'uid': [
        r'U\.?I\.?D\.?\s*No\.?\s*[:\-–]*\s*([0-9]{6,15})',
        r'الرقم الموحد\s*[:\-–]*\s*([0-9]{6,15})'
    ],
    'full_name': [
        r'Full\s*Name\s*[:\-–]*\s*(Mr\.|Mrs\.|Ms\.)?\s*([A-Z0-9 \-\'\.]+)',
        r'الاسم الكامل\s*[:\-–]*\s*([A-Z\u0600-\u06FF0-9 \-\'\.]+)'
    ],
    'nationality': [
        r'Nationality\s*[:\-–]*\s*([A-Za-z ]+)',
        r'الجنسية\s*[:\-–]*\s*([A-Za-z\u0600-\u06FF ]+)'
    ],
    'place_of_birth': [
        r'Place\s*of\s*Birth\s*[:\-–]*\s*([A-Z0-9 \-\,\/]+)',
        r'مكان الميلاد\s*[:\-–]*\s*([A-Z0-9 \-\,\/\u0600-\u06FF]+)'
    ],
    'date_of_birth': [
        r'Date\s*of\s*Birth\s*[:\-–]*\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})',
        r'تاريخ الميلاد\s*[:\-–]*\s*([0-9\/\-]{6,10})'
    ],
    'passport_no': [
        r'Passport\s*No\.?\s*[:\-–]*\s*(?:Normal\s*\/\s*)?([A-Z0-9]+)',
        r'رقم الجواز\s*[:\-–]*\s*([A-Z0-9]+)'
    ],
    'profession': [
        r'Profession\s*[:\-–]*\s*([A-Za-z ]+)',
        r'المهنة\s*[:\-–]*\s*([A-Za-z\u0600-\u06FF ]+)'
    ],
    'employer_name': [
        r'Employer[\s\S]{0,30}Name\s*[:\-–]*\s*([A-Z0-9 \.\-&\,]+)',
        r'الاسم\s*[:\-–]*\s*([A-Z0-9 \.\-&\,\u0600-\u06FF]+)'
    ]
}

def extract_text_from_pdf(path):
    text = ""
    try:
        reader = PdfReader(path)
        for p in reader.pages:
            try:
                t = p.extract_text() or ""
            except Exception:
                t = ""
            text += "\\n" + t
    except Exception as e:
        print(f"Failed to read {path}: {e}")
    return text

def find_first(regex_list, text):
    for rx in regex_list:
        m = re.search(rx, text, re.IGNORECASE)
        if m:
            # return last capture group if multiple groups and some empty
            groups = [g for g in m.groups() if g is not None]
            return groups[-1].strip() if groups else m.group(1).strip()
    return ""

def cleanup(s):
    return re.sub(r'\\s+', ' ', s or '').strip()

def process_folder(folder):
    p = Path(folder)
    pdfs = sorted([f for f in p.iterdir() if f.is_file() and f.suffix.lower()=='.pdf'])
    if not pdfs:
        messagebox.showinfo("No PDFs", f"No PDF files found in {folder}")
        return
    wb = Workbook()
    ws = wb.active
    headers = ["EmployeeID","FileName","EntryPermitNo","DatePlaceIssue","ValidUntil","UID","FullName","Nationality","PlaceOfBirth","DateOfBirth","PassportNo","Profession","EmployerName"]
    ws.append(headers)
    for f in pdfs:
        fname = f.name
        empid = fname.split('_')[0]
        text = extract_text_from_pdf(str(f))
        # sometimes text may contain Arabic newline flows; convert to spaces
        text_sp = text.replace('\\r',' ').replace('\\n',' ')
        data = {
            "EmployeeID": empid,
            "FileName": fname,
            "EntryPermitNo": cleanup(find_first(REGEXES['entry_permit_no'], text_sp)),
            "DatePlaceIssue": cleanup(find_first(REGEXES['date_place_issue'], text_sp)),
            "ValidUntil": cleanup(find_first(REGEXES['valid_until'], text_sp)),
            "UID": cleanup(find_first(REGEXES['uid'], text_sp)),
            "FullName": cleanup(find_first(REGEXES['full_name'], text_sp)),
            "Nationality": cleanup(find_first(REGEXES['nationality'], text_sp)),
            "PlaceOfBirth": cleanup(find_first(REGEXES['place_of_birth'], text_sp)),
            "DateOfBirth": cleanup(find_first(REGEXES['date_of_birth'], text_sp)),
            "PassportNo": cleanup(find_first(REGEXES['passport_no'], text_sp)),
            "Profession": cleanup(find_first(REGEXES['profession'], text_sp)),
            "EmployerName": cleanup(find_first(REGEXES['employer_name'], text_sp))
        }
        ws.append([data[h] for h in headers])
        print(f"Processed {fname}")
    out = p / "EntryPermitData.xlsx"
    wb.save(out)
    messagebox.showinfo("Done", f"Extraction complete. Excel saved to:\\n{out}")
    print("Saved:", out)

def main():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select folder containing PDFs (employeeID_EP.pdf)")
    if not folder:
        print("No folder selected. Exiting.")
        return
    process_folder(folder)

if __name__ == "__main__":
    main()
