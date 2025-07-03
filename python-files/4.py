import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
import tempfile
import win32api
import win32print
import subprocess

# 👉 Custom Label Layout
def draw_custom_label(pdf, x, y, w, h, data):
    pdf.set_fill_color(255, 255, 200)
    pdf.rect(x, y, w, h, 'DF')

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(x, y + 4)
    pdf.cell(w, 6, str(data['UID']), align='C')

    pdf.set_font("Arial", "", 10)
    pdf.set_xy(x, y + 11)
    pdf.cell(w, 5, str(data['Paper Type']), align='C')

    pdf.set_font("Arial", "B", 11)
    pdf.set_xy(x, y + 17)
    pdf.cell(w, 5, str(data['SubjectName']), align='C')

    pdf.set_font("Arial", "", 10)
    pdf.set_xy(x, y + 23)
    pdf.cell(w, 5, str(data['ExamTime']), align='C')

# 👉 PDF Generate + Preview + Confirm + Print
def generate_labels_preview_then_print(excel_path, setup):
    try:
        df = pd.read_excel(excel_path)
        pdf = FPDF('P', 'mm', setup['paper_size'])
        pdf.set_auto_page_break(False)

        total_labels = setup['labels_per_row'] * setup['labels_per_col']

        for i, row in df.iterrows():
            if i % total_labels == 0:
                pdf.add_page()

            pos = i % total_labels
            col = pos % setup['labels_per_row']
            row_pos = pos // setup['labels_per_row']

            x = setup['margin_x'] + col * (setup['label_width'] + setup['gap_x'])
            y = setup['margin_y'] + row_pos * (setup['label_height'] + setup['gap_y'])

            draw_custom_label(pdf, x, y, setup['label_width'], setup['label_height'], row)

        temp_path = os.path.join(tempfile.gettempdir(), "preview_label.pdf")
        pdf.output(temp_path)

        # 👉 Show preview first
        os.startfile(temp_path)

        # 👉 Ask for confirmation
        confirm = messagebox.askyesno("প্রিন্ট কনফার্ম", "আপনি কি এই ফাইলটি প্রিন্ট করতে চান?")
        if confirm:
            win32api.ShellExecute(0, "printto", temp_path, f'"{setup["printer_name"]}"', ".", 0)
            return True, "✅ প্রিন্ট পাঠানো হয়েছে!"
        else:
            return False, "❌ প্রিন্ট বাতিল করা হয়েছে।"

    except Exception as e:
        return False, str(e)

# 👉 UI Window
def open_setup_window():
    def on_generate():
        try:
            setup = {
                'paper_size': combo_paper.get(),
                'printer_name': combo_printer.get(),
                'labels_per_row': int(entry_row.get()),
                'labels_per_col': int(entry_col.get()),
                'label_width': float(entry_width.get()),
                'label_height': float(entry_height.get()),
                'margin_x': float(entry_margin_x.get()),
                'margin_y': float(entry_margin_y.get()),
                'gap_x': float(entry_gap_x.get()),
                'gap_y': float(entry_gap_y.get())
            }

            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
            if not file_path:
                return

            success, result = generate_labels_preview_then_print(file_path, setup)
            if success:
                messagebox.showinfo("✅ Success", result)
            else:
                messagebox.showinfo("ℹ️ Info", result)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    app = tk.Tk()
    app.title("📄 Label Designer + Preview + Print")
    app.geometry("430x610")

    def add_entry(label, default):
        tk.Label(app, text=label).pack()
        e = tk.Entry(app)
        e.insert(0, str(default))
        e.pack()
        return e

    tk.Label(app, text="📄 Paper Size").pack()
    combo_paper = ttk.Combobox(app, values=["A4", "Letter"], state="readonly")
    combo_paper.set("A4")
    combo_paper.pack()

    tk.Label(app, text="🖨️ Printer").pack()
    printers = [p[2] for p in win32print.EnumPrinters(2)]
    combo_printer = ttk.Combobox(app, values=printers, state="readonly", width=40)
    combo_printer.set(win32print.GetDefaultPrinter())
    combo_printer.pack()

    entry_row = add_entry("🔳 Labels Per Row:", 4)
    entry_col = add_entry("🔲 Labels Per Column:", 10)
    entry_width = add_entry("↔️ Label Width (mm):", 48)
    entry_height = add_entry("↕️ Label Height (mm):", 27)
    entry_margin_x = add_entry("📐 Margin X:", 5)
    entry_margin_y = add_entry("📐 Margin Y:", 10)
    entry_gap_x = add_entry("🟰 Gap X:", 3)
    entry_gap_y = add_entry("🟰 Gap Y:", 3)

    tk.Button(app, text="👁️ Preview → Print", command=on_generate, bg="#4CAF50", fg="white").pack(pady=20)
    app.mainloop()

open_setup_window()
