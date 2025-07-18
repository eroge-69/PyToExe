import os
from PyPDF2 import PdfReader
import openpyxl

folder_path = os.getcwd()
data = [("Tên File", "Số Trang")]

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(folder_path, filename)
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
        except Exception as e:
            num_pages = f"Lỗi: {e}"
        data.append((filename, num_pages))

excel_path = os.path.join(folder_path, "Thong_ke_so_trang.xlsx")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Thống kê PDF"

for row in data:
    ws.append(row)

wb.save(excel_path)
print(f"✅ Đã lưu: {excel_path}")
input("Nhấn Enter để thoát...")
