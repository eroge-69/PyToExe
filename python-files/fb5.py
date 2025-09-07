import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import os
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed

class AccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Manager")
        self.root.geometry("800x600")
        
        # حالة البرنامج
        self.is_running = False
        self.is_paused = False
        self.current_thread = None
        
        # إعدادات
        self.min_delay = 1  # ثانية
        self.max_delay = 5  # ثانية
        self.concurrent_browsers = 3  # عدد المتصفحات التي تعمل في نفس الوقت
        
        # إنشاء الواجهة
        self.create_widgets()
        
        # إنشاء مجلد لحفظ الكوكيز
        self.cookies_dir = "cookies"
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
    
    def create_widgets(self):
        # إطار الحسابات
        accounts_frame = ttk.LabelFrame(self.root, text="الحسابات (email:pass)")
        accounts_frame.pack(fill="x", padx=10, pady=5)
        
        self.accounts_text = scrolledtext.ScrolledText(accounts_frame, height=8)
        self.accounts_text.pack(fill="x", padx=5, pady=5)
        
        # عداد الحسابات
        self.accounts_count_var = tk.StringVar(value="عدد الحسابات: 0")
        self.accounts_count_label = ttk.Label(accounts_frame, textvariable=self.accounts_count_var)
        self.accounts_count_label.pack(pady=5)
        
        # أزرار الإضافة والمسح للحسابات
        accounts_buttons_frame = ttk.Frame(accounts_frame)
        accounts_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.add_btn = ttk.Button(accounts_buttons_frame, text="إضافة", command=self.add_accounts)
        self.add_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(accounts_buttons_frame, text="مسح", command=self.clear_accounts)
        self.clear_btn.pack(side="left", padx=5)
        
        # إطار الحسابات النشطة وغير النشطة
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # الحسابات النشطة
        active_frame = ttk.LabelFrame(status_frame, text="الحسابات النشطة")
        active_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.active_listbox = tk.Listbox(active_frame)
        self.active_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # عداد الحسابات النشطة
        self.active_count_var = tk.StringVar(value="عدد الحسابات النشطة: 0")
        self.active_count_label = ttk.Label(active_frame, textvariable=self.active_count_var)
        self.active_count_label.pack(pady=5)
        
        # زر حفظ الحسابات النشطة
        self.save_active_btn = ttk.Button(active_frame, text="حفظ", command=self.save_active_accounts)
        self.save_active_btn.pack(pady=5)
        
        # الحسابات غير النشطة
        inactive_frame = ttk.LabelFrame(status_frame, text="الحسابات غير النشطة")
        inactive_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.inactive_listbox = tk.Listbox(inactive_frame)
        self.inactive_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # عداد الحسابات غير النشطة
        self.inactive_count_var = tk.StringVar(value="عدد الحسابات غير النشطة: 0")
        self.inactive_count_label = ttk.Label(inactive_frame, textvariable=self.inactive_count_var)
        self.inactive_count_label.pack(pady=5)
        
        # إطار الإعدادات العامة
        settings_frame = ttk.LabelFrame(self.root, text="الإعدادات العامة")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # زمن التأخير
        ttk.Label(settings_frame, text="زمن التأخير (ثانية):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.min_delay_var = tk.StringVar(value="1")
        self.min_delay_spin = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.min_delay_var, width=8)
        self.min_delay_spin.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="إلى").grid(row=0, column=2, padx=5, pady=5)
        
        self.max_delay_var = tk.StringVar(value="5")
        self.max_delay_spin = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.max_delay_var, width=8)
        self.max_delay_spin.grid(row=0, column=3, padx=5, pady=5)
        
        # عدد المتصفحات المتزامنة
        ttk.Label(settings_frame, text="المتصفحات المتزامنة:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        self.concurrent_var = tk.StringVar(value="3")
        self.concurrent_spin = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.concurrent_var, width=8)
        self.concurrent_spin.grid(row=1, column=1, padx=5, pady=5)
        
        # خيارات إضافية
        ttk.Label(settings_frame, text="وضع المتصفح:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(settings_frame, text="خفي (Headless)", variable=self.headless_var)
        self.headless_check.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # عنوان URL للهدف
        ttk.Label(settings_frame, text="URL الهدف:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.target_url_var = tk.StringVar(value="https://www.facebook.com")
        self.target_url_entry = ttk.Entry(settings_frame, textvariable=self.target_url_var, width=30)
        self.target_url_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
        # أزرار التحكم
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ttk.Button(buttons_frame, text="Start", command=self.start_process)
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = ttk.Button(buttons_frame, text="Pause", command=self.pause_process, state="disabled")
        self.pause_btn.pack(side="left", padx=5)
        
        self.resume_btn = ttk.Button(buttons_frame, text="Resume", command=self.resume_process, state="disabled")
        self.resume_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="Stop", command=self.stop_process, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # حالة التشغيل
        self.status_var = tk.StringVar(value="جاهز")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill="x", padx=10, pady=5)
        
        # ربط حدث تغيير النص في حقل الحسابات لتحديث العداد
        self.accounts_text.bind("<KeyRelease>", self.update_accounts_count)
    
    def update_accounts_count(self, event=None):
        """تحديث عداد الحسابات في الحقل الأول"""
        accounts = self.get_accounts()
        self.accounts_count_var.set(f"عدد الحسابات: {len(accounts)}")
    
    def update_active_count(self):
        """تحديث عداد الحسابات النشطة"""
        count = self.active_listbox.size()
        self.active_count_var.set(f"عدد الحسابات النشطة: {count}")
    
    def update_inactive_count(self):
        """تحديث عداد الحسابات غير النشطة"""
        count = self.inactive_listbox.size()
        self.inactive_count_var.set(f"عدد الحسابات غير النشطة: {count}")
    
    def add_accounts(self):
        """إضافة حسابات من ملف"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف الحسابات",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    accounts_content = f.read()
                
                # إضافة المحتوى إلى حقل النص
                current_content = self.accounts_text.get("1.0", tk.END).strip()
                if current_content:
                    accounts_content = current_content + "\n" + accounts_content
                
                self.accounts_text.delete("1.0", tk.END)
                self.accounts_text.insert("1.0", accounts_content)
                
                # تحديث العداد
                self.update_accounts_count()
                
                messagebox.showinfo("نجاح", "تم إضافة الحسابات بنجاح")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في قراءة الملف: {str(e)}")
    
    def clear_accounts(self):
        """مسح جميع الحسابات من الحقل"""
        if messagebox.askyesno("تأكيد", "هل تريد مسح جميع الحسابات؟"):
            self.accounts_text.delete("1.0", tk.END)
            self.update_accounts_count()
    
    def save_active_accounts(self):
        """حفظ الحسابات النشطة في ملف نصي"""
        if self.active_listbox.size() == 0:
            messagebox.showwarning("تحذير", "لا توجد حسابات نشطة للحفظ")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="حفظ الحسابات النشطة",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(self.active_listbox.size()):
                        f.write(self.active_listbox.get(i) + "\n")
                
                messagebox.showinfo("نجاح", f"تم حفظ {self.active_listbox.size()} حساب نشط في الملف")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في حفظ الملف: {str(e)}")
    
    def get_accounts(self):
        """استخراج الحسابات من حقل النص"""
        text = self.accounts_text.get("1.0", tk.END).strip()
        if not text:
            return []
        
        accounts = []
        for line in text.split('\n'):
            line = line.strip()
            if ':' in line:
                email, password = line.split(':', 1)
                accounts.append({'email': email.strip(), 'password': password.strip()})
        
        return accounts
    
    def update_settings(self):
        """تحديث الإعدادات من الواجهة"""
        try:
            self.min_delay = max(1, int(self.min_delay_var.get()))
            self.max_delay = max(self.min_delay, int(self.max_delay_var.get()))
            self.concurrent_browsers = max(1, min(10, int(self.concurrent_var.get())))
            self.target_url = self.target_url_var.get().strip()
            if not self.target_url:
                messagebox.showerror("خطأ", "يجب إدخال عنوان URL الهدف")
                return False
        except ValueError:
            messagebox.showerror("خطأ", "قيم التأخير وعدد المتصفحات يجب أن تكون أرقامًا صحيحة")
            return False
        return True
    
    def start_process(self):
        """بدء عملية معالجة الحسابات"""
        if not self.update_settings():
            return
        
        accounts = self.get_accounts()
        if not accounts:
            messagebox.showwarning("تحذير", "لم تدخل أي حسابات")
            return
        
        # تفريغ القوائم
        self.active_listbox.delete(0, tk.END)
        self.inactive_listbox.delete(0, tk.END)
        
        # تحديث العدادات
        self.update_active_count()
        self.update_inactive_count()
        
        # تحديث حالة الأزرار
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.status_var.set("جاري المعالجة...")
        
        # بدء العملية في thread منفصل
        self.is_running = True
        self.is_paused = False
        self.current_thread = threading.Thread(target=self.process_accounts, args=(accounts,))
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def pause_process(self):
        """إيقاف مؤقت للعملية"""
        self.is_paused = True
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")
        self.status_var.set("متوقف مؤقتاً")
    
    def resume_process(self):
        """استئناف العملية"""
        self.is_paused = False
        self.resume_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.status_var.set("جاري المعالجة...")
    
    def stop_process(self):
        """إيقاف العملية"""
        self.is_running = False
        self.is_paused = False
        
        # تحديث حالة الأزرار
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.status_var.set("متوقف")
    
    def process_accounts(self, accounts):
        """معالجة الحسابات باستخدام متصفحات متعددة في نفس الوقت"""
        # تقسيم الحسابات إلى مجموعات حسب عدد المتصفحات المتزامنة
        account_groups = [accounts[i:i + self.concurrent_browsers] 
                         for i in range(0, len(accounts), self.concurrent_browsers)]
        
        for group_index, account_group in enumerate(account_groups):
            if not self.is_running:
                break
            
            # الانتظار إذا كانت العملية موقفة مؤقتًا
            while self.is_paused and self.is_running:
                time.sleep(0.5)
            
            if not self.is_running:
                break
            
            # تحديث حالة المجموعة الحالية
            self.root.after(0, lambda: self.status_var.set(
                f"جاري معالجة المجموعة {group_index + 1} من {len(account_groups)}"
            ))
            
            # معالجة المجموعة الحالية من الحسابات في نفس الوقت
            with ThreadPoolExecutor(max_workers=self.concurrent_browsers) as executor:
                # بدء معالجة جميع الحسابات في المجموعة الحالية
                future_to_account = {
                    executor.submit(self.process_account, account): account 
                    for account in account_group
                }
                
                # جمع النتائج
                for future in as_completed(future_to_account):
                    account = future_to_account[future]
                    try:
                        success = future.result()
                        # تحديث الواجهة
                        self.root.after(0, self.update_account_list, account, success)
                    except Exception as e:
                        print(f"خطأ في معالجة الحساب {account['email']}: {str(e)}")
                        self.root.after(0, self.update_account_list, account, False)
            
            # تأخير عشوائي بين المجموعات
            if group_index < len(account_groups) - 1:  # لا تأخير بعد المجموعة الأخيرة
                delay = self.get_random_delay()
                time.sleep(delay)
        
        # إعادة تعيين حالة البرنامج بعد الانتهاء
        self.root.after(0, self.reset_ui)
    
    def get_random_delay(self):
        """الحصول على وقت تأخير عشوائي"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def process_account(self, account):
        """معالجة حساب فردي"""
        driver = None
        try:
            # إعداد متصفح Chrome
            chrome_options = Options()
            
            # إضافة خيارات لتحسين الاستقرار
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # التحكم في وضع العرض (خفي أو عادي)
            if self.headless_var.get():
                chrome_options.add_argument("--headless=new")  # استخدام الوضع الجديد للheadless
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            
            # استخدام منافذ مختلفة لكل متصفح لتجنب التعارض
            chrome_options.add_argument("--remote-debugging-port=0")
            
            # استخدام webdriver_manager لتثبيت وتحديد المسار التلقائي لـ ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # إخفاء علامات automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            driver.implicitly_wait(10)
            
            # الانتقال إلى الصفحة الهدف
            driver.get(self.target_url)
            time.sleep(3)  # انتظار تحميل الصفحة
            
            # محاولة العثور على حقول تسجيل الدخول بطرق مختلفة
            email_field = None
            password_field = None
            
            # البحث عن الحقول بطرق مختلفة
            selectors = [
                ("input[type='email']", By.CSS_SELECTOR),
                ("input[type='text'][name*='mail']", By.CSS_SELECTOR),
                ("#email", By.CSS_SELECTOR),
                ("input[name='email']", By.CSS_SELECTOR),
                ("//input[contains(@id, 'email') or contains(@name, 'email')]", By.XPATH)
            ]
            
            for selector, by_method in selectors:
                try:
                    email_field = driver.find_element(by_method, selector)
                    if email_field:
                        break
                except:
                    continue
            
            # إذا لم نجد حقل البريد، نعتبر أن الصفحة لا تحتوي على نموذج تسجيل دخول
            if not email_field:
                print(f"لم يتم العثور على حقل البريد الإلكتروني في {self.target_url}")
                return False
            
            # البحث عن حقل كلمة المرور
            password_selectors = [
                ("input[type='password']", By.CSS_SELECTOR),
                ("#pass", By.CSS_SELECTOR),
                ("#password", By.CSS_SELECTOR),
                ("input[name='pass']", By.CSS_SELECTOR),
                ("input[name='password']", By.CSS_SELECTOR),
                ("//input[contains(@id, 'pass') or contains(@name, 'pass')]", By.XPATH)
            ]
            
            for selector, by_method in password_selectors:
                try:
                    password_field = driver.find_element(by_method, selector)
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print(f"لم يتم العثور على حقل كلمة المرور في {self.target_url}")
                return False
            
            # ملء بيانات تسجيل الدخول
            email_field.clear()
            email_field.send_keys(account['email'])
            
            password_field.clear()
            password_field.send_keys(account['password'])
            
            # البحث عن زر تسجيل الدخول
            login_selectors = [
                ("button[type='submit']", By.CSS_SELECTOR),
                ("input[type='submit']", By.CSS_SELECTOR),
                ("#loginbutton", By.CSS_SELECTOR),
                ("button[name='login']", By.CSS_SELECTOR),
                ("//button[contains(text(), 'Login') or contains(text(), 'Log In') or contains(text(), 'تسجيل')]", By.XPATH)
            ]
            
            login_button = None
            for selector, by_method in login_selectors:
                try:
                    login_button = driver.find_element(by_method, selector)
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                login_button.click()
            else:
                # إذا لم نجد زرًا، نضغط Enter في حقل كلمة المرور
                password_field.send_keys(Keys.RETURN)
            
            # الانتظار لمدة 30 ثانية لإتمام المصادقة الثنائية إذا كانت مطلوبة
            time.sleep(30)
            
            # التحقق من نجاح تسجيل الدخول
            # ننتظر تغيير الصفحة أو ظهور عناصر تدل على نجاح التسجيل
            time.sleep(5)
            
            # طرق مختلفة للتحقق من نجاح تسجيل الدخول
            success_indicators = [
                (By.ID, "logoutForm"),  # نموذج تسجيل الخروج
                (By.XPATH, "//a[contains(@href, 'logout') or contains(@href, 'logoff')]"),  # رابط تسجيل الخروج
                (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'مرحبا')]"),  # رسالة ترحيب
                (By.XPATH, "//*[contains(text(), 'My Account') or contains(text(), 'حسابي')]"),  # حسابي
            ]
            
            login_success = False
            for by, value in success_indicators:
                try:
                    element = driver.find_element(by, value)
                    if element:
                        login_success = True
                        break
                except:
                    continue
            
            # إذا لم نجد أي من مؤشرات النجاح، نتحقق من عنوان URL
            if not login_success:
                current_url = driver.current_url
                # إذا كان عنوان URL مختلف عن صفحة التسجيل، قد يكون التسجيل ناجحًا
                if "login" not in current_url.lower() and "signin" not in current_url.lower():
                    login_success = True
            
            if login_success:
                # حفظ الكوكيز
                cookies = driver.get_cookies()
                self.save_cookies(account['email'], cookies)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"خطأ في معالجة الحساب {account['email']}: {str(e)}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_cookies(self, email, cookies):
        """حفظ الكوكيز في ملف"""
        try:
            # تنظيف اسم الملف من الأحرف غير المسموح بها
            safe_email = "".join(c for c in email if c.isalnum() or c in ('@', '.', '_', '-')).rstrip()
            cookie_file = os.path.join(self.cookies_dir, f"{safe_email}_cookies.json")
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"تم حفظ كوكيز للحساب: {email}")
        except Exception as e:
            print(f"خطأ في حفظ الكوكيز للحساب {email}: {str(e)}")
    
    def update_account_list(self, account, success):
        """تحديث قائمة الحسابات في الواجهة"""
        account_str = f"{account['email']}:{account['password']}"
        
        if success:
            self.active_listbox.insert(tk.END, account_str)
            self.update_active_count()
            print(f"تمت معالجة الحساب بنجاح: {account['email']}")
        else:
            self.inactive_listbox.insert(tk.END, account_str)
            self.update_inactive_count()
            print(f"فشلت معالجة الحساب: {account['email']}")
    
    def reset_ui(self):
        """إعادة تعيين واجهة المستخدم بعد انتهاء العملية"""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.status_var.set("تم الانتهاء من المعالجة")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManager(root)
    root.mainloop()
