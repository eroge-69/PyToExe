import os
import sqlite3
import base64
import hashlib
import shutil
import csv
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# ----------------- Constants -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # مسار البرنامج الحالي
APP_DIR = os.path.join(BASE_DIR, ".pw_manager")        # مجلد البرنامج المخفي
CACHE_DIR = os.path.join(APP_DIR, "cache")             # مجلد cache مخفي داخل APP_DIR
DB_FILE = os.path.join(APP_DIR, "passwords.db")
ITERATIONS = 200_000
backend = default_backend()
FONT_MAIN = ("Arial", 11)

# ----------------- Ensure hidden app directory -----------------
for directory in [APP_DIR, CACHE_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# ----------------- Database Initialization -----------------
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                master_salt BLOB,
                master_hash BLOB,
                iterations INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                site TEXT,
                login TEXT,
                password BLOB,
                note BLOB,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

# ----------------- Key Derivation -----------------
def derive_key(master_password, salt, iterations=ITERATIONS):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

# ----------------- User Management -----------------
def create_user(username, master_password):
    salt = os.urandom(16)
    master_hash = hashlib.sha256(master_password.encode() + salt).digest()
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            'INSERT INTO users (username, master_salt, master_hash, iterations) VALUES (?, ?, ?, ?)',
            (username, salt, master_hash, ITERATIONS)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, master_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, master_salt, master_hash, iterations FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        uid, salt, master_hash, iterations = row
        if hashlib.sha256(master_password.encode() + salt).digest() == master_hash:
            return uid, salt, iterations
    return None, None, None

def change_master_password(user_id, old_password, new_password):
    uid, salt, iterations = verify_user_by_id(user_id, old_password)
    if uid:
        new_salt = os.urandom(16)
        new_hash = hashlib.sha256(new_password.encode() + new_salt).digest()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('UPDATE users SET master_salt=?, master_hash=? WHERE id=?', (new_salt, new_hash, user_id))
        conn.commit()
        conn.close()
        return True
    return False

def verify_user_by_id(user_id, master_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, master_salt, master_hash, iterations FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        uid, salt, master_hash, iterations = row
        if hashlib.sha256(master_password.encode() + salt).digest() == master_hash:
            return uid, salt, iterations
    return None, None, None

# ----------------- Entry Management -----------------
def encrypt_entry(key, password, note):
    f = Fernet(key)
    return f.encrypt(password.encode()), f.encrypt(note.encode())

def decrypt_entry(key, enc_pwd, enc_note):
    f = Fernet(key)
    return f.decrypt(enc_pwd).decode(), f.decrypt(enc_note).decode()

def add_entry(user_id, key, site, login, password, note):
    enc_pwd, enc_note = encrypt_entry(key, password, note)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id FROM entries WHERE user_id=? AND site=? AND login=?', (user_id, site, login))
    if c.fetchone():
        conn.close()
        return False
    c.execute(
        'INSERT INTO entries (user_id, site, login, password, note) VALUES (?, ?, ?, ?, ?)',
        (user_id, site, login, enc_pwd, enc_note)
    )
    conn.commit()
    conn.close()
    return True

def list_entries(user_id, search_term=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if search_term:
        term = f"%{search_term}%"
        c.execute('SELECT id, site, login FROM entries WHERE user_id=? AND (site LIKE ? OR login LIKE ?)', (user_id, term, term))
    else:
        c.execute('SELECT id, site, login FROM entries WHERE user_id=?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_entry(user_id, key, entry_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT site, login, password, note FROM entries WHERE id=? AND user_id=?', (entry_id, user_id))
    row = c.fetchone()
    conn.close()
    if row:
        site, login, enc_pwd, enc_note = row
        pwd, note = decrypt_entry(key, enc_pwd, enc_note)
        return site, login, pwd, note
    return None

def delete_entry(entry_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM entries WHERE id=?', (entry_id,))
    conn.commit()
    conn.close()

def update_entry(user_id, key, entry_id, site, login, password, note):
    enc_pwd, enc_note = encrypt_entry(key, password, note)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        'UPDATE entries SET site=?, login=?, password=?, note=? WHERE id=? AND user_id=?',
        (site, login, enc_pwd, enc_note, entry_id, user_id)
    )
    conn.commit()
    conn.close()

# ----------------- CSV Export/Import -----------------
def export_entries_csv(user_id, key, filepath):
    entries = list_entries(user_id)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Site', 'Login', 'Password', 'Note'])
        for eid, site, login in entries:
            _, _, pwd, note = get_entry(user_id, key, eid)
            writer.writerow([site, login, pwd, note])

def import_entries_csv(user_id, key, filepath):
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                add_entry(user_id, key, row['Site'], row['Login'], row['Password'], row['Note'])
        return True
    except Exception as e:
        print(e)
        return False

# ----------------- GUI -----------------
class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("500x250")
        self.root.configure(bg="#f0f0f0")
        self.user_id = None
        self.key = None
        self.show_passwords = False
        self.login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- Login Screen ---
    def login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=60)

        tk.Label(frame, text="Username:", font=FONT_MAIN, bg="#f0f0f0").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        username_entry = tk.Entry(frame, font=FONT_MAIN)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Master Password:", font=FONT_MAIN, bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_entry = tk.Entry(frame, show='*', font=FONT_MAIN)
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        def login_action():
            username = username_entry.get()
            master_password = password_entry.get()
            uid, salt, iterations = verify_user(username, master_password)
            if uid:
                self.user_id = uid
                self.key = derive_key(master_password, salt, iterations)
                self.main_screen()
            else:
                messagebox.showerror("Error", "اسم المستخدم أو Master Password غير صحيح")

        def create_action():
            username = username_entry.get()
            master_password = password_entry.get()
            if create_user(username, master_password):
                messagebox.showinfo("Info", "تم إنشاء الحساب بنجاح")
            else:
                messagebox.showerror("Error", "اسم المستخدم موجود بالفعل")

        tk.Button(frame, text="Login", width=12, command=login_action, bg="#4CAF50", fg="white").grid(row=2, column=0, pady=10)
        tk.Button(frame, text="Create User", width=12, command=create_action, bg="#2196F3", fg="white").grid(row=2, column=1, pady=10)

    # --- Main Screen ---
    def main_screen(self):
        self.clear_screen()
        top_frame = tk.Frame(self.root, bg="#f0f0f0")
        top_frame.pack(fill="x", pady=5)

        tk.Label(top_frame, text=f"User ID: {self.user_id}", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side="left", padx=10)
        tk.Button(top_frame, text="Backup DB", width=12, command=self.backup_db, bg="#FF9800", fg="white").pack(side="right", padx=5)
        tk.Button(top_frame, text="Restore DB", width=12, command=self.restore_db, bg="#FF5722", fg="white").pack(side="right", padx=5)
        tk.Button(top_frame, text="Export CSV", width=12, command=self.export_csv, bg="#607D8B", fg="white").pack(side="right", padx=5)
        tk.Button(top_frame, text="Import CSV", width=12, command=self.import_csv, bg="#795548", fg="white").pack(side="right", padx=5)
        tk.Button(top_frame, text="Add Entry", width=12, command=lambda: self.add_entry_window(refresh_callback), bg="#4CAF50", fg="white").pack(side="right", padx=5)
        tk.Button(top_frame, text="Settings", width=12, command=self.settings_window, bg="#9C27B0", fg="white").pack(side="right", padx=5)

        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Search:", bg="#f0f0f0").pack(side="left")
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ('ID', 'Site', 'Login', 'Password', 'Note')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="center")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#e8e8e8')

        # Refresh function
        def refresh_callback():
            tree.delete(*tree.get_children())
            search_term = search_entry.get().strip()
            for idx, (eid, site, login) in enumerate(list_entries(self.user_id, search_term)):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                pwd_display = "******" if not self.show_passwords else get_entry(self.user_id, self.key, eid)[2]
                tree.insert('', tk.END, values=(eid, site, login, pwd_display, ""), tags=(tag,))

        # Double-click to edit
        def show_entry_window(entry_id):
            result = get_entry(self.user_id, self.key, entry_id)
            if not result:
                return
            site, login, pwd, note = result
            win = tk.Toplevel(self.root)
            win.title("Entry Details")
            win.geometry("360x220")
            win.configure(bg="#f9f9f9")

            tk.Label(win, text="Site:", bg="#f9f9f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            site_entry = tk.Entry(win)
            site_entry.insert(0, site)
            site_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(win, text="Login:", bg="#f9f9f9").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            login_entry = tk.Entry(win)
            login_entry.insert(0, login)
            login_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(win, text="Password:", bg="#f9f9f9").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            pwd_entry = tk.Entry(win)
            pwd_entry.insert(0, pwd)
            pwd_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(win, text="Note:", bg="#f9f9f9").grid(row=3, column=0, padx=5, pady=5, sticky="e")
            note_entry = tk.Entry(win)
            note_entry.insert(0, note)
            note_entry.grid(row=3, column=1, padx=5, pady=5)

            tk.Button(win, text="Save", bg="#4CAF50", fg="white",
                      command=lambda: [update_entry(self.user_id, self.key, entry_id,
                                                    site_entry.get(), login_entry.get(),
                                                    pwd_entry.get(), note_entry.get()),
                                       refresh_callback(), win.destroy()]).grid(row=4, column=0, pady=10)
            tk.Button(win, text="Delete", bg="#F44336", fg="white",
                      command=lambda: [delete_entry(entry_id), refresh_callback(), win.destroy()]).grid(row=4, column=1, pady=10)
            tk.Button(win, text="Cancel", bg="#9E9E9E", fg="white", command=win.destroy).grid(row=5, column=0, columnspan=2, pady=5)

        def on_double_click(event):
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                eid = item['values'][0]
                show_entry_window(eid)

        tree.bind("<Double-1>", on_double_click)
        search_entry.bind("<KeyRelease>", lambda e: refresh_callback())
        refresh_callback()

        tk.Button(top_frame, text="Show/Hide Passwords", bg="#607D8B", fg="white",
                  command=lambda: [self.toggle_passwords(refresh_callback)]).pack(side="right", padx=5)

    def toggle_passwords(self, refresh_callback):
        self.show_passwords = not self.show_passwords
        refresh_callback()

    # --- Add Entry Window ---
    def add_entry_window(self, refresh_callback):
        win = tk.Toplevel(self.root)
        win.title("Add Entry")
        win.geometry("320x200")
        win.configure(bg="#f9f9f9")

        tk.Label(win, text="Site:", bg="#f9f9f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        site_entry = tk.Entry(win)
        site_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Login:", bg="#f9f9f9").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        login_entry = tk.Entry(win)
        login_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(win, text="Password:", bg="#f9f9f9").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        pwd_entry = tk.Entry(win)
        pwd_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(win, text="Note:", bg="#f9f9f9").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        note_entry = tk.Entry(win)
        note_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(win, text="Save", bg="#4CAF50", fg="white",
                  command=lambda: [self.save_new_entry(site_entry.get(), login_entry.get(),
                                                       pwd_entry.get(), note_entry.get(), refresh_callback), win.destroy()]).grid(row=4, column=0, columnspan=2, pady=10)

    def save_new_entry(self, site, login, password, note, refresh_callback):
        if add_entry(self.user_id, self.key, site, login, password, note):
            messagebox.showinfo("Info", "تم حفظ البيانات")
            refresh_callback()
        else:
            messagebox.showerror("Error", "السجل موجود بالفعل")

    # --- Backup / Restore ---
    def backup_db(self):
        dest = filedialog.asksaveasfilename(defaultextension=".bak", filetypes=[("Backup Files","*.bak")])
        if dest:
            try:
                shutil.copyfile(DB_FILE, dest)
                messagebox.showinfo("Backup", "تم النسخ الاحتياطي بنجاح")
            except Exception as e:
                messagebox.showerror("Error", f"فشل النسخ الاحتياطي: {e}")

    def restore_db(self):
        src = filedialog.askopenfilename(filetypes=[("Backup Files","*.bak")])
        if src:
            try:
                shutil.copyfile(src, DB_FILE)
                messagebox.showinfo("Restore", "تم استرجاع النسخة الاحتياطية بنجاح")
            except Exception as e:
                messagebox.showerror("Error", f"فشل الاسترجاع: {e}")

    # --- CSV Export / Import ---
    def export_csv(self):
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
        if dest:
            export_entries_csv(self.user_id, self.key, dest)
            messagebox.showinfo("Export CSV", "تم تصدير السجلات بنجاح")

    def import_csv(self):
        src = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if src:
            if import_entries_csv(self.user_id, self.key, src):
                messagebox.showinfo("Import CSV", "تم استيراد السجلات بنجاح")
            else:
                messagebox.showerror("Import CSV", "فشل الاستيراد")

    # --- Settings Window ---
    def settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("360x180")
        win.configure(bg="#f9f9f9")

        tk.Label(win, text="Change Master Password", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=5)
        tk.Label(win, text="Old Password:", bg="#f9f9f9").pack(pady=5)
        old_entry = tk.Entry(win, show='*')
        old_entry.pack(pady=2)
        tk.Label(win, text="New Password:", bg="#f9f9f9").pack(pady=5)
        new_entry = tk.Entry(win, show='*')
        new_entry.pack(pady=2)

        tk.Button(win, text="Change Password", bg="#9C27B0", fg="white",
                  command=lambda: self.change_master_password_action(old_entry.get(), new_entry.get(), win)).pack(pady=10)

    def change_master_password_action(self, old_pass, new_pass, win):
        if change_master_password(self.user_id, old_pass, new_pass):
            messagebox.showinfo("Success", "تم تغيير Master Password")
            win.destroy()
        else:
            messagebox.showerror("Error", "كلمة المرور القديمة غير صحيحة")

# ----------------- Run GUI -----------------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()
