import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import PyPDF2
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET
from PIL import Image

class FileConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("File Format Converter - sided0or v1.0")
        root.geometry("500x300")
        root.resizable(False, False)

        mainframe = ttk.Frame(root, padding=10)
        mainframe.pack(fill='both', expand=True)

        # — Input file selector —
        ttk.Label(mainframe, text="Input File:").grid(row=0, column=0, sticky='w')
        self.input_entry = ttk.Entry(mainframe, width=40)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(mainframe, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5)

        # — Output format chooser —
        ttk.Label(mainframe, text="Output Format:").grid(row=1, column=0, sticky='w')
        self.format_combo = ttk.Combobox(mainframe, values=['txt','pdf','xml'], state='readonly')
        self.format_combo.current(0)
        self.format_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # — Convert button —
        self.convert_btn = ttk.Button(mainframe, text="Convert", command=self.start_conversion)
        self.convert_btn.grid(row=2, column=1, pady=15)

        # — Progress bar & status —
        self.progress = ttk.Progressbar(mainframe, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=3, pady=5)
        self.status_label = ttk.Label(mainframe, text="")
        self.status_label.grid(row=4, column=0, columnspan=3)

        # allow columns to expand
        for i in range(3):
            mainframe.columnconfigure(i, weight=1)

    def browse_input(self):
        filetypes = [
            ("PDF Files","*.pdf"),
            ("Text Files","*.txt"),
            ("XML Files","*.xml"),
            ("Image Files","*.png *.jpg *.jpeg *.bmp *.gif")
        ]
        infile = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if infile:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, infile)

    def start_conversion(self):
        infile = self.input_entry.get()
        if not infile:
            messagebox.showerror("Error", "Please select an input file.")
            return
        out_ext = self.format_combo.get()
        in_ext = os.path.splitext(infile)[1].lower().lstrip('.')
        if in_ext == out_ext:
            messagebox.showerror("Error","Input and output formats are the same!")
            return

        default_name = os.path.splitext(os.path.basename(infile))[0] + '.' + out_ext
        outfile = filedialog.asksaveasfilename(
            defaultextension='.'+out_ext,
            initialfile=default_name,
            filetypes=[(out_ext.upper()+" Files","*."+out_ext)]
        )
        if not outfile:
            return

        # disable UI while working
        self.convert_btn.config(state='disabled')
        self.status_label.config(text="Converting…")
        threading.Thread(
            target=self.convert_file,
            args=(infile, outfile, in_ext, out_ext),
            daemon=True
        ).start()

    def convert_file(self, infile, outfile, in_ext, out_ext):
        try:
            self.progress['value'] = 0
            # route to the appropriate converter
            if in_ext=='pdf' and out_ext=='txt':
                self.pdf_to_txt(infile, outfile)
            elif in_ext=='txt' and out_ext=='pdf':
                self.txt_to_pdf(infile, outfile)
            elif in_ext=='xml' and out_ext=='txt':
                self.xml_to_txt(infile, outfile)
            elif in_ext=='txt' and out_ext=='xml':
                self.txt_to_xml(infile, outfile)
            elif in_ext in ['png','jpg','jpeg','bmp','gif'] and out_ext=='pdf':
                self.image_to_pdf(infile, outfile)
            else:
                messagebox.showerror("Unsupported",
                    f"Conversion from {in_ext.upper()} to {out_ext.upper()} not supported.")
                return

            self.status_label.config(text="Done!")
            messagebox.showinfo("Success", f"Converted to {out_ext.upper()} successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.convert_btn.config(state='normal')
            self.progress['value'] = 0

    def pdf_to_txt(self, infile, outfile):
        reader = PyPDF2.PdfReader(infile)
        total = len(reader.pages)
        self.progress['maximum'] = total
        with open(outfile, 'w', encoding='utf-8') as f:
            for i, page in enumerate(reader.pages):
                f.write((page.extract_text() or "") + "\n")
                self.progress['value'] = i + 1
                self._update_progress()

    def txt_to_pdf(self, infile, outfile):
        with open(infile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        total = len(lines)
        self.progress['maximum'] = total
        c = canvas.Canvas(outfile)
        text_obj = c.beginText(40, 800)
        for i, line in enumerate(lines):
            text_obj.textLine(line.rstrip('\n'))
            self.progress['value'] = i + 1
            self._update_progress()
        c.drawText(text_obj)
        c.save()

    def xml_to_txt(self, infile, outfile):
        tree = ET.parse(infile)
        texts = list(tree.itertext())
        total = len(texts)
        self.progress['maximum'] = total
        with open(outfile, 'w', encoding='utf-8') as f:
            for i, txt in enumerate(texts):
                f.write(txt)
                if i % 10 == 0:
                    self.progress['value'] = i + 1
                    self._update_progress()
        self.progress['value'] = total

    def txt_to_xml(self, infile, outfile):
        with open(infile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        total = len(lines)
        self.progress['maximum'] = total
        root = ET.Element('root')
        for i, ln in enumerate(lines):
            el = ET.SubElement(root, 'line')
            el.text = ln.rstrip('\n')
            self.progress['value'] = i + 1
            self._update_progress()
        ET.ElementTree(root).write(outfile, encoding='utf-8', xml_declaration=True)

    def image_to_pdf(self, infile, outfile):
        img = Image.open(infile)
        rgb = img.convert('RGB')
        self.progress['maximum'] = 1
        rgb.save(outfile, 'PDF', resolution=100.0)
        self.progress['value'] = 1
        self._update_progress()

    def _update_progress(self):
        # keep UI responsive
        self.progress.update()
        self.progress.update_idletasks()

if __name__ == '__main__':
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()
