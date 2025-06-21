import fitz  # PyMuPDF
import re
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
from tkinter import Tk, filedialog
import os


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text.replace('\u00AD', '')  # Удаление мягких дефисов


def extract_blocks_with_ids(text):
    parts = re.split(r'\n(\d{11})\n', text)
    blocks = []
    for i in range(1, len(parts) - 1, 2):
        pub_id = parts[i]
        raw_block = parts[i + 1].strip()
        clean_block = re.sub(r'\s*\n\s*', ' ', raw_block)
        blocks.append((pub_id, clean_block))
    return blocks


def filter_voronezh_blocks(blocks_with_ids):
    pattern = r'в\s*[-]?\s*о\s*[-]?\s*р\s*[-]?\s*о\s*[-]?\s*н\s*[-]?\s*е?\s*[-]?\s*ж\s*([-]?\s*с\s*[-]?\s*к\s*[-]?\с*а\s*[-]?\s*я)?'
    return [
        (pub_id, block)
        for pub_id, block in blocks_with_ids
        if re.search(pattern, block, re.IGNORECASE)
    ]


def save_to_docx(blocks_with_ids, filename):
    doc = Document()
    title = doc.add_paragraph()
    run = title.add_run("Публикация в газете «Коммерсант» от __.__.20__ №___")
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(12)
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT

    for pub_id, block in blocks_with_ids:
        paragraph = doc.add_paragraph(style='List Number')
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.paragraph_format.space_after = Pt(0)

        run_id = paragraph.add_run(f"{pub_id}")
        run_id.bold = True
        run_id.font.name = 'Times New Roman'
        run_id._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
        run_id.font.size = Pt(12)

        paragraph._element.append(OxmlElement('w:br'))

        run_text = paragraph.add_run(block)
        run_text.font.name = 'Times New Roman'
        run_text._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
        run_text.font.size = Pt(12)

    doc.save(filename)


def main():
    # Открываем диалог выбора PDF-файла
    Tk().withdraw()
    pdf_path = filedialog.askopenfilename(title="Выберите PDF-файл", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        print("Файл не выбран.")
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    base_dir = os.path.dirname(pdf_path)

    output_txt = os.path.join(base_dir, f"{base_name}.txt")
    output_docx = os.path.join(base_dir, f"{base_name}.docx")

    full_text = extract_text_from_pdf(pdf_path)
    blocks_with_ids = extract_blocks_with_ids(full_text)
    voronezh_blocks = filter_voronezh_blocks(blocks_with_ids)

    with open(output_txt, "w", encoding="utf-8") as f:
        for i, (pub_id, block) in enumerate(voronezh_blocks, 1):
            f.write(f"{i}. {pub_id}\n{block}\n\n")

    save_to_docx(voronezh_blocks, output_docx)


if __name__ == "__main__":
    main()
