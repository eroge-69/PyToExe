import fitz  # PyMuPDF
import pandas as pd


def pdf_to_text(file_path, output_path="output.txt", excel_path="c:\\temp\\output_file1.xlsx"):
    """
    Extracts structured text data from a PDF and saves both plain text and Excel.
    """
    doc = fitz.open(file_path)
    all_text = []

    headers = [
        'PO Number', 'PO Date', 'VENDOR ID', 'SITE ID', 'CONTRACT ID', 'SAP ID',
        'CODE', 'Description', 'Qty', 'UNIT PRICE', 'TOTAL PRICE', 'Total PO Value'
    ]

    # لیست داده‌های هر ستون
    extracted_data = {h: [] for h in headers}

    for page in doc:
        text = page.get_text("text")
        all_text.append(text)

        lines = text.splitlines()

        # بررسی اینکه خطوط لازم وجود دارند
        try:
            row_values = [
                lines[0].split(":")[1].strip(),
                lines[1].split(":")[1].strip(),
                lines[4].split(":")[1].strip(),
                lines[8].split(":")[1].strip(),
                lines[10].split(":")[1].strip(),
                lines[11].split(":")[1].strip(),
                f"{lines[28]} {lines[29]} {lines[30]} {lines[31]}".strip(),
                lines[27].strip(),
                lines[34].strip(),
                lines[35].strip(),
                lines[36].strip(),
                lines[15].split(":")[1].strip(),
            ]

            # حذف کاما برای جلوگیری از مشکل CSV
            row_values = [val.replace(",", "") for val in row_values]

            for h, val in zip(headers, row_values):
                extracted_data[h].append(val)

        except (IndexError, ValueError):
            # اگر صفحه ساختار لازم رو نداشت، رد می‌کنیم
            continue

    doc.close()

    # ذخیره فایل اکسل
    df = pd.DataFrame(extracted_data)
    df.to_excel(excel_path, index=False)

    # ذخیره متن کامل
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))

    return f"Saved text to {output_path} and Excel to {excel_path}"



if __name__ == "__main__":
    print("Nasir Telecom 1404-05")
    print(
        pdf_to_text(
            r"C:\temp\pdf.pdf",
            r"C:\temp\sample1.txt"
        )

    )
