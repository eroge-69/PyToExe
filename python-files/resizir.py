import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

CONVERSION = {'px': 1, 'cm': 37.795275591, 'mm': 3.7795275591, 'inch': 96}

def resize_images(files, width, height, unit, dpi, size_limit, size_unit, export_format):
    try:
        for file_path in files:
            img = Image.open(file_path)
            w_px = int(float(width) * CONVERSION[unit])
            h_px = int(float(height) * CONVERSION[unit])
            img = img.resize((w_px, h_px))
            img.info['dpi'] = (int(dpi), int(dpi))
            base, _ = os.path.splitext(file_path)
            new_file = f"{base}_new.{export_format.lower()}"
            img.save(new_file, export_format.upper())
        messagebox.showinfo("Success", "Images resized and saved.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_files():
    files = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    if files:
        entry_files.delete(0, tk.END)
        entry_files.insert(0, "; ".join(files))

def start():
    files = entry_files.get().split('; ')
    width = entry_width.get()
    height = entry_height.get()
    unit = combo_unit.get()
    dpi = entry_dpi.get()
    size_limit = entry_size.get()
    size_unit = combo_size_unit.get()
    export_format = combo_export_format.get()
    if not all([files, width, height, unit, dpi, size_limit, size_unit, export_format]):
        messagebox.showwarning("Missing", "Please fill all fields.")
        return
    resize_images(files, width, height, unit, dpi, size_limit, size_unit, export_format)

root = tk.Tk()
root.title("✨ Advanced Image Resizer Tool")
root.geometry("500x550")
root.configure(bg="#f0f4f7")

frame = ttk.Frame(root, padding=20, style='Card.TFrame')
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

style = ttk.Style()
style.configure('TFrame', background='#f0f4f7')
style.configure('TLabel', background='#f0f4f7', font=('Arial', 11))
style.configure('TButton', font=('Arial', 11, 'bold'))
style.configure('TEntry', font=('Arial', 11))
style.configure('TCombobox', font=('Arial', 11))
style.configure('Card.TFrame', background='white', relief='raised', borderwidth=2)

header = ttk.Label(frame, text="🖼️ Resize & Export Images", font=('Arial', 16, 'bold'))
header.pack(pady=10)

ttk.Label(frame, text="Select Images:").pack(anchor=tk.W, pady=(10,0))
entry_files = ttk.Entry(frame, width=60)
entry_files.pack(fill=tk.X, pady=2)
ttk.Button(frame, text="Browse", command=select_files).pack(pady=5)

ttk.Label(frame, text="Width:").pack(anchor=tk.W)
entry_width = ttk.Entry(frame)
entry_width.pack(fill=tk.X, pady=2)

ttk.Label(frame, text="Height:").pack(anchor=tk.W)
entry_height = ttk.Entry(frame)
entry_height.pack(fill=tk.X, pady=2)

ttk.Label(frame, text="Unit:").pack(anchor=tk.W)
combo_unit = ttk.Combobox(frame, values=['px', 'cm', 'mm', 'inch'])
combo_unit.set('cm')
combo_unit.pack(fill=tk.X, pady=2)

ttk.Label(frame, text="DPI:").pack(anchor=tk.W)
entry_dpi = ttk.Entry(frame)
entry_dpi.insert(0, "200")
entry_dpi.pack(fill=tk.X, pady=2)

ttk.Label(frame, text="Size:").pack(anchor=tk.W)
entry_size = ttk.Entry(frame)
entry_size.insert(0, "17")
entry_size.pack(fill=tk.X, pady=2)

combo_size_unit = ttk.Combobox(frame, values=['KB', 'MB'])
combo_size_unit.set('KB')
combo_size_unit.pack(fill=tk.X, pady=2)

ttk.Label(frame, text="Export Format:").pack(anchor=tk.W)
combo_export_format = ttk.Combobox(frame, values=['JPEG', 'JPG', 'PNG', 'PDF'])
combo_export_format.set('JPEG')
combo_export_format.pack(fill=tk.X, pady=2)

ttk.Button(frame, text="✅ Resize Image", command=start).pack(pady=15)

ttk.Label(frame, text="⚠️ Note: You can resize up to 10 images at once.").pack(anchor=tk.W, pady=5)

root.mainloop()
