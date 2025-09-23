from PIL import Image
from pathlib import Path
import os
import subprocess
import tkinter as tk
from tkinter import filedialog

# === Settings ===
dpi = 300
page_size_inches = (8.27, 11.69)  # A4 in inches
img_size_inches = (3.5, 2.2)
vertical_spacing_inches = 0.5
pdf_output = "output.pdf"
pdf_viewer = r"C:\Program Files\Tracker Software\PDF Viewer\PDFXCview.exe"

# === Convert inches to pixels ===
def inches_to_px(inches, dpi=dpi):
    return int(round(inches * dpi))

page_w, page_h = [inches_to_px(v) for v in page_size_inches]
img_w, img_h = [inches_to_px(v) for v in img_size_inches]
spacing = inches_to_px(vertical_spacing_inches)

# === Function to create one PDF page ===
def create_page(images):
    page = Image.new("RGB", (page_w, page_h), "white")
    total_height = len(images) * img_h + (len(images) - 1) * spacing
    start_y = (page_h - total_height) // 2

    for i, img_path in enumerate(images):
        try:
            img = Image.open(img_path).convert("RGB")
            img = img.resize((img_w, img_h), Image.LANCZOS)
            x = (page_w - img_w) // 2
            y = start_y + i * (img_h + spacing)
            page.paste(img, (x, y))
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    return page

# === Main process ===
def main():
    # Open dialog box for input folder
    root = tk.Tk()
    root.withdraw()
    input_folder = filedialog.askdirectory(title="Select Folder with Images")
    if not input_folder:
        print("No folder selected. Exiting.")
        return

    # Collect all images (JPG + JPEG + PNG)
    img_files = sorted(
        [f for f in Path(input_folder).glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    )

    if not img_files:
        print("No images found in selected folder.")
        return

    pages = []

    # Process images in blocks of 8 (4 odd, then 4 even)
    for i in range(0, len(img_files), 8):
        block = img_files[i:i+8]
        odd_imgs = block[0::2]  # 1st, 3rd, 5th, 7th
        even_imgs = block[1::2] # 2nd, 4th, 6th, 8th

        if odd_imgs:
            pages.append(create_page(odd_imgs))
        if even_imgs:
            pages.append(create_page(even_imgs))

    if pages:
        pages[0].save(pdf_output, save_all=True, append_images=pages[1:], resolution=dpi)
        print(f"✅ PDF saved: {pdf_output}")
        # Open with PDF-XChange Viewer
        if os.path.exists(pdf_viewer):
            subprocess.Popen([pdf_viewer, pdf_output])

if __name__ == "__main__":
    main()
