import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from docx2pdf import convert
import fitz  # PyMuPDF
import pyperclip
import json

settings_file = "settings.json"

# تحميل الإعدادات
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    return {"save_folder": "", "image_path": ""}

# حفظ الإعدادات
def save_settings(settings):
    with open(settings_file, "w") as f:
        json.dump(settings, f)

settings = load_settings()

def choose_settings(first_time=False):
    folder = filedialog.askdirectory(title="اختر فولدر الحفظ")
    if not folder:
        if first_time:
            messagebox.showerror("خطأ", "لازم تختار فولدر الحفظ أول مرة")
            return False
        return
    img = filedialog.askopenfilename(title="اختر صورة الهيدر والفوتر", 
                                     filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
    if not img:
        if first_time:
            messagebox.showerror("خطأ", "لازم تختار صورة الهيدر والفوتر أول مرة")
            return False
        return
    settings["save_folder"] = folder
    settings["image_path"] = img
    save_settings(settings)
    if not first_time:
        messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح")
    return True

def convert_and_send():
    phone = phone_entry.get().strip()
    if not phone:
        messagebox.showerror("خطأ", "اكتب رقم الهاتف")
        return
    
    if phone.startswith("0"):
        phone = phone[1:]
    phone = "20" + phone  # كود مصر
    
    word_file = filedialog.askopenfilename(title="اختر ملف Word", 
                                           filetypes=[("Word Files", "*.docx;*.doc")])
    if not word_file:
        return
    
    if not settings["save_folder"] or not settings["image_path"]:
        messagebox.showerror("خطأ", "لازم تختار فولدر وصورة الأول (من زر إعدادات)")
        return
    
    # تحويل Word إلى PDF مؤقت
    temp_pdf = os.path.join(settings["save_folder"], "temp.pdf")
    convert(word_file, temp_pdf)
    
    # اسم الملف النهائي بنفس اسم Word
    pdf_file = os.path.join(
        settings["save_folder"],
        os.path.basename(word_file).replace(".docx", ".pdf").replace(".doc", ".pdf")
    )
    
    # افتح PDF وأضف صورة الخلفية
    pdf = fitz.open(temp_pdf)
    img = fitz.Pixmap(settings["image_path"])
    for page in pdf:
        rect = page.rect
        page.insert_image(rect, pixmap=img)
    pdf.save(pdf_file)
    pdf.close()
    os.remove(temp_pdf)
    
    # نسخ المسار للكليب بورد
    pyperclip.copy(pdf_file)
    
    # فتح واتساب ويب
    url = f"https://wa.me/{phone}"
    webbrowser.open(url)
    
    messagebox.showinfo("تم", f"PDF جاهز في:\n{pdf_file}\n\nالمسار اتنسخ للكليب بورد")

# واجهة البرنامج
root = tk.Tk()
root.title("Word to PDF Sender")

# أول مرة فقط
if not settings["save_folder"] or not settings["image_path"]:
    if not choose_settings(first_time=True):
        root.destroy()
        exit()

tk.Label(root, text="رقم الهاتف:").pack(pady=5)
phone_entry = tk.Entry(root, width=30)
phone_entry.pack(pady=5)

tk.Button(root, text="إعدادات", command=choose_settings).pack(pady=5)
tk.Button(root, text="إرسال", command=convert_and_send).pack(pady=10)

root.mainloop()