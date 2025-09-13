import tkinter as tk
from tkinter import filedialog, messagebox
import os

def repair_jpeg(file_path, output_dir):
    # نمونه ساده: فقط کپی می‌کند، باید الگوریتم تعمیر اضافه شود
    filename = os.path.basename(file_path)
    output_path = os.path.join(output_dir, f"repaired_{filename}")
    with open(file_path, "rb") as src, open(output_path, "wb") as dst:
        data = src.read()
        dst.write(data)
    return output_path

def select_files():
    files = filedialog.askopenfilenames(title="انتخاب فایل‌های jpg", filetypes=[("JPEG files", "*.jpg;*.jpeg")])
    file_list.delete(0, tk.END)
    for f in files:
        file_list.insert(tk.END, f)

def select_output_folder():
    folder = filedialog.askdirectory(title="انتخاب پوشه خروجی")
    output_folder_var.set(folder)

def start_repair():
    files = file_list.get(0, tk.END)
    output_dir = output_folder_var.get()
    if not files or not output_dir:
        messagebox.showerror("خطا", "لطفاً فایل‌ها و پوشه خروجی را انتخاب کنید.")
        return
    for f in files:
        repaired = repair_jpeg(f, output_dir)
    messagebox.showinfo("اتمام", "عملیات بازیابی تمام شد.")

root = tk.Tk()
root.title("برنامه بازیابی JPG آسیب دیده")

tk.Button(root, text="انتخاب فایل‌ها", command=select_files).pack()
file_list = tk.Listbox(root, width=80, height=6)
file_list.pack()

output_folder_var = tk.StringVar()
tk.Button(root, text="انتخاب پوشه خروجی", command=select_output_folder).pack()
tk.Entry(root, textvariable=output_folder_var, width=60).pack()

tk.Button(root, text="شروع بازیابی", command=start_repair).pack()

root.mainloop()