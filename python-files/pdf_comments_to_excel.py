import fitz  # PyMuPDF
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def extract_comments_to_excel(pdf_path, excel_path):
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        comments = []

        # Iterate through each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            for annot in page.annots():
                if annot.type[0] == 8:  # 8 corresponds to Text annotations (comments)
                    comment_text = annot.info.get("content", "")
                    if comment_text:
                        # Get text color (RGB)
                        text_color = annot.colors.get("stroke", (0, 0, 0))  # Default to black if not set
                        text_color_rgb = f"RGB({int(text_color[0]*255)}, {int(text_color[1]*255)}, {int(text_color[2]*255)})"
                        
                        # Get background color (fill color, if available)
                        bg_color = annot.colors.get("fill", None)
                        bg_color_rgb = "None"
                        if bg_color:
                            bg_color_rgb = f"RGB({int(bg_color[0]*255)}, {int(bg_color[1]*255)}, {int(bg_color[2]*255)})"

                        comments.append({
                            "Page": page_num + 1,
                            "Comment": comment_text,
                            "Author": annot.info.get("title", "Unknown"),
                            "Date": annot.info.get("modDate", "Unknown"),
                            "Text Color": text_color_rgb,
                            "Background Color": bg_color_rgb
                        })

        # Close the PDF
        doc.close()

        if not comments:
            messagebox.showinfo("Info", "No comments found in the PDF.")
            return

        # Create DataFrame and save to Excel
        df = pd.DataFrame(comments)
        df.to_excel(excel_path, index=False)
        messagebox.showinfo("Success", f"Comments extracted and saved to {excel_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

class PDFCommentExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Comment Extractor")
        self.root.geometry("600x300")

        # PDF File Selection
        self.label_pdf = tk.Label(root, text="Select PDF File:")
        self.label_pdf.pack(pady=10)

        self.pdf_path_var = tk.StringVar()
        self.entry_pdf = tk.Entry(root, textvariable=self.pdf_path_var, width=50)
        self.entry_pdf.pack(pady=5)

        self.btn_browse_pdf = tk.Button(root, text="Browse", command=self.browse_pdf)
        self.btn_browse_pdf.pack(pady=5)

        # Excel File Selection
        self.label_excel = tk.Label(root, text="Select Output Excel File:")
        self.label_excel.pack(pady=10)

        self.excel_path_var = tk.StringVar()
        self.entry_excel = tk.Entry(root, textvariable=self.excel_path_var, width=50)
        self.entry_excel.pack(pady=5)

        self.btn_browse_excel = tk.Button(root, text="Browse", command=self.browse_excel)
        self.btn_browse_excel.pack(pady=5)

        # Extract Button
        self.btn_extract = tk.Button(root, text="Extract Comments", command=self.extract)
        self.btn_extract.pack(pady=20)

    def browse_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path_var.set(file_path)

    def browse_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            self.excel_path_var.set(file_path)

    def extract(self):
        pdf_path = self.pdf_path_var.get()
        excel_path = self.excel_path_var.get()

        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return
        if not excel_path:
            messagebox.showerror("Error", "Please select an output Excel file.")
            return

        extract_comments_to_excel(pdf_path, excel_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCommentExtractorApp(root)
    root.mainloop()