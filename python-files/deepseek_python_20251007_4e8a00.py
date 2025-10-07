import tkinter as tk
from tkinter import ttk
import jdatetime
from tkinter import messagebox

class PersianCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("تقویم جلالی")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # تنظیم فونت برای پشتیبانی از فارسی
        self.font = ("Tahoma", 12)
        
        # تاریخ کنونی
        self.current_date = jdatetime.date.today()
        
        self.create_widgets()
        self.update_calendar()
    
    def create_widgets(self):
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # هدر با تاریخ امروز
        self.header_label = ttk.Label(main_frame, 
                                     text=self.get_current_date_string(),
                                     font=("Tahoma", 16, "bold"))
        self.header_label.pack(pady=10)
        
        # کنترل‌های ناوبری
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(pady=10)
        
        ttk.Button(nav_frame, text="ماه قبل", 
                  command=self.previous_month).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(nav_frame, text="امروز", 
                  command=self.go_to_today).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(nav_frame, text="ماه بعد", 
                  command=self.next_month).pack(side=tk.RIGHT, padx=5)
        
        # نمایش ماه و سال
        self.month_year_label = ttk.Label(main_frame, 
                                         font=("Tahoma", 14, "bold"))
        self.month_year_label.pack(pady=5)
        
        # ایجاد جدول تقویم
        self.create_calendar_grid(main_frame)
        
        # اطلاعات اضافی
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(info_frame, text="اطلاعات تاریخ انتخاب شده:", 
                 font=("Tahoma", 12, "bold")).pack()
        
        self.selected_date_label = ttk.Label(info_frame, 
                                            font=("Tahoma", 10))
        self.selected_date_label.pack()
    
    def create_calendar_grid(self, parent):
        # فریم برای روزهای هفته
        days_frame = ttk.Frame(parent)
        days_frame.pack(pady=10)
        
        # نام روزهای هفته
        persian_days = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        
        for i, day in enumerate(persian_days):
            label = ttk.Label(days_frame, text=day, 
                             font=("Tahoma", 12, "bold"),
                             width=5, anchor="center")
            label.grid(row=0, column=i, padx=2, pady=2)
        
        # ایجاد جدول تقویم
        self.calendar_frame = ttk.Frame(parent)
        self.calendar_frame.pack()
        
        self.day_buttons = []
        for row in range(6):
            row_buttons = []
            for col in range(7):
                btn = ttk.Button(self.calendar_frame, 
                               text="", 
                               width=5,
                               command=lambda r=row, c=col: self.on_date_click(r, c))
                btn.grid(row=row, column=col, padx=2, pady=2)
                row_buttons.append(btn)
            self.day_buttons.append(row_buttons)
    
    def update_calendar(self):
        # به روزرسانی برچسب ماه و سال
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        month_name = month_names[self.current_date.month - 1]
        self.month_year_label.config(
            text=f"{month_name} {self.current_date.year}"
        )
        
        # محاسبه اولین روز ماه
        first_day = jdatetime.date(self.current_date.year, self.current_date.month, 1)
        
        # پیدا کردن روز هفته برای اولین روز ماه (0=شنبه, 6=جمعه)
        start_day = (first_day.weekday() + 2) % 7  # تنظیم برای شروع از شنبه
        
        # تعداد روزهای ماه
        if self.current_date.month <= 6:
            days_in_month = 31
        elif self.current_date.month <= 11:
            days_in_month = 30
        else:  # اسفند
            # بررسی سال کبیسه
            if first_day.isleap():
                days_in_month = 30
            else:
                days_in_month = 29
        
        # پاک کردن تقویم
        for row in self.day_buttons:
            for btn in row:
                btn.config(text="", state="disabled")
        
        # پر کردن تقویم با روزهای ماه
        day_counter = 1
        for row in range(6):
            for col in range(7):
                if (row == 0 and col < start_day) or day_counter > days_in_month:
                    continue
                
                if day_counter <= days_in_month:
                    btn = self.day_buttons[row][col]
                    btn.config(text=str(day_counter), state="normal")
                    
                    # هایلایت کردن تاریخ امروز
                    if (day_counter == self.current_date.day and 
                        self.current_date.year == jdatetime.date.today().year and
                        self.current_date.month == jdatetime.date.today().month):
                        btn.config(style="Today.TButton")
                    else:
                        btn.config(style="TButton")
                    
                    day_counter += 1
    
    def previous_month(self):
        # رفتن به ماه قبل
        if self.current_date.month == 1:
            self.current_date = jdatetime.date(
                self.current_date.year - 1, 12, 1
            )
        else:
            self.current_date = jdatetime.date(
                self.current_date.year, self.current_date.month - 1, 1
            )
        self.update_calendar()
    
    def next_month(self):
        # رفتن به ماه بعد
        if self.current_date.month == 12:
            self.current_date = jdatetime.date(
                self.current_date.year + 1, 1, 1
            )
        else:
            self.current_date = jdatetime.date(
                self.current_date.year, self.current_date.month + 1, 1
            )
        self.update_calendar()
    
    def go_to_today(self):
        # بازگشت به تاریخ امروز
        self.current_date = jdatetime.date.today()
        self.update_calendar()
        self.header_label.config(text=self.get_current_date_string())
    
    def on_date_click(self, row, col):
        # مدیریت کلیک روی تاریخ
        day_text = self.day_buttons[row][col].cget("text")
        if day_text:
            day = int(day_text)
            selected_date = jdatetime.date(
                self.current_date.year, self.current_date.month, day
            )
            
            # نمایش اطلاعات تاریخ انتخاب شده
            self.show_date_info(selected_date)
    
    def show_date_info(self, date):
        # نمایش اطلاعات تاریخ انتخاب شده
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        day_names = [
            "شنبه", "یکشنبه", "دوشنبه", "سه شنبه", 
            "چهارشنبه", "پنجشنبه", "جمعه"
        ]
        
        month_name = month_names[date.month - 1]
        day_name = day_names[date.weekday()]
        
        info_text = f"{day_name}، {date.day} {month_name} {date.year}"
        
        # تبدیل به میلادی
        gregorian_date = date.togregorian()
        info_text += f"\nمیلادی: {gregorian_date.strftime('%Y/%m/%d')}"
        
        self.selected_date_label.config(text=info_text)
    
    def get_current_date_string(self):
        # دریافت رشته تاریخ امروز
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        today = jdatetime.date.today()
        month_name = month_names[today.month - 1]
        
        return f"امروز: {today.day} {month_name} {today.year}"

def main():
    root = tk.Tk()
    
    # ایجاد استایل برای دکمه امروز
    style = ttk.Style()
    style.configure("Today.TButton", background="#ffeb3b")
    
    app = PersianCalendar(root)
    root.mainloop()

if __name__ == "__main__":
    main()