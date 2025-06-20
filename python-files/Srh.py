import customtkinter as ctk
import sqlite3
from datetime import datetime
import webbrowser
import os
from tkinter import messagebox
from tkinter import ttk
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import tkinter as tk

# دالة لتحسين النص العربي
def arabic_text(text):
    if not text or not isinstance(text, str):
        return text
    reshaped_text = reshape(text)
    return get_display(reshaped_text)

# في قسم إعدادات الواجهة بعد set_default_color_theme
ctk.set_widget_scaling(1.0)  # ضبط حجم العناصر
ctk.set_window_scaling(1.0)


# الألوان الثابتة
GOLD = "#D4AF37"
GOLD_LIGHT = "#FFE38A"
DARK_BG = "#1A1A1A"
DARK_CARD = "#222"
RED = "#C44"

# إعدادات الواجهة
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# إنشاء قاعدة البيانات وتجهيز الجداول
def init_db():
    conn = sqlite3.connect('institute.db')
    cursor = conn.cursor()

    # جدول الطلاب
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        study_type TEXT CHECK(study_type IN ('حضوري', 'الكتروني')),
        has_card INTEGER DEFAULT 0,
        has_badge INTEGER DEFAULT 0,
        status TEXT DEFAULT 'مستمر',
        barcode TEXT UNIQUE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # جدول المدرسين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        total_fee REAL DEFAULT 0,
        institute_percentage INTEGER DEFAULT 30,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # جدول علاقة الطلاب بالمدرسين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_teacher (
        student_id INTEGER,
        teacher_id INTEGER,
        PRIMARY KEY (student_id, teacher_id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )
    ''')

    # جدول الأقساط
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS installments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        teacher_id INTEGER,
        amount REAL NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )
    ''')

    # جدول سحوبات المدرسين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teacher_withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        amount REAL NOT NULL,
        withdrawal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )
    ''')

    conn.commit()
    conn.close()


# فئة بطاقة الوحدة
class ModuleCard(ctk.CTkFrame):
    def __init__(self, master, title, desc, icon, command=None, card_x=0, card_y=0, card_w=260, card_h=350, selected_student_id=None, **kwargs):
        super().__init__(master, fg_color=DARK_CARD, border_color=GOLD, border_width=2, corner_radius=20, width=card_w, height=card_h, **kwargs)
        self.place(x=card_x, y=card_y)
        self.grid_propagate(False)
        self.icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 48), text_color=GOLD)
        self.icon.place(relx=0.5, y=50, anchor="center")
        self.title = ctk.CTkLabel(self, text=title, font=("Tajawal", 22, "bold"), text_color=GOLD_LIGHT)
        self.title.place(relx=0.5, y=112, anchor="center")
        self.desc = ctk.CTkLabel(self, text=desc, font=("Tajawal", 15), text_color="#EEE", wraplength=210, justify="center")
        self.desc.place(relx=0.5, y=182, anchor="center")
        self.btn = ctk.CTkButton(self, text="ادخل", fg_color=GOLD, text_color=DARK_BG, font=("Tajawal", 15, "bold"), command=command, width=120, height=38)
        self.btn.place(relx=0.5, rely=0.87, anchor="center")


class TeachersWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إدارة المدرسين")
        self.geometry("1300x700")
        self.resizable(False, False)
        self.configure(bg_color=DARK_BG)
        self.transient(master)
        self.grab_set()

        # متغيرات النموذج
        self.teacher_id = None
        self.name_var = ctk.StringVar()
        self.subject_var = ctk.StringVar()
        self.total_fee_var = ctk.StringVar()
        self.percentage_var = ctk.StringVar(value="30")
        self.notes_var = ctk.StringVar()

        # عناصر الواجهة
        self.create_widgets()

        # تحميل المواد والمدرسين
        self.load_subjects_cards()

    def create_widgets(self):
        """إنشاء عناصر واجهة المستخدم"""
        # عنوان النافذة
        ctk.CTkLabel(
            self,
            text="إدارة المدرسين",
            font=("Tajawal", 24, "bold"),
            text_color=GOLD_LIGHT
        ).pack(pady=10)

        # إطار عرض المواد
        self.subjects_frame = ctk.CTkScrollableFrame(
            self,
            width=1260,
            height=600,
            fg_color=DARK_BG
        )
        self.subjects_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # إطار إضافة مدرس جديد (مخفي في البداية)
        self.add_teacher_frame = ctk.CTkFrame(
            self,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20,
            width=400,
            height=500
        )
        self.add_teacher_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.add_teacher_frame.place_forget()

        # عناصر نموذج إضافة مدرس
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="إضافة مدرس جديد",
            font=("Tajawal", 20, "bold"),
            text_color=GOLD_LIGHT
        ).place(x=120, y=20)

        # حقل الاسم
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="اسم المدرس:",
            font=("Tajawal", 14)
        ).place(x=300, y=80)
        ctk.CTkEntry(
            self.add_teacher_frame,
            textvariable=self.name_var,
            width=250,
            font=("Tajawal", 14)
        ).place(x=30, y=80)

        # حقل المادة
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="المادة:",
            font=("Tajawal", 14)
        ).place(x=320, y=130)
        ctk.CTkEntry(
            self.add_teacher_frame,
            textvariable=self.subject_var,
            width=250,
            font=("Tajawal", 14)
        ).place(x=30, y=130)

        # حقل الأجر الكلي
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="الأجر الكلي:",
            font=("Tajawal", 14)
        ).place(x=290, y=180)
        ctk.CTkEntry(
            self.add_teacher_frame,
            textvariable=self.total_fee_var,
            width=250,
            font=("Tajawal", 14)
        ).place(x=30, y=180)

        # حقل نسبة المعهد
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="نسبة المعهد %:",
            font=("Tajawal", 14)
        ).place(x=270, y=230)
        ctk.CTkEntry(
            self.add_teacher_frame,
            textvariable=self.percentage_var,
            width=250,
            font=("Tajawal", 14)
        ).place(x=30, y=230)

        # حقل الملاحظات
        ctk.CTkLabel(
            self.add_teacher_frame,
            text="ملاحظات:",
            font=("Tajawal", 14)
        ).place(x=300, y=280)
        ctk.CTkEntry(
            self.add_teacher_frame,
            textvariable=self.notes_var,
            width=250,
            font=("Tajawal", 14)
        ).place(x=30, y=280)

        # أزرار التحكم
        ctk.CTkButton(
            self.add_teacher_frame,
            text="حفظ",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=100,
            command=self.save_teacher
        ).place(x=220, y=350)

        ctk.CTkButton(
            self.add_teacher_frame,
            text="إلغاء",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=100,
            command=self.hide_add_teacher_form
        ).place(x=80, y=350)

    def load_subjects_cards(self):
        """تحميل المواد الدراسية وعرضها ككارتات"""
        # مسح المحتوى القديم
        for widget in self.subjects_frame.winfo_children():
            widget.destroy()

        # جلب المواد من قاعدة البيانات
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        # جلب جميع المواد الفريدة
        cursor.execute("SELECT DISTINCT subject FROM teachers ORDER BY subject")
        subjects = [row[0] for row in cursor.fetchall()]

        # إذا لم تكن هناك مواد، نعرض رسالة ونضيف زر إضافة مدرس
        if not subjects:
            no_subjects_frame = ctk.CTkFrame(
                self.subjects_frame,
                fg_color=DARK_CARD,
                width=1200,
                height=100
            )
            no_subjects_frame.pack(pady=20, fill="x")

            ctk.CTkLabel(
                no_subjects_frame,
                text="لا توجد مواد مدرجة بعد",
                font=("Tajawal", 16),
                text_color=GOLD_LIGHT
            ).pack(side="left", padx=20, pady=20)

            ctk.CTkButton(
                no_subjects_frame,
                text="إضافة مدرس جديد",
                fg_color=GOLD,
                text_color=DARK_BG,
                font=("Tajawal", 14, "bold"),
                command=self.show_add_teacher_form
            ).pack(side="right", padx=20, pady=20)

            conn.close()
            return

        # عرض كل مادة في كارت منفصل
        for subject in subjects:
            subject_card = ctk.CTkFrame(
                self.subjects_frame,
                fg_color=DARK_CARD,
                border_color=GOLD,
                border_width=1,
                corner_radius=15,
                width=1200,
                height=200
            )
            subject_card.pack(pady=10, fill="x")
            subject_card.pack_propagate(False)

            # عنوان المادة
            title_frame = ctk.CTkFrame(subject_card, fg_color="transparent")
            title_frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(
                title_frame,
                text=subject,
                font=("Tajawal", 18, "bold"),
                text_color=GOLD_LIGHT
            ).pack(side="right")

            ctk.CTkButton(
                title_frame,
                text="إضافة مدرس لهذه المادة",
                fg_color=GOLD,
                text_color=DARK_BG,
                font=("Tajawal", 12, "bold"),
                width=150,
                height=30,
                command=lambda s=subject: self.add_teacher_for_subject(s)
            ).pack(side="left")

            # جلب مدرسي هذه المادة
            cursor.execute("""
                SELECT id, name, 
                (SELECT COUNT(*) FROM student_teacher WHERE teacher_id=teachers.id) as student_count
                FROM teachers 
                WHERE subject=?
                ORDER BY name
            """, (subject,))
            teachers = cursor.fetchall()

            # عرض المدرسين في صف أفقي مع شريط تمرير
            teachers_scroll = ctk.CTkScrollableFrame(
                subject_card,
                orientation="horizontal",
                height=120,
                fg_color="transparent"
            )
            teachers_scroll.pack(fill="x", padx=10, pady=5)

            for teacher_id, name, student_count in teachers:
                teacher_btn = ctk.CTkButton(
                    teachers_scroll,
                    text=f"{name}\nعدد الطلاب: {student_count}",
                    font=("Tajawal", 14),
                    fg_color="#333",
                    hover_color="#444",
                    width=180,
                    height=100,
                    corner_radius=10,
                    command=lambda tid=teacher_id: self.show_teacher_details(tid)
                )
                teacher_btn.pack(side="left", padx=5)

        conn.close()

        # زر إضافة مدرس جديد
        add_btn_frame = ctk.CTkFrame(self.subjects_frame, fg_color="transparent")
        add_btn_frame.pack(pady=10)

        ctk.CTkButton(
            add_btn_frame,
            text="إضافة مدرس جديد",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 16, "bold"),
            width=200,
            height=50,
            command=self.show_add_teacher_form
        ).pack()

    def add_teacher_for_subject(self, subject):
        """إضافة مدرس لمادة محددة"""
        self.subject_var.set(subject)
        self.show_add_teacher_form()

    def show_add_teacher_form(self):
        """عرض نموذج إضافة مدرس جديد"""
        self.add_teacher_frame.lift()
        self.add_teacher_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.name_var.set("")
        self.subject_var.set("")
        self.total_fee_var.set("")
        self.percentage_var.set("30")
        self.notes_var.set("")
        self.teacher_id = None

    def hide_add_teacher_form(self):
        """إخفاء نموذج إضافة مدرس جديد"""
        self.add_teacher_frame.place_forget()

    def save_teacher(self):
        """حفظ بيانات المدرس في قاعدة البيانات"""
        # التحقق من البيانات المدخلة
        if not self.name_var.get().strip():
            messagebox.showerror("خطأ", "يرجى إدخال اسم المدرس")
            return

        if not self.subject_var.get().strip():
            messagebox.showerror("خطأ", "يرجى إدخال المادة")
            return

        try:
            total_fee = float(self.total_fee_var.get())
            if total_fee <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أجر كلي صحيح أكبر من الصفر")
            return

        try:
            percentage = int(self.percentage_var.get())
            if not 0 <= percentage <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال نسبة صحيحة بين 0 و 100")
            return

        # حفظ البيانات في قاعدة البيانات
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        try:
            if self.teacher_id:  # إذا كان هناك ID، فهذا تحديث لمدرس موجود
                cursor.execute("""
                    UPDATE teachers 
                    SET name=?, subject=?, total_fee=?, institute_percentage=?, notes=?
                    WHERE id=?
                """, (
                    self.name_var.get().strip(),
                    self.subject_var.get().strip(),
                    total_fee,
                    percentage,
                    self.notes_var.get().strip(),
                    self.teacher_id
                ))
                message = "تم تحديث بيانات المدرس بنجاح"
            else:  # إذا لم يكن هناك ID، فهذا مدرس جديد
                cursor.execute("""
                    INSERT INTO teachers (name, subject, total_fee, institute_percentage, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.name_var.get().strip(),
                    self.subject_var.get().strip(),
                    total_fee,
                    percentage,
                    self.notes_var.get().strip()
                ))
                message = "تم إضافة المدرس بنجاح"

            conn.commit()
            messagebox.showinfo("نجاح", message)
            self.hide_add_teacher_form()
            self.load_subjects_cards()  # إعادة تحميل الكارتات لتحديث البيانات

        except sqlite3.Error as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ أثناء حفظ البيانات:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("خطأ غير متوقع", f"حدث خطأ غير متوقع:\n{str(e)}")
        finally:
            conn.close()

    def show_teacher_details(self, teacher_id):
        """عرض تفاصيل المدرس وطلابه"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        # جلب بيانات المدرس
        cursor.execute("""
            SELECT name, subject, total_fee, institute_percentage, notes
            FROM teachers WHERE id=?
        """, (teacher_id,))
        teacher_data = cursor.fetchone()

        if not teacher_data:
            messagebox.showerror("خطأ", "لم يتم العثور على بيانات المدرس")
            conn.close()
            return

        name, subject, total_fee, percentage, notes = teacher_data

        # جلب عدد الطلاب
        cursor.execute("""
            SELECT COUNT(*) FROM student_teacher WHERE teacher_id=?
        """, (teacher_id,))
        student_count = cursor.fetchone()[0]

        # جلب قائمة الطلاب
        cursor.execute("""
            SELECT s.id, s.name, s.status, s.study_type
            FROM students s
            JOIN student_teacher st ON s.id = st.student_id
            WHERE st.teacher_id=?
            ORDER BY s.name
        """, (teacher_id,))
        students = cursor.fetchall()

        conn.close()

        # إنشاء نافذة التفاصيل
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"تفاصيل المدرس: {name}")
        details_window.geometry("800x600")
        details_window.resizable(False, False)
        details_window.transient(self)
        details_window.grab_set()

        # الإطار الرئيسي
        main_frame = ctk.CTkFrame(
            details_window,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # عنوان النافذة
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(
            title_frame,
            text=f"المدرس: {name}",
            font=("Tajawal", 20, "bold"),
            text_color=GOLD_LIGHT
        ).pack(side="right")

        ctk.CTkLabel(
            title_frame,
            text=f"المادة: {subject}",
            font=("Tajawal", 16),
            text_color="#DDD"
        ).pack(side="right", padx=20)

        # معلومات المدرس
        info_frame = ctk.CTkFrame(main_frame, fg_color="#333", corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")

        info_text = f"""
        الأجر الكلي: {total_fee:,} دينار
        نسبة المعهد: {percentage}%
        عدد الطلاب: {student_count}
        """

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Tajawal", 14),
            text_color="white",
            justify="right",
            anchor="e"
        ).pack(pady=10, padx=20, fill="x")

        # ملاحظات المدرس
        if notes:
            notes_frame = ctk.CTkFrame(main_frame, fg_color="#333", corner_radius=10)
            notes_frame.pack(pady=10, padx=20, fill="x")

            ctk.CTkLabel(
                notes_frame,
                text=f"ملاحظات:\n{notes}",
                font=("Tajawal", 12),
                text_color="#AAA",
                justify="right",
                wraplength=700
            ).pack(pady=10, padx=20, fill="x")

        # قائمة الطلاب
        students_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        students_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            students_frame,
            text="قائمة الطلاب:",
            font=("Tajawal", 16, "bold"),
            text_color=GOLD_LIGHT
        ).pack(anchor="w")

        if students:
            # جدول الطلاب
            columns = ("id", "name", "status", "study_type")
            tree = ttk.Treeview(
                students_frame,
                columns=columns,
                show="headings",
                height=10
            )

            # تنسيق الجدول
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview",
                            background=DARK_CARD,
                            foreground="white",
                            fieldbackground=DARK_CARD,
                            borderwidth=0)
            style.configure("Treeview.Heading",
                            background=GOLD,
                            foreground=DARK_BG,
                            font=("Tajawal", 12, "bold"))
            style.map("Treeview", background=[("selected", "#444")])

            # عناوين الأعمدة
            tree.heading("id", text="تسلسل")
            tree.column("id", width=80, anchor="center")

            tree.heading("name", text="اسم الطالب")
            tree.column("name", width=300, anchor="center")

            tree.heading("status", text="الحالة")
            tree.column("status", width=100, anchor="center")

            tree.heading("study_type", text="نوع الدراسة")
            tree.column("study_type", width=150, anchor="center")

            # إضافة البيانات
            for student in students:
                tree.insert("", "end", values=student)

            tree.pack(fill="both", expand=True, pady=10)

            # شريط التمرير
            scrollbar = ttk.Scrollbar(students_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
        else:
            ctk.CTkLabel(
                students_frame,
                text="لا يوجد طلاب مسجلين لهذا المدرس بعد",
                font=("Tajawal", 14),
                text_color="#AAA"
            ).pack(pady=20)

        # أزرار التحكم
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="تعديل بيانات المدرس",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=150,
            command=lambda: self.edit_teacher(teacher_id, details_window)
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            buttons_frame,
            text="إغلاق",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=150,
            command=details_window.destroy
        ).pack(side="left", padx=10)

    def edit_teacher(self, teacher_id, parent_window):
        """تحميل بيانات المدرس للتعديل"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, subject, total_fee, institute_percentage, notes
            FROM teachers WHERE id=?
        """, (teacher_id,))

        teacher_data = cursor.fetchone()
        conn.close()

        if teacher_data:
            self.teacher_id = teacher_id
            self.name_var.set(teacher_data[0])
            self.subject_var.set(teacher_data[1])
            self.total_fee_var.set(str(teacher_data[2]))
            self.percentage_var.set(str(teacher_data[3]))
            self.notes_var.set(teacher_data[4] or "")

            parent_window.destroy()
            self.show_add_teacher_form()
class StudentsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إدارة الطلاب")
        self.geometry("1200x600")
        self.resizable(False, False)
        self.configure(bg_color=DARK_BG)
        self.transient(master)
        self.grab_set()

        # متغيرات النموذج
        self.student_id = None
        self.name_var = ctk.StringVar()
        self.barcode_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="مستمر")
        self.study_type_var = ctk.StringVar(value="حضوري")
        self.has_card_var = ctk.IntVar(value=0)
        self.has_badge_var = ctk.IntVar(value=0)
        self.notes_var = ctk.StringVar()
        self.generate_barcode()

        # ========== إطار النموذج ==========
        self.form_frame = ctk.CTkFrame(
            self,
            width=350,
            height=550,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        self.form_frame.place(x=20, y=20)

        # عنوان النموذج
        ctk.CTkLabel(
            self.form_frame,
            text="بيانات الطالب",
            font=("Tajawal", 20, "bold"),
            text_color=GOLD_LIGHT
        ).place(x=120, y=20)

        # ------ حقول الإدخال ------
        # حقل اسم الطالب
        ctk.CTkLabel(
            self.form_frame,
            text="الاسم",
            font=("Tajawal", 14)
        ).place(x=290, y=70)
        self.name_entry = ctk.CTkEntry(
            self.form_frame,
            textvariable=self.name_var,
            width=250,
            font=("Tajawal", 14)
        )
        self.name_entry.place(x=30, y=70)

        # حقل حالة الطالب
        ctk.CTkLabel(
            self.form_frame,
            text="حالة الطالب",
            font=("Tajawal", 14)
        ).place(x=255, y=120)
        self.status_menu = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.status_var,
            values=["مستمر", "منسحب"],
            width=220,
            font=("Tajawal", 14)
        )
        self.status_menu.place(x=30, y=120)

        # حقل نوع الدراسة
        ctk.CTkLabel(
            self.form_frame,
            text="الدراسة",
            font=("Tajawal", 14)
        ).place(x=270, y=170)
        self.study_type_menu = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.study_type_var,
            values=["حضوري", "الكتروني"],
            width=220,
            font=("Tajawal", 14)
        )
        self.study_type_menu.place(x=30, y=170)

        # ------ خيارات إضافية ------
        # خانة اختيار كارت الحجز
        self.card_check = ctk.CTkCheckBox(
            self.form_frame,
            text="كارت الحجز",
            variable=self.has_card_var,
            font=("Tajawal", 14)
        )
        self.card_check.place(x=180, y=210)

        # خانة اختيار الباج
        self.badge_check = ctk.CTkCheckBox(
            self.form_frame,
            text="باج",
            variable=self.has_badge_var,
            font=("Tajawal", 14)
        )
        self.badge_check.place(x=30, y=210)

        # حقل المدرسين
        ctk.CTkLabel(
            self.form_frame,
            text="المدرسين",
            font=("Tajawal", 14)
        ).place(x=270, y=245)

        # إطار المدرسين مع شريط تمرير
        self.teachers_frame = ctk.CTkScrollableFrame(
            self.form_frame,
            width=250,
            height=100,
            fg_color=DARK_CARD
        )
        self.teachers_frame.place(x=30, y=270)

        # حقل البحث عن المدرسين
        self.teachers_search_var = ctk.StringVar()
        self.teachers_search_entry = ctk.CTkEntry(
            self.teachers_frame,
            textvariable=self.teachers_search_var,
            width=230,
            font=("Tajawal", 14),
            placeholder_text="ابحث عن مدرس..."
        )
        self.teachers_search_entry.pack(fill="x", pady=5)
        self.teachers_search_entry.bind("<KeyRelease>", self.search_teachers_for_student)

        # إطار نتائج البحث عن المدرسين
        self.teachers_results_frame = ctk.CTkFrame(
            self.teachers_frame,
            width=230,
            fg_color=DARK_CARD
        )
        self.teachers_results_frame.pack(fill="both", expand=True)

        # ------ أزرار التحكم ------
        # صف الأزرار العلوي
        self.add_btn = ctk.CTkButton(
            self.form_frame,
            text="إضافة",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=80,
            command=self.add_student
        )
        self.add_btn.place(x=210, y=510)

        self.update_btn = ctk.CTkButton(
            self.form_frame,
            text="تعديل",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=80,
            command=self.update_student,
            state="disabled"
        )
        self.update_btn.place(x=120, y=510)

        # صف الأزرار السفلي
        self.clear_btn = ctk.CTkButton(
            self.form_frame,
            text="تفريغ",
            fg_color="#555",
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=80,
            command=self.clear_form
        )
        self.clear_btn.place(x=30, y=510)

        # ========== إطار عرض البيانات ==========
        self.table_frame = ctk.CTkFrame(
            self,
            width=800,
            height=550,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        self.table_frame.place(x=380, y=20)

        # عنوان قائمة الطلاب
        ctk.CTkLabel(
            self.table_frame,
            text="قائمة الطلاب",
            font=("Tajawal", 20, "bold"),
            text_color=GOLD_LIGHT
        ).place(x=350, y=10)

        # ------ شريط البحث ------
        self.search_frame = ctk.CTkFrame(
            self.table_frame,
            fg_color="transparent",
            width=760,
            height=30
        )
        self.search_frame.place(x=20, y=50)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            textvariable=self.search_var,
            width=400,
            font=("Tajawal", 14),
            placeholder_text="ابحث باسم الطالب، الباركود، الحالة أو نوع الدراسة"
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_students)

        # أزرار البحث
        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="بحث",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=80,
            command=self.search_students
        )
        self.search_btn.pack(side="right", padx=5)

        self.reload_btn = ctk.CTkButton(
            self.search_frame,
            text="عرض الكل",
            fg_color="#555",
            text_color="white",
            font=("Tajawal", 14),
            width=80,
            command=self.load_students
        )
        self.reload_btn.pack(side="left", padx=5)

        # ------ جدول الطلاب ------
        self.students_table = ttk.Treeview(
            self.table_frame,
            columns=("barcode", "name", "status", "study_type", "has_card", "has_badge"),  # تمت إزالة "id" من هنا
            show="headings",
            height=20
        )

        # تنسيق الجدول
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=DARK_CARD,
                        foreground="white",
                        fieldbackground=DARK_CARD,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=GOLD,
                        foreground=DARK_BG,
                        font=("Tajawal", 12, "bold"))
        style.map("Treeview", background=[("selected", "#444")])

        # عناوين الأعمدة (تمت إزالة عمود "تسلسل")
        columns_config = [
            ("barcode", "باركود", 80),
            ("name", "اسم الطالب", 320),
            ("status", "الحالة", 80),
            ("study_type", "الدراسة", 80),
            ("has_card", "كارت", 60),
            ("has_badge", "باج", 60)
        ]

        for col_id, col_text, col_width in columns_config:
            self.students_table.heading(col_id, text=col_text)
            self.students_table.column(col_id, width=col_width, anchor="center")

        self.students_table.place(x=30, y=110)

        # شريط التمرير
        scrollbar = ttk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.students_table.yview
        )
        scrollbar.place(x=760, y=90, height=440)
        self.students_table.configure(yscrollcommand=scrollbar.set)

        # أحداث الجدول
        self.students_table.bind("<ButtonRelease-1>", self.select_student)

        # زر عرض البروفايل
        self.show_teachers_btn = ctk.CTkButton(
            self.table_frame,
            text="عرض بروفايل الطالب",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=150,
            command=self.show_student_profile,
            state="disabled"
        )
        self.show_teachers_btn.place(x=320, y=500)

        # تحميل البيانات الأولية
        self.load_students()

    def get_teacher_total_fee(self, teacher_id):
        """استرجاع المبلغ الكلي للمدرس من قاعدة البيانات"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_fee FROM teachers WHERE id=?", (teacher_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    # ========== دوال الوظائف ==========
    def search_teachers_for_student(self, event=None):
        """بحث عن المدرسين أثناء الكتابة وعرضهم"""
        search_term = self.teachers_search_var.get().strip()

        # مسح نتائج البحث السابقة
        for widget in self.teachers_results_frame.winfo_children():
            widget.destroy()

        if not search_term:
            return

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, subject FROM teachers 
            WHERE name LIKE ? 
            ORDER BY name
            LIMIT 10
        """, (f"%{search_term}%",))

        teachers = cursor.fetchall()
        conn.close()

        for teacher_id, name, subject in teachers:
            btn = ctk.CTkButton(
                self.teachers_results_frame,
                text=f"{name} - {subject}",
                font=("Tajawal", 12),
                fg_color=DARK_CARD,
                hover_color="#333",
                anchor="w",
                command=lambda tid=teacher_id, n=name: self.assign_teacher(tid, n)
            )
            btn.pack(fill="x", pady=2)

    def assign_teacher(self, teacher_id, teacher_name):
        """ربط المدرس المحدد بالطالب الحالي"""
        if not self.student_id:
            messagebox.showwarning("تحذير", "يجب اختيار طالب أولاً")
            return

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        try:
            # التحقق من عدم وجود العلاقة مسبقاً
            cursor.execute("""
                SELECT 1 FROM student_teacher 
                WHERE student_id=? AND teacher_id=?
            """, (self.student_id, teacher_id))

            if cursor.fetchone():
                messagebox.showinfo("معلومة", "المدرس مسجل بالفعل لهذا الطالب")
                return

            # إضافة العلاقة
            cursor.execute("""
                INSERT INTO student_teacher (student_id, teacher_id)
                VALUES (?, ?)
            """, (self.student_id, teacher_id))

            conn.commit()
            messagebox.showinfo("نجاح", f"تم ربط المدرس {teacher_name} بالطالب بنجاح")
            self.load_student_teachers()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء ربط المدرس: {str(e)}")
        finally:
            conn.close()

    def load_student_teachers(self):
        """تحميل قائمة المدرسين المرتبطين بالطالب الحالي"""
        if not self.student_id:
            return

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.id, t.name, t.subject 
            FROM teachers t
            JOIN student_teacher st ON t.id = st.teacher_id
            WHERE st.student_id = ?
            ORDER BY t.name
        """, (self.student_id,))

        teachers = cursor.fetchall()
        conn.close()

        # مسح المدرسين الحاليين المعروضين
        for widget in self.teachers_results_frame.winfo_children():
            widget.destroy()

        # إنشاء إطار جديد لعرض المدرسين بطريقة منظمة
        container = ctk.CTkFrame(self.teachers_results_frame, fg_color=DARK_CARD)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # عنوان القسم
        title_label = ctk.CTkLabel(
            container,
            text=f"المدرسين المسجلين ({len(teachers)}):",
            font=("Tajawal", 14, "bold"),
            text_color=GOLD_LIGHT
        )
        title_label.pack(anchor="w", pady=(0, 10))

        if not teachers:
            no_teachers_label = ctk.CTkLabel(
                container,
                text="لا يوجد مدرسين مسجلين لهذا الطالب",
                font=("Tajawal", 12),
                text_color="#AAA"
            )
            no_teachers_label.pack(anchor="w")
            return

        # عرض كل مدرس في بطاقة منفصلة
        for teacher_id, name, subject in teachers:
            teacher_card = ctk.CTkFrame(
                container,
                fg_color="#333",
                corner_radius=10,
                border_color=GOLD,
                border_width=1
            )
            teacher_card.pack(fill="x", pady=3, padx=2)

            # محتوى البطاقة
            content_frame = ctk.CTkFrame(teacher_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=5)

            # اسم المدرس (بخط أكبر)
            name_label = ctk.CTkLabel(
                content_frame,
                text=f"👨‍🏫 {name}",
                font=("Tajawal", 14, "bold"),
                text_color=GOLD_LIGHT,
                anchor="w"
            )
            name_label.pack(fill="x")

            # المادة (بخط أصغر)
            subject_label = ctk.CTkLabel(
                content_frame,
                text=f"📚 {subject}",
                font=("Tajawal", 12),
                text_color="#DDD",
                anchor="w"
            )
            subject_label.pack(fill="x")

    def generate_barcode(self):
        """توليد باركود تلقائي للطالب"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("SELECT barcode FROM students WHERE barcode LIKE 'BN-%'")
        existing_barcodes = [b[0] for b in cursor.fetchall()]
        conn.close()

        if existing_barcodes:
            numbers = []
            for barcode in existing_barcodes:
                try:
                    numbers.append(int(barcode[3:]))
                except ValueError:
                    continue

            new_number = max(numbers) + 1 if numbers else 1
        else:
            new_number = 1

        self.barcode_var.set(f"BN-{new_number:04d}")

    def load_students(self, search_query=None):
        """تحميل قائمة الطلاب من قاعدة البيانات"""
        self.students_table.delete(*self.students_table.get_children())

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        query = """
            SELECT barcode, name, status, study_type, has_card, has_badge, id 
            FROM students 
        """
        params = ()

        if search_query:
            query += "WHERE name LIKE ? OR barcode LIKE ? OR status LIKE ? OR study_type LIKE ?"
            params = (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")

        query += "ORDER BY id DESC"
        cursor.execute(query, params)

        for student in cursor.fetchall():
            self.students_table.insert("", "end", values=(
                student[0],  # barcode
                student[1],  # name
                student[2],  # status
                student[3],  # study_type
                "نعم" if student[4] else "لا",  # has_card
                "نعم" if student[5] else "لا",  # has_badge
                student[6]   # id (مخفي ولكن موجود في البيانات)
            ))

        conn.close()

    def search_students(self, event=None):
        """بحث الطلاب حسب معايير البحث"""
        self.load_students(self.search_var.get().strip())

    def select_student(self, event):
        """اختيار طالب من الجدول لعرض بياناته"""
        selected = self.students_table.focus()
        if not selected:
            return

        student_data = self.students_table.item(selected)['values']
        if not student_data or len(student_data) < 7:
            return

        # ملاحظة: student_data[6] يحتوي على ID رغم أنه غير معروض
        self.student_id = student_data[6]
        self.name_var.set(student_data[1])
        self.barcode_var.set(student_data[0])
        self.status_var.set(student_data[2])
        self.study_type_var.set(student_data[3])
        self.has_card_var.set(1 if student_data[4] == "نعم" else 0)
        self.has_badge_var.set(1 if student_data[5] == "نعم" else 0)

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()
        cursor.execute("SELECT notes FROM students WHERE id=?", (self.student_id,))
        notes = cursor.fetchone()[0] or ""
        self.notes_var.set(notes)
        conn.close()

        # تحميل المدرسين المرتبطين بالطالب المحدد
        self.load_student_teachers()

        # تفعيل/تعطيل الأزرار حسب الحالة
        self.update_btn.configure(state="normal")
        self.show_teachers_btn.configure(state="normal")
        self.add_btn.configure(state="disabled")

    def clear_form(self):
        """تفريغ كامل لحقول النموذج وإعادة تعيين جميع المتغيرات"""
        # إعادة تعيين متغيرات النموذج
        self.student_id = None
        self.name_var.set("")
        self.generate_barcode()
        self.status_var.set("مستمر")
        self.study_type_var.set("حضوري")
        self.has_card_var.set(0)
        self.has_badge_var.set(0)
        self.notes_var.set("")

        # مسح حقل البحث عن المدرسين
        self.teachers_search_var.set("")

        # مسح قائمة المدرسين المرتبطين
        for widget in self.teachers_results_frame.winfo_children():
            widget.destroy()

        # مسح حقل البحث الرئيسي
        self.search_var.set("")

        # إعادة تعيين حالة الأزرار
        self.update_btn.configure(state="disabled")
        self.show_teachers_btn.configure(state="disabled")
        self.add_btn.configure(state="normal")

        # إعادة تحميل قائمة الطلاب لعرض جميع الطلاب
        self.load_students()
    def add_student(self):
        """إضافة طالب جديد"""
        if not self.name_var.get():
            messagebox.showerror("خطأ", "يرجى إدخال اسم الطالب")
            return

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO students (name, barcode, status, study_type, has_card, has_badge, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.name_var.get(),
                self.barcode_var.get(),
                self.status_var.get(),
                self.study_type_var.get(),
                self.has_card_var.get(),
                self.has_badge_var.get(),
                self.notes_entry.get("1.0", "end").strip()
            ))

            conn.commit()
            messagebox.showinfo("نجاح", "تمت إضافة الطالب بنجاح")
            self.load_students()
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "باركود الطالب موجود مسبقاً")
        finally:
            conn.close()

    def update_student(self):
        """تحديث بيانات الطالب مع التحقق من البيانات ومعالجة الأخطاء"""
        if not self.student_id:
            messagebox.showwarning("تحذير", "لم يتم اختيار أي طالب للتحديث")
            return

        # التحقق من إدخال الاسم
        if not self.name_var.get().strip():
            messagebox.showerror("خطأ", "يرجى إدخال اسم الطالب")
            return

        conn = None
        try:
            conn = sqlite3.connect('institute.db')
            cursor = conn.cursor()

            # التحقق من أن الباركود غير مستخدم لطالب آخر
            cursor.execute("""
                SELECT id FROM students 
                WHERE barcode = ? AND id != ?
            """, (self.barcode_var.get(), self.student_id))

            if cursor.fetchone():
                messagebox.showerror("خطأ", "باركود الطالب موجود مسبقاً لطالب آخر")
                return

            # تنفيذ تحديث البيانات
            cursor.execute("""
                UPDATE students 
                SET name=?, barcode=?, status=?, study_type=?, has_card=?, has_badge=?, notes=?
                WHERE id=?
            """, (
                self.name_var.get().strip(),
                self.barcode_var.get().strip(),
                self.status_var.get(),
                self.study_type_var.get(),
                self.has_card_var.get(),
                self.has_badge_var.get(),
                self.notes_var.get().strip(),
                self.student_id
            ))

            conn.commit()
            messagebox.showinfo("نجاح", "تم تحديث بيانات الطالب بنجاح")
            self.load_students()

        except sqlite3.Error as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ أثناء تحديث الطالب:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("خطأ غير متوقع", f"حدث خطأ غير متوقع:\n{str(e)}")
        finally:
            if conn:
                conn.close()

    def show_student_profile(self):
        """عرض بروفايل الطالب مع تفاصيل المدرسين والمدفوعات"""
        if not self.student_id:
            return

        profile_window = ctk.CTkToplevel(self)
        profile_window.title(f"بروفايل الطالب: {self.name_var.get()}")
        profile_window.geometry("1000x700")
        profile_window.resizable(False, False)
        profile_window.transient(self)
        profile_window.grab_set()

        # ------ الإطار الرئيسي ------
        main_frame = ctk.CTkFrame(
            profile_window,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # ------ قسم معلومات الطالب ------
        info_frame = ctk.CTkFrame(main_frame, fg_color=DARK_CARD)
        info_frame.pack(pady=10, padx=10, fill="x")

        # العنوان
        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(anchor="center", pady=5)

        ctk.CTkLabel(
            title_frame,
            text=":معلومات الطالب",
            font=("Tajawal", 16, "bold"),
            text_color=GOLD_LIGHT
        ).pack(side="right")

        ctk.CTkLabel(
            title_frame,
            text=self.name_var.get(),
            font=("Tajawal", 16, "bold"),
            text_color=GOLD
        ).pack(side="right", padx=5)

        # بطاقة المعلومات
        card_frame = ctk.CTkFrame(
            info_frame,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=1,
            corner_radius=10
        )
        card_frame.pack(pady=10, padx=20, fill="x", expand=True)

        info_text = f"""
        الباركود: {self.barcode_var.get()}
        حالة الطالب: {self.status_var.get()}
        نوع الدراسة: {self.study_type_var.get()}
        كارت الحجز: {"نعم" if self.has_card_var.get() else "لا"}
        الباج: {"نعم" if self.has_badge_var.get() else "لا"}
        تاريخ التسجيل: {self.get_student_creation_date()}
        """

        ctk.CTkLabel(
            card_frame,
            text=info_text,
            font=("Tajawal", 14),
            text_color="white",
            justify="right",
            anchor="e",
            wraplength=500
        ).pack(pady=10, padx=20, fill="x", expand=True)

        # ------ قسم المدرسين والمدفوعات ------
        ctk.CTkLabel(
            main_frame,
            text="المدرسين المسجل عندهم والمدفوعات",
            font=("Tajawal", 16, "bold"),
            text_color=GOLD_LIGHT
        ).pack(pady=5)

        # إطار المدرسين مع شريط تمرير
        teachers_scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            width=940,
            height=300,
            fg_color=DARK_CARD
        )
        teachers_scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # تحميل بيانات المدرسين
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                t.id,
                t.name,
                t.subject,
                t.total_fee,
                COALESCE(SUM(i.amount), 0) AS paid_amount,
                t.total_fee - COALESCE(SUM(i.amount), 0) AS remaining_amount
            FROM teachers t
            JOIN student_teacher ON t.id = student_teacher.teacher_id
            LEFT JOIN installments i ON i.teacher_id = t.id AND i.student_id = student_teacher.student_id
            WHERE student_teacher.student_id = ?
            GROUP BY t.id, t.name, t.subject, t.total_fee
        """, (self.student_id,))

        teachers = cursor.fetchall()
        conn.close()

        # عرض كل مدرس في بطاقة منفصلة
        for teacher in teachers:
            teacher_id, name, subject, total_fee, paid, remaining = teacher

            # إنشاء بطاقة المدرس
            teacher_card = ctk.CTkFrame(
                teachers_scroll_frame,
                fg_color="#333",
                border_color=GOLD,
                border_width=1,
                corner_radius=15,
                width=900,
                height=120
            )
            teacher_card.pack(fill="x", pady=5, padx=5)
            teacher_card.grid_propagate(False)
            teacher_card.pack_propagate(False)

            # إطار محتوى البطاقة
            content_frame = ctk.CTkFrame(teacher_card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # معلومات المدرس (الجانب الأيمن)
            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.pack(side="right", fill="both", expand=True)

            # اسم المدرس
            ctk.CTkLabel(
                info_frame,
                text=f"👨‍🏫 {name}",
                font=("Tajawal", 16, "bold"),
                text_color=GOLD_LIGHT,
                anchor="w"
            ).pack(fill="x", pady=(0, 5))

            # المادة
            ctk.CTkLabel(
                info_frame,
                text=f"📚 {subject}",
                font=("Tajawal", 14),
                text_color="#DDD",
                anchor="w"
            ).pack(fill="x", pady=(0, 10))

            # معلومات المدفوعات (في صف واحد)
            payments_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            payments_frame.pack(fill="x")

            # المبلغ الكلي
            ctk.CTkLabel(
                payments_frame,
                text=f"المبلغ الكلي: {total_fee:,} دينار",
                font=("Tajawal", 12),
                text_color="#AAA"
            ).pack(side="right", padx=10)

            # المبلغ المدفوع
            ctk.CTkLabel(
                payments_frame,
                text=f"المدفوع: {paid:,} دينار",
                font=("Tajawal", 12),
                text_color="#0A0" if paid > 0 else "#AAA"
            ).pack(side="right", padx=10)

            # المبلغ المتبقي
            ctk.CTkLabel(
                payments_frame,
                text=f"المتبقي: {remaining:,} دينار",
                font=("Tajawal", 12),
                text_color=RED if remaining > 0 else "#0A0"
            ).pack(side="right", padx=10)

            # أزرار التحكم (الجانب الأيسر)
            buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=200)
            buttons_frame.pack(side="left", fill="y")

            # زر إضافة قسط
            add_payment_btn = ctk.CTkButton(
                buttons_frame,
                text="إضافة قسط",
                fg_color=GOLD,
                text_color=DARK_BG,
                font=("Tajawal", 12, "bold"),
                width=120,
                height=30,
                command=lambda tid=teacher_id, n=name: self.add_payment_for_teacher(tid, n, profile_window)
            )
            add_payment_btn.pack(pady=5)

            # زر تفاصيل الأقساط
            details_btn = ctk.CTkButton(
                buttons_frame,
                text="تفاصيل الأقساط",
                fg_color="#555",
                text_color="white",
                font=("Tajawal", 12, "bold"),
                width=120,
                height=30,
                command=lambda tid=teacher_id, n=name: self.show_payment_details_for_teacher(tid, n)
            )
            details_btn.pack(pady=5)

        # ------ أزرار التحكم العامة ------
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="إغلاق",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            command=profile_window.destroy
        ).pack(side="left", padx=10)

    def add_payment_for_teacher(self, teacher_id, teacher_name, parent_window):
        """إضافة مدفوعات لمدرس معين"""
        # إنشاء نافذة إضافة المدفوعات
        payment_window = ctk.CTkToplevel(parent_window)
        payment_window.title(f"إضافة قسط للمدرس: {teacher_name}")
        payment_window.geometry("500x300")
        payment_window.resizable(False, False)
        payment_window.transient(parent_window)
        payment_window.grab_set()

        # ------ إطار النموذج ------
        form_frame = ctk.CTkFrame(
            payment_window,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # عنوان النافذة
        ctk.CTkLabel(
            form_frame,
            text=f"إضافة قسط للمدرس: {teacher_name}",
            font=("Tajawal", 16, "bold"),
            text_color=GOLD_LIGHT
        ).pack(pady=10)

        # حقل المبلغ
        ctk.CTkLabel(
            form_frame,
            text="المبلغ (دينار):",
            font=("Tajawal", 14)
        ).pack(pady=(10, 0))

        self.amount_var = ctk.StringVar()
        self.amount_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.amount_var,
            font=("Tajawal", 14),
            width=400,
            placeholder_text="أدخل المبلغ المدفوع"
        )
        self.amount_entry.pack(pady=5)

        # حقل الملاحظات
        ctk.CTkLabel(
            form_frame,
            text="ملاحظات:",
            font=("Tajawal", 14)
        ).pack(pady=(10, 0))

        self.payment_notes_var = ctk.StringVar()
        self.payment_notes_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.payment_notes_var,
            font=("Tajawal", 14),
            width=400,
            placeholder_text="أي ملاحظات حول المدفوعات"
        )
        self.payment_notes_entry.pack(pady=5)

        # ------ أزرار التحكم ------
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="حفظ المدفوعات",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=150,
            command=lambda: self.save_teacher_payment(teacher_id, payment_window)
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            button_frame,
            text="إلغاء",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=150,
            command=payment_window.destroy
        ).pack(side="left", padx=10)

    def save_teacher_payment(self, teacher_id, payment_window):
        """حفظ مدفوعات المدرس في قاعدة البيانات"""
        # التحقق من إدخال المبلغ
        try:
            amount = round(float(self.amount_var.get()), 3)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح أكبر من الصفر")
            return

        # الحصول على الملاحظات
        notes = self.payment_notes_var.get().strip()

        # حفظ البيانات في قاعدة البيانات
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO installments (student_id, teacher_id, amount, notes)
                VALUES (?, ?, ?, ?)
            """, (self.student_id, teacher_id, amount, notes))

            conn.commit()
            messagebox.showinfo("نجاح", "تم حفظ المدفوعات بنجاح")
            payment_window.destroy()
            self.show_student_profile()  # إعادة تحميل البروفايل لتحديث البيانات

        except sqlite3.Error as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ المدفوعات:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ غير متوقع:\n{str(e)}")
        finally:
            conn.close()

    def get_teacher_total_fee_by_name(self, teacher_name):
        """استرجاع المبلغ الكلي للمدرس بناءً على الاسم"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()
        try:
            # استخراج الاسم فقط (بدون المادة إذا كان متضمناً)
            name_only = teacher_name.split(" - ")[0].strip()
            cursor.execute("SELECT total_fee FROM teachers WHERE name=?", (name_only,))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            conn.close()
    def generate_payment_receipt_html(self, payment_data):
        """إنشاء HTML للوصل الاحترافي"""
        student_name = self.name_var.get()
        teacher_name = payment_data['teacher_name']
        amount = payment_data['amount']
        payment_date = payment_data['payment_date']
        try:
            # تحويل التاريخ إذا كان بتنسيق SQLite
            payment_date = datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        except:
            # إذا كان التاريخ بالفعل بالتنسيق المطلوب
            pass
        notes = payment_data['notes'] or "لا توجد ملاحظات"

        # حساب المبالغ الكلية والمتبقية (يمكنك تعديل هذا الجزء حسب احتياجاتك)
        total_fee = payment_data.get('total_fee', self.get_teacher_total_fee(payment_data['teacher_id']))
        remaining = payment_data.get('remaining', 0)

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>وصل دفع - معهد صرح البنوك</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .page {{
                    width: 210mm;
                    height: 297mm;
                    margin: 0 auto;
                    background: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    position: relative;
                    page-break-after: always;
                }}
                .receipt {{
                    width: 90%;
                    margin: 0 auto;
                    padding: 15mm 0;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #D4AF37;
                    padding-bottom: 10px;
                }}
                .header h1 {{
                    color: #D4AF37;
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 5px 0;
                    font-size: 16px;
                }}
                .info-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .info-table th, .info-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: right;
                }}
                .info-table th {{
                    background-color: #f2f2f2;
                }}
                .copy {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px dashed #D4AF37;
                }}
                .copy-title {{
                    text-align: center;
                    font-weight: bold;
                    color: #D4AF37;
                    margin-bottom: 10px;
                }}
                .signature {{
                    margin-top: 30px;
                    text-align: left;
                    float: left;
                    width: 40%;
                }}
                .stamp {{
                    margin-top: 30px;
                    text-align: right;
                    float: right;
                    width: 40%;
                }}
                .footer {{
                    clear: both;
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777;
                }}
                @media print {{
                    body {{
                        background: none;
                    }}
                    .page {{
                        box-shadow: none;
                        margin: 0;
                        width: auto;
                        height: auto;
                    }}
                    .no-print {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="receipt">
                    <!-- النسخة الأولى (للمعهد) -->
                    <div class="header">
                        <h1>معهد صرح البنوك</h1>
                        <p>وصل استلام دفعة</p>
                    </div>

                    <table class="info-table">
                        <tr>
                            <th>اسم الطالب:</th>
                            <td>{student_name}</td>
                        </tr>
                        <tr>
                            <th>اسم المدرس:</th>
                            <td>{teacher_name}</td>
                        </tr>
                        <tr>
                            <th>المبلغ المدفوع:</th>
                            <td>{amount:,.3f} دينار</td>
                        </tr>
                        <tr>
                            <th>المبلغ الكلي:</th>
                            <td>{total_fee:,.3f} دينار</td>
                        </tr>
                        <tr>
                            <th>المبلغ المتبقي:</th>
                            <td>{remaining:,.3f} دينار</td>
                        </tr>
                        <tr>
                            <th>تاريخ الدفع:</th>
                            <td>{payment_date}</td>
                        </tr>
                        <tr>
                            <th>ملاحظات:</th>
                            <td>{notes}</td>
                        </tr>
                    </table>

                    <div class="signature">
                        <p>توقيع المسؤول: _________________</p>
                    </div>

                    <div class="stamp">
                        <p>ختم المعهد</p>
                    </div>

                    <div class="footer">
                        <p>شكراً لثقتكم - للاستفسار: 1234567890</p>
                    </div>

                    <!-- النسخة الثانية (للطالب) -->
                    <div class="copy">
                        <div class="copy-title">نسخة الطالب</div>

                        <table class="info-table">
                            <tr>
                                <th>اسم الطالب:</th>
                                <td>{student_name}</td>
                            </tr>
                            <tr>
                                <th>اسم المدرس:</th>
                                <td>{teacher_name}</td>
                            </tr>
                            <tr>
                                <th>المبلغ المدفوع:</th>
                                <td>{amount:,.3f} دينار</td>
                            </tr>
                            <tr>
                                <th>المبلغ الكلي:</th>
                                <td>{total_fee:,.3f} دينار</td>
                            </tr>
                            <tr>
                                <th>المبلغ المتبقي:</th>
                                <td>{remaining:,.3f} دينار</td>
                            </tr>
                            <tr>
                                <th>تاريخ الدفع:</th>
                                <td>{payment_date}</td>
                            </tr>
                            <tr>
                                <th>ملاحظات:</th>
                                <td>{notes}</td>
                            </tr>
                        </table>

                        <div class="signature">
                            <p>توقيع المسؤول: _________________</p>
                        </div>

                        <div class="stamp">
                            <p>ختم المعهد</p>
                        </div>

                        <div class="footer">
                            <p>شكراً لثقتكم - للاستفسار: 1234567890</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="no-print" style="text-align:center; margin:20px;">
                <button onclick="window.print()" style="padding:10px 20px; background:#D4AF37; color:white; border:none; cursor:pointer;">
                    طباعة الوصل
                </button>
            </div>
        </body>
        </html>
        """
        return html

    def print_payment_receipt(self, selected_payment, teacher_name):
        """طباعة وصل الدفع مع تحسينات التعامل مع الأخطاء"""
        try:
            # تحضير بيانات الوصل
            payment_data = {
                'teacher_id': None,  # سيتم تعبئته لاحقاً
                'amount': float(selected_payment[0].replace(" دينار", "").replace(",", "")),
                'payment_date': selected_payment[1],
                'notes': selected_payment[2],
                'teacher_name': teacher_name,
                'total_fee': self.get_teacher_total_fee_by_name(teacher_name),
                'remaining': 0  # سيتم حسابه لاحقاً
            }

            # حساب المبلغ المتبقي
            payment_data['remaining'] = payment_data['total_fee'] - payment_data['amount']

            # إنشاء HTML للوصل
            html_content = self.generate_payment_receipt_html(payment_data)

            # إنشاء مجلد مؤقت إذا لم يكن موجوداً
            temp_dir = os.path.join(os.getcwd(), "temp_receipts")
            os.makedirs(temp_dir, exist_ok=True)

            # حفظ HTML في ملف مؤقت
            temp_file = os.path.join(temp_dir, f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # فتح المتصفح للطباعة
            webbrowser.open(f"file://{temp_file}")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء الوصل:\n{str(e)}")

    def show_payment_details_for_teacher(self, teacher_id, teacher_name):
        """عرض تفاصيل الأقساط للمدرس المحدد"""
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"تفاصيل الأقساط للطالب {self.name_var.get()} لدى المدرس {teacher_name}")
        details_window.geometry("1000x600")  # زيادة الارتفاع لإضافة الزر
        details_window.resizable(False, False)
        details_window.transient(self)
        details_window.grab_set()

        # ------ الإطار الرئيسي ------
        main_frame = ctk.CTkFrame(
            details_window,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # العنوان
        ctk.CTkLabel(
            main_frame,
            text=f"تفاصيل جميع الأقساط للمدرس: {teacher_name}",
            font=("Tajawal", 16, "bold"),
            text_color=GOLD_LIGHT
        ).pack(pady=10)

        # جدول الأقساط
        columns = ("amount", "date", "notes")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

        # تنسيق الجدول
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=DARK_CARD,
                        foreground="white",
                        fieldbackground=DARK_CARD,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=GOLD,
                        foreground=DARK_BG,
                        font=("Tajawal", 12, "bold"))
        style.map("Treeview", background=[("selected", "#444")])

        # عناوين وأعمدة الجدول
        tree_columns = [
            ("amount", "المبلغ", 150),
            ("date", "تاريخ الدفع", 200),
            ("notes", "ملاحظات", 400)
        ]

        for col_id, col_text, col_width in tree_columns:
            tree.heading(col_id, text=col_text)
            tree.column(col_id, width=col_width, anchor="center")

        tree.pack(pady=10, padx=10, fill="both", expand=True)

        # شريط التمرير
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # تحميل بيانات الأقساط
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT amount, payment_date, notes 
            FROM installments
            WHERE student_id = ? AND teacher_id = ?
            ORDER BY payment_date DESC
        """, (self.student_id, teacher_id))

        total_paid = 0
        for amount, payment_date, notes in cursor.fetchall():
            formatted_date = datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            formatted_amount = f"{amount:,.3f} دينار"
            tree.insert("", "end", values=(formatted_amount, formatted_date, notes or "لا توجد ملاحظات"))
            total_paid += amount

        conn.close()

        # إجمالي المدفوعات
        total_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        total_frame.pack(pady=10)

        ctk.CTkLabel(
            total_frame,
            text=f"إجمالي المدفوعات: {total_paid:,.3f} دينار",
            font=("Tajawal", 14, "bold"),
            text_color=GOLD_LIGHT
        ).pack(side="right", padx=20)

        # زر طباعة الوصل
        print_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        print_frame.pack(pady=10)

        def on_print_click():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("تحذير", "يرجى اختيار دفعة لطباعة الوصل")
                return

            selected_payment = tree.item(selected_item)['values']
            self.print_payment_receipt(selected_payment, teacher_name)

        print_btn = ctk.CTkButton(
            print_frame,
            text="طباعة وصل الدفع",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=200,
            command=on_print_click
        )
        print_btn.pack(side="right", padx=10)

        # زر الإغلاق
        close_btn = ctk.CTkButton(
            print_frame,
            text="إغلاق",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=200,
            command=details_window.destroy
        )
        close_btn.pack(side="left", padx=10)

    def get_student_creation_date(self):
        """الحصول على تاريخ تسجيل الطالب"""
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()
        cursor.execute("SELECT created_at FROM students WHERE id=?", (self.student_id,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        return "غير معروف"

    def add_payment(self):
        """إضافة مدفوعات جديدة للطالب عند المدرسين"""
        if not self.student_id:
            messagebox.showwarning("تحذير", "يجب اختيار طالب أولاً")
            return

        # إنشاء نافذة إضافة المدفوعات
        payment_window = ctk.CTkToplevel(self)
        payment_window.title(f"إضافة مدفوعات للطالب: {self.name_var.get()}")
        payment_window.geometry("600x400")
        payment_window.resizable(False, False)
        payment_window.transient(self)
        payment_window.grab_set()

        # ------ إطار النموذج ------
        form_frame = ctk.CTkFrame(
            payment_window,
            fg_color=DARK_CARD,
            border_color=GOLD,
            border_width=2,
            corner_radius=20
        )
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # عنوان النافذة
        ctk.CTkLabel(
            form_frame,
            text="إضافة مدفوعات جديدة",
            font=("Tajawal", 18, "bold"),
            text_color=GOLD_LIGHT
        ).pack(pady=10)

        # ------ حقول الإدخال ------
        # اختيار المدرس
        ctk.CTkLabel(
            form_frame,
            text="اختر المدرس:",
            font=("Tajawal", 14)
        ).pack(pady=(10, 0))

        self.teacher_var = ctk.StringVar()
        self.teacher_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.teacher_var,
            font=("Tajawal", 14),
            width=400
        )
        self.teacher_menu.pack(pady=5)

        # حقل المبلغ
        ctk.CTkLabel(
            form_frame,
            text="المبلغ (دينار):",
            font=("Tajawal", 14)
        ).pack(pady=(10, 0))

        self.amount_var = ctk.StringVar()
        self.amount_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.amount_var,
            font=("Tajawal", 14),
            width=400,
            placeholder_text="أدخل المبلغ المدفوع"
        )
        self.amount_entry.pack(pady=5)

        # حقل الملاحظات
        ctk.CTkLabel(
            form_frame,
            text="ملاحظات:",
            font=("Tajawal", 14)
        ).pack(pady=(10, 0))

        self.payment_notes_var = ctk.StringVar()
        self.payment_notes_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.payment_notes_var,
            font=("Tajawal", 14),
            width=400,
            placeholder_text="أي ملاحظات حول المدفوعات"
        )
        self.payment_notes_entry.pack(pady=5)

        # ------ أزرار التحكم ------
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="حفظ المدفوعات",
            fg_color=GOLD,
            text_color=DARK_BG,
            font=("Tajawal", 14, "bold"),
            width=150,
            command=self.save_payment
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            button_frame,
            text="إلغاء",
            fg_color=RED,
            text_color="white",
            font=("Tajawal", 14, "bold"),
            width=150,
            command=payment_window.destroy
        ).pack(side="left", padx=10)

        # تحميل قائمة المدرسين
        self.load_teachers_for_payment()

    def load_teachers_for_payment(self):
        """تحميل قائمة المدرسين المسجلين للطالب لإضافة المدفوعات"""
        if not self.student_id:
            return

        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.id, t.name, t.subject 
            FROM teachers t
            JOIN student_teacher st ON t.id = st.teacher_id
            WHERE st.student_id = ?
            ORDER BY t.name
        """, (self.student_id,))

        teachers = cursor.fetchall()
        conn.close()

        # تحضير قائمة المدرسين للقائمة المنسدلة
        teacher_options = []
        teacher_data = {}  # لحفظ بيانات المدرسين للاستخدام لاحقاً

        for teacher_id, name, subject in teachers:
            # تصحيح الأسماء الخاطئة
            display_text = f"{name} - {subject}"
            teacher_options.append(display_text)
            teacher_data[display_text] = teacher_id  # حفظ الـ ID للاستخدام عند الحفظ

        if not teacher_options:
            messagebox.showwarning("تحذير", "لا يوجد مدرسين مسجلين لهذا الطالب")
            return

        # تعيين القيم للقائمة المنسدلة
        self.teacher_menu.configure(values=teacher_options)

        # تخزين بيانات المدرسين كخاصية للفئة للوصول إليها لاحقاً
        self._teacher_payment_data = teacher_data

        if teacher_options:  # التحقق من وجود مدرسين قبل التحديد
            self.teacher_var.set(teacher_options[0])  # تحديد أول مدرس افتراضياً

    def save_payment(self):
        """حفظ المدفوعات في قاعدة البيانات"""
        if not self.student_id:
            return

        # التحقق من إدخال المبلغ
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح أكبر من الصفر")
            return

        # الحصول على الـ ID من البيانات المحفوظة
        selected_teacher = self.teacher_var.get()
        teacher_id = self._teacher_payment_data.get(selected_teacher)

        if not teacher_id:
            messagebox.showerror("خطأ", "لم يتم اختيار مدرس صحيح")
            return

        # الحصول على الملاحظات
        notes = self.payment_notes_var.get().strip()

        # حفظ البيانات في قاعدة البيانات
        conn = sqlite3.connect('institute.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO installments (student_id, teacher_id, amount, notes)
                VALUES (?, ?, ?, ?)
            """, (self.student_id, teacher_id, amount, notes))

            conn.commit()
            messagebox.showinfo("نجاح", "تم حفظ المدفوعات بنجاح")

            # إغلاق النافذة بعد الحفظ
            for window in self.winfo_children():
                if isinstance(window, ctk.CTkToplevel):
                    window.destroy()
                    break

            # تحديث بيانات الطالب
            self.load_student_teachers()

        except sqlite3.Error as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ المدفوعات:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ غير متوقع:\n{str(e)}")
        finally:
            conn.close()
    def show_payment_details(self):
        """عرض تفاصيل المدفوعات (وظيفة وهمية)"""
        messagebox.showinfo("تفاصيل المدفوعات", "سيتم عرض تفاصيل جميع المدفوعات")
# الفئة الرئيسية للتطبيق
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("لوحة إدارة المعهد")
        self.geometry("1300x650")
        self.resizable(False, False)
        self.configure(bg_color=DARK_BG)

        # رأس الصفحة
        self.header = ctk.CTkFrame(self, fg_color="transparent", width=1300, height=95)
        self.header.place(x=0, y=16)

        ctk.CTkLabel(self.header,
                     text="نظام إدارة معهد صرح البنوك",
                     font=("Tajawal", 15, "bold"),
                     text_color=GOLD).place(relx=0.5, y=15, anchor="center")

        ctk.CTkLabel(self.header,
                     text="لوحة تحكم المعهد",
                     font=("Tajawal", 32, "bold"),
                     text_color=GOLD_LIGHT).place(relx=0.5, y=50, anchor="center")

        ctk.CTkLabel(self.header,
                     text="إدارة الطلاب، المدرسين، الحسابات، الإحصائيات",
                     font=("Tajawal", 15),
                     text_color="#EEE").place(relx=0.5, y=82, anchor="center")

        # بطاقات الوحدات
        cards_info = [
            ("إدارة الطلاب", "إضافة وتعديل الطلاب وربطهم بالمدرسين ومتابعة كارتات الحجز.", "🧑‍🎓", self.open_students),
            ("إدارة المدرسين", "تسجيل وتعديل المدرسين وتحديد المواد والأقساط والنسب.", "👨‍🏫", self.open_teachers),
            ("إدارة الحسابات", "متابعة الأقساط والمدفوعات والمتبقي للطلاب والمدرسين.", "💵", self.open_accounts),
            ("الإحصائيات", "تقارير وإحصائيات دقيقة لنتائج وأداء المعهد.", "📊", self.open_stats)
        ]

        # إعدادات البطاقات
        card_width = 260
        card_height = 350
        start_x = 90
        start_y = 160
        gap = 30

        # إنشاء البطاقات
        for i, (title, desc, icon, cmd) in enumerate(cards_info):
            card_x = start_x + (i * (card_width + gap))
            ModuleCard(
                master=self,
                title=title,
                desc=desc,
                icon=icon,
                command=cmd,
                card_x=card_x,
                card_y=start_y,
                card_w=card_width,
                card_h=card_height
            )

        # تذييل الصفحة
        self.footer = ctk.CTkLabel(
            self,
            text="© 2025-2026 معهد صرح البنوك. جميع الحقوق محفوظة.",
            font=("Tajawal", 13),
            text_color="#888",
            width=1300,
            height=32
        )
        self.footer.place(x=0, y=620)

        # تهيئة نوافذ التطبيق
        self.students_window = None
        self.teachers_window = None
        self.accounts_window = None
        self.stats_window = None

    def open_students(self):
        if self.students_window is None or not self.students_window.winfo_exists():
            self.students_window = StudentsWindow(self)
        else:
            self.students_window.focus()

    def open_teachers(self):
        if self.teachers_window is None or not self.teachers_window.winfo_exists():
            self.teachers_window = TeachersWindow(self)
        else:
            self.teachers_window.focus()
    def open_accounts(self):
        messagebox.showinfo("فتح نافذة", "سيتم فتح نافذة إدارة الحسابات")

    def open_stats(self):
        messagebox.showinfo("فتح نافذة", "سيتم فتح نافذة الإحصائيات")

# تشغيل التطبيق
if __name__ == "__main__":
    init_db()  # تهيئة قاعدة البيانات
    app = MainApp()
    app.mainloop()