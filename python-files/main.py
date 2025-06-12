
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def move_and_rename_pdfs(source_dir, output_dir):
    for root, dirs, files in os.walk(source_dir, topdown=False):
        for name in files:
            if name.lower().endswith(".pdf"):
                folder_name = os.path.basename(os.path.dirname(root))
                top_folder = os.path.basename(os.path.dirname(root)) if os.path.basename(root) != os.path.basename(source_dir) else os.path.basename(root)
                target_folder = os.path.join(output_dir, top_folder)
                os.makedirs(target_folder, exist_ok=True)
                new_name = f"{top_folder} - {name}"
                src_file = os.path.join(root, name)
                dst_file = os.path.join(target_folder, new_name)
                add_front_page_and_copy(src_file, dst_file, top_folder)

def add_front_page_and_copy(input_pdf_path, output_pdf_path, title):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica-Bold", 40)
    can.drawCentredString(A4[0]/2, A4[1]/2, title)
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(input_pdf_path)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])
    for page in existing_pdf.pages:
        output.add_page(page)
    with open(output_pdf_path, "wb") as outputStream:
        output.write(outputStream)

def select_source():
    folder = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder)

def select_target():
    folder = filedialog.askdirectory()
    target_entry.delete(0, tk.END)
    target_entry.insert(0, folder)

def process():
    source = source_entry.get()
    target = target_entry.get()
    if not os.path.isdir(source) or not os.path.isdir(target):
        messagebox.showerror("Error", "Selecteer geldige mappen.")
        return
    move_and_rename_pdfs(source, target)
    messagebox.showinfo("Klaar", "Verwerking voltooid.")

app = tk.Tk()
app.title("Prepare Structure Files for Flydocs")
tk.Label(app, text="Selecteer bronmap:").pack()
source_entry = tk.Entry(app, width=60)
source_entry.pack()
tk.Button(app, text="Bladeren", command=select_source).pack()
tk.Label(app, text="Selecteer doelmap:").pack()
target_entry = tk.Entry(app, width=60)
target_entry.pack()
tk.Button(app, text="Bladeren", command=select_target).pack()
tk.Button(app, text="Start Verwerking", command=process).pack(pady=10)
app.mainloop()
