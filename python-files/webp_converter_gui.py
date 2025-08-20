
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

def convert_images():
    files = filedialog.askopenfilenames(title="Vyber PNG/JPG obrázky", filetypes=[("Obrázky", "*.png *.jpg *.jpeg")])
    if not files:
        return

    output_dir = filedialog.askdirectory(title="Vyber výstupný priečinok")
    if not output_dir:
        return

    try:
        quality = int(quality_var.get())
        if not (0 <= quality <= 100):
            raise ValueError
    except ValueError:
        messagebox.showerror("Chyba", "Zadaj platnú kvalitu medzi 0 a 100.")
        return

    success = 0
    failed = 0

    for file in files:
        try:
            img = Image.open(file).convert("RGB")
            base = os.path.splitext(os.path.basename(file))[0]
            out_path = os.path.join(output_dir, base + ".webp")
            img.save(out_path, "webp", quality=quality)
            success += 1
        except Exception as e:
            failed += 1

    messagebox.showinfo("Hotovo", f"Úspešne konvertovaných: {success}\nZlyhaných: {failed}")

# GUI
root = tk.Tk()
root.title("WebP Konvertor")
root.geometry("400x200")
root.resizable(False, False)

tk.Label(root, text="Kvalita (0-100):").pack(pady=10)
quality_var = tk.StringVar(value="85")
tk.Entry(root, textvariable=quality_var, width=10).pack()

tk.Button(root, text="Vybrať a konvertovať obrázky", command=convert_images).pack(pady=20)

tk.Label(root, text="Made by GPT 🤘").pack(side="bottom", pady=10)

root.mainloop()
