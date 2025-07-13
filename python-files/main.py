# This file is the entry point of the application. It initializes the OCR process, handles PDF file input, and orchestrates the reading, classification, and renaming of files.

import os
from src.ocr.reader import extract_text_from_pdf
from src.utils.excel_writer import write_to_excel

def main():
    input_folder = "path/to/pdf/folder"  # Thư mục chứa file PDF
    output_excel = "output.xlsx"         # Tên file Excel xuất ra

    extracted_data = []

    # Duyệt qua các file PDF trong thư mục
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(input_folder, file_name)
            print(f"Processing {file_name}...")

            # Gọi hàm OCR để trích xuất nội dung
            text = extract_text_from_pdf(file_path)

            # Giả sử bạn phân tích nội dung để lấy ngày và loại văn bản
            # (Cần thêm logic phân tích cụ thể)
            extracted_data.append({
                "File Name": file_name,
                "Content": text,
                "Date": "2025-07-12",  # Ví dụ: ngày giả định
                "Document Type": "Example Type"  # Ví dụ: loại văn bản giả định
            })

    # Xuất dữ liệu ra file Excel
    write_to_excel(extracted_data, output_excel)

if __name__ == "__main__":
    main()