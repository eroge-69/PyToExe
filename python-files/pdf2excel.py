import sys
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def extract_text_and_tables(pdf_path):
    raw_text_pages = []
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            tables = page.extract_tables()

            # Gom bảng
            if tables:
                for table in tables:
                    if table and any(any(cell for cell in row) for row in table):
                        all_tables.append(table)

                        # Loại bỏ text trùng với bảng
                        flat_table_text = [
                            str(cell).strip() for row in table for cell in row if cell
                        ]
                        for t in flat_table_text:
                            if t and t in text:
                                text = text.replace(t, "")

            raw_text_pages.append(text.strip())

    # Nếu không có text → OCR fallback
    if not any(raw_text_pages):
        print("⚠️ Không có text, chuyển sang OCR...")
        pages = convert_from_path(pdf_path)
        for page in pages:
            text = pytesseract.image_to_string(page, lang="eng")
            raw_text_pages.append(text)

    return raw_text_pages, all_tables


def extract_dynamic_headers(all_text):
    """Tách header theo dạng key-value mà không cần biết trước field"""
    header_info = []
    leftover_text = []

    combined_text = "\n".join(all_text)
    lines = combined_text.split("\n")

    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            if key and value:
                header_info.append((key, value))
            else:
                leftover_text.append(line)
        else:
            parts = re.split(r"\s{2,}", line)
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                if key and value:
                    header_info.append((key, value))
                else:
                    leftover_text.append(line)
            else:
                leftover_text.append(line)

    return header_info, leftover_text


def pdf_to_excel_dynamic(pdf_path, excel_path="output.xlsx"):
    raw_text_pages, all_tables = extract_text_and_tables(pdf_path)

    header_info, leftover_text = extract_dynamic_headers(raw_text_pages)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Header
        if header_info:
            header_df = pd.DataFrame(header_info, columns=["Field", "Value"])
            header_df.to_excel(writer, sheet_name="Header", index=False)

        # Raw_Text
        text_df = pd.DataFrame({
            "Line": list(range(1, len(leftover_text) + 1)),
            "Text": leftover_text
        })
        text_df.to_excel(writer, sheet_name="Raw_Text", index=False)

        # Tables
        for i, table in enumerate(all_tables, start=1):
            df = pd.DataFrame(table)
            df.to_excel(writer, sheet_name=f"Table_{i}", index=False, header=False)


def run_gui():
    def select_pdf():
        path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")], title="Chọn file PDF"
        )
        if path:
            entry_pdf.delete(0, tk.END)
            entry_pdf.insert(0, path)

    def select_excel():
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Chọn nơi lưu Excel"
        )
        if path:
            entry_excel.delete(0, tk.END)
            entry_excel.insert(0, path)

    def convert_action():
        pdf_path = entry_pdf.get()
        excel_path = entry_excel.get()
        if not pdf_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file PDF")
            return
        if not excel_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn nơi lưu Excel")
            return
        try:
            pdf_to_excel_dynamic(pdf_path, excel_path)
            messagebox.showinfo("Thành công", f"Đã convert sang Excel:\n{excel_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    root = tk.Tk()
    root.title("PDF → Excel Converter")

    tk.Label(root, text="Chọn PDF:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_pdf = tk.Entry(root, width=50)
    entry_pdf.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=select_pdf).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="Lưu Excel:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_excel = tk.Entry(root, width=50)
    entry_excel.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=select_excel).grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="Convert", command=convert_action, bg="green", fg="white").grid(row=2, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
