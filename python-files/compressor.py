import os
from tkinter import Tk, filedialog, messagebox
from PIL import Image

TARGET_SIZE = 200 * 1024  # 200 KB
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png']

def compress_image(image_path, output_path):
    img = Image.open(image_path)
    img_format = img.format

    quality = 95
    step = 5

    while True:
        img.save(output_path, format=img_format, quality=quality, optimize=True)
        if os.path.getsize(output_path) <= TARGET_SIZE or quality <= 10:
            break
        quality -= step

def main():
    root = Tk()
    root.withdraw()

    files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not files:
        return

    output_dir = filedialog.askdirectory(title="Select Output Folder")
    if not output_dir:
        return

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext not in SUPPORTED_FORMATS:
            continue
        filename = os.path.basename(file)
        output_path = os.path.join(output_dir, filename)
        try:
            compress_image(file, output_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compress {filename}.\n{e}")

    messagebox.showinfo("Done", "Compression complete!")

if __name__ == "__main__":
    main()
