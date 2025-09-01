import pandas as pd
import re
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import xlsxwriter

# نافذة اختيار ملف الإكسل
Tk().withdraw()
file_path = askopenfilename(title="اختر ملف Excel")

# قراءة الملف
full_df = pd.read_excel(file_path, sheet_name=0, skiprows=0)

# الحصول على جميع الأعمدة
all_cols_data = []
for i in range(full_df.shape[1]):
    all_cols_data.append(full_df.iloc[:, i].fillna('').astype(str).tolist())

main_tape_col_data = all_cols_data[0]

def extract_tape_info(tape_block_data_by_column):
    tape_seq = ""
    tape_number = ""
    barcode_id = ""

    if tape_block_data_by_column and tape_block_data_by_column[0]:
        for i in range(min(3, len(tape_block_data_by_column[0]))):
            m_seq = re.search(r"ت\s*س\s*ل\s*س\s*ل\s*ـ*\s*الش\s*ر\s*ي\s*ط\s*/\s*(\d+)", tape_block_data_by_column[0][i])
            if m_seq:
                tape_seq = m_seq.group(1)
                break

    search_lines_for_tape_num = []
    for i in range(min(5, len(tape_block_data_by_column[0]) if tape_block_data_by_column else 0)):
        combined_row_content = ""
        for col_data in tape_block_data_by_column:
            if i < len(col_data):
                combined_row_content += col_data[i] + " "
        search_lines_for_tape_num.append(combined_row_content.strip())

    for line in search_lines_for_tape_num:
        m_num = re.search(r"ر\s*ق\s*ـ*\s*م\s*\s*الش\s*ر\s*ي\s*ط\s*/\s*(.+)", line)
        if m_num:
            raw_tape_number = m_num.group(1)
            cleaned_tape_number = re.sub(r'\s+', '', raw_tape_number)

            if re.match(r"ا\s*ل\s*ر\s*ي\s*ا\s*ض\s*ي\s*ة", cleaned_tape_number):
                tape_number = "الرياضية"
            else:
                tape_number = cleaned_tape_number
            break

    if not tape_seq:
        return None

    barcode_patterns_combined = re.compile(
        r"Barcode\s*ID\s*(\d+)|"
        r"(SBA-\d+)|"
        r"(?:Identifier\s*[:/]?\s*(\S+))|"
        r"(1(?:0{10,}|0{20,})\d+)|"
        r"(1\d{8,})|"
        r"(\d{15,})"
    )

    if len(tape_block_data_by_column) > 1 and tape_block_data_by_column[1]:
        search_scope_paragraph_for_barcode = tape_block_data_by_column[1][:50]
        for line in search_scope_paragraph_for_barcode:
            m_barcode = barcode_patterns_combined.search(line)
            if m_barcode:
                for group in m_barcode.groups():
                    if group:
                        barcode_id = group.strip()
                        break
                if barcode_id:
                    break

    material = ""
    if tape_block_data_by_column and len(tape_block_data_by_column[0]) > 1:
        m2 = re.search(r"المـ*ادة\s*/\s*(.+)", tape_block_data_by_column[0][1])
        material = m2.group(1).strip() if m2 else ""

    presenter = ""
    if tape_block_data_by_column and len(tape_block_data_by_column[0]) > 2:
        m_presenter = re.search(r"تقـ*ديـ*م\s*/\s*(.+)", tape_block_data_by_column[0][2])
        presenter = m_presenter.group(1).strip() if m_presenter else ""

    director = ""
    if tape_block_data_by_column and len(tape_block_data_by_column[0]) > 3:
        m_director = re.search(r"إخـ*راج\s*/\s*(.+)", tape_block_data_by_column[0][3])
        director = m_director.group(1).strip() if m_director else ""

    date = ""
    if tape_block_data_by_column and len(tape_block_data_by_column[0]) > 4:
        m_date = re.search(r"تاريخ\s*(?:النسـ*خ|التسجيل)\s*/\s*([\d\s\/\-\هـ]+)\s*", tape_block_data_by_column[0][4])
        if m_date:
            date = m_date.group(1).strip().replace(" ", "")

    paragraph = ""
    if len(tape_block_data_by_column) > 1 and tape_block_data_by_column[1]:
        relevant_paragraph_lines = tape_block_data_by_column[1][7:35]
        filtered_paragraph_lines = []
        for line in relevant_paragraph_lines:
            stripped_line = line.strip()
            if not re.match(r"^ص\s*\d+", stripped_line):
                if stripped_line:
                    filtered_paragraph_lines.append(stripped_line)
        paragraph = "\n".join(filtered_paragraph_lines)

    return {
        "تسلسل الشريط": tape_seq,
        "رقم الشريط": tape_number,
        "المادة": material,
        "تقديم": presenter,
        "إخراج": director,
        "تاريخ التسجيل": date,
        "الفقرة": paragraph,
        "Barcode ID": barcode_id
    }

# استخراج بدايات الشرائط
tape_start_pattern = r"ت\s*س\s*ل\s*س\s*ل\s*ـ*\s*الش\s*ر\s*ي\s*ط\s*/\s*(\d+)"
start_indices = [i for i, line in enumerate(main_tape_col_data) if re.search(tape_start_pattern, line)]

tapes_data = []
for idx, start in enumerate(start_indices):
    end = start_indices[idx + 1] if idx + 1 < len(start_indices) else len(main_tape_col_data)
    tape_block_data_by_column = [col_list[start:end] for col_list in all_cols_data]
    extracted_info = extract_tape_info(tape_block_data_by_column)
    if extracted_info:
        tapes_data.append(extracted_info)

df = pd.DataFrame(tapes_data)

# ترتيب الأعمدة
desired_column_order = [
    "تسلسل الشريط",
    "رقم الشريط",
    "Barcode ID",
    "المادة",
    "تاريخ التسجيل",
    "إخراج",
    "تقديم",
    "الفقرة"
]

df = df[desired_column_order]

# حفظ الملف
output_filename = "جدول_الشرائط_موسع.xlsx"
writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
df.to_excel(writer, index=False, sheet_name='البيانات')

workbook = writer.book
worksheet = writer.sheets['البيانات']
worksheet.right_to_left()

writer.close()

print(f"تم حفظ الملف: {output_filename}")
