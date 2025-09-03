import fitz  # PyMuPDF
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import concurrent.futures

# Preset resolutions
PRESET_RESOLUTIONS = {
    "800 x 1000": (800, 1000),
    "1024 x 768": (1024, 768),
    "1280 x 720": (1280, 720),
    "1920 x 1080": (1920, 1080)
}

def convert_page_to_image(page, page_num, resize_width, resize_height, output_dir, pdf_name):
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = img.resize((resize_width, resize_height), Image.Resampling.LANCZOS)
    image_path = os.path.join(output_dir, f"{pdf_name}_page_{page_num + 1}.png")
    img.save(image_path)

def process_pdf(pdf_path, resize_width, resize_height, output_dir):
    try:
        pdf_document = fitz.open(pdf_path)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                futures.append(executor.submit(convert_page_to_image, page, page_num, resize_width, resize_height, output_dir, pdf_name))
            concurrent.futures.wait(futures)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process {pdf_path}: {e}")

def convert_multiple_pdfs(pdf_paths, resize_width, resize_height, progress_label):
    output_dir = os.path.join(os.path.dirname(pdf_paths[0]), "resized")
    os.makedirs(output_dir, exist_ok=True)

    progress_label.config(text="Converting PDFs...")
    for pdf_path in pdf_paths:
        process_pdf(pdf_path, resize_width, resize_height, output_dir)

    progress_label.config(text="Conversion complete.")
    messagebox.showinfo("Success", f"All PDFs converted and saved to '{output_dir}'.")

def start_conversion(pdf_paths, resolution_key, progress_label):
    if resolution_key not in PRESET_RESOLUTIONS:
        messagebox.showwarning("Invalid Selection", "Please select a valid resolution.")
        return

    resize_w, resize_h = PRESET_RESOLUTIONS[resolution_key]
    threading.Thread(target=convert_multiple_pdfs, args=(pdf_paths, resize_w, resize_h, progress_label)).start()

def select_pdfs_and_convert(progress_label):
    pdf_paths = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF files", "*.pdf")])
    if not pdf_paths:
        messagebox.showwarning("No File", "No PDF files were selected.")
        return

    selected_resolution = resolution_var.get()
    start_conversion(pdf_paths, selected_resolution, progress_label)

# GUI setup
root = tk.Tk()
root.title("Multi-PDF to Image Converter")
root.geometry("500x380")
root.configure(bg="#f7f9fc")
root.eval('tk::PlaceWindow . center')

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12), padding=10)
style.configure("TLabel", font=("Segoe UI", 12), background="#f7f9fc")
style.configure("TCombobox", font=("Segoe UI", 11))

ttk.Label(root, text="📄 Select a preset resolution:").pack(pady=(30, 10))

resolution_var = tk.StringVar(value="800 x 1000")
resolution_menu = ttk.Combobox(root, textvariable=resolution_var, values=list(PRESET_RESOLUTIONS.keys()), state="readonly", width=25)
resolution_menu.pack(pady=5)

progress_label = ttk.Label(root, text="", foreground="green")
progress_label.pack(pady=(10, 0))

ttk.Button(root, text="📂 Select PDF(s) and Convert", command=lambda: select_pdfs_and_convert(progress_label)).pack(pady=30)

ttk.Label(root, text="Images will be saved in a folder named 'resized'.").pack(pady=(10, 0))

root.mainloop()
