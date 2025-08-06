import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# دالة عمل نسخة احتياطية
def backup_drivers():
    folder = filedialog.askdirectory(title="اختر مجلد حفظ النسخة الاحتياطية")
    if folder:
        try:
            # أمر pnputil لعمل النسخة الاحتياطية
            command = f'pnputil /export-driver * "{folder}"'
            subprocess.run(command, shell=True, check=True)
            messagebox.showinfo("نجاح", "تم عمل النسخة الاحتياطية بنجاح.")
        except subprocess.CalledProcessError:
            messagebox.showerror("خطأ", "فشل في عمل النسخة الاحتياطية. تأكد أنك مشغل البرنامج كمسؤول.")

# دالة استعادة التعريفات
def restore_drivers():
    folder = filedialog.askdirectory(title="اختر مجلد النسخة الاحتياطية")
    if folder:
        try:
            # أمر pnputil لاستعادة التعريفات
            command = f'pnputil /add-driver "{folder}\\*.inf" /subdirs /install'
            subprocess.run(command, shell=True, check=True)
            messagebox.showinfo("نجاح", "تم استعادة التعريفات بنجاح.")
        except subprocess.CalledProcessError:
            messagebox.showerror("خطأ", "فشل في استعادة التعريفات. تأكد أنك مشغل البرنامج كمسؤول.")

# إعداد واجهة البرنامج باستخدام Tkinter
root = tk.Tk()
root.title("DVBAK - Driver Backup & Restore")
root.geometry("300x150")
root.resizable(False, False)

# نص العنوان
label = tk.Label(root, text="DVBAK - النسخ و الاستعادة", font=("Arial", 12))
label.pack(pady=10)

# زر النسخ الاحتياطي
backup_btn = tk.Button(root, text="Backup", width=20, command=backup_drivers)
backup_btn.pack(pady=5)

# زر استعادة التعريفات
restore_btn = tk.Button(root, text="Restore", width=20, command=restore_drivers)
restore_btn.pack(pady=5)

# تشغيل واجهة البرنامج
root.mainloop()
# نهاية البرنامج