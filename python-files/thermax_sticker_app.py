import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class ThermaxStickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermax Sticker Generator")
        self.data = None
        self.current_row = 0

        self.width_mm = 100
        self.height_mm = 50

        tk.Button(root, text="Load Excel", command=self.load_excel, bg="lightblue").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(root, text="Generate PDF", command=self.generate_pdf, bg="lightgreen").grid(row=0, column=1, padx=5, pady=5)

        self.preview = tk.Label(root, text="Preview will appear here", justify="left", anchor="w", bg="#f4f4f4", width=80, height=8)
        self.preview.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        tk.Button(root, text="Previous", command=self.prev_record).grid(row=2, column=0, pady=5)
        tk.Button(root, text="Next", command=self.next_record).grid(row=2, column=1, pady=5)

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            self.data = pd.read_excel(file_path)
            self.current_row = 0
            self.show_preview()

    def show_preview(self):
        if self.data is not None and not self.data.empty:
            row = self.data.iloc[self.current_row]
            preview_text = f"""Customer : {row['Customer']}
PO No. : {row['PO No.']}    Thermax Project No. : {row['Thermax Project No.']}
Item – SR. NO {row['SR No.']}    Part Code : {row['Part Code']}
Description : {row['Description']}
Pyrotech Project No. : {row['Pyrotech Project No.']}
Qty : {row['Qty']} of {row['Total Qty']}"""
            self.preview.config(text=preview_text)

    def next_record(self):
        if self.data is not None and self.current_row < len(self.data) - 1:
            self.current_row += 1
            self.show_preview()

    def prev_record(self):
        if self.data is not None and self.current_row > 0:
            self.current_row -= 1
            self.show_preview()

    def generate_pdf(self):
        if self.data is None:
            messagebox.showerror("Error", "Please load Excel first")
            return

        w, h = self.width_mm * mm, self.height_mm * mm
        output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_file:
            return

        c = canvas.Canvas(output_file, pagesize=(w, h))

        for _, row in self.data.iterrows():
            x = 10
            y = h - 15
            gap = 14  # vertical line spacing

            # Border
            c.setLineWidth(1)
            c.rect(2, 2, w - 4, h - 4)

            # Customer (Big + Bold)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x, y, f"Customer : {row['Customer']}")

            c.setFont("Helvetica", 9)
            y -= gap
            c.drawString(x, y, f"PO No. : {row['PO No.']}")
            c.drawString(x + 100, y, f"Thermax Project No. : {row['Thermax Project No.']}")

            y -= gap
            c.drawString(x, y, f"Item – SR. NO {row['SR No.']}")
            c.drawString(x + 100, y, f"Part Code : {row['Part Code']}")

            y -= gap
            c.drawString(x, y, f"Description : {row['Description']}")

            y -= gap
            c.drawString(x, y, f"Pyrotech Project No. : {row['Pyrotech Project No.']}")

            y -= gap
            c.setFont("Helvetica-Bold", 12)
            c.setFillColorRGB(1, 0, 0)
            c.drawString(x, y, f"Qty : {row['Qty']} of {row['Total Qty']}")
            c.setFillColorRGB(0, 0, 0)

            # Footer — shifted slightly up
            make_in_india_y = 8
            footer_line1_y = make_in_india_y + 18
            footer_line2_y = make_in_india_y + 10

            c.setFont("Helvetica", 7)
            c.drawCentredString(w / 2, footer_line1_y, "Manufactured By : Pyrotech Electronics Pvt. Ltd.")
            c.drawCentredString(w / 2, footer_line2_y, "Mail – pyrotech@pyrotechindia.com, Website – www.pyrotechindia.com")

            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(w / 2, make_in_india_y, "MAKE IN INDIA")

            c.showPage()

        c.save()
        messagebox.showinfo("Success", "Sticker PDF generated!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ThermaxStickerApp(root)
    root.mainloop()
