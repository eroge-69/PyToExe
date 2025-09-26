"""
pdf_to_jpg_gui.py
PDF -> JPG dönüştürücü (Tkinter GUI + sürükle-bırak + çoklu dosya).

Gereksinimler:
  pip install pymupdf pillow tkinterdnd2

Çalıştırma:
  python pdf_to_jpg_gui.py

.exe yapmak için:
  pyinstaller --onefile --noconsole pdf_to_jpg_gui.py
"""

import fitz
import os
from tkinter import Tk, filedialog, Button, Label, Entry, StringVar, IntVar, messagebox, Listbox, END, Scrollbar, RIGHT, Y
from PIL import Image

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def pdf_to_jpg(pdf_path, outdir, dpi=150, quality=85):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        messagebox.showerror("Hata", f"PDF açılamadı: {e}")
        return

    base = os.path.splitext(os.path.basename(pdf_path))[0]
    doc_out = os.path.join(outdir, base)
    ensure_dir(doc_out)

    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)

    for pno in range(doc.page_count):
        try:
            page = doc.load_page(pno)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            if mode == "RGBA":
                img = img.convert("RGB")

            out_name = f"{base}_page{pno+1}.jpg"
            out_path = os.path.join(doc_out, out_name)
            img.save(out_path, "JPEG", quality=quality)
        except Exception as e:
            messagebox.showwarning("Uyarı", f"Sayfa {pno+1} dönüştürülemedi: {e}")

    doc.close()
    return doc_out


class PDF2JPGApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF -> JPG Dönüştürücü")
        master.geometry("500x400")

        self.outdir = StringVar(value="./output")
        self.dpi = IntVar(value=150)
        self.quality = IntVar(value=85)

        Label(master, text="Seçilen PDF Dosyaları:").pack(anchor="w", padx=10, pady=5)

        self.listbox = Listbox(master, selectmode="extended")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(self.listbox, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        Button(master, text="PDF Ekle", command=self.select_pdfs).pack(pady=5)
        Button(master, text="Seçiliyi Sil", command=self.remove_selected).pack(pady=5)

        Label(master, text="Çıktı Klasörü:").pack(anchor="w", padx=10, pady=5)
        Button(master, text="Klasör Seç", command=self.select_outdir).pack(padx=10)
        Label(master, textvariable=self.outdir, fg="blue").pack(anchor="w", padx=10)

        Label(master, text="DPI:").pack(anchor="w", padx=10, pady=5)
        Entry(master, textvariable=self.dpi).pack(padx=10)

        Label(master, text="Kalite (1-100):").pack(anchor="w", padx=10, pady=5)
        Entry(master, textvariable=self.quality).pack(padx=10)

        Button(master, text="Dönüştür", command=self.convert_all).pack(pady=15)

        if DND_AVAILABLE:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind('<<Drop>>', self.drop_files)

    def select_pdfs(self):
        paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for p in paths:
            if p not in self.listbox.get(0, END):
                self.listbox.insert(END, p)

    def remove_selected(self):
        selection = list(self.listbox.curselection())
        selection.reverse()
        for i in selection:
            self.listbox.delete(i)

    def select_outdir(self):
        path = filedialog.askdirectory()
        if path:
            self.outdir.set(path)

    def convert_all(self):
        files = self.listbox.get(0, END)
        if not files:
            messagebox.showwarning("Eksik Bilgi", "PDF dosyası seçilmedi.")
            return

        for f in files:
            out = pdf_to_jpg(f, self.outdir.get(), dpi=self.dpi.get(), quality=self.quality.get())
            if out:
                print(f"Tamamlandı: {out}")

        messagebox.showinfo("Bitti", "Tüm PDF dosyaları dönüştürüldü.")

    def drop_files(self, event):
        files = event.data.strip().split()
        for f in files:
            f = f.strip("{}")  # bazı sistemlerde path süslü parantez içinde gelir
            if f.lower().endswith(".pdf") and f not in self.listbox.get(0, END):
                self.listbox.insert(END, f)


if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = Tk()
    app = PDF2JPGApp(root)
    root.mainloop()
