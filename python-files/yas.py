import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

def convert_csv_to_xlsx(csv_file, xlsx_file, phone_column):
    try:
        # خواندن فایل CSV
        df = pd.read_csv(csv_file)
        
        # اگر ستون شماره تماس وجود داشت، به متن تبدیل کن
        if phone_column in df.columns:
            df[phone_column] = df[phone_column].astype(str)
        
        # نوشتن به فایل XLSX
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            if phone_column in df.columns:
                col_idx = df.columns.get_loc(phone_column) + 1
                for row in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row, column=col_idx)
                    cell.number_format = '@'  # فرمت text
        
        return f"تبدیل با موفقیت انجام شد! فایل خروجی: {xlsx_file}"
    except Exception as e:
        return f"خطا: {str(e)}"

class CSVtoXLSXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تبدیل CSV به Excel")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # تنظیم تم و استایل
        style = ttk.Style()
        style.theme_use('clam')  # تم مدرن
        style.configure('TButton', font=('Arial', 10), padding=10)
        style.configure('TLabel', font=('Arial', 11))
        style.configure('TEntry', font=('Arial', 10))
        
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # برچسب و دکمه انتخاب فایل CSV
        ttk.Label(main_frame, text="فایل CSV را انتخاب کنید:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.csv_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.csv_path_var, width=40, state='readonly').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="انتخاب فایل", command=self.select_csv_file).grid(row=1, column=1, padx=5)
        
        # فیلد برای نام ستون شماره تماس
        ttk.Label(main_frame, text="نام ستون شماره تماس (مثل Phone یا Mobile):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_column_var = tk.StringVar(value="Phone")
        ttk.Entry(main_frame, textvariable=self.phone_column_var, width=20).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # دکمه ذخیره فایل خروجی
        ttk.Label(main_frame, text="محل ذخیره فایل Excel:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.xlsx_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.xlsx_path_var, width=40, state='readonly').grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="ذخیره فایل", command=self.select_xlsx_file).grid(row=5, column=1, padx=5)
        
        # دکمه تبدیل
        ttk.Button(main_frame, text="تبدیل کن", command=self.convert).grid(row=6, column=0, columnspan=2, pady=20)
        
        # برچسب وضعیت
        self.status_var = tk.StringVar(value="لطفاً فایل CSV را انتخاب کنید")
        ttk.Label(main_frame, textvariable=self.status_var, wraplength=400).grid(row=7, column=0, columnspan=2, pady=5)
        
        # تنظیم رنگ پس‌زمینه و دکمه‌ها
        self.root.configure(bg='#f0f0f0')
        style.configure('TButton', background='#4CAF50', foreground='white')
        style.map('TButton', background=[('active', '#45a049')])
    
    def select_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_path_var.set(file_path)
            self.status_var.set("فایل CSV انتخاب شد. حالا فایل خروجی را مشخص کنید.")
    
    def select_xlsx_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.xlsx_path_var.set(file_path)
            self.status_var.set("فایل خروجی انتخاب شد. حالا دکمه تبدیل را بزنید.")
    
    def convert(self):
        csv_file = self.csv_path_var.get()
        xlsx_file = self.xlsx_path_var.get()
        phone_column = self.phone_column_var.get()
        
        if not csv_file or not xlsx_file:
            messagebox.showerror("خطا", "لطفاً فایل CSV و محل ذخیره Excel را انتخاب کنید.")
            return
        
        result = convert_csv_to_xlsx(csv_file, xlsx_file, phone_column)
        self.status_var.set(result)
        if "موفقیت" in result:
            messagebox.showinfo("موفق", result)
        else:
            messagebox.showerror("خطا", result)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVtoXLSXApp(root)
    root.mainloop()