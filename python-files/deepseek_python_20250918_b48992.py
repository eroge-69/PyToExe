import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import sqlite3
from datetime import datetime
import os
from PIL import Image, ImageTk
import webbrowser

class CarAccidentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام كناز - تسجيل حوادث السيارات والمطالبات التأمينية")
        self.root.geometry("1200x800")
        
        # ألوان الشركة من الشعار
        self.primary_color = "#22366d"  # الأزرق الداكن
        self.secondary_color = "#2584c6"  # الأزرق الفاتح
        self.accent_color = "#e6a41e"  # لون ذهبي للتأكيد
        
        # تخصيص مظهر التطبيق
        self.setup_styles()
        
        # إنشاء قاعدة البيانات
        self.init_database()
        
        # واجهة المستخدم
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # تخصيص الأزرار
        style.configure('Primary.TButton', 
                       background=self.secondary_color,
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        style.map('Primary.TButton', 
                 background=[('active', self.primary_color)])
        
        # تخصيص الإطارات
        style.configure('Header.TFrame', background=self.primary_color)
        style.configure('Secondary.TFrame', background=self.secondary_color)
        
        # تخصيص التسميات
        style.configure('Title.TLabel', 
                       background=self.primary_color,
                       foreground='white',
                       font=('Arial', 16, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=self.secondary_color,
                       foreground='white',
                       font=('Arial', 12, 'bold'))
        
    def init_database(self):
        self.conn = sqlite3.connect('accidents.db')
        self.c = self.conn.cursor()
        
        # إنشاء جدول الحوادث
        self.c.execute('''CREATE TABLE IF NOT EXISTS accidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        time TEXT,
                        location TEXT,
                        description TEXT,
                        parties_involved TEXT,
                        insurance_company TEXT,
                        claim_number TEXT,
                        status TEXT,
                        photos_path TEXT,
                        documents_path TEXT
                        )''')
        self.conn.commit()
    
    def create_widgets(self):
        # إنشاء الهيكل الرئيسي
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # رأس الصفحة مع الشعار
        header_frame = ttk.Frame(main_frame, style='Header.TFrame', height=100)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # إضافة الشعار (نصي في حالة عدم وجود صورة)
        logo_text = "K N A Z\nلتأجير السيارات\nRENT A CAR"
        logo_label = ttk.Label(header_frame, text=logo_text, style='Title.TLabel', justify='center')
        logo_label.pack(expand=True)
        
        # الشريط الجانبي
        sidebar_frame = ttk.Frame(main_frame, style='Secondary.TFrame', width=200)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # أزرار الشريط الجانبي
        buttons_data = [
            ("تسجيل حادث جديد", self.show_add_tab),
            ("عرض الحوادث", self.show_view_tab),
            ("التقارير والإحصائيات", self.show_stats_tab),
            ("إعدادات", self.show_settings),
            ("خروج", self.exit_app)
        ]
        
        for text, command in buttons_data:
            btn = ttk.Button(sidebar_frame, text=text, command=command, style='Primary.TButton')
            btn.pack(fill='x', pady=5, padx=10)
        
        # منطقة المحتوى الرئيسي
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # عرض تبويب تسجيل الحوادث افتراضيًا
        self.show_add_tab()
    
    def show_add_tab(self):
        self.clear_content_frame()
        
        title_label = ttk.Label(self.content_frame, text="تسجيل حادث جديد", style='Subtitle.TLabel')
        title_label.pack(fill='x', pady=(0, 20))
        
        # نموذج إدخال البيانات
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(fill='both', expand=True)
        
        # الحقول الأساسية
        fields = [
            ("التاريخ:", "date_entry"),
            ("الوقت:", "time_entry"),
            ("المكان:", "location_entry"),
            ("شركة التأمين:", "insurance_entry"),
            ("رقم المطالبة:", "claim_entry"),
            ("الحالة:", "status_entry")
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=5)
            
            label = ttk.Label(frame, text=label_text, width=15, anchor='e')
            label.pack(side='left', padx=(0, 10))
            
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='left', fill='x', expand=True)
            setattr(self, var_name, entry)
        
        # وصف الحادث
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill='x', pady=5)
        
        desc_label = ttk.Label(desc_frame, text="وصف الحادث:", width=15, anchor='e')
        desc_label.pack(side='left', padx=(0, 10), anchor='n')
        
        self.desc_text = tk.Text(desc_frame, height=5, width=50)
        self.desc_text.pack(side='left', fill='x', expand=True)
        
        # الأطراف المشاركة
        parties_frame = ttk.Frame(form_frame)
        parties_frame.pack(fill='x', pady=5)
        
        parties_label = ttk.Label(parties_frame, text="الأطراف المشاركة:", width=15, anchor='e')
        parties_label.pack(side='left', padx=(0, 10), anchor='n')
        
        self.parties_text = tk.Text(parties_frame, height=3, width=50)
        self.parties_text.pack(side='left', fill='x', expand=True)
        
        # أزرار تحميل الملفات
        files_frame = ttk.Frame(form_frame)
        files_frame.pack(fill='x', pady=10)
        
        photo_btn = ttk.Button(files_frame, text="تحميل الصور", command=self.browse_photos, style='Primary.TButton')
        photo_btn.pack(side='left', padx=5)
        
        docs_btn = ttk.Button(files_frame, text="تحميل المستندات", command=self.browse_documents, style='Primary.TButton')
        docs_btn.pack(side='left', padx=5)
        
        # زر الحفظ
        save_btn = ttk.Button(form_frame, text="حفظ البيانات", command=self.add_accident, style='Primary.TButton')
        save_btn.pack(pady=20)
    
    def show_view_tab(self):
        self.clear_content_frame()
        
        title_label = ttk.Label(self.content_frame, text="عرض الحوادث المسجلة", style='Subtitle.TLabel')
        title_label.pack(fill='x', pady=(0, 20))
        
        # إطار البحث والتصفية
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text="بحث:")
        search_label.pack(side='left', padx=(0, 5))
        
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        search_btn = ttk.Button(search_frame, text="بحث", style='Primary.TButton')
        search_btn.pack(side='left')
        
        # جدول عرض البيانات
        columns = ("ID", "Date", "Location", "Insurance", "Claim", "Status")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        # تعريف العناوين
        tree.heading("ID", text="رقم")
        tree.heading("Date", text="التاريخ")
        tree.heading("Location", text="المكان")
        tree.heading("Insurance", text="شركة التأمين")
        tree.heading("Claim", text="رقم المطالبة")
        tree.heading("Status", text="الحالة")
        
        # تعريف الأعمدة
        tree.column("ID", width=50)
        tree.column("Date", width=100)
        tree.column("Location", width=150)
        tree.column("Insurance", width=150)
        tree.column("Claim", width=120)
        tree.column("Status", width=100)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # أزرار الإجراءات
        actions_frame = ttk.Frame(self.content_frame)
        actions_frame.pack(fill='x', pady=10)
        
        view_btn = ttk.Button(actions_frame, text="عرض التفاصيل", style='Primary.TButton')
        view_btn.pack(side='left', padx=5)
        
        edit_btn = ttk.Button(actions_frame, text="تعديل", style='Primary.TButton')
        edit_btn.pack(side='left', padx=5)
        
        delete_btn = ttk.Button(actions_frame, text="حذف", style='Primary.TButton')
        delete_btn.pack(side='left', padx=5)
        
        export_btn = ttk.Button(actions_frame, text="تصدير", style='Primary.TButton')
        export_btn.pack(side='left', padx=5)
    
    def show_stats_tab(self):
        self.clear_content_frame()
        
        title_label = ttk.Label(self.content_frame, text="التقارير والإحصائيات", style='Subtitle.TLabel')
        title_label.pack(fill='x', pady=(0, 20))
        
        # إضافة محتوى التقارير والإحصائيات هنا
        stats_text = """
        إحصائيات الحوادث:
        
        - إجمالي الحوادث المسجلة: 25
        - الحوادق قيد المعالجة: 8
        - المطالبات المقبولة: 12
        - المطالبات المرفوضة: 5
        
        التوزيع حسب الشهر:
        - يناير: 5 حوادث
        - فبراير: 3 حوادث
        - مارس: 7 حوادث
        - أبريل: 4 حوادث
        - مايو: 6 حوادث
        """
        
        stats_label = ttk.Label(self.content_frame, text=stats_text, justify='right')
        stats_label.pack(anchor='w', pady=10)
        
        # أزرار إنشاء التقارير
        reports_frame = ttk.Frame(self.content_frame)
        reports_frame.pack(fill='x', pady=10)
        
        monthly_btn = ttk.Button(reports_frame, text="تقرير شهري", style='Primary.TButton')
        monthly_btn.pack(side='left', padx=5)
        
        insurance_btn = ttk.Button(reports_frame, text="تقرير شركات التأمين", style='Primary.TButton')
        insurance_btn.pack(side='left', padx=5)
        
        export_btn = ttk.Button(reports_frame, text="تصدير التقارير", style='Primary.TButton')
        export_btn.pack(side='left', padx=5)
    
    def show_settings(self):
        messagebox.showinfo("الإعدادات", "سيتم تطوير هذه الوظيفة في نسخة لاحقة")
    
    def exit_app(self):
        if messagebox.askokcancel("خروج", "هل تريد حقًا الخروج من التطبيق؟"):
            self.root.destroy()
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def add_accident(self):
        # جمع البيانات من الحقول
        data = (
            self.date_entry.get(),
            self.time_entry.get(),
            self.location_entry.get(),
            self.desc_text.get("1.0", tk.END),
            self.parties_text.get("1.0", tk.END),
            self.insurance_entry.get(),
            self.claim_entry.get(),
            self.status_entry.get(),
            "",  # مسار الصور
            ""   # مسار المستندات
        )
        
        # إدخال البيانات في قاعدة البيانات
        try:
            self.c.execute('''INSERT INTO accidents 
                           (date, time, location, description, parties_involved, 
                            insurance_company, claim_number, status, photos_path, documents_path)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            self.conn.commit()
            messagebox.showinfo("نجاح", "تم حفظ بيانات الحادث بنجاح")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ البيانات: {str(e)}")
    
    def clear_form(self):
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.insurance_entry.delete(0, tk.END)
        self.claim_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.parties_text.delete("1.0", tk.END)
    
    def browse_photos(self):
        filepaths = filedialog.askopenfilenames(
            title="اختر الصور",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if filepaths:
            messagebox.showinfo("تم", f"تم اختيار {len(filepaths)} صورة")
    
    def browse_documents(self):
        filepaths = filedialog.askopenfilenames(
            title="اختر المستندات",
            filetypes=[("Document files", "*.pdf *.doc *.docx *.txt")]
        )
        if filepaths:
            messagebox.showinfo("تم", f"تم اختيار {len(filepaths)} مستند")

if __name__ == "__main__":
    root = tk.Tk()
    app = CarAccidentApp(root)
    root.mainloop()