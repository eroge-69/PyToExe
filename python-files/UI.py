import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
from pathlib import Path
import threading

# ---- Marker-Erkennung ----
def is_marker(pix, box_size=200, threshold=60, black_ratio=0.05):
    w, h = pix.width, pix.height
    img = pix.samples
    n = pix.n
    black_pixels = 0
    total = 0
    for y in range(0, min(box_size, h)):
        for x in range(0, min(box_size, w)):
            offset = (y * w + x) * n
            gray = sum(img[offset:offset+3]) / 3
            if gray < threshold:
                black_pixels += 1
            total += 1
    ratio = black_pixels / total
    return ratio > black_ratio, ratio

# ---- PDF split ----
def split_pdf_by_marker(input_pdf, output_folder="output", log=lambda msg: print(msg)):
    doc_fitz = fitz.open(input_pdf)
    log(f"[INFO] PDF geladen: {input_pdf} ({len(doc_fitz)} Seiten)")

    marker_pages = []
    for i in range(len(doc_fitz)):
        page = doc_fitz[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # hohe Auflösung
        marker, ratio = is_marker(pix, box_size=200, threshold=60, black_ratio=0.05)
        if marker:
            marker_pages.append(i)
            log(f"[MARKER] erkannt auf Seite {i+1} ({ratio*100:.1f}% schwarze Pixel)")

    if not marker_pages:
        log("[WARNUNG] Keine Marker gefunden, es wird nur eine Datei erstellt.")
        marker_pages = [0]

    marker_pages.append(len(doc_fitz))

    reader = PdfReader(input_pdf)
    out_dir = Path(output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(len(marker_pages)-1):
        start, end = marker_pages[idx], marker_pages[idx+1]
        writer = PdfWriter()
        for p in range(start, end):
            writer.add_page(reader.pages[p])
        out_path = out_dir / f"Arztbrief_{idx+1}.pdf"
        with out_path.open("wb") as f:
            writer.write(f)
        log(f"[EXPORT] {out_path} (Seiten {start+1}–{end})")

    log("[FERTIG] Alle Arztbriefe gespeichert.")

# ---- GUI ----
class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arztbrief-Splitter")
        self.root.geometry("600x400")

        self.file_path = None

        self.btn_select = tk.Button(root, text="PDF auswählen", command=self.select_file)
        self.btn_select.pack(pady=10)

        self.btn_start = tk.Button(root, text="Start", command=self.start_split, state=tk.DISABLED)
        self.btn_start.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Dateien", "*.pdf")])
        if path:
            self.file_path = path
            self.text_area.insert(tk.END, f"[INFO] Datei ausgewählt: {path}\n")
            self.text_area.see(tk.END)
            self.btn_start.config(state=tk.NORMAL)

    def start_split(self):
        if not self.file_path:
            messagebox.showerror("Fehler", "Bitte zuerst eine PDF auswählen!")
            return

        # Thread, damit GUI nicht einfriert
        threading.Thread(target=self.run_split).start()

    def run_split(self):
        def log(msg):
            self.text_area.insert(tk.END, msg + "\n")
            self.text_area.see(tk.END)
            self.root.update_idletasks()

        split_pdf_by_marker(self.file_path, output_folder="output", log=log)

# ---- Main ----
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterApp(root)
    root.mainloop()
