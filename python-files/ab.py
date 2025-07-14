import os
from tkinter import Tk, filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter

def flip_odd_pages(pdf_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for i, page in enumerate(reader.pages):
        if i % 2 == 0:  # 0-based index for odd-numbered pages (1,3,5...)
            page.rotate_clockwise(180)
        writer.add_page(page)

    output_path = os.path.splitext(pdf_path)[0] + "_flipped.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def main():
    root = Tk()
    root.withdraw()  # Hide the main window

    messagebox.showinfo("Flip Odd Pages", "Select a PDF file to flip odd pages.")
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

    if not pdf_path:
        messagebox.showwarning("No file selected", "You didn't select a file.")
        return

    try:
        output = flip_odd_pages(pdf_path)
        messagebox.showinfo("Success", f"Flipped PDF saved as:\n{output}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main()
