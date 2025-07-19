from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ابزار تولید فایل‌های تبلیغاتی")
        self.root.geometry("1000x700")
        
        # متغیرهای ذخیره‌سازی محصولات
        self.products = []
        self.current_product_index = None
        
        # ایجاد نوار ابزار
        self.create_navbar()
        
        # ایجاد نوت‌بوک (تب‌ها)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تب وارد کردن ابجکت
        self.create_enter_tab()
        
        # تب ساخت ابجکت
        self.create_build_tab()
        
        # تب نمایش کد تولید شده
        self.create_code_tab()
        
        # مخفی کردن تب‌های غیرفعال
        self.notebook.hide(2)
        
        # تنظیم تم
        style = ttk.Style()
        style.configure('TButton', font=('Tahoma', 10))
        style.configure('TFrame', background='#f0f0f0')
        style.map('Nav.TButton', 
                 background=[('active', '#4CAF50'), ('pressed', '#45a049')],
                 foreground=[('active', 'white')])

    def create_navbar(self):
        """ایجاد نوار ابزار با دو دکمه اصلی"""
        navbar = ttk.Frame(self.root, height=50)
        navbar.pack(fill='x', padx=10, pady=10)
        
        # دکمه وارد کردن ابجکت
        self.btn_enter = ttk.Button(
            navbar, 
            text="وارد کردن ابجکت محصولات", 
            command=self.show_enter_tab,
            style='Nav.TButton',
            width=25
        )
        self.btn_enter.pack(side='right', padx=5)
        
        # دکمه ساخت ابجکت
        self.btn_build = ttk.Button(
            navbar, 
            text="ساخت ابجکت جدید", 
            command=self.show_build_tab,
            style='Nav.TButton',
            width=25
        )
        self.btn_build.pack(side='right', padx=5)
        
        # برچسب عنوان
        lbl_title = tk.Label(
            navbar, 
            text="فوتوپیا اتوماسیون - مدیریت محصولات", 
            font=('Tahoma', 14, 'bold'),
            fg='#2c3e50'
        )
        lbl_title.pack(side='left', padx=10)

    def create_enter_tab(self):
        """تب وارد کردن مستقیم کد محصولات"""
        tab_enter = ttk.Frame(self.notebook)
        self.notebook.add(tab_enter, text="وارد کردن ابجکت")
        
        # بخش ورودی
        frame_input = ttk.LabelFrame(tab_enter, text="ورود دستی آبجکت محصولات")
        frame_input.pack(fill='both', expand=True, padx=10, pady=10)
        
        lbl_instruction = tk.Label(
            frame_input,
            text="""👇 کد آبجکت محصولات را در کادر زیر پیست کنید (فرمت استاندارد جاوااسکریپت)

نکته: کد باید حاوی آرایه‌ای از 12 شیء محصول با ساختار زیر باشد:
{
    name: "نام محصول",
    measure: "اندازه",
    price: قیمت,
    oldPrice: قیمت قبلی
}""",
            font=('Tahoma', 10),
            justify='right',
            anchor='w'
        )
        lbl_instruction.pack(fill='x', padx=10, pady=5)
        
        # کادر متن برای ورود کد
        self.txt_products = scrolledtext.ScrolledText(
            frame_input, 
            height=15,
            font=('Courier New', 10),
            wrap=tk.NONE
        )
        self.txt_products.pack(fill='both', expand=True, padx=10, pady=5)
        
        # دکمه شروع
        btn_start = ttk.Button(
            frame_input,
            text="شروع پردازش با این محصولات",
            command=self.start_with_entered_code,
            width=30
        )
        btn_start.pack(pady=10)
        
        # مثال پیشفرض
        example_code = """[
    { name: "Vaseline Lip Therapy", measure: "20g", price: 2.47, oldPrice: 2.97 },
    { name: "Tide Pods Detergent", measure: "1.8kg", price: 12.99, oldPrice: 14.99 },
    { name: "Tide Liquid 48 Loads", measure: "1.86L", price: 14.97, oldPrice: 16.97 },
    { name: "Tide Unscented", measure: "3.9L", price: 28.97, oldPrice: 32.97 },
    { name: "Bounce Dryer Sheets", measure: "200ct", price: 5.99, oldPrice: 6.99 },
    { name: "Mr Clean Citrus", measure: "3.78L", price: 8.97, oldPrice: 10.97 },
    { name: "Cascade Dishwasher Pods", measure: "790g", price: 24.97, oldPrice: 27.97 },
    { name: "Dawn Dish Liquid", measure: "535ml", price: 3.47, oldPrice: 4.47 },
    { name: "Palmolive Hand Wash", measure: "300ml", price: 0.97, oldPrice: 1.97 },
    { name: "Sinutab Day Night", measure: "24 Caplets", price: 14.97, oldPrice: 15.97 },
    { name: "Loratadine 24Hr", measure: "10mg 24Tb", price: 11.97, oldPrice: 13.97 },
    { name: "Robitussin Night Syrup", measure: "230ml", price: 10.97, oldPrice: 12.97 }
]"""
        self.txt_products.insert('1.0', example_code)

    def create_build_tab(self):
        """تب ساخت ابجکت محصولات با فرم ورودی"""
        tab_build = ttk.Frame(self.notebook)
        self.notebook.add(tab_build, text="ساخت ابجکت")
        
        # قاب اصلی با اسکرول بار
        main_frame = ttk.Frame(tab_build)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # کانواس و اسکرول بار
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # راه‌حل جایگزین با تابع جداگانه
        def configure_scrollregion(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", configure_scrollregion)
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # عنوان بخش
        lbl_title = tk.Label(
            self.scrollable_frame,
            text="اطلاعات 12 محصول را وارد کنید:",
            font=('Tahoma', 12, 'bold'),
            fg='#2c3e50'
        )
        lbl_title.grid(row=0, column=0, columnspan=5, pady=10, sticky='w')
        
        # هدر جدول
        headers = ["#", "نام محصول", "قیمت فعلی", "قیمت قبلی", "واحد اندازه‌گیری", "عملیات"]
        for col, header in enumerate(headers):
            lbl = tk.Label(
                self.scrollable_frame, 
                text=header, 
                font=('Tahoma', 10, 'bold'),
                bg='#e0e0e0',
                padx=10,
                pady=5
            )
            lbl.grid(row=1, column=col, padx=5, pady=2, sticky='ew')
        
        # ایجاد فرم ورودی برای 12 محصول
        self.product_entries = []
        for i in range(12):
            frame = ttk.Frame(self.scrollable_frame)
            frame.grid(row=i+2, column=0, columnspan=5, padx=5, pady=5, sticky='ew')
            
            # شماره محصول
            lbl_num = tk.Label(frame, text=f"{i+1}", width=3, font=('Tahoma', 10))
            lbl_num.grid(row=0, column=0, padx=5)
            
            # ورودی‌ها
            name_var = tk.StringVar()
            price_var = tk.StringVar()
            old_price_var = tk.StringVar()
            measure_var = tk.StringVar()
            
            entry_name = ttk.Entry(frame, textvariable=name_var, width=25)
            entry_price = ttk.Entry(frame, textvariable=price_var, width=10)
            entry_old_price = ttk.Entry(frame, textvariable=old_price_var, width=10)
            entry_measure = ttk.Entry(frame, textvariable=measure_var, width=15)
            
            entry_name.grid(row=0, column=1, padx=5)
            entry_price.grid(row=0, column=2, padx=5)
            entry_old_price.grid(row=0, column=3, padx=5)
            entry_measure.grid(row=0, column=4, padx=5)
            
            # دکمه‌های عملیات
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=0, column=5, padx=5)
            
            btn_edit = ttk.Button(
                btn_frame, 
                text="ویرایش", 
                width=6,
                command=lambda idx=i: self.edit_product(idx)
            )
            btn_edit.pack(side='left', padx=2)
            
            btn_delete = ttk.Button(
                btn_frame, 
                text="حذف", 
                width=6,
                command=lambda idx=i: self.delete_product(idx)
            )
            btn_delete.pack(side='left', padx=2)
            
            # ذخیره متغیرها
            self.product_entries.append({
                'name': name_var,
                'price': price_var,
                'old_price': old_price_var,
                'measure': measure_var,
                'frame': frame
            })
        
        # دکمه‌های پایانی
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=14, column=0, columnspan=5, pady=20)
        
        btn_generate = ttk.Button(
            btn_frame, 
            text="تولید کد ابجکت", 
            command=self.generate_js_code,
            width=20
        )
        btn_generate.pack(side='right', padx=10)
        
        btn_clear = ttk.Button(
            btn_frame, 
            text="پاک کردن همه", 
            command=self.clear_all_products,
            width=20
        )
        btn_clear.pack(side='right', padx=10)

    def create_code_tab(self):
        """تب نمایش کد تولید شده"""
        tab_code = ttk.Frame(self.notebook)
        self.notebook.add(tab_code, text="کد تولید شده")
        
        # قاب نمایش کد
        frame_code = ttk.LabelFrame(tab_code, text="کد آبجکت تولید شده")
        frame_code.pack(fill='both', expand=True, padx=10, pady=10)
        
        # کادر متن برای نمایش کد
        self.txt_js_code = scrolledtext.ScrolledText(
            frame_code, 
            height=15,
            font=('Courier New', 10),
            wrap=tk.NONE
        )
        self.txt_js_code.pack(fill='both', expand=True, padx=10, pady=5)
        self.txt_js_code.config(state='disabled')  # غیرفعال برای ویرایش
        
        # دکمه‌های پایین
        btn_frame = ttk.Frame(frame_code)
        btn_frame.pack(pady=10)
        
        btn_copy = ttk.Button(
            btn_frame, 
            text="کپی کد", 
            command=self.copy_js_code,
            width=15
        )
        btn_copy.pack(side='right', padx=10)
        
        btn_run = ttk.Button(
            btn_frame, 
            text="اجرای اتوماسیون", 
            command=self.run_with_generated_code,
            width=15
        )
        btn_run.pack(side='right', padx=10)
        
        btn_back = ttk.Button(
            btn_frame, 
            text="بازگشت به ویرایش", 
            command=self.show_build_tab,
            width=15
        )
        btn_back.pack(side='right', padx=10)

    def show_enter_tab(self):
        """نمایش تب وارد کردن ابجکت"""
        self.notebook.select(0)
        self.btn_enter.state(['pressed'])
        self.btn_build.state(['!pressed'])

    def show_build_tab(self):
        """نمایش تب ساخت ابجکت"""
        self.notebook.select(1)
        self.btn_build.state(['pressed'])
        self.btn_enter.state(['!pressed'])
        self.notebook.hide(2)

    def show_code_tab(self):
        """نمایش تب کد تولید شده"""
        self.notebook.select(2)
        self.notebook.add(self.notebook.children['!frame3'], text="کد تولید شده")

    def edit_product(self, index):
        """ویرایش محصول (در این نسخه ساده، فقط فوکوس می‌دهد)"""
        entries = self.product_entries[index]
        entries['name'].set(entries['name'].get())  # فقط برای مثال
        messagebox.showinfo("ویرایش", f"محصول شماره {index+1} برای ویرایش آماده است.")

    def delete_product(self, index):
        """حذف محصول"""
        if messagebox.askyesno("حذف محصول", f"آیا از حذف محصول شماره {index+1} مطمئنید؟"):
            # پاک کردن مقادیر
            self.product_entries[index]['name'].set('')
            self.product_entries[index]['price'].set('')
            self.product_entries[index]['old_price'].set('')
            self.product_entries[index]['measure'].set('')
            messagebox.showinfo("حذف شد", f"محصول شماره {index+1} حذف شد.")

    def clear_all_products(self):
        """پاک کردن همه محصولات"""
        if messagebox.askyesno("پاک کردن همه", "آیا از پاک کردن همه محصولات مطمئنید؟"):
            for i in range(12):
                self.product_entries[i]['name'].set('')
                self.product_entries[i]['price'].set('')
                self.product_entries[i]['old_price'].set('')
                self.product_entries[i]['measure'].set('')
            messagebox.showinfo("پاکسازی", "همه محصولات پاک شدند.")

    def generate_js_code(self):
        """تولید کد جاوااسکریپت از محصولات وارد شده"""
        products = []
        has_error = False
        
        for i in range(12):
            name = self.product_entries[i]['name'].get().strip()
            measure = self.product_entries[i]['measure'].get().strip()
            price = self.product_entries[i]['price'].get().strip()
            old_price = self.product_entries[i]['old_price'].get().strip()
            
            # اعتبارسنجی ورودی‌ها
            if not name or not measure or not price or not old_price:
                messagebox.showerror(
                    "خطا", 
                    f"لطفاً همه فیلدهای محصول شماره {i+1} را پر کنید."
                )
                has_error = True
                break
                
            try:
                price_val = float(price)
                old_price_val = float(old_price)
            except ValueError:
                messagebox.showerror(
                    "خطا", 
                    f"مقادیر قیمت در محصول شماره {i+1} باید عددی باشند."
                )
                has_error = True
                break
                
            products.append({
                'name': name,
                'measure': measure,
                'price': price_val,
                'oldPrice': old_price_val
            })
        
        if not has_error:
            # تولید کد جاوااسکریپت
            js_code = "var products = [\n"
            for i, p in enumerate(products):
                # استفاده از نقل‌قول‌های متناوب برای رفع مشکل
                js_code += f'    {{ name: "{p["name"]}", measure: "{p["measure"]}", price: {p["price"]}, oldPrice: {p["oldPrice"]} }}'
                if i < 11:
                    js_code += ",\n"
                else:
                    js_code += "\n];"
            
            # نمایش کد در تب مربوطه
            self.txt_js_code.config(state='normal')
            self.txt_js_code.delete('1.0', tk.END)
            self.txt_js_code.insert('1.0', js_code)
            self.txt_js_code.config(state='disabled')
            
            # ذخیره محصولات برای استفاده بعدی
            self.products = products
            
            # نمایش تب کد تولید شده
            self.show_code_tab()

    def copy_js_code(self):
        """کپی کد به کلیپ‌بورد"""
        code = self.txt_js_code.get('1.0', tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("کپی شد", "کد با موفقیت در کلیپ‌بورد کپی شد.")

    def start_with_entered_code(self):
        """شروع پردازش با کد وارد شده"""
        code = self.txt_products.get('1.0', tk.END).strip()
        if not code:
            messagebox.showerror("خطا", "لطفاً کد محصولات را وارد کنید.")
            return
        
        # ذخیره کد برای استفاده بعدی
        self.products_code = code
        
        # بستن پنجره و شروع اتوماسیون
        self.root.destroy()
        run_browser(code)

    def run_with_generated_code(self):
        """اجرای اتوماسیون با کد تولید شده"""
        if not self.products:
            messagebox.showerror("خطا", "هیچ محصولی ایجاد نشده است.")
            return
        
        # بستن پنجره و شروع اتوماسیون
        self.root.destroy()
        
        # تولید کد از محصولات
        js_code = "[\n"
        for i, p in enumerate(self.products):
            # استفاده از نقل‌قول‌های متناوب برای رفع مشکل
            js_code += f'    {{ name: "{p["name"]}", measure: "{p["measure"]}", price: {p["price"]}, oldPrice: {p["oldPrice"]} }}'
            if i < 11:
                js_code += ",\n"
            else:
                js_code += "\n]"
        
        run_browser(js_code)


def run_browser(products_object_code):
    """تابع اجرای اتوماسیون مرورگر"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 60)

    try:
        driver.get('https://www.photopea.com/api/playground')
        time.sleep(10)

        textarea = wait.until(EC.presence_of_element_located((By.ID, 'script')))
        textarea.clear()
        
        # ساخت اسکریپت نهایی با استفاده از کد محصولات
        script_content = f"""
{products_object_code}

for (var i = 0; i < products.length; i++) {{
    var idx = i + 1;
    var p = products[i];
    var priceParts = p.price.toFixed(2).split('.');

    app.activeDocument.layers.getByName('nameUnit' + idx).textItem.contents = p.name + "\\n" + p.measure;
    app.activeDocument.layers.getByName('price' + idx).textItem.contents = priceParts[0];
    app.activeDocument.layers.getByName('pointPrice' + idx).textItem.contents = priceParts[1];
    app.activeDocument.layers.getByName('oldPrice' + idx).textItem.contents = "Was\\n" + "$" + p.oldPrice.toFixed(2);
}}
        """
        textarea.send_keys(script_content)

        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)

        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        PSD_PATH = os.path.abspath("Flyer.psd")
        file_input.send_keys(PSD_PATH)

        driver.switch_to.default_content()

        buttons = driver.find_elements(By.CLASS_NAME, 'btn')
        run_button = None
        for btn in buttons:
            if 'Run' in btn.text:
                run_button = btn
                break

        if run_button:
            run_button.click()
            print("✅ دکمه Run کلیک شد.")
        else:
            driver.execute_script("alert('❌ دکمه Run پیدا نشد. خودت بزن.')")
            print("❌ دکمه Run پیدا نشد.")

    except Exception as e:
        print("ارور:", e)
        driver.execute_script("alert('خطا در اجرا! خودت بررسی کن.')")
    finally:
        input("✅ برای بستن مرورگر Enter بزن...") 
        driver.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()