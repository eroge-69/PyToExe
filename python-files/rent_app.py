import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class RentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rent Manager - دار الصناعات التقليدية")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

        # قائمة جانبية
        sidebar = tk.Frame(self.root, bg="#1E90FF", width=200)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="القائمة", bg="#1E90FF", fg="white", font=("Arial", 14)).pack(pady=10)
        ttk.Button(sidebar, text="إضافة حرفي", command=self.add_craftsman).pack(fill="x", padx=10, pady=5)
        ttk.Button(sidebar, text="فواتير الكهرباء", command=self.electricity_bills).pack(fill="x", padx=10, pady=5)
        ttk.Button(sidebar, text="الاشتراكات", command=self.subscriptions).pack(fill="x", padx=10, pady=5)
        ttk.Button(sidebar, text="خروج", command=self.root.quit).pack(fill="x", padx=10, pady=20)

        # محتوى رئيسي
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(side="right", fill="both", expand=True)

        tk.Label(self.main_frame, text="📊 إدارة الإيجارات", bg="white", fg="#1E90FF", font=("Arial", 20)).pack(pady=20)

    def add_craftsman(self):
        messagebox.showinfo("إضافة حرفي", "هنا يمكن إضافة حرفي جديد.")

    def electricity_bills(self):
        messagebox.showinfo("فواتير الكهرباء", "هنا تظهر فواتير الكهرباء.")

    def subscriptions(self):
        messagebox.showinfo("الاشتراكات", "هنا يمكن إدارة الاشتراكات.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RentApp(root)
    root.mainloop()
