import os
import sys
import shutil
from PyPDF2 import PdfReader

def log_message(message, file_path):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"{message}\n")

def check_pdf_pages(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        for i in range(total_pages):
            try:
                _ = reader.pages[i].extract_text()
            except Exception:
                return False
        return True
    except Exception:
        return False

def check_and_move_pdfs(source_folder):
    editable_folder = os.path.join(source_folder, "Editable PDF")
    corrupt_folder = os.path.join(source_folder, "Corrupt PDF")
    log_file = os.path.join(source_folder, "Info.log")

    os.makedirs(editable_folder, exist_ok=True)
    os.makedirs(corrupt_folder, exist_ok=True)

    for file_name in os.listdir(source_folder):
        if file_name.lower().endswith(".pdf"):
            file_path = os.path.join(source_folder, file_name)
            result = check_pdf_pages(file_path)

            if result:
                shutil.move(file_path, os.path.join(editable_folder, file_name))
                log_message(f"File Name - {file_name} - Status valid. - Moved to 'Editable PDF'.", log_file)
            else:
                shutil.move(file_path, os.path.join(corrupt_folder, file_name))
                log_message(f"File Name - {file_name} - Status corrupted. - Moved to 'Corrupt PDF'.", log_file)

if __name__ == "__main__":
    source_folder = sys.argv[1]
    if not os.path.isdir(source_folder):
        sys.exit(1)

    check_and_move_pdfs(source_folder)
