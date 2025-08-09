        
        self.setup_ui()import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import arabic_reshaper
from bidi.algorithm import get_display

class WaterAssociationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("جمعية إكجكال للماء الصالح للشرب")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f8ff')
        
        # بيانات وهمية للأعضاء (يمكن استبدالها بقاعدة بيانات حقيقية)
        self.members_data = {
            "001": {
                "الاسم": "أحمد محمد علي",
                "اللقب": "العلوي",
                "المؤشر الجديد": "1250",
                "المؤشر القديم": "1180",
                "الاستهلاك": "70",
                "الاشتراك": "50.00",
                "الثمن": "105.00",
                "الدين": "25.00",
                "الواجب الإداري": "10.00",
                "التاريخ": "2024/12/15"
            },
            "002": {
                "الاسم": "فاطمة حسن",
                "اللقب": "الحسني",
                "المؤشر الجديد": "985",
                "المؤشر القديم": "920",
                "الاستهلاك": "65",
                "الاشتراك": "50.00",
                "الثمن": "97.50",
                "الدين": "0.00",
                "الواجب الإداري": "10.00",
                "التاريخ": "2024/12/15"
            },
            "003": {
                "الاسم": "محمد عبد الله",
                "اللقب": "المغربي",
                "المؤشر الجديد": "2100",
                "المؤشر القديم": "2005",
                "الاستهلاك": "95",
                "الاشتراك": "50.00",
                "الثمن": "142.50",
                "الدين": "75.00",
                "الواجب الإداري": "10.00",
                "التاريخ": "2024/12/15"
            }
        }
        
    def format_arabic_text(self, text):
        """تنسيق النص العربي للعرض الصحيح"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except:
            # في حالة عدم توفر المكتبات، يعرض النص كما هو
            return text
    
    def setup_ui(self):
        # العنوان الرئيسي
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text=self.format_arabic_text("جمعية إكجكال للماء الصالح للشرب"),
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # إطار إدخال رقم العضو
        input_frame = tk.Frame(self.root, bg='#f0f8ff')
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text=self.format_arabic_text("رقم العضو:"),
            font=('Arial', 16, 'bold'),
            bg='#f0f8ff'
        ).pack(side='right', padx=10)
        
        self.member_id_var = tk.StringVar()
        self.member_entry = tk.Entry(
            input_frame,
            textvariable=self.member_id_var,
            font=('Arial', 16),
            width=15,
            justify='center'
        )
        self.member_entry.pack(side='right', padx=10)
        
        search_btn = tk.Button(
            input_frame,
            text=self.format_arabic_text("بحث"),
            command=self.search_member,
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20
        )
        search_btn.pack(side='right', padx=10)
        
        # أزرار إضافة وحذف الأعضاء
        add_btn = tk.Button(
            input_frame,
            text=self.format_arabic_text("إضافة عضو"),
            command=self.add_member,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20
        )
        add_btn.pack(side='right', padx=10)
        
        remove_btn = tk.Button(
            input_frame,
            text=self.format_arabic_text("حذف عضو"),
            command=self.remove_member,
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20
        )
        remove_btn.pack(side='right', padx=10)
        
        # إطار عرض البيانات
        self.data_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.data_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # ربط مفتاح Enter بالبحث
        self.member_entry.bind('<Return>', lambda event: self.search_member())
        
        self.create_empty_form()
    
    def create_empty_form(self):
        # مسح المحتوى السابق
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        empty_label = tk.Label(
            self.data_frame,
            text=self.format_arabic_text("أدخل رقم العضو للبحث عن بياناته"),
            font=('Arial', 16),
            bg='#f0f8ff',
            fg='#7f8c8d'
        )
        empty_label.pack(expand=True)
    
    def search_member(self):
        member_id = self.member_id_var.get().strip()
        
        if not member_id:
            messagebox.showwarning(self.format_arabic_text("تحذير"), self.format_arabic_text("يرجى إدخال رقم العضو"))
            return
        
        if member_id in self.members_data:
            self.display_member_data(self.members_data[member_id])
        else:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("رقم العضو غير موجود"))
            self.create_empty_form()
    
    def display_member_data(self, member_data):
        # مسح المحتوى السابق
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # إنشاء إطار للبيانات مع حدود
        info_frame = tk.Frame(self.data_frame, bg='white', relief='ridge', bd=2)
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # عنوان البيانات
        header_label = tk.Label(
            info_frame,
            text=self.format_arabic_text("بيانات العضو"),
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        header_label.pack(pady=10)
        
        # إطار البيانات الرئيسية
        main_data_frame = tk.Frame(info_frame, bg='white')
        main_data_frame.pack(fill='x', padx=20, pady=10)
        
        # الصف الأول - الاسم واللقب
        row1_frame = tk.Frame(main_data_frame, bg='white')
        row1_frame.pack(fill='x', pady=5)
        
        self.create_data_field(row1_frame, self.format_arabic_text("الاسم:"), self.format_arabic_text(member_data["الاسم"]), 'right')
        self.create_data_field(row1_frame, self.format_arabic_text("اللقب:"), self.format_arabic_text(member_data["اللقب"]), 'left')
        
        # الصف الثاني - المؤشرات
        row2_frame = tk.Frame(main_data_frame, bg='white')
        row2_frame.pack(fill='x', pady=5)
        
        self.create_data_field(row2_frame, self.format_arabic_text("المؤشر الجديد:"), member_data["المؤشر الجديد"], 'right')
        self.create_data_field(row2_frame, self.format_arabic_text("المؤشر القديم:"), member_data["المؤشر القديم"], 'left')
        
        # الصف الثالث - الاستهلاك والاشتراك
        row3_frame = tk.Frame(main_data_frame, bg='white')
        row3_frame.pack(fill='x', pady=5)
        
        self.create_data_field(row3_frame, self.format_arabic_text("الاستهلاك:"), f"{member_data['الاستهلاك']} {self.format_arabic_text('م³')}", 'right')
        self.create_data_field(row3_frame, self.format_arabic_text("الاشتراك:"), f"{member_data['الاشتراك']} {self.format_arabic_text('درهم')}", 'left')
        
        # الصف الرابع - الثمن والدين
        row4_frame = tk.Frame(main_data_frame, bg='white')
        row4_frame.pack(fill='x', pady=5)
        
        self.create_data_field(row4_frame, self.format_arabic_text("الثمن:"), f"{member_data['الثمن']} {self.format_arabic_text('درهم')}", 'right')
        self.create_data_field(row4_frame, self.format_arabic_text("الدين:"), f"{member_data['الدين']} {self.format_arabic_text('درهم')}", 'left')
        
        # الصف الخامس - الواجب الإداري والتاريخ
        row5_frame = tk.Frame(main_data_frame, bg='white')
        row5_frame.pack(fill='x', pady=5)
        
        self.create_data_field(row5_frame, self.format_arabic_text("الواجب الإداري:"), f"{member_data['الواجب الإداري']} {self.format_arabic_text('درهم')}", 'right')
        self.create_data_field(row5_frame, self.format_arabic_text("التاريخ:"), member_data["التاريخ"], 'left')
        
        # إطار الإمضاء
        signature_frame = tk.Frame(info_frame, bg='white')
        signature_frame.pack(fill='x', padx=20, pady=20)
        
        signature_label = tk.Label(
            signature_frame,
            text=self.format_arabic_text("الإمضاء: ________________________"),
            font=('Arial', 14),
            bg='white'
        )
        signature_label.pack(anchor='e', padx=20)
        
        # حساب المجموع الكلي
        total = float(member_data["الثمن"]) + float(member_data["الدين"]) + float(member_data["الواجب الإداري"])
        
        total_frame = tk.Frame(info_frame, bg='#ecf0f1')
        total_frame.pack(fill='x', pady=10)
        
        total_label = tk.Label(
            total_frame,
            text=self.format_arabic_text(f"المجموع الكلي: {total:.2f} درهم"),
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1',
            fg='#e74c3c'
        )
        total_label.pack(pady=10)
        
        # أزرار الإجراءات
        actions_frame = tk.Frame(info_frame, bg='white')
        actions_frame.pack(fill='x', pady=10)
        
        print_btn = tk.Button(
            actions_frame,
            text=self.format_arabic_text("طباعة"),
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            command=self.print_bill
        )
        print_btn.pack(side='right', padx=10)
        
        clear_btn = tk.Button(
            actions_frame,
            text=self.format_arabic_text("مسح"),
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            command=self.clear_form
        )
        clear_btn.pack(side='right', padx=10)
    
    def create_data_field(self, parent, label_text, value_text, side):
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(side=side, fill='x', expand=True, padx=10)
        
        label = tk.Label(
            field_frame,
            text=label_text,
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        label.pack(anchor='e' if side == 'right' else 'w')
        
        value = tk.Label(
            field_frame,
            text=value_text,
            font=('Arial', 12),
            bg='#ecf0f1',
            relief='sunken',
            bd=1,
            padx=10,
            pady=5
        )
        value.pack(fill='x', pady=2)
    
    def print_bill(self):
        messagebox.showinfo(self.format_arabic_text("طباعة"), self.format_arabic_text("سيتم إرسال الفاتورة للطباعة"))
    
    def clear_form(self):
        self.member_id_var.set("")
        self.create_empty_form()
    
    def add_member(self):
        """فتح نافذة إضافة عضو جديد"""
        self.add_member_window()
    
    def remove_member(self):
        """حذف عضو موجود"""
        member_id = self.member_id_var.get().strip()
        
        if not member_id:
            messagebox.showwarning(self.format_arabic_text("تحذير"), self.format_arabic_text("يرجى إدخال رقم العضو المراد حذفه"))
            return
        
        if member_id not in self.members_data:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("رقم العضو غير موجود"))
            return
        
        # تأكيد الحذف
        member_name = self.members_data[member_id]['الاسم']
        confirm = messagebox.askyesno(
            self.format_arabic_text("تأكيد الحذف"),
            self.format_arabic_text(f"هل أنت متأكد من حذف العضو: {member_name}؟")
        )
        
        if confirm:
            del self.members_data[member_id]
            messagebox.showinfo(self.format_arabic_text("نجح الحذف"), self.format_arabic_text("تم حذف العضو بنجاح"))
            self.clear_form()
    
    def add_member_window(self):
        """نافذة إضافة عضو جديد"""
        add_window = tk.Toplevel(self.root)
        add_window.title(self.format_arabic_text("إضافة عضو جديد"))
        add_window.geometry("500x600")
        add_window.configure(bg='#f0f8ff')
        add_window.grab_set()  # جعل النافذة مودال
        
        # عنوان النافذة
        title_label = tk.Label(
            add_window,
            text=self.format_arabic_text("إضافة عضو جديد"),
            font=('Arial', 18, 'bold'),
            bg='#f0f8ff',
            fg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # إطار النموذج
        form_frame = tk.Frame(add_window, bg='white', relief='ridge', bd=2)
        form_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # متغيرات النموذج
        fields = {}
        field_names = [
            ("رقم العضو", "member_id"),
            ("الاسم", "name"), 
            ("اللقب", "surname"),
            ("المؤشر الجديد", "new_reading"),
            ("المؤشر القديم", "old_reading"),
            ("الاشتراك", "subscription"),
            ("الثمن", "price"),
            ("الدين", "debt"),
            ("الواجب الإداري", "admin_fee")
        ]
        
        for i, (label_text, field_key) in enumerate(field_names):
            # إطار كل حقل
            field_frame = tk.Frame(form_frame, bg='white')
            field_frame.pack(fill='x', padx=20, pady=8)
            
            # التسمية
            label = tk.Label(
                field_frame,
                text=self.format_arabic_text(f"{label_text}:"),
                font=('Arial', 12, 'bold'),
                bg='white',
                anchor='e',
                width=15
            )
            label.pack(side='right', padx=10)
            
            # صندوق الإدخال
            fields[field_key] = tk.StringVar()
            entry = tk.Entry(
                field_frame,
                textvariable=fields[field_key],
                font=('Arial', 12),
                width=25
            )
            entry.pack(side='right', padx=10)
            
            # قيم افتراضية لبعض الحقول
            if field_key == "subscription":
                fields[field_key].set("50.00")
            elif field_key == "debt":
                fields[field_key].set("0.00")
            elif field_key == "admin_fee":
                fields[field_key].set("10.00")
        
        # إطار الأزرار
        buttons_frame = tk.Frame(form_frame, bg='white')
        buttons_frame.pack(fill='x', pady=20)
        
        # زر الحفظ
        save_btn = tk.Button(
            buttons_frame,
            text=self.format_arabic_text("حفظ"),
            command=lambda: self.save_new_member(fields, add_window),
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=30
        )
        save_btn.pack(side='right', padx=20)
        
        # زر الإلغاء
        cancel_btn = tk.Button(
            buttons_frame,
            text=self.format_arabic_text("إلغاء"),
            command=add_window.destroy,
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=30
        )
        cancel_btn.pack(side='right', padx=20)
        
        # توسيط النافذة
        add_window.update_idletasks()
        x = (add_window.winfo_screenwidth() // 2) - (add_window.winfo_width() // 2)
        y = (add_window.winfo_screenheight() // 2) - (add_window.winfo_height() // 2)
        add_window.geometry(f"+{x}+{y}")
    
    def save_new_member(self, fields, window):
        """حفظ العضو الجديد"""
        # التحقق من البيانات
        member_id = fields['member_id'].get().strip()
        name = fields['name'].get().strip()
        surname = fields['surname'].get().strip()
        
        if not member_id:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("يرجى إدخال رقم العضو"))
            return
        
        if member_id in self.members_data:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("رقم العضو موجود مسبقاً"))
            return
        
        if not name:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("يرجى إدخال اسم العضو"))
            return
        
        if not surname:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("يرجى إدخال لقب العضو"))
            return
        
        # التحقق من القيم الرقمية
        try:
            new_reading = int(fields['new_reading'].get() or "0")
            old_reading = int(fields['old_reading'].get() or "0")
            subscription = float(fields['subscription'].get() or "50.0")
            price = float(fields['price'].get() or "0.0")
            debt = float(fields['debt'].get() or "0.0")
            admin_fee = float(fields['admin_fee'].get() or "10.0")
            
            # حساب الاستهلاك
            consumption = new_reading - old_reading
            if consumption < 0:
                messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("المؤشر الجديد يجب أن يكون أكبر من المؤشر القديم"))
                return
            
            # إذا لم يتم إدخال الثمن، احسبه تلقائياً
            if price == 0.0:
                price = subscription + (consumption * 1.5)  # سعر المتر المكعب 1.5 درهم
            
        except ValueError:
            messagebox.showerror(self.format_arabic_text("خطأ"), self.format_arabic_text("يرجى إدخال قيم رقمية صحيحة"))
            return
        
        # إنشاء بيانات العضو الجديد
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        new_member = {
            "الاسم": name,
            "اللقب": surname,
            "المؤشر الجديد": str(new_reading),
            "المؤشر القديم": str(old_reading),
            "الاستهلاك": str(consumption),
            "الاشتراك": f"{subscription:.2f}",
            "الثمن": f"{price:.2f}",
            "الدين": f"{debt:.2f}",
            "الواجب الإداري": f"{admin_fee:.2f}",
            "التاريخ": current_date
        }
        
        # إضافة العضو الجديد
        self.members_data[member_id] = new_member
        
        # رسالة نجاح
        messagebox.showinfo(
            self.format_arabic_text("نجح الحفظ"), 
            self.format_arabic_text(f"تم إضافة العضو {name} {surname} بنجاح")
        )
        
        # إغلاق النافذة وعرض بيانات العضو الجديد
        window.destroy()
        self.member_id_var.set(member_id)
        self.search_member()

def main():
    root = tk.Tk()
    app = WaterAssociationApp(root)
    
    # توسيط النافذة على الشاشة
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()