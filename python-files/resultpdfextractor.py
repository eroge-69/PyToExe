import os
import re
import pandas as pd
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from pytesseract import image_to_string
from tkinter import filedialog, Tk, messagebox
from PIL import Image

# ✅ Path to Tesseract OCR (change if installed elsewhere)
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSERACT_CMD"] = tesseract_path

# ✅ Ask for PDF files
root = Tk()
root.withdraw()
pdf_files = filedialog.askopenfilenames(
    title="📄 Select Student Result PDF Files",
    filetypes=[("PDF Files", "*.pdf")]
)

if not pdf_files:
    messagebox.showwarning("No Files Selected", "❗ You didn't select any PDF files.")
    exit()

# === PROCESSING ===
all_students = []

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except:
        return ""

def extract_text_with_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path, dpi=300)
        text = ""
        for img in images:
            text += image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"OCR failed for {pdf_path}: {e}")
        return ""

def extract_student_data(text):
    student = {}
    enrol = re.search(r"Enrolment No[:\-]?\s*(\d+)", text)
    name = re.search(r"Candidate Name[:\-]?\s*(.+)", text)

    student["Enrolment No"] = enrol.group(1).strip() if enrol else ""
    student["Candidate Name"] = name.group(1).strip() if name else ""

    marks = re.findall(r"(\d{3})\s*[:\-]?\s*(\d{1,3})", text)
    for code, mark in marks:
        student[code.strip()] = int(mark)

    return student

# === LOOP THROUGH SELECTED FILES ===
for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    print(f"📄 Processing: {filename}")

    text = extract_text_from_pdf(pdf_path)
    if not text or "Enrolment No" not in text:
        print("🧠 Using OCR...")
        text = extract_text_with_ocr(pdf_path)

    if text:
        student_data = extract_student_data(text)
        if student_data.get("Enrolment No"):
            all_students.append(student_data)
        else:
            print(f"⚠️ Skipped {filename}: Missing Enrolment No")
    else:
        print(f"⚠️ Could not extract text from {filename}")

# === SAVE RESULTS ===
if all_students:
    df = pd.DataFrame(all_students)
    output_path = os.path.join(os.path.dirname(pdf_files[0]), "all_students_results.xlsx")
    df.to_excel(output_path, index=False)
    messagebox.showinfo("✅ Done", f"Results saved to:\n{output_path}")
else:
    messagebox.showwarning("No Data Found", "No student data extracted from the selected PDFs.")
