import pandas as pd
import os
import shutil
from datetime import datetime
import pdfrw
from pdfrw import PdfReader, PdfWriter
import fitz  # PyMuPDF
import math

# ---------------------------- CONFIG ----------------------------

EXCEL_FILE = 'Lacey Act Data.xlsx'
FORM1_TEMPLATE = 'Lacey Act Form 1.pdf'
FORM2_TEMPLATE = 'Lacey Act Form 2.pdf'
MAX_FORM1_ROWS = 6
MAX_FORM2_ROWS = 13

FIELD_MAP = {
    '11 HTSUS NUMBER no dashessymbols': 'Commodity Code',
    '12 ENTERED VALUE': 'Entered Value',
    '13 ARTICLECOMPONENT OF ARTICLE': 'Description',
    '14 PLANT SCIENTIFIC NAME Genus Species': 'Genus',
    '14 PLANT SCIENTIFIC NAME Genus Species_2': 'Species',
    '15 COUNTRY OF HARVEST': 'Country Of Harvest',
    '16 QUANTITY OF PLANT MATERIAL': 'Quantity of Plant Material',
    '17 UNIT': 'g',  # <-- Static value
    '18 PERCENT RECYCLED': '0'  # <-- Static value
}

# ---------------------------- FUNCTIONS ----------------------------

def regenerate_visible_form_values(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        widgets = page.widgets()
        if widgets is None:
            continue
        for widget in widgets:
            if widget.field_value:
                widget.update()
    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def list_all_fields(pdf_path):
    pdf = PdfReader(pdf_path)
    print(f"\n📄 FIELD NAMES in {pdf_path}:\n")
    for page in pdf.pages:
        if '/Annots' in page:
            for annot in page['/Annots']:
                if annot['/Subtype'] == '/Widget' and annot.get('/T'):
                    field_name = annot['/T'][1:-1]
                    print(field_name)


def get_today_folder(prefix='Filled Lacey Acts'):
    base_name = datetime.today().strftime(f"{prefix} %Y-%m-%d")
    suffix = 1
    while True:
        folder_name = f"{base_name} {suffix:03}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            return folder_name
        suffix += 1


def clean_value(v):
    try:
        return str(v).replace(',', '.').strip()
    except:
        return v


def duplicate_pdf(template_path, dest_path):
    shutil.copy(template_path, dest_path)


def fill_fields(pdf_path, row_data, start_index=1, page_number=None, total_pages=None):
    pdf = PdfReader(pdf_path)

    if hasattr(pdf, 'Root') and hasattr(pdf.Root, 'AcroForm'):
        pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

    total_rows = len(row_data)

    for page in pdf.pages:
        if '/Annots' not in page:
            continue
        for annotation in page['/Annots']:
            if annotation['/Subtype'] != '/Widget' or '/T' not in annotation:
                continue

            key = annotation['/T'][1:-1]  # remove parentheses

            # 📄 Handle static page fields
            if key == "PageNumber" and page_number is not None:
                annotation.update(pdfrw.PdfDict(V=str(page_number)))
                continue
            elif key == "TotalPages" and total_pages is not None:
                annotation.update(pdfrw.PdfDict(V=str(total_pages)))
                continue

            # Row-based fields (as before)
            row_num = None
            if 'Row' in key:
                try:
                    row_num = int(key.split('Row')[1].split('_')[0])
                except ValueError:
                    continue

            if row_num is None:
                continue

            data_index = row_num - start_index
            if data_index < 0 or data_index >= total_rows:
                continue
            row = row_data[data_index]

            for fkey, excel_col in FIELD_MAP.items():
                if fkey.endswith('_2'):
                    base = fkey.replace('_2', '')
                    expected_key = f"{base}Row{row_num}_2"
                else:
                    expected_key = f"{fkey}Row{row_num}"

                if key.strip() == expected_key.strip():
                    if excel_col in row:
                        value = clean_value(row[excel_col])
                    elif excel_col in ['g', '0']:
                        value = excel_col  # static default
                    else:
                        value = ''

                    print(f"→ Filling {expected_key}: {value}")
                    annotation.update(pdfrw.PdfDict(V='{}'.format(value)))
                    break

    PdfWriter(trailer=pdf).write(pdf_path)


# ---------------------------- MAIN ----------------------------

def main():
    df = pd.read_excel(EXCEL_FILE, sheet_name='Data')
    total_rows = len(df)
    overflow_rows = max(0, total_rows - MAX_FORM1_ROWS)
    extra_pages = math.ceil(overflow_rows / MAX_FORM2_ROWS)
    total_pages = 1 + extra_pages

    folder = get_today_folder()

    form1_data = df.iloc[:MAX_FORM1_ROWS]
    remaining = df.iloc[MAX_FORM1_ROWS:]

    # --- Fill Form 1 ---
    form1_output = os.path.join(folder, 'Filled Lacey Form PPQ505.pdf')
    duplicate_pdf(FORM1_TEMPLATE, form1_output)
    fill_fields(form1_output, form1_data.to_dict(orient='records'), start_index=1)
    regenerate_visible_form_values(form1_output)
    print(f"✅ Form 1 saved to: {form1_output}")

    # --- Fill Form 2 and extensions ---
    for i in range(0, len(remaining), MAX_FORM2_ROWS):
        chunk = remaining.iloc[i:i + MAX_FORM2_ROWS]
        page_number = (i // MAX_FORM2_ROWS) + 1
        form2_output = os.path.join(folder, f"Filled Lacey Form PPQ505B {page_number}.pdf")
        duplicate_pdf(FORM2_TEMPLATE, form2_output)

        current_page = 2 + (i // MAX_FORM2_ROWS)
        fill_fields(
            form2_output,
            chunk.to_dict(orient='records'),
            start_index=1,
            page_number=current_page,
            total_pages=total_pages
        )
        regenerate_visible_form_values(form2_output)
        print(f"→ Filling Page {current_page} of {total_pages}")
        print(f"✅ {page_number} saved to: {form2_output}")


if __name__ == "__main__":
    main()
