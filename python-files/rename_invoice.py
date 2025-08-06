
import os
import re
from PyPDF2 import PdfReader
from tkinter import filedialog, Tk

def extract_invoice_number(text):
    match = re.search(r"Invoice No\.? ?: *([A-Z0-9]+)", text)
    return match.group(1).strip() if match else None

def main():
    # Hide Tkinter window
    root = Tk()
    root.withdraw()

    # Ask user to select PDF file(s)
    file_paths = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])
    if not file_paths:
        print("No file selected.")
        return

    for pdf_file in file_paths:
        try:
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()

            invoice_number = extract_invoice_number(full_text)
            if invoice_number:
                folder = os.path.dirname(pdf_file)
                new_filename = os.path.join(folder, f"{invoice_number}.pdf")
                os.rename(pdf_file, new_filename)
                print(f"✅ Renamed: {os.path.basename(pdf_file)} → {os.path.basename(new_filename)}")
            else:
                print(f"❌ Invoice number not found in: {os.path.basename(pdf_file)}")

        except Exception as e:
            print(f"⚠️ Error processing {pdf_file}: {e}")

if __name__ == "__main__":
    main()
