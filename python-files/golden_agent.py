
# كود برنامج الوسيط الذهبي بلغة بايثون باستخدام Tkinter
# يشمل: إدخال، تعديل، حذف، بحث، نسخ احتياطي، وتصدير إلى Excel - يعمل أوفلاين ويدعم اللغة العربية

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv

DATA_FILE = "data.json"

class RealEstateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("الوسيط الذهبي - برنامج أرشفة العقارات")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f4f4f4")

        self.data = []
        self.load_data()

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#f4f4f4")
        frame.pack(pady=10)

        labels = ["اسم العقار", "اسم الوسيط", "رقم الوسيط", "نوع العقار", "الموقع", "السعر (د.ع)", "الحالة", "ملاحظات"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame, text=label, bg="#f4f4f4").grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky='e')
            entry = tk.Entry(frame, width=40)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)
            self.entries[label] = entry

        btn_frame = tk.Frame(self.root, bg="#f4f4f4")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="إضافة", command=self.add_entry).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="تعديل", command=self.edit_entry).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="حذف", command=self.delete_entry).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="نسخ احتياطي", command=self.backup_data).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="تصدير إلى Excel", command=self.export_to_excel).grid(row=0, column=4, padx=5)

        search_frame = tk.Frame(self.root, bg="#f4f4f4")
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="بحث:", bg="#f4f4f4").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_table())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side='left', padx=5)

        self.tree = ttk.Treeview(self.root, columns=labels, show="headings", height=10)
        for col in labels:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

        self.update_table()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_entry(self):
        entry = {key: self.entries[key].get() for key in self.entries}
        if not entry["اسم العقار"]:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم العقار.")
            return
        self.data.append(entry)
        self.save_data()
        self.update_table()
        self.clear_entries()

    def edit_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار عنصر لتعديله.")
            return
        index = self.tree.index(selected[0])
        self.data[index] = {key: self.entries[key].get() for key in self.entries}
        self.save_data()
        self.update_table()

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار عنصر لحذفه.")
            return
        index = self.tree.index(selected[0])
        del self.data[index]
        self.save_data()
        self.update_table()
        self.clear_entries()

    def backup_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("تم", "تم حفظ نسخة احتياطية بنجاح.")

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.entries.keys())
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("تم", "تم تصدير البيانات بنجاح.")

    def update_table(self):
        search = self.search_var.get()
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            if any(search.lower() in str(value).lower() for value in item.values()):
                self.tree.insert('', 'end', values=list(item.values()))

    def load_selected(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            for key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, self.data[index][key])

    def clear_entries(self):
        for key in self.entries:
            self.entries[key].delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealEstateApp(root)
    root.mainloop()
