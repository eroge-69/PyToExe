import tkinter as tk
from tkinter import filedialog, messagebox

from rembg import remove
from PIL import Image, ImageTk

def remove_bg():

    input_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("PNG, JPG, JPEG", "*.png;*.jpg;*.jpeg")]
    )
    if not input_path:
        return

    img = Image.open(input_path).convert("RGBA")

    out_img = remove(img)

    save_path = filedialog.asksaveasfilename(
        title="Save Image As",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )
    if save_path:
        out_img.save(save_path)
        messagebox.showinfo("Saved", f"Image saved to {save_path}")


root = tk.Tk()
root.title("EmadBG Remover")
root.iconbitmap("icon.ico")
root.geometry("400x500")
root.resizable(False, False)

img_logo = Image.open("logo.png").resize((400, 250)) 
logo = ImageTk.PhotoImage(img_logo)
label_logo = tk.Label(root, image=logo)
label_logo.image = logo
label_logo.pack(pady=10)

btn_style = {
    "bg": "#78b5ff",
    "fg": "white",
    "font": ("Arial", 12, "bold"),
    "width": 20,
    "height": 2,
    "relief": "raised",
    "bd": 4
}

tk.Button(root, text="Remove Background", command=remove_bg, **btn_style).pack(pady=20)
tk.Button(root, text="Exit", command=root.destroy, **btn_style).pack(pady=20)

root.mainloop()