import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def convert():
    file_path = filedialog.askopenfilename(
        title="Select PNG file",
        filetypes=[("PNG files", "*.png")]
    )
    if not file_path:
        return

    save_path = filedialog.asksaveasfilename(
        title="Save as JPG",
        defaultextension=".jpg",
        filetypes=[("JPEG files", "*.jpg;*.jpeg")]
    )
    if not save_path:
        return

    try:
        img = Image.open(file_path)
        rgb_img = img.convert('RGB')
        rgb_img.save(save_path, 'JPEG')
        messagebox.showinfo("Success", f"Saved as {save_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("PNG to JPG Converter")
root.geometry("300x100")
tk.Button(root, text="Select PNG and Convert", command=convert, height=2, width=25).pack(pady=20)
root.mainloop()