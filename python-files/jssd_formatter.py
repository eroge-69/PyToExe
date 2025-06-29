
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def apply_jssd_formatting(doc_path):
    doc = Document(doc_path)

    for para in doc.paragraphs:
        # Set font to Arial, size 12
        for run in para.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(12)

        # Identify and bold headings
        if para.style.name.lower().startswith("heading"):
            for run in para.runs:
                run.bold = True
        else:
            for run in para.runs:
                run.bold = False

        # Set spacing before and after paragraphs to simulate two-line space
        para.paragraph_format.space_before = Pt(12)
        para.paragraph_format.space_after = Pt(12)

        # Set left indentation for main paragraphs
        para.paragraph_format.left_indent = Inches(0.5)

    # Save new document
    base, ext = os.path.splitext(doc_path)
    new_path = base + "_output" + ext
    doc.save(new_path)
    return new_path

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
    if filepath:
        output_file = apply_jssd_formatting(filepath)
        messagebox.showinfo("Success", f"Formatted file saved as:\n{output_file}")

app = tk.Tk()
app.title("JSSD Formatter")
app.geometry("300x150")

frame = tk.Frame(app)
frame.pack(pady=30)

browse_button = tk.Button(frame, text="Apply JSSD", command=browse_file, height=2, width=20)
browse_button.pack()

app.mainloop()
