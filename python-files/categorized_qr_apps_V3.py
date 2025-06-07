import os
import fitz  # PyMuPDF
from pyzbar.pyzbar import decode
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import time

def extract_qr_code_from_page(page):
    """
    Render PDF page to image and decode QR code.
    Returns the QR code data as string if found, else None.
    """
    zoom = 2  # scale to improve QR detection
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    mode = "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        # Return the first QR code found on the page
        return obj.data.decode("utf-8")
    return None

def save_pages_to_pdf(pages, original_doc, output_path):
    """
    Save given pages (list of page indices) from original_doc into a new PDF at output_path.
    """
    if not pages:
        return False
    new_pdf = fitz.open()
    for pno in pages:
        new_pdf.insert_pdf(original_doc, from_page=pno, to_page=pno)
    new_pdf.save(output_path)
    new_pdf.close()
    return True

def process_pdf(input_pdf_path, output_base_dir):
    if not os.path.isfile(input_pdf_path):
        messagebox.showerror("Error", f"Input PDF file '{input_pdf_path}' does not exist.")
        return

    if not os.path.isdir(output_base_dir):
        os.makedirs(output_base_dir)
        print(f"Created output directory '{output_base_dir}'.")

    print(f"Opening input PDF: {input_pdf_path}")
    doc = fitz.open(input_pdf_path)

    total_inputted_pages = doc.page_count
    qr_page_map = {}  # qr_code_str -> list of page numbers (0-based)
    detected_qr_pages_count = 0
    undetected_qr_pages_count = 0
    detected_qr_numbers = [] # To store unique QR codes detected

    print(f"Processing {total_inputted_pages} pages to detect QR codes...")

    for i in range(total_inputted_pages):
        page = doc.load_page(i)
        qr_code = extract_qr_code_from_page(page)
        if qr_code:
            qr_code = qr_code.strip()
            qr_page_map.setdefault(qr_code, []).append(i)
            detected_qr_pages_count += 1
            if qr_code not in detected_qr_numbers:
                detected_qr_numbers.append(qr_code)
            print(f"Page {i+1}: Detected QR code '{qr_code}'")
        else:
            undetected_qr_pages_count += 1
            print(f"Page {i+1}: No QR code detected.")

    # Update the GUI labels with the processing results
    total_pages_label.config(text=f"Total Inputted Pages: {total_inputted_pages}")
    detected_pages_label.config(text=f"Detected QR Pages: {detected_qr_pages_count}")
    undetected_pages_label.config(text=f"Undetected QR Pages: {undetected_qr_pages_count}")
    
    # Sort detected QR numbers for a cleaner display
    detected_qr_numbers.sort()
    qr_list_text = "\n".join(detected_qr_numbers) if detected_qr_numbers else "None"
    detected_qr_list_label.config(text=f"Detected QR Numbers:\n{qr_list_text}")


    if not qr_page_map:
        messagebox.showinfo("Info", "No QR codes detected in any pages. Exiting.")
        return

    print(f"\nFound {len(qr_page_map)} unique QR code(s). Generating categorized PDFs...")

    for qr_code, pages in qr_page_map.items():
        folder_path = os.path.join(output_base_dir, qr_code)
        os.makedirs(folder_path, exist_ok=True)
        output_pdf_path = os.path.join(folder_path, f"{qr_code}.pdf")
        saved = save_pages_to_pdf(pages, doc, output_pdf_path)
        if saved:
            print(f"Saved {len(pages)} page(s) with QR '{qr_code}' to {output_pdf_path}")
        else:
            print(f"Failed to save pages for QR '{qr_code}'")

    print("\nCategorization completed.")
    categorized_folders = len(qr_page_map)
    categorized_files = sum(len(pages) for pages in qr_page_map.values())
    messagebox.showinfo("Success", f"Categorization completed successfully!\nTotal categorized folders: {categorized_folders}\nTotal categorized QR files: {categorized_files}\nFile name: {os.path.basename(input_pdf_path)}")
    saved_path_label.config (text=f"Saved categorized PDFs to: {output_base_dir}")

def upload_pdf():
    input_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if input_pdf_path:
        uploaded_file_label.config(text=f"Uploaded File: {os.path.basename(input_pdf_path)}")
        output_base_dir = os.path.join(os.path.dirname(input_pdf_path), "categorized_pdf")
        confirm_button.config(command=lambda: process_pdf(input_pdf_path, output_base_dir))
        # Reset results when a new PDF is uploaded
        total_pages_label.config(text="Total Inputted Pages: 0")
        detected_pages_label.config(text="Detected QR Pages: 0")
        undetected_pages_label.config(text="Undetected QR Pages: 0")
        detected_qr_list_label.config(text="Detected QR Numbers:\nNone")
        saved_path_label.config(text="Saved To: (Not yet saved)")

def update_time():
    current_time = time.strftime("%H:%M:%S")
    time_label.config(text=f"Current Time: {current_time}")
    root.after(1000, update_time)  # Update time every second

# Create the main application window
root = tk.Tk()
root.title("AndhikaProject - QR Code PDF Categorizer")
root.geometry("500x600") # Increased window size to accommodate new labels

# Create a label to display the current time
time_label = tk.Label(root, text="", font=("Helvetica", 12))
time_label.pack(pady=5)

# Create a label to display the uploaded file name
uploaded_file_label = tk.Label(root, text="Uploaded File: None", font=("Helvetica", 12))
uploaded_file_label.pack(pady=5)

# Create a button to upload PDF
upload_button = tk.Button(root, text="Upload PDF", command=upload_pdf)
upload_button.pack(pady=5)

# Create a confirmation button
confirm_button = tk.Button(root, text="Confirm", state=tk.NORMAL)
confirm_button.pack(pady=5)

# --- New Labels for displaying results ---
total_pages_label = tk.Label(root, text="Total Inputted Pages: 0", font=("Helvetica", 12))
total_pages_label.pack(pady=2)

detected_pages_label = tk.Label(root, text="Detected QR Pages: 0", font=("Helvetica", 12))
detected_pages_label.pack(pady=2)

undetected_pages_label = tk.Label(root, text="Undetected QR Pages: 0", font=("Helvetica", 12))
undetected_pages_label.pack(pady=2)

saved_path_label = tk.Label (root, text="Saved Path: None", font=("Helvetica", 12), wraplength=450, justify=tk.CENTER)
saved_path_label.pack(pady=5)

detected_qr_list_label = tk.Label(root, text="Detected QR Numbers:\nNone", font=("Helvetica", 12), justify=tk.LEFT)
detected_qr_list_label.pack(pady=10)
# --- End of New Labels ---

# Create an exit button
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Start the time update function
update_time()

# Start the GUI event loop
root.mainloop()