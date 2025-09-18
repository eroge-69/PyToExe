import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext
import fitz  # PyMuPDF

# ---------------- GUI Browsing ----------------
def browse_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    label_pdf_file.config(text=file_path if file_path else "No file selected")

def browse_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    label_csv_file.config(text=file_path if file_path else "No file selected")

def browse_folder():
    folder_path = filedialog.askdirectory()
    label_folder.config(text=folder_path if folder_path else "No folder selected")

# ---------------- PDF Processing ----------------
def split_pdf_by_keywords(pdf_path, csv_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = pd.read_csv(csv_path)
    keywords = df['keywords'].astype(str).tolist()

    total_pages = get_total_pages(pdf_path)
    pages_found = search_keyword_in_pdf(pdf_path, keywords)
    end_pages = calculate_end_pages(pages_found, total_pages)

    df['found_page'] = pages_found
    df['end_page'] = end_pages

    for idx, row in df.iterrows():
        found_page = row['found_page']
        end_page = row['end_page']
        keyword = row['keywords']
        extract_pdf_pages_fitz(pdf_path, found_page, end_page, output_dir, keyword)

    df.to_csv(csv_path, index=False)
    log(f"บันทึกข้อมูลสำเร็จที่ {csv_path}")

def get_total_pages(pdf_path):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    return total_pages

def search_keyword_in_pdf(pdf_path, keywords):
    results = []
    doc = fitz.open(pdf_path)
    for word in keywords:
        found_page = None
        for i in range(1, len(doc)):  # เริ่มจากหน้า 2
            page = doc[i]
            try:
                text = page.get_text("text")
                if text and word.lower() in text.lower():
                    found_page = i + 1
                    break
            except Exception as e:
                log(f"เกิดข้อผิดพลาดหน้า {i+1}: {e}")
        results.append(found_page)
    doc.close()
    return results

def calculate_end_pages(found_pages, total_pages):
    end_pages = []
    i = 0
    while i < len(found_pages):
        found_page = found_pages[i]
        if found_page is None:
            end_pages.append(None)
            i += 1
            continue
        if i + 1 < len(found_pages):
            j = i + 1
            while j < len(found_pages) and found_pages[j] is None:
                j += 1
            end_page = found_pages[j] - 1 if j < len(found_pages) else total_pages
        else:
            end_page = total_pages
        end_pages.append(end_page)
        i += 1
    return end_pages

def extract_pdf_pages_fitz(pdf_path, found_page, end_page, output_folder, keyword):
    doc = fitz.open(pdf_path)
    if found_page is None or end_page is None:
        log(f"ข้าม {keyword}: found_page หรือ end_page เป็น None")
        doc.close()
        return

    try:
        found_page = int(found_page)
        end_page = int(end_page)
    except ValueError:
        log(f"ข้าม {keyword}: ไม่สามารถแปลงหน้าเป็น int (found_page={found_page}, end_page={end_page})")
        doc.close()
        return

    new_pdf = fitz.open()
    for pno in range(found_page - 1, end_page):
        new_pdf.insert_pdf(doc, from_page=pno, to_page=pno)

    safe_keyword = "".join([c if c.isalnum() or c in "_-" else "_" for c in keyword])
    output_path = os.path.join(output_folder, f"{safe_keyword}.pdf")

    try:
        new_pdf.save(output_path)
        log(f"บันทึกไฟล์ PDF: {output_path}")
    except Exception as e:
        log(f"ไม่สามารถบันทึกไฟล์ {safe_keyword}.pdf: {e}")
    finally:
        new_pdf.close()
        doc.close()

# ---------------- Logging ----------------
def log(message):
    log_output.config(state=tk.NORMAL)
    log_output.insert(tk.END, message + "\n")
    log_output.see(tk.END)
    log_output.config(state=tk.DISABLED)

# ---------------- Run Program ----------------
def run_program():
    pdf_path = label_pdf_file.cget("text")
    csv_path = label_csv_file.cget("text")
    output_dir = label_folder.cget("text")

    if "No file selected" in (pdf_path, csv_path, output_dir):
        log("Please select PDF, CSV, and output folder before running.")
        return
    log("Running program...")
    split_pdf_by_keywords(pdf_path, csv_path, output_dir)
    log("Program finished successfully!")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Extract PDF and CSV")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(fill=tk.X, padx=10, pady=10)

# PDF
pdf_frame = tk.Frame(frame)
pdf_frame.pack(fill=tk.X, anchor="w", pady=5)
tk.Button(pdf_frame, text="Main PDF", command=browse_pdf).pack(side=tk.LEFT, padx=5)
label_pdf_file = tk.Label(pdf_frame, text="No file selected", wraplength=450, anchor="w")
label_pdf_file.pack(side=tk.LEFT, padx=5)
tk.Label(frame, text="PDF Daily-Request ที่ต้องการ Extract File", font=("Arial", 8), fg="gray").pack(anchor="w", pady=5)

# CSV
csv_frame = tk.Frame(frame)
csv_frame.pack(fill=tk.X, anchor="w", pady=5)
tk.Button(csv_frame, text="Main CSV", command=browse_csv).pack(side=tk.LEFT, padx=5)
label_csv_file = tk.Label(csv_frame, text="No file selected", wraplength=450, anchor="w")
label_csv_file.pack(side=tk.LEFT, padx=5)
tk.Label(frame, text="CSV File ที่ต้องการ Extract Data", font=("Arial", 8), fg="gray").pack(anchor="w", pady=5)

# Output Folder
folder_frame = tk.Frame(frame)
folder_frame.pack(fill=tk.X, anchor="w", pady=5)
tk.Button(folder_frame, text="Output Folder", command=browse_folder).pack(side=tk.LEFT, padx=5)
label_folder = tk.Label(folder_frame, text="No folder selected", wraplength=450, anchor="w")
label_folder.pack(side=tk.LEFT, padx=5)
tk.Label(frame, text="Folder ที่ต้องการบันทึกผลลัพธ์", font=("Arial", 8), fg="gray").pack(anchor="w", pady=5)

# Run Button
tk.Button(root, text="Run Program", command=run_program).pack(pady=20)

# ScrolledText
log_output = scrolledtext.ScrolledText(root, width=70, height=15, wrap=tk.WORD, state=tk.DISABLED)
log_output.pack(padx=10, pady=10)

root.mainloop()
