import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger

def merge_pdfs_from_folder():
    # Prompt user to select folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select Folder with PDFs")

    if not folder_selected:
        print("No folder selected.")
        return

    merger = PdfMerger()

    # List all PDF files in the folder
    for filename in sorted(os.listdir(folder_selected)):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder_selected, filename)
            merger.append(filepath)
            print(f"Merged: {filename}")

    output_path = os.path.join(folder_selected, "merged_output.pdf")
    merger.write(output_path)
    merger.close()
    print(f"\nAll PDFs merged into: {output_path}")

merge_pdfs_from_folder()