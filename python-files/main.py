from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel  # ← إصلاح الاستيراد

from تسجيل_الدخول import تحقق_الدخول
from أدوات import حفظ_السجل

class تطبيق_المحاسبة(MDApp):
    def build(self):
        self.الواجهة = Screen()

        self.اسم_المستخدم = MDTextField(
            hint_text="اسم المستخدم",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint_x=0.7
        )
        self.كلمة_المرور = MDTextField(
            hint_text="كلمة المرور",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.7
        )
        زر_الدخول = MDRaisedButton(
            text="تسجيل الدخول",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.تسجيل_الدخول
        )

        self.الواجهة.add_widget(self.اسم_المستخدم)
        self.الواجهة.add_widget(self.كلمة_المرور)
        self.الواجهة.add_widget(زر_الدخول)

        return self.الواجهة

    def تسجيل_الدخول(self, instance):
        المستخدم = self.اسم_المستخدم.text
        المرور = self.كلمة_المرور.text

        if تحقق_الدخول(المستخدم, المرور):
            حفظ_السجل(f"تم تسجيل الدخول بنجاح: {المستخدم}")
            self.اظهار_الواجهة_الرئيسية(المستخدم)
        else:
            حفظ_السجل(f"فشل تسجيل الدخول: {المستخدم}", نوع="ERROR")
            MDDialog(title="فشل الدخول", text="البيانات غير صحيحة").open()

    def اظهار_الواجهة_الرئيسية(self, المستخدم):
        الشاشة_جديدة = Screen()

        رسالة_ترحيب = MDLabel(
            text=f"مرحبًا، {المستخدم} 👋",
            halign="center",
            pos_hint={"center_y": 0.6}
        )

        زر_الخروج = MDRaisedButton(
            text="تسجيل الخروج",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.stop
        )

        الشاشة_جديدة.add_widget(رسالة_ترحيب)
        الشاشة_جديدة.add_widget(زر_الخروج)

        self.root.clear_widgets()
        self.root.add_widget(الشاشة_جديدة)

تطبيق_المحاسبة().run()

def اظهار_شاشة_العملاء(self):
    شاشة_العملاء = Screen()

    عنوان = MDLabel(
        text="📋 قائمة العملاء",
        halign="center",
        pos_hint={"center_y": 0.85},
        theme_text_color="Custom",
        text_color=(0, 0.5, 0.8, 1),
        font_style="H5"
    )

    زر_إضافة = MDRaisedButton(
        text="➕ إضافة عميل",
        pos_hint={"center_x": 0.5, "center_y": 0.6},
        on_release=lambda x: self.عرض_نافذة_إضافة_عميل()
    )

    زر_رجوع = MDRaisedButton(
        text="⬅️ رجوع",
        pos_hint={"center_x": 0.5, "center_y": 0.4},
        on_release=lambda x: self.اظهار_الواجهة_الرئيسية("العودة")
    )

    شاشة_العملاء.add_widget(عنوان)
    شاشة_العملاء.add_widget(زر_إضافة)
    شاشة_العملاء.add_widget(زر_رجوع)

    self.root.clear_widgets()
    self.root.add_widget(شاشة_العملاء)

def عرض_نافذة_إضافة_عميل(self):
    self.dialog = MDDialog(
        title="إضافة عميل جديد",
        text="(سيتم تنفيذها لاحقًا)",
        buttons=[
            MDRaisedButton(text="موافق", on_release=lambda x: self.dialog.dismiss()),
            MDRaisedButton(text="إلغاء", on_release=lambda x: self.dialog.dismiss())
        ]
    )
    self.dialog.open()

زر_العملاء = MDRaisedButton(
    text="📁 إدارة العملاء",
    pos_hint={"center_x": 0.5, "center_y": 0.5},
    on_release=lambda x: self.اظهار_شاشة_العملاء()
)
الشاشة_جديدة.add_widget(زر_العملاء)

import sqlite3

def إنشاء_قاعدة_البيانات():
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS العملاء (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            الاسم TEXT NOT NULL,
            رقم_الهاتف TEXT,
            البريد TEXT
        )
    ''')
    conn.commit()
    conn.close()

def إضافة_عميل(الاسم, رقم_الهاتف, البريد):
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO العملاء (الاسم, رقم_الهاتف, البريد) VALUES (?, ?, ?)', (الاسم, رقم_الهاتف, البريد))
    conn.commit()
    conn.close()

def استعلام_العملاء():
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM العملاء')
    النتائج = cursor.fetchall()
    conn.close()
    return النتائج

def عرض_قائمة_العملاء(self):
    العملاء = استعلام_العملاء()
    القائمة = MDList()
    for عميل in العملاء:
        عنصر = OneLineListItem(text=f"{عميل[1]} - {عميل[2]}")
        القائمة.add_widget(عنصر)
    self.root.clear_widgets()
    self.root.add_widget(القائمة)

def عرض_نافذة_إضافة_عميل(self):
    المحتوى = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
    self.حقل_الاسم = MDTextField(hint_text="اسم العميل")
    self.حقل_الهاتف = MDTextField(hint_text="رقم الهاتف")
    self.حقل_البريد = MDTextField(hint_text="البريد الإلكتروني")

    المحتوى.add_widget(self.حقل_الاسم)
    المحتوى.add_widget(self.حقل_الهاتف)
    المحتوى.add_widget(self.حقل_البريد)

    self.dialog = MDDialog(
        title="➕ إضافة عميل",
        type="custom",
        content_cls=المحتوى,
        buttons=[
            MDRaisedButton(text="حفظ", on_release=lambda x: self.حفظ_بيانات_العميل()),
            MDFlatButton(text="إلغاء", on_release=lambda x: self.dialog.dismiss())
        ]
    )
    self.dialog.open()

def حفظ_بيانات_العميل(self):
    الاسم = self.حقل_الاسم.text
    الهاتف = self.حقل_الهاتف.text
    البريد = self.حقل_البريد.text
    if الاسم.strip():
        إضافة_عميل(الاسم, الهاتف, البريد)
        self.dialog.dismiss()
        self.اظهار_شاشة_العملاء()
    else:
        print("يرجى إدخال الاسم")

def عرض_قائمة_العملاء(self):
    العملاء = استعلام_العملاء()
    القائمة = MDList()

    for عميل in العملاء:
        صندوق = MDBoxLayout(orientation="horizontal", spacing=10)
        تفاصيل = MDLabel(text=f"{عميل[1]} | {عميل[2]} | {عميل[3]}", halign="left")
        
        زر_تعديل = MDRaisedButton(text="✏️", on_release=lambda x, id=عميل[0]: self.تعديل_عميل(id))
        زر_حذف = MDRaisedButton(text="🗑️", on_release=lambda x, id=عميل[0]: self.حذف_عميل(id))

        صندوق.add_widget(تفاصيل)
        صندوق.add_widget(زر_تعديل)
        صندوق.add_widget(زر_حذف)
        القائمة.add_widget(صندوق)

    الشاشة = Screen()
    الشاشة.add_widget(القائمة)
    self.root.clear_widgets()
    self.root.add_widget(الشاشة)

def تعديل_عميل(self, معرف_العميل):
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM العملاء WHERE id = ?', (معرف_العميل,))
    العميل = cursor.fetchone()
    conn.close()

    المحتوى = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
    self.حقل_تعديل_الاسم = MDTextField(hint_text="اسم العميل", text=عميل[1])
    self.حقل_تعديل_الهاتف = MDTextField(hint_text="رقم الهاتف", text=عميل[2])
    self.حقل_تعديل_البريد = MDTextField(hint_text="البريد الإلكتروني", text=عميل[3])

    المحتوى.add_widget(self.حقل_تعديل_الاسم)
    المحتوى.add_widget(self.حقل_تعديل_الهاتف)
    المحتوى.add_widget(self.حقل_تعديل_البريد)

    self.dialog = MDDialog(
        title="✏️ تعديل العميل",
        type="custom",
        content_cls=المحتوى,
        buttons=[
            MDRaisedButton(text="حفظ", on_release=lambda x: self.حفظ_تعديل_العميل(معرف_العميل)),
            MDFlatButton(text="إلغاء", on_release=lambda x: self.dialog.dismiss())
        ]
    )
    self.dialog.open()

def حفظ_تعديل_العميل(self, معرف_العميل):
    الاسم = self.حقل_تعديل_الاسم.text
    الهاتف = self.حقل_تعديل_الهاتف.text
    البريد = self.حقل_تعديل_البريد.text

    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE العملاء
        SET الاسم = ?, رقم_الهاتف = ?, البريد = ?
        WHERE id = ?
    ''', (الاسم, الهاتف, البريد, معرف_العميل))
    conn.commit()
    conn.close()

    self.dialog.dismiss()
    self.اظهار_شاشة_العملاء()

def حذف_عميل(self, معرف_العميل):
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM العملاء WHERE id = ?', (معرف_العميل,))
    conn.commit()
    conn.close()
    self.اظهار_شاشة_العملاء()

self.حقل_بحث = MDTextField(
    hint_text="🔍 ابحث باسم أو رقم الهاتف",
    pos_hint={"center_x": 0.5, "center_y": 0.9},
    size_hint_x=0.8,
    on_text_validate=self.تشغيل_البحث
)

def بحث_عن_عميل(كلمة_بحث):
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    query = '''
        SELECT * FROM العملاء
        WHERE الاسم LIKE ? OR رقم_الهاتف LIKE ?
    '''
    like_pattern = f'%{كلمة_بحث}%'
    cursor.execute(query, (like_pattern, like_pattern))
    النتائج = cursor.fetchall()
    conn.close()
    return النتائج
def تشغيل_البحث(self, instance):
    كلمة_بحث = self.حقل_بحث.text
    نتائج = بحث_عن_عميل(كلمة_بحث)
    self.عرض_نتائج_البحث(نتائج)

def عرض_تفاصيل_العميل(self, معرف_العميل):
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()

    # بيانات العميل
    cursor.execute('SELECT * FROM العملاء WHERE id = ?', (معرف_العميل,))
    العميل = cursor.fetchone()

    # الفواتير والمشتريات
    cursor.execute('SELECT التاريخ, المبلغ FROM الفواتير WHERE معرف_العميل = ?', (معرف_العميل,))
    الفواتير = cursor.fetchall()

    cursor.execute('SELECT المنتج, الكمية, السعر FROM المشتريات WHERE معرف_العميل = ?', (معرف_العميل,))
    المشتريات = cursor.fetchall()

    conn.close()

    # إنشاء الشاشة
    شاشة = Screen()

    شاشة.add_widget(MDLabel(
        text=f"📇 العميل: {عميل[1]}",
        halign="center",
        font_style="H5",
        theme_text_color="Custom",
        text_color=(0.1, 0.3, 0.6, 1),
        pos_hint={"center_y": 0.9}
    ))

    شاشة.add_widget(MDLabel(
        text=f"📞 الهاتف: {عميل[2]} | ✉️ البريد: {عميل[3]}",
        halign="center",
        pos_hint={"center_y": 0.8}
    ))

    # قسم الفواتير
    شاشة.add_widget(MDLabel(text="🧾 الفواتير:", halign="center"))
    for فاتورة in الفواتير:
        شاشة.add_widget(MDLabel(text=f"التاريخ: {فاتورة[0]}, المبلغ: {فاتورة[1]} ريال"))

    # قسم المشتريات
    شاشة.add_widget(MDLabel(text="🛒 المشتريات:", halign="center"))
    for عملية in المشتريات:
        شاشة.add_widget(MDLabel(text=f"{عملية[0]} × {عملية[1]} = {عملية[2]} ريال"))

    # زر العودة
    زر_رجوع = MDRaisedButton(
        text="⬅️ رجوع",
        pos_hint={"center_x": 0.5, "center_y": 0.1},
        on_release=lambda x: self.اظهار_شاشة_العملاء()
    )
    شاشة.add_widget(زر_رجوع)

    self.root.clear_widgets()
    self.root.add_widget(شاشة)

    conn.close()

    # إنشاء الشاشة
    شاشة = Screen()

    شاشة.add_widget(MDLabel(
        text=f"📇 العميل: {عميل[1]}",
        halign="center",
        font_style="H5",
        theme_text_color="Custom",
        text_color=(0.1, 0.3, 0.6, 1),
        pos_hint={"center_y": 0.9}
    ))

    شاشة.add_widget(MDLabel(
        text=f"📞 الهاتف: {عميل[2]} | ✉️ البريد: {عميل[3]}",
        halign="center",
        pos_hint={"center_y": 0.8}
    ))

    # قسم الفواتير
    شاشة.add_widget(MDLabel(text="🧾 الفواتير:", halign="center"))
    for فاتورة in الفواتير:
        شاشة.add_widget(MDLabel(text=f"التاريخ: {فاتورة[0]}, المبلغ: {فاتورة[1]} ريال"))

    # قسم المشتريات
    شاشة.add_widget(MDLabel(text="🛒 المشتريات:", halign="center"))
    for عملية in المشتريات:
        شاشة.add_widget(MDLabel(text=f"{عملية[0]} × {عملية[1]} = {عملية[2]} ريال"))

    # زر العودة
    زر_رجوع = MDRaisedButton(
        text="⬅️ رجوع",
        pos_hint={"center_x": 0.5, "center_y": 0.1},
        on_release=lambda x: self.اظهار_شاشة_العملاء()
    )
    شاشة.add_widget(زر_رجوع)

    self.root.clear_widgets()
    self.root.add_widget(شاشة)

    conn.close()

    شاشة = Screen()

    عنوان = MDLabel(
        text=f"📇 تفاصيل العميل: {عميل[1]}",
        halign="center",
        theme_text_color="Custom",
        text_color=(0.1, 0.3, 0.6, 1),
        font_style="H5",
        pos_hint={"center_y": 0.85}
    )

    تفاصيل = MDLabel(
        text=f"""
رقم الهاتف: {عميل[2]}
البريد الإلكتروني: {عميل[3]}
رقم العميل: {عميل[0]}
        """,
        halign="center",
        pos_hint={"center_y": 0.6}
    )

    زر_رجوع = MDRaisedButton(
        text="⬅️ رجوع",
        pos_hint={"center_x": 0.5, "center_y": 0.3},
        on_release=lambda x: self.اظهار_شاشة_العملاء()
    )

    شاشة.add_widget(عنوان)
    شاشة.add_widget(تفاصيل)
    شاشة.add_widget(زر_رجوع)

    self.root.clear_widgets()
    self.root.add_widget(شاشة)

عنصر = OneLineListItem(
    text=f"{عميل[1]} - {عميل[2]}",
    on_release=lambda x, id=عميل[0]: self.عرض_تفاصيل_العميل(id)
)

def إنشاء_جداول_إضافية():
    conn = sqlite3.connect('العملاء.db')
    cursor = conn.cursor()
    
    # جدول الفواتير
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS الفواتير (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            معرف_العميل INTEGER,
            التاريخ TEXT,
            المبلغ REAL,
            FOREIGN KEY (معرف_العميل) REFERENCES العملاء(id)
        )
    ''')

    # جدول المشتريات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS المشتريات (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            معرف_العميل INTEGER,
            المنتج TEXT,
            الكمية INTEGER,
            السعر REAL,
            FOREIGN KEY (معرف_العميل) REFERENCES العملاء(id)
        )
    ''')

    conn.commit()
    conn.close()

def حذف_التكرار_من_القائمة(قائمة):
    return list(set(قائمة))
def حذف_التكرار_مع_ترتيب(قائمة):
    نتيجة = []
    for عنصر in قائمة:
        if عنصر not in نتيجة:
            نتيجة.append(عنصر)
    return نتيجة
def حذف_التكرار(قائمة):
    جديدة = []
    for عنصر in قائمة:
        if عنصر not in جديدة:
            جديدة.append(عنصر)
    return جديدة

المشتريات = [
    ("تفاح", 2, 5),
    ("موز", 1, 3),
    ("تفاح", 2, 5),
    ("برتقال", 3, 4),
    ("موز", 1, 3)
]

# حذف التكرار
المشتريات_بدون_تكرار = حذف_التكرار(المشتريات)

# تنسيق جدولي + حساب الإجمالي
إجمالي = 0

print("—" * 40)
print(f"{'المنتج':<10}{'الكمية':<10}{'السعر':<10}{'الإجمالي':<10}")
print("—" * 40)

for عملية in المشتريات_بدون_تكرار:
    المنتج, الكمية, السعر = عملية
    المجموع = الكمية * السعر
    إجمالي += المجموع
    print(f"{المنتج:<10}{الكمية:<10}{السعر:<10}{المجموع:<10}")

print("—" * 40)
print(f"{'إجمالي الكل':<30}{إجمالي} ريال")
print("—" * 40)

# قائمة المخزون
المخزون = {
    "تفاح": {"الكمية": 10, "السعر": 5},
    "موز": {"الكمية": 15, "السعر": 3},
    "برتقال": {"الكمية": 8, "السعر": 4}
}

# سجل العمليات (مشتريات / مبيعات)
السجل = []

# عملية تحديث المخزون
def تحديث_المخزون(المنتج, الكمية, نوع):
    if المنتج in المخزون:
        if نوع == "شراء":
            المخزون[المنتج]["الكمية"] += الكمية
        elif نوع == "بيع":
            المخزون[المنتج]["الكمية"] -= الكمية
        السجل.append((المنتج, الكمية, نوع))

# عرض قائمة منسدلة للمستخدم
def عرض_القائمة_المنسدلة():
    print("اختر المنتج:")
    for i, اسم in enumerate(mخزون.keys(), 1):
        print(f"{i}. {اسم}")

# طباعة تقرير المخزون
def طباعة_المخزون():
    print("—" * 40)
    print(f"{'المنتج':<10}{'الكمية':<10}{'السعر':<10}")
    print("—" * 40)
    for منتج, بيانات in المخزون.items():
        print(f"{منتج:<10}{بيانات['الكمية']:<10}{بيانات['السعر']:<10}")
    print("—" * 40)

# تنفيذ مثال
تحديث_المخزون("تفاح", 2, "شراء")
تحديث_المخزون("موز", 3, "بيع")
عرض_القائمة_المنسدلة()
طباعة_المخزون()

import tkinter as tk
from tkinter import ttk

المخزون = {
    "تفاح": {"الكمية": 10, "السعر": 5},
    "موز": {"الكمية": 15, "السعر": 3},
    "برتقال": {"الكمية": 8, "السعر": 4}
}

السجل = []

def تحديث_المخزون():
    المنتج = اسم_المنتج.get()
    الكمية = int(كمية_المنتج.get())
    نوع = نوع_العملية.get()

    if المنتج in المخزون:
        if نوع == "شراء":
            المخزون[المنتج]["الكمية"] += الكمية
        elif نوع == "بيع":
            المخزون[المنتج]["الكمية"] -= الكمية
        السجل.append((المنتج, الكمية, نوع))

    تحديث_الجدول()

def تحديث_الجدول():
    for صف in الجدول.get_children():
        الجدول.delete(صف)
    for منتج, بيانات in المخزون.items():
        الجدول.insert("", "end", values=(منتج, بيانات["الكمية"], بيانات["السعر"]))

نافذة = tk.Tk()
نافذة.title("إدارة المخزون")

اسم_المنتج = ttk.Combobox(نافذة, values=list(المخزون.keys()))
كمية_المنتج = tk.Entry(نافذة)
نوع_العملية = ttk.Combobox(نافذة, values=["شراء", "بيع"])
زر_تنفيذ = tk.Button(نافذة, text="تنفيذ", command=تحديث_المخزون)

اسم_المنتج.grid(row=0, column=0)
كمية_المنتج.grid(row=0, column=1)
نوع_العملية.grid(row=0, column=2)
زر_تنفيذ.grid(row=0, column=3)

الجدول = ttk.Treeview(نافذة, columns=("المنتج", "الكمية", "السعر"), show="headings")
for اسم in ["المنتج", "الكمية", "السعر"]:
    الجدول.heading(اسم, text=اسم)
الجدول.grid(row=1, column=0, columnspan=4)

تحديث_الجدول()
نافذة.mainloop()

from datetime import datetime
import csv

# بيانات المخزون والسجل
المخزون = {
    "تفاح": {"الكمية": 10, "السعر": 5},
    "موز": {"الكمية": 15, "السعر": 3},
    "برتقال": {"الكمية": 8, "السعر": 4}
}
السجل = []

# تحديث المخزون
def تحديث_المخزون(المنتج, الكمية, نوع):
    if المنتج in المخزون:
        if نوع == "شراء":
            المخزون[المنتج]["الكمية"] += الكمية
        elif نوع == "بيع":
            المخزون[المنتج]["الكمية"] -= الكمية
        السجل.append((المنتج, الكمية, نوع))

# حفظ الملف باسم تلقائي
def حفظ_السجل_في_CSV():
    الآن = datetime.now()
    اسم_الملف = f"سجل_المخزون_{الآن.strftime('%Y_%m_%d_%H%M')}.csv"
    with open(اسم_الملف, mode='w', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow(["المنتج", "الكمية", "العملية"])
        for عملية in السجل:
            writer.writerow(عملية)
    print(f"✅ تم حفظ الملف باسم: {اسم_الملف}")

# طباعة حالة المخزون
def طباعة_المخزون():
    print("—" * 40)
    print(f"{'المنتج':<10}{'الكمية':<10}{'السعر':<10}")
    print("—" * 40)
    for منتج, بيانات in المخزون.items():
        print(f"{منتج:<10}{بيانات['الكمية']:<10}{بيانات['السعر']:<10}")
    print("—" * 40)

# 📌 نقطة البداية
if __name__ == "__main__":
    تحديث_المخزون("تفاح", 2, "شراء")
    تحديث_المخزون("موز", 3, "بيع")
    طباعة_المخزون()
    حفظ_السجل_في_CSV()

from datetime import datetime
import csv

المخزون = {
    "تفاح": {"الكمية": 10, "السعر": 5},
    "موز": {"الكمية": 15, "السعر": 3},
    "برتقال": {"الكمية": 8, "السعر": 4}
}
السجل = []

def تحديث_المخزون(المنتج, الكمية, نوع):
    try:
        if المنتج in المخزون:
            if نوع == "شراء":
                المخزون[المنتج]["الكمية"] += الكمية
            elif نوع == "بيع":
                المخزون[المنتج]["الكمية"] -= الكمية
            else:
                raise ValueError("⚠️ نوع العملية غير معروف")
            السجل.append((المنتج, الكمية, نوع))
        else:
            raise KeyError("❌ المنتج غير موجود في المخزون")
    except Exception as e:
        تسجيل_الخطأ(e)

def تسجيل_الخطأ(الخطأ):
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("سجل_الأخطاء.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])
    print(f"🚨 خطأ تم تسجيله: {الخطأ}")

def حفظ_السجل_في_CSV():
    الآن = datetime.now()
    اسم_الملف = f"سجل_المخزون_{الآن.strftime('%Y_%m_%d_%H%M')}.csv"
    with open(اسم_الملف, mode='w', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow(["المنتج", "الكمية", "العملية"])
        for عملية in السجل:
            writer.writerow(عملية)
    print(f"✅ تم حفظ الملف باسم: {اسم_الملف}")

# نقطة البداية
if __name__ == "__main__":
    # تجربة خطأ متعمّد لاختبار النظام
    تحديث_المخزون("أناناس", 5, "شراء")
    تحديث_المخزون("تفاح", 2, "بيع")
    تحديث_المخزون("موز", 3, "استرجاع")
    حفظ_السجل_في_CSV()

from datetime import datetime
import csv

المخزون = {
    "تفاح": {"الكمية": 10, "السعر": 5},
    "موز": {"الكمية": 15, "السعر": 3},
    "برتقال": {"الكمية": 8, "السعر": 4}
}
السجل = []

def تحديث_المخزون(المنتج, الكمية, نوع):
    try:
        if المنتج in المخزون:
            if نوع == "شراء":
                المخزون[المنتج]["الكمية"] += الكمية
            elif نوع == "بيع":
                المخزون[المنتج]["الكمية"] -= الكمية
            else:
                raise ValueError("⚠️ نوع العملية غير معروف")
            السجل.append((المنتج, الكمية, نوع))
        else:
            raise KeyError("❌ المنتج غير موجود في المخزون")
    except Exception as e:
        تسجيل_الخطأ(e)

def تسجيل_الخطأ(الخطأ):
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("سجل_الأخطاء.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])
    print(f"🚨 خطأ تم تسجيله: {الخطأ}")

def حفظ_السجل_في_CSV():
    الآن = datetime.now()
    اسم_الملف = f"سجل_المخزون_{الآن.strftime('%Y_%m_%d_%H%M')}.csv"
    with open(اسم_الملف, mode='w', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow(["المنتج", "الكمية", "العملية"])
        for عملية in السجل:
            writer.writerow(عملية)
    print(f"✅ تم حفظ الملف باسم: {اسم_الملف}")

# نقطة البداية
if __name__ == "__main__":
    # تجربة خطأ متعمّد لاختبار النظام
    تحديث_المخزون("أناناس", 5, "شراء")
    تحديث_المخزون("تفاح", 2, "بيع")
    تحديث_المخزون("موز", 3, "استرجاع")
    حفظ_السجل_في_CSV()

from tkinter import messagebox
import traceback

def تسجيل_الخطأ_المنبثق(الخطأ):
    # تسجيل في ملف
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("سجل_الأخطاء.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])

    # تنبيه منبثق
    رسالة = f"حدث خطأ أثناء التشغيل:\n{الخطأ}"
    messagebox.showerror("🚨 تنبيه خطأ", رسالة)import tkinter as tk
from datetime import datetime
import csv

def تسجيل_الخطأ_داخل_الواجهة(الواجهة, مربع_الخطأ, الخطأ):
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # حفظ في ملف الأخطاء
    with open("سجل_الأخطاء.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])
    
    # عرض الخطأ داخل مربع النص
    مربع_الخطأ.config(state='normal')  # فك الحماية
    مربع_الخطأ.delete(1.0, tk.END)     # حذف النص السابق
    مربع_الخطأ.insert(tk.END, f"🚨 حدث خطأ:\n{الخطأ}")
    مربع_الخطأ.config(state='disabled')  # إعادة الحماية

def تنفيذ_العملية():
    try:
        نوع = "استرجاع"
        if نوع not in ["شراء", "بيع"]:
            raise ValueError(f"⚠️ نوع العملية '{نوع}' غير مدعوم")
    except Exception as e:
        تسجيل_الخطأ_داخل_الواجهة(نافذة, مربع_الخطأ, e)

# إنشاء الواجهة
نافذة = tk.Tk()
نافذة.title("نظام عرض الخطأ داخل التطبيق")

زر_تنفيذ = tk.Button(نافذة, text="تنفيذ العملية", command=تنفيذ_العملية)
زر_تنفيذ.pack(pady=10)

# مربع خاص لعرض الخطأ
مربع_الخطأ = tk.Text(نافذة, height=5, width=50, fg='red', font=('Arial', 12))
مربع_الخطأ.pack()
مربع_الخطأ.config(state='disabled')  # حماية الكتابة

نافذة.mainloop()

import tkinter as tk
from datetime import datetime
import csv

# تسجيل الخطأ داخل قائمة الأخطاء
def تسجيل_الخطأ_في_القائمة(القائمة, الخطأ):
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # حفظ في ملف CSV
    with open("سجل_الأخطاء.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])
    
    # إضافة الخطأ إلى القائمة
    القائمة.insert(tk.END, f"[{الآن}] {الخطأ}")

def تنفيذ_العملية():
    try:
        نوع = "استرجاع"
        if نوع not in ["شراء", "بيع"]:
            raise ValueError(f"⚠️ نوع العملية '{نوع}' غير مدعوم")
    except Exception as e:
        تسجيل_الخطأ_في_القائمة(قائمة_الأخطاء, e)

# واجهة التطبيق
نافذة = tk.Tk()
نافذة.title("نظام إدارة الأخطاء")

زر_تنفيذ = tk.Button(نافذة, text="تنفيذ العملية", command=تنفيذ_العملية)
زر_تنفيذ.pack(pady=10)

# إطار يحتوي على القائمة وشريط التمرير
إطار = tk.Frame(نافذة)
إطار.pack()

# قائمة الأخطاء
قائمة_الأخطاء = tk.Listbox(إطار, width=80, height=10, font=('Arial', 12), fg='red')
قائمة_الأخطاء.pack(side=tk.LEFT, fill=tk.BOTH)

# شريط تمرير مرتبط بالقائمة
شريط = tk.Scrollbar(إطار)
شريط.pack(side=tk.RIGHT, fill=tk.Y)
قائمة_الأخطاء.config(yscrollcommand=شريط.set)
شريط.config(command=قائمة_الأخطاء.yview)

نافذة.mainloop()

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import csv

# تسجيل الخطأ داخل القائمة
def تسجيل_الخطأ_في_القائمة(القائمة, الخطأ, سجل):
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    النص = f"[{الآن}] {الخطأ}"
    القائمة.insert(tk.END, النص)

    # حفظ في ملف CSV
    with open(sجل, mode='a', encoding='utf-8-sig', newline='') as ملف:
        writer = csv.writer(ملف)
        writer.writerow([الآن, str(الخطأ)])

# عرض تفاصيل الخطأ عند الضغط
def عرض_التفاصيل(event):
    المختار = قائمة_الأخطاء.curselection()
    if المختار:
        النص = قائمة_الأخطاء.get(المختار)
        messagebox.showinfo("تفاصيل الخطأ", النص)

# زر لمسح كل الأخطاء
def مسح_القائمة():
    قائمة_الأخطاء.delete(0, tk.END)

def تنفيذ_العملية():
    try:
        نوع = "استرجاع"
        if نوع not in ["شراء", "بيع"]:
            raise ValueError(f"⚠️ نوع العملية '{نوع}' غير مدعوم")
    except Exception as e:
        تسجيل_الخطأ_في_القائمة(قائمة_الأخطاء, e, "سجل_الأخطاء.csv")

# واجهة المستخدم
نافذة = tk.Tk()
نافذة.title("📋 مدير الأخطاء التفاعلي")

زر_تنفيذ = tk.Button(نافذة, text="تنفيذ العملية", command=تنفيذ_العملية)
زر_تنفيذ.pack(pady=10)

# الإطار الذي يحتوي على القائمة وشريط التمرير
إطار = tk.Frame(نافذة)
إطار.pack()

قائمة_الأخطاء = tk.Listbox(إطار, width=80, height=10, font=('Arial', 12), fg='red')
قائمة_الأخطاء.pack(side=tk.LEFT, fill=tk.BOTH)

شريط = tk.Scrollbar(إطار)
شريط.pack(side=tk.RIGHT, fill=tk.Y)
قائمة_الأخطاء.config(yscrollcommand=شريط.set)
شريط.config(command=قائمة_الأخطاء.yview)

# ربط الضغط على عنصر بالقائمة
قائمة_الأخطاء.bind('<<ListboxSelect>>', عرض_التفاصيل)

زر_مسح = tk.Button(نافذة, text="🧹 مسح جميع الأخطاء", command=مسح_القائمة)
زر_مسح.pack(pady=10)

نافذة.mainloop()

import tkinter as tk
from tkinter import messagebox

# دالة لإضافة مرتجع
def إضافة_مرتجع():
    العنصر = إدخال_المرتجع.get()
    if العنصر:
        قائمة_المرتجعات.insert(tk.END, العنصر)
        إدخال_المرتجع.delete(0, tk.END)
    else:
        messagebox.showwarning("تنبيه", "يرجى إدخال اسم المرتجع أولًا!")

# دالة لحذف المرتجع المختار
def حذف_المرتجع():
    مختار = قائمة_المرتجعات.curselection()
    if مختار:
        قائمة_المرتجعات.delete(مختار)
    else:
        messagebox.showinfo("معلومة", "اختر مرتجعًا للحذف.")

# دالة لعرض تفاصيل المرتجع
def عرض_التفاصيل(event):
    مختار = قائمة_المرتجعات.curselection()
    if مختار:
        اسم = قائمة_المرتجعات.get(مختار)
        messagebox.showinfo("تفاصيل المرتجع", f"المرتجع المختار:\n{اسم}")

# الواجهة
نافذة = tk.Tk()
نافذة.title("📝 قائمة المرتجعات")

# مدخل الإدخال
إدخال_المرتجع = tk.Entry(نافذة, font=('Arial', 12), width=40)
إدخال_المرتجع.pack(pady=5)

# زر الإضافة
زر_إضافة = tk.Button(نافذة, text="➕ إضافة مرتجع", command=إضافة_مرتجع)
زر_إضافة.pack(pady=5)

# القائمة
قائمة_المرتجعات = tk.Listbox(نافذة, width=50, height=10, font=('Arial', 12))
قائمة_المرتجعات.pack(pady=10)

# ربط الضغط على عنصر لعرض التفاصيل
قائمة_المرتجعات.bind('<<ListboxSelect>>', عرض_التفاصيل)

# زر الحذف
زر_حذف = tk.Button(نافذة, text="🗑️ حذف المرتجع", command=حذف_المرتجع)
زر_حذف.pack(pady=5)

نافذة.mainloop()
import tkinter as tk
from datetime import datetime
import csv

المرتجعات_الكاملة = []

def إضافة_مرتجع():
    الاسم = إدخال_الاسم.get()
    النوع = اختيار_النوع.get()
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M')

    if الاسم:
        نص = f"{الاسم} | النوع: {النوع} | التاريخ: {الآن}"
        المرتجعات_الكاملة.append((الاسم, النوع, الآن))
        تحديث_القائمة(النوع_المحدد.get())

        with open("المرتجعات.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
            writer = csv.writer(ملف)
            writer.writerow([الاسم, النوع, الآن])

        إدخال_الاسم.delete(0, tk.END)

def تحديث_القائمة(نوع_مطلوب):
    قائمة_العرض.delete(0, tk.END)
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        if نوع_مطلوب == "الكل" or نوع == نوع_مطلوب:
            قائمة_العرض.insert(tk.END, f"{اسم} | النوع: {نوع} | التاريخ: {وقت}")

def حذف_المختار():
    مختار = قائمة_العرض.curselection()
    if مختار:
        النص = قائمة_العرض.get(مختار)
        قائمة_العرض.delete(مختار)
        # إزالة من المرتجعات_الكاملة
        المرتجعات_الكاملة[:] = [r for r in المرتجعات_الكاملة if f"{r[0]} | النوع: {r[1]} | التاريخ: {r[2]}" != النص]

def تصفية_حسب_النوع(_):
    تحديث_القائمة(نوع_المحدد.get())

# إنشاء الواجهة
نافذة = tk.Tk()
نافذة.title("🌟 مدير المرتجعات الاحترافي")

tk.Label(نافذة, text="📦 اسم المرتجع").pack()
إدخال_الاسم = tk.Entry(نافذة, font=('Arial', 12), width=40)
إدخال_الاسم.pack(pady=5)

tk.Label(نافذة, text="🛒 نوع المنتج").pack()
الأنواع = ["إلكترونيات", "ملابس", "أغذية", "أدوات مكتبية"]
اختيار_النوع = tk.StringVar(value=الأنواع[0])
قائمة_الأنواع = tk.OptionMenu(نافذة, اختيار_النوع, *الأنواع)
قائمة_الأنواع.pack(pady=5)

tk.Button(نافذة, text="➕ إضافة المرتجع", command=إضافة_مرتجع).pack(pady=5)

# تصفية حسب النوع
tk.Label(نافذة, text="🔍 تصفية حسب النوع").pack()
نوع_المحدد = tk.StringVar(value="الكل")
قائمة_تصفية = tk.OptionMenu(نافذة, نوع_المحدد, "الكل", *الأنواع, command=تصفية_حسب_النوع)
قائمة_تصفية.pack(pady=5)

# قائمة العرض
قائمة_العرض = tk.Listbox(نافذة, width=60, height=10, font=('Arial', 12))
قائمة_العرض.pack(pady=10)

# زر حذف المختار
tk.Button(نافذة, text="🗑️ حذف المرتجع المختار", command=حذف_المختار).pack(pady=5)

نافذة.mainloop()
def البحث_بالاسم():
    مفتاح = مربع_البحث.get().lower()
    قائمة_العرض.delete(0, tk.END)
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        if مفتاح in اسم.lower():
            قائمة_العرض.insert(tk.END, f"{اسم} | النوع: {نوع} | التاريخ: {وقت}")

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def تصدير_PDF():
    doc = SimpleDocTemplate("المرتجعات.pdf")
    ستايل = getSampleStyleSheet()
    عناصر = []

    عناصر.append(Paragraph("📋 قائمة المرتجعات", ستايل['Title']))
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        عناصر.append(Paragraph(f"- {اسم} | النوع: {نوع} | التاريخ: {وقت}", ستايل['Normal']))

    doc.build(عناصر)
    messagebox.showinfo("✅ تم", "تم تصدير المرتجعات إلى ملف PDF بنجاح!")

from collections import Counter

def عرض_الإحصائيات():
    العد = Counter([نوع for _, نوع, _ in المرتجعات_الكاملة])
    رسائل = [f"{نوع}: {عدد}" for نوع, عدد in العد.items()]
    نص = "\n".join(رسائل)
    messagebox.showinfo("📊 إحصائيات المرتجعات", نص)

# مربع البحث
tk.Label(نافذة, text="🔎 بحث حسب الاسم").pack()
مربع_البحث = tk.Entry(نافذة, font=('Arial', 12), width=30)
مربع_البحث.pack(pady=5)
tk.Button(نافذة, text="🔍 بحث", command=البحث_بالاسم).pack()

# tk.Button(نافذة, text="🔍 بحث ضمن النوع المحدد", command=البحث_بالاسم_داخل_النوع).pack(pady=5)


# زر الإحصائيات
tk.Button(نافذة, text="📊 عرض إحصائيات المرتجعات", command=عرض_الإحصائيات).pack(pady=5)

tk.Button(نافذة, text="📋 نسخ المرتجع إلى الحافظة", command=نسخ_إلى_الحافظة).pack(pady=5)📁 icons/
    ➤ add.png
    ➤ delete.png
    ➤ search.png
    ➤ pdf.png
    ➤ stats.png
    ➤ copy.png

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkinter import PhotoImage
import csv
from collections import Counter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

المرتجعات_الكاملة = []

def إضافة_مرتجع():
    الاسم = إدخال_الاسم.get()
    النوع = اختيار_النوع.get()
    الآن = datetime.now().strftime('%Y-%m-%d %H:%M')

    if الاسم:
        المرتجعات_الكاملة.append((الاسم, النوع, الآن))
        تحديث_القائمة(نوع_المحدد.get())
        إدخال_الاسم.delete(0, tk.END)

        with open("المرتجعات.csv", mode='a', encoding='utf-8-sig', newline='') as ملف:
            writer = csv.writer(ملف)
            writer.writerow([الاسم, النوع, الآن])
    else:
        messagebox.showwarning("⚠️", "يرجى إدخال اسم المرتجع!")

def تحديث_القائمة(نوع_مطلوب):
    قائمة_العرض.delete(0, tk.END)
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        if نوع_مطلوب == "الكل" or نوع == نوع_مطلوب:
            قائمة_العرض.insert(tk.END, f"{اسم} | النوع: {نوع} | التاريخ: {وقت}")

def تصفية_حسب_النوع(_):
    تحديث_القائمة(نوع_المحدد.get())

def حذف_المختار():
    مختار = قائمة_العرض.curselection()
    if مختار:
        النص = قائمة_العرض.get(mختار)
        قائمة_العرض.delete(mختار)
        المرتجعات_الكاملة[:] = [r for r in المرتجعات_الكاملة if f"{r[0]} | النوع: {r[1]} | التاريخ: {r[2]}" != النص]

def نسخ_إلى_الحافظة():
    مختار = قائمة_العرض.curselection()
    if مختار:
        النص = قائمة_العرض.get(mختار)
        نافذة.clipboard_clear()
        نافذة.clipboard_append(النص)
        messagebox.showinfo("✅ تم النسخ", "تم نسخ المرتجع إلى الحافظة.")

def البحث_بالاسم_داخل_النوع():
    مفتاح = مربع_البحث.get().lower()
    نوع_مطلوب = نوع_المحدد.get()
    قائمة_العرض.delete(0, tk.END)
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        if (نوع_مطلوب == "الكل" or نوع == نوع_مطلوب) and (مفتاح in اسم.lower()):
            قائمة_العرض.insert(tk.END, f"{اسم} | النوع: {نوع} | التاريخ: {وقت}")

def تصدير_PDF():
    doc = SimpleDocTemplate("المرتجعات.pdf")
    ستايل = getSampleStyleSheet()
    عناصر = [Paragraph("📋 قائمة المرتجعات", ستايل['Title'])]
    for اسم, نوع, وقت in المرتجعات_الكاملة:
        عناصر.append(Paragraph(f"- {اسم} | النوع: {نوع} | التاريخ: {وقت}", ستايل['Normal']))
    doc.build(عناصر)
    messagebox.showinfo("✅ تم", "تم تصدير المرتجعات إلى ملف PDF.")

def عرض_الإحصائيات():
    العد = Counter([نوع for _, نوع, _ in المرتجعات_الكاملة])
    نص = "\n".join([f"{نوع}: {عدد}" for نوع, عدد in العد.items()])
    messagebox.showinfo("📊 إحصائيات المرتجعات", نص)

# الواجهة
نافذة = tk.Tk()
نافذة.title("🎯 مدير المرتجعات المتطور")

# تحميل الصور
أيقونة_إضافة = PhotoImage(file="icons/add.png")
أيقونة_بحث = PhotoImage(file="icons/search.png")
أيقونة_نسخ = PhotoImage(file="icons/copy.png")
أيقونة_PDF = PhotoImage(file="icons/pdf.png")
أيقونة_حذف = PhotoImage(file="icons/delete.png")
أيقونة_إحصاء = PhotoImage(file="icons/stats.png")

# إدخال الاسم
tk.Label(نافذة, text="📦 اسم المرتجع").grid(row=0, column=0, padx=5, pady=5)
إدخال_الاسم = tk.Entry(نافذة, font=('Arial', 12), width=30)
إدخال_الاسم.grid(row=0, column=1, columnspan=2, padx=5)

# اختيار النوع
tk.Label(نافذة, text="🛒 نوع المنتج").grid(row=1, column=0)
الأنواع = ["إلكترونيات", "ملابس", "أغذية", "أدوات مكتبية"]
اختيار_النوع = tk.StringVar(value=الأنواع[0])
tk.OptionMenu(نافذة, اختيار_النوع, *الأنواع).grid(row=1, column=1)

# إضافة
tk.Button(نافذة, text="إضافة", image=أيقونة_إضافة, compound=tk.LEFT, command=إضافة_مرتجع).grid(row=1, column=2)

# مربع البحث
tk.Label(نافذة, text="🔎 بحث حسب الاسم").grid(row=2, column=0)
مربع_البحث = tk.Entry(نافذة, font=('Arial', 12), width=20)
مربع_البحث.grid(row=2, column=1)
tk.Button(نافذة, text="بحث", image=أيقونة_بحث, compound=tk.LEFT, command=البحث_بالاسم_داخل_النوع).grid(row=2, column=2)

# تصفية
tk.Label(نافذة, text="🔍 نوع لتصفية").grid(row=3, column=0)
نوع_المحدد = tk.StringVar(value="الكل")
tk.OptionMenu(نافذة, نوع_المحدد, "الكل", *الأنواع, command=تصفية_حسب_النوع).grid(row=3, column=1)

# القائمة
قائمة_العرض = tk.Listbox(نافذة, width=70, height=10, font=('Arial', 12))
قائمة_العرض.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# أزرار إضافية
tk.Button(نافذة, text="نسخ", image=أيقونة_نسخ, compound=tk.LEFT, command=نسخ_إلى_الحافظة).grid(row=5, column=0)
tk.Button(نافذة, text="حذف", image=أيقونة_حذف, compound=tk.LEFT, command=حذف_المختار).grid(row=5, column=1)
tk.Button(نافذة, text="PDF", image=أيقونة_PDF, compound=tk.LEFT, command=تصدير_PDF).grid(row=5, column=2)

tk.Button(نافذة, text="إحصائيات", image=أيقونة_إحصاء, compound=tk.LEFT, command=عرض_الإحصائيات).grid(row=6, column=1, pady=10)

نافذة.mainloop()

 جدول = Table(بيانات)
    جدول.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    doc.build([جدول])
    messagebox.showinfo("✅ تم", "تم تصدير القائمة إلى PDF.")

from openpyxl import Workbook

def تصدير_Excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "الموظفون"
    ws.append(["#", "الاسم", "الوظيفة"])
    for i, (الاسم, الوظيفة) in enumerate(الموظفون, start=1):
        ws.append([i, الاسم, الوظيفة])
    wb.save("الموظفون.xlsx")
    messagebox.showinfo("✅ تم", "تم حفظ الملف Excel بنجاح.")

import sqlite3

# الاتصال وإنشاء الجدول
conn = sqlite3.connect("الموظفون.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS موظفون (اسم TEXT, وظيفة TEXT)")
conn.commit()

def حفظ_الموظف(الاسم, الوظيفة):
    cursor.execute("INSERT INTO موظفون VALUES (?, ?)", (الاسم, الوظيفة))
    conn.commit()

def استرجاع_الموظفين():
    الموظفون.clear()
    for row in cursor.execute("SELECT * FROM موظفون"):
        الموظفون.append((row[0], row[1]))
    تحديث_القائمة()

الموظفون.append((الاسم, الوظيفة, التقييم))

اختيار_التقييم = tk.StringVar(value="⭐️⭐️⭐️")
tk.OptionMenu(نافذة, اختيار_التقييم, "⭐️", "⭐️⭐️", "⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️").grid(row=3, column=1)
from django.db import models

class منتج(models.Model):
    الاسم = models.CharField(max_length=100)
    الكمية_المتوفرة = models.IntegerField(default=0)
    السعر = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.الاسم

class عملية_بيع(models.Model):
    المنتج = models.ForeignKey(منتج, on_delete=models.CASCADE)
    الكمية = models.IntegerField()
    التاريخ = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.الكمية} من {self.المنتج}"
from django.shortcuts import render
from .models import منتج, عملية_بيع
from django.db.models import Sum

def عرض_الموازنة(request):
    النتائج = []

    for المنتج in منتج.objects.all():
        اجمالي_المبيعات = عملية_بيع.objects.filter(المنتج=المنتج).aggregate(Sum('الكمية'))['الكمية__sum'] or 0
        المتبقي = المنتج.الكمية_المتوفرة - اجمالي_المبيعات

        النتائج.append({
            'المنتج': المنتج.الاسم,
            'المخزون': المنتج.الكمية_المتوفرة,
            'المبيعات': اجمالي_المبيعات,
            'المتبقي': المتبقي
        })

    return render(request, 'الموازنة.html', {'النتائج': النتائج})

<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>موازنة المنتجات</title>
    <style>
        body { font-family: Arial; direction: rtl; }
        table { width: 80%; margin: auto; border-collapse: collapse; }
        th, td { padding: 10px; border: 1px solid #444; text-align: center; }
        th { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">📊 جدول موازنة المنتجات</h2>
    <table>
        <tr>
            <th>اسم المنتج</th>
            <th>المخزون</th>
            <th>إجمالي المبيعات</th>
            <th>المتبقي</th>
        </tr>
        {% for صف in النتائج %}
        <tr>
            <td>{{ صف.المنتج }}</td>
            <td>{{ صف.المخزون }}</td>
            <td>{{ صف.المبيعات }}</td>
            <td>{{ صف.المتبقي }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>

from django import forms
from .models import عملية_بيع

class نموذج_عملية_بيع(forms.ModelForm):
    class Meta:
        model = عملية_بيع
        fields = ['المنتج', 'الكمية']
        labels = {
            'المنتج': 'المنتج',
            'الكمية': 'الكمية المباعة'
        }

<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تسجيل عملية بيع جديدة</title>
    <style>
        body { font-family: Arial; direction: rtl; text-align: center; margin-top: 50px; }
        form { width: 300px; margin: auto; }
        input, select { width: 100%; padding: 10px; margin-bottom: 15px; }
        button { padding: 10px 20px; background-color: green; color: white; border: none; }
    </style>
</head>
<body>
    <h2>🛍️ تسجيل عملية بيع جديدة</h2>
    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">تسجيل</button>
    </form>
</body>
</html>

from .forms import نموذج_عملية_بيع

def بيع_جديد(request):
    if request.method == 'POST':
        form = نموذج_عملية_بيع(request.POST)
        if form.is_valid():
            form.save()
            return redirect('عرض_الموازنة')
    else:
        form = نموذج_عملية_بيع()

    return render(request, 'بيع_جديد.html', {'form': form})

from django.urls import path
from . import views

urlpatterns = [
    path('بيع_جديد/', views.بيع_جديد, name='بيع_جديد'),
    path('الموازنة/', views.عرض_الموازنة, name='عرض_الموازنة'),
]

from .models import منتج, عمليةبيع

def احسب_الموازنة():
    النتائج = []
    المنتجات = منتج.objects.all()

    for المنتج in المنتجات:
        المباع = عمليةبيع.objects.filter(المنتج=المنتج).aggregate(Sum('الكمية'))['الكمية__sum'] or 0
        المتبقي = المنتج.الكمية_في_المخزن - المباع

        النتائج.append({
            'المنتج': المنتج.الاسم,
            'المخزون': المنتج.الكمية_في_المخزن,
            'المبيعات': المباع,
            'المتبقي': المتبقي
        })

    return النتائج
