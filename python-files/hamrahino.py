import os
import psycopg2
import bcrypt
import time
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkinter import Listbox

ctk.set_appearance_mode("Dark")
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
        cursor = conn.cursor()
        

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(225) UNIQUE NOT NULL,
                password VARCHAR(30) NOT NULL,
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
            CREATE TABLE IF NOT EXISTS predefined_questions (
                id SERIAL PRIMARY KEY,
                question_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_answers (
                id SERIAL PRIMARY KEY,
                question_id INT REFERENCES predefined_questions(id),
                student_id INT REFERENCES users(id),
                answer TEXT NOT NULL,
                additional_notes TEXT,
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
        
        conn.commit()
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
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            if conn is None:
                print("اتصال به دیتابیس برقرار نشد.")
                return None
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
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            if conn is None:
                print("اتصال به دیتابیس برقرار نشد.")
                return None
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
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            if conn is None:
                print("Error: Database connection failed.")
                return {}
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
        """حذف کاربر با توجه به شناسه."""
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
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
    """صفحه اصلی دانش‌آموز برای دسترسی به امکانات مختلف"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="پنل دانش‌آموز", font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold")).pack(pady=15)
        ctk.CTkButton(self, text="👤 مشاهده اطلاعات من", command=self.show_info, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📝 درخواست برنامه جدید", command=self.request_plan, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📄 مشاهده برنامه نهایی", command=self.view_final_plan, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="✏️ درخواست تغییر برنامه", command=lambda: controller.show_frame("StudentChangeRequestPage"), font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="💬 گفتگو با مشاور", command=self.chat_with_advisor, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=self.persian_font).pack(pady=5)


        ctk.CTkLabel(self, text="عنوان برنامه پیشنهادی", font=self.persian_font).pack(pady=(20, 5))
        self.plan_title_entry = ctk.CTkEntry(self, font=self.persian_font)
        self.plan_title_entry.pack(pady=5)

        ctk.CTkLabel(self, text="توضیحات", font=self.persian_font).pack(pady=5)
        self.plan_desc_entry = ctk.CTkTextbox(self, height=100, font=self.persian_font)
        self.plan_desc_entry.pack(pady=5)

        ctk.CTkButton(self, text="📨 ارسال درخواست برنامه", command=self.submit_plan_request, font=self.persian_font).pack(pady=10)
    
    def show_info(self):
        user = self.controller.current_user
        info = f"نام: {user.get('full_name')}\nپایه: {user.get('grade')}\nمدرسه: {user.get('school')}"
        messagebox.showinfo("مشخصات من", info)

    def request_plan(self):
        messagebox.showinfo("راهنما", "لطفاً فرم پایین را برای درخواست برنامه پر کنید.")

    def submit_plan_request(self):
        title = self.plan_title_entry.get().strip()
        desc = self.plan_desc_entry.get("1.0", tk.END).strip()
        student_id = self.controller.current_user.get("id")

        if not title:
            messagebox.showerror("خطا", "عنوان برنامه نمی‌تواند خالی باشد")
            return

        try:
            conn = DatabaseManager.get_connection()
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
        try:
            conn = DatabaseManager.get_connection()
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

    def chat_with_advisor(self):
        messagebox.showerror("خطا","این بخش بزودی اضافه خواهد شد")

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

        try:
            conn = DatabaseManager.get_connection()
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
        for user_id, user in users.items():
            if user.get('role') == 'مدیر' and user.get('username') == username:
                if Security.check_password(user['password'], password):
                    self.controller.current_user = {**user, "id": user_id}
                    AuthManager.reset_failed_attempts(user_id)
                    self.controller.show_frame("twofactorpasswordPage")
                    return
                else:
                    AuthManager.record_failed_attempt(user_id)
        if AuthManager.is_account_locked(user_id):
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
    """پنل مدیر مدرسه (مشاهده و افزودن دانش‌آموز)."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        ctk.CTkLabel(self, text="پنل مدیر مدرسه", font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="مشاهده دانش‌آموزان", command=self.view_students, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="افزودن دانش‌آموز", command=lambda: controller.show_frame("AddStudentPage"), font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="افزودن مشاور", command=lambda: controller.show_frame("AddAdvisorPage"), font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
    
    def view_students(self):
        users = DatabaseManager.get_all_users()
        students = {uid: user for uid, user in users.items() if user.get('role') == 'دانش آموز'}
        info = "\n".join(f"{uid}: {user.get('full_name', user.get('username'))}" for uid, user in students.items())
        messagebox.showinfo("دانش‌آموزان", info)


class AdminPanelPage(ctk.CTkFrame):
    """پنل ادمین اصلی برای مدیریت مدیران و مشاهده دانش‌آموزان."""
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
        
        ctk.CTkButton(self, text="مشاهده پروفایل مدیر", command=self.view_admin_profile, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="حذف مدیر", command=self.delete_admin_action, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="افزودن مدیر", command=lambda: controller.show_frame("AddAdminPage"), font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="تازه سازی", command=self.refresh_all, font=persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=persian_font).pack(pady=5)
        

        self.refresh_all()

    def refresh_all(self):
        """Refresh both admin and student lists."""
        self.load_admins()
        self.refresh_student_list()
        self.admin_combobox.set("")
        self.student_combobox.set("")

    def load_admins(self):
        users = DatabaseManager.get_all_users()
        if users:
            self.admin_users = {uid: user for uid, user in users.items() if user.get('role') == 'مدیر'}
            names = [user.get('full_name', user.get('username')) for uid, user in self.admin_users.items()]
            self.admin_combobox.configure(values=names)
    
    def refresh_student_list(self):
        users = DatabaseManager.get_all_users()
        if users:
            self.student_users = {uid: user for uid, user in users.items() if user.get('role') == 'دانش آموز'}
            names = [user.get('full_name', user.get('username')) for uid, user in self.student_users.items()]
            self.student_combobox.configure(values=names)
    
    def view_admin_profile(self):
        selected_name = self.admin_combobox.get()
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                profile_info = (f"کد ملی: {user.get('username')}\n"
                                f"نام و نام خانوادگی: {user.get('full_name')}\n"
                                f"نقش: {user.get('role')}\n"
                                f"رمز مرحله دوم: {user.get('twofactorpassword')}\n"
                                f"نام مدرسه: {user.get('school_name')}")
                messagebox.showinfo("پروفایل مدیر", profile_info)
                return
        messagebox.showerror("خطا", "مدیری انتخاب نشده است")
    
    def delete_admin_action(self):
        selected_name = self.admin_combobox.get()
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                if messagebox.askyesno("تایید", "آیا مطمئن هستید که می‌خواهید این مدیر را حذف کنید؟"):
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "مدیر حذف شد")
                        self.refresh_all()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف مدیر")
                return
        messagebox.showerror("خطا", "مدیری انتخاب نشده است")

class AddAdvisorPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        
        ctk.CTkLabel(self, text="افزودن مشاور جدید", font=persian_font).pack(pady=10)
        
        fields = [
            ("کد ملی", "username_entry"),
            ("شماره تلفن", "password_entry"),
            ("نام کامل", "fullname_entry"),
            ("نام مدرسه", "school_entry")
        ]
        
        self.entries = {}
        for label, name in fields:
            ctk.CTkLabel(self, text=label, font=persian_font).pack(pady=5)
            entry = ctk.CTkEntry(self, font=persian_font)
            entry.pack(pady=5)
            self.entries[name] = entry

        ctk.CTkButton(self, text="ذخیره", command=self.save_advisor, font=persian_font).pack(pady=10)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("SchoolManagerPanelPage"), font=persian_font).pack(pady=5)

    def save_advisor(self):
        advisor_data = {
            'username': self.entries['username_entry'].get(),
            'password': Security.hash_password(self.entries['password_entry'].get()),
            'full_name': self.entries['fullname_entry'].get(),
            'role': 'مشاور',
            "school_name": self.school_entry.get().strip() 
        }
        
        if DatabaseManager.add_admin(advisor_data):
            messagebox.showinfo("موفقیت", "مشاور با موفقیت اضافه شد")
            self.controller.show_frame("SchoolManagerPanelPage")


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
        phone_number = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        school = self.school_entry.get().strip()
        grade = self.grade_entry.get().strip()
        age = self.age_entry.get().strip()

        if not national_code.isdigit() or len(national_code) != 10:
            messagebox.showerror("خطا", "کد ملی باید 10 رقمی و فقط شامل ارقام باشد")
            return
        if not age.isdigit():
            messagebox.showerror("خطا", "سن باید به صورت عدد وارد شود")
            return

        hashed_password = Security.hash_password(phone_number)
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

        ctk.CTkButton(self, text="💬مشاهده چت‌ها", command=self.goto_chat, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self,text="دانش‌آموزان من",command=lambda: messagebox.showerror("خطا","این بخش بزودی اضافه خواهد شده"),font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📝 برنامه های درخواست شده", command=  lambda: messagebox.showerror("خطا","این بخش بزودی اضافه خواهد شده"),font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=self.persian_font).pack(pady=5)

    def goto_chat(self):
        messagebox.showerror("خطا","این بخش بزودی اضافه خواهد شد")

            
class AdvisorRequestReviewPage(ctk.CTkFrame):
    """صفحه بررسی درخواست‌های برنامه توسط مشاور"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        if not controller.current_user:
            controller.show_frame("AdvisorLoginPage")
            return

        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.selected_request_id = None
        self.file_path = None
        self.persian_font = ctk.CTkFont(family="B Nazanin", size=20)
        self.selected_request_id = None
        self.selected_student_id = None
        self.file_path = None

        ctk.CTkLabel(self, text="درخواست‌های برنامه دانش‌آموزان", font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold")).pack(pady=10)

        self.listbox = tk.Listbox(self, font=("B Nazanin", 12), width=100, height=15)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_request_detail)

        self.detail_box = ctk.CTkTextbox(self, height=150, font=self.persian_font)
        self.detail_box.pack(padx=10, pady=5, fill="both")
        self.detail_box.configure(state="disabled")

        ctk.CTkButton(self, text="📂 انتخاب فایل برنامه", command=self.upload_file, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="📤 ارسال فایل نهایی و تایید", command=self.send_final_program, font=self.persian_font).pack(pady=5)
        ctk.CTkButton(self, text="🔄 بروزرسانی لیست", command=self.refresh_requests, font=self.persian_font).pack(pady=5)

        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("AdvisorPanelPage"), font=self.persian_font).pack(pady=10)

        self.refresh_requests()

    def refresh_requests(self):
        """بارگذاری درخواست‌های مرتبط با مدرسه مشاور"""
        if not self.controller.current_user:
            self.controller.show_frame("AdvisorLoginPage")
            return

        self.listbox.delete(0, tk.END)
        school = self.controller.current_user.get("school_name")

        try:
            conn = DatabaseManager.get_connection()
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
                self.listbox.insert(tk.END, f"{req[1]} | عنوان: {req[2]} | وضعیت: {req[3]}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت درخواست‌ها: {e}")
        finally:
            conn.close()

    def show_request_detail(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        req = self.requests[selection[0]]
        self.selected_request_id, student_name, title, status, school, self.selected_student_id = req
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
        if not self.file_path or not self.selected_student_id:
            messagebox.showerror("خطا", "لطفاً ابتدا فایل را انتخاب کرده و یک درخواست را از لیست انتخاب کنید.")
            return

        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO program_files (student_id, file_path, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id)
                DO UPDATE SET file_path = EXCLUDED.file_path, status = EXCLUDED.status
            """, (self.selected_student_id, self.file_path, "نوشته شده"))

            cursor.execute("UPDATE program_requests SET status = %s WHERE id = %s", ("نوشته شده", self.selected_request_id))

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

        self.refresh_requests()

    def refresh_requests(self):
        self.listbox.delete(0, tk.END)
        self.requests = []
        school = self.controller.current_user.get("school_name")

        try:
            conn = DatabaseManager.get_connection()
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

        try:
            req_id, _, _, _, _, student_id = self.selected_request
            conn = DatabaseManager.get_connection()
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
        ctk.CTkButton(self, text="بازگشت", command=lambda: controller.show_frame("StartPage"), font=self.persian_font).pack(pady=5)

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
            self.controller.show_frame("AdminPanelPage")
        else:
            messagebox.showerror("خطا", "خطا در افزودن مشاور")


class AdminLoginPage(ctk.CTkFrame):
    """صفحه ورود ادمین اصلی (دسترسی فوق‌مدیر)."""
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

    def refresh_all(self):
        """Refresh both admin and student lists."""
        self.load_admins()
        self.refresh_student_list()
        self.admin_combobox.set("")
        self.student_combobox.set("")

    def load_admins(self):
        users = DatabaseManager.get_all_users()
        if users:
            self.admin_users = {uid: user for uid, user in users.items() if user.get('role') == 'مدیر'}
            names = [user.get('full_name', user.get('username')) for uid, user in self.admin_users.items()]
            self.admin_combobox.configure(values=names)
    
    def refresh_student_list(self):
        users = DatabaseManager.get_all_users()
        if users:
            self.student_users = {uid: user for uid, user in users.items() if user.get('role') == 'دانش آموز'}
            names = [user.get('full_name', user.get('username')) for uid, user in self.student_users.items()]
            self.student_combobox.configure(values=names)
    
    def view_admin_profile(self):
        selected_name = self.admin_combobox.get()
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                profile_info = (f"کد ملی: {user.get('username')}\n"
                                f"نام و نام خانوادگی: {user.get('full_name')}\n"
                                f"نقش: {user.get('role')}\n"
                                f"رمز مرحله دوم: {user.get('twofactorpassword')}\n"
                                f"نام مدرسه: {user.get('school_name')}")
                messagebox.showinfo("پروفایل مدیر", profile_info)
                return
        messagebox.showerror("خطا", "مدیری انتخاب نشده است")
    
    def delete_admin_action(self):
        selected_name = self.admin_combobox.get()
        for user_id, user in self.admin_users.items():
            if user.get('full_name') == selected_name or user.get('username') == selected_name:
                if messagebox.askyesno("تایید", "آیا مطمئن هستید که می‌خواهید این مدیر را حذف کنید؟"):
                    if DatabaseManager.delete_user(user_id):
                        messagebox.showinfo("موفقیت", "مدیر حذف شد")
                        self.refresh_all()
                    else:
                        messagebox.showerror("خطا", "خطا در حذف مدیر")
                return
        messagebox.showerror("خطا", "مدیری انتخاب نشده است")

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
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        twofactor_password = self.twofactor_password_entry.get().strip()
        school_name = self.school_name_entry.get().strip()

        if not all([username, password, full_name, twofactor_password, school_name]):
            messagebox.showerror("خطا", "لطفا تمام فیلدها را پر کنید")
            return

        hashed_password = Security.hash_password(password)
        admin_data = {
            "username": username,
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
                messagebox.showerror("خطا", "ابتدا باید وارد شوید")
                return
            if user.get("role") not in self.PAGE_ROLES[page_name]:
                messagebox.showerror("دسترسی غیرمجاز", "شما اجازه دسترسی به این بخش را ندارید")
                return
        frame = self.frames[page_name]
        frame.tkraise()

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