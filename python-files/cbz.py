import zipfile
from PIL import Image
import io
import tkinter as tk
from tkinter import filedialog, messagebox
import statistics
import os
import img2pdf
from natsort import natsorted, ns

def split_image_vertically(im):
    width, height = im.size
    return [
        im.crop((0, 0, width, height // 2)),
        im.crop((0, height // 2, width, height))
    ]

def split_image_horizontally(im):
    width, height = im.size
    return [
        im.crop((0, 0, width // 2, height)),
        im.crop((width // 2, 0, width, height))
    ]

# ✅ Smart split (only splits when wider or taller than usual)
def smart_split(im, normal_width, normal_height, scale_factor):
    w, h = im.size
    print(f"📏 Image size: {w}x{h}, Normal: {normal_width}x{normal_height}, Scale: {scale_factor}")

    is_wide = w > normal_width * scale_factor
    is_tall = h > normal_height * scale_factor

    if is_wide and is_tall:
        print("↔↕ Splitting vertically, then horizontally")
        parts = []
        for part in split_image_vertically(im):
            if part.width > normal_width * scale_factor:
                parts.extend(split_image_horizontally(part))
            else:
                parts.append(part)
        return parts
    elif is_wide:
        print("↔ Splitting horizontally")
        return split_image_horizontally(im)
    elif is_tall:
        print("↕ Splitting vertically")
        return split_image_vertically(im)
    else:
        print("✅ No split needed")
        return [im]

def process_cbz(cbz_path, scale_factor=1.1):
    try:
        with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
            img_names = natsorted([
                f for f in zip_ref.namelist()
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and not f.endswith('/')
            ], alg=ns.IGNORECASE | ns.FLOAT)

            images_data = []
            widths = []
            heights = []

            for name in img_names:
                try:
                    with zip_ref.open(name) as file:
                        im = Image.open(io.BytesIO(file.read())).convert('RGB')
                        images_data.append(im)
                        widths.append(im.width)
                        heights.append(im.height)
                except Exception as e:
                    print(f"⚠️ Skipping corrupted image {name} in {cbz_path}: {e}")

            if not images_data:
                return []

            normal_width = int(statistics.median(widths))
            normal_height = int(statistics.median(heights))
            print(f"🧠 Median size from CBZ: {normal_width}x{normal_height}")

            processed_images = []
            for im in images_data:
                processed_images.extend(smart_split(im, normal_width, normal_height, scale_factor))

            return processed_images
    except Exception as e:
        print(f"❌ Failed to process {cbz_path}: {e}")
        return []

def save_images_to_pdf_lossless(images, final_pdf_path):
    img_bytes_list = []

    for i, im in enumerate(images):
        img_bytes = io.BytesIO()
        im.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        img_bytes_list.append(img_bytes)

    with open(final_pdf_path, "wb") as f:
        f.write(img2pdf.convert(img_bytes_list))

def main():
    root = tk.Tk()
    root.withdraw()

    cbz_files = filedialog.askopenfilenames(
        title="Select CBZ files",
        filetypes=[("Comic Book Zip", "*.cbz"), ("All files", "*.*")]
    )
    if not cbz_files:
        return

    cbz_files = natsorted(cbz_files, alg=ns.IGNORECASE | ns.FLOAT)

    print("\n📚 Merge Order:")
    for i, path in enumerate(cbz_files, 1):
        print(f"{i:02}: {os.path.basename(path)}")

    pdf_file = filedialog.asksaveasfilename(
        title="Save Final PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_file:
        return

    all_images = []
    for cbz_path in cbz_files:
        images = process_cbz(cbz_path)
        if images:
            all_images.extend(images)

    if not all_images:
        messagebox.showerror("Error", "No valid images found.")
        return

    try:
        save_images_to_pdf_lossless(all_images, pdf_file)
        messagebox.showinfo("Success", f"Final PDF saved to:\n{pdf_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")

    root.quit()
    os._exit(0)

if __name__ == "__main__":
    main()
