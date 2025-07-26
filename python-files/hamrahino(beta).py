import os
import psycopg2
import bcrypt
import time
import datetime
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import sys

ctk.set_default_color_theme("blue")

KEY_FILE = "aes_key.key"

def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as file:
            return file.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as file:
        file.write(key)
    return key

AES_KEY = load_or_generate_key()
cipher = Fernet(AES_KEY)


class DatabaseManager:
    DB_CONFIG = {
        "host": "grande-casse.liara.cloud",
        "user": "root",
        "password": "udx4Rqjm2JeKoBmSSrLdDUXt",
        "database": "hamrahino",
        "port": 32862
    }

    @staticmethod
    def setup():
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا","اتصال به دستابیس برقرار نشد")
            return
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(225) UNIQUE NOT NULL,
                    password VARCHAR(70) NOT NULL,
                    full_name VARCHAR(255),
                    role VARCHAR(50),
                    school VARCHAR(255),
                    grade VARCHAR(50),
                    age VARCHAR(10),
                    twofactorpassword VARCHAR(255),
                    school_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS program_files (
                student_id INT PRIMARY KEY REFERENCES users(id),
                file_path VARCHAR(255),
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )                      
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS program_requests (
                    id SERIAL PRIMARY KEY,
                    student_id INT REFERENCES users(id) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'در انتظار بررسی' NOT NULL,
                    file_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            ''')   
            cursor.execute("""
                SELECT title, description, status, file_path, created_at 
                FROM program_requests 
                ORDER BY created_at DESC
                LIMIT 1
            """)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS change_requests (
                    id SERIAL PRIMARY KEY,
                    student_id INT REFERENCES users(id),
                    description TEXT,
                    file_path VARCHAR(255),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    sender_id INT REFERENCES users(id),
                    receiver_id INT REFERENCES users(id),
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
        except Exception as e:
            print(f"Error in setup(): {e}")
        finally:
            conn.close()

    
    @staticmethod
    def get_connection():
        try:
            return psycopg2.connect(**DatabaseManager.DB_CONFIG)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    @staticmethod
    def add_student(student_data):
        """افزودن دانش‌آموز جدید به دیتابیس."""
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, full_name, role, school, grade, age)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                student_data['username'],
                student_data['password'],
                student_data['full_name'],  
                student_data.get('role', 'دانش آموز'),
                student_data.get('school', ''),
                student_data.get('grade', ''),
                student_data.get('age', '')
            ))
            student_id = cursor.fetchone()[0]
            conn.commit()
            return str(student_id)
        except Exception as e:
            print(f"خطا در افزودن دانش‌آموز: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def add_admin(admin_data):
        """افزودن مدیر جدید به دیتابیس."""
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, full_name, role, twofactorpassword, school_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                admin_data['username'],
                admin_data['password'],
                admin_data['full_name'],
                admin_data.get('role', 'مدیر'),
                admin_data.get('twofactorpassword'),
                admin_data.get('school_name')
            ))
            admin_id = cursor.fetchone()[0]
            conn.commit()
            return str(admin_id)
        except Exception as e:
            print(f"خطا در افزودن مدیر: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_users():
        """دریافت تمامی کاربران به صورت داینامیک از دیتابیس."""
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            users_dict = {}
            for row in rows:
                user = dict(zip(columns, row))
                users_dict[str(user.get("id"))] = user
            return users_dict
        except Exception as e:
            print(f"Error getting users: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def delete_user(user_id):
        """حذف کاربر و رکوردهای مرتبط با توجه به شناسه."""
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE sender_id = %s OR receiver_id = %s', (user_id, user_id))
            cursor.execute('DELETE FROM program_files WHERE student_id = %s', (user_id,))
            cursor.execute('DELETE FROM change_requests WHERE student_id = %s', (user_id,))
            cursor.execute('DELETE FROM program_requests WHERE student_id = %s', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            if conn:
                conn.close()

class AuthManager:
    """مدیریت تلاش‌های ناموفق ورود و قفل موقت حساب."""
    failed_attempts = {}

    @staticmethod
    def is_account_locked(user_id):
        """بررسی قفل بودن حساب کاربر به دلیل تلاش‌های ناموفق."""
        if user_id in AuthManager.failed_attempts:
            failed_count, last_attempt_time = AuthManager.failed_attempts[user_id]
            if failed_count >= 3:
                lock_time = 60 * 5  
                if time.time() - last_attempt_time < lock_time:
                    return True
                else:
                    AuthManager.failed_attempts[user_id] = [0, time.time()]
        return False

    @staticmethod
    def record_failed_attempt(user_id):
        """ثبت یک تلاش ناموفق برای کاربر."""
        if user_id in AuthManager.failed_attempts:
            failed_count, last_attempt_time = AuthManager.failed_attempts[user_id]
            AuthManager.failed_attempts[user_id] = [failed_count + 1, time.time()]
        else:
            AuthManager.failed_attempts[user_id] = [1, time.time()]

    @staticmethod
    def reset_failed_attempts(user_id):
        """ریست کردن شمارش تلاش‌های ناموفق برای کاربر."""
        if user_id in AuthManager.failed_attempts:
            AuthManager.failed_attempts[user_id] = [0, time.time()]

class Security:
    """متدهای امنیتی برای هش کردن و رمزگشایی."""
    @staticmethod
    def hash_password(password):
        """هش کردن رمز عبور با bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def check_password(stored_hash, provided_password):
        """بررسی تطابق رمز عبور ورودی با هش ذخیره‌شده."""
        return bcrypt.checkpw(provided_password.encode(), stored_hash.encode())
     
    @staticmethod
    def encrypt_data(data):
        """رمزگذاری داده با Fernet."""
        return cipher.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data):
        """رمزگشایی داده با Fernet."""
        return cipher.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def is_valid_codemeli(national_ID: str) -> bool:
        if not national_ID.isdigit() or len(national_ID) != 10:
            return False
        check = int(national_ID[9])
        s = sum(int(national_ID[i]) * (10 - i) for i in range(9))
        r = s % 11
        if r < 2:
            return check == r
        else:
            return check == (11 - r)


class StartPage(ctk.CTkFrame):
    """صفحه شروع (انتخاب نقش کاربر)."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="به همراهینو خوش آمدید", font=ctk.CTkFont(family="B Nazanin", size=30)).pack(pady=10)
        ctk.CTkButton(self, text="ورود دانش‌آموز", command=lambda: controller.show_frame("StudentLoginPage"), font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="ورود مدیر مدرسه", command=lambda: controller.show_frame("ManagerLoginPage"), font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="ورود مشاور", command=lambda: controller.show_frame("AdvisorLoginPage"), font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="ورود ادمین", command=lambda: controller.show_frame("AdminLoginPage"), font=persian_font).pack(pady=10)

class ChatPage(ctk.CTkFrame):
    """صفحه چت بین مشاور و دانش‌آموز با ظاهر مدرن و امکانات کامل"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.chat_partner_id = None
        self.student_list = []
        self.student_id_map = {}

        ctk.CTkLabel(self, text="💬 چت بین مشاور و دانش‌آموز", font=ctk.CTkFont(family="B Nazanin", size=22, weight="bold")).pack(pady=10)

        self.student_combobox = None
        if getattr(controller, 'current_user', None) and controller.current_user.get("role") == "مشاور":
            self.student_combobox = ctk.CTkComboBox(self, values=[], font=self.persian_font, state="readonly", width=300)
            self.student_combobox.pack(pady=5)
            self.student_combobox.bind("<<ComboboxSelected>>", self.on_student_selected)
            self.load_students()

        self.chat_display = tk.Text(self, height=18, state="disabled", font=("B Nazanin", 14), bg="#f5f5fa")
        self.chat_display.pack(padx=12, pady=5, fill="both", expand=True)

        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(fill="x", padx=10, pady=5)
        self.message_entry = ctk.CTkEntry(entry_frame, font=self.persian_font, width=700)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(entry_frame, text="📤 ارسال", command=self.send_message, font=self.persian_font, width=80).pack(side="left")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="🔄 بروزرسانی پیام‌ها", command=self.load_messages, font=self.persian_font, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="بازگشت", command=self._back, font=self.persian_font, width=120).pack(side="left", padx=5)

    def load_students(self):
        """بارگذاری لیست دانش‌آموزان مدرسه مشاور"""
        user = getattr(self.controller, 'current_user', None)
        if not user or user.get("role") != "مشاور":
            return
        school = user.get("school_name")
        conn = DatabaseManager.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name, username FROM users WHERE role = 'دانش آموز' AND school = %s", (school,))
            rows = cursor.fetchall()
            self.student_list = [f"{row[1]} ({row[2]})" for row in rows]
            self.student_id_map = {f"{row[1]} ({row[2]})": row[0] for row in rows}
            if self.student_combobox:
                self.student_combobox.configure(values=self.student_list)
                self.student_combobox.set("")
        except Exception as e:
            pass
        finally:
            conn.close()

    def on_student_selected(self, event=None):
        if self.student_combobox:
            selected = self.student_combobox.get()
            self.chat_partner_id = self.student_id_map.get(selected)
            self.load_messages()

    def refresh_messages(self):
        if getattr(self.controller, 'current_user', None):
            self.load_messages()

    def _back(self):
        role = self.controller.current_user.get("role")
        if role == "مشاور":
            self.controller.show_frame("AdvisorPanelPage")
        else:
            self.controller.show_frame("StudentPanelPage")

    def load_messages(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", tk.END)
        user = self.controller.current_user
        user_id = int(user["id"])
        role = user.get("role")

        conn = DatabaseManager.get_connection()
        if not conn:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد")
            return
        try:
            cursor = conn.cursor()
            if role == "دانش آموز":
                # دانش‌آموز فقط با مشاور مدرسه خود چت می‌کند
                cursor.execute("SELECT id FROM users WHERE role = 'مشاور' AND school_name = %s LIMIT 1", (user.get("school"),))
                row = cursor.fetchone()
                if not row:
                    self.chat_display.insert(tk.END, "مشاور مدرسه شما یافت نشد.")
                    self.chat_display.configure(state="disabled")
                    return
                self.chat_partner_id = row[0]
            elif role == "مشاور":
                if not self.chat_partner_id:
                    self.chat_display.insert(tk.END, "لطفاً یک دانش‌آموز را از لیست انتخاب کنید.")
                    self.chat_display.configure(state="disabled")
                    return
            else:
                self.chat_display.insert(tk.END, "نقش کاربر نامعتبر است.")
                self.chat_display.configure(state="disabled")
                return
            cursor.execute("""
                SELECT sender_id, message, created_at FROM messages
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                ORDER BY created_at ASC
            """, (user_id, self.chat_partner_id, self.chat_partner_id, user_id))
            rows = cursor.fetchall()
            if not rows:
                self.chat_display.insert(tk.END, "هنوز پیامی وجود ندارد.")
            for sender, msg, time in rows:
                name = "من" if sender == user_id else ("مشاور" if role == "دانش آموز" else "دانش‌آموز")
                self.chat_display.insert(tk.END, f"[{time.strftime('%H:%M')}] {name}: {msg}\n")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت پیام‌ها: {e}")
        finally:
            self.chat_display.configure(state="disabled")
            conn.close()

    def send_message(self):
        text = self.message_entry.get().strip()
        if not text:
            return
        user_id = int(self.controller.current_user["id"])
        if not self.chat_partner_id:
            self.load_messages()
            if not self.chat_partner_id:
                return
        conn = DatabaseManager.get_connection()
        if not conn:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد")
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, message)
                VALUES (%s, %s, %s)
            """, (user_id, self.chat_partner_id, text))
            conn.commit()
            self.message_entry.delete(0, tk.END)
            self.load_messages()
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ارسال پیام: {e}")
        finally:
            conn.close()
            
class StudentLoginPage(ctk.CTkFrame):
    """صفحه ورود دانش‌آموز."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="ورود دانش‌آموز", font=persian_font).pack(pady=5)
        ctk.CTkLabel(self, text="کد ملی", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)
        ctk.CTkLabel(self, text="شماره تلفن", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)
        ctk.CTkButton(self, text="ورود", command=self.authenticate_user, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
    
    def authenticate_user(self):
        national_code = self.username_entry.get()
        phone_number = self.password_entry.get()
        users = DatabaseManager.get_all_users()

        for user_id, user in users.items():
            if user.get("username") == national_code and user.get("role") == "دانش آموز":
                if Security.check_password(user['password'], phone_number):
                    self.controller.current_user = {
                        "id": int(user_id),
                        "username": user['username'],
                        "full_name": user['full_name'],
                        "role": user['role'],
                        "school": user.get('school', ''),
                        "grade": user.get('grade', ''),
                        "age": user.get('age', '')
                    }
                    AuthManager.reset_failed_attempts(user_id)
                    messagebox.showinfo("موفقیت", "ورود موفقیت‌آمیز بود")
                    self.controller.show_frame("StudentPanelPage")
                    return
                else:
                    AuthManager.record_failed_attempt(user_id)
        messagebox.showerror("خطا", "کد ملی یا شماره تلفن نادرست است")
      

class StudentPanelPage(ctk.CTkFrame):
    """صفحه اصلی دانش‌آموز"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="پنل دانش‌آموز", font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold")).pack(pady=15)
        ctk.CTkButton(self, text="👤 مشاهده اطلاعات من", command=self.show_info, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📝 درخواست برنامه جدید", command=self.open_plan_request_form, font=self.persian_font).pack(pady=5)

        ctk.CTkButton(self, text="📄 مشاهده برنامه نهایی", command=self.view_final_plan, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="✏️ درخواست تغییر برنامه", command=lambda: controller.show_frame("StudentChangeRequestPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="💬 گفتگو با مشاور", command=lambda: controller.show_frame("ChatPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=self.persian_font).pack(pady=5)

    
    def show_info(self):
        user = self.controller.current_user
        info = f"نام: {user.get('full_name')}\nپایه: {user.get('grade')}\nمدرسه: {user.get('school')}"
        messagebox.showinfo("مشخصات من", info)


    def open_plan_request_form(self):
        form = ctk.CTkToplevel(self)
        form.title("درخواست برنامه جدید")
        form.geometry("400x350")
        persian_font = self.persian_font

        ctk.CTkLabel(form, text="عنوان برنامه:", font=persian_font).pack(pady=8)
        self.plan_title_entry = ctk.CTkEntry(form, font=persian_font, width=320)
        self.plan_title_entry.pack(pady=5)

        ctk.CTkLabel(form, text="توضیحات برنامه:", font=persian_font).pack(pady=8)
        self.plan_desc_entry = ctk.CTkTextbox(form, font=persian_font, height=100, width=320)
        self.plan_desc_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(form)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="ارسال درخواست", command=lambda: self._submit_and_close(form), font=persian_font).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="انصراف", command=form.destroy, font=persian_font).pack(side="left", padx=8)

    def _submit_and_close(self, form):
        self.submit_plan_request()
        form.destroy()
        
    def submit_plan_request(self):
        title = self.plan_title_entry.get().strip()
        desc = self.plan_desc_entry.get("1.0", tk.END).strip()
        student_id = self.controller.current_user.get("id")

        if not title:
            messagebox.showerror("خطا", "عنوان برنامه نمی‌تواند خالی باشد")
            return

        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO program_requests (student_id, title, description, status)
                VALUES (%s, %s, %s, %s)
            """, (student_id, title, desc, "در حال بررسی"))
            conn.commit()
            messagebox.showinfo("ارسال شد", "✅ درخواست برنامه با موفقیت ارسال شد")
            self.plan_title_entry.delete(0, tk.END)
            self.plan_desc_entry.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ارسال درخواست: {e}")
        finally:
            conn.close()

    def view_final_plan(self):
        student_id = self.controller.current_user.get("id")
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, status FROM program_files WHERE student_id = %s", (student_id,))
            row = cursor.fetchone()
            if row:
                file_path, status = row
                messagebox.showinfo("برنامه من", f"وضعیت برنامه: {status}\nمسیر فایل: {file_path}")
            else:
                messagebox.showinfo("برنامه‌ای یافت نشد", "هیچ برنامه‌ای برای شما ثبت نشده است.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت برنامه: {e}")
        finally:
            conn.close()

class StudentChangeRequestPage(ctk.CTkFrame):
    """دانش‌آموز درخواست تغییر برنامه و فایل فعلی را آپلود می‌کند."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.file_path = None

        ctk.CTkLabel(self, text="درخواست تغییر برنامه", font=self.persian_font).pack(pady=10)

        self.description_box = ctk.CTkTextbox(self, height=120, font=self.persian_font)
        self.description_box.pack(padx=10, pady=5, fill="both")
        self.description_box.insert("1.0", "در اینجا تغییرات مورد نظر خود را بنویسید...")

        ctk.CTkButton(self, text="📂 انتخاب فایل برنامه فعلی", command=self.select_file, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📤 ارسال درخواست تغییر", command=self.send_request, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StudentPanelPage"), font=self.persian_font).pack(pady=10)

    def select_file(self):
        filetypes = [("PDF files", "*.pdf"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_path = path
            messagebox.showinfo("فایل انتخاب شد", f"📄 فایل انتخاب‌شده: {os.path.basename(path)}")

    def send_request(self):
        description = self.description_box.get("1.0", tk.END).strip()
        student_id = self.controller.current_user.get("id")

        if not self.file_path or not description:
            messagebox.showerror("خطا", "توضیح تغییر یا فایل انتخاب نشده است")
            return

        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO change_requests (student_id, description, file_path, status)
                VALUES (%s, %s, %s, %s)
            """, (student_id, description, self.file_path, "در انتظار بررسی"))
            conn.commit()
            messagebox.showinfo("درخواست ثبت شد", "✅ درخواست شما برای بررسی ارسال شد")
            self.description_box.delete("1.0", tk.END)
            self.file_path = None
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ارسال درخواست: {e}")
        finally:
            conn.close()

class ManagerLoginPage(ctk.CTkFrame):
    """صفحه ورود مدیر مدرسه."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="ورود مدیر مدرسه", font=persian_font).pack(pady=5)
        ctk.CTkLabel(self, text="کدملی", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)
        ctk.CTkLabel(self, text="شماره تلفن", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)
        ctk.CTkButton(self, text="ورود", command=self.check_credentials, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
    
    def check_credentials(self):
        username = self.username_entry.get().lower()
        password = self.password_entry.get().lower()
        users = DatabaseManager.get_all_users()
        user_id = None
        for uid, user in users.items():
            if user.get('role') == 'مدیر' and user.get('username') == username:
                user_id = uid
                if Security.check_password(user['password'], password):
                    self.controller.current_user = {**user, "id": user_id}
                    AuthManager.reset_failed_attempts(user_id)
                    self.controller.show_frame("twofactorpasswordPage")
                    return
                else:
                    AuthManager.record_failed_attempt(user_id)
                    break
        if user_id and AuthManager.is_account_locked(user_id):
            messagebox.showerror("هشدار", "حساب شما به مدت ۵ دقیقه قفل شده است.")
            return
        messagebox.showerror("خطا", "گذرواژه یا کد ملی نادرست است")


class twofactorpasswordPage(ctk.CTkFrame):
    """صفحه احراز هویت دو مرحله‌ای برای مدیران"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        
        ctk.CTkLabel(self, text="رمز مرحله دوم:", font=persian_font).pack(pady=5)
        self.twofactor_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.twofactor_entry.pack(pady=5)
        
        ctk.CTkButton(self, text="تایید", command=self.verify).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("ManagerLoginPage")).pack(pady=5)

    def verify(self):
        entered_code = self.twofactor_entry.get()
        stored_code = self.controller.current_user.get('twofactorpassword')
        if entered_code == stored_code:
            self.controller.show_frame("SchoolManagerPanelPage")
        else:
            messagebox.showerror("خطا", "رمز مرحله دوم نادرست است!")

class SchoolManagerPanelPage(ctk.CTkFrame):
    """پنل مدیر مدرسه"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="پنل مدیر مدرسه", font=persian_font).pack(pady=10)
        
        ctk.CTkLabel(self, text="دانش آموزان مدرسه من", font=persian_font).pack(pady=5)
        self.student_combobox = ctk.CTkComboBox(self, values=[], font=persian_font, state="readonly")
        self.student_combobox.pack(pady=5)
        self.refresh_student_combobox()
        
        ctk.CTkLabel(self, text="مشاوران مدرسه من", font=persian_font).pack(pady=5)
        self.advisor_combobox = ctk.CTkComboBox(self, values=[], font=persian_font, state="readonly")
        self.advisor_combobox.pack(pady=5)
        self.refresh_advisors()

        ctk.CTkButton(self, text="افزودن دانش‌آموز", command=lambda: controller.show_frame("AddStudentPage"), font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="افزودن مشاور", command=lambda: controller.show_frame("AddAdvisorPage"), font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="حذف دانش‌آموز", command=self.delete_student_action, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="حذف مشاور", command=self.delete_advisor_action, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="🔄 بروزرسانی لیست‌ها", command=self.refresh_all_lists, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
    
    def refresh_all_lists(self):
        self.refresh_student_combobox()
        self.refresh_advisors()
    
    def refresh_student_combobox(self):
        if not self.controller.current_user:
            return
        users = DatabaseManager.get_all_users()
        school_name = self.controller.current_user.get("school_name")
        self.students = {uid: user for uid, user in users.items()
                        if user.get('role') == 'دانش آموز' and user.get('school') == school_name}
        names = []
        for user in self.students.values():
            full_name = user.get('full_name')
            username = user.get('username')
            if full_name:
                names.append(f"{full_name} ({username})")
            else:
                names.append(username)
        self.student_combobox.configure(values=names)
        self.student_combobox.set("")

    def refresh_advisors(self):
        users = DatabaseManager.get_all_users()
        if not self.controller.current_user:
            return
        school = self.controller.current_user.get("school_name")
        self.advisors = {uid: user for uid, user in users.items()
            if user.get("role") == "مشاور" and user.get("school_name") == school}
        names = []
        for user in self.advisors.values():
            full_name = user.get('full_name')
            username = user.get('username')
            if full_name:
                names.append(f"{full_name} ({username})")
            else:
                names.append(username)
        self.advisor_combobox.configure(values=names)
        self.advisor_combobox.set("")

    def delete_student_action(self):
        selected_name = self.student_combobox.get()
        if not selected_name:
            messagebox.showerror("خطا", "لطفاً یک دانش‌آموز را انتخاب کنید")
            return
        if '(' in selected_name and selected_name.endswith(')'):
            username = selected_name.split('(')[-1][:-1].strip()
        else:
            username = selected_name.strip()
        for user_id, user in self.students.items():
            if user.get('username') == username:
                confirm = messagebox.askyesno("تایید", f"آیا مطمئن هستید که می‌خواهید دانش‌آموز {user.get('full_name', user.get('username'))} حذف شود؟")
                if confirm:
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "دانش‌آموز با موفقیت حذف شد.")
                        self.refresh_student_combobox()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف دانش‌آموز.")
                return
        messagebox.showerror("خطا", "دانش‌آموز مورد نظر یافت نشد.")
    
    def delete_advisor_action(self):
        selected_name = self.advisor_combobox.get()
        if not selected_name:
            messagebox.showerror("خطا", "لطفاً یک مشاور را انتخاب کنید")
            return
        if '(' in selected_name and selected_name.endswith(')'):
            username = selected_name.split('(')[-1][:-1].strip()
        else:
            username = selected_name.strip()
        for user_id, user in self.advisors.items():
            if user.get('username') == username:
                confirm = messagebox.askyesno("تایید", f"آیا مطمئن هستید که می‌خواهید مشاور {user.get('full_name', user.get('username'))} حذف شود؟")
                if confirm:
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "مشاور با موفقیت حذف شد.")
                        self.refresh_advisors()
                    else:
                        messagebox.showerror("خطا", "حذف مشاور با خطا مواجه شد.")
                return
        messagebox.showerror("خطا", "مشاور انتخاب‌شده یافت نشد.")
    
    def view_students(self):
        users = DatabaseManager.get_all_users()
        students = {uid: user for uid, user in users.items() if user.get('role') == 'دانش آموز'}
        info = "\n".join(f"{uid}: {user.get('full_name', user.get('username'))}" for uid, user in students.items())
        messagebox.showinfo("دانش‌آموزان", info)


class AdminPanelPage(ctk.CTkFrame):
    """پنل ادمین اصلی"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="پنل مدیریت", font=persian_font).pack(pady=10)
        
        ctk.CTkLabel(self, text="لیست مدیران", font=persian_font).pack(pady=5)
        self.admin_combobox = ctk.CTkComboBox(self, values=[], state="readonly")
        self.admin_combobox.pack(pady=5)
        
        ctk.CTkLabel(self, text="لیست دانش‌آموزان", font=persian_font).pack(pady=5)
        self.student_combobox = ctk.CTkComboBox(self, values=[], state="readonly")
        self.student_combobox.pack(pady=5)
        
        ctk.CTkLabel(self, text="لیست مشاوران", font=persian_font).pack(pady=5)
        self.advisor_combobox = ctk.CTkComboBox(self, values=[], state="readonly", font=persian_font)
        self.advisor_combobox.pack(pady=5)

        ctk.CTkButton(self, text="مشاهده پروفایل مدیر", command=self.view_admin_profile, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="افزودن مدیر", command=lambda: controller.show_frame("AddAdminPage"), font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="حذف مدیر", command=self.delete_admin_action, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="حذف دانش‌آموز", command=self.delete_student_action, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="حذف مشاور", command=self.delete_advisor_action, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="تازه سازی", command=self.refresh_all, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
        

        self.refresh_all()

    def delete_admin_action(self):
        selected_name = self.admin_combobox.get()
        if not hasattr(self, 'admin_users'):
            messagebox.showerror("خطا", "لیست مدیران بارگذاری نشده است.")
            return
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                if messagebox.askyesno("تایید", f"آیا مطمئن هستید که می‌خواهید مدیر {user.get('full_name')} را حذف کنید؟"):
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "مدیر حذف شد")
                        self.refresh_all()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف مدیر")
                return
        messagebox.showerror("خطا", "مدیری انتخاب نشده یا یافت نشد")

    def view_admin_profile(self):
        """نمایش اطلاعات مدیر انتخاب‌شده از کمبوباکس"""
        selected_name = self.admin_combobox.get()
        if not hasattr(self, 'admin_users'):
            messagebox.showerror("خطا", "لیست مدیران بارگذاری نشده است.")
            return
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                info = f"نام: {user.get('full_name', '')}\nکد ملی: {user.get('username', '')}\nمدرسه: {user.get('school_name', '')}\n"
                info += f"گذرواژه مرحله دوم: {user.get('twofactorpassword', '')}"
                messagebox.showinfo("پروفایل مدیر", info)
                return
        messagebox.showerror("خطا", "مدیر انتخاب‌شده یافت نشد.")

    def refresh_all(self):
        """Refresh both admin and student lists."""
        self.load_admins()
        self.refresh_student_list()
        self.refresh_advisor_list()
        self.admin_combobox.set("")
        self.student_combobox.set("")
        self.advisor_combobox.set("")

    def refresh_student_list(self):
        users = DatabaseManager.get_all_users()
        self.student_users = {uid: user for uid, user in users.items() if user.get('role') == 'دانش آموز'}
        names = [user.get('full_name', user.get('username')) for user in self.student_users.values()]
        self.student_combobox.configure(values=names)

    def load_admins(self):
        users = DatabaseManager.get_all_users()
        if users:
            self.admin_users = {uid: user for uid, user in users.items() if user.get('role') == 'مدیر'}
            names = [user.get('full_name', user.get('username')) for uid, user in self.admin_users.items()]
            self.admin_combobox.configure(values=names)
    
    def refresh_advisor_list(self):
        users = DatabaseManager.get_all_users()
        self.advisor_users = {uid: user for uid, user in users.items() if user.get("role") == "مشاور"}
        names = [user.get('full_name', user.get('username')) for user in self.advisor_users.values()]
        self.advisor_combobox.configure(values=names)
                        
    def delete_student_action(self):
        selected_name = self.student_combobox.get()
        for user_id, user in self.student_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                if messagebox.askyesno("تایید", f"آیا مطمئن هستید که می‌خواهید دانش‌آموز {user.get('full_name')} را حذف کنید؟"):
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "دانش‌آموز حذف شد")
                        self.refresh_all()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف دانش‌آموز")
                return
        messagebox.showerror("خطا", "دانش‌آموزی انتخاب نشده یا یافت نشد")

    def delete_advisor_action(self):
        selected_name = self.advisor_combobox.get()
        for uid, user in self.advisor_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                confirm = messagebox.askyesno("تایید", f"آیا مطمئن هستید که می‌خواهید مشاور {user.get('full_name')} حذف شود؟")
                if confirm:
                    if DatabaseManager.delete_user(uid):
                        messagebox.showinfo("موفقیت", "مشاور با موفقیت حذف شد.")
                        self.refresh_all()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف مشاور.")
                return
        messagebox.showerror("خطا", "مشاور انتخاب‌شده یافت نشد.")


class AddStudentPage(ctk.CTkFrame):
    """صفحه افزودن دانش‌آموز جدید."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="افزودن دانش‌آموز", font=persian_font).pack(pady=10)
        
        ctk.CTkLabel(self, text="کد ملی", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="شماره تلفن", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="نام و نام خانوادگی", font=persian_font).pack(pady=5)
        self.fullname_entry = ctk.CTkEntry(self, font=persian_font)
        self.fullname_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="نام مدرسه", font=persian_font).pack(pady=5)
        self.school_entry = ctk.CTkEntry(self, font=persian_font)
        self.school_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="پایه تحصیلی", font=persian_font).pack(pady=5)
        self.grade_entry = ctk.CTkComboBox(self, values=["هفتم", "هشتم", "نهم"], font=persian_font, state="readonly")
        self.grade_entry.pack(pady=10)
        
        ctk.CTkLabel(self, text="سن", font=persian_font).pack(pady=5)
        self.age_entry = ctk.CTkEntry(self, font=persian_font)
        self.age_entry.pack(pady=5)
        
        ctk.CTkButton(self, text="ذخیره", command=self.save_student, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("SchoolManagerPanelPage"), font=persian_font).pack(pady=5)
    
    def save_student(self):
        national_code = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        school = self.school_entry.get().strip()
        grade = self.grade_entry.get().strip()
        age = self.age_entry.get().strip()

        if not Security.is_valid_codemeli(national_code):
            messagebox.showerror("خطا", "کد ملی نامعتبر است")
            return
        if not age.isdigit():
            messagebox.showerror("خطا", "سن باید به صورت عدد وارد شود")
            return

        hashed_password = Security.hash_password(password)
        student_data = {
            "username": national_code,
            "password": hashed_password,
            "full_name": full_name,
            "role": "دانش آموز",
            "school": school,
            "grade": grade,
            "age": age
        }
        student_id = DatabaseManager.add_student(student_data)
        if student_id:
            messagebox.showinfo("موفقیت", "دانش‌آموز با موفقیت افزوده شد!")
        else:
            messagebox.showerror("خطا", "خطا: دانش‌آموز قبلا ثبت شده است")

class AdvisorLoginPage(ctk.CTkFrame):
    """صفحه ورود مشاور."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)

        ctk.CTkLabel(self, text="ورود مشاور", font=persian_font).pack(pady=5)
        ctk.CTkLabel(self, text="کد ملی", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self, text="رمز عبور", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self, text="ورود", command=self.authenticate_advisor, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)

    def authenticate_advisor(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        users = DatabaseManager.get_all_users()

        for user_id, user in users.items():
            if user.get("role") == "مشاور" and user.get("username") == username:
                if Security.check_password(user["password"], password):
                    self.controller.current_user = {
                        "id": user_id,
                        "username": username,
                        "role": "مشاور",
                        "school_name": user.get("school_name")
                    }
                    AuthManager.reset_failed_attempts(user_id)
                    self.controller.show_frame("AdvisorPanelPage")
                    return
        messagebox.showerror("خطا", "اطلاعات ورود نادرست است!")

class AdvisorPanelPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)

        ctk.CTkLabel(self, text="پنل مشاور", font=self.persian_font).pack(pady=10)


        ctk.CTkButton(self, text="💬مشاهده چت‌ها", command=lambda: controller.show_frame("ChatPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📝 برنامه‌های درخواست شده", command=lambda: controller.show_frame("AdvisorRequestReviewPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="✏️ درخواست‌های تغییر برنامه", command=lambda: controller.show_frame("ChangeRequestReviewPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=self.persian_font).pack(pady=5)
            

class AdvisorRequestReviewPage(ctk.CTkFrame):
    """صفحه بررسی درخواست‌های برنامه دانش‌آموزان توسط مشاور"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.selected_request = None
        self.selected_student_id = None
        self.file_path = None

        ctk.CTkLabel(self, text="درخواست‌های برنامه دانش‌آموزان", font=ctk.CTkFont(family="B Nazanin", size=22, weight="bold")).pack(pady=10)

        self.listbox = tk.Listbox(self, font=("B Nazanin", 13), width=90, height=14)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_request_detail)

        self.detail_box = ctk.CTkTextbox(self, height=120, font=self.persian_font)
        self.detail_box.pack(padx=10, pady=5, fill="both")
        self.detail_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=8)
        ctk.CTkButton(btn_frame, text="📂 انتخاب فایل برنامه", command=self.upload_file, font=self.persian_font, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📤 ارسال فایل نهایی و تایید", command=self.send_final_program, font=self.persian_font, width=140).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 بروزرسانی لیست", command=self.refresh_requests, font=self.persian_font, width=120).pack(side="left", padx=5)

        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("AdvisorPanelPage"), font=self.persian_font).pack(pady=10)

        self.refresh_requests()

    def refresh_requests(self):
        """بارگذاری درخواست‌های برنامه دانش‌آموزان مدرسه مشاور"""
        if not self.controller.current_user:
            self.controller.show_frame("AdvisorLoginPage")
            return
        self.listbox.delete(0, tk.END)
        self.requests = []
        school = self.controller.current_user.get("school_name")
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, u.full_name, r.title, r.status, u.school, r.student_id
                FROM program_requests r
                JOIN users u ON r.student_id = u.id
                WHERE u.school = %s
                ORDER BY r.created_at DESC
            """, (school,))
            self.requests = cursor.fetchall()
            for req in self.requests:
                req_id, student_name, title, status, school, student_id = req
                self.listbox.insert(tk.END, f"👤 {student_name} | عنوان: {title} | وضعیت: {status}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت درخواست‌ها: {e}")
        finally:
            conn.close()

    def show_request_detail(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        req = self.requests[selection[0]]
        req_id, student_name, title, status, school, student_id = req
        self.selected_request = req_id
        self.selected_student_id = student_id
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert("1.0", f"👤 دانش‌آموز: {student_name}\n🏫 مدرسه: {school}\n📌 عنوان برنامه: {title}\n📂 وضعیت: {status}\n")
        self.detail_box.configure(state="disabled")

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf"), ("Excel", "*.xlsx"), ("All files", "*.*")])
        if path:
            self.file_path = path
            messagebox.showinfo("فایل انتخاب شد", f"📄 {os.path.basename(path)} انتخاب شد")

    def send_final_program(self):
        if not self.file_path or not self.selected_student_id or not self.selected_request:
            messagebox.showerror("خطا", "لطفاً ابتدا یک درخواست را انتخاب و فایل را بارگذاری کنید.")
            return
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO program_files (student_id, file_path, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id)
                DO UPDATE SET file_path = EXCLUDED.file_path, status = EXCLUDED.status
            """, (self.selected_student_id, self.file_path, "نوشته شده"))
            cursor.execute("UPDATE program_requests SET status = %s WHERE id = %s", ("نوشته شده", self.selected_request))
            conn.commit()
            messagebox.showinfo("ارسال شد", "✅ فایل نهایی با موفقیت ارسال شد و وضعیت بروزرسانی شد")
            self.file_path = None
            self.refresh_requests()
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت فایل: {e}")
        finally:
            conn.close()


class ChangeRequestReviewPage(ctk.CTkFrame):
    """بررسی درخواست‌های تغییر برنامه توسط مشاور یا مدیر."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.selected_request = None
        self.file_path = None

        ctk.CTkLabel(self, text="درخواست‌های تغییر برنامه", font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold")).pack(pady=10)

        self.listbox = tk.Listbox(self, font=("B Nazanin", 12), width=100, height=15)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_request_detail)

        self.detail_box = ctk.CTkTextbox(self, height=150, font=self.persian_font)
        self.detail_box.pack(padx=10, pady=5, fill="both")
        self.detail_box.configure(state="disabled")

        ctk.CTkButton(self, text="📂 انتخاب فایل جدید", command=self.upload_file, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📤 ارسال نسخه اصلاح‌شده", command=self.send_updated_file, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="🔄 بروزرسانی لیست", command=self.refresh_requests, font=self.persian_font).pack(pady=5)

        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("AdvisorPanelPage"), font=self.persian_font).pack(pady=10)


    def refresh_requests(self):
        if not self.controller.current_user:
            self.controller.show_frame("AdvisorLoginPage")
            return
        self.listbox.delete(0, tk.END)
        self.requests = []
        if not self.controller.current_user:
            return 
        school = self.controller.current_user.get("school_name")

        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cr.id, u.full_name, cr.description, cr.status, cr.file_path, cr.student_id
                FROM change_requests cr
                JOIN users u ON cr.student_id = u.id
                WHERE u.school = %s AND cr.status = 'در انتظار بررسی'
                ORDER BY cr.id DESC
            """, (school,))
            self.requests = cursor.fetchall()
            for req in self.requests:
                self.listbox.insert(tk.END, f"{req[1]} | وضعیت: {req[3]}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت درخواست‌ها: {e}")
        finally:
            conn.close()

    def show_request_detail(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        req = self.requests[selection[0]]
        self.selected_request = req
        req_id, name, desc, status, filepath, student_id = req
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert("1.0", f"👤 دانش‌آموز: {name}\n📄 توضیح تغییر: {desc}\n📎 فایل فعلی: {filepath}\n📂 وضعیت: {status}\n")
        self.detail_box.configure(state="disabled")

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf"), ("Excel", "*.xlsx"), ("All files", "*.*")])
        if path:
            self.file_path = path
            messagebox.showinfo("فایل انتخاب شد", f"📄 {os.path.basename(path)} انتخاب شد")

    def send_updated_file(self):
        if not self.selected_request or not self.file_path:
            messagebox.showerror("خطا", "لطفاً ابتدا یک درخواست و یک فایل انتخاب کنید")
            return

        req_id, _, _, _, _, student_id = self.selected_request
        conn = DatabaseManager.get_connection()
        if conn is None:
            messagebox.showerror("خطا", "اتصال به دیتابیس برقرار نشد. برنامه بسته می‌شود.")
            sys.exit(1)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE change_requests SET status = 'تایید شده' WHERE id = %s
            """, (req_id,))
            cursor.execute("""
                INSERT INTO program_files (student_id, file_path, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id)
                DO UPDATE SET file_path = EXCLUDED.file_path, status = EXCLUDED.status
            """, (student_id, self.file_path, "نسخه اصلاح‌شده"))
            conn.commit()
            messagebox.showinfo("ثبت شد", "✅ نسخه اصلاح‌شده ارسال شد و وضعیت درخواست به 'تایید شده' تغییر کرد")
            self.refresh_requests()
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بروزرسانی: {e}")
        finally:
            conn.close()


class AddAdvisorPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)

        ctk.CTkLabel(self, text="افزودن مشاور", font=self.persian_font).pack(pady=10)

        self.username_entry = self._create_entry("کد ملی")
        self.password_entry = self._create_entry("رمز عبور", show=None)
        self.fullname_entry = self._create_entry("نام و نام خانوادگی")

        ctk.CTkButton(self, text="ذخیره", command=self.save_advisor, font=self.persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("SchoolManagerPanelPage"), font=self.persian_font).pack(pady=5)

    def _create_entry(self, label_text, show=None):
        ctk.CTkLabel(self, text=label_text, font=self.persian_font).pack(pady=5)
        entry = ctk.CTkEntry(self, font=self.persian_font, show=show)
        entry.pack(pady=5)
        return entry

    def save_advisor(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()

        if not all([username, password, full_name]):
            messagebox.showerror("خطا", "همه فیلدها الزامی هستند")
            return

        hashed_password = Security.hash_password(password)
        advisor_data = {
            "username": username,
            "password": hashed_password,
            "full_name": full_name,
            "role": "مشاور"
        }

        advisor_id = DatabaseManager.add_admin(advisor_data)
        if advisor_id:
            messagebox.showinfo("موفقیت", "مشاور با موفقیت افزوده شد!")
            self.controller.show_frame("SchoolManagerPanelPage")
        else:
            messagebox.showerror("خطا", "خطا در افزودن مشاور")


class AdminLoginPage(ctk.CTkFrame):
    """صفحه ورود ادمین اصلی"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="ورود ادمین", font=persian_font).pack(pady=5)
        ctk.CTkLabel(self, text="رمز عبور", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)
        ctk.CTkButton(self, text="تایید", command=self.check_admin_password, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
    
    def check_admin_password(self):
        password = self.password_entry.get()
        if password == "2011201013891389":
            self.controller.show_frame("AdminCredentialsPage")
        else:
            messagebox.showerror("خطا", "رمز عبور نادرست است")


class AdminCredentialsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        
        ctk.CTkLabel(self, text="نام کاربری", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="رمز عبور", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)
        
        ctk.CTkButton(self, text="ورود", command=self.authenticate_admin, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
        
    def authenticate_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if (username == "ANFR" and password == "NFRA") or (username == "MMTA" and password == "ATMM"):
            messagebox.showinfo("موفقیت", "ورود ادمین موفقیت‌آمیز بود!")
            self.controller.show_frame("AdminPanelPage")
        else:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور نادرست است")

class AddAdminPage(ctk.CTkFrame):
    """صفحه افزودن مدیر جدید."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)

        ctk.CTkLabel(self, text="افزودن مدیر", font=persian_font).pack(pady=10)

        ctk.CTkLabel(self, text="کد ملی", font=persian_font).pack(pady=5)
        self.username_entry = ctk.CTkEntry(self, font=persian_font)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self, text="شماره تلفن", font=persian_font).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*", font=persian_font)
        self.password_entry.pack(pady=5)

        ctk.CTkLabel(self, text="نام و نام خانوادگی", font=persian_font).pack(pady=5)
        self.fullname_entry = ctk.CTkEntry(self, font=persian_font)
        self.fullname_entry.pack(pady=5)

        ctk.CTkLabel(self, text="گذرواژه مرحله دوم", font=persian_font).pack(pady=5)
        self.twofactor_password_entry = ctk.CTkEntry(self, font=persian_font)
        self.twofactor_password_entry.pack(pady=5)

        ctk.CTkLabel(self, text="نام مدرسه", font=persian_font).pack(pady=5)
        self.school_name_entry = ctk.CTkEntry(self, font=persian_font)
        self.school_name_entry.pack(pady=5)

        ctk.CTkButton(self, text="ذخیره", command=self.save_admin, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("AdminPanelPage"), font=persian_font).pack(pady=5)

    def save_admin(self):
        national_code = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        twofactor_password = self.twofactor_password_entry.get().strip()
        school_name = self.school_name_entry.get().strip()

        if not all([national_code, password, full_name, twofactor_password, school_name]):
            messagebox.showerror("خطا", "لطفا تمام فیلدها را پر کنید")
            return

        if not Security.is_valid_codemeli(national_code):
            messagebox.showerror("خطا", "کد ملی نامعتبر است")
            return
        
        hashed_password = Security.hash_password(password)
        admin_data = {
            "username": national_code,
            "password": hashed_password,
            "full_name": full_name,
            "role": "مدیر",
            "twofactorpassword": twofactor_password,
            "school_name": school_name
        }

        
        admin_id = DatabaseManager.add_admin(admin_data)
        if admin_id:
            messagebox.showinfo("موفقیت", "مدیر با موفقیت افزوده شد!")
            self.controller.show_frame("AdminPanelPage")
        else:
            messagebox.showerror("خطا", "خطا در افزودن مدیر")

class App(ctk.CTk):
    PAGE_ROLES = {
        "AdvisorPanelPage": ["مشاور"],
        "StudentPanelPage": ["دانش آموز"],
        "ManagerPanelPage": ["مدیر"],
        "AdvisorRequestReviewPage": ["مشاور"],
        "ChangeRequestReviewPage": ["مشاور"],
        "StudentChangeRequestPage": ["دانش آموز"],
        "ChatPage": ["مشاور", "دانش آموز"],
        "AdvisorRequestReviewPage": ["مشاور"],
    }

    def __init__(self):
        super().__init__()
        self.title("همراهینو")
        self.geometry("1000x800")
        self.current_user = None
        
        now = datetime.datetime.now()
        if 6 <= now.hour < 18:
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (
            StartPage,
            StudentLoginPage,
            StudentPanelPage,
            ManagerLoginPage,
            twofactorpasswordPage,
            SchoolManagerPanelPage,
            StudentChangeRequestPage,
            AdminLoginPage,
            AdminCredentialsPage,
            AdminPanelPage,
            AddAdvisorPage,
            AdvisorPanelPage,
            AdvisorLoginPage,
            AddStudentPage,
            AdvisorRequestReviewPage,
            AddAdminPage,
            ChangeRequestReviewPage,
            ChatPage,
        ):
            frame = F(parent=container, controller=self)
            name = F.__name__ 
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.theme_button = ctk.CTkButton(self, text="تغییر پس زمینه", font=persian_font, command=self.toggle_theme)
        self.theme_button.pack(pady=10)
        
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        if page_name in self.PAGE_ROLES:
            user = self.current_user
            if not user:
                return
            if user.get("role") not in self.PAGE_ROLES[page_name]:
                messagebox.showerror("دسترسی غیرمجاز", "شما اجازه دسترسی به این بخش را ندارید")
                return
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "ChatPage" and hasattr(frame, "refresh_messages"):
            try:
                frame.refresh_messages()
            except Exception as e:
                print(f"خطا در اجرای refresh_messages برای {page_name}: {e}")
        elif hasattr(frame, "refresh_requests"):
            try:
                frame.refresh_requests()
            except Exception as e:
                print(f"خطا در اجرای refresh_requests برای {page_name}: {e}")

    def toggle_theme(self):
        """تغییر تم بین تاریک و روشن."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode.lower() == "dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    conn = DatabaseManager.get_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
    else:
        print("Database connection failed.")
    DatabaseManager.setup()
    app = App()
    app.mainloop()