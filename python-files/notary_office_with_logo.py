
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

class NotaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت دفترخانه")
        self.root.geometry("950x650+200+100")
        self.root.configure(bg="#f2f2f2")

        # فونت عمومی
        self.font = ("B Nazanin", 14)

        # نمایش لوگو و نام سردفتر
        logo_frame = tk.Frame(self.root, bg="#f2f2f2")
        logo_frame.grid(row=0, column=0, columnspan=2, pady=10)

        try:
            self.logo_image = tk.PhotoImage(file="ghove.png")
            logo_label = tk.Label(logo_frame, image=self.logo_image, bg="#f2f2f2")
            logo_label.pack(side="left", padx=10)
        except Exception as e:
            logo_label = tk.Label(logo_frame, text="[آرم قوه قضاییه یافت نشد]", bg="#f2f2f2", font=self.font)
            logo_label.pack(side="left", padx=10)

        tk.Label(logo_frame, text="دفترخانه رسمی - نام سردفتر: مصطفی سرپناه سورکوهی", bg="#f2f2f2", font=("B Nazanin", 16, "bold")).pack(side="left", padx=10)

        # تعریف فیلدها
        self.fields = {
            "نام": tk.StringVar(),
            "نام خانوادگی": tk.StringVar(),
            "شماره پلاک ثبتی": tk.StringVar(),
            "افراد ممنوع المعامله": tk.StringVar(),
            "صدور سند مالکیت المثنی": tk.StringVar(),
            "مفقودی سند مالکیت": tk.StringVar(),
            "ستون اضافه ۱": tk.StringVar(),
            "ستون اضافه ۲": tk.StringVar()
        }

        self.create_widgets()
        self.create_table()

    def create_widgets(self):
        row = 1
        for label, var in self.fields.items():
            tk.Label(self.root, text=label, bg="#f2f2f2", font=self.font).grid(row=row, column=0, padx=10, pady=5, sticky='e')
            tk.Entry(self.root, textvariable=var, font=self.font, width=40).grid(row=row, column=1, padx=10, pady=5, sticky='w')
            row += 1

        tk.Button(self.root, text="ذخیره", command=self.save_data, bg="#4CAF50", fg="white", font=self.font).grid(row=row, column=0, padx=10, pady=20)
        tk.Button(self.root, text="جستجو", command=self.search_data, bg="#2196F3", fg="white", font=self.font).grid(row=row, column=1, padx=10, pady=20, sticky='w')

    def create_table(self):
        self.tree = ttk.Treeview(self.root, columns=list(self.fields.keys()), show="headings", height=10)
        for col in self.fields.keys():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=20, column=0, columnspan=2, padx=10, pady=10)

    def save_data(self):
        data = {field: var.get() for field, var in self.fields.items()}
        df = pd.DataFrame([data])
        file_exists = os.path.isfile("notary_data.csv")
        if file_exists:
            df.to_csv("notary_data.csv", mode='a', header=False, index=False)
        else:
            df.to_csv("notary_data.csv", index=False)
        self.update_table()
        messagebox.showinfo("ذخیره", "اطلاعات با موفقیت ذخیره شد.")

    def search_data(self):
        self.update_table()

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if os.path.isfile("notary_data.csv"):
            df = pd.read_csv("notary_data.csv")
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=list(row))

if __name__ == "__main__":
    root = tk.Tk()
    app = NotaryApp(root)
    root.mainloop()
