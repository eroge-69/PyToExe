import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

output_dir = None  


def create_text_overlay(text, page_width, page_height):
    
    img = Image.new("RGBA", (page_width, page_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    
    font = ImageFont.load_default()
    text_width, text_height = draw.textsize(text, font=font)

   
    x = page_width - text_width - 20
    y = 20
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

   
    byte_io = BytesIO()
    img.convert("RGB").save(byte_io, format="PDF")
    byte_io.seek(0)

    return PdfReader(byte_io)


def stamp_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    filename = os.path.basename(input_path)

    for page in reader.pages:
        width = int(page.mediabox.width)
        height = int(page.mediabox.height)

      
        overlay_pdf = create_text_overlay(filename, width, height)
        overlay_page = overlay_pdf.pages[0]

       
        page.merge_page(overlay_page)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


def process_pdfs(filepaths):
    global output_dir
    if not output_dir:
        messagebox.showerror("Error", "Please select an output folder first!")
        return

    for pdf in filepaths:
        output_path = os.path.join(output_dir, os.path.basename(pdf))
        stamp_pdf(pdf, output_path)

    messagebox.showinfo("Done", f"Stamped PDFs saved to: {os.path.abspath(output_dir)}")


def select_pdfs():
    filepaths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if filepaths:
        process_pdfs(filepaths)


def select_output_folder():
    global output_dir
    folder = filedialog.askdirectory()
    if folder:
        output_dir = folder
        messagebox.showinfo("Output Folder", f"Output folder set to:\n{output_dir}")



root = tk.Tk()
root.title("PDF Stamper")
root.geometry("350x180")

label = tk.Label(root, text="Select output folder, then choose PDFs to stamp")
label.pack(pady=10)

btn_folder = tk.Button(root, text="Select Output Folder", command=select_output_folder)
btn_folder.pack(pady=5)

btn_pdfs = tk.Button(root, text="Select PDFs", command=select_pdfs)
btn_pdfs.pack(pady=15)

root.mainloop()

from cx_Freeze import setup, Executable

setup(
    name="PDF Stamper",
    version="1.0",
    description="Because HSHS IT Team is lazy",
    executables=[Executable("pdf_stamper.py", base="Win32GUI")]
)
