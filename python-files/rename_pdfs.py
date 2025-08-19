import os
import re
from PyPDF2 import PdfReader

def clean_filename(name):
    # Remove invalid characters for Windows filenames
    return re.sub(r'[\\/:"*?<>|]+', '', name).strip()

def get_pdf_title_or_first_line(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        # Try to get the title from metadata
        title = reader.metadata.title
        if title:
            return clean_filename(title)
        else:
            # If no title metadata, extract first line of text from first page
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if text:
                first_line = text.strip().split('\n')
                return clean_filename(first_line)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return None

def rename_pdfs_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            full_path = os.path.join(folder_path, filename)
            new_name = get_pdf_title_or_first_line(full_path)
            if new_name:
                new_filename = new_name + '.pdf'
                new_full_path = os.path.join(folder_path, new_filename)
                # Avoid overwriting files
                if new_full_path != full_path and not os.path.exists(new_full_path):
                    print(f"Renaming '{filename}' to '{new_filename}'")
                    os.rename(full_path, new_full_path)
                else:
                    print(f"Skipping '{filename}': target filename exists or same as source")
            else:
                print(f"No title found for '{filename}', skipping.")

if __name__ == '__main__':
    folder = input("Enter the full path to the folder containing PDF books: ").strip()
    if os.path.isdir(folder):
        rename_pdfs_in_folder(folder)
    else:
        print("Invalid folder path.")