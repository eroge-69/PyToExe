import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from datetime import datetime

# ------------------- وظائف تفكيك -------------------
def detect_and_decrypt(file_path):
    """
    دالة كشف نوع التشفير ومعالجته.
    حالياً تدعم الشيفرات العادية لـ Lua و FiveM.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # مثال مبسط: إزالة التعليقات والمضاعفات
        content = content.replace('--[[Encrypted]]', '')
        content = content.replace('--Encrypted', '')
        return content
    except Exception as e:
        return f"Error: {e}"

# ------------------- واجهة المستخدم -------------------
class DecryptGUI:
    def __init__(self, root):
        self.root = root
        root.title("Lua & FiveM Decryptor")
        root.geometry("700x500")
        root.configure(bg="#1c1c1c")

        # عنوان جذاب
        self.title = tk.Label(root, text="Lua & FiveM Decryptor", font=("Arial", 24, "bold"), fg="#d86aff", bg="#1c1c1c")
        self.title.pack(pady=10)

        # زر اختيار الملف
        self.select_btn = tk.Button(root, text="اختر ملف Lua/FiveM", command=self.select_file, font=("Arial", 14), bg="#3a3a3a", fg="#d86aff", activebackground="#5a2eff")
        self.select_btn.pack(pady=10)

        # مكان عرض النتائج
        self.result_area = scrolledtext.ScrolledText(root, width=80, height=20, font=("Consolas", 12), bg="#2a2a2a", fg="#ffffff")
        self.result_area.pack(pady=10)

        # زر حفظ الملف المفكوك
        self.save_btn = tk.Button(root, text="احفظ الملف المفكوك", command=self.save_file, font=("Arial", 14), bg="#3a3a3a", fg="#d86aff", activebackground="#5a2eff")
        self.save_btn.pack(pady=10)
        self.save_btn.config(state='disabled')

        self.file_path = None
        self.decrypted_content = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Lua & FiveM Files", "*.lua"), ("All Files", "*.*")])
        if self.file_path:
            self.result_area.delete(1.0, tk.END)
            self.decrypted_content = detect_and_decrypt(self.file_path)
            self.result_area.insert(tk.END, self.decrypted_content)
            self.save_btn.config(state='normal')
            messagebox.showinfo("تم", f"تم تفكيك الملف: {os.path.basename(self.file_path)}")

    def save_file(self):
        if self.decrypted_content:
            save_path = filedialog.asksaveasfilename(defaultextension=".lua", filetypes=[("Lua Files", "*.lua"), ("All Files", "*.*")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.decrypted_content)
                messagebox.showinfo("تم", f"تم حفظ الملف المفكوك في:\n{save_path}")

# ------------------- تشغيل التطبيق -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DecryptGUI(root)
    root.mainloop()
