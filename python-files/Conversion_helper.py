import os # to access the files path
import tkinter as tk # for the graphical UI stuff
from tkinter import filedialog, messagebox
import win32com.client # for accessing the windows API

"function for converting the old word files"

def batch_convert_word_files(word_files):
    if not word_files:
        return

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        for input_path in word_files:
            try:
                input_path = os.path.normpath(os.path.abspath(input_path))
                doc = word.Documents.Open(input_path)
                output_path = os.path.splitext(input_path)[0] + ".docx"
                doc.SaveAs2(output_path, FileFormat=16)
                doc.Close()
                os.remove(input_path)
                print(f"Replaced {input_path} with {output_path}")
            except Exception as e:
                print(f"Error converting Word file {input_path}: {e}")
    finally:
        word.Quit()

"function for converting the old excel files"

def batch_convert_excel_files(excel_files):
    if not excel_files:
        return

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    try:
        for input_path in excel_files:
            try:
                input_path = os.path.normpath(os.path.abspath(input_path))
                wb = excel.Workbooks.Open(input_path)
                output_path = os.path.splitext(input_path)[0] + ".xlsx"
                wb.SaveAs(output_path, FileFormat=51)
                wb.Close()
                os.remove(input_path)
                print(f"Replaced {input_path} with {output_path}")
            except Exception as e:
                print(f"Error converting Excel file {input_path}: {e}")
    finally:
        excel.Quit()


def convert_files():
    input_files = filedialog.askopenfilenames(
        title="Select .doc and .xls files",
        filetypes=[("Old Office Files", "*.doc *.xls")]
    )
    if not input_files:
        return

    confirm = messagebox.askyesno(
        "Confirm Conversion",
        "This will convert and replace all selected files.\n"
        "Original .doc/.xls files will be permanently deleted.\n\nProceed?"
    )
    if not confirm:
        return

    word_files = [f for f in input_files if f.lower().endswith(".doc")]
    excel_files = [f for f in input_files if f.lower().endswith(".xls")]

    batch_convert_word_files(word_files)
    batch_convert_excel_files(excel_files)

    messagebox.showinfo("Done", "All files converted and originals replaced.")


"building the graphical UI"
root = tk.Tk()
root.title("Batch Office File Converter (.doc/.xls to .docx/.xlsx)")
root.geometry("420x150")

label = tk.Label(root, text="Convert and replace old Office files (.doc/.xls).", wraplength=350)
label.pack(pady=20)

btn = tk.Button(root, text="Select Files and Convert", command=convert_files)
btn.pack(pady=10)

root.mainloop()

#     "C:\Users\SourjyamoyBarman\OneDrive - SummitTX Capital\Conversion_helper.py"