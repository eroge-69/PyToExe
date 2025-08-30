import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys
import ctypes
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class HibernateFixer:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامه بررسی و تعمیر Hibernate برای متاتریدر 5")
        self.root.geometry("600x500")
        
        # ایجاد تب‌ها
        self.tab_control = ttk.Notebook(root)
        
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text='بررسی وضعیت')
        self.tab_control.add(self.tab2, text='تعمیر مشکلات')
        self.tab_control.add(self.tab3, text='راهنمایی')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # تب اول - بررسی وضعیت
        self.status_text = tk.Text(self.tab1, height=20, width=70)
        self.status_text.pack(pady=10, padx=10)
        
        self.check_btn = tk.Button(self.tab1, text="بررسی وضعیت", command=self.check_status)
        self.check_btn.pack(pady=5)
        
        # تب دوم - تعمیر مشکلات
        self.repair_label = tk.Label(self.tab2, text="برای تعمیر مشکلات شناسایی شده، دکمه زیر را بزنید:")
        self.repair_label.pack(pady=10)
        
        self.repair_btn = tk.Button(self.tab2, text="تعمیر خودکار", command=self.repair_issues)
        self.repair_btn.pack(pady=5)
        
        self.repair_status = tk.Label(self.tab2, text="")
        self.repair_status.pack(pady=5)
        
        # تب سوم - راهنمایی
        help_text = """
        راهنمای استفاده از برنامه:
        
        1. ابتدا از تب 'بررسی وضعیت' استفاده کنید تا مشکلات سیستم شناسایی شوند.
        2. در صورت وجود مشکل، به تب 'تعمیر مشکلات' رفته و روی دکمه 'تعمیر خودکار' کلیک کنید.
        3. پس از تعمیر، مجدداً وضعیت را بررسی کنید.
        
        مشکلات رایج Hibernate:
        - غیرفعال بودن Hibernate در سیستم
        - عدم وجود فضای کافی برای فایل Hibernate
        - تنظیمات نادرست در رجیستری
        - درایورهای قدیمی یا ناسازگار
        - مشکلات مربوط به سخت‌افزار
        - تداخل نرم‌افزارهای امنیتی با فرایند Hibernate
        
        برای عملکرد بهتر متاتریدر 5 پس از Hibernate:
        - مطمئن شوید آخرین نسخه متاتریدر را نصب کرده‌اید
        - درایورهای کارت گرافیک و سیستم را به روز کنید
        - از عدم تداخل آنتی‌ویروس با متاتریدر اطمینان حاصل کنید
        """
        
        self.help_text = tk.Text(self.tab3, height=25, width=70)
        self.help_text.pack(pady=10, padx=10)
        self.help_text.insert(tk.END, help_text)
        self.help_text.config(state=tk.DISABLED)
    
    def check_status(self):
        self.status_text.delete(1.0, tk.END)
        problems = []
        
        # بررسی فعال بودن Hibernate
        try:
            result = subprocess.run(['powercfg', '/availablesleepstates'], 
                                   capture_output=True, text=True, encoding='utf-8')
            if 'Hibernate' not in result.stdout:
                problems.append("Hibernate در سیستم شما فعال نیست")
        except:
            problems.append("خطا در بررسی وضعیت Hibernate")
        
        # بررسی وجود فایل hiberfil.sys و اندازه آن
        if os.path.exists("C:\\hiberfil.sys"):
            size = os.path.getsize("C:\\hiberfil.sys") / (1024 * 1024 * 1024)  # تبدیل به گیگابایت
            if size < 2:  # اگر کمتر از ۲ گیگابایت باشد
                problems.append(f"فایل Hibernate بسیار کوچک است ({size:.2f} GB). اندازه توصیه شده: 75% از RAM")
        else:
            problems.append("فایل Hibernate یافت نشد")
        
        # بررسی وضعیت رجیستری برای Hibernate
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power")
            value, _ = winreg.QueryValueEx(key, "HibernateEnabled")
            if value != 1:
                problems.append("Hibernate در رجیستری غیرفعال است")
            winreg.CloseKey(key)
        except:
            problems.append("خطا در بررسی رجیستری Hibernate")
        
        # نمایش نتایج
        if problems:
            self.status_text.insert(tk.END, "مشکلات شناسایی شده:\n\n")
            for i, problem in enumerate(problems, 1):
                self.status_text.insert(tk.END, f"{i}. {problem}\n")
            
            self.status_text.insert(tk.END, "\nلطفاً به تب 'تعمیر مشکلات' بروید تا مشکلات رفع شوند.")
        else:
            self.status_text.insert(tk.END, "هیچ مشکل شناخته شده‌ای در سیستم شما شناسایی نشد.\n")
            self.status_text.insert(tk.END, "اگر همچنان مشکل دارید، ممکن است مشکل از متاتریدر یا سخت‌افزار باشد.")
    
    def repair_issues(self):
        try:
            # فعال کردن Hibernate
            subprocess.run(['powercfg', '/hibernate', 'on'], check=True)
            
            # تنظیم اندازه فایل Hibernate به 75% از RAM (مقدار پیشفرض)
            subprocess.run(['powercfg', '/hibernate', '/size', '75'], check=True)
            
            # فعال کردن Hibernate در رجیستری
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "HibernateEnabled", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            self.repair_status.config(text="تعمیر با موفقیت انجام شد. لطفاً سیستم را restart کنید.")
            messagebox.showinfo("موفق", "تعمیر با موفقیت انجام شد. لطفاً سیستم را restart کنید.")
            
        except Exception as e:
            self.repair_status.config(text=f"خطا در تعمیر: {str(e)}")
            messagebox.showerror("خطا", f"خطا در تعمیر: {str(e)}")

if __name__ == "__main__":
    run_as_admin()
    
    root = tk.Tk()
    app = HibernateFixer(root)
    root.mainloop()
