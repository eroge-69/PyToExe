
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

from PyPDF2 import PdfReader

def extract_first_mobile_number(pdf_path):
    pattern = r'09\d{9}'
    try:
        with open(pdf_path, ' 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    match = re.search(pattern, text)
                    if match:
                        return match.group()
    except Exception as e:
        print(f"خطا در فایل {pdf_path}: {e}")
    return "شماره یافت نشد"

def process_folder(folder_path):
    output_lines = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            number = extract_first_mobile_number(pdf_path)
            output_lines.append(f"{filename}: {number}")

    output_file = os.path.join(folder_path, "output.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    messagebox.showinfo("پایان", f"استخراج شماره‌ها انجام شد. خروجی در:\n{output_file}")

def main():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="پوشه حاوی فایل‌های PDF را انتخاب کنید")
    if folder_selected:
        process_folder(folder_selected)

if __name__ == '__main__':
    main()
