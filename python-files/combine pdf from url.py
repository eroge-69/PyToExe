import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from PyPDF2 import PdfMerger
import io

def merge_pdfs():
    urls = text_box.get("1.0", tk.END).strip().split("\n")
    if not urls or urls == [""]:
        messagebox.showwarning("No URLs", "Please enter at least one PDF URL.")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save Combined PDF As"
    )
    if not save_path:
        return

    merger = PdfMerger()

    try:
        for url in urls:
            url = url.strip()
            if not url:
                continue
            status_label.config(text=f"Downloading: {url}")
            root.update_idletasks()

            response = requests.get(url)
            response.raise_for_status()

            pdf_file = io.BytesIO(response.content)
            merger.append(pdf_file)

        with open(save_path, "wb") as f:
            merger.write(f)
        merger.close()

        messagebox.showinfo("Success", f"Combined PDF saved at:\n{save_path}")
        status_label.config(text="Done ✅")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Failed ❌")

# GUI setup
root = tk.Tk()
root.title("PDF Merger from URLs")
root.geometry("500x400")

label = tk.Label(root, text="Enter PDF URLs (one per line):")
label.pack(pady=5)

text_box = tk.Text(root, height=12, width=60)
text_box.pack(padx=10, pady=5)

merge_button = tk.Button(root, text="Download & Merge PDFs", command=merge_pdfs)
merge_button.pack(pady=10)

status_label = tk.Label(root, text="Idle", fg="blue")
status_label.pack(pady=5)

root.mainloop()
