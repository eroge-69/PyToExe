import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
from pylibdmtx import encode

# Szablon kodu Data Matrix z miejscami na parametry
TEMPLATE = (
    "[)@06@K3000780347@4K000050@16K5002410322"
    "@P{P}"
    "@1PQ65112A8838@20P"
    "@30PGW CSSRM3.EM-N3N6-A737-K2L2-SA"
    "@31P11119647@32P@Q6000@14D@16D@VN.A."
    "@1T@1Z{Z}@2Z@3Z105456@S120368401@@"
)

def generate_datamatrix(data_str: str, scale: int = 6):
    """Generuje obraz Data Matrix i zwraca obiekt PIL.Image."""
    png_bytes = encode(data_str.encode("utf-8"))
    img = Image.open(BytesIO(png_bytes))
    if scale != 1:
        w, h = img.size
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    return img

def on_generate():
    p_val = entry_p.get().strip()
    z_val = entry_z.get().strip()

    if not p_val or not z_val:
        messagebox.showwarning("Błąd", "Wpisz wartości dla P i 1Z!")
        return

    data = TEMPLATE.format(P=p_val, Z=z_val)

    try:
        img = generate_datamatrix(data, scale=6)
        img.save("datamatrix.png", format="PNG")

        # Wyświetlenie w GUI
        img_tk = ImageTk.PhotoImage(img)
        label_img.config(image=img_tk)
        label_img.image = img_tk

        messagebox.showinfo("Sukces", "Data Matrix zapisany jako datamatrix.png")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się wygenerować kodu:\n{e}")

# --- GUI ---
root = tk.Tk()
root.title("Generator Data Matrix")

tk.Label(root, text="Wartość P:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_p = tk.Entry(root, width=30)
entry_p.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Wartość 1Z:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_z = tk.Entry(root, width=30)
entry_z.grid(row=1, column=1, padx=5, pady=5)

btn_generate = tk.Button(root, text="Generuj", command=on_generate)
btn_generate.grid(row=2, column=0, columnspan=2, pady=10)

label_img = tk.Label(root)
label_img.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
