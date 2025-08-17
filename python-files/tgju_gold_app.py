import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import re
import time
import datetime as dt
import jdatetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

# --- کلاس TGJUGoldFetcher: منطق استخراج داده ---
class TGJUGoldFetcher:
    BASE_URL = "https://english.tgju.org/profile/geram18"
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.stop_flag = False

    def _update_status(self, message):
        """فراخوانی تابع بازگشتی برای به‌روزرسانی وضعیت در UI"""
        if self.status_callback:
            self.status_callback(message)

    def stop(self):
        """تنظیم پرچم توقف برای خاتمه عملیات"""
        self.stop_flag = True

    def fetch_data(self, start_jalali_str, end_jalali_str, output_filepath):
        """
        استخراج داده‌های طلا از TGJU و ذخیره در فایل اکسل.
        
        پارامترها:
            start_jalali_str (str): تاریخ شروع به فرمت شمسی YYYY-MM-DD.
            end_jalali_str (str): تاریخ پایان به فرمت شمسی YYYY-MM-DD.
            output_filepath (str): مسیر کامل فایل اکسل خروجی.
        
        بازگشتی:
            bool: True اگر عملیات موفق بود، False در غیر این صورت.
        """
        self.stop_flag = False
        try:
            # 1. اعتبارسنجی و تبدیل تاریخ‌ها
            start_jalali_date = jdatetime.date.fromisoformat(start_jalali_str)
            end_jalali_date = jdatetime.date.fromisoformat(end_jalali_str)

            if start_jalali_date > end_jalali_date:
                raise ValueError("تاریخ شروع باید قبل از یا برابر با تاریخ پایان باشد.")

            start_gregorian_date = start_jalali_date.togregorian()
            end_gregorian_date = end_jalali_date.togregorian()

            self._update_status(f"در حال جمع‌آوری داده‌ها از {start_jalali_str} تا {end_jalali_str}...")

            all_data = []
            page = 1
            # این پرچم نشان می‌دهد که آیا در حین استخراج، به داده‌ای رسیده‌ایم که از تاریخ شروع ما قدیمی‌تر است.
            # چون صفحات از جدید به قدیم هستند، اگر به این حالت برسیم یعنی همه داده‌های مورد نیاز را استخراج کرده‌ایم.
            reached_start_date_in_history = False 

            while not self.stop_flag:
                url = f"{self.BASE_URL}?p={page}"
                self._update_status(f"در حال دریافت صفحه {page}...")
                
                try:
                    html = requests.get(url, headers=self.HEADERS, timeout=15).text
                except requests.exceptions.RequestException as e:
                    raise IOError(f"خطا در ارتباط شبکه: {e}. لطفا اتصال اینترنت را بررسی کنید.")

                soup = BeautifulSoup(html, "html.parser")
                rows = soup.findAll("tr")
                
                if not rows: # اگر صفحه‌ای خالی از سطرها بود، یعنی به پایان تاریخچه رسیده‌ایم
                    break

                page_processed_any_data_row = False # آیا در این صفحه حداقل یک سطر داده معتبر پیدا کردیم؟
                
                for r in rows:
                    if self.stop_flag: break # بررسی پرچم توقف در هر مرحله
                    cols = [c.get_text(strip=True).replace(',', '') for c in r.findAll("td")]
                    # بررسی اینکه آیا سطر یک سطر داده‌ای معتبر است
                    if len(cols) >= 6 and re.match(r"^\d{4}-\d{2}-\d{2}$", cols[0]):
                        page_processed_any_data_row = True

                        gdate_str = cols[0]
                        gdate = dt.date.fromisoformat(gdate_str)

                        if gdate < start_gregorian_date:
                            # اگر تاریخ فعلی قدیمی‌تر از تاریخ شروع ما بود، یعنی از بازه مورد نظر عبور کرده‌ایم
                            reached_start_date_in_history = True
                            break # از حلقه داخلی (بررسی سطرها) خارج شو، چون بقیه سطرها و صفحات بعدی هم قدیمی‌ترند

                        if gdate > end_gregorian_date:
                            continue # این تاریخ جدیدتر از تاریخ پایان ماست، پس آن را نادیده بگیر

                        # اگر به اینجا رسیدیم، تاریخ در بازه [start_gregorian_date, end_gregorian_date] قرار دارد
                        try:
                            high = int(cols[1])
                            low = int(cols[2])
                            avg = (high + low) // 2
                            all_data.append([gdate, high, low, avg])
                        except ValueError:
                            self._update_status(f"هشدار: داده‌های نامعتبر برای تاریخ {gdate_str} یافت شد. نادیده گرفته شد.")
                            continue
                
                if reached_start_date_in_history:
                    break # اگر به تاریخ شروع در تاریخچه رسیدیم، کل عملیات استخراج را متوقف کن

                if not page_processed_any_data_row and page > 1:
                    # اگر در صفحه‌ای که خالی از سطر نبودیم، هیچ سطر داده‌ای معتبری پیدا نشد (غیر از صفحه اول)
                    # احتمالاً به پایان تاریخچه یا داده‌های نامربوط رسیده‌ایم
                    break

                page += 1
                time.sleep(0.7) # برای رعایت قوانین کرالینگ و جلوگیری از بلاک شدن IP

            if self.stop_flag:
                self._update_status("عملیات توسط کاربر متوقف شد.")
                return False

            if not all_data:
                self._update_status("هیچ داده‌ای برای بازه تاریخ مشخص شده یافت نشد. لطفا بازه را بررسی کنید.")
                return False

            df = pd.DataFrame(all_data, columns=["GregorianDate", "High", "Low", "Average"])
            df.sort_values("GregorianDate", inplace=True) # اطمینان از ترتیب صعودی برای محاسبه روند

            # فیلتر نهایی برای اطمینان از اینکه داده‌ها دقیقاً در بازه مشخص‌شده هستند
            df = df[(df["GregorianDate"] >= start_gregorian_date) & (df["GregorianDate"] <= end_gregorian_date)]
            
            if df.empty:
                self._update_status("هیچ داده‌ای برای بازه تاریخ مشخص شده یافت نشد. لطفا بازه را بررسی کنید.")
                return False

            df["PersianDate"] = [jdatetime.date.fromgregorian(date=d) for d in df["GregorianDate"]]
            
            # محاسبه روند (صعودی/نزولی/بدون تغییر)
            df['Previous_Average'] = df['Average'].shift(1)
            
            def get_trend(row):
                if pd.isna(row['Previous_Average']):
                    return "---" # برای اولین روز داده‌ای برای مقایسه با روز قبل نیست
                if row['Average'] > row['Previous_Average']:
                    return "صعودی"
                elif row['Average'] < row['Previous_Average']:
                    return "نزولی"
                else:
                    return "بدون تغییر"

            df["Trend"] = df.apply(get_trend, axis=1)

            # انتخاب ستون‌ها و تغییر نام آن‌ها طبق درخواست شما
            df = df[["PersianDate", "Low", "High", "Average", "Trend"]]
            df.columns = ["تاریخ", "حداقل", "حداکثر", "میانگین", "روند"]

            # ذخیره در فایل اکسل
            try:
                df.to_excel(output_filepath, index=False)
                self._update_status(f"عملیات با موفقیت انجام شد. فایل در: {output_filepath} ذخیره شد.")
                return True
            except Exception as e:
                raise IOError(f"خطا در ذخیره فایل اکسل: {e}. لطفا مطمئن شوید فایل باز نیست و مسیر معتبر است.")

        except ValueError as e:
            self._update_status(f"خطای تاریخ: {e}")
            return False
        except IOError as e:
            self._update_status(f"خطا: {e}")
            return False
        except Exception as e:
            self._update_status(f"خطای ناشناخته: {e}")
            return False

# --- کلاس GoldApp: رابط کاربری Tkinter ---
class GoldApp:
    def __init__(self, master):
        self.master = master
        master.title("استخراج قیمت طلا از TGJU")
        master.geometry("450x300")
        master.resizable(False, False) # اندازه ثابت پنجره

        self.fetcher = TGJUGoldFetcher(self.update_status)
        self.current_thread = None

        self._create_widgets()

    def _create_widgets(self):
        # ورودی‌های تاریخ
        ttk.Label(self.master, text="تاریخ شروع (مثال: 1403-01-01):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.start_date_entry = ttk.Entry(self.master, width=20)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.start_date_entry.insert(0, jdatetime.date(1403, 1, 1).isoformat()) # تاریخ پیش‌فرض فروردین 1403

        ttk.Label(self.master, text="تاریخ پایان (مثال: 1404-05-31):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.end_date_entry = ttk.Entry(self.master, width=20)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        # تاریخ پیش‌فرض مرداد 1404 (از تاریخ فعلی)
        self.end_date_entry.insert(0, jdatetime.date.today().isoformat()) 

        # مسیر خروجی فایل
        ttk.Label(self.master, text="مسیر ذخیره فایل اکسل:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.output_path_entry = ttk.Entry(self.master, width=25)
        self.output_path_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.output_path_entry.insert(0, "gold_prices.xlsx") # نام فایل پیش‌فرض

        self.browse_button = ttk.Button(self.master, text="مرور", command=self.browse_output_path)
        self.browse_button.grid(row=2, column=2, padx=5, pady=5)

        # دکمه‌های عملیاتی
        self.start_button = ttk.Button(self.master, text="شروع استخراج", command=self.start_fetching)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.stop_button = ttk.Button(self.master, text="توقف", command=self.stop_fetching, state=tk.DISABLED)
        self.stop_button.grid(row=3, column=2, pady=10)

        # برچسب وضعیت
        self.status_label = ttk.Label(self.master, text="آماده به کار", wraplength=400, justify="right")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.status_label.configure(foreground="blue")

        # تنظیم ستون‌ها برای واکنش‌پذیری (اگر پنجره قابل تغییر اندازه باشد)
        self.master.grid_columnconfigure(1, weight=1)

    def update_status(self, message):
        """به‌روزرسانی برچسب وضعیت در ترد اصلی Tkinter"""
        self.master.after(0, lambda: self.status_label.config(text=message))

    def browse_output_path(self):
        """باز کردن پنجره انتخاب مسیر ذخیره فایل"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=self.output_path_entry.get()
        )
        if filepath:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, filepath)

    def start_fetching(self):
        """شروع عملیات استخراج در یک ترد جداگانه"""
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        output_filepath = self.output_path_entry.get()

        # اعتبارسنجی اولیه فرمت تاریخ
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date_str) or \
           not re.match(r"^\d{4}-\d{2}-\d{2}$", end_date_str):
            messagebox.showerror("خطا", "لطفا تاریخ را با فرمت صحیح YYYY-MM-DD وارد کنید.")
            return

        if not output_filepath:
            messagebox.showerror("خطا", "لطفا مسیر ذخیره فایل را مشخص کنید.")
            return

        # غیرفعال کردن دکمه شروع و فعال کردن دکمه توقف
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("شروع عملیات استخراج...")

        # اجرای عملیات استخراج در یک ترد جداگانه
        self.current_thread = threading.Thread(target=self._run_fetching_thread, args=(start_date_str, end_date_str, output_filepath))
        self.current_thread.start()

    def _run_fetching_thread(self, start_date_str, end_date_str, output_filepath):
        """تابع اجرایی ترد استخراج داده"""
        success = self.fetcher.fetch_data(start_date_str, end_date_str, output_filepath)
        
        # پس از اتمام عملیات (موفق یا ناموفق)، دکمه‌ها را به حالت اولیه برگردان
        self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        
        if success:
            self.master.after(0, lambda: messagebox.showinfo("پایان عملیات", "داده‌ها با موفقیت استخراج و ذخیره شدند."))
        elif not self.fetcher.stop_flag: # اگر کاربر عملیات را متوقف نکرده باشد، یعنی خطایی رخ داده است
             # پیغام خطا توسط fetch_data در status_label به‌روز شده است
             self.master.after(0, lambda: messagebox.showerror("خطا", "عملیات استخراج با خطا مواجه شد. جزئیات در وضعیت نمایش داده شده است."))


    def stop_fetching(self):
        """درخواست توقف عملیات استخراج"""
        if self.current_thread and self.current_thread.is_alive():
            self.fetcher.stop()
            self.stop_button.config(state=tk.DISABLED)
            self.update_status("درخواست توقف ارسال شد. در حال اتمام عملیات جاری...")
        
# --- نقطه شروع برنامه ---
if __name__ == "__main__":
    # بررسی اتصال اینترنت قبل از شروع برنامه
    try:
        requests.get("http://www.google.com", timeout=5)
    except requests.exceptions.ConnectionError:
        messagebox.showerror("خطای اتصال به اینترنت", "لطفاً اتصال اینترنت خود را بررسی کنید. برنامه نیاز به دسترسی به اینترنت دارد.")
        exit()

    root = tk.Tk()
    app = GoldApp(root)
    root.mainloop()