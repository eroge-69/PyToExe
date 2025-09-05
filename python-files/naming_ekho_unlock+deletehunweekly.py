import os
import re
import unicodedata
from datetime import datetime, timedelta
from tkinter import Tk, filedialog
from pypdf import PdfReader, PdfWriter
import pdfplumber


# --- Name and date parsing helpers ---


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def load_hungarian_first_names_local(path="hungarian_names.txt"):
    names = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    names.add(name)
    except FileNotFoundError:
        raise Exception(f"Hungarian names file not found at: {path}")
    return names


def is_first_name(name, names_db):
    name_normalized = remove_accents(name).strip().lower()
    names_normalized = {remove_accents(n).lower() for n in names_db}
    return name_normalized in names_normalized


def parse_name(raw_name, names_db):
    raw_name = raw_name.strip()
    # Remove anything after 'Company' if present
    if "Company" in raw_name:
        raw_name = raw_name.split("Company")[0].strip()

    parts = raw_name.split()
    if len(parts) >= 2:
        if is_first_name(parts[0], names_db):
            reordered = [parts[1], parts[0]] + parts[2:]
            # Return the reordered name WITHOUT accents and uppercase
            reordered_name = " ".join(reordered)
            reorder_no_accents = remove_accents(reordered_name).upper()
            return reorder_no_accents
    # Return original name WITHOUT accents and uppercase if no reorder
    no_accents_name = remove_accents(raw_name).upper()
    return no_accents_name


def get_short_name_code(full_name):
    last_name = full_name.split()[0]
    length = len(last_name)
    if length >= 4:
        return last_name[:4].upper()
    elif length == 3:
        return last_name[:3].upper()
    else:
        return last_name.upper()


def parse_dates(text_snippet):
    date_pattern = r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})|(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})'
    matches = re.findall(date_pattern, text_snippet)
    dates = []
    for m in matches:
        if m[0]:  # yyyy.mm.dd pattern
            try:
                year = int(m[0])
                month = int(m[1])
                day = int(m[2])
                dt = datetime(year, month, day)
                dates.append(dt)
            except Exception:
                continue
        else:  # dd.mm.yyyy or dd.mm.yy
            d1, d2, y = m[3], m[4], m[5]
            if len(y) == 2:
                y = '20' + y
            try:
                dt = datetime(int(y), int(d1), int(d2))
            except ValueError:
                try:
                    dt = datetime(int(y), int(d2), int(d1))
                except ValueError:
                    continue
            dates.append(dt)
    dates.sort()
    return dates


def generate_filename(full_text, names_db):
    full_text = re.sub(r"^Period\s+\d+\s+Starts.*(?:\n.*)*?", "", full_text,
                       flags=re.IGNORECASE | re.MULTILINE)

    name_match = re.search(r"Name:\s*(.+)", full_text, re.IGNORECASE)
    if not name_match:
        raise Exception("Name not found in PDF")
    raw_name = name_match.group(1).strip()
    full_name = parse_name(raw_name, names_db)

    date_pos = full_text.lower().find('date')
    if date_pos == -1:
        raise Exception("Date header not found")
    date_text_snippet = full_text[date_pos:]

    dates = parse_dates(date_text_snippet)
    if not dates:
        raise Exception("No valid dates found")

    first_date_str = dates[0].strftime('%m%d')
    last_date_str = dates[-1].strftime('%m%d')
    day_before_last_str = (dates[-1] - timedelta(days=1)).strftime('%m%d')
    short_code = get_short_name_code(full_name)

    filename = f"{full_name} EKHO - {short_code}_{first_date_str}-{last_date_str} - WE25{day_before_last_str}.pdf"
    return filename


# --- Unlock PDF by rewriting all pages ---


def unlock_pdf(input_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(input_path, "wb") as out_f:
        writer.write(out_f)


# --- PDF page removal for "HETI TELJESÍTÉSI IGAZOLÁS" ---


def remove_certification_page(input_path, keyword="HETI TELJESÍTÉSI IGAZOLÁS"):
    # Use pdfplumber to find offending pages
    with pdfplumber.open(input_path) as pdf:
        remove_indices = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and keyword in text:
                remove_indices.append(i)

    if not remove_indices:
        return False  # No certification page found

    # Remove page(s) from the PDF
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for i in range(len(reader.pages)):
        if i not in remove_indices:
            writer.add_page(reader.pages[i])

    # Save back over the original file
    with open(input_path, "wb") as out_f:
        writer.write(out_f)
    return True


# --- Main processing logic ---


def process_and_rename_pdfs(folder_path, names_db):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)

            try:
                # Unlock the PDF first
                unlock_pdf(file_path)
                print(f"Unlocked PDF: {filename}")

                # Remove certification page if present
                removed = remove_certification_page(file_path)
                if removed:
                    print(f"Certification page removed from {filename}")

                with pdfplumber.open(file_path) as pdf:
                    full_text = ""
                    total_pages = len(pdf.pages)
                    half_pages = max(total_pages // 2, 1)
                    for page in pdf.pages[:half_pages]:
                        page_text = page.extract_text()
                        if page_text:
                            full_text += page_text + "\n"

                new_name = generate_filename(full_text, names_db)
                new_path = os.path.join(folder_path, new_name)
                os.rename(file_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")

            except Exception as e:
                print(f"Failed to process {filename}: {e}")


if __name__ == "__main__":
    print("Loading Hungarian first name list from 'hungarian_names.txt' ...")
    hungarian_first_names = load_hungarian_first_names_local()

    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Input Folder Containing PDFs")
    root.destroy()

    if folder_selected:
        process_and_rename_pdfs(folder_selected, hungarian_first_names)
    else:
        print("No folder selected.")
