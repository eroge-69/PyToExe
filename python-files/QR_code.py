import os
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse

import qrcode
from qrcode.image.svg import SvgImage
from PIL import Image
from pathvalidate import sanitize_filename

# Fallback import for Resampling enum on older Pillow versions
ResamplingFilter = getattr(Image, "Resampling", Image).LANCZOS

def make_safe_filename(url):
    parsed = urlparse(url)
    base = parsed.netloc + parsed.path.replace('/', '_')
    return sanitize_filename(base or 'qr_code', platform='auto')

def generate_qr():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Required", "Please enter a URL.")
        return

    # Filenames
    base = make_safe_filename(url)
    png_path = f"{base}.png"
    svg_path = f"{base}.svg"

    # Build QR
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Resize to chosen resolution
    res = resolution_var.get()
    img = img.resize((res, res), resample=ResamplingFilter)

    # Overlay logo if provided
    logo_file = logo_path_var.get()
    if logo_file:
        logo = Image.open(logo_file)
        box = res // 5
        logo.thumbnail((box, box), resample=ResamplingFilter)
        pos = ((res - logo.size[0]) // 2, (res - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

    # Save PNG & SVG
    img.save(png_path)
    qrcode.make(url, image_factory=SvgImage).save(svg_path)

    # Show full paths
    messagebox.showinfo(
        "QR Code Saved",
        f"PNG ({res}×{res}px):\n  {os.path.abspath(png_path)}\n\n"
        f"SVG:\n  {os.path.abspath(svg_path)}"
    )

def choose_logo():
    path = filedialog.askopenfilename(
        title="Select Logo Image",
        filetypes=[("Image Files","*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.ico")])
    if path:
        logo_path_var.set(path)


root = tk.Tk()
root.title("QR Code Generator")

# URL row
tk.Label(root, text="URL:") \
    .grid(row=0, column=0, sticky="e", padx=5, pady=5)
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

# Logo chooser row
tk.Label(root, text="Logo (optional):") \
    .grid(row=1, column=0, sticky="e", padx=5, pady=5)
logo_path_var = tk.StringVar()
tk.Entry(root, textvariable=logo_path_var, width=30) \
    .grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse…", command=choose_logo) \
    .grid(row=1, column=2, padx=5, pady=5)

# —— NEW: Put all radios into a frame ——
tk.Label(root, text="PNG Resolution:") \
    .grid(row=2, column=0, sticky="ne", padx=5, pady=5)

resolution_var = tk.IntVar(value=1000)
resolutions = [100, 200, 450, 1000, 2000]

res_frame = tk.Frame(root)
res_frame.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)

for val in resolutions:
    rb = tk.Radiobutton(res_frame,
                        text=f"{val}px",
                        variable=resolution_var,
                        value=val)
    rb.pack(side="left", padx=4)   # pack them snugly side by side

# Generate button
tk.Button(root, text="Generate QR Code", command=generate_qr) \
    .grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
