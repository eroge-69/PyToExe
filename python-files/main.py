import os
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader
import pdfplumber

"""
This script helps you organize and copy PDF invoices into neatly named folders based on client codes and invoice dates. 
Here's how it works:

1. It prompts you to select one or more PDF files.
2. It extracts the client code and invoice date from each file's text.
3. It creates a folder named using the extracted details (e.g., "ABC - Invoices - March 20, 2024").
4. It copies each PDF into its corresponding folder.
5. If the script can't extract the necessary details, it places the file in an "Error" folder.
6. After processing all selected files, it lets you know it's done!

It's a simple and efficient way to keep your invoices organized. Happy sorting! 🚀
"""

def extract_info(file_path):
    with pdfplumber.open(file_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

    # Extract client code
    client_code_match = re.search(r'CLIENT\s+([A-Za-z0-9]{3})', text)
    client_code = client_code_match.group(1) if client_code_match else 'Error'

    # Extract invoice/bill date and transform it to 'MMMM DD, YYYY'
    date_match = re.search(r'(INVOICE|BILL) DATE.*?([A-Za-z]{3}\d{2}/\d{2})', text)
    if date_match:
        invoice_date_str = datetime.strptime(date_match.group(2), '%b%d/%y').strftime('%B %d, %Y')
    else:
        invoice_date_str = 'Error'

    return client_code, invoice_date_str

def process_pdf(file_path, output_directory):
    client_code, invoice_date_str = extract_info(file_path)

    # Determine the folder name based on client code and invoice date
    if client_code != 'Error':
        folder_name = f"{client_code} - Invoices - {invoice_date_str}" if invoice_date_str != 'Error' else f"{client_code} Error"
    else:
        folder_name = 'Error'

    # Create folder if it doesn't exist
    folder_path = os.path.join(output_directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Define the output filename and copy the PDF
    output_filename = os.path.join(folder_path, os.path.basename(file_path))
    pdf_writer = PdfWriter()
    pdf_reader = PdfReader(file_path)
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)
    with open(output_filename, 'wb') as out:
        pdf_writer.write(out)
    print(f"Copied: {output_filename}")

def select_pdfs():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(title='Select PDF Files', filetypes=[('PDF Files', '*.pdf')])
    return list(file_paths)

def main():
    pdf_files = select_pdfs()
    output_directory = filedialog.askdirectory(title='Select Output Directory')
    if not output_directory:
        print("No output directory selected, exiting.")
        return

    for file_path in pdf_files:
        print(f"Processing {file_path}...")
        process_pdf(file_path, output_directory)

    print("All files have been processed.")

if __name__ == "__main__":
    main()
