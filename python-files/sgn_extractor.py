import fitz  # PyMuPDF
import pandas as pd
import re
import sys
import os

def extract_address_mprn_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    data = []

    for page in doc:
        text = page.get_text()
        matches = re.findall(r'MPRN:\s*(\d+)\s*Address:\s*(.+?)(?=MPRN:|\Z)', text, re.DOTALL)
        for mprn, address in matches:
            cleaned_address = ' '.join(address.strip().split())
            data.append({'Address': cleaned_address, 'MPRN': mprn})

    doc.close()
    return data

def export_to_excel(data, output_path):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    print(f"Data successfully exported to {output_path}")

def process_sgn_service_card(pdf_path, output_excel_path):
    extracted_data = extract_address_mprn_from_pdf(pdf_path)
    export_to_excel(extracted_data, output_excel_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: sgn_extractor.exe <input_pdf_path> <output_excel_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_excel = sys.argv[2]

    if not os.path.exists(input_pdf):
        print(f"Error: File '{input_pdf}' does not exist.")
        sys.exit(1)

    process_sgn_service_card(input_pdf, output_excel)
