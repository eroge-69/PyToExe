import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import datetime
import configparser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import shutil
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import bcrypt
import csv

# إعدادات الملفات
CONFIG_FILE = "config.ini"
PRODUCTS_FILE = "products.json"
INVOICE_DIR = "invoices"
LOGO_FILE = "logo.png"
ICON_FILE = "logo.ico"
DEBTS_FILE = os.path.join(INVOICE_DIR, "debts.xlsx")
DEBT_PAYMENTS_FILE = os.path.join(INVOICE_DIR, "debt_payments.xlsx")
os.environ["LANG"] = "en_US.UTF-8"

# إنشاء المجلدات والملفات إذا لم تكن موجودة
os.makedirs(INVOICE_DIR, exist_ok=True)

# إعدادات التصميم
BG_COLOR = "#2c3e50"
SIDEBAR_COLOR = "#34495e"
BUTTON_COLOR = "#3498db"
BUTTON_HOVER = "#2980b9"
BUTTON_ACTIVE = "#1c6ca8"
TEXT_COLOR = "#ecf0f1"
ENTRY_COLOR = "#bdc3c7"
FONT = ("Arial", 12)
LARGE_FONT = ("Arial", 16)
TITLE_FONT = ("Arial", 24, "bold")

class Application:
    def __init__(self):
        self.setup_files()
        self.config = self.load_config()
        self.run_login()

    def setup_files(self):
        """إنشاء الملفات الأساسية إذا لم تكن موجودة"""
        if not os.path.exists(CONFIG_FILE):
            config = configparser.ConfigParser()
            config['DEFAULT'] = {
                'company_name': 'متجرنا',
                'default_currency': 'EGP',
                'tax_rate': '0.14'
            }
            config['AUTH'] = {
                'admin_hash': bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8'),
                'cashier_hash': bcrypt.hashpw(b'cashier123', bcrypt.gensalt()).decode('utf-8')
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                config.write(f)

        if not os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        if not os.path.exists(DEBTS_FILE):
            pd.DataFrame(columns=[
                "رقم الفاتورة", "التاريخ", "اسم العميل", 
                "المبلغ", "المبلغ المتبقي", "حالة السداد", "تاريخ السداد", "المنتجات"
            ]).to_excel(DEBTS_FILE, index=False)

        if not os.path.exists(DEBT_PAYMENTS_FILE):
            pd.DataFrame(columns=[
                "رقم الفاتورة", "التاريخ", "اسم العميل",
                "المبلغ المسدد", "المبلغ المتبقي", "طريقة السداد"
            ]).to_excel(DEBT_PAYMENTS_FILE, index=False)

        if not os.path.exists(os.path.join(INVOICE_DIR, "invoices.xlsx")):
            pd.DataFrame(columns=[
                "رقم الفاتورة", "التاريخ", "اسم العميل", 
                "الإجمالي", "مسار الصورة", "المنتجات", "نوع الفاتورة"
            ]).to_excel(os.path.join(INVOICE_DIR, "invoices.xlsx"), index=False)

    def load_config(self):
        """تحميل إعدادات التطبيق"""
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config

    def run_login(self):
        """تشغيل نافذة تسجيل الدخول"""
        LoginWindow(self)

def arabic_text(text):
    """تصحيح النصوص العربية لعرضها بشكل صحيح"""
    try:
        reshaped_text = reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

def load_products():
    """تحميل قائمة المنتجات"""
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
            for p in products:
                if isinstance(p.get('price', 0), str):
                    p['price'] = float(p['price'])
                if isinstance(p.get('quantity', 0), str):
                    p['quantity'] = int(p['quantity'])
            return products
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_products(products):
    """حفظ قائمة المنتجات"""
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

def search_products(search_term):
    """بحث في المنتجات"""
    products = load_products()
    return [p for p in products if search_term.lower() in p["name"].lower() or 
            search_term.lower() in p.get("code", "").lower()]

def update_product_quantity(product_name, sold_quantity):
    """تحديث كمية المنتج بعد البيع"""
    products = load_products()
    for product in products:
        if product['name'] == product_name:
            if product['quantity'] >= sold_quantity:
                product['quantity'] -= sold_quantity
                save_products(products)
                return True
            else:
                return False
    return False

def save_invoice_to_image(invoice_items, company_name, customer_name, total, invoice_type="بيع"):
    """حفظ الفاتورة كصورة"""
    try:
        img_width = 1000
        item_height = 50
        header_height = 200
        footer_height = 150
        img_height = header_height + len(invoice_items)*item_height + footer_height
        
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img, 'RGB')
        
        try:
            if os.path.exists(LOGO_FILE):
                logo = Image.open(LOGO_FILE)
                logo.thumbnail((150, 150))
                img.paste(logo, (img_width-200, 40))
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_medium = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # عنوان الفاتورة
        draw.text((img_width//2-150, 50), arabic_text(company_name), fill="black", font=font_large)
        draw.text((img_width//2-100, 100), arabic_text(f"فاتورة {invoice_type}"), fill="black", font=font_medium)
        
        # معلومات الفاتورة
        draw.text((100, 150), arabic_text(f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"), 
                fill="black", font=font_small)
        draw.text((img_width-300, 150), arabic_text(f"العميل: {customer_name}"), 
                fill="black", font=font_small)
        
        # تفاصيل الفاتورة
        y_position = header_height
        draw.line((50, y_position-10, img_width-50, y_position-10), fill="black", width=3)
        
        # عناوين الأعمدة
        draw.text((150, y_position), arabic_text("المنتج"), fill="black", font=font_small)
        draw.text((400, y_position), arabic_text("السعر"), fill="black", font=font_small)
        draw.text((550, y_position), arabic_text("الكمية"), fill="black", font=font_small)
        draw.text((700, y_position), arabic_text("الإجمالي"), fill="black", font=font_small)
        
        y_position += 40
        draw.line((50, y_position, img_width-50, y_position), fill="black", width=2)
        
        # عناصر الفاتورة
        for item in invoice_items:
            y_position += item_height
            draw.text((150, y_position), arabic_text(item[0]), fill="black", font=font_small)
            
            try:
                price = float(item[1])
                draw.text((400, y_position), f"{price:.2f}", fill="black", font=font_small)
            except ValueError:
                draw.text((400, y_position), item[1], fill="black", font=font_small)
            
            draw.text((550, y_position), str(item[2]), fill="black", font=font_small)
            
            try:
                item_total = float(item[3])
                draw.text((700, y_position), f"{item_total:.2f}", fill="black", font=font_small)
            except ValueError:
                draw.text((700, y_position), item[3], fill="black", font=font_small)
        
        # المجموع
        y_position += item_height + 40
        draw.line((50, y_position, img_width-50, y_position), fill="black", width=3)
        draw.text((img_width-200, y_position+50), 
                arabic_text(f"المجموع: {float(total):.2f} {arabic_text('جنيه')}"), 
                fill="black", font=font_medium)
        
        # ختم الفاتورة
        draw.text((img_width//2-100, y_position+100), 
                arabic_text("شكراً لتعاملكم معنا"), 
                fill="black", font=font_small)
        
        return img
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء الفاتورة: {str(e)}")
        return None

class StyledButton(tk.Button):
    """زر مخصص بتصميم حديث وتأثيرات"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = self.cget("background")
        self.configure(
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5,
            font=FONT,
            highlightthickness=0,
            cursor="hand2"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_enter(self, e):
        self.configure(background=BUTTON_HOVER)
    
    def on_leave(self, e):
        self.configure(background=self.default_bg)
    
    def on_press(self, e):
        self.configure(relief=tk.SUNKEN, background=BUTTON_ACTIVE)
    
    def on_release(self, e):
        self.configure(relief=tk.RAISED, background=self.default_bg)

class LoginWindow:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.style = ttk.Style()
        self.root.style.theme_use("clam")
        self.root.iconbitmap(None)
        self.root.title("تسجيل الدخول")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_COLOR)
        
        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        # إضافة صورة خلفية
        try:
            bg_image = Image.open("login_bg.png") if os.path.exists("login_bg.png") else None
            if bg_image:
                bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                bg_label = tk.Label(self.root, image=self.bg_photo)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
        
        self.setup_ui()
        self.root.mainloop()
    
    def setup_ui(self):
        # إطار تسجيل الدخول
        login_frame = tk.Frame(self.root, bg=BG_COLOR, bd=5, relief=tk.RAISED)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # عنوان النظام
        title_label = tk.Label(login_frame, text=arabic_text("لوحة تسجيل الدخول"), 
                             font=("Arial", 28, "bold"), bg=BG_COLOR, fg="#f1c40f")
        title_label.pack(pady=(20, 40))
        
        # إطار حقول الإدخال
        input_frame = tk.Frame(login_frame, bg=BG_COLOR)
        input_frame.pack(pady=10, padx=20)
        
        # نوع المستخدم
        tk.Label(input_frame, text=arabic_text("نوع المستخدم:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=1, pady=5, sticky="e")
        
        self.user_type = ttk.Combobox(input_frame, values=[arabic_text("مدير"), arabic_text("كاشير")], 
                                    state="readonly", font=FONT, width=25)
        self.user_type.grid(row=0, column=0, pady=5, padx=10)
        
        # كلمة المرور
        tk.Label(input_frame, text=arabic_text("كلمة المرور:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=1, pady=5, sticky="e")
        
        self.entry_pass = tk.Entry(input_frame, show="*", font=FONT, bg=ENTRY_COLOR, width=27)
        self.entry_pass.grid(row=1, column=0, pady=5, padx=10)
        
        # إظهار/إخفاء كلمة المرور
        self.show_pass_var = tk.BooleanVar(value=False)
        show_pass_btn = tk.Checkbutton(input_frame, text=arabic_text("إظهار كلمة المرور"), 
                                     variable=self.show_pass_var, command=self.toggle_password,
                                     bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, selectcolor=BG_COLOR)
        show_pass_btn.grid(row=2, column=1, pady=5, sticky="w")
        
        # أزرار التحكم
        btn_frame = tk.Frame(login_frame, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        btn_login = StyledButton(btn_frame, text=arabic_text("دخول"), command=self.check_login, 
                            bg="#27ae60", fg=TEXT_COLOR)
        btn_login.pack(side="right", padx=10)
        
        btn_change_pass = StyledButton(btn_frame, text=arabic_text("تغيير كلمة المرور"), 
                                  command=self.show_change_password, 
                                  bg="#3498db", fg=TEXT_COLOR)
        btn_change_pass.pack(side="right", padx=10)
        
        btn_exit = StyledButton(btn_frame, text=arabic_text("خروج"), command=self.root.destroy,
                           bg="#e74c3c", fg=TEXT_COLOR)
        btn_exit.pack(side="right", padx=10)
    
    def toggle_password(self):
        if self.show_pass_var.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="*")
    
    def check_login(self):
        user_type = self.user_type.get()
        password = self.entry_pass.get().encode('utf-8')
        
        if not user_type:
            messagebox.showerror("خطأ", "يجب اختيار نوع المستخدم")
            return
        
        if user_type == arabic_text("مدير"):
            stored_hash = self.app.config['AUTH'].get('admin_hash', '').encode('utf-8')
        else:
            stored_hash = self.app.config['AUTH'].get('cashier_hash', '').encode('utf-8')
        
        if bcrypt.checkpw(password, stored_hash):
            self.root.destroy()
            if user_type == arabic_text("مدير"):
                AdminPanel(self.app)
            else:
                CashierPanel(self.app)
        else:
            messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")
    
    def show_change_password(self):
        pass_window = tk.Toplevel(self.root)
        pass_window.title("تغيير كلمة المرور")
        pass_window.geometry("400x400")
        pass_window.configure(bg=BG_COLOR)
        
        tk.Label(pass_window, text=arabic_text("تغيير كلمة المرور"), font=TITLE_FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        tk.Label(pass_window, text=arabic_text("نوع المستخدم:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack()
        user_type = ttk.Combobox(pass_window, values=[arabic_text("مدير"), arabic_text("كاشير")], 
                                state="readonly", font=FONT)
        user_type.pack(pady=5)
        
        tk.Label(pass_window, text=arabic_text("كلمة المرور الحالية:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack()
        old_pass = tk.Entry(pass_window, show="*", font=FONT, bg=ENTRY_COLOR)
        old_pass.pack(pady=5)
        
        tk.Label(pass_window, text=arabic_text("كلمة المرور الجديدة:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack()
        new_pass = tk.Entry(pass_window, show="*", font=FONT, bg=ENTRY_COLOR)
        new_pass.pack(pady=5)
        
        tk.Label(pass_window, text=arabic_text("تأكيد كلمة المرور:"), font=FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack()
        confirm_pass = tk.Entry(pass_window, show="*", font=FONT, bg=ENTRY_COLOR)
        confirm_pass.pack(pady=5)
        
        def save_password():
            utype = user_type.get()
            opass = old_pass.get().encode('utf-8')
            npass = new_pass.get()
            cpass = confirm_pass.get()
            
            if not utype:
                messagebox.showerror("خطأ", "يجب اختيار نوع المستخدم")
                return
            
            if utype == arabic_text("مدير"):
                stored_hash = self.app.config['AUTH'].get('admin_hash', '').encode('utf-8')
            else:
                stored_hash = self.app.config['AUTH'].get('cashier_hash', '').encode('utf-8')
            
            if not bcrypt.checkpw(opass, stored_hash):
                messagebox.showerror("خطأ", "كلمة المرور الحالية غير صحيحة")
                return
            
            if npass != cpass:
                messagebox.showerror("خطأ", "كلمة المرور غير متطابقة")
                return
            
            if utype == arabic_text("مدير"):
                self.app.config.set('AUTH', 'admin_hash', bcrypt.hashpw(npass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
            else:
                self.app.config.set('AUTH', 'cashier_hash', bcrypt.hashpw(npass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
            
            with open(CONFIG_FILE, 'w') as configfile:
                self.app.config.write(configfile)
            
            messagebox.showinfo("تم", "تم تغيير كلمة المرور بنجاح")
            pass_window.destroy()
        
        save_btn = StyledButton(pass_window, text=arabic_text("حفظ"), command=save_password, 
                 bg=BUTTON_COLOR, fg=TEXT_COLOR)
        save_btn.pack(pady=20)

class AdminPanel:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.style = ttk.Style()
        self.root.style.theme_use("clam")
        self.root.iconbitmap(None)
        self.root.title("لوحة التحكم - المدير")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_COLOR)
        self.fullscreen_state = True
        
        self.setup_ui()
        self.root.mainloop()
    
    def toggle_fullscreen(self):
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes('-fullscreen', self.fullscreen_state)
    
    def setup_ui(self):
        # إنشاء الشريط الجانبي
        sidebar = tk.Frame(self.root, bg=SIDEBAR_COLOR, width=250)
        sidebar.pack(side="right", fill="y")
        
        # عنوان اللوحة
        title_frame = tk.Frame(sidebar, bg="#2c3e50", height=80)
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text=arabic_text("لوحة المدير"), font=("Arial", 18, "bold"), 
                bg="#2c3e50", fg="#f1c40f").pack(pady=20)
        
                # إضافة هذه السطور لتعيين الأيقونة
        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        # أزرار القائمة
        buttons = [
            ("الرئيسية", self.show_dashboard),
            ("إدارة المنتجات", self.show_products_management),
            ("إدارة الفواتير", self.show_invoices_management),
            ("إدارة الديون", self.show_debts_management),
            ("تقارير المبيعات", self.show_sales_reports),
            ("إعدادات النظام", self.show_settings),
            ("تصغير الشاشة", self.toggle_fullscreen),
            ("تسجيل الخروج", self.logout)
        ]
        
        for text, command in buttons:
            btn = StyledButton(sidebar, text=arabic_text(text), command=command,
                          bg=SIDEBAR_COLOR, fg=TEXT_COLOR,
                          anchor="e", justify="right", padx=20, pady=10,
                        )
            btn.pack(fill="x")
        
        # إطار المحتوى الرئيسي
        self.content_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        self.show_dashboard()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("لوحة التحكم الرئيسية"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=50)
        
        stats_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        stats_frame.pack(pady=20)
        
        # إحصائيات المنتجات
        products = load_products()
        total_products = len(products)
        total_value = sum(p['price'] * p['quantity'] for p in products)
        
        # إحصائيات الفواتير
        invoice_files = [f for f in os.listdir(INVOICE_DIR) if f.startswith("INV-") and f.endswith(".png")]
        today_invoices = len([f for f in invoice_files if f.startswith(f"INV-{datetime.datetime.now().strftime('%Y%m%d')}")])
        
        # إحصائيات الديون
        if os.path.exists(DEBTS_FILE):
            df = pd.read_excel(DEBTS_FILE)

            # تصفية الديون النشطة فقط (المتبقي > 0)
            active_debts = df[df["المبلغ المتبقي"] > 0]

            total_debts = active_debts["المبلغ المتبقي"].sum()
            num_debtors = active_debts["اسم العميل"].nunique()
        else:
            total_debts = 0
            num_debtors = 0
        
        stats = [
            ("إجمالي المنتجات", total_products),
            ("القيمة الإجمالية", f"{total_value:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"),
            ("الفواتير اليومية", today_invoices),
            ("إجمالي الديون", f"{total_debts:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"),
            ("عدد المديونين", num_debtors)
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg=SIDEBAR_COLOR, padx=20, pady=10, bd=1, relief=tk.RAISED)
            stat_frame.grid(row=i//2, column=i%2, padx=10, pady=10)
            
            tk.Label(stat_frame, text=arabic_text(label), font=FONT, 
                    bg=SIDEBAR_COLOR, fg=TEXT_COLOR).pack()
            tk.Label(stat_frame, text=arabic_text(str(value)), font=LARGE_FONT, 
                    bg=SIDEBAR_COLOR, fg=BUTTON_COLOR).pack()
    
    def show_products_management(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إدارة المنتجات"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        # إطار البحث والإضافة
        search_add_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_add_frame.pack(pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_add_frame, textvariable=self.search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_add_frame, text=arabic_text("بحث"), 
                             command=self.search_products, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        add_btn = StyledButton(search_add_frame, text=arabic_text("إضافة منتج"), 
                          command=self.add_product, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        add_btn.pack(side="left", padx=5)
        
        # زر استيراد من إكسل
        import_btn = StyledButton(search_add_frame, text=arabic_text(" استيراد من إكسل"), 
                               command=self.import_from_excel, bg="#2ecc71", fg=TEXT_COLOR)
        import_btn.pack(side="left", padx=5)
        
        # جدول المنتجات
        columns = ("#", "الكود", "الاسم", "السعر", "الكمية", "التصنيف")
        self.products_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.products_tree.heading(col, text=arabic_text(col))
            self.products_tree.column(col, width=100, anchor="center")
        
        self.products_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        # أزرار التحكم
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        delete_btn = StyledButton(control_frame, text=arabic_text("حذف"), 
                             command=self.delete_product, bg="red", fg=TEXT_COLOR)
        delete_btn.pack(side="left", padx=10)
        
        export_btn = StyledButton(control_frame, text=arabic_text("تصدير"), 
                             command=self.export_products, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        export_btn.pack(side="left", padx=10)
        
        self.load_products_to_tree()
        
    def import_from_excel(self):
        # فتح نافذة لاختيار ملف الإكسل
        file_path = filedialog.askopenfilename(
            title="اختر ملف الإكسل",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return
        
        try:
            # قراءة ملف الإكسل
            df = pd.read_excel(file_path)
            
            # التحقق من وجود الأعمدة الأساسية
            required_columns = ['الكود', 'الاسم', 'السعر', 'الكمية']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messagebox.showerror(
                    "خطأ",
                    f"الملف لا يحتوي على الأعمدة المطلوبة: {', '.join(missing_columns)}"
                )
                return
            
            # تحميل المنتجات الحالية
            products = load_products()
            
            # عدد المنتجات قبل الاستيراد
            before_count = len(products)
            
            # معالجة البيانات واستيرادها
            for _, row in df.iterrows():
                product = {
                    "code": str(row['الكود']),
                    "name": str(row['الاسم']),
                    "price": float(row['السعر']),
                    "quantity": int(row['الكمية']),
                    "category": str(row.get('التصنيف', '')),
                    "description": str(row.get('الوصف', ''))
                }
                
                # التحقق من عدم تكرار الكود
                if not any(p['code'] == product['code'] for p in products):
                    products.append(product)
            
            # حفظ المنتجات الجديدة
            save_products(products)
            
            # عدد المنتجات المضافة
            added_count = len(products) - before_count
            
            # عرض رسالة نجاح
            messagebox.showinfo(
                "تم الاستيراد",
                f"تمت إضافة {added_count} منتج بنجاح من أصل {len(df)} منتج في الملف"
            )
            
            # تحديث جدول المنتجات
            self.load_products_to_tree()
            
        except Exception as e:
            messagebox.showerror(
                "خطأ في الاستيراد",
                f"حدث خطأ أثناء استيراد الملف: {str(e)}"
            )
    
    def load_products_to_tree(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        products = load_products()
        for i, product in enumerate(products, 1):
            quantity = product.get("quantity", 0)
            quantity_text = "منتهي" if quantity == 0 else str(quantity)
            
            self.products_tree.insert("", "end", values=(
                i,
                product.get("code", ""),
                product.get("name", ""),
                f"{product.get('price', 0):.2f}",
                quantity_text,
                product.get("category", "")
            ))
    
    def search_products(self):
        search_term = self.search_var.get()
        if not search_term:
            self.load_products_to_tree()
            return
        
        products = search_products(search_term)
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for i, product in enumerate(products, 1):
            quantity = product.get("quantity", 0)
            quantity_text = "منتهي" if quantity == 0 else str(quantity)
            
            self.products_tree.insert("", "end", values=(
                i,
                product.get("code", ""),
                product.get("name", ""),
                f"{product.get('price', 0):.2f}",
                quantity_text,
                product.get("category", "")
            ))
    
    def add_product(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة منتج جديد")
        add_window.geometry("500x400")
        add_window.configure(bg=BG_COLOR)
        
        tk.Label(add_window, text=arabic_text("إضافة منتج جديد"), font=TITLE_FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        fields = [
            ("الكود", "code"),
            ("الاسم", "name"),
            ("السعر", "price"),
            ("الكمية", "quantity"),
            ("التصنيف", "category"),
            ("الوصف", "description")
        ]
        
        self.product_entries = {}
        
        for label, field in fields:
            frame = tk.Frame(add_window, bg=BG_COLOR)
            frame.pack(pady=5)
            
            tk.Label(frame, text=arabic_text(label), font=FONT, 
                    bg=BG_COLOR, fg=TEXT_COLOR, width=15).pack(side="right")
            
            entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
            entry.pack(side="right")
            self.product_entries[field] = entry
        
        def save_product():
            product_data = {}
            for field, entry in self.product_entries.items():
                value = entry.get()
                if field in ["price", "quantity"]:
                    try:
                        value = float(value) if field == "price" else int(value)
                    except ValueError:
                        messagebox.showerror("خطأ", f"قيمة غير صحيحة لـ {field}")
                        return
                product_data[field] = value
            
            products = load_products()
            products.append(product_data)
            save_products(products)
            
            messagebox.showinfo("تم", "تمت إضافة المنتج بنجاح")
            add_window.destroy()
            self.load_products_to_tree()
        
        save_btn = StyledButton(add_window, text=arabic_text("حفظ"), command=save_product,
                           bg=BUTTON_COLOR, fg=TEXT_COLOR)
        save_btn.pack(pady=20)
    
    def delete_product(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار منتج للحذف")
            return
        
        item_values = self.products_tree.item(selected_item)['values']
        product_name = item_values[2]
        product_code = item_values[1]
        
        confirm = messagebox.askyesno("تأكيد", 
                                    f"هل أنت متأكد من حذف المنتج: {product_name}؟")
        if not confirm:
            return
        
        products = load_products()
        products = [p for p in products if str(p.get("code", "")) != str(product_code)]
        
        save_products(products)
        messagebox.showinfo("تم", "تم حذف المنتج بنجاح")
        self.load_products_to_tree()
    
    def export_products(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV Files", "*.csv")],
                                               title=arabic_text("حفظ ملف المنتجات"))
        if not file_path:
            return
        
        products = load_products()
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["الكود", "الاسم", "السعر", "الكمية", "التصنيف", "الوصف"])
            
            for product in products:
                writer.writerow([
                    product.get('code', ''),
                    product.get('name', ''),
                    product.get('price', 0),
                    product.get('quantity', 0),
                    product.get('category', ''),
                    product.get('description', '')
                ])
        
        messagebox.showinfo("تم", f"تم تصدير البيانات إلى: {file_path}")
    
    def show_invoices_management(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إدارة الفواتير"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.invoice_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.invoice_search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.search_invoices, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        columns = ("#", "رقم الفاتورة", "التاريخ", "العميل", "الإجمالي", "النوع")
        self.invoices_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.invoices_tree.heading(col, text=arabic_text(col))
            self.invoices_tree.column(col, width=120, anchor="center")
        
        self.invoices_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        view_btn = StyledButton(control_frame, text=arabic_text("عرض"), 
                           command=self.view_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        view_btn.pack(side="left", padx=10)
        
        print_btn = StyledButton(control_frame, text=arabic_text("طباعة"), 
                            command=self.print_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        print_btn.pack(side="left", padx=10)
        
        delete_btn = StyledButton(control_frame, text=arabic_text("حذف"), 
                             command=self.delete_invoice, bg="red", fg=TEXT_COLOR)
        delete_btn.pack(side="left", padx=10)
        
        self.load_invoices()
    
    def load_invoices(self):
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            
            for i, row in df.iterrows():
                self.invoices_tree.insert("", "end", values=(
                    i+1,
                    row["رقم الفاتورة"],
                    row["التاريخ"],
                    row["اسم العميل"],
                    f"{row['الإجمالي']:.2f}",
                    row.get("نوع الفاتورة", "بيع")
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن تحميل الفواتير: {str(e)}")
    
    def search_invoices(self):
        search_term = self.invoice_search_var.get()
        if not search_term:
            self.load_invoices()
            return
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            filtered_df = df[df["اسم العميل"].str.contains(search_term, case=False, na=False)]
            
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            
            for i, row in filtered_df.iterrows():
                self.invoices_tree.insert("", "end", values=(
                    i+1,
                    row["رقم الفاتورة"],
                    row["التاريخ"],
                    row["اسم العميل"],
                    f"{row['الإجمالي']:.2f}",
                    row.get("نوع الفاتورة", "بيع")
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن البحث في الفواتير: {str(e)}")
    
    def view_invoice(self):
        selected_item = self.invoices_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار فاتورة للعرض")
            return
        
        item_values = self.invoices_tree.item(selected_item)['values']
        invoice_num = item_values[1]
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            invoice_data = df[df["رقم الفاتورة"] == invoice_num].iloc[0]
            
            view_window = tk.Toplevel(self.root)
            view_window.title(f"فاتورة رقم {invoice_num}")
            view_window.geometry("800x600")
            view_window.configure(bg=BG_COLOR)
            
            # عرض تفاصيل الفاتورة
            tk.Label(view_window, text=arabic_text(f"فاتورة رقم: {invoice_num}"), 
                    font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
            
            tk.Label(view_window, text=arabic_text(f"التاريخ: {invoice_data['التاريخ']}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text(f"العميل: {invoice_data['اسم العميل']}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text(f"الإجمالي: {invoice_data['الإجمالي']:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text("المنتجات:"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
            
            products_text = tk.Text(view_window, font=FONT, bg=ENTRY_COLOR, height=10)
            products_text.pack(pady=10, padx=20, fill="both", expand=True)
            products_text.insert(tk.END, arabic_text(invoice_data["المنتجات"]))
            products_text.config(state="disabled")
            
            # عرض صورة الفاتورة إذا كانت موجودة
            if os.path.exists(invoice_data["مسار الصورة"]):
                img = Image.open(invoice_data["مسار الصورة"])
                img.thumbnail((600, 400))
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(view_window, image=photo)
                label.image = photo
                label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن عرض الفاتورة: {str(e)}")
    
    def print_invoice(self):
        selected_item = self.invoices_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار فاتورة للطباعة")
            return
        
        item_values = self.invoices_tree.item(selected_item)['values']
        invoice_num = item_values[1]
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            invoice_data = df[df["رقم الفاتورة"] == invoice_num].iloc[0]
            
            if os.path.exists(invoice_data["مسار الصورة"]):
                img = Image.open(invoice_data["مسار الصورة"])
                img.show()
            else:
                messagebox.showerror("خطأ","لا يمكن العثور على صورة الفاتورة")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن طباعة الفاتورة: {str(e)}")
    
    def delete_invoice(self):
        selected_item = self.invoices_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار فاتورة للحذف")
            return
        
        item_values = self.invoices_tree.item(selected_item)['values']
        invoice_num = item_values[1]
        
        confirm = messagebox.askyesno("تأكيد", 
                                    f"هل أنت متأكد من حذف الفاتورة رقم: {invoice_num}؟")
        if not confirm:
            return
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            invoice_data = df[df["رقم الفاتورة"] == invoice_num].iloc[0]
            
            # حذف صورة الفاتورة
            if os.path.exists(invoice_data["مسار الصورة"]):
                os.remove(invoice_data["مسار الصورة"])
            
            # حذف الفاتورة من ملف الإكسل
            df = df[df["رقم الفاتورة"] != invoice_num]
            df.to_excel(excel_file, index=False)
            
            self.invoices_tree.delete(selected_item)
            messagebox.showinfo("تم", "تم حذف الفاتورة بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن حذف الفاتورة: {str(e)}")
    
    def show_debts_management(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إدارة الديون"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.debt_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.debt_search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.search_debts, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        columns = ("#", "اسم العميل", "المبلغ", "المتبقي", "حالة السداد", "تاريخ الفاتورة", "رقم الفاتورة")
        self.debts_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.debts_tree.heading(col, text=arabic_text(col))
            if col == "رقم الفاتورة":
                self.debts_tree.column(col, width=0, stretch=False)  # إخفاء العمود
            else:
                self.debts_tree.column(col, width=120, anchor="center")
        
        self.debts_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        pay_btn = StyledButton(control_frame, text=arabic_text("تسديد"), 
                          command=self.pay_debt, bg="#27ae60", fg=TEXT_COLOR)
        pay_btn.pack(side="left", padx=10)
        
        print_btn = StyledButton(control_frame, text=arabic_text("طباعة"), 
                            command=self.print_debt_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        print_btn.pack(side="left", padx=10)
        
        delete_btn = StyledButton(control_frame, text=arabic_text("حذف"), 
                            command=self.delete_debt, bg="red", fg=TEXT_COLOR)
        delete_btn.pack(side="left", padx=10)
        
        self.load_debts()
    
    def load_debts(self):
        if not os.path.exists(DEBTS_FILE):
            return

        for item in self.debts_tree.get_children():
            self.debts_tree.delete(item)

        try:
            df = pd.read_excel(DEBTS_FILE)
            # التعديل هنا: عرض فقط الديون النشطة
            active_debts = df[df["المبلغ المتبقي"] > 0]

            for i, row in active_debts.iterrows():
                self.debts_tree.insert("", "end", values=(
                    i+1,
                    row["اسم العميل"],
                    f"{row['المبلغ']:.2f}",
                    f"{row['المبلغ المتبقي']:.2f}",
                    row["حالة السداد"],
                    row["التاريخ"],
                    row["رقم الفاتورة"]
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن تحميل بيانات الديون: {str(e)}")
    
    def search_debts(self):
        search_term = self.debt_search_var.get()
        if not search_term:
            self.load_debts()
            return
        
        if not os.path.exists(DEBTS_FILE):
            return
        
        try:
            df = pd.read_excel(DEBTS_FILE)
            # التعديل هنا: تصفية الديون النشطة فقط
            active_debts = df[df["المبلغ المتبقي"] > 0]
            filtered_df = active_debts[active_debts["اسم العميل"].str.contains(search_term, case=False, na=False)]
            
            for item in self.debts_tree.get_children():
                self.debts_tree.delete(item)
            
            for i, row in filtered_df.iterrows():
                self.debts_tree.insert("", "end", values=(
                    i+1,
                    row["اسم العميل"],
                    f"{row['المبلغ']:.2f}",
                    f"{row['المبلغ المتبقي']:.2f}",
                    row["حالة السداد"],
                    row["التاريخ"],
                    row["رقم الفاتورة"]
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن البحث في الديون: {str(e)}")
    
    def delete_debt(self):
        selected_item = self.debts_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار دين للحذف")
            return
        
        item_values = self.debts_tree.item(selected_item)['values']
        invoice_num = item_values[6]  # رقم الفاتورة
        
        confirm = messagebox.askyesno("تأكيد", 
                                    f"هل أنت متأكد من حذف الدين رقم: {invoice_num}؟")
        if not confirm:
            return
        
        try:
            df = pd.read_excel(DEBTS_FILE)
            df = df[df['رقم الفاتورة'] != invoice_num]
            df.to_excel(DEBTS_FILE, index=False)
            self.debts_tree.delete(selected_item)
            messagebox.showinfo("تم", "تم حذف الدين بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن حذف الدين: {str(e)}")
    
    def pay_debt(self):
        selected_item = self.debts_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار دين لتسديده")
            return
        
        item_values = self.debts_tree.item(selected_item)['values']
        customer_name = item_values[1]
        total_amount = float(item_values[2])
        remaining_amount = float(item_values[3])
        invoice_num = item_values[6]  # رقم الفاتورة
        
        pay_window = tk.Toplevel(self.root)
        pay_window.title("تسديد دين")
        pay_window.geometry("500x400")
        pay_window.configure(bg=BG_COLOR)
        
        tk.Label(pay_window, text=arabic_text(f"تسديد دين للعميل: {customer_name}"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        tk.Label(pay_window, text=arabic_text(f"المبلغ الإجمالي: {total_amount:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(pay_window, text=arabic_text(f"المبلغ المتبقي: {remaining_amount:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(pay_window, text=arabic_text("المبلغ المسدد:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.payment_amount = tk.DoubleVar(value=remaining_amount)
        payment_entry = tk.Entry(pay_window, textvariable=self.payment_amount, font=FONT, bg=ENTRY_COLOR)
        payment_entry.pack()
        
        tk.Label(pay_window, text=arabic_text("طريقة السداد:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.payment_method = ttk.Combobox(pay_window, 
                                         values=[arabic_text("نقدي"), arabic_text("تحويل بنكي")],
                                         state="readonly", font=FONT)
        self.payment_method.pack()
        self.payment_method.current(0)
        
        def process_payment():
            paid_amount = self.payment_amount.get()
            payment_method = self.payment_method.get()
            
            if paid_amount <= 0:
                messagebox.showerror("خطأ", "المبلغ يجب أن يكون أكبر من الصفر")
                return
            
            if paid_amount > remaining_amount:
                messagebox.showerror("خطأ", "المبلغ المسدد أكبر من المبلغ المتبقي")
                return
            
            try:
                # تحديث ملف الديون
                df = pd.read_excel(DEBTS_FILE)
                mask = (df["اسم العميل"] == customer_name) & (df["رقم الفاتورة"] == invoice_num)
                
                new_remaining = remaining_amount - paid_amount
                status = "مسدد" if new_remaining <= 0 else "مسدد جزئياً"
                
                df.loc[mask, "المبلغ المتبقي"] = new_remaining
                df.loc[mask, "حالة السداد"] = status
                df.loc[mask, "تاريخ السداد"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # حفظ ملف الديون
                df.to_excel(DEBTS_FILE, index=False)
                
                # تسجيل عملية السداد
                payment_data = {
                    "رقم الفاتورة": [invoice_num],
                    "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "اسم العميل": [customer_name],
                    "المبلغ المسدد": [paid_amount],
                    "المبلغ المتبقي": [new_remaining],
                    "طريقة السداد": [payment_method]
                }
                
                payment_df = pd.DataFrame(payment_data)
                
                if os.path.exists(DEBT_PAYMENTS_FILE):
                    with pd.ExcelWriter(DEBT_PAYMENTS_FILE, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                        existing_df = pd.read_excel(DEBT_PAYMENTS_FILE)
                        last_row = len(existing_df)
                        payment_df.to_excel(writer, startrow=last_row+1, index=False, header=False)
                else:
                    payment_df.to_excel(DEBT_PAYMENTS_FILE, index=False)
                
                # إنشاء فاتورة السداد
                payment_items = [
                    ["سداد دين", f"{paid_amount:.2f}", 1, f"{paid_amount:.2f}"]
                ]
                
                img = save_invoice_to_image(payment_items, 
                                          self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                          customer_name, 
                                          paid_amount,
                                          "سداد دين")
                
                if img:
                    payment_filename = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    payment_path = os.path.join(INVOICE_DIR, payment_filename)
                    img.save(payment_path)
                    
                    # إضافة فاتورة السداد إلى ملف الفواتير
                    excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
                    invoice_data = {
                        "رقم الفاتورة": [f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "اسم العميل": [customer_name],
                        "الإجمالي": [paid_amount],
                        "مسار الصورة": [payment_path],
                        "المنتجات": ["سداد دين"],
                        "نوع الفاتورة": "سداد دين"
                    }
                    
                    df_inv = pd.DataFrame(invoice_data)
                    if os.path.exists(excel_file):
                        with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                            existing_df = pd.read_excel(excel_file)
                            last_row = len(existing_df)
                            df_inv.to_excel(writer, startrow=last_row+1, index=False, header=False)
                    else:
                        df_inv.to_excel(excel_file, index=False)
                    
                    # عرض الفاتورة للمستخدم
                    img.show()
                
                message = (f"تم تسديد المبلغ بالكامل ({paid_amount:.2f})" 
                          if new_remaining <= 0 
                          else arabic_text(f"تم تسديد {paid_amount:.2f}، المتبقي {new_remaining:.2f}"))
                
                messagebox.showinfo("تم", message)
                pay_window.destroy()
                self.load_debts()
                self.show_dashboard()  # تحديث لوحة التحكم الرئيسية
            except Exception as e:
                messagebox.showerror("خطأ", f"لا يمكن تسديد الدين: {str(e)}")
        
        btn_frame = tk.Frame(pay_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        StyledButton(btn_frame, text=arabic_text("تسديد"), command=process_payment,
                bg="#27ae60", fg=TEXT_COLOR).pack(side="left", padx=10)
        
        StyledButton(btn_frame, text=arabic_text("إلغاء"), command=pay_window.destroy,
                bg="red", fg=TEXT_COLOR).pack(side="left", padx=10)
    
    def print_debt_invoice(self):
        selected_item = self.debts_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار دين لطباعة فاتورته")
            return
        
        item_values = self.debts_tree.item(selected_item)['values']
        customer_name = item_values[1]
        remaining_amount = float(item_values[3])
        
        try:
            df = pd.read_excel(DEBTS_FILE)
            debt_data = df[(df["اسم العميل"] == customer_name) & (df["المبلغ المتبقي"] > 0)].iloc[0]
            
            items = [["فاتورة دين", f"{remaining_amount:.2f}", 1, f"{remaining_amount:.2f}"]]
            img = save_invoice_to_image(items, 
                                      self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                      customer_name, 
                                      remaining_amount,
                                      "دين")
            
            if img:
                img.show()
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن طباعة فاتورة الدين: {str(e)}")
    
    def show_sales_reports(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("تقارير المبيعات"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        options_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        options_frame.pack(pady=20)
        
        tk.Label(options_frame, text=arabic_text("نوع التقرير:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=10)
        
        self.report_type = ttk.Combobox(options_frame, 
                                      values=[arabic_text("يومي"), arabic_text("أسبوعي"), arabic_text("شهري")],
                                      state="readonly", font=FONT)
        self.report_type.grid(row=0, column=1, padx=10)
        self.report_type.current(0)
        
        tk.Label(options_frame, text=arabic_text("الفترة:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, padx=10)
        
        self.report_date = tk.Entry(options_frame, font=FONT, bg=ENTRY_COLOR)
        self.report_date.grid(row=1, column=1, padx=10)
        self.report_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        generate_btn = StyledButton(options_frame, text=arabic_text("إنشاء التقرير"), 
                               command=self.generate_report, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        generate_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.report_text = tk.Text(self.content_frame, font=FONT, bg=ENTRY_COLOR, height=15)
        self.report_text.pack(pady=20, padx=20, fill="both", expand=True)
        
        export_btn = StyledButton(self.content_frame, text=arabic_text("تصدير التقرير"), 
                             command=self.export_report, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        export_btn.pack(pady=10)
    
    def generate_report(self):
        report_type = self.report_type.get()
        date_str = self.report_date.get()
        
        try:
            report_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD")
            return
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            df["التاريخ"] = pd.to_datetime(df["التاريخ"])
            
            if report_type == arabic_text("يومي"):
                filtered_df = df[df["التاريخ"].dt.date == report_date.date()]
            elif report_type == arabic_text("أسبوعي"):
                filtered_df = df[df["التاريخ"].dt.isocalendar().week == report_date.isocalendar()[1]]
            else:
                filtered_df = df[(df["التاريخ"].dt.month == report_date.month) & 
                               (df["التاريخ"].dt.year == report_date.year)]
            
            total_sales = filtered_df["الإجمالي"].sum()
            num_invoices = len(filtered_df)
            
            self.report_text.delete(1.0, tk.END)
            
            if report_type == arabic_text("يومي"):
                self.report_text.insert(tk.END, f"تقرير المبيعات اليومي لتاريخ: {report_date.strftime('%Y-%m-%d')}\n\n")
            elif report_type == arabic_text("أسبوعي"):
                self.report_text.insert(tk.END, f"تقرير المبيعات الأسبوعي للأسبوع: {report_date.isocalendar()[1]}\n\n")
            else:
                self.report_text.insert(tk.END, f"تقرير المبيعات الشهري لشهر: {report_date.strftime('%Y-%m')}\n\n")
            
            self.report_text.insert(tk.END, f"إجمالي المبيعات: {total_sales:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}\n")
            self.report_text.insert(tk.END, f"عدد الفواتير: {num_invoices}\n\n")
            
            # عرض تفاصيل الفواتير
            self.report_text.insert(tk.END, "تفاصيل الفواتير:\n")
            for _, row in filtered_df.iterrows():
                self.report_text.insert(tk.END, f"- فاتورة رقم {row['رقم الفاتورة']} بتاريخ {row['التاريخ']} للعميل {row['اسم العميل']} بمبلغ {row['الإجمالي']:.2f}\n")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن إنشاء التقرير: {str(e)}")
    
    def export_report(self):
        report_text = self.report_text.get(1.0, tk.END)
        if not report_text.strip():
            messagebox.showerror("خطأ", "لا يوجد تقرير لتصديره")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt")],
                                               title="حفظ التقرير")
        if not file_path:
            return
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        messagebox.showinfo("تم", f"تم حفظ التقرير في: {file_path}")
    
    def show_settings(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إعدادات النظام"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        settings_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        settings_frame.pack(pady=20)
        
        tk.Label(settings_frame, text=arabic_text("اسم الشركة:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        self.company_name_var = tk.StringVar(value=self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'))
        company_entry = tk.Entry(settings_frame, textvariable=self.company_name_var, 
                               font=FONT, bg=ENTRY_COLOR, width=30)
        company_entry.grid(row=0, column=0, padx=10, pady=10)
        
        tk.Label(settings_frame, text=arabic_text("شعار الشركة:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=2, padx=10, pady=10, sticky="e")
        
        self.logo_path_var = tk.StringVar(value=self.app.config.get('DEFAULT', 'logo_path', fallback=''))
        logo_entry = tk.Entry(settings_frame, textvariable=self.logo_path_var, 
                            font=FONT, bg=ENTRY_COLOR, width=30, state="readonly")
        logo_entry.grid(row=1, column=0, padx=10, pady=10)
        
        browse_btn = StyledButton(settings_frame, text=arabic_text("استعراض"), 
                             command=self.browse_logo, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        browse_btn.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(settings_frame, text=arabic_text("العملة الافتراضية:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        
        self.currency_var = tk.StringVar(value=self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه'))
        currency_entry = tk.Entry(settings_frame, textvariable=self.currency_var, 
                                font=FONT, bg=ENTRY_COLOR, width=30)
        currency_entry.grid(row=2, column=0, padx=10, pady=10)
        
        tk.Label(settings_frame, text=arabic_text("معدل الضريبة:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=3, column=2, padx=10, pady=10, sticky="e")
        
        self.tax_var = tk.StringVar(value=self.app.config.get('DEFAULT', 'tax_rate', fallback='0.14'))
        tax_entry = tk.Entry(settings_frame, textvariable=self.tax_var, 
                           font=FONT, bg=ENTRY_COLOR, width=30)
        tax_entry.grid(row=3, column=0, padx=10, pady=10)
        
        save_btn = StyledButton(self.content_frame, text=arabic_text("حفظ الإعدادات"), 
                           command=self.save_settings, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        save_btn.pack(pady=20)
    
    def browse_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")],
                                            title=arabic_text("اختر صورة الشعار"))
        if file_path:
            try:
                shutil.copy(file_path, LOGO_FILE)
                self.logo_path_var.set(file_path)
            except Exception as e:
                messagebox.showerror("خطأ", f"لا يمكن تحميل الصورة: {str(e)}")
    
    def save_settings(self):
        self.app.config.set('DEFAULT', 'company_name', self.company_name_var.get())
        self.app.config.set('DEFAULT', 'logo_path', self.logo_path_var.get())
        self.app.config.set('DEFAULT', 'default_currency', self.currency_var.get())
        self.app.config.set('DEFAULT', 'tax_rate', self.tax_var.get())
        
        with open(CONFIG_FILE, 'w') as configfile:
            self.app.config.write(configfile)
        
        messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح")
    
    def logout(self):
        self.root.destroy()
        LoginWindow(self.app)

class CashierPanel:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.style = ttk.Style()
        self.root.style.theme_use("clam")
        self.root.iconbitmap(None)
        self.root.title("لوحة التحكم - الكاشير")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_COLOR)
        self.fullscreen_state = True
        
        self.current_invoice = {
            "customer_name": "",
            "items": [],
            "total": 0.0
        }
        
        self.setup_ui()
        self.root.mainloop()
        
                # إضافة هذه السطور لتعيين الأيقونة
        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def toggle_fullscreen(self):
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes('-fullscreen', self.fullscreen_state)
    
    def setup_ui(self):
        # إنشاء الشريط الجانبي
        sidebar = tk.Frame(self.root, bg=SIDEBAR_COLOR, width=250)
        sidebar.pack(side="right", fill="y")
        
        # عنوان اللوحة
        title_frame = tk.Frame(sidebar, bg="#2c3e50", height=80)
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text=arabic_text("لوحة الكاشير"), font=("Arial", 18, "bold"), 
                bg="#2c3e50", fg="#f1c40f").pack(pady=20)
        
        # أزرار القائمة
        buttons = [
            ("فاتورة جديدة", self.show_create_invoice),
            ("إدارة الديون", self.show_manage_debts),
            ("عرض الفواتير", self.show_view_invoices),
            ("بحث عن منتج", self.show_search_product),
            ("تصغير الشاشة", self.toggle_fullscreen),
            ("تسجيل الخروج", self.logout)
        ]
        
        for text, command in buttons:
            btn = StyledButton(sidebar, text=arabic_text(text), command=command,
                          bg=SIDEBAR_COLOR, fg=TEXT_COLOR,
                          anchor="e", justify="right", padx=20, pady=10)
            btn.pack(fill="x")
        
        # إطار المحتوى الرئيسي
        self.content_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        self.show_create_invoice()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_create_invoice(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إنشاء فاتورة جديدة"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        customer_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        customer_frame.pack(pady=10)
        
        tk.Label(customer_frame, text=arabic_text("اسم العميل:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="right")
        
        self.customer_name = tk.Entry(customer_frame, font=FONT, bg=ENTRY_COLOR, width=30)
        self.customer_name.pack(side="right", padx=10)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.product_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.product_search_var, 
                              font=FONT, bg=ENTRY_COLOR, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.search_product_for_invoice, 
                             bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        self.search_results_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        self.search_results_frame.pack(pady=10)
        
        columns = ["المنتج", "السعر", "الكمية", "الإجمالي", "خيارات"]
        self.invoice_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.invoice_tree.heading(col, text=arabic_text(col))
            self.invoice_tree.column(col, width=120, anchor="center")
        
        self.invoice_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        self.total_var = tk.StringVar(value="0.00")
        total_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        total_frame.pack(pady=10)
        
        tk.Label(total_frame, text=arabic_text("المجموع:"), 
                font=LARGE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        
        tk.Label(total_frame, textvariable=self.total_var, 
                font=LARGE_FONT, bg=BG_COLOR, fg=BUTTON_COLOR).pack(side="left", padx=10)
        
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=20)
        
        save_btn = StyledButton(control_frame, text=arabic_text("حفظ الفاتورة"), 
                           command=self.save_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        save_btn.pack(side="left", padx=10)
        
        credit_btn = StyledButton(control_frame, text=arabic_text("بيع بالدين"), 
                             command=self.show_credit_options, bg="#8e44ad", fg=TEXT_COLOR)
        credit_btn.pack(side="left", padx=10)
        
        print_btn = StyledButton(control_frame, text=arabic_text("طباعة الفاتورة"), 
                            command=self.print_current_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        print_btn.pack(side="left", padx=10)
        
        clear_btn = StyledButton(control_frame, text=arabic_text("مسح الفاتورة"), 
                            command=self.clear_invoice, bg="red", fg=TEXT_COLOR)
        clear_btn.pack(side="left", padx=10)
        
        if self.current_invoice["items"]:
            for item in self.current_invoice["items"]:
                self.invoice_tree.insert("", "end", values=item)
            self.total_var.set(f"{self.current_invoice['total']:.2f}")
            self.customer_name.insert(0, self.current_invoice["customer_name"])
    
    def show_credit_options(self):
        credit_window = tk.Toplevel(self.root)
        credit_window.title("خيارات البيع بالدين")
        credit_window.geometry("400x300")
        credit_window.configure(bg=BG_COLOR)
        
        tk.Label(credit_window, text=arabic_text("خيارات البيع بالدين"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        btn_frame = tk.Frame(credit_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        # خيار دفع كامل المبلغ لاحقاً
        full_debt_btn = StyledButton(btn_frame, text=arabic_text("بيع بالدين بالكامل"), 
                                  command=lambda: self.save_credit_invoice("full"),
                                  bg="#8e44ad", fg=TEXT_COLOR)
        full_debt_btn.pack(pady=10, fill="x")
        
        # خيار دفع جزء من المبلغ الآن
        partial_pay_btn = StyledButton(btn_frame, text=arabic_text("دفع جزء الآن والباقي لاحقاً"), 
                                    command=lambda: self.show_partial_payment(),
                                    bg="#9b59b6", fg=TEXT_COLOR)
        partial_pay_btn.pack(pady=10, fill="x")
        
        cancel_btn = StyledButton(btn_frame, text=arabic_text("إلغاء"), 
                               command=credit_window.destroy,
                               bg="red", fg=TEXT_COLOR)
        cancel_btn.pack(pady=10, fill="x")
    
    def show_partial_payment(self):
        customer_name = self.customer_name.get()
        if not customer_name:
            messagebox.showerror("خطأ", "يجب إدخال اسم العميل")
            return
        
        items = []
        for item in self.invoice_tree.get_children():
            values = self.invoice_tree.item(item)['values']
            items.append(values[:4])
        
        if not items:
            messagebox.showerror("خطأ", "لا توجد عناصر في الفاتورة")
            return
        
        total = float(self.total_var.get())
        
        pay_window = tk.Toplevel(self.root)
        pay_window.title("دفع جزء من المبلغ")
        pay_window.geometry("500x400")
        pay_window.configure(bg=BG_COLOR)
        
        tk.Label(pay_window, text=arabic_text(f"دفع جزء من المبلغ للعميل: {customer_name}"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        tk.Label(pay_window, text=arabic_text(f"المبلغ الإجمالي: {total:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(pay_window, text=arabic_text("المبلغ المسدد الآن:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.paid_amount = tk.DoubleVar(value=0.0)
        paid_entry = tk.Entry(pay_window, textvariable=self.paid_amount, font=FONT, bg=ENTRY_COLOR)
        paid_entry.pack()
        
        tk.Label(pay_window, text=arabic_text("طريقة السداد:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.payment_method = ttk.Combobox(pay_window, 
                                         values=[arabic_text("نقدي"), arabic_text("تحويل بنكي")],
                                         state="readonly", font=FONT)
        self.payment_method.pack()
        self.payment_method.current(0)
        
        def process_partial_payment():
            paid_now = self.paid_amount.get()
            payment_method = self.payment_method.get()
            
            if paid_now <= 0:
                messagebox.showerror("خطأ", "المبلغ يجب أن يكون أكبر من الصفر")
                return
            
            if paid_now > total:
                messagebox.showerror("خطأ", "المبلغ المسدد أكبر من المبلغ الإجمالي")
                return
            
            # حفظ الفاتورة بالدين مع المبلغ المتبقي
            debt_amount = total - paid_now
            
            # تحديث كميات المنتجات في المخزون
            for item in items:
                product_name = item[0]
                sold_quantity = int(item[2])
                
                if not update_product_quantity(product_name, sold_quantity):
                    messagebox.showerror("خطأ", f"لا يمكن تحديث كمية المنتج: {product_name}")
                    return
            
            # إنشاء فاتورة للجزء المدفوع
            paid_items = [[arabic_text("دفعة أولية"), f"{paid_now:.2f}", 1, f"{paid_now:.2f}"]]
            img_paid = save_invoice_to_image(paid_items, 
                                          self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                          customer_name, 
                                          paid_now,
                                          "دفعة أولية")
            
            if img_paid:
                paid_filename = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                paid_path = os.path.join(INVOICE_DIR, paid_filename)
                img_paid.save(paid_path)
                
                # إضافة فاتورة الدفعة إلى ملف الفواتير
                excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
                paid_data = {
                    "رقم الفاتورة": [f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "اسم العميل": [customer_name],
                    "الإجمالي": [paid_now],
                    "مسار الصورة": [paid_path],
                    "المنتجات": [arabic_text("دفعة أولية")],
                    "نوع الفاتورة": "دفعة أولية"
                }
                
                df_paid = pd.DataFrame(paid_data)
                if os.path.exists(excel_file):
                    with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                        existing_df = pd.read_excel(excel_file)
                        last_row = len(existing_df)
                        df_paid.to_excel(writer, startrow=last_row+1, index=False, header=False)
                else:
                    df_paid.to_excel(excel_file, index=False)
            
            # إنشاء فاتورة للدين المتبقي
            try:
                df = pd.read_excel(DEBTS_FILE) if os.path.exists(DEBTS_FILE) else pd.DataFrame()
                
                new_debt = {
                    "رقم الفاتورة": [f"CR-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "اسم العميل": [customer_name],
                    "المبلغ": [debt_amount],
                    "المبلغ المتبقي": [debt_amount],
                    "حالة السداد": ["غير مسدد"],
                    "تاريخ السداد": [""],
                    "المنتجات": [", ".join([f"{item[0]} ({item[2]} × {item[1]})" for item in items])]
                }
                
                new_df = pd.DataFrame(new_debt)
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_excel(DEBTS_FILE, index=False)
                
                # إنشاء فاتورة للدين
                debt_items = [[arabic_text("فاتورة دين"), f"{debt_amount:.2f}", 1, f"{debt_amount:.2f}"]]
                img_debt = save_invoice_to_image(debt_items, 
                                              self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                              customer_name, 
                                              debt_amount,
                                              "دين")
                
                if img_debt:
                    debt_filename = f"DEBT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    debt_path = os.path.join(INVOICE_DIR, debt_filename)
                    img_debt.save(debt_path)
                    
                    # إضافة فاتورة الدين إلى ملف الفواتير
                    debt_data = {
                        "رقم الفاتورة": [f"DEBT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "اسم العميل": [customer_name],
                        "الإجمالي": [debt_amount],
                        "مسار الصورة": [debt_path],
                        "المنتجات": [", ".join([f"{item[0]} ({item[2]} × {item[1]})" for item in items])],
                        "نوع الفاتورة": "دين"
                    }
                    
                    df_debt = pd.DataFrame(debt_data)
                    if os.path.exists(excel_file):
                        with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                            existing_df = pd.read_excel(excel_file)
                            last_row = len(existing_df)
                            df_debt.to_excel(writer, startrow=last_row+1, index=False, header=False)
                    else:
                        df_debt.to_excel(excel_file, index=False)
                
                messagebox.showinfo("تم", 
                                  f"تم حفظ الفاتورة بالدين للعميل {customer_name}\nالمبلغ المتبقي: {debt_amount:.2f}")
                
                self.current_invoice = {
                    "customer_name": "",
                    "items": [],
                    "total": 0.0
                }
                self.clear_invoice()
                pay_window.destroy()
            except Exception as e:
                messagebox.showerror("خطأ", 
                                   f"لا يمكن حفظ الفاتورة بالدين: {str(e)}")
        
        btn_frame = tk.Frame(pay_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        StyledButton(btn_frame, text=arabic_text("حفظ"), command=process_partial_payment,
                bg=BUTTON_COLOR, fg=TEXT_COLOR).pack(side="left", padx=10)
        
        StyledButton(btn_frame, text=arabic_text("إلغاء"), command=pay_window.destroy,
                bg="red", fg=TEXT_COLOR).pack(side="left", padx=10)
    
    def save_credit_invoice(self, payment_type="full"):
        customer_name = self.customer_name.get()
        if not customer_name:
            messagebox.showerror("خطأ","يجب إدخال اسم العميل")
            return
        
        items = []
        for item in self.invoice_tree.get_children():
            values = self.invoice_tree.item(item)['values']
            items.append(values[:4])
        
        if not items:
            messagebox.showerror("خطأ","لا توجد عناصر في الفاتورة")
            return
        
        total = float(self.total_var.get())
        
        # تحديث كميات المنتجات في المخزون
        for item in items:
            product_name = item[0]
            sold_quantity = int(item[2])
            
            if not update_product_quantity(product_name, sold_quantity):
                messagebox.showerror("خطأ", f"لا يمكن تحديث كمية المنتج: {product_name}")
                return
        
        try:
            df = pd.read_excel(DEBTS_FILE) if os.path.exists(DEBTS_FILE) else pd.DataFrame()
            
            new_debt = {
                "رقم الفاتورة": [f"CR-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "اسم العميل": [customer_name],
                "المبلغ": [total],
                "المبلغ المتبقي": [total],
                "حالة السداد": ["غير مسدد"],
                "تاريخ السداد": [""],
                "المنتجات": [", ".join([f"{item[0]} ({item[2]} × {item[1]})" for item in items])]
            }
            
            new_df = pd.DataFrame(new_debt)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(DEBTS_FILE, index=False)
            
            # إنشاء فاتورة للدين
            debt_items = [[arabic_text("فاتورة دين"), f"{total:.2f}", 1, f"{total:.2f}"]]
            img = save_invoice_to_image(debt_items, 
                                      self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                      customer_name, 
                                      total,
                                      "دين")
            
            if img:
                debt_filename = f"DEBT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                debt_path = os.path.join(INVOICE_DIR, debt_filename)
                img.save(debt_path)
                
                # إضافة فاتورة الدين إلى ملف الفواتير
                excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
                debt_data = {
                    "رقم الفاتورة": [f"DEBT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                    "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "اسم العميل": [customer_name],
                    "الإجمالي": [total],
                    "مسار الصورة": [debt_path],
                    "المنتجات": [", ".join([f"{item[0]} ({item[2]} × {item[1]})" for item in items])],
                    "نوع الفاتورة": "دين"
                }
                
                df_debt = pd.DataFrame(debt_data)
                if os.path.exists(excel_file):
                    with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                        existing_df = pd.read_excel(excel_file)
                        last_row = len(existing_df)
                        df_debt.to_excel(writer, startrow=last_row+1, index=False, header=False)
                else:
                    df_debt.to_excel(excel_file, index=False)
            
            messagebox.showinfo("تم", 
                              f"تم حفظ الفاتورة بالدين للعميل {customer_name}\nالمبلغ الإجمالي: {total:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}")
            
            self.current_invoice = {
                "customer_name": "",
                "items": [],
                "total": 0.0
            }
            self.clear_invoice()
        except Exception as e:
            messagebox.showerror("خطأ", 
                               f"لا يمكن حفظ الفاتورة بالدين: {str(e)}")
    
    def show_manage_debts(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("إدارة الديون"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.debt_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.debt_search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.search_debts, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        columns = ("#", "اسم العميل", "المبلغ", "المتبقي", "حالة السداد", "تاريخ الفاتورة", "رقم الفاتورة")
        self.debts_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.debts_tree.heading(col, text=arabic_text(col))
            if col == "رقم الفاتورة":
                self.debts_tree.column(col, width=0, stretch=False)  # إخفاء العمود
            else:
                self.debts_tree.column(col, width=120, anchor="center")
        
        self.debts_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        pay_btn = StyledButton(control_frame, text=arabic_text("تسديد"), 
                          command=self.pay_debt, bg="#27ae60", fg=TEXT_COLOR)
        pay_btn.pack(side="left", padx=10)
        
        self.load_debts()
    
    def load_debts(self):
        if not os.path.exists(DEBTS_FILE):
            return
        
        for item in self.debts_tree.get_children():
            self.debts_tree.delete(item)
        
        try:
            df = pd.read_excel(DEBTS_FILE)
            for i, row in df.iterrows():
                if row["المبلغ المتبقي"] > 0:  # عرض فقط الديون التي لم تسدد بالكامل
                    self.debts_tree.insert("", "end", values=(
                        i+1,
                        row["اسم العميل"],
                        f"{row['المبلغ']:.2f}",
                        f"{row['المبلغ المتبقي']:.2f}",
                        row["حالة السداد"],
                        row["التاريخ"],
                        row["رقم الفاتورة"]  # إضافة رقم الفاتورة
                    ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن تحميل بيانات الديون: {str(e)}")
    
    def search_debts(self):
        search_term = self.debt_search_var.get()
        if not search_term:
            self.load_debts()
            return
        
        if not os.path.exists(DEBTS_FILE):
            return
        
        try:
            df = pd.read_excel(DEBTS_FILE)
            filtered_df = df[df["اسم العميل"].str.contains(search_term, case=False, na=False)]
            
            for item in self.debts_tree.get_children():
                self.debts_tree.delete(item)
            
            for i, row in filtered_df.iterrows():
                if row["المبلغ المتبقي"] > 0:  # عرض فقط الديون التي لم تسدد بالكامل
                    self.debts_tree.insert("", "end", values=(
                        i+1,
                        row["اسم العميل"],
                        f"{row['المبلغ']:.2f}",
                        f"{row['المبلغ المتبقي']:.2f}",
                        row["حالة السداد"],
                        row["التاريخ"],
                        row["رقم الفاتورة"]
                    ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن البحث في الديون: {str(e)}")
    
    def pay_debt(self):
        selected_item = self.debts_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار دين لتسديده")
            return
        
        item_values = self.debts_tree.item(selected_item)['values']
        customer_name = item_values[1]
        total_amount = float(item_values[2])
        remaining_amount = float(item_values[3])
        invoice_num = item_values[6]  # رقم الفاتورة
        
        pay_window = tk.Toplevel(self.root)
        pay_window.title("تسديد دين")
        pay_window.geometry("500x400")
        pay_window.configure(bg=BG_COLOR)
        
        tk.Label(pay_window, text=arabic_text(f"تسديد دين للعميل: {customer_name}"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        tk.Label(pay_window, text=arabic_text(f"المبلغ الإجمالي: {total_amount:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(pay_window, text=arabic_text(f"المبلغ المتبقي: {remaining_amount:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='EGP')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(pay_window, text=arabic_text("المبلغ المسدد:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.payment_amount = tk.DoubleVar(value=remaining_amount)
        payment_entry = tk.Entry(pay_window, textvariable=self.payment_amount, font=FONT, bg=ENTRY_COLOR)
        payment_entry.pack()
        
        tk.Label(pay_window, text=arabic_text("طريقة السداد:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        self.payment_method = ttk.Combobox(pay_window, 
                                         values=[arabic_text("نقدي"), arabic_text("تحويل بنكي")],
                                         state="readonly", font=FONT)
        self.payment_method.pack()
        self.payment_method.current(0)
        
        def process_payment():
            paid_amount = self.payment_amount.get()
            payment_method = self.payment_method.get()
            
            if paid_amount <= 0:
                messagebox.showerror("خطأ", "المبلغ يجب أن يكون أكبر من الصفر")
                return
            
            if paid_amount > remaining_amount:
                messagebox.showerror("خطأ", "المبلغ المسدد أكبر من المبلغ المتبقي")
                return
            
            try:
                # تحديث ملف الديون
                df = pd.read_excel(DEBTS_FILE)
                mask = (df["اسم العميل"] == customer_name) & (df["رقم الفاتورة"] == invoice_num)
                
                new_remaining = remaining_amount - paid_amount
                status = "مسدد" if new_remaining <= 0 else "مسدد جزئياً"
                
                df.loc[mask, "المبلغ المتبقي"] = new_remaining
                df.loc[mask, "حالة السداد"] = status
                df.loc[mask, "تاريخ السداد"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # حفظ ملف الديون
                df.to_excel(DEBTS_FILE, index=False)
                
                # تسجيل عملية السداد
                payment_data = {
                    "رقم الفاتورة": [invoice_num],
                    "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "اسم العميل": [customer_name],
                    "المبلغ المسدد": [paid_amount],
                    "المبلغ المتبقي": [new_remaining],
                    "طريقة السداد": [payment_method]
                }
                
                payment_df = pd.DataFrame(payment_data)
                
                if os.path.exists(DEBT_PAYMENTS_FILE):
                    with pd.ExcelWriter(DEBT_PAYMENTS_FILE, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                        existing_df = pd.read_excel(DEBT_PAYMENTS_FILE)
                        last_row = len(existing_df)
                        payment_df.to_excel(writer, startrow=last_row+1, index=False, header=False)
                else:
                    payment_df.to_excel(DEBT_PAYMENTS_FILE, index=False)
                
                # إنشاء فاتورة السداد
                payment_items = [
                    ["سداد دين", f"{paid_amount:.2f}", 1, f"{paid_amount:.2f}"]
                ]
                
                img = save_invoice_to_image(payment_items, 
                                          self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا'),
                                          customer_name, 
                                          paid_amount,
                                          "سداد دين")
                
                if img:
                    payment_filename = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    payment_path = os.path.join(INVOICE_DIR, payment_filename)
                    img.save(payment_path)
                    
                    # إضافة فاتورة السداد إلى ملف الفواتير
                    excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
                    invoice_data = {
                        "رقم الفاتورة": [f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"],
                        "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "اسم العميل": [customer_name],
                        "الإجمالي": [paid_amount],
                        "مسار الصورة": [payment_path],
                        "المنتجات": ["سداد دين"],
                        "نوع الفاتورة": "سداد دين"
                    }
                    
                    df_inv = pd.DataFrame(invoice_data)
                    if os.path.exists(excel_file):
                        with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                            existing_df = pd.read_excel(excel_file)
                            last_row = len(existing_df)
                            df_inv.to_excel(writer, startrow=last_row+1, index=False, header=False)
                    else:
                        df_inv.to_excel(excel_file, index=False)
                    
                    # عرض الفاتورة للمستخدم
                    img.show()
                
                message = (f"تم تسديد المبلغ بالكامل ({paid_amount:.2f})" 
                          if new_remaining <= 0 
                          else arabic_text(f"تم تسديد {paid_amount:.2f}، المتبقي {new_remaining:.2f}"))
                
                messagebox.showinfo("تم", message)
                pay_window.destroy()
                self.load_debts()
            except Exception as e:
                messagebox.showerror("خطأ", f"لا يمكن تسديد الدين: {str(e)}")
        
        btn_frame = tk.Frame(pay_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        StyledButton(btn_frame, text=arabic_text("تسديد"), command=process_payment,
                bg="#27ae60", fg=TEXT_COLOR).pack(side="left", padx=10)
        
        StyledButton(btn_frame, text=arabic_text("إلغاء"), command=pay_window.destroy,
                bg="red", fg=TEXT_COLOR).pack(side="left", padx=10)
    
    def show_view_invoices(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("عرض الفواتير"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.invoice_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.invoice_search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.search_invoices, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        columns = ("#", "رقم الفاتورة", "التاريخ", "العميل", "الإجمالي", "النوع")
        self.invoices_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.invoices_tree.heading(col, text=arabic_text(col))
            self.invoices_tree.column(col, width=120, anchor="center")
        
        self.invoices_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        control_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        control_frame.pack(pady=10)
        
        view_btn = StyledButton(control_frame, text=arabic_text("عرض"), 
                           command=self.view_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        view_btn.pack(side="left", padx=10)
        
        print_btn = StyledButton(control_frame, text=arabic_text("طباعة"), 
                            command=self.print_invoice, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        print_btn.pack(side="left", padx=10)
        
        self.load_invoices()
    
    def load_invoices(self):
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            
            for i, row in df.iterrows():
                self.invoices_tree.insert("", "end", values=(
                    i+1,
                    row["رقم الفاتورة"],
                    row["التاريخ"],
                    row["اسم العميل"],
                    f"{row['الإجمالي']:.2f}",
                    row.get("نوع الفاتورة", "بيع")
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن تحميل الفواتير: {str(e)}")
    
    def search_invoices(self):
        search_term = self.invoice_search_var.get()
        if not search_term:
            self.load_invoices()
            return
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            filtered_df = df[df["اسم العميل"].str.contains(search_term, case=False, na=False)]
            
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            
            for i, row in filtered_df.iterrows():
                self.invoices_tree.insert("", "end", values=(
                    i+1,
                    row["رقم الفاتورة"],
                    row["التاريخ"],
                    row["اسم العميل"],
                    f"{row['الإجمالي']:.2f}",
                    row.get("نوع الفاتورة", "بيع")
                ))
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن البحث في الفواتير: {str(e)}")
    
    def view_invoice(self):
        selected_item = self.invoices_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار فاتورة للعرض")
            return
        
        item_values = self.invoices_tree.item(selected_item)['values']
        invoice_num = item_values[1]
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            invoice_data = df[df["رقم الفاتورة"] == invoice_num].iloc[0]
            
            view_window = tk.Toplevel(self.root)
            view_window.title(f"فاتورة رقم {invoice_num}")
            view_window.geometry("800x600")
            view_window.configure(bg=BG_COLOR)
            
            # عرض تفاصيل الفاتورة
            tk.Label(view_window, text=arabic_text(f"فاتورة رقم: {invoice_num}"), 
                    font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
            
            tk.Label(view_window, text=arabic_text(f"التاريخ: {invoice_data['التاريخ']}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text(f"العميل: {invoice_data['اسم العميل']}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text(f"الإجمالي: {invoice_data['الإجمالي']:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            
            tk.Label(view_window, text=arabic_text("المنتجات:"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
            
            products_text = tk.Text(view_window, font=FONT, bg=ENTRY_COLOR, height=10)
            products_text.pack(pady=10, padx=20, fill="both", expand=True)
            products_text.insert(tk.END, arabic_text(invoice_data["المنتجات"]))
            products_text.config(state="disabled")
            
            # عرض صورة الفاتورة إذا كانت موجودة
            if os.path.exists(invoice_data["مسار الصورة"]):
                img = Image.open(invoice_data["مسار الصورة"])
                img.thumbnail((600, 400))
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(view_window, image=photo)
                label.image = photo
                label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن عرض الفاتورة: {str(e)}")
    
    def print_invoice(self):
        selected_item = self.invoices_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يجب اختيار فاتورة للطباعة")
            return
        
        item_values = self.invoices_tree.item(selected_item)['values']
        invoice_num = item_values[1]
        
        excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
        if not os.path.exists(excel_file):
            return
        
        try:
            df = pd.read_excel(excel_file)
            invoice_data = df[df["رقم الفاتورة"] == invoice_num].iloc[0]
            
            if os.path.exists(invoice_data["مسار الصورة"]):
                img = Image.open(invoice_data["مسار الصورة"])
                img.show()
            else:
                messagebox.showerror("خطأ","لا يمكن العثور على صورة الفاتورة")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن طباعة الفاتورة: {str(e)}")
    
    def search_product_for_invoice(self):
        search_term = self.product_search_var.get()
        if not search_term:
            return
        
        products = search_products(search_term)
        
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
        
        if not products:
            tk.Label(self.search_results_frame, text=arabic_text("لا توجد نتائج"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
            return
        
        for product in products[:5]:
            product_frame = tk.Frame(self.search_results_frame, bg=BG_COLOR)
            product_frame.pack(fill="x", pady=2)
            
            tk.Label(product_frame, 
                    text=arabic_text(f"{product['name']} - {product['price']:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}"), 
                    font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
            
            add_btn = StyledButton(product_frame, text=arabic_text("إضافة"), 
                              command=lambda p=product: self.add_to_invoice(p),
                              bg=BUTTON_COLOR, fg=TEXT_COLOR)
            add_btn.pack(side="right", padx=10)
    
    def add_to_invoice(self, product):
        qty_window = tk.Toplevel(self.root)
        qty_window.title("إضافة منتج")
        qty_window.geometry("300x200")
        qty_window.configure(bg=BG_COLOR)
        
        tk.Label(qty_window, text=arabic_text(f"المنتج: {product['name']}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        tk.Label(qty_window, text=arabic_text(f"السعر: {product['price']:.2f} {self.app.config.get('DEFAULT', 'default_currency', fallback='جنيه')}"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Label(qty_window, text=arabic_text("الكمية:"), 
                font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        qty_var = tk.IntVar(value=1)
        qty_entry = tk.Entry(qty_window, textvariable=qty_var, font=FONT, bg=ENTRY_COLOR)
        qty_entry.pack()
        
        def add_product():
            quantity = qty_var.get()
            if quantity <= 0:
                messagebox.showerror("خطأ","الكمية يجب أن تكون أكبر من الصفر")
                return
            
            # التحقق من توفر الكمية في المخزون
            available_quantity = product.get('quantity', 0)
            if quantity > available_quantity:
                messagebox.showerror("خطأ", f"الكمية المطلوبة غير متوفرة. المتاح: {available_quantity}")
                return
            
            total = product['price'] * quantity
            item_values = (
                product['name'],
                f"{product['price']:.2f}",
                quantity,
                f"{total:.2f}",
                arabic_text("حذف")
            )
            
            self.invoice_tree.insert("", "end", values=item_values)
            self.current_invoice["items"].append(item_values)
            self.current_invoice["total"] += total
            self.total_var.set(f"{self.current_invoice['total']:.2f}")
            qty_window.destroy()
        
        StyledButton(qty_window, text=arabic_text("إضافة"), command=add_product,
                bg=BUTTON_COLOR, fg=TEXT_COLOR).pack(pady=20)
    
    def save_invoice(self):
        customer_name = self.customer_name.get()
        if not customer_name:
            messagebox.showerror("خطأ", "يجب إدخال اسم العميل")
            return
        
        items = []
        for item in self.invoice_tree.get_children():
            values = self.invoice_tree.item(item)['values']
            items.append(values[:4])
        
        if not items:
            messagebox.showerror("خطأ", "لا توجد عناصر في الفاتورة")
            return
        
        # تحديث كميات المنتجات في المخزون
        for item in items:
            product_name = item[0]
            sold_quantity = int(item[2])
            
            if not update_product_quantity(product_name, sold_quantity):
                messagebox.showerror("خطأ", f"لا يمكن تحديث كمية المنتج: {product_name}")
                return
        
        invoice_num = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        total = float(self.total_var.get())
        company_name = self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا')
        
        img = save_invoice_to_image(items, company_name, customer_name, total)
        if img is None:
            return
        
        invoice_date = datetime.datetime.now().strftime("%Y%m%d")
        invoice_filename = f"{invoice_num}_{invoice_date}_{customer_name.replace(' ', '_')}_{total:.2f}.png"
        invoice_path = os.path.join(INVOICE_DIR, invoice_filename)
        
        try:
            img.save(invoice_path)
            
            # حفظ الفاتورة في ملف إكسل
            excel_file = os.path.join(INVOICE_DIR, "invoices.xlsx")
            invoice_data = {
                "رقم الفاتورة": [invoice_num],
                "التاريخ": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "اسم العميل": [customer_name],
                "الإجمالي": [total],
                "مسار الصورة": [invoice_path],
                "المنتجات": [", ".join([f"{item[0]} ({item[2]} × {item[1]})" for item in items])],
                "نوع الفاتورة": "بيع"
            }
            
            df = pd.DataFrame(invoice_data)
            
            if os.path.exists(excel_file):
                with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    existing_df = pd.read_excel(excel_file)
                    last_row = len(existing_df)
                    df.to_excel(writer, startrow=last_row+1, index=False, header=False)
            else:
                df.to_excel(excel_file, index=False)
            
            messagebox.showinfo("تم", 
                              f"تم حفظ الفاتورة رقم {invoice_num} بنجاح")
            
            self.current_invoice = {
                "customer_name": "",
                "items": [],
                "total": 0.0
            }
            self.clear_invoice()
        except Exception as e:
            messagebox.showerror("خطأ", 
                               f"لا يمكن حفظ الفاتورة: {str(e)}")
    
    def print_current_invoice(self):
        customer_name = self.customer_name.get()
        if not customer_name:
            messagebox.showerror("خطأ", "يجب إدخال اسم العميل")
            return
        
        items = []
        for item in self.invoice_tree.get_children():
            values = self.invoice_tree.item(item)['values']
            items.append(values[:4])
        
        if not items:
            messagebox.showerror("خطأ","لا توجد عناصر في الفاتورة")
            return
        
        total = float(self.total_var.get())
        company_name = self.app.config.get('DEFAULT', 'company_name', fallback='متجرنا')
        
        img = save_invoice_to_image(items, company_name, customer_name, total)
        if img is None:
            return
        
        print_window = tk.Toplevel(self.root)
        print_window.title("طباعة الفاتورة")
        print_window.geometry("400x300")
        print_window.configure(bg=BG_COLOR)
        
        img.thumbnail((300, 200))
        photo = ImageTk.PhotoImage(img)
        
        label = tk.Label(print_window, image=photo)
        label.image = photo
        label.pack(pady=10)
        
        tk.Label(print_window, text=arabic_text("خيارات الطباعة:"), 
               font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        copy_frame = tk.Frame(print_window, bg=BG_COLOR)
        copy_frame.pack(pady=5)
        
        tk.Label(copy_frame, text=arabic_text("عدد النسخ:"), 
               font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="right")
        
        self.copy_var = tk.IntVar(value=1)
        tk.Spinbox(copy_frame, from_=1, to=10, textvariable=self.copy_var, 
                  font=FONT, width=5).pack(side="right", padx=5)
        
        btn_frame = tk.Frame(print_window, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        StyledButton(btn_frame, text=arabic_text("طباعة"), 
                 command=lambda: self.print_image(img),
                 bg=BUTTON_COLOR, fg=TEXT_COLOR).pack(side="right", padx=10)
        
        StyledButton(btn_frame, text=arabic_text("حفظ الفاتورة"), 
                 command=lambda: self.save_invoice_from_print(img, customer_name, items, total),
                 bg=BUTTON_COLOR, fg=TEXT_COLOR).pack(side="right", padx=10)
        
        StyledButton(btn_frame, text=arabic_text("إلغاء"), 
                 command=print_window.destroy,
                 bg="red", fg=TEXT_COLOR).pack(side="right", padx=10)
    
    def print_image(self, img):
        try:
            temp_path = os.path.join(INVOICE_DIR, "temp_print.png")
            img.save(temp_path, "PNG", dpi=(300, 300))
            
            if os.name == 'nt':
                os.startfile(temp_path, "print")
            elif os.name == 'posix':
                os.system(f"lpr {temp_path}")
            
            messagebox.showinfo("تم", "تم إرسال الفاتورة إلى الطابعة")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن الطباعة: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def save_invoice_from_print(self, img, customer_name, items, total):
        invoice_num = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        invoice_date = datetime.datetime.now().strftime("%Y%m%d")
        invoice_filename = f"{invoice_num}_{invoice_date}_{customer_name.replace(' ', '_')}_{total:.2f}.png"
        invoice_path = os.path.join(INVOICE_DIR, invoice_filename)
        
        try:
            img.save(invoice_path, "PNG", dpi=(300, 300))
            messagebox.showinfo("تم", 
                              f"تم حفظ الفاتورة رقم {invoice_num} بنجاح")
            
            self.current_invoice = {
                "customer_name": "",
                "items": [],
                "total": 0.0
            }
            self.clear_invoice()
        except Exception as e:
            messagebox.showerror("خطأ", 
                               f"لا يمكن حفظ الفاتورة: {str(e)}")
    
    def clear_invoice(self):
        self.customer_name.delete(0, tk.END)
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        self.total_var.set("0.00")
        
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
        
        self.current_invoice = {
            "customer_name": "",
            "items": [],
            "total": 0.0
        }
    
    def show_search_product(self):
        self.clear_content()
        tk.Label(self.content_frame, text=arabic_text("بحث عن منتج"), 
                font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        search_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=FONT, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = StyledButton(search_frame, text=arabic_text("بحث"), 
                             command=self.perform_search, bg=BUTTON_COLOR, fg=TEXT_COLOR)
        search_btn.pack(side="left", padx=5)
        
        self.results_tree = ttk.Treeview(self.content_frame, 
                                       columns=("الكود", "الاسم", "السعر", "الكمية", "التصنيف"), 
                                       show="headings", height=15)
        
        for col in ["الكود", "الاسم", "السعر", "الكمية", "التصنيف"]:
            self.results_tree.heading(col, text=arabic_text(col))
            self.results_tree.column(col, width=120, anchor="center")
        
        self.results_tree.pack(pady=20, padx=10, fill="both", expand=True)
        
        self.load_all_products()
    
    def perform_search(self):
        search_term = self.search_var.get()
        if not search_term:
            self.load_all_products()
            return
        
        products = search_products(search_term)
        self.display_results(products)
    
    def load_all_products(self):
        products = load_products()
        self.display_results(products)
    
    def display_results(self, products):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for product in products:
            quantity = product.get("quantity", 0)
            quantity_text = "منتهي" if quantity == 0 else str(quantity)
            
            self.results_tree.insert("", "end", values=(
                product.get("code", ""),
                product.get("name", ""),
                f"{product.get('price', 0):.2f}",
                quantity_text,
                product.get("category", "")
            ))
    
    def logout(self):
        self.root.destroy()
        LoginWindow(self.app)

if __name__ == "__main__":
    # اختبار استيراد numpy
    try:
        import numpy as np
        print("numpy imported successfully!")
        print(f"numpy version: {np.__version__}")
    except ImportError as e:
        print(f"Error importing numpy: {e}")
    
    app = Application()