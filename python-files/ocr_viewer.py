import os
import sys
import pytesseract
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

# 🔍 Auto-detect bundled Tesseract binary
def get_tesseract_path():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    tesseract_path = os.path.join(base_path, "tesseract", "tesseract.exe")
    if os.path.exists(tesseract_path):
        return tesseract_path
    else:
        messagebox.showerror("Tesseract Not Found", "Tesseract binary not found.")
        sys.exit(1)

pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()

# 🖼️ GUI Setup
root = tk.Tk()
root.title("OCR Viewer")
root.geometry("600x400")

text_box = tk.Text(root, wrap="word")
text_box.pack(expand=True, fill="both")

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

btn = tk.Button(root, text="Open Image", command=open_image)
btn.pack(pady=10)

root.mainloop()