
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# إعداد المستخدم وكلمة المرور
USERNAME = "Beshoy"
PASSWORD = "1357"

class MagicTouchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام ماجيك تاتش")
        self.root.geometry("1000x700")
        self.root.configure(bg="#fef5e7")
        self.login_screen()

    def login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="تسجيل الدخول", font=("Cairo", 26, "bold"), bg="#fef5e7", fg="#b9770e").pack(pady=30)

        tk.Label(self.root, text="اسم المستخدم:", font=("Cairo", 16), bg="#fef5e7").pack()
        self.username_entry = tk.Entry(self.root, font=("Cairo", 16))
        self.username_entry.pack(pady=10)

        tk.Label(self.root, text="كلمة المرور:", font=("Cairo", 16), bg="#fef5e7").pack()
        self.password_entry = tk.Entry(self.root, show="*", font=("Cairo", 16))
        self.password_entry.pack(pady=10)

        tk.Button(self.root, text="دخول", font=("Cairo", 16, "bold"), bg="#f9e79f", command=self.check_login).pack(pady=20)

    def check_login(self):
        if self.username_entry.get() == USERNAME and self.password_entry.get() == PASSWORD:
            self.main_interface()
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")

    def main_interface(self):
        self.clear_window()

        # تحميل اللوجو
        logo_img = Image.open("images.jpg")
        logo_img = logo_img.resize((150, 150))
        self.logo = ImageTk.PhotoImage(logo_img)
        tk.Label(self.root, image=self.logo, bg="#fef5e7").pack(pady=10)

        tk.Label(self.root, text="نظام إدارة ماجيك تاتش", font=("Cairo", 28, "bold"), bg="#fef5e7", fg="#b9770e").pack(pady=10)

        button_frame = tk.Frame(self.root, bg="#fef5e7")
        button_frame.pack(pady=20)

        buttons = [
            ("🧾 فواتير المبيعات", 0, 0),
            ("🛒 فواتير المشتريات", 0, 1),
            ("📦 إدارة المخازن", 0, 2),
            ("💰 الحسابات", 1, 0),
            ("🏭 التصنيع", 1, 1),
            ("👤 الموارد البشرية", 1, 2),
            ("📊 التقارير", 2, 0),
            ("🔒 تسجيل الخروج", 2, 2)
        ]

        for text, row, col in buttons:
            tk.Button(button_frame, text=text, font=("Cairo", 16, "bold"), bg="#f9e79f", fg="#6e2c00",
                      width=18, height=2, relief="groove").grid(row=row, column=col, padx=15, pady=15)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicTouchApp(root)
    root.mainloop()
