import fitz  # PyMuPDF
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_pdf_to_csv():
    pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not pdf_file:
        return

    csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        return

    try:
        doc = fitz.open(pdf_file)
        cards = []
        for page in doc:
            text = page.get_text("text")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    question = lines[i]
                    answer = lines[i + 1]
                    cards.append([question, answer])

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Front", "Back"])
            writer.writerows(cards)

        messagebox.showinfo("نجاح", f"تم إنشاء الملف:\n{csv_file}")
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

# GUI
root = tk.Tk()
root.title("PDF to Anki Converter")
root.geometry("300x150")

btn = tk.Button(root, text="اختر PDF وحوله إلى CSV", command=convert_pdf_to_csv, padx=10, pady=5)
btn.pack(expand=True)

root.mainloop()
