
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

def extract_black_text(pdf_path):
    doc = fitz.open(pdf_path)
    black_text_blocks = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("type") == 0:  # text block
                for line in b["lines"]:
                    for span in line["spans"]:
                        color = span.get("color", 0)
                        if color == 0:  # black text
                            text = span["text"].strip()
                            if text:
                                black_text_blocks.append((page_num, span))
    return black_text_blocks

def modify_pdf_text(pdf_path, modifications, output_path):
    doc = fitz.open(pdf_path)
    for page_num, span in modifications.items():
        page = doc[page_num]
        for item in span:
            rect = fitz.Rect(item['bbox'])
            page.add_redact_annot(rect, fill=(1, 1, 1))
        doc[page_num].apply_redactions()

    for page_num, span in modifications.items():
        page = doc[page_num]
        for item in span:
            page.insert_text((item['bbox'][0], item['bbox'][1]), item['new_text'], fontsize=item['size'], fontname="helv", fill=(0, 0, 0))

    doc.save(output_path)

def main():
    root = tk.Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(title="选择PDF发票", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    black_texts = extract_black_text(pdf_path)
    if not black_texts:
        messagebox.showinfo("提示", "未找到可编辑的黑色文本。")
        return

    modifications = {}
    for idx, (page_num, span) in enumerate(black_texts):
        old_text = span["text"]
        new_text = simpledialog.askstring("编辑文本", f"原内容: {old_text}\n输入新内容（留空则不修改）:")
        if new_text is not None and new_text != old_text:
            if page_num not in modifications:
                modifications[page_num] = []
            modifications[page_num].append({
                "bbox": span["bbox"],
                "new_text": new_text,
                "size": span["size"]
            })

    if modifications:
        output_path = filedialog.asksaveasfilename(title="保存新PDF", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            modify_pdf_text(pdf_path, modifications, output_path)
            messagebox.showinfo("完成", "PDF修改完成并保存。")
    else:
        messagebox.showinfo("提示", "无修改内容。")

if __name__ == "__main__":
    main()
