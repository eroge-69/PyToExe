# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
from datetime import datetime, date, timedelta
import os
import json
import csv

# اختیاری برای ارسال پیامک واقعی (مثال Kavenegar) – در حالت پیش‌فرض شبیه‌سازی می‌شود
import requests

APP_TITLE = "سیستم مدیریت آموزشگاه موسیقی سیپان"
DB_NAME = "music_school.db"

# ----------------------------- ابزارهای کمکی -----------------------------
def today_str():
    return datetime.now().strftime('%Y-%m-%d')

def now_hms():
    return datetime.now().strftime('%H:%M:%S')

def parse_time_to_minutes(hhmm: str) -> int:
    # انتظار "HH:MM"
    try:
        h, m = hhmm.strip().split(':')
        return int(h) * 60 + int(m)
    except Exception:
        raise ValueError("قالب ساعت باید به صورت HH:MM باشد")

def times_overlap(s1, e1, s2, e2) -> bool:
    # sX و eX بر حسب دقیقه
    return s1 < e2 and s2 < e1

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ----------------------------- برنامه اصلی -----------------------------
class MusicSchoolManager:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x720")
        self.root.configure(bg='#f0f0f0')

        # اتصال دیتابیس
        self.init_database()

        # UI
        self.create_ui()

        # بارگذاری تنظیمات پیامک (پس از ساخت تب مربوطه)
        self.load_sms_settings()

        # مقادیر پیش‌فرض تنظیمات (در صورت نبودن)
        self.ensure_default_settings()

        # رویدادهای کاربردی
        self.student_tree.bind("<Double-1>", lambda e: self.open_student_profile_dialog())

    # ----------------------------- دیتابیس -----------------------------
    def init_database(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

        # جداول اولیه (قدیمی)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                course TEXT,
                registration_date TEXT,
                notes TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                specialty TEXT,
                hire_date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER,
                schedule TEXT,
                price INTEGER,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')

        # مهاجرت و جداول جدید
        self.migrate_database()
        self.conn.commit()

    def migrate_database(self):
        # افزودن ستون‌ها در صورت نبود
        def add_column_if_missing(table, column, coldef):
            self.cursor.execute(f"PRAGMA table_info({table})")
            cols = [r[1] for r in self.cursor.fetchall()]
            if column not in cols:
                self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}")

        add_column_if_missing('students', 'birth_date', 'TEXT')
        add_column_if_missing('students', 'loyalty_points', 'INTEGER DEFAULT 0')

        add_column_if_missing('teachers', 'pay_type', 'TEXT DEFAULT "hourly"')   # hourly|per_student|contract
        add_column_if_missing('teachers', 'pay_rate', 'REAL DEFAULT 0')

        # جداول جدید
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enroll_date TEXT,
                status TEXT DEFAULT 'active',
                tuition INTEGER DEFAULT 0,
                installments INTEGER DEFAULT 1,
                next_due_date TEXT,
                balance INTEGER DEFAULT 0,
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                teacher_id INTEGER,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_online INTEGER DEFAULT 0,
                online_url TEXT,
                content_path TEXT,
                FOREIGN KEY(course_id) REFERENCES courses(id),
                FOREIGN KEY(teacher_id) REFERENCES teachers(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status TEXT CHECK(status IN ('present','absent','late')) DEFAULT 'present',
                recorded_at TEXT,
                UNIQUE(session_id, student_id),
                FOREIGN KEY(session_id) REFERENCES sessions(id),
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                enrollment_id INTEGER,
                amount INTEGER NOT NULL,
                discount INTEGER DEFAULT 0,
                loyalty_used INTEGER DEFAULT 0,
                loyalty_earned INTEGER DEFAULT 0,
                method TEXT,
                date TEXT,
                note TEXT,
                invoice_no TEXT UNIQUE,
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY(course_id) REFERENCES courses(id),
                FOREIGN KEY(enrollment_id) REFERENCES enrollments(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount INTEGER NOT NULL,
                date TEXT,
                note TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                score REAL,
                grade TEXT,
                date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                question TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                student_id INTEGER,
                question_id INTEGER,
                rating INTEGER,
                comment TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                content TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                period TEXT,
                basis TEXT,
                amount INTEGER,
                paid_at TEXT,
                note TEXT
            )
        ''')

        # درج قالب‌های پیش‌فرض پیامک اگر خالی بود
        self.cursor.execute("SELECT COUNT(*) FROM message_templates")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany('''
                INSERT INTO message_templates (name, content) VALUES (?,?)
            ''', [
                ("یادآوری کلاس", "یادآوری کلاس {course} با {teacher} در تاریخ {date} ساعت {time}. آموزشگاه {center_name}"),
                ("یادآوری قسط", "یادآوری قسط شهریه برای {name}: مبلغ {amount} تومان تا تاریخ {date}. آموزشگاه {center_name}"),
                ("تولد", "تولدتان مبارک {name}! از طرف آموزشگاه موسیقی {center_name}")
            ])

    def ensure_default_settings(self):
        def ensure(key, value):
            self.cursor.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?,?)", (key, value))
            self.conn.commit()

        ensure("center_name", "سیپان")
        ensure("invoice_prefix", "SIPAN-INV-")
        ensure("loyalty_amount_per_point", "100000")  # به ازای هر 100هزار تومان = 1 امتیاز
        ensure("loyalty_point_value", "10000")        # هر امتیاز = 10هزار تومان تخفیف
        ensure("invoice_output_dir", os.path.abspath("./invoices"))

    def get_setting(self, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row and row[0] is not None else default

    # ----------------------------- UI -----------------------------
    def create_ui(self):
        toolbar = tk.Frame(self.root, bg='#2c3e50', height=50)
        toolbar.pack(fill=tk.X)
        tk.Label(toolbar, text="آموزشگاه موسیقی سیپان",
                 font=('Tahoma', 16, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # تب‌ها
        self.student_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.student_tab, text='هنرجویان')
        self.create_student_tab()

        self.teacher_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.teacher_tab, text='مدرسان')
        self.create_teacher_tab()

        self.course_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.course_tab, text='دوره‌ها')
        self.create_course_tab()

        self.session_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.session_tab, text='جلسات/برنامه')
        self.create_session_tab()

        self.attendance_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.attendance_tab, text='حضور و غیاب')
        self.create_attendance_tab()

        self.finance_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.finance_tab, text='مالی')
        self.create_finance_tab()

        self.reports_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.reports_tab, text='گزارش‌ها')
        self.create_reports_tab()

        self.sms_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.sms_tab, text='پیامک/اطلاع‌رسانی')
        self.create_sms_tab()

        self.tools_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.tools_tab, text='ابزارها')
        self.create_tools_tab()

    # ----------------------------- هنرجویان -----------------------------
    def create_student_tab(self):
        form = tk.LabelFrame(self.student_tab, text="ثبت نام هنرجو",
                             font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form, text="نام و نام خانوادگی:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.student_name = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.student_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="شماره تماس:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.student_phone = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.student_phone.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="تاریخ تولد (YYYY-MM-DD):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.student_birth = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.student_birth.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="دوره (اختیاری):").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.student_course = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.student_course.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form, text="یادداشت:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.student_notes = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.student_notes.grid(row=2, column=1, padx=5, pady=5)

        btns = tk.Frame(form)
        btns.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(btns, text="ثبت نام", command=self.add_student,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="حذف", command=self.delete_student,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="بروزرسانی", command=self.refresh_students,
                  bg='#3498db', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="ثبت نام در دوره", command=self.enroll_student_dialog,
                  bg='#8e44ad', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="پروفایل هنرجو", command=self.open_student_profile_dialog,
                  bg='#e67e22', fg='white', padx=20).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(self.student_tab, text="لیست هنرجویان",
                                   font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'نام', 'تلفن', 'دوره', 'ثبت‌نام', 'تولد', 'امتیاز')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=130)
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_students()

    def add_student(self):
        name = self.student_name.get().strip()
        phone = self.student_phone.get().strip()
        birth = self.student_birth.get().strip()
        course = self.student_course.get().strip()
        notes = self.student_notes.get().strip()

        if not name or not phone:
            messagebox.showerror("خطا", "نام و شماره تماس الزامی است!")
            return

        self.cursor.execute('''
            INSERT INTO students (name, phone, course, registration_date, notes, birth_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, course, today_str(), notes, birth or None))
        self.conn.commit()

        # پاکسازی
        for w in (self.student_name, self.student_phone, self.student_birth, self.student_course, self.student_notes):
            w.delete(0, tk.END)

        self.refresh_students()
        messagebox.showinfo("موفق", "هنرجو با موفقیت ثبت شد!")

    def delete_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "لطفا یک هنرجو را انتخاب کنید!")
            return
        item = self.student_tree.item(sel)
        student_id = item['values'][0]
        if messagebox.askyesno("تایید", "آیا مطمئن هستید؟"):
            self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            self.cursor.execute("DELETE FROM enrollments WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM payments WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM grades WHERE student_id=?", (student_id,))
            self.conn.commit()
            self.refresh_students()

    def refresh_students(self):
        for i in self.student_tree.get_children():
            self.student_tree.delete(i)
        self.cursor.execute("SELECT id, name, phone, COALESCE(course,''), COALESCE(registration_date,''), COALESCE(birth_date,''), COALESCE(loyalty_points,0) FROM students ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.student_tree.insert('', tk.END, values=row)

    def enroll_student_dialog(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "ابتدا یک هنرجو را از لیست انتخاب کنید.")
            return
        student_id = self.student_tree.item(sel)['values'][0]

        dlg = tk.Toplevel(self.root)
        dlg.title("ثبت نام هنرجو در دوره")
        dlg.geometry("500x280")

        tk.Label(dlg, text="دوره:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.enroll_course_cb = ttk.Combobox(dlg, width=40, state="readonly")
        self.enroll_course_map = self.fetch_courses_combomap()
        self.enroll_course_cb['values'] = [v for (_, v) in self.enroll_course_map]
        self.enroll_course_cb.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dlg, text="شهریه (تومان):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        e_tuition = tk.Entry(dlg); e_tuition.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dlg, text="تعداد اقساط:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        e_inst = tk.Entry(dlg); e_inst.insert(0, "1"); e_inst.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(dlg, text="سررسید قسط اول (YYYY-MM-DD):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        e_due = tk.Entry(dlg); e_due.insert(0, today_str()); e_due.grid(row=3, column=1, padx=5, pady=5)

        def do_enroll():
            try:
                idx = self.enroll_course_cb.current()
                if idx < 0: 
                    messagebox.showerror("خطا", "دوره را انتخاب کنید")
                    return
                course_id = self.enroll_course_map[idx][0]
                tuition = int(e_tuition.get() or "0")
                inst = int(e_inst.get() or "1")
                next_due = e_due.get().strip() or None

                # بررسی تداخل زمانی: جلسات دوره جدید با دوره‌های فعال هنرجو
                if self.student_has_schedule_conflict(student_id, course_id):
                    messagebox.showerror("تداخل زمانی", "برنامه‌ی این دوره با دوره‌های فعال هنرجو تداخل دارد.")
                    return

                self.cursor.execute('''
                    INSERT INTO enrollments (student_id, course_id, enroll_date, tuition, installments, next_due_date, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, course_id, today_str(), tuition, inst, next_due, tuition))
                self.conn.commit()
                messagebox.showinfo("موفق", "ثبت نام انجام شد.")
                dlg.destroy()
            except ValueError:
                messagebox.showerror("خطا", "مقادیر مالی باید عدد باشند.")

        tk.Button(dlg, text="ثبت", command=do_enroll, bg="#27ae60", fg="white").grid(row=4, column=1, sticky='w', padx=5, pady=15)
        tk.Button(dlg, text="بستن", command=dlg.destroy).grid(row=4, column=1, sticky='e', padx=5, pady=15)

    def student_has_schedule_conflict(self, student_id, new_course_id) -> bool:
        # جلسات همه دوره‌های فعال هنرجو
        self.cursor.execute("SELECT course_id FROM enrollments WHERE student_id=? AND status='active'", (student_id,))
        active_courses = [r[0] for r in self.cursor.fetchall()]
        if not active_courses:
            return False
        if new_course_id in active_courses:
            return False

        # جلسات دوره جدید
        self.cursor.execute("SELECT date, start_time, end_time FROM sessions WHERE course_id=?", (new_course_id,))
        new_sessions = self.cursor.fetchall()
        if not new_sessions:
            return False

        # جلسات دوره‌های فعلی
        placeholders = ",".join("?" * len(active_courses))
        self.cursor.execute(f"SELECT date, start_time, end_time FROM sessions WHERE course_id IN ({placeholders})", tuple(active_courses))
        existing = self.cursor.fetchall()

        for d1, s1, e1 in new_sessions:
            s1m, e1m = parse_time_to_minutes(s1), parse_time_to_minutes(e1)
            for d2, s2, e2 in existing:
                if d1 == d2 and times_overlap(s1m, e1m, parse_time_to_minutes(s2), parse_time_to_minutes(e2)):
                    return True
        return False

    def open_student_profile_dialog(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "ابتدا یک هنرجو را انتخاب کنید.")
            return
        student_id, name, phone = self.student_tree.item(sel)['values'][0:3]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"پروفایل هنرجو - {name}")
        dlg.geometry("1000x600")

        info = tk.LabelFrame(dlg, text="اطلاعات پایه"); info.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info, text=f"نام: {name}").pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(info, text=f"تلفن: {phone}").pack(side=tk.LEFT, padx=10, pady=5)

        # ثبت نمره
        grade_frame = tk.LabelFrame(dlg, text="نمرات")
        grade_frame.pack(fill=tk.X, padx=10, pady=5)
        self.profile_course_cb = ttk.Combobox(grade_frame, width=40, state="readonly")
        self.profile_course_map = self.fetch_student_courses_map(student_id)
        self.profile_course_cb['values'] = [v for (_, v) in self.profile_course_map]
        self.profile_course_cb.pack(side=tk.LEFT, padx=5)
        self.profile_score = tk.Entry(grade_frame, width=10); self.profile_score.pack(side=tk.LEFT, padx=5)
        tk.Button(grade_frame, text="ثبت نمره", command=lambda: self.add_grade_from_profile(student_id)).pack(side=tk.LEFT, padx=5)

        # پرداخت از پروفایل
        pay_frame = tk.LabelFrame(dlg, text="پرداخت شهریه")
        pay_frame.pack(fill=tk.X, padx=10, pady=5)
        self.profile_pay_amount = tk.Entry(pay_frame, width=12); self.profile_pay_amount.pack(side=tk.LEFT, padx=5)
        tk.Button(pay_frame, text="پرداخت", command=lambda: self.add_payment_from_profile(student_id)).pack(side=tk.LEFT, padx=5)

        # لیست ثبت‌نام‌ها
        enroll_frame = tk.LabelFrame(dlg, text="ثبت‌نام‌ها")
        enroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ('id','course','enroll_date','status','tuition','balance','next_due')
        self.profile_enroll_tree = ttk.Treeview(enroll_frame, columns=columns, show='headings', height=7)
        for c in columns:
            self.profile_enroll_tree.heading(c, text=c)
            self.profile_enroll_tree.column(c, width=120)
        self.profile_enroll_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_profile_enrollments(student_id)

        # لیست پرداخت‌ها
        payments_frame = tk.LabelFrame(dlg, text="پرداخت‌ها")
        payments_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns2 = ('id','course','amount','discount','date','invoice')
        self.profile_pay_tree = ttk.Treeview(payments_frame, columns=columns2, show='headings', height=7)
        for c in columns2:
            self.profile_pay_tree.heading(c, text=c)
            self.profile_pay_tree.column(c, width=120)
        self.profile_pay_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_profile_payments(student_id)

        # دکمه پیامک شخصی
        tk.Button(dlg, text="ارسال پیامک به هنرجو", command=lambda: self.send_single_sms_dialog(student_id),
                  bg="#e67e22", fg="white").pack(pady=5)

    def fetch_student_courses_map(self, student_id):
        self.cursor.execute('''
            SELECT e.course_id, c.name FROM enrollments e
            JOIN courses c ON e.course_id=c.id
            WHERE e.student_id=? ORDER BY e.id DESC
        ''', (student_id,))
        return [(r[0], r[1]) for r in self.cursor.fetchall()]

    def add_grade_from_profile(self, student_id):
        idx = self.profile_course_cb.current()
        if idx < 0:
            messagebox.showerror("خطا", "دوره را انتخاب کنید")
            return
        course_id = self.profile_course_map[idx][0]
        try:
            score = float(self.profile_score.get())
        except:
            messagebox.showerror("خطا", "نمره باید عدد باشد.")
            return
        self.cursor.execute("INSERT INTO grades (student_id, course_id, score, date) VALUES (?,?,?,?)",
                            (student_id, course_id, score, today_str()))
        self.conn.commit()
        messagebox.showinfo("موفق", "نمره ثبت شد.")

    def refresh_profile_enrollments(self, student_id):
        for i in self.profile_enroll_tree.get_children():
            self.profile_enroll_tree.delete(i)
        self.cursor.execute('''
            SELECT e.id, c.name, e.enroll_date, e.status, e.tuition, e.balance, COALESCE(e.next_due_date,'')
            FROM enrollments e JOIN courses c ON e.course_id=c.id
            WHERE e.student_id=? ORDER BY e.id DESC
        ''', (student_id,))
        for row in self.cursor.fetchall():
            self.profile_enroll_tree.insert('', tk.END, values=row)

    def refresh_profile_payments(self, student_id):
        for i in self.profile_pay_tree.get_children():
            self.profile_pay_tree.delete(i)
        self.cursor.execute('''
            SELECT p.id, c.name, p.amount, p.discount, p.date, COALESCE(p.invoice_no,'')
            FROM payments p LEFT JOIN courses c ON p.course_id=c.id
            WHERE p.student_id=? ORDER BY p.id DESC
        ''', (student_id,))
        for row in self.cursor.fetchall():
            self.profile_pay_tree.insert('', tk.END, values=row)

    def add_payment_from_profile(self, student_id):
        try:
            amount = int(self.profile_pay_amount.get() or "0")
        except:
            messagebox.showerror("خطا", "مبلغ نامعتبر است.")
            return
        # انتخاب آخرین ثبت‌نام فعال برای سادگی
        self.cursor.execute("SELECT id, course_id FROM enrollments WHERE student_id=? AND status='active' ORDER BY id DESC LIMIT 1", (student_id,))
        row = self.cursor.fetchone()
        if not row:
            messagebox.showerror("خطا", "ثبت‌نام فعالی برای هنرجو یافت نشد.")
            return
        enrollment_id, course_id = row
        self._create_payment(student_id, course_id, enrollment_id, amount, discount=0, method="cash", note="پرداخت از پروفایل", print_invoice=True)
        self.profile_pay_amount.delete(0, tk.END)
        self.refresh_profile_payments(student_id)
        self.refresh_profile_enrollments(student_id)
        self.refresh_finance_tables()
        self.refresh_students()

    # ----------------------------- مدرسان -----------------------------
    def create_teacher_tab(self):
        form = tk.LabelFrame(self.teacher_tab, text="ثبت مدرس",
                             font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form, text="نام مدرس:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.teacher_name = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.teacher_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="شماره تماس:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.teacher_phone = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.teacher_phone.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="تخصص:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.teacher_specialty = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.teacher_specialty.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="نوع پرداخت:").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.teacher_paytype = ttk.Combobox(form, width=27, state="readonly",
                                            values=["hourly", "per_student", "contract"])
        self.teacher_paytype.set("hourly")
        self.teacher_paytype.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form, text="نرخ (تومان/ساعت یا نفر):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.teacher_payrate = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.teacher_payrate.insert(0, "0")
        self.teacher_payrate.grid(row=2, column=1, padx=5, pady=5)

        btns = tk.Frame(form); btns.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(btns, text="ثبت مدرس", command=self.add_teacher,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="حذف", command=self.delete_teacher,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="بروزرسانی", command=self.refresh_teachers,
                  bg='#3498db', fg='white', padx=20).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(self.teacher_tab, text="لیست مدرسان", font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID', 'نام', 'تلفن', 'تخصص', 'استخدام', 'نوع پرداخت', 'نرخ')
        self.teacher_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for c in columns:
            self.teacher_tree.heading(c, text=c)
            self.teacher_tree.column(c, width=140)
        self.teacher_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_teachers()

    def add_teacher(self):
        name = self.teacher_name.get().strip()
        phone = self.teacher_phone.get().strip()
        spec = self.teacher_specialty.get().strip()
        paytype = self.teacher_paytype.get().strip()
        try:
            payrate = float(self.teacher_payrate.get() or "0")
        except:
            messagebox.showerror("خطا", "نرخ نامعتبر است.")
            return
        if not name or not phone:
            messagebox.showerror("خطا", "نام و شماره تماس الزامی است!")
            return

        self.cursor.execute('''
            INSERT INTO teachers (name, phone, specialty, hire_date, pay_type, pay_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, spec, today_str(), paytype, payrate))
        self.conn.commit()
        for w in (self.teacher_name, self.teacher_phone, self.teacher_specialty, self.teacher_payrate):
            w.delete(0, tk.END)
        self.teacher_paytype.set("hourly")
        self.refresh_teachers()
        self.refresh_course_teacher_combo()
        messagebox.showinfo("موفق", "مدرس ثبت شد.")

    def delete_teacher(self):
        sel = self.teacher_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "یک مدرس انتخاب کنید!")
            return
        teacher_id = self.teacher_tree.item(sel)['values'][0]
        if messagebox.askyesno("تایید", "حذف مدرس انجام شود؟"):
            self.cursor.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
            self.conn.commit()
            self.refresh_teachers()
            self.refresh_course_teacher_combo()

    def refresh_teachers(self):
        for i in self.teacher_tree.get_children():
            self.teacher_tree.delete(i)
        self.cursor.execute("SELECT id, name, phone, COALESCE(specialty,''), COALESCE(hire_date,''), COALESCE(pay_type,''), COALESCE(pay_rate,0) FROM teachers ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.teacher_tree.insert('', tk.END, values=row)

    # ----------------------------- دوره‌ها -----------------------------
    def create_course_tab(self):
        form = tk.LabelFrame(self.course_tab, text="ثبت دوره",
                             font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form, text="نام دوره:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.course_name = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.course_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="برنامه (توضیح کوتاه):").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.course_schedule = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.course_schedule.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="قیمت (تومان):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.course_price = tk.Entry(form, width=30, font=('Tahoma', 10))
        self.course_price.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="مدرس:").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.course_teacher_cb = ttk.Combobox(form, width=27, state="readonly")
        self.refresh_course_teacher_combo()
        self.course_teacher_cb.grid(row=1, column=3, padx=5, pady=5)

        btns = tk.Frame(form); btns.grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button(btns, text="ثبت دوره", command=self.add_course,
                  bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="حذف", command=self.delete_course,
                  bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="بروزرسانی", command=self.refresh_courses,
                  bg='#3498db', fg='white', padx=20).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(self.course_tab, text="لیست دوره‌ها", font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID', 'نام دوره', 'مدرس', 'برنامه', 'قیمت')
        self.course_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for c in columns:
            self.course_tree.heading(c, text=c)
            self.course_tree.column(c, width=180 if c=='نام دوره' else 140)
        self.course_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_courses()

    def refresh_course_teacher_combo(self):
        self.cursor.execute("SELECT id, name FROM teachers ORDER BY name")
        self.teacher_combo_map = self.cursor.fetchall()
        self.course_teacher_cb['values'] = [r[1] for r in self.teacher_combo_map] if hasattr(self, 'course_teacher_cb') else []

    def add_course(self):
        name = self.course_name.get().strip()
        schedule = self.course_schedule.get().strip()
        price = self.course_price.get().strip()
        t_idx = self.course_teacher_cb.current()
        teacher_id = self.teacher_combo_map[t_idx][0] if t_idx >= 0 else None

        if not name:
            messagebox.showerror("خطا", "نام دوره الزامی است!")
            return
        try:
            price = int(price) if price else 0
        except:
            messagebox.showerror("خطا", "قیمت باید عدد باشد!")
            return

        self.cursor.execute('''
            INSERT INTO courses (name, schedule, price, teacher_id)
            VALUES (?, ?, ?, ?)
        ''', (name, schedule, price, teacher_id))
        self.conn.commit()
        for w in (self.course_name, self.course_schedule, self.course_price):
            w.delete(0, tk.END)
        self.refresh_courses()
        messagebox.showinfo("موفق", "دوره ثبت شد.")

    def delete_course(self):
        sel = self.course_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "لطفا یک دوره را انتخاب کنید!")
            return
        course_id = self.course_tree.item(sel)['values'][0]
        if messagebox.askyesno("تایید", "حذف دوره انجام شود؟"):
            self.cursor.execute("DELETE FROM courses WHERE id=?", (course_id,))
            self.cursor.execute("DELETE FROM enrollments WHERE course_id=?", (course_id,))
            self.cursor.execute("DELETE FROM sessions WHERE course_id=?", (course_id,))
            self.conn.commit()
            self.refresh_courses()

    def refresh_courses(self):
        for i in self.course_tree.get_children():
            self.course_tree.delete(i)
        self.cursor.execute('''
            SELECT c.id, c.name, COALESCE(t.name,'-') AS tname, COALESCE(c.schedule,''), COALESCE(c.price,0)
            FROM courses c LEFT JOIN teachers t ON c.teacher_id=t.id
            ORDER BY c.id DESC
        ''')
        for row in self.cursor.fetchall():
            self.course_tree.insert('', tk.END, values=row)

    def fetch_courses_combomap(self):
        self.cursor.execute('''
            SELECT c.id, c.name || CASE WHEN t.name IS NOT NULL THEN ' (مدرس: '||t.name||')' ELSE '' END
            FROM courses c LEFT JOIN teachers t ON c.teacher_id=t.id ORDER BY c.name
        ''')
        return self.cursor.fetchall()

    # ----------------------------- جلسات/برنامه -----------------------------
    def create_session_tab(self):
        form = tk.LabelFrame(self.session_tab, text="افزودن جلسه/کلاس", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form, text="دوره:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.session_course_cb = ttk.Combobox(form, width=40, state="readonly")
        self.session_course_map = self.fetch_courses_combomap()
        self.session_course_cb['values'] = [v for (_, v) in self.session_course_map]
        self.session_course_cb.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="تاریخ (YYYY-MM-DD):").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.session_date = tk.Entry(form, width=20); self.session_date.insert(0, today_str()); self.session_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form, text="شروع (HH:MM):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.session_start = tk.Entry(form, width=20); self.session_start.insert(0, "16:00"); self.session_start.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="پایان (HH:MM):").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.session_end = tk.Entry(form, width=20); self.session_end.insert(0, "17:00"); self.session_end.grid(row=1, column=3, padx=5, pady=5)

        self.session_is_online = tk.IntVar(value=0)
        tk.Checkbutton(form, text="آنلاین", variable=self.session_is_online).grid(row=2, column=0, sticky='w', padx=5, pady=5)

        tk.Label(form, text="لینک کلاس آنلاین (اختیاری):").grid(row=2, column=1, sticky='e', padx=5, pady=5)
        self.session_url = tk.Entry(form, width=45); self.session_url.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

        tk.Label(form, text="فایل/ویدئوی ضبط‌شده (اختیاری):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.session_content = tk.Entry(form, width=45); self.session_content.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(form, text="انتخاب فایل", command=self.browse_session_content).grid(row=3, column=2, padx=5, pady=5)

        tk.Button(form, text="افزودن جلسه", command=self.add_session, bg="#27ae60", fg="white").grid(row=4, column=1, padx=5, pady=10, sticky='w')
        tk.Button(form, text="بروزرسانی", command=self.refresh_sessions, bg="#3498db", fg="white").grid(row=4, column=2, padx=5, pady=10)
        tk.Button(form, text="حذف", command=self.delete_session, bg="#e74c3c", fg="white").grid(row=4, column=3, padx=5, pady=10)

        list_frame = tk.LabelFrame(self.session_tab, text="لیست جلسات", font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID','دوره','مدرس','تاریخ','شروع','پایان','آنلاین')
        self.session_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for c in columns:
            self.session_tree.heading(c, text=c)
            self.session_tree.column(c, width=150)
        self.session_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_sessions()

    def browse_session_content(self):
        path = filedialog.askopenfilename(title="انتخاب فایل/ویدئو")
        if path:
            self.session_content.delete(0, tk.END)
            self.session_content.insert(0, path)

    def add_session(self):
        idx = self.session_course_cb.current()
        if idx < 0:
            messagebox.showerror("خطا", "دوره را انتخاب کنید")
            return
        course_id = self.session_course_map[idx][0]
        self.cursor.execute("SELECT teacher_id FROM courses WHERE id=?", (course_id,))
        trow = self.cursor.fetchone()
        teacher_id = trow[0] if trow else None
        d = self.session_date.get().strip()
        s = self.session_start.get().strip()
        e = self.session_end.get().strip()
        try:
            sm, em = parse_time_to_minutes(s), parse_time_to_minutes(e)
        except Exception as ex:
            messagebox.showerror("خطا", str(ex)); return
        if sm >= em:
            messagebox.showerror("خطا", "ساعت پایان باید بعد از شروع باشد.")
            return

        # جلوگیری از تداخل زمانی مدرس
        if teacher_id:
            self.cursor.execute("SELECT id, start_time, end_time FROM sessions WHERE date=? AND teacher_id=?", (d, teacher_id))
            for _, s2, e2 in self.cursor.fetchall():
                if times_overlap(sm, em, parse_time_to_minutes(s2), parse_time_to_minutes(e2)):
                    messagebox.showerror("تداخل", "برنامه‌ی این مدرس در این زمان جلسه‌ی دیگری دارد.")
                    return

        self.cursor.execute('''
            INSERT INTO sessions (course_id, teacher_id, date, start_time, end_time, is_online, online_url, content_path)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (course_id, teacher_id, d, s, e, self.session_is_online.get(), self.session_url.get().strip() or None, self.session_content.get().strip() or None))
        self.conn.commit()
        self.refresh_sessions()
        messagebox.showinfo("موفق", "جلسه افزوده شد.")

    def delete_session(self):
        sel = self.session_tree.selection()
        if not sel:
            messagebox.showerror("خطا", "یک جلسه را انتخاب کنید.")
            return
        session_id = self.session_tree.item(sel)['values'][0]
        if messagebox.askyesno("تایید", "حذف جلسه انجام شود؟"):
            self.cursor.execute("DELETE FROM sessions WHERE id=?", (session_id,))
            self.cursor.execute("DELETE FROM attendance WHERE session_id=?", (session_id,))
            self.conn.commit()
            self.refresh_sessions()

    def refresh_sessions(self):
        for i in self.session_tree.get_children():
            self.session_tree.delete(i)
        self.session_course_map = self.fetch_courses_combomap()
        self.session_course_cb['values'] = [v for (_, v) in self.session_course_map]
        self.cursor.execute('''
            SELECT s.id, c.name, COALESCE(t.name,'-'), s.date, s.start_time, s.end_time, CASE s.is_online WHEN 1 THEN 'بله' ELSE 'خیر' END
            FROM sessions s JOIN courses c ON s.course_id=c.id
            LEFT JOIN teachers t ON s.teacher_id=t.id
            ORDER BY s.date DESC, s.start_time DESC
        ''')
        for row in self.cursor.fetchall():
            self.session_tree.insert('', tk.END, values=row)

    # ----------------------------- حضور و غیاب -----------------------------
    def create_attendance_tab(self):
        top = tk.LabelFrame(self.attendance_tab, text="ثبت حضور و غیاب", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="جلسه:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.att_session_cb = ttk.Combobox(top, width=60, state="readonly")
        self.att_session_map = self.fetch_sessions_combomap()
        self.att_session_cb['values'] = [v for (_, v) in self.att_session_map]
        self.att_session_cb.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(top, text="بارگذاری هنرجویان", command=self.load_attendance_students).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(top, text="حاضر", command=lambda: self.set_att_status('present')).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(top, text="غایب", command=lambda: self.set_att_status('absent')).grid(row=0, column=4, padx=5, pady=5)
        tk.Button(top, text="تاخیر", command=lambda: self.set_att_status('late')).grid(row=0, column=5, padx=5, pady=5)
        tk.Button(top, text="ذخیره", command=self.save_attendance, bg="#27ae60", fg="white").grid(row=0, column=6, padx=5, pady=5)

        list_frame = tk.LabelFrame(self.attendance_tab, text="هنرجویان جلسه", font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID','نام','وضعیت')
        self.att_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for c in columns:
            self.att_tree.heading(c, text=c)
            self.att_tree.column(c, width=200 if c=='نام' else 120)
        self.att_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def fetch_sessions_combomap(self):
        self.cursor.execute('''
            SELECT s.id, c.name || ' | ' || s.date || ' ' || s.start_time || '-' || s.end_time
            FROM sessions s JOIN courses c ON s.course_id=c.id
            ORDER BY s.date DESC, s.start_time DESC
        ''')
        return self.cursor.fetchall()

    def load_attendance_students(self):
        self.att_session_map = self.fetch_sessions_combomap()
        self.att_session_cb['values'] = [v for (_, v) in self.att_session_map]
        idx = self.att_session_cb.current()
        if idx < 0:
            messagebox.showerror("خطا", "یک جلسه انتخاب کنید.")
            return
        session_id = self.att_session_map[idx][0]

        for i in self.att_tree.get_children():
            self.att_tree.delete(i)

        # هنرجویان ثبت‌نام‌شده در دوره‌ی این جلسه
        self.cursor.execute("SELECT course_id FROM sessions WHERE id=?", (session_id,))
        cid = self.cursor.fetchone()[0]
        self.cursor.execute('''
            SELECT st.id, st.name
            FROM enrollments e JOIN students st ON e.student_id=st.id
            WHERE e.course_id=? AND e.status='active'
        ''', (cid,))
        students = self.cursor.fetchall()

        # وضعیت‌های موجود
        self.cursor.execute("SELECT student_id, status FROM attendance WHERE session_id=?", (session_id,))
        status_map = {r[0]: r[1] for r in self.cursor.fetchall()}

        for sid, name in students:
            st = status_map.get(sid, '')
            self.att_tree.insert('', tk.END, values=(sid, name, st))

    def set_att_status(self, status):
        for sel in self.att_tree.selection():
            vals = list(self.att_tree.item(sel)['values'])
            vals[2] = status
            self.att_tree.item(sel, values=vals)

    def save_attendance(self):
        idx = self.att_session_cb.current()
        if idx < 0:
            messagebox.showerror("خطا", "جلسه را انتخاب کنید.")
            return
        session_id = self.att_session_map[idx][0]
        for item in self.att_tree.get_children():
            sid, _, status = self.att_tree.item(item)['values']
            if not status:  # اگر خالی رها شده
                continue
            self.cursor.execute('''
                INSERT INTO attendance (session_id, student_id, status, recorded_at)
                VALUES (?,?,?,?)
                ON CONFLICT(session_id, student_id) DO UPDATE SET status=excluded.status, recorded_at=excluded.recorded_at
            ''', (session_id, sid, status, f"{today_str()} {now_hms()}"))
        self.conn.commit()
        messagebox.showinfo("موفق", "حضور و غیاب ذخیره شد.")

    # ----------------------------- مالی -----------------------------
    def create_finance_tab(self):
        wrapper = tk.Frame(self.finance_tab, bg="white")
        wrapper.pack(fill=tk.BOTH, expand=True)

        # پرداخت‌ها
        payments_frame = tk.LabelFrame(wrapper, text="پرداخت شهریه", font=('Tahoma', 10, 'bold'))
        payments_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(payments_frame, text="هنرجو:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.pay_student_cb = ttk.Combobox(payments_frame, width=35, state="readonly")
        self.refresh_pay_students_combo()
        self.pay_student_cb.grid(row=0, column=1, padx=5, pady=5)
        self.pay_student_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_pay_courses_combo())

        tk.Label(payments_frame, text="دوره:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.pay_course_cb = ttk.Combobox(payments_frame, width=35, state="readonly")
        self.pay_course_cb.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(payments_frame, text="مبلغ:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.pay_amount = tk.Entry(payments_frame, width=20); self.pay_amount.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(payments_frame, text="تخفیف:").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.pay_discount = tk.Entry(payments_frame, width=20); self.pay_discount.insert(0, "0"); self.pay_discount.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(payments_frame, text="روش پرداخت:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.pay_method = ttk.Combobox(payments_frame, width=18, state="readonly", values=["cash","card","online"])
        self.pay_method.set("cash"); self.pay_method.grid(row=2, column=1, padx=5, pady=5)

        self.pay_use_points = tk.IntVar(value=0)
        tk.Checkbutton(payments_frame, text="استفاده از امتیاز وفاداری", variable=self.pay_use_points).grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.pay_points_to_use = tk.Entry(payments_frame, width=10); self.pay_points_to_use.insert(0, "0"); self.pay_points_to_use.grid(row=2, column=3, sticky='w', padx=5, pady=5)

        self.pay_print_invoice = tk.IntVar(value=1)
        tk.Checkbutton(payments_frame, text="چاپ فاکتور", variable=self.pay_print_invoice).grid(row=3, column=0, padx=5, pady=5, sticky='w')

        tk.Button(payments_frame, text="ثبت پرداخت", command=self.add_payment, bg="#27ae60", fg="white").grid(row=3, column=3, padx=5, pady=10, sticky='e')

        # جدول پرداخت‌ها
        list_frame = tk.LabelFrame(wrapper, text="لیست پرداخت‌ها", font=('Tahoma', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID','هنرجو','دوره','مبلغ','تخفیف','روش','تاریخ','فاکتور')
        self.payments_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        for c in columns:
            self.payments_tree.heading(c, text=c)
            self.payments_tree.column(c, width=130)
        self.payments_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # هزینه‌ها
        exp_frame = tk.LabelFrame(wrapper, text="ثبت هزینه", font=('Tahoma', 10, 'bold'))
        exp_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(exp_frame, text="دسته:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.exp_cat = tk.Entry(exp_frame, width=28); self.exp_cat.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(exp_frame, text="مبلغ:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.exp_amount = tk.Entry(exp_frame, width=20); self.exp_amount.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(exp_frame, text="توضیح:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.exp_note = tk.Entry(exp_frame, width=60); self.exp_note.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        tk.Button(exp_frame, text="ثبت هزینه", command=self.add_expense, bg="#c0392b", fg="white").grid(row=2, column=3, padx=5, pady=10, sticky='e')

        # جدول هزینه‌ها
        exp_list = tk.LabelFrame(wrapper, text="لیست هزینه‌ها", font=('Tahoma', 10, 'bold'))
        exp_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns2 = ('ID','دسته','مبلغ','تاریخ','توضیح')
        self.expense_tree = ttk.Treeview(exp_list, columns=columns2, show='headings', height=8)
        for c in columns2:
            self.expense_tree.heading(c, text=c)
            self.expense_tree.column(c, width=150)
        self.expense_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # یادآوری اقساط
        tk.Button(wrapper, text="ارسال یادآوری اقساط سررسید", command=self.send_due_reminders, bg="#8e44ad", fg="white").pack(pady=5)

        self.refresh_finance_tables()

    def refresh_pay_students_combo(self):
        self.cursor.execute("SELECT id, name FROM students ORDER BY name")
        self.pay_students_map = self.cursor.fetchall()
        if hasattr(self, 'pay_student_cb'):
            self.pay_student_cb['values'] = [r[1] for r in self.pay_students_map]

    def refresh_pay_courses_combo(self):
        idx = self.pay_student_cb.current()
        if idx < 0:
            self.pay_course_cb['values'] = []
            return
        student_id = self.pay_students_map[idx][0]
        self.cursor.execute('''
            SELECT e.id, c.name FROM enrollments e JOIN courses c ON e.course_id=c.id
            WHERE e.student_id=? AND e.status='active'
        ''', (student_id,))
        self.pay_enroll_map = self.cursor.fetchall()
        self.pay_course_cb['values'] = [r[1] for r in self.pay_enroll_map]

    def add_payment(self):
        sidx = self.pay_student_cb.current()
        eidx = self.pay_course_cb.current()
        if sidx < 0 or eidx < 0:
            messagebox.showerror("خطا", "هنرجو و دوره را انتخاب کنید.")
            return
        student_id = self.pay_students_map[sidx][0]
        enrollment_id, course_name = self.pay_enroll_map[eidx]
        self.cursor.execute("SELECT course_id FROM enrollments WHERE id=?", (enrollment_id,))
        course_id = self.cursor.fetchone()[0]
        try:
            amount = int(self.pay_amount.get() or "0")
            discount = int(self.pay_discount.get() or "0")
        except:
            messagebox.showerror("خطا", "مبالغ باید عدد باشند.")
            return
        method = self.pay_method.get()
        use_points = int(self.pay_points_to_use.get() or "0") if self.pay_use_points.get() else 0
        print_inv = bool(self.pay_print_invoice.get())
        self._create_payment(student_id, course_id, enrollment_id, amount, discount, method, note="", points_to_use=use_points, print_invoice=print_inv)
        self.pay_amount.delete(0, tk.END)
        self.pay_discount.delete(0, tk.END); self.pay_discount.insert(0, "0")
        self.pay_points_to_use.delete(0, tk.END); self.pay_points_to_use.insert(0, "0")
        self.refresh_finance_tables()
        self.refresh_students()

    def _create_payment(self, student_id, course_id, enrollment_id, amount, discount=0, method="cash", note="", points_to_use=0, print_invoice=False):
        # وفاداری
        amount_per_point = int(self.get_setting("loyalty_amount_per_point", "100000"))
        point_value = int(self.get_setting("loyalty_point_value", "10000"))
        loyalty_used_value = points_to_use * point_value
        loyalty_earned = amount // amount_per_point

        # به روزرسانی امتیاز هنرجو
        self.cursor.execute("UPDATE students SET loyalty_points=COALESCE(loyalty_points,0)-?+? WHERE id=?", (points_to_use, loyalty_earned, student_id))

        inv_prefix = self.get_setting("invoice_prefix", "INV-")
        invoice_no = inv_prefix + datetime.now().strftime('%Y%m%d-%H%M%S')

        self.cursor.execute('''
            INSERT INTO payments (student_id, course_id, enrollment_id, amount, discount, loyalty_used, loyalty_earned, method, date, note, invoice_no)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (student_id, course_id, enrollment_id, amount, discount + loyalty_used_value, points_to_use, loyalty_earned, method, today_str(), note, invoice_no))

        # کاهش مانده شهریه (تخفیف نیز کسر می‌شود)
        self.cursor.execute("UPDATE enrollments SET balance = MAX(0, balance - (? + ?)) WHERE id=?", (amount, discount + loyalty_used_value, enrollment_id))

        # جابجایی سررسید قسط بعدی در صورت نیاز
        self.cursor.execute("SELECT balance, next_due_date FROM enrollments WHERE id=?", (enrollment_id,))
        bal, due = self.cursor.fetchone()
        if bal > 0 and due:
            try:
                nxt = (datetime.strptime(due, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
                self.cursor.execute("UPDATE enrollments SET next_due_date=? WHERE id=?", (nxt, enrollment_id))
            except:
                pass

        self.conn.commit()
        if print_invoice:
            self.generate_invoice(invoice_no)
            messagebox.showinfo("فاکتور", f"فاکتور {invoice_no} صادر شد.")

    def add_expense(self):
        try:
            amount = int(self.exp_amount.get() or "0")
        except:
            messagebox.showerror("خطا", "مبلغ هزینه باید عدد باشد.")
            return
        cat = self.exp_cat.get().strip() or "متفرقه"
        note = self.exp_note.get().strip() or ""
        self.cursor.execute("INSERT INTO expenses (category, amount, date, note) VALUES (?,?,?,?)",
                            (cat, amount, today_str(), note))
        self.conn.commit()
        self.exp_cat.delete(0, tk.END)
        self.exp_amount.delete(0, tk.END)
        self.exp_note.delete(0, tk.END)
        self.refresh_finance_tables()

    def refresh_finance_tables(self):
        for i in self.payments_tree.get_children():
            self.payments_tree.delete(i)
        self.cursor.execute('''
            SELECT p.id, s.name, c.name, p.amount, p.discount, COALESCE(p.method,''), p.date, p.invoice_no
            FROM payments p LEFT JOIN students s ON p.student_id=s.id
            LEFT JOIN courses c ON p.course_id=c.id
            ORDER BY p.id DESC
        ''')
        for row in self.cursor.fetchall():
            self.payments_tree.insert('', tk.END, values=row)

        for i in self.expense_tree.get_children():
            self.expense_tree.delete(i)
        self.cursor.execute("SELECT id, category, amount, date, COALESCE(note,'') FROM expenses ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.expense_tree.insert('', tk.END, values=row)

    def send_due_reminders(self):
        # دو روز آینده
        self.cursor.execute('''
            SELECT e.id, s.name, s.phone, e.balance, e.next_due_date
            FROM enrollments e JOIN students s ON e.student_id=s.id
            WHERE e.status='active' AND e.balance>0 AND e.next_due_date IS NOT NULL 
              AND date(e.next_due_date) <= date('now','+2 day')
        ''')
        rows = self.cursor.fetchall()
        if not rows:
            messagebox.showinfo("یادآوری", "مورد سررسید یافت نشد.")
            return
        center = self.get_setting("center_name", "آموزشگاه")
        cnt = 0
        for _, name, phone, bal, due in rows:
            msg = f"یادآوری قسط شهریه برای {name}: مبلغ {bal} تومان تا تاریخ {due}. {center}"
            self._send_sms_simulated([phone], msg)
            cnt += 1
        messagebox.showinfo("یادآوری", f"پیامک یادآوری برای {cnt} مورد ارسال شد (شبیه‌سازی).")

    def generate_invoice(self, invoice_no):
        out_dir = self.get_setting("invoice_output_dir", os.path.abspath("./invoices"))
        ensure_dir(out_dir)
        path = os.path.join(out_dir, f"{invoice_no}.txt")
        # اطلاعات پرداخت
        self.cursor.execute("SELECT p.id, s.name, s.phone, c.name, p.amount, p.discount, p.date FROM payments p LEFT JOIN students s ON p.student_id=s.id LEFT JOIN courses c ON p.course_id=c.id WHERE p.invoice_no=?", (invoice_no,))
        row = self.cursor.fetchone()
        if not row:
            return
        pid, sname, sphone, cname, amount, discount, pdate = row
        center = self.get_setting("center_name", "سیپان")
        content = [
            f"آموزشگاه موسیقی {center}",
            f"شماره فاکتور: {invoice_no}",
            f"تاریخ: {pdate}",
            "-"*40,
            f"هنرجو: {sname} | تلفن: {sphone}",
            f"دوره: {cname or '-'}",
            f"مبلغ: {amount} تومان",
            f"تخفیف/امتیاز: {discount} تومان",
            f"قابل پرداخت: {max(0, amount - discount)} تومان",
            "-"*40,
            "با سپاس از انتخاب شما."
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    # ----------------------------- گزارش‌ها -----------------------------
    def create_reports_tab(self):
        wrap = tk.Frame(self.reports_tab, bg="white")
        wrap.pack(fill=tk.BOTH, expand=True)

        top = tk.LabelFrame(wrap, text="شاخص‌ها", font=('Tahoma', 10, 'bold')); top.pack(fill=tk.X, padx=10, pady=10)
        self.lbl_income = tk.Label(top, text="درآمد: 0"); self.lbl_income.pack(side=tk.LEFT, padx=10, pady=5)
        self.lbl_expense = tk.Label(top, text="هزینه: 0"); self.lbl_expense.pack(side=tk.LEFT, padx=10, pady=5)
        self.lbl_profit = tk.Label(top, text="سود/زیان: 0"); self.lbl_profit.pack(side=tk.LEFT, padx=10, pady=5)
        self.lbl_outstanding = tk.Label(top, text="مانده شهریه: 0"); self.lbl_outstanding.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(top, text="به‌روزرسانی", command=self.refresh_reports).pack(side=tk.RIGHT, padx=10)

        # گزارش حضور و غیاب (۳۰ روز اخیر)
        att = tk.LabelFrame(wrap, text="حضور و غیاب (۳۰ روز اخیر)", font=('Tahoma', 10, 'bold')); att.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('دوره','تعداد حاضر','غایب/تاخیر','درصد حضور')
        self.report_att_tree = ttk.Treeview(att, columns=columns, show='headings', height=10)
        for c in columns:
            self.report_att_tree.heading(c, text=c)
            self.report_att_tree.column(c, width=200 if c=='دوره' else 140)
        self.report_att_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(wrap, text="خروجی CSV از پرداخت‌ها", command=self.export_payments_csv).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(wrap, text="خروجی CSV از هزینه‌ها", command=self.export_expenses_csv).pack(side=tk.LEFT, padx=10, pady=10)

        self.refresh_reports()

    def refresh_reports(self):
        # مالی
        self.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM payments")
        income = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
        expense = self.cursor.fetchone()[0]
        profit = income - expense
        self.cursor.execute("SELECT COALESCE(SUM(balance),0) FROM enrollments WHERE status='active'")
        outstanding = self.cursor.fetchone()[0]

        self.lbl_income.config(text=f"درآمد: {income:,} تومان")
        self.lbl_expense.config(text=f"هزینه: {expense:,} تومان")
        self.lbl_profit.config(text=f"سود/زیان: {profit:,} تومان")
        self.lbl_outstanding.config(text=f"مانده شهریه: {outstanding:,} تومان")

        # حضور و غیاب
        for i in self.report_att_tree.get_children():
            self.report_att_tree.delete(i)
        self.cursor.execute('''
            SELECT c.name,
                   SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS pr,
                   SUM(CASE WHEN a.status!='present' THEN 1 ELSE 0 END) AS ab
            FROM attendance a 
            JOIN sessions s ON a.session_id=s.id
            JOIN courses c ON s.course_id=c.id
            WHERE date(a.recorded_at) >= date('now','-30 day')
            GROUP BY c.id
            ORDER BY c.name
        ''')
        for cname, pr, ab in self.cursor.fetchall():
            total = pr + ab
            rate = (pr / total * 100) if total else 0
            self.report_att_tree.insert('', tk.END, values=(cname, pr, ab, f"{rate:.1f}%"))

    def export_payments_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="payments.csv")
        if not path: return
        self.cursor.execute('''
            SELECT p.id, s.name AS student, c.name AS course, p.amount, p.discount, p.method, p.date, p.invoice_no
            FROM payments p LEFT JOIN students s ON p.student_id=s.id
            LEFT JOIN courses c ON p.course_id=c.id
            ORDER BY p.id DESC
        ''')
        rows = self.cursor.fetchall()
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Student","Course","Amount","Discount","Method","Date","Invoice"])
            writer.writerows(rows)
        messagebox.showinfo("CSV", "فایل payments.csv ذخیره شد.")

    def export_expenses_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="expenses.csv")
        if not path: return
        self.cursor.execute("SELECT id, category, amount, date, note FROM expenses ORDER BY id DESC")
        rows = self.cursor.fetchall()
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Category","Amount","Date","Note"])
            writer.writerows(rows)
        messagebox.showinfo("CSV", "فایل expenses.csv ذخیره شد.")

    # ----------------------------- پیامک/اطلاع‌رسانی -----------------------------
    def create_sms_tab(self):
        settings_frame = tk.LabelFrame(self.sms_tab, text="تنظیمات پیامک", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(settings_frame, text="API Key:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.api_key = tk.Entry(settings_frame, width=40, font=('Tahoma', 10), show='*')
        self.api_key.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(settings_frame, text="شماره فرستنده:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.sender_number = tk.Entry(settings_frame, width=40, font=('Tahoma', 10))
        self.sender_number.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(settings_frame, text="ذخیره تنظیمات", command=self.save_sms_settings, bg='#27ae60', fg='white').grid(row=2, column=1, pady=10, sticky='w')

        group_frame = tk.LabelFrame(self.sms_tab, text="گیرندگان و قالب پیام", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        group_frame.pack(fill=tk.X, padx=10, pady=10)

        self.sms_target = tk.StringVar(value="students")
        ttk.Radiobutton(group_frame, text="همه هنرجویان", variable=self.sms_target, value="students").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(group_frame, text="همه مدرسان", variable=self.sms_target, value="teachers").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(group_frame, text="همه", variable=self.sms_target, value="all").pack(side=tk.LEFT, padx=10)

        tk.Label(group_frame, text="قالب:").pack(side=tk.LEFT, padx=10)
        self.template_cb = ttk.Combobox(group_frame, width=25, state="readonly",
                                        values=["سفارشی","یادآوری کلاس","یادآوری قسط","تولد"])
        self.template_cb.set("سفارشی")
        self.template_cb.pack(side=tk.LEFT, padx=5)
        tk.Button(group_frame, text="اعمال قالب", command=self.apply_template).pack(side=tk.LEFT, padx=5)

        # انتخاب هدف ویژه (دوره/جلسه)
        special = tk.LabelFrame(self.sms_tab, text="فیلتر ویژه (اختیاری)", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        special.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(special, text="دوره:").pack(side=tk.LEFT)
        self.sms_course_cb = ttk.Combobox(special, width=40, state="readonly")
        self.sms_course_map = self.fetch_courses_combomap()
        self.sms_course_cb['values'] = [v for (_, v) in self.sms_course_map]
        self.sms_course_cb.pack(side=tk.LEFT, padx=5)

        tk.Label(special, text="جلسه:").pack(side=tk.LEFT, padx=10)
        self.sms_session_cb = ttk.Combobox(special, width=40, state="readonly")
        self.sms_session_map = self.fetch_sessions_combomap()
        self.sms_session_cb['values'] = [v for (_, v) in self.sms_session_map]
        self.sms_session_cb.pack(side=tk.LEFT, padx=5)

        msg_frame = tk.LabelFrame(self.sms_tab, text="متن پیام", font=('Tahoma', 10, 'bold'), padx=20, pady=10)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.sms_text = scrolledtext.ScrolledText(msg_frame, height=10, width=60, font=('Tahoma', 10))
        self.sms_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btns = tk.Frame(msg_frame); btns.pack(pady=5)
        tk.Button(btns, text="ارسال پیامک", command=self.send_group_sms, bg='#e67e22', fg='white', padx=30, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="یادآوری اقساط امروز", command=self.send_due_reminders, bg='#8e44ad', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="تبریک تولدهای امروز", command=self.send_birthday_sms, bg='#16a085', fg='white', padx=20).pack(side=tk.LEFT, padx=5)

    def apply_template(self):
        tpl = self.template_cb.get()
        center = self.get_setting("center_name", "سیپان")
        if tpl == "یادآوری کلاس":
            self.sms_text.delete('1.0', tk.END)
            self.sms_text.insert(tk.END, f"یادآوری کلاس {{course}} در تاریخ {{date}} ساعت {{time}}. آموزشگاه {center}")
        elif tpl == "یادآوری قسط":
            self.sms_text.delete('1.0', tk.END)
            self.sms_text.insert(tk.END, f"یادآوری قسط شهریه: مبلغ {{amount}} تومان تا تاریخ {{date}}. آموزشگاه {center}")
        elif tpl == "تولد":
            self.sms_text.delete('1.0', tk.END)
            self.sms_text.insert(tk.END, f"تولدتان مبارک {{name}}! از طرف آموزشگاه موسیقی {center}")
        else:
            # سفارشی - دست نزن
            pass

    def save_sms_settings(self):
        settings = {'api_key': self.api_key.get(), 'sender': self.sender_number.get()}
        with open('sms_settings.json', 'w') as f:
            json.dump(settings, f)
        messagebox.showinfo("موفق", "تنظیمات ذخیره شد!")

    def load_sms_settings(self):
        if os.path.exists('sms_settings.json'):
            with open('sms_settings.json', 'r') as f:
                settings = json.load(f)
                self.api_key.insert(0, settings.get('api_key', ''))
                self.sender_number.insert(0, settings.get('sender', ''))

    def _send_sms_simulated(self, numbers, text):
        # اگر API تنظیم نباشد، شبیه‌سازی می‌کنیم
        api_key = self.api_key.get().strip()
        sender = self.sender_number.get().strip()
        if not api_key or not sender:
            messagebox.showinfo("ارسال پیامک (شبیه‌سازی)", f"به {len(set(numbers))} نفر ارسال شد.\n\nمتن:\n{text}")
            return True
        # نمونه واقعی (در حلقه) – برای جلوگیری از کندی، فقط ساختار:
        """
        try:
            url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
            for number in set(numbers):
                data = {'receptor': number,'message': text,'sender': sender}
                requests.post(url, data=data, timeout=10)
            messagebox.showinfo("موفق", f"پیامک به {len(set(numbers))} نفر ارسال شد.")
            return True
        except Exception as e:
            messagebox.showerror("خطا", f"ارسال پیامک ناموفق: {e}")
            return False
        """
        messagebox.showinfo("ارسال پیامک", f"پیامک به {len(set(numbers))} نفر آماده ارسال است (API فعال).")
        return True

    def send_group_sms(self):
        text = self.sms_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showerror("خطا", "متن پیام خالی است!")
            return

        numbers = []
        target = self.sms_target.get()

        # فیلتر دوره/جلسه در صورت انتخاب
        selected_students = set()
        course_id = None
        session_id = None
        if self.sms_course_cb.current() >= 0:
            course_id = self.sms_course_map[self.sms_course_cb.current()][0]
        if self.sms_session_cb.current() >= 0:
            session_id = self.sms_session_map[self.sms_session_cb.current()][0]

        if target in ['students','all']:
            if session_id:
                # هنرجویان همان جلسه
                self.cursor.execute("SELECT course_id FROM sessions WHERE id=?", (session_id,))
                cid = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT s.phone, s.id FROM enrollments e JOIN students s ON e.student_id=s.id WHERE e.course_id=? AND e.status='active'", (cid,))
            elif course_id:
                self.cursor.execute("SELECT s.phone, s.id FROM enrollments e JOIN students s ON e.student_id=s.id WHERE e.course_id=? AND e.status='active'", (course_id,))
            else:
                self.cursor.execute("SELECT phone, id FROM students")
            for ph, sid in self.cursor.fetchall():
                numbers.append(ph); selected_students.add(sid)

        if target in ['teachers','all']:
            self.cursor.execute("SELECT phone FROM teachers")
            numbers.extend([r[0] for r in self.cursor.fetchall()])

        if not numbers:
            messagebox.showerror("خطا", "شماره‌ای یافت نشد.")
            return

        # جایگزینی ساده متغیرها (در صورت یک جلسه/دوره)
        if "{course}" in text or "{date}" in text or "{time}" in text:
            cname, d, t = "-", today_str(), ""
            if session_id:
                self.cursor.execute("SELECT c.name, s.date, s.start_time FROM sessions s JOIN courses c ON s.course_id=c.id WHERE s.id=?", (session_id,))
                r = self.cursor.fetchone()
                if r: cname, d, t = r[0], r[1], r[2]
            elif course_id:
                self.cursor.execute("SELECT name FROM courses WHERE id=?", (course_id,))
                r = self.cursor.fetchone()
                if r: cname = r[0]
            text = text.replace("{course}", str(cname)).replace("{date}", str(d)).replace("{time}", str(t))

        # ارسال
        self._send_sms_simulated(numbers, text)

    def send_birthday_sms(self):
        # تولدهای امروز
        self.cursor.execute("SELECT name, phone FROM students WHERE birth_date IS NOT NULL AND strftime('%m-%d', birth_date)=strftime('%m-%d','now')")
        rows = self.cursor.fetchall()
        if not rows:
            messagebox.showinfo("تولد", "امروز تولدی ثبت نیست.")
            return
        center = self.get_setting("center_name", "سیپان")
        cnt = 0
        for name, phone in rows:
            msg = f"تولدتان مبارک {name}! از طرف آموزشگاه موسیقی {center}"
            self._send_sms_simulated([phone], msg)
            cnt += 1
        messagebox.showinfo("تولد", f"برای {cnt} نفر پیام تبریک ارسال شد (شبیه‌سازی).")

    # ----------------------------- ابزارها -----------------------------
    def create_tools_tab(self):
        wrap = tk.Frame(self.tools_tab, bg="white")
        wrap.pack(fill=tk.BOTH, expand=True)

        inv = tk.LabelFrame(wrap, text="فاکتور/رسید", font=('Tahoma', 10, 'bold')); inv.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(inv, text="شماره فاکتور:").pack(side=tk.LEFT, padx=5)
        self.tool_invoice_no = tk.Entry(inv, width=30); self.tool_invoice_no.pack(side=tk.LEFT, padx=5)
        tk.Button(inv, text="تولید مجدد فایل فاکتور", command=lambda: self.generate_invoice(self.tool_invoice_no.get().strip()),
                  bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=5)

        cid = tk.LabelFrame(wrap, text="جست‌وجو با شماره تماس (Caller ID ساده)", font=('Tahoma', 10, 'bold')); cid.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(cid, text="شماره:").pack(side=tk.LEFT, padx=5)
        self.tool_phone_lookup = tk.Entry(cid, width=30); self.tool_phone_lookup.pack(side=tk.LEFT, padx=5)
        tk.Button(cid, text="باز کردن پروفایل", command=self.open_profile_by_phone).pack(side=tk.LEFT, padx=5)

        sets = tk.LabelFrame(wrap, text="تنظیمات مؤسسه و وفاداری", font=('Tahoma', 10, 'bold')); sets.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(sets, text="نام آموزشگاه:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.set_center_name = tk.Entry(sets, width=30); self.set_center_name.insert(0, self.get_setting("center_name","سیپان")); self.set_center_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(sets, text="پیشوند فاکتور:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.set_inv_prefix = tk.Entry(sets, width=30); self.set_inv_prefix.insert(0, self.get_setting("invoice_prefix","SIPAN-INV-")); self.set_inv_prefix.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(sets, text="مبلغ/هر امتیاز (تومان):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.set_amt_per_point = tk.Entry(sets, width=30); self.set_amt_per_point.insert(0, self.get_setting("loyalty_amount_per_point","100000")); self.set_amt_per_point.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(sets, text="ارزش هر امتیاز (تومان):").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.set_point_value = tk.Entry(sets, width=30); self.set_point_value.insert(0, self.get_setting("loyalty_point_value","10000")); self.set_point_value.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(sets, text="مسیر ذخیره فاکتورها:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.set_inv_dir = tk.Entry(sets, width=60); self.set_inv_dir.insert(0, self.get_setting("invoice_output_dir", os.path.abspath("./invoices"))); self.set_inv_dir.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        tk.Button(sets, text="ذخیره تنظیمات", command=self.save_center_settings, bg="#27ae60", fg="white").grid(row=3, column=3, padx=5, pady=10, sticky='e')

    def save_center_settings(self):
        items = [
            ("center_name", self.set_center_name.get().strip() or "سیپان"),
            ("invoice_prefix", self.set_inv_prefix.get().strip() or "SIPAN-INV-"),
            ("loyalty_amount_per_point", self.set_amt_per_point.get().strip() or "100000"),
            ("loyalty_point_value", self.set_point_value.get().strip() or "10000"),
            ("invoice_output_dir", self.set_inv_dir.get().strip() or os.path.abspath("./invoices"))
        ]
        for k, v in items:
            self.cursor.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, v))
        self.conn.commit()
        messagebox.showinfo("تنظیمات", "ذخیره شد.")

    def open_profile_by_phone(self):
        phone = (self.tool_phone_lookup.get() or "").strip()
        if not phone:
            return
        self.cursor.execute("SELECT id FROM students WHERE phone=?", (phone,))
        r = self.cursor.fetchone()
        if not r:
            messagebox.showinfo("یافت نشد", "هنرجویی با این شماره ثبت نشده است.")
            return
        # انتخاب سطر هنرجو
        sid = r[0]
        for item in self.student_tree.get_children():
            if self.student_tree.item(item)['values'][0] == sid:
                self.student_tree.selection_set(item)
                self.student_tree.see(item)
                break
        self.open_student_profile_dialog()

    # ----------------------------- پایان -----------------------------
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicSchoolManager(root)
    root.mainloop()
