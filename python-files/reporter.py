import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from persiantools.jdatetime import JalaliDate
import os

class LocomotiveServiceForm:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم ثبت خدمات لکوموتیو")
        self.root.geometry("800x700")
        
        # لیست خدمات پرتکرار
        self.common_services = [
            "ایونت گیری",
            "تست تحریک",
            "تست ترمز",
            "سرریز روغن",
            "تست سلف لود",
            "آبگیری دیزل",
            "شارژ روغن گاورنر",
            "تعویض زغال پمپ سوخت"
        ]
        
        # لیست برای ذخیره خدمات اضافی
        self.additional_services = []
        
        # متغیرهای فرم
        self.loco_number = tk.StringVar()
        self.service_date = tk.StringVar()
        self.region = tk.StringVar()
        self.shift = tk.StringVar()
        self.common_services_vars = [tk.IntVar() for _ in range(len(self.common_services))]
        
        # ایجاد فرم
        self.create_form()
        
    def create_form(self):
        # قاب اصلی
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان فرم
        ttk.Label(main_frame, text="فرم ثبت خدمات لکوموتیو", font=("Tahoma", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # فیلد شماره لکوموتیو
        ttk.Label(main_frame, text="شماره لکوموتیو:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.loco_number).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # فیلد تاریخ سرویس
        ttk.Label(main_frame, text="تاریخ سرویس (شمسی):").grid(row=2, column=0, sticky=tk.W, pady=5)
        today = JalaliDate.today().strftime("%Y/%m/%d")
        self.service_date.set(today)
        ttk.Entry(main_frame, textvariable=self.service_date).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # فیلد ناحیه سرویس
        ttk.Label(main_frame, text="ناحیه سرویس:").grid(row=3, column=0, sticky=tk.W, pady=5)
        regions = ["اردکان", "چادرملو", "اصفهان", "طبس", "تربت", "آپرین"]
        ttk.Combobox(main_frame, textvariable=self.region, values=regions).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # فیلد شیفت
        ttk.Label(main_frame, text="شیفت:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.shift, values=["صبح", "شب"]).grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # خدمات پرتکرار (چک باکس)
        ttk.Label(main_frame, text="خدمات پرتکرار:", font=("Tahoma", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        for i, service in enumerate(self.common_services):
            ttk.Checkbutton(main_frame, text=service, variable=self.common_services_vars[i]).grid(row=6+i//2, column=i%2, sticky=tk.W, pady=2)
        
        # خدمات اضافی
        ttk.Label(main_frame, text="سایر خدمات:", font=("Tahoma", 10, "bold")).grid(row=10, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        self.additional_services_frame = ttk.Frame(main_frame)
        self.additional_services_frame.grid(row=11, column=0, columnspan=2, sticky=tk.EW)
        
        # ایجاد 5 کادر اولیه برای خدمات اضافی
        self.create_additional_service_row()
        self.create_additional_service_row()
        self.create_additional_service_row()
        self.create_additional_service_row()
        self.create_additional_service_row()
        
        # دکمه اضافه کردن سطر جدید
        ttk.Button(main_frame, text="خدمت بعدی +", command=self.create_additional_service_row).grid(row=12, column=0, columnspan=2, pady=10)
        
        # دکمه ثبت گزارش
        ttk.Button(main_frame, text="ثبت گزارش", command=self.save_report).grid(row=13, column=0, columnspan=2, pady=20)
        
        # تنظیمات ستون‌ها
        main_frame.columnconfigure(1, weight=1)
        
    def create_additional_service_row(self):
        row = len(self.additional_services)
        
        service_var = tk.StringVar()
        time_var = tk.StringVar()
        
        frame = ttk.Frame(self.additional_services_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=f"خدمت {row+1}:").pack(side=tk.LEFT, padx=5)
        service_entry = ttk.Entry(frame, textvariable=service_var, width=40)
        service_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(frame, text="زمان (دقیقه):").pack(side=tk.LEFT, padx=5)
        time_entry = ttk.Entry(frame, textvariable=time_var, width=5)
        time_entry.pack(side=tk.LEFT, padx=5)
        
        self.additional_services.append((service_var, time_var))
        
    def save_report(self):
        # اعتبارسنجی فیلدهای اجباری
        if not self.loco_number.get():
            messagebox.showerror("خطا", "لطفاً شماره لکوموتیو را وارد کنید")
            return
            
        if not self.service_date.get():
            messagebox.showerror("خطا", "لطفاً تاریخ سرویس را وارد کنید")
            return
            
        if not self.region.get():
            messagebox.showerror("خطا", "لطفاً ناحیه سرویس را انتخاب کنید")
            return
            
        # جمع‌آوری خدمات انتخاب شده
        selected_services = []
        
        # خدمات پرتکرار انتخاب شده
        for i, var in enumerate(self.common_services_vars):
            if var.get() == 1:
                selected_services.append((self.common_services[i], ""))  # زمان برای خدمات پرتکرار خالی است
                
        # خدمات اضافی
        for service_var, time_var in self.additional_services:
            service = service_var.get().strip()
            time = time_var.get().strip()
            
            if service:
                selected_services.append((service, time))
                
        if not selected_services:
            messagebox.showerror("خطا", "حداقل یک خدمت باید انتخاب یا وارد شود")
            return
            
        # آماده‌سازی داده برای ذخیره در اکسل
        data = []
        loco_num = self.loco_number.get()
        date = self.service_date.get()
        region = self.region.get()
        shift = self.shift.get() if self.shift.get() else ""
        
        for service, time in selected_services:
            data.append({
                "دیزل": loco_num,
                "تاریخ": date,
                "واحد": region,
                "شیفت": shift,
                "خدمات مازاد": service,
                "زمان": time
            })
            
        # ذخیره در فایل اکسل
        df = pd.DataFrame(data)
        
        # اگر فایل وجود دارد، داده جدید را به آن اضافه می‌کنیم
        if os.path.exists("services_report.xlsx"):
            existing_df = pd.read_excel("services_report.xlsx")
            df = pd.concat([existing_df, df], ignore_index=True)
            
        df.to_excel("services_report.xlsx", index=False)
        
        messagebox.showinfo("موفق", "گزارش با موفقیت ثبت شد")
        
        # ریست فرم برای ورود بعدی
        self.reset_form()
        
    def reset_form(self):
        # ریست تمام فیلدها به جز تاریخ
        self.loco_number.set("")
        self.region.set("")
        self.shift.set("")
        
        for var in self.common_services_vars:
            var.set(0)
            
        for service_var, time_var in self.additional_services:
            service_var.set("")
            time_var.set("")
            
        # حذف سطرهای اضافی بیش از 5 سطر اولیه
        while len(self.additional_services) > 5:
            self.additional_services[-1][0].set("")
            self.additional_services[-1][1].set("")
            self.additional_services.pop()
            
        # پاک کردن ویجت‌های اضافی
        for widget in self.additional_services_frame.winfo_children():
            widget.destroy()
            
        # ایجاد مجدد 5 سطر اولیه
        for _ in range(5):
            self.create_additional_service_row()

if __name__ == "__main__":
    root = tk.Tk()
    app = LocomotiveServiceForm(root)
    root.mainloop()