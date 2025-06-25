
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

DATA_FILE = "devices_abdulmalik.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["رقم الجهاز", "نوع الجهاز", "MAC Address", "IP Address", "مكان التركيب", "الملكية", "الحالة", "التاريخ", "ملاحظات"])

class DeviceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("حصر الأجهزة - عبدالملك")
        self.root.geometry("1000x600")

        self.fields = ["رقم الجهاز", "نوع الجهاز", "MAC Address", "IP Address", "مكان التركيب", "الملكية", "الحالة", "التاريخ", "ملاحظات"]
        self.entries = {}

        form_frame = tk.Frame(root)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        for i, field in enumerate(self.fields):
            lbl = tk.Label(form_frame, text=field)
            lbl.grid(row=0, column=i, padx=5)
            entry = tk.Entry(form_frame, width=15)
            entry.grid(row=1, column=i, padx=5)
            self.entries[field] = entry

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="إضافة", command=self.add_device).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="حذف المحدد", command=self.delete_selected).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="تصدير CSV", command=self.export_csv).pack(side=tk.LEFT, padx=10)

        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="بحث:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_table)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(root, columns=self.fields, show="headings")
        for field in self.fields:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=100)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.load_data()

    def add_device(self):
        values = [self.entries[f].get() for f in self.fields]
        if not all(values[:4]):
            messagebox.showwarning("تحذير", "يرجى تعبئة الحقول الأساسية.")
            return
        with open(DATA_FILE, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(values)
        self.clear_entries()
        self.load_data()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        all_data = self.get_all_data()
        selected_values = [self.tree.item(item)['values'] for item in selected]
        remaining_data = [row for row in all_data if row not in selected_values]
        with open(DATA_FILE, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.fields)
            writer.writerows(remaining_data)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with open(DATA_FILE, "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if self.search_var.get().lower() in " ".join(row).lower():
                    self.tree.insert("", tk.END, values=row)

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def get_all_data(self):
        with open(DATA_FILE, "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            return list(reader)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(DATA_FILE, "r", newline='', encoding='utf-8') as f_in, open(file_path, "w", newline='', encoding='utf-8') as f_out:
                f_out.write(f_in.read())
            messagebox.showinfo("تم", "تم تصدير البيانات بنجاح.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeviceApp(root)
    root.mainloop()
