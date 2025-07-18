import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# === LOGIC FUNCTIONS ===

def browse_split_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        split_file_entry.delete(0, 'end')
        split_file_entry.insert(0, file_path)

def split_pdf():
    file_path = split_file_entry.get()
    ranges = split_range_entry.get().strip()

    if not os.path.isfile(file_path):
        messagebox.showerror("Error", "No valid PDF file selected.")
        return

    if not ranges:
        messagebox.showerror("Error", "Please enter valid page ranges.")
        return

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.dirname(file_path)

        sections = []
        for part in ranges.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
            else:
                start = end = int(part)
            sections.append((start, end))

        for i, (start, end) in enumerate(sections, start=1):
            writer = PdfWriter()
            for j in range(start - 1, end):
                if j < total_pages:
                    writer.add_page(reader.pages[j])
            out_path = os.path.join(output_dir, f"{base_name}_section_{i}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)

        messagebox.showinfo("Success", "PDF successfully split!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_merge_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for file in files:
        if file not in merge_listbox.get(0, tk.END):
            merge_listbox.insert(tk.END, file)

def clear_merge_list():
    merge_listbox.delete(0, tk.END)

def merge_pdfs():
    files = list(merge_listbox.get(0, tk.END))
    if not files:
        messagebox.showwarning("No Files", "Please add at least one PDF to merge.")
        return

    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_path:
        try:
            merger = PdfMerger()
            for file in files:
                merger.append(file)
            merger.write(output_path)
            merger.close()
            messagebox.showinfo("Success", f"Merged PDF saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# === MAIN UI ===
root = tk.Tk()
root.title("PDF Split & Merge Tool")
root.geometry("720x600")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 11))
style.configure("TEntry", padding=5, relief="flat", font=("Segoe UI", 10))
style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10, "bold"),
                background="#2e2e2e", foreground="#ffffff")
style.map("TButton", background=[("active", "#4b4b4b")])

# --- Notebook (Tabs)
tabs = ttk.Notebook(root)
tabs.pack(expand=True, fill="both", padx=20, pady=20)

# === SPLIT TAB ===
split_tab = ttk.Frame(tabs)
tabs.add(split_tab, text="✂️ Split PDF")

split_frame = ttk.Frame(split_tab, padding=30)
split_frame.pack(expand=True, fill="both")

ttk.Label(split_frame, text="Select PDF file to split:").grid(row=0, column=0, sticky="w", pady=(0, 5))
split_file_entry = ttk.Entry(split_frame, width=60)
split_file_entry.grid(row=1, column=0, columnspan=2, sticky="we", pady=5)
ttk.Button(split_frame, text="Browse", command=browse_split_pdf).grid(row=1, column=2, padx=10)

ttk.Label(split_frame, text="Enter page ranges (e.g. 1-3,5,7-9):").grid(row=2, column=0, columnspan=2, sticky="w", pady=(20, 5))
split_range_entry = ttk.Entry(split_frame, width=40)
split_range_entry.grid(row=3, column=0, columnspan=2, sticky="we", pady=5)

ttk.Button(split_frame, text="Split PDF", command=split_pdf).grid(row=4, column=0, columnspan=3, pady=30)

# === MERGE TAB ===
merge_tab = ttk.Frame(tabs)
tabs.add(merge_tab, text="➕ Merge PDFs")

merge_frame = ttk.Frame(merge_tab, padding=30)
merge_frame.pack(expand=True, fill="both")

ttk.Label(merge_frame, text="List of PDFs to merge:").pack(anchor="w")
merge_listbox = tk.Listbox(merge_frame, height=12, bg="#2a2a2a", fg="#ffffff",
                           font=("Segoe UI", 10), selectbackground="#444444", relief="flat", bd=1)
merge_listbox.pack(fill="both", pady=10)

ttk.Button(merge_frame, text="Add PDFs", command=add_merge_files).pack(pady=(5, 2))
ttk.Button(merge_frame, text="Clear List", command=clear_merge_list).pack(pady=2)
ttk.Button(merge_frame, text="Merge PDFs", command=merge_pdfs).pack(pady=20)

# === FOOTER ===
footer = tk.Label(root, text="Software by Department 7.1 KL team. 20250718v1.0",
                  font=("Segoe UI", 9), bg="#1e1e1e", fg="#888888")
footer.pack(pady=10)

root.mainloop()
