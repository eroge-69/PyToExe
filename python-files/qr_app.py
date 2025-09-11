import os
import qrcode
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

def generate_qr(url, logo_path=None):
    pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
    os.makedirs(pictures_dir, exist_ok=True)
    save_path = os.path.join(pictures_dir, "qr_code.png")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if logo_path:
        try:
            logo = Image.open(logo_path)
            qr_width, qr_height = qr_img.size
            logo_size = qr_width // 4
            logo = logo.resize((logo_size, logo_size))
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            messagebox.showwarning("Logo Error", f"Failed to embed logo: {e}")

    qr_img.save(save_path)
    messagebox.showinfo("Success", f"QR Code saved to: {save_path}")

# ==== GUI ====
def browse_logo():
    path = filedialog.askopenfilename(
        title="Select Logo Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if path:
        logo_entry.delete(0, tk.END)
        logo_entry.insert(0, path)

def create_qr():
    url = url_entry.get().strip()
    logo_path = logo_entry.get().strip() or None
    if not url:
        messagebox.showerror("Error", "Please enter a URL or text!")
        return
    generate_qr(url, logo_path)

root = tk.Tk()
root.title("QR Code Generator")
root.geometry("400x200")

tk.Label(root, text="Enter URL or Text:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text="Logo (optional):").pack(pady=5)
frame = tk.Frame(root)
frame.pack()
logo_entry = tk.Entry(frame, width=38)
logo_entry.pack(side=tk.LEFT)
tk.Button(frame, text="Browse", command=browse_logo).pack(side=tk.LEFT, padx=5)

tk.Button(root, text="Generate QR Code", command=create_qr, bg="green", fg="white").pack(pady=20)

root.mainloop()
