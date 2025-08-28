import os
import fitz  # PyMuPDF
from tkinter import *
from tkinter import filedialog, messagebox
from fpdf import FPDF

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Text to PDF Converter")
        self.root.geometry("800x600")

        self.font_size = IntVar(value=12)
        self.pdf_path = None

        # Text area
        self.text_area = Text(root, wrap=WORD, font=("Arial", 12))
        self.text_area.pack(padx=10, pady=10, expand=True, fill=BOTH)

        # Controls
        control_frame = Frame(root)
        control_frame.pack(pady=5)

        Button(control_frame, text="📂 Load File (TXT / PDF / VSF)", command=self.load_file).pack(side=LEFT, padx=5)
        Button(control_frame, text="📝 Clear Text", command=self.clear_text).pack(side=LEFT, padx=5)
        Button(control_frame, text="💾 Save as PDF", command=self.save_as_pdf).pack(side=LEFT, padx=5)
        Button(control_frame, text="🖨️ Print PDF", command=self.print_pdf).pack(side=LEFT, padx=5)

        Label(root, text="Font Size:").pack()
        Spinbox(root, from_=8, to=30, textvariable=self.font_size).pack()

    def load_file(self):
        path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("Text or PDF Files", "*.txt *.pdf *.vsf")]
        )
        if not path:
            return

        try:
            ext = os.path.splitext(path)[1].lower()
            content = ""

            if ext in ['.txt', '.vsf']:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

            elif ext == '.pdf':
                doc = fitz.open(path)
                for page in doc:
                    content += page.get_text()
                doc.close()

            else:
                messagebox.showerror("Unsupported", "Only .txt, .vsf and .pdf supported.")
                return

            self.text_area.delete(1.0, END)
            self.text_area.insert(END, content)
            self.pdf_path = None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def clear_text(self):
        self.text_area.delete(1.0, END)

    def save_as_pdf(self):
        text = self.text_area.get(1.0, END).strip()
        if not text:
            messagebox.showerror("Error", "Text area is empty!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF as"
        )
        if not save_path:
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=self.font_size.get())
            pdf.set_auto_page_break(auto=True, margin=15)

            for line in text.split('\n'):
                pdf.multi_cell(0, 10, line)

            pdf.output(save_path)
            self.pdf_path = save_path
            messagebox.showinfo("Success", f"PDF saved:\n{save_path}")
            os.startfile(save_path)

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save PDF:\n{e}")

    def print_pdf(self):
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            messagebox.showerror("Error", "Please save the PDF first.")
            return
        try:
            os.startfile(self.pdf_path, "print")
            messagebox.showinfo("Printing", "Sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Printing failed:\n{e}")

if __name__ == "__main__":
    root = Tk()
    app = PDFApp(root)
    root.mainloop()
