import os
import json
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pdf2docx import Converter
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

# ===== CONFIG =====
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "OUTPUT_FOLDER": "C:\\Users\\OzanKIRAY\\Downloads",
    "POPPLER_PATH": r"C:\\Program Files (x86)\\poppler-24.08.0\\Library\\bin"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
OUTPUT_FOLDER = config["OUTPUT_FOLDER"]
POPPLER_PATH = config["POPPLER_PATH"]
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===== CORE FUNCTIONS =====
def convert_to_jpeg(filepaths):
    results = []
    for filepath in filepaths:
        try:
            name_no_ext = os.path.splitext(os.path.basename(filepath))[0]
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            out_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}.jpeg")
            images[0].save(out_file, "JPEG")
            results.append(out_file)
        except (PDFPageCountError, PDFSyntaxError, Exception) as e:
            results.append(f"Error ({filepath}): {e}")
    return results

def convert_to_docx(filepaths):
    results = []
    for filepath in filepaths:
        try:
            name_no_ext = os.path.splitext(os.path.basename(filepath))[0]
            out_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}.docx")
            cv = Converter(filepath)
            cv.convert(out_file)
            cv.close()
            results.append(out_file)
        except Exception as e:
            results.append(f"Error ({filepath}): {e}")
    return results

def merge_pdfs(filepaths):
    results = []
    try:
        merger = PdfMerger()
        for filepath in filepaths:
            merger.append(filepath)
        out_file = os.path.join(OUTPUT_FOLDER, "merged.pdf")
        merger.write(out_file)
        merger.close()
        results.append(out_file)
    except Exception as e:
        results.append(f"Error: {e}")
    return results

def split_pdfs(filepaths):
    results = []
    for filepath in filepaths:
        try:
            name_no_ext = os.path.splitext(os.path.basename(filepath))[0]
            reader = PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                out_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}_page_{i+1}.pdf")
                with open(out_file, "wb") as out:
                    writer.write(out)
                results.append(out_file)
        except Exception as e:
            results.append(f"Error ({filepath}): {e}")
    return results

# ===== GUI APP =====
class PDFToolsApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("📄 PDF Tools")
        self.geometry("400x320")
        self.configure(bg="white")

        tk.Label(self, text="Drag & Drop PDFs into a box", font=("Arial", 12, "bold"), bg="white").pack(pady=10)

        # Create drop zones
        self.create_drop_zone("🖼 Convert to JPEG", convert_to_jpeg, multiple=True).pack(fill="x", padx=20, pady=5)
        self.create_drop_zone("📄 Convert to DOCX", convert_to_docx, multiple=True).pack(fill="x", padx=20, pady=5)
        self.create_drop_zone("✂️ Split PDF(s)", split_pdfs, multiple=True).pack(fill="x", padx=20, pady=5)
        self.create_drop_zone("📚 Merge PDFs", merge_pdfs, multiple=True).pack(fill="x", padx=20, pady=5)

        # Status label
        self.status = tk.Label(self, text="", fg="green", bg="white", font=("Arial", 9))
        self.status.pack(pady=10)

    def create_drop_zone(self, text, action, multiple=False):
        frame = tk.Label(self, text=text, relief="ridge", borderwidth=2, bg="#f0f0f0",
                         font=("Arial", 11), height=3)
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind('<<Drop>>', lambda e, a=action, m=multiple: self.handle_drop(e, a, m))
        return frame

    def handle_drop(self, event, action, multiple):
        files = self.parse_dnd_files(event.data)
        if not files:
            self.set_status("⚠️ No valid PDF files dropped", error=True)
            return

        if multiple:
            results = action(files)
        else:
            results = [action(files[0])]

        self.set_status(f"✅ Processed {len(files)} file(s). Output in '{OUTPUT_FOLDER}'")

    def parse_dnd_files(self, data):
        files = []
        current = ""
        in_brace = False
        for c in data:
            if c == "{":
                in_brace = True
                current = ""
            elif c == "}":
                in_brace = False
                files.append(current)
                current = ""
            elif c == " " and not in_brace:
                if current:
                    files.append(current)
                    current = ""
            else:
                current += c
        if current:
            files.append(current)
        return [f for f in files if f.lower().endswith(".pdf")]

    def set_status(self, msg, error=False):
        self.status.config(text=msg, fg="red" if error else "green")

# ===== RUN APP =====
if __name__ == "__main__":
    app = PDFToolsApp()
    app.mainloop()
