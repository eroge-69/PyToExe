import tkinter as tk
from tkinter import messagebox
from docx import Document
import os

TEMPLATE_FILE = "sabarimala duty pramod 24-25.docx"
OUTPUT_FILE = "output.docx"

FIELDS = [
    "subject",
    "reference",
    "file number",
    "date",
    "designation",
    "name"
]

def fill_template():
    data = { field: entries[field].get() for field in FIELDS }

    if not os.path.exists(TEMPLATE_FILE):
        messagebox.showerror("Error", f"Template file '{TEMPLATE_FILE}' not found.")
        return

    doc = Document(TEMPLATE_FILE)
    for para in doc.paragraphs:
        for key, val in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in para.text:
                para.text = para.text.replace(placeholder, val)

    doc.save(OUTPUT_FILE)
    messagebox.showinfo("Success", f"Document saved as '{OUTPUT_FILE}'")

root = tk.Tk()
root.title("Word Document Auto-Filler")

entries = {}
for i, field in enumerate(FIELDS):
    tk.Label(root, text=field.title() + ":").grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[field] = entry

tk.Button(root, text="Generate Document", command=fill_template, bg="green", fg="white").grid(
    row=len(FIELDS), columnspan=2, pady=15
)

root.mainloop()
