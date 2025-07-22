import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil

# إعداد مجلد لحفظ الصور والملفات
os.makedirs("patients_data/images", exist_ok=True)
os.makedirs("patients_data/files", exist_ok=True)

# دالة لحفظ البيانات
def save_data():
    name = entry_name.get()
    surname = entry_surname.get()
    if not name or not surname:
        messagebox.showwarning("تنبيه", "يرجى إدخال الاسم واللقب")
        return
    messagebox.showinfo("تم", f"تم حفظ بيانات المريض: {name} {surname}")

# اختيار صورة
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("صور", "*.png *.jpg *.jpeg")])
    if file_path:
        shutil.copy(file_path, "patients_data/images")
        img = Image.open(file_path)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk

# اختيار الملف الطبي
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("ملفات", "*.pdf *.jpg *.jpeg *.png")])
    if file_path:
        shutil.copy(file_path, "patients_data/files")
        messagebox.showinfo("تم", "تم رفع الملف الطبي بنجاح")

# نافذة التطبيق
root = tk.Tk()
root.title("تسجيل مريض")
root.geometry("400x500")

tk.Label(root, text="الاسم:", font=("Arial", 12)).pack(pady=5)
entry_name = tk.Entry(root, font=("Arial", 12))
entry_name.pack()

tk.Label(root, text="اللقب:", font=("Arial", 12)).pack(pady=5)
entry_surname = tk.Entry(root, font=("Arial", 12))
entry_surname.pack()

tk.Label(root, text="صورة المريض:", font=("Arial", 12)).pack(pady=10)
image_label = tk.Label(root)
image_label.pack()
tk.Button(root, text="رفع صورة", command=upload_image).pack(pady=5)

tk.Label(root, text="الملف الطبي:", font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="رفع ملف طبي", command=upload_file).pack(pady=5)

tk.Button(root, text="حفظ البيانات", bg="green", fg="white", font=("Arial", 12), command=save_data).pack(pady=20)

root.mainloop()