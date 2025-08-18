import tkinter as tk
from tkinter import messagebox
import os
import socket
import re
import hashlib
import sqlite3
import time

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# مسیر فایل admins.txt در AppData\Roaming
ADMINS_FILE = os.path.join(os.environ["APPDATA"], "admins.txt")
is_admin_logged_in = False

# مسیر دیتابیس در AppData\Roaming
DB_PATH = os.path.join(os.environ["APPDATA"], "contacts.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_admins():
    admins = {}
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    admins[parts[0]] = parts[1]
    return admins

def add_admin(username, password):
    hashed = hash_password(password)
    with open(ADMINS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username},{hashed}\n")

# اگر فایل وجود نداشت، آن را بساز و ادمین‌ها را اضافه کن
if not os.path.exists(ADMINS_FILE):
    add_admin("MY", "456")      # ادمین پیش‌فرض
    add_admin("admin", "123")   # ادمین جدید

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_farsi TEXT,
        name_english TEXT,
        short_code TEXT UNIQUE,
        phone TEXT,
        ip TEXT,
        location_code TEXT,
        voip TEXT,
        manager_phone TEXT,
        username TEXT,
        password TEXT,
        description TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_farsi(char):
    return re.fullmatch(r"[آ-ی\s]*", char) is not None

def validate_english(val):
    return re.fullmatch(r"[a-zA-Z\s]*", val) is not None

def validate_short(val):
    return len(val) <= 3 and (val == "" or val.isalpha())

def validate_phone(val):
    return val.isdigit() or val == ""

def validate_code(val):
    return len(val) <= 8 and (val == "" or val.isalnum()) 

def clear_entries():
    for e in [entry_name_farsi, entry_name_english, entry_short_code, entry_phone, entry_ip, entry_code, entry_voip_phone, entry_manager_phone, entry_username, entry_password]:
        e.delete(0, tk.END)
    text_description.delete("1.0", tk.END)

def on_add():
    name_farsi = entry_name_farsi.get().strip()
    name_english = entry_name_english.get().strip()
    short_code = entry_short_code.get().strip()
    phone = entry_phone.get().strip()
    ip = entry_ip.get().strip()
    code = entry_code.get().strip()
    voip = entry_voip_phone.get().strip()
    manager_phone = entry_manager_phone.get().strip()
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    description = text_description.get("1.0", "end-1c").strip()

    if not name_farsi or not short_code:
        messagebox.showwarning("خطا", "نام فارسی و کد سه‌حرفی اجباری هستند.")
        return

    if not is_valid_ip(ip) and ip != "":
        messagebox.showwarning("خطا", "آدرس IP معتبر نیست.")
        return

    if len(description) > 200:
        messagebox.showwarning("خطا", "توضیحات نمی‌تواند بیش از ۲۰۰ کاراکتر باشد.")
        return

    contact = (name_farsi, name_english, short_code, phone, ip, code, voip, manager_phone, username, password, description)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE short_code = ?", (short_code,))
        if cursor.fetchone():
            messagebox.showwarning("تکراری", "کد سه‌حرفی قبلاً ثبت شده است.")
            conn.close()
            return

        cursor.execute("""
            INSERT INTO contacts (name_farsi, name_english, short_code, phone, ip, location_code, voip, manager_phone, username, password, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, contact)

        conn.commit()
        conn.close()

        messagebox.showinfo("ثبت شد", "مخاطب با موفقیت ثبت شد.")
        clear_entries()
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ذخیره مخاطب:\n{e}")

def show_login_window():
    win = tk.Toplevel(root)
    win.title("ورود ادمین")

    tk.Label(win, text="نام کاربری:").grid(row=0, column=0, padx=10, pady=5)
    user = tk.Entry(win)
    user.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(win, text="رمز عبور:").grid(row=1, column=0, padx=10, pady=5)
    pwd = tk.Entry(win, show="*")
    pwd.grid(row=1, column=1, padx=10, pady=5)

    def check():
        global is_admin_logged_in
        admins = load_admins()
        uname = user.get().strip()
        pword = pwd.get().strip()
        if uname in admins and admins[uname] == hash_password(pword):
            is_admin_logged_in = True
            win.destroy()
            messagebox.showinfo("ورود موفق", f"خوش آمدید {uname}!")
        else:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور اشتباه است.")

    tk.Button(win, text="ورود", command=check).grid(row=2, column=0, columnspan=2, pady=10)

def show_add_window():
    if not is_admin_logged_in:
        messagebox.showwarning("خطا", "ابتدا به عنوان ادمین وارد شوید.")
        return

    win = tk.Toplevel(root)
    win.title("افزودن مخاطب")

    vc_farsi = (root.register(validate_farsi), "%P")
    vc_english = (root.register(validate_english), "%P")
    vc_short = (root.register(validate_short), "%P")
    vc_phone = (root.register(validate_phone), "%P")
    vc_code = (root.register(validate_code), "%P")

    global entry_name_farsi, entry_name_english, entry_short_code, entry_phone, entry_ip, entry_code
    global entry_voip_phone, entry_manager_phone, entry_username, entry_password, text_description

    tk.Label(win, text="نام فارسی:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    entry_name_farsi = tk.Entry(win, validate="key", validatecommand=vc_farsi)
    entry_name_farsi.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="English Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entry_name_english = tk.Entry(win, validate="key", validatecommand=vc_english)
    entry_name_english.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="کد سه‌حرفی کانال:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entry_short_code = tk.Entry(win, validate="key", validatecommand=vc_short)
    entry_short_code.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="IP Address:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    entry_ip = tk.Entry(win)
    entry_ip.grid(row=3, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="شماره تلفن 1:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    entry_phone = tk.Entry(win, validate="key", validatecommand=vc_phone)
    entry_phone.grid(row=4, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="شماره تلفن مسئول:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    entry_manager_phone = tk.Entry(win, validate="key", validatecommand=vc_phone)
    entry_manager_phone.grid(row=5, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="Location indicator:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
    entry_code = tk.Entry(win, validate="key", validatecommand=vc_code)
    entry_code.grid(row=6, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="VOIP:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
    entry_voip_phone = tk.Entry(win, validate="key", validatecommand=vc_phone)
    entry_voip_phone.grid(row=7, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="administrator user:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
    entry_username = tk.Entry(win)
    entry_username.grid(row=8, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="Server Password:").grid(row=9, column=0, sticky="e", padx=5, pady=5)
    entry_password = tk.Entry(win, show="*")
    entry_password.grid(row=9, column=1, sticky="w", padx=5, pady=5)

    tk.Label(win, text="توضیحات (حداکثر ۲۰۰ کاراکتر):").grid(row=10, column=0, sticky="ne", padx=5, pady=5)
    text_description = tk.Text(win, width=40, height=5)
    text_description.grid(row=10, column=1, sticky="w", padx=5, pady=5)

    def limit_description(event):
        content = text_description.get("1.0", "end-1c")
        if len(content) > 200:
            text_description.delete("1.0", "end")
            text_description.insert("1.0", content[:200])
            messagebox.showwarning("هشدار", "توضیحات نمی‌تواند بیش از ۲۰۰ کاراکتر باشد.")
    text_description.bind("<KeyRelease>", limit_description)

    tk.Button(win, text="افزودن مخاطب", command=on_add).grid(row=11, column=0, columnspan=2, pady=10)

# ==== تابع حذف مخاطب ====
def delete_contact(contact_id, win):
    if not is_admin_logged_in:
        messagebox.showwarning("خطا", "فقط ادمین می‌تواند مخاطب را حذف کند.")
        return

    confirm = messagebox.askyesno("تأیید", "آیا مطمئن هستید که این مخاطب حذف شود؟")
    if not confirm:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("حذف شد", "مخاطب با موفقیت حذف شد.")
    win.destroy()
    advanced_search()  # دوباره نتایج را نشان بدهد

# ==== تابع جستجوی پیشرفته ====
def advanced_search():
    name_farsi = entry_search_name.get().strip()
    name_english = entry_search_english.get().strip()
    short_code = entry_search_short.get().strip()
    ip = entry_search_ip.get().strip()
    voip = entry_search_voip.get().strip()
    phone = entry_search_phone.get().strip()

    query = "SELECT * FROM contacts WHERE 1=1"
    params = []

    if name_farsi:
        query += " AND name_farsi LIKE ?"
        params.append(f"%{name_farsi}%")
    if name_english:
        query += " AND name_english LIKE ?"
        params.append(f"%{name_english}%")
    if short_code:
        query += " AND short_code LIKE ?"
        params.append(f"%{short_code}%")
    if ip:
        query += " AND ip LIKE ?"
        params.append(f"%{ip}%")
    if voip:
        query += " AND voip LIKE ?"
        params.append(f"%{voip}%")
    if phone:
        query += " AND phone LIKE ?"
        params.append(f"%{phone}%")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    if not results:
        messagebox.showinfo("نتیجه", "موردی یافت نشد.")
        return

    result_win = tk.Toplevel(root)
    result_win.title("نتایج جستجو")

    container = tk.Frame(result_win, padx=10, pady=10)
    container.pack(fill="both", expand=True)

    headers = ["ID", "نام فارسی", "English Name", "کد سه‌حرفی", "تلفن", "IP", "کد محل", "VOIP", "تلفن مسئول", "نام کاربری", "رمز عبور", "توضیحات", "عملیات"]
    
    for col, header in enumerate(headers):
        tk.Label(container, text=header, borderwidth=1, relief="solid", width=15, bg="#cce6ff").grid(row=0, column=col, sticky="nsew")

    for row_num, row in enumerate(results, start=1):
        for col_num, value in enumerate(row):
            if headers[col_num] == "توضیحات":
                txt = tk.Text(container, width=40, height=4, wrap="word")
                txt.insert("1.0", value)
                txt.config(state="disabled", bg="#f0f0f0")
                txt.grid(row=row_num, column=col_num, sticky="nsew", padx=2, pady=2)
            else:
                tk.Label(container, text=value, borderwidth=1, relief="solid", width=15).grid(row=row_num, column=col_num, sticky="nsew", padx=2, pady=2)

        # دکمه حذف
        tk.Button(container, text="حذف", fg="red",
                  command=lambda rid=row[0], w=result_win: delete_contact(rid, w)
        ).grid(row=row_num, column=len(headers)-1, padx=2, pady=2)

    for col in range(len(headers)):
        container.grid_columnconfigure(col, weight=1)

# ==== GUI اصلی ====
root = tk.Tk()
root.title("سامانه اطلاعات ايستگاههاي مخابرات هوانوردي")
root.state('zoomed')

# فریم بالا برای لوگو و ساعت
top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=5)

# لوگو
if PIL_AVAILABLE and os.path.exists("logo.png"):
    img = Image.open("logo.png")
    img = img.resize((80, 80), Image.ANTIALIAS)
    logo_img = ImageTk.PhotoImage(img)
    logo_label = tk.Label(top_frame, image=logo_img)
    logo_label.pack(side="left")

# ساعت و تاریخ
time_label = tk.Label(top_frame, font=("Tahoma", 12))
time_label.pack(side="right")

def update_time():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

update_time()

# دکمه‌ها
btn_login = tk.Button(root, text="Admin Login", command=show_login_window)
btn_login.pack(padx=10, pady=10)

btn_add = tk.Button(root, text="Add a new AFTN station", command=show_add_window)
btn_add.pack(padx=10, pady=10)

# جستجوی پیشرفته
search_frame = tk.LabelFrame(root, text="Advanced search")
search_frame.pack(fill="x", padx=10, pady=10)

tk.Label(search_frame, text="Persian Name:").grid(row=0, column=0, padx=5, pady=5)
entry_search_name = tk.Entry(search_frame)
entry_search_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(search_frame, text="English Name:").grid(row=0, column=2, padx=5, pady=5)
entry_search_english = tk.Entry(search_frame)
entry_search_english.grid(row=0, column=3, padx=5, pady=5)

tk.Label(search_frame, text="Three letter channel name:").grid(row=1, column=0, padx=5, pady=5)
entry_search_short = tk.Entry(search_frame)
entry_search_short.grid(row=1, column=1, padx=5, pady=5)

tk.Label(search_frame, text="IP address:").grid(row=1, column=2, padx=5, pady=5)
entry_search_ip = tk.Entry(search_frame)
entry_search_ip.grid(row=1, column=3, padx=5, pady=5)

tk.Label(search_frame, text="VOIP:").grid(row=2, column=0, padx=5, pady=5)
entry_search_voip = tk.Entry(search_frame)
entry_search_voip.grid(row=2, column=1, padx=5, pady=5)

tk.Label(search_frame, text="Phone number:").grid(row=2, column=2, padx=5, pady=5)
entry_search_phone = tk.Entry(search_frame)
entry_search_phone.grid(row=2, column=3, padx=5, pady=5)

tk.Button(search_frame, text="Search", command=advanced_search).grid(row=3, column=0, columnspan=4, pady=10)

root.mainloop()
