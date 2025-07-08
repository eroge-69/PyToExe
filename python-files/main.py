import os
import qrcode
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image

def generate_qr():
    text = entry.get().strip()
    custom_name = name_entry.get().strip()

    if not text:
        messagebox.showwarning("Xatolik", "Iltimos, matn kiriting!")
        return

    # Sana bo‘yicha papka yaratish
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(os.getcwd(), today)
    os.makedirs(folder, exist_ok=True)

    # QR kod fayl nomini aniqlash
    if custom_name:
        # Foydalanuvchi bergan nom bilan
        filename = os.path.join(folder, f"{custom_name}.png")
        counter = 1
        while os.path.exists(filename):  # Agar mavjud bo‘lsa, oxiriga raqam qo‘shamiz
            filename = os.path.join(folder, f"{custom_name}_{counter}.png")
            counter += 1
    else:
        # Avtomatik 0001, 0002, ...
        i = 1
        while True:
            filename = os.path.join(folder, f"{i:04d}.png")
            if not os.path.exists(filename):
                break
            i += 1

    # QR kodni yaratish
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

    # Tozalash
    entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)

    messagebox.showinfo("Muvaffaqiyatli", f"QR kod saqlandi:\n{filename}")

# GUI oynasi
root = tk.Tk()
root.title("QR Kod Yaratish")
root.geometry("420x250")
root.minsize(420, 250)  # ✅ Minimal o‘lcham belgilandi


tk.Label(root, text="Matn yoki link kiriting:").pack(pady=(10, 0))
entry = tk.Entry(root, width=55)
entry.pack(pady=5)

tk.Label(root, text="QR kod nomi (ixtiyoriy):").pack()
name_entry = tk.Entry(root, width=55)
name_entry.pack(pady=5)

tk.Button(root, text="QR kod yaratish", command=generate_qr).pack(pady=15)

root.mainloop()
