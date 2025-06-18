import fitz  # PyMuPDF
import os
import re
from tkinter import Tk, filedialog

def clean_filename(name):
    # Remove or replace illegal filename characters
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

def split_pdf_by_markers(input_pdf_path, output_dir):
    doc = fitz.open(input_pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    start_text = "St Paul and St Timothy's Catholic Infant School"
    end_text = "Mrs Griffin"

    start_page = None
    part_num = 1
    found_any = False

    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"Scanning page {i + 1}")

        if start_page is None and start_text in text:
            print(f"Found start on page {i + 1}")
            start_page = i

        elif start_page is not None and end_text in text:
            print(f"Found end on page {i + 1}")
            end_page = i
            new_doc = fitz.open()

            for j in range(start_page, end_page + 1):
                new_doc.insert_pdf(doc, from_page=j, to_page=j)

            # Extract pupil name from first page
            first_page_text = new_doc[0].get_text()
            pupil_name = None

            # Try multiple regex patterns to find pupil name
            patterns = [
                r'Pupil:\s*([A-Za-z ,.\'-]+)',
                r'Pupil\s*-\s*([A-Za-z ,.\'-]+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, first_page_text, re.IGNORECASE)
                if match:
                    pupil_name = match.group(1).strip()
                    print(f"Extracted pupil name: {pupil_name}")
                    break

            if pupil_name:
                pupil_name = clean_filename(pupil_name)
                # Insert dash between first and second word if applicable
                name_parts = pupil_name.split()
                if len(name_parts) >= 2:
                    pupil_name = name_parts[0] + '-' + ' '.join(name_parts[1:])
                output_filename = f"2- {pupil_name}.pdf"
            else:
                print("No pupil name found, using default filename.")
                output_filename = f"split_part_{part_num}.pdf"

            output_path = os.path.join(output_dir, output_filename)
            new_doc.save(output_path)
            new_doc.close()

            print(f"Saved: {output_path}")

            part_num += 1
            start_page = None
            found_any = True

    doc.close()

    if not found_any:
        print("No matching start/end patterns found. No PDFs were created.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    input_pdf_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )

    if input_pdf_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        split_pdf_by_markers(input_pdf_path, script_dir)
        input("\nDone. Press Enter to exit...")
    else:
        print("No file selected.")
        input("\nPress Enter to exit...")
