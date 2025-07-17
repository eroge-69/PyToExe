import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128, code39, eanbc, qr
from reportlab.lib.pagesizes import mm

def generate_barcodes():
    try:
        width_cm = float(entry_width.get())
        height_cm = float(entry_height.get())
        excel_path = entry_excel.get()
        barcode_type = combo_type.get()

        if not os.path.exists(excel_path):
            messagebox.showerror("Fehler", "Excel-Datei wurde nicht gefunden.")
            return

        df = pd.read_excel(excel_path, engine="openpyxl")
        if df.empty:
            messagebox.showerror("Fehler", "Excel-Datei enthält keine Daten.")
            return

        label_width = width_cm * mm
        label_height = height_cm * mm
        page_size = (label_width, label_height)

        bar_width = 1.2
        bar_height = label_height * 0.65
        font_size = 20

        def get_barcode(value):
            if barcode_type == "Code128":
                return code128.Code128(value, barHeight=bar_height, barWidth=bar_width)
            elif barcode_type == "Code39":
                return code39.Standard39(value, barHeight=bar_height, barWidth=bar_width, checksum=0)
            elif barcode_type == "EAN13":
                if not value.isdigit() or len(value) != 12:
                    raise ValueError("EAN13 benötigt genau 12 Ziffern.")
                return eanbc.Ean13BarcodeWidget(value)
            elif barcode_type == "QR":
                return qr.QrCodeWidget(value)
            else:
                raise ValueError("Unbekannter Barcode-Typ.")

        filename_base = "Barcodes_From_Excel"
        output_pdf = f"{filename_base}_{barcode_type}_{int(width_cm)}x{int(height_cm)}cm.pdf"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_pdf)

        c = canvas.Canvas(output_path, pagesize=page_size)

        for idx, row in df.iterrows():
            value = str(row.iloc[0]).strip()
            barcode_obj = get_barcode(value)

            if barcode_type in ["EAN13", "QR"]:
                from reportlab.graphics.shapes import Drawing
                d = Drawing(0, 0)
                d.add(barcode_obj)
                barcode_width = d.minWidth()
                barcode_height_draw = bar_height
                barcode_x = (label_width - barcode_width) / 2
                barcode_y = (label_height - barcode_height_draw) / 2 + font_size + 10
                d.drawOn(c, barcode_x, barcode_y)
                start_y = barcode_y - font_size - 10
            else:
                barcode_x = (label_width - barcode_obj.width) / 2
                total_height = bar_height + font_size + 10
                start_y = (label_height - total_height) / 2
                barcode_obj.drawOn(c, barcode_x, start_y + font_size + 10)

            c.setFont("Helvetica", font_size)
            c.drawCentredString(label_width / 2, start_y, value)
            c.showPage()

        c.save()
        messagebox.showinfo("Fertig", f"PDF erfolgreich gespeichert:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Fehler", str(e))

def select_excel():
    filepath = filedialog.askopenfilename(filetypes=[("Excel-Dateien", "*.xlsx")])
    if filepath:
        entry_excel.delete(0, tk.END)
        entry_excel.insert(0, filepath)

root = tk.Tk()
root.title("Barcode Generator aus Excel")

tk.Label(root, text="Etikettenbreite (cm):").grid(row=0, column=0, sticky="e")
entry_width = tk.Entry(root)
entry_width.insert(0, "10")
entry_width.grid(row=0, column=1)

tk.Label(root, text="Etikettenhöhe (cm):").grid(row=1, column=0, sticky="e")
entry_height = tk.Entry(root)
entry_height.insert(0, "15")
entry_height.grid(row=1, column=1)

tk.Label(root, text="Barcode-Typ:").grid(row=2, column=0, sticky="e")
combo_type = ttk.Combobox(root, values=["Code128", "Code39", "EAN13", "QR"], state="readonly")
combo_type.set("Code128")
combo_type.grid(row=2, column=1)

tk.Label(root, text="Excel-Datei:").grid(row=3, column=0, sticky="e")
entry_excel = tk.Entry(root, width=40)
entry_excel.grid(row=3, column=1)
tk.Button(root, text="Durchsuchen...", command=select_excel).grid(row=3, column=2)

tk.Button(root, text="Barcodes erzeugen", command=generate_barcodes).grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
