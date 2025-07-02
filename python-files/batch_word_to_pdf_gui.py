import os
import comtypes.client
import tkinter as tk
from tkinter import filedialog, messagebox

def word_to_pdf(input_folder, output_folder):
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False

    for filename in os.listdir(input_folder):
        if filename.endswith(".docx") or filename.endswith(".doc"):
            doc_path = os.path.join(input_folder, filename)
            pdf_filename = os.path.splitext(filename)[0] + ".pdf"
            pdf_path = os.path.join(output_folder, pdf_filename)
            try:
                doc = word.Documents.Open(doc_path)
                doc.SaveAs(pdf_path, FileFormat=17)
                doc.Close()
                print(f"Converted: {doc_path} -> {pdf_path}")
            except Exception as e:
                print(f"Failed: {doc_path} - {e}")

    word.Quit()
    messagebox.showinfo("Done", "Batch conversion completed!")

def select_input():
    path = filedialog.askdirectory(title="Select folder with Word files")
    if path:
        input_var.set(path)

def select_output():
    path = filedialog.askdirectory(title="Select output folder for PDFs")
    if path:
        output_var.set(path)

def start_conversion():
    in_folder = input_var.get()
    out_folder = output_var.get()
    if not in_folder or not out_folder:
        messagebox.showerror("Error", "Please select both input and output folders.")
        return
    word_to_pdf(in_folder, out_folder)

root = tk.Tk()
root.title("Batch Word to PDF Converter")

input_var = tk.StringVar()
output_var = tk.StringVar()

tk.Label(root, text="Input folder with Word files:").pack(pady=5)
tk.Entry(root, textvariable=input_var, width=50).pack()
tk.Button(root, text="Browse...", command=select_input).pack(pady=5)

tk.Label(root, text="Output folder for PDFs:").pack(pady=5)
tk.Entry(root, textvariable=output_var, width=50).pack()
tk.Button(root, text="Browse...", command=select_output).pack(pady=5)

tk.Button(root, text="Start Conversion", command=start_conversion, bg="lightgreen").pack(pady=15)

root.mainloop()
