 import re
import pandas as pd
from tkinter import Tk, filedialog, Button, Label, ttk, messagebox
from pypdf import PdfReader

# Constants
max_cols = 30

def process_pdfs(pdf_paths, progress_var, progress_bar, root):
    all_rows = []
    total_files = len(pdf_paths)
    
    for file_idx, pdf_path in enumerate(pdf_paths, start=1):
        reader = PdfReader(pdf_path)

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text = page.extract_text()
            if not text:
                continue

            if "HEMOGRAMME" in text:
                lines = text.splitlines()
                lines = lines[:67]
                if len(lines) > 10:
                    lines.pop(10)
                lines = lines[6:]

                # Filtering
                lines = [line for line in lines if "N° d'ordre" not in line and line.strip()]
                lines = [line for line in lines if "<= 20" not in line and line.strip()]
                lines = [line for line in lines if "/µl" not in line and line.strip()]
                cleaned_text1 = "\n".join(lines)

                # Cleaning
                cleaned_text2 = re.sub(r'Le Biologiste.*?ANTECEDENTS\s*\n?', '', cleaned_text1, flags=re.DOTALL)
                cleaned_text2 = re.sub(r'Prélèvement de Sang.*?ANTECEDENTS\s*\n?', '', cleaned_text2, flags=re.DOTALL)
                cleaned_text2 = re.sub(r'GB...........................*?Erythroblastes%.*?\s*\n?', '', cleaned_text2, flags=re.DOTALL)
                cleaned_text2 = re.sub(r'Consultation.*?ANTECEDENTS\s*\n?', '', cleaned_text2, flags=re.DOTALL)
                cleaned_text2 = re.sub(r'Admission.*?ANTECEDENTS\s*\n?', '', cleaned_text2, flags=re.DOTALL)
                cleaned_text2 = re.sub(r'.{5}à\s*\n?', '', cleaned_text2)
                cleaned_text2 = re.sub(r'>>>> .*? <<<<.*?\s*\n?', '', cleaned_text2, flags=re.DOTALL)

                # Split into lines
                lines_list = re.split(r'\r?\n', cleaned_text2)
                lines_list = [line for line in lines_list if line.strip()]

                # Adjust columns
                if len(lines_list) < max_cols and len(lines_list) >= 28:
                    val1 = lines_list[26]
                    val2 = lines_list[27]
                    lines_list = lines_list[:26] + ["", ""] + [val1, val2]
                elif len(lines_list) > max_cols:
                    lines_list = lines_list[:max_cols]

                # Final enforce
                lines_list = lines_list[:max_cols]
                all_rows.append(lines_list)

        # Update progress
        progress_var.set(int((file_idx / total_files) * 100))
        progress_bar.update_idletasks()

    if all_rows:
        df = pd.DataFrame(all_rows)
        df.columns = [f"Column{i+1}" for i in range(df.shape[1])]

        # Ask user where to save Excel file
        excel_path = filedialog.asksaveasfilename(
            title="Save Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if excel_path:
            df.to_excel(excel_path, index=False)
            messagebox.showinfo("Success", f"Excel file saved as:\n{excel_path}")
    else:
        messagebox.showwarning("No Data", "No valid data extracted from selected PDF(s).")

def select_pdfs(root, progress_var, progress_bar):
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_paths:
        process_pdfs(file_paths, progress_var, progress_bar, root)

def main():
    root = Tk()
    root.title("Hematology PDF Extractor")
    root.geometry("400x200")

    label = Label(root, text="Select one or multiple PDF files to extract data:")
    label.pack(pady=10)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=10)

    btn = Button(root, text="Select PDFs", command=lambda: select_pdfs(root, progress_var, progress_bar))
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    import tkinter as tk
    main()

