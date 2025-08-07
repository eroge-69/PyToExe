
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4

class BarcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode PDF Generator")
        self.root.geometry("400x200")
        self.root.configure(bg="#f0f0f0")

        self.label = tk.Label(root, text="Select a .txt or .csv file with serials", wraplength=350, bg="#f0f0f0")
        self.label.pack(pady=20)

        self.button = tk.Button(root, text="Select File", command=self.select_file)
        self.button.pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.csv")])
        if file_path:
            self.process_file(file_path)

    def process_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                serials = [line.strip() for line in f if line.strip()]
            if not serials:
                raise ValueError("File is empty or invalid format.")
            self.generate_pdf(serials)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def generate_pdf(self, serials):
        try:
            output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save PDF As")
            if not output_path:
                return

            page_width, page_height = A4
            margin_x = 40
            margin_y = 40
            barcode_height = 50
            barcode_spacing_y = 90
            barcodes_per_column = 6
            columns = 2
            column_width = (page_width - 2 * margin_x) / columns

            c = canvas.Canvas(output_path, pagesize=A4)

            for i, serial in enumerate(serials):
                column = i % columns
                row = (i // columns) % barcodes_per_column
                if i > 0 and i % (columns * barcodes_per_column) == 0:
                    c.showPage()

                barcode = code128.Code128(serial, barHeight=barcode_height, barWidth=1)
                barcode_width = barcode.width
                x = margin_x + column * column_width + (column_width - barcode_width) / 2
                y = page_height - margin_y - row * barcode_spacing_y

                barcode.drawOn(c, x, y)
                text_width = c.stringWidth(serial, "Helvetica", 10)
                c.setFont("Helvetica", 10)
                c.drawString(x + (barcode_width - text_width) / 2, y - 15, serial)

            c.save()
            messagebox.showinfo("Success", f"PDF saved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = BarcodeApp(root)
    root.mainloop()
