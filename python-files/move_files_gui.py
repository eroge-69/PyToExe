
import os
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def main():
    # نافذة اختيار المجلد
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="اختر المجلد اللي فيه الملفات")

    if not folder_path:
        messagebox.showerror("خطأ", "لم يتم اختيار مجلد.")
        return

    # طلب امتداد الملف (مثلاً: .xls)
    file_ext = simpledialog.askstring("اختر نوع الملف", "اكتب امتداد الملف (مثال: .xls أو .pdf):")
    if not file_ext:
        messagebox.showerror("خطأ", "لم يتم إدخال امتداد.")
        return

    file_ext = file_ext.lower().strip()
    if not file_ext.startswith("."):
        file_ext = "." + file_ext

    # تنفيذ النقل
    moved_files = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(file_ext):
            file_path = os.path.join(folder_path, filename)
            folder_name = os.path.splitext(filename)[0]
            target_folder = os.path.join(folder_path, folder_name)

            os.makedirs(target_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(target_folder, filename))
            moved_files += 1

    messagebox.showinfo("تم", f"✅ تم نقل {moved_files} ملف داخل مجلدات بأسمائها.")

if __name__ == "__main__":
    main()
