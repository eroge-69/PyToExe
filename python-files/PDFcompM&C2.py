import os
import io
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from PIL import Image


def extract_chars(page):
    chars = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                bbox = span.get("bbox", None)
                if not text.strip() or not bbox:
                    continue
                try:
                    x0, y0, x1, y1 = bbox
                    span_width = x1 - x0
                    if len(text) > 0:
                        char_width = span_width / len(text)
                        for i, c in enumerate(text):
                            char_bbox = [x0 + i * char_width, y0, x0 + (i + 1) * char_width, y1]
                            chars.append({"c": c, "bbox": char_bbox})
                except Exception as e:
                    print(f"Skipping span due to error: {e}")
    return chars


def draw_differences_on_page(page1, page2):
    chars1 = extract_chars(page1)
    chars2 = extract_chars(page2)

    doc1_copy = fitz.open("pdf", page1.parent.write())
    doc2_copy = fitz.open("pdf", page2.parent.write())

    draw_page1 = doc1_copy[page1.number]
    draw_page2 = doc2_copy[page2.number]

    for c1, c2 in zip(chars1, chars2):
        if c1["c"] != c2["c"]:
            draw_page1.draw_rect(c1["bbox"], color=(1, 0, 0), width=1)
            draw_page2.draw_rect(c2["bbox"], color=(1, 0, 0), width=1)

    img1 = draw_page1.get_pixmap(dpi=100)
    img2 = draw_page2.get_pixmap(dpi=100)

    return img1, img2


def compare_pdfs(master_path, comparison_path, output_path):
    try:
        doc1 = fitz.open(master_path)
        doc2 = fitz.open(comparison_path)
        output = canvas.Canvas(output_path, pagesize=landscape(A3))
        width, height = landscape(A3)

        max_pages = max(len(doc1), len(doc2))

        for i in range(max_pages):
            page1 = doc1[i] if i < len(doc1) else None
            page2 = doc2[i] if i < len(doc2) else None

            if page1 and page2:
                img1_pix, img2_pix = draw_differences_on_page(page1, page2)
            else:
                img1_pix = page1.get_pixmap(dpi=100) if page1 else None
                img2_pix = page2.get_pixmap(dpi=100) if page2 else None

            output.setFont("Helvetica-Bold", 18)
            output.setFillColorRGB(1, 0, 0)
            output.drawString(100, height - 40, "MASTER")
            output.drawString(width / 2 + 80, height - 40, "REPLICA")

            if img1_pix:
                img1 = ImageReader(io.BytesIO(img1_pix.tobytes("png")))
                output.drawImage(img1, 30, 60, width / 2 - 40, height - 100, preserveAspectRatio=True)

            if img2_pix:
                img2 = ImageReader(io.BytesIO(img2_pix.tobytes("png")))
                output.drawImage(img2, width / 2 + 10, 60, width / 2 - 40, height - 100, preserveAspectRatio=True)

            output.showPage()

        output.save()
        return True
    except Exception as e:
        print("Error comparing PDFs:", e)
        return False


# =================== GUI PART ===================

class PDFComparatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch PDF Comparator")
        self.root.geometry("600x400")
        self.file_pairs = []

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.frame, height=10, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.btn_add = tk.Button(self.frame, text="Add PDF Pair", command=self.add_pair)
        self.btn_add.pack(pady=5)

        self.btn_remove = tk.Button(self.frame, text="Remove Selected", command=self.remove_selected)
        self.btn_remove.pack(pady=5)

        self.btn_process = tk.Button(self.frame, text="Compare PDFs", command=self.process_all)
        self.btn_process.pack(pady=10)

    def add_pair(self):
        master_path = filedialog.askopenfilename(title="Select Master PDF", filetypes=[("PDF Files", "*.pdf")])
        if not master_path:
            return
        comparison_path = filedialog.askopenfilename(title="Select Comparison PDF", filetypes=[("PDF Files", "*.pdf")])
        if not comparison_path:
            return

        self.file_pairs.append((master_path, comparison_path))
        self.listbox.insert(tk.END, f"Master: {os.path.basename(master_path)} | Compare: {os.path.basename(comparison_path)}")

    def remove_selected(self):
        index = self.listbox.curselection()
        if index:
            self.file_pairs.pop(index[0])
            self.listbox.delete(index[0])

    def process_all(self):
        if not self.file_pairs:
            messagebox.showwarning("No Pairs", "Please add PDF file pairs first.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        for master, compare in self.file_pairs:
            master_base = os.path.splitext(os.path.basename(master))[0][:5].upper()
            compare_base = os.path.splitext(os.path.basename(compare))[0][:5].upper()
            output_name = f"comparison_result_{master_base}-{compare_base}.pdf"
            output_path = os.path.join(output_dir, output_name)

            success = compare_pdfs(master, compare, output_path)
            if not success:
                messagebox.showerror("Error", f"Failed to compare: {os.path.basename(master)} and {os.path.basename(compare)}")
                return

        messagebox.showinfo("Success", "All comparisons completed successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFComparatorGUI(root)
    root.mainloop()
