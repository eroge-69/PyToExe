import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import os
import csv
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import random
import string
import smtplib
from email.message import EmailMessage
import threading

# Constants
DB_FILE = "passwords.db"
SALT = b"my_salt_1234"  # Change for your app!
ITERATIONS = 100_000

# --- Database Setup & Access ---

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS master (
        id INTEGER PRIMARY KEY,
        password_hash TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        category TEXT DEFAULT '',
        notes TEXT DEFAULT ''
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS email_settings (
        id INTEGER PRIMARY KEY,
        sender_email TEXT,
        sender_password TEXT,
        recipient_email TEXT,
        smtp_server TEXT,
        smtp_port INTEGER
    )
    """)
    conn.commit()
    return conn

def get_master_hash(conn):
    c = conn.cursor()
    c.execute("SELECT password_hash FROM master WHERE id=1")
    row = c.fetchone()
    return row[0] if row else None

def set_master_hash(conn, hash_str):
    c = conn.cursor()
    if get_master_hash(conn):
        c.execute("UPDATE master SET password_hash = ? WHERE id=1", (hash_str,))
    else:
        c.execute("INSERT INTO master(id, password_hash) VALUES (1, ?)", (hash_str,))
    conn.commit()

def save_email_settings(conn, sender_email, sender_password, recipient_email, smtp_server, smtp_port):
    c = conn.cursor()
    c.execute("SELECT id FROM email_settings WHERE id=1")
    if c.fetchone():
        c.execute("""UPDATE email_settings SET sender_email=?, sender_password=?, recipient_email=?, smtp_server=?, smtp_port=? WHERE id=1""",
                  (sender_email, sender_password, recipient_email, smtp_server, smtp_port))
    else:
        c.execute("""INSERT INTO email_settings(id, sender_email, sender_password, recipient_email, smtp_server, smtp_port)
                     VALUES(1,?,?,?,?,?)""",
                  (sender_email, sender_password, recipient_email, smtp_server, smtp_port))
    conn.commit()

def get_email_settings(conn):
    c = conn.cursor()
    c.execute("SELECT sender_email, sender_password, recipient_email, smtp_server, smtp_port FROM email_settings WHERE id=1")
    return c.fetchone()

# --- Security & Encryption ---

def hash_master_password(password: str) -> str:
    # Use sha256 with salt, stored as hex
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), SALT, ITERATIONS)
    return base64.urlsafe_b64encode(dk).decode()

def derive_key(password: str) -> bytes:
    # Derive a Fernet key from master password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_password(password_plain: str, key: bytes) -> str:
    f = Fernet(key)
    token = f.encrypt(password_plain.encode())
    return token.decode()

def decrypt_password(password_encrypted: str, key: bytes) -> str:
    f = Fernet(key)
    try:
        decrypted = f.decrypt(password_encrypted.encode())
        return decrypted.decode()
    except InvalidToken:
        return "<Decryption Error>"

# --- Password Strength Meter ---

def password_strength(password: str) -> str:
    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)

    score = sum([has_lower, has_upper, has_digit, has_special])

    if length >= 12 and score == 4:
        return "Strong"
    elif length >= 8 and score >= 3:
        return "Medium"
    else:
        return "Weak"

# --- Password Generator ---

def generate_password(length=16):
    if length < 8:
        length = 8
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

# --- Email Sending (async) ---

def send_email_alert(settings, subject, body):
    def _send():
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = settings[0]
            msg['To'] = settings[2]
            msg.set_content(body)

            server = smtplib.SMTP_SSL(settings[3], settings[4])
            server.login(settings[0], settings[1])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Email send failed: {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

# --- GUI ---

class LoginWindow(tk.Toplevel):
    def __init__(self, master, conn, on_success):
        super().__init__(master)
        self.conn = conn
        self.on_success = on_success
        self.title("Login - Password Manager")
        self.geometry("350x150")
        self.resizable(False, False)

        self.label = ttk.Label(self, text="Enter Master Password:")
        self.label.pack(pady=10)

        self.password_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        self.entry.pack(pady=5, fill='x', padx=20)
        self.entry.focus()

        self.btn = ttk.Button(self, text="Login", command=self.check_password)
        self.btn.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.master_hash = get_master_hash(conn)
        if self.master_hash is None:
            self.label.config(text="Set a new Master Password:")

    def check_password(self):
        pw = self.password_var.get()
        if not pw:
            messagebox.showwarning("Input Required", "Please enter a master password.")
            return
        if self.master_hash is None:
            # Set master password
            hashed = hash_master_password(pw)
            set_master_hash(self.conn, hashed)
            self.on_success(pw)
            self.destroy()
        else:
            # Verify
            hashed = hash_master_password(pw)
            if hashed == self.master_hash:
                self.on_success(pw)
                self.destroy()
            else:
                messagebox.showerror("Error", "Incorrect master password.")
                self.password_var.set("")
                self.entry.focus()

    def on_close(self):
        self.master.destroy()  # Close whole app if login window closed

class PasswordManagerApp(tk.Tk):
    def __init__(self, master_password):
        super().__init__()
        self.title("Password Manager")
        self.geometry("800x500")
        self.resizable(True, True)

        self.conn = init_db()
        self.master_password = master_password
        self.key = derive_key(master_password)
        self.email_settings = get_email_settings(self.conn) or ("", "", "", "", 465)
        self.is_dark = False

        self.create_widgets()
        self.load_passwords()

    def create_widgets(self):
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_passwords())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Treeview for password entries
        columns = ("site", "username", "password", "category", "notes")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150, anchor='w')
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)

        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add", command=self.add_password).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_password).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_password).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Generate Password", command=self.generate_password_ui).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Import CSV", command=self.import_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Email Settings", command=self.email_settings_window).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Toggle Dark Mode", command=self.toggle_theme).pack(side='right')

        # Password strength label (for generated or input)
        self.strength_label = ttk.Label(self, text="")
        self.strength_label.pack(pady=2)

        self.style = ttk.Style(self)
        self.light_theme()

    def load_passwords(self):
        search = self.search_var.get().lower()
        c = self.conn.cursor()
        if search:
            c.execute("SELECT id, site, username, password, category, notes FROM passwords WHERE LOWER(site) LIKE ? OR LOWER(username) LIKE ?", 
                      (f'%{search}%', f'%{search}%'))
        else:
            c.execute("SELECT id, site, username, password, category, notes FROM passwords")
        rows = c.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            decrypted_pwd = decrypt_password(row[3], self.key)
            self.tree.insert('', 'end', iid=row[0], values=(row[1], row[2], decrypted_pwd, row[4], row[5]))

    def add_password(self):
        PasswordEntryDialog(self, self.conn, self.key, None, self.email_settings, self.on_password_changed)

    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a password entry to edit.")
            return
        pid = selected[0]
        PasswordEntryDialog(self, self.conn, self.key, pid, self.email_settings, self.on_password_changed)

    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a password entry to delete.")
            return
        pid = selected[0]
        confirm = messagebox.askyesno("Confirm Delete", "Delete selected password entry?")
        if confirm:
            c = self.conn.cursor()
            c.execute("DELETE FROM passwords WHERE id=?", (pid,))
            self.conn.commit()
            self.load_passwords()
            if self.email_settings and all(self.email_settings):
                subject = "Password Entry Deleted"
                body = f"Entry ID {pid} was deleted from your password manager."
                send_email_alert(self.email_settings, subject, body)

    def generate_password_ui(self):
        length = simpledialog.askinteger("Generate Password", "Enter password length (min 8):", minvalue=8, maxvalue=128)
        if length:
            pwd = generate_password(length)
            self.strength_label.config(text=f"Generated Password Strength: {password_strength(pwd)}")
            # Show generated password and offer to copy or use it
            CopyPasswordDialog(self, pwd)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        c = self.conn.cursor()
        c.execute("SELECT site, username, password, category, notes FROM passwords")
        rows = c.fetchall()
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Site", "Username", "Password", "Category", "Notes"])
                for r in rows:
                    decrypted_pwd = decrypt_password(r[2], self.key)
                    writer.writerow([r[0], r[1], decrypted_pwd, r[3], r[4]])
            messagebox.showinfo("Exported", f"Passwords exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{e}")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    site = row.get("Site", "").strip()
                    username = row.get("Username", "").strip()
                    password = row.get("Password", "").strip()
                    category = row.get("Category", "").strip()
                    notes = row.get("Notes", "").strip()
                    if site and username and password:
                        encrypted_pwd = encrypt_password(password, self.key)
                        c = self.conn.cursor()
                        c.execute("INSERT INTO passwords (site, username, password, category, notes) VALUES (?, ?, ?, ?, ?)",
                                  (site, username, encrypted_pwd, category, notes))
                        count += 1
                self.conn.commit()
                messagebox.showinfo("Imported", f"Imported {count} passwords.")
                self.load_passwords()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV:\n{e}")

    def email_settings_window(self):
        EmailSettingsDialog(self, self.conn, self.email_settings, self.on_email_settings_changed)

    def on_email_settings_changed(self, new_settings):
        self.email_settings = new_settings

    def on_password_changed(self):
        self.load_passwords()
        # Optionally send email alert if configured
        if self.email_settings and all(self.email_settings):
            subject = "Password Entry Changed"
            body = "A password entry was added/edited in your password manager."
            send_email_alert(self.email_settings, subject, body)

    def toggle_theme(self):
        if self.is_dark:
            self.light_theme()
        else:
            self.dark_theme()
        self.is_dark = not self.is_dark

    def light_theme(self):
        self.style.theme_use('default')
        self.style.configure('.', background='white', foreground='black')
        self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')

    def dark_theme(self):
        self.style.theme_use('clam')
        self.style.configure('.', background='#2e2e2e', foreground='white')
        self.style.configure('Treeview', background='#3c3f41', foreground='white', fieldbackground='#3c3f41')

class PasswordEntryDialog(tk.Toplevel):
    def __init__(self, master, conn, key, entry_id, email_settings, callback):
        super().__init__(master)
        self.conn = conn
        self.key = key
        self.entry_id = entry_id
        self.email_settings = email_settings
        self.callback = callback
        self.title("Add Password" if entry_id is None else "Edit Password")
        self.geometry("400x400")
        self.resizable(False, False)

        # Variables
        self.site_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        # Layout
        ttk.Label(self, text="Site/URL:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.site_var).pack(fill='x', padx=10)

        ttk.Label(self, text="Username:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.username_var).pack(fill='x', padx=10)

        ttk.Label(self, text="Password:").pack(anchor='w', padx=10, pady=5)
        pw_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        pw_entry.pack(fill='x', padx=10)

        # Password strength label
        self.strength_label = ttk.Label(self, text="")
        self.strength_label.pack(anchor='w', padx=10, pady=2)

        # Show/hide password checkbox
        self.show_pw_var = tk.BooleanVar(value=False)
        def toggle_pw():
            pw_entry.config(show='' if self.show_pw_var.get() else '*')
        ttk.Checkbutton(self, text="Show Password", variable=self.show_pw_var, command=toggle_pw).pack(anchor='w', padx=10)

        # Update strength on password change
        def on_pw_change(*args):
            self.strength_label.config(text="Strength: " + password_strength(self.password_var.get()))
        self.password_var.trace_add("write", on_pw_change)

        ttk.Label(self, text="Category:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.category_var).pack(fill='x', padx=10)

        ttk.Label(self, text="Notes:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.notes_var).pack(fill='x', padx=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=15)

        ttk.Button(btn_frame, text="Generate Password", command=self.generate_password).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Save", command=self.save_entry).pack(side='right', padx=10)

        # Load data if editing
        if entry_id:
            self.load_entry()

    def load_entry(self):
        c = self.conn.cursor()
        c.execute("SELECT site, username, password, category, notes FROM passwords WHERE id=?", (self.entry_id,))
        row = c.fetchone()
        if row:
            self.site_var.set(row[0])
            self.username_var.set(row[1])
            decrypted = decrypt_password(row[2], self.key)
            self.password_var.set(decrypted)
            self.category_var.set(row[3])
            self.notes_var.set(row[4])

    def generate_password(self):
        pwd = generate_password(16)
        self.password_var.set(pwd)

    def save_entry(self):
        site = self.site_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        category = self.category_var.get().strip()
        notes = self.notes_var.get().strip()

        if not site or not username or not password:
            messagebox.showwarning("Missing Data", "Site, username and password are required.")
            return

        encrypted_pwd = encrypt_password(password, self.key)
        c = self.conn.cursor()
        if self.entry_id is None:
            c.execute("INSERT INTO passwords (site, username, password, category, notes) VALUES (?, ?, ?, ?, ?)",
                      (site, username, encrypted_pwd, category, notes))
        else:
            c.execute("UPDATE passwords SET site=?, username=?, password=?, category=?, notes=? WHERE id=?",
                      (site, username, encrypted_pwd, category, notes, self.entry_id))
        self.conn.commit()
        self.callback()
        self.destroy()

class CopyPasswordDialog(tk.Toplevel):
    def __init__(self, master, password):
        super().__init__(master)
        self.title("Generated Password")
        self.geometry("400x150")
        self.resizable(False, False)

        ttk.Label(self, text="Generated Password:").pack(pady=5)
        self.pwd_var = tk.StringVar(value=password)
        entry = ttk.Entry(self, textvariable=self.pwd_var, font=("TkDefaultFont", 14))
        entry.pack(fill='x', padx=10)
        entry.select_range(0, 'end')
        entry.focus()

        ttk.Button(self, text="Copy to Clipboard", command=self.copy_clipboard).pack(pady=10)

    def copy_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.pwd_var.get())
        messagebox.showinfo("Copied", "Password copied to clipboard.")

class EmailSettingsDialog(tk.Toplevel):
    def __init__(self, master, conn, settings, callback):
        super().__init__(master)
        self.conn = conn
        self.callback = callback
        self.title("Email Settings")
        self.geometry("400x350")
        self.resizable(False, False)

        sender_email, sender_password, recipient_email, smtp_server, smtp_port = settings

        self.sender_var = tk.StringVar(value=sender_email)
        self.sender_pass_var = tk.StringVar(value=sender_password)
        self.recipient_var = tk.StringVar(value=recipient_email)
        self.smtp_server_var = tk.StringVar(value=smtp_server or "smtp.gmail.com")
        self.smtp_port_var = tk.IntVar(value=smtp_port or 465)

        ttk.Label(self, text="Sender Email:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.sender_var).pack(fill='x', padx=10)

        ttk.Label(self, text="Sender Email Password:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.sender_pass_var, show="*").pack(fill='x', padx=10)

        ttk.Label(self, text="Recipient Email:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.recipient_var).pack(fill='x', padx=10)

        ttk.Label(self, text="SMTP Server:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.smtp_server_var).pack(fill='x', padx=10)

        ttk.Label(self, text="SMTP Port:").pack(anchor='w', padx=10, pady=5)
        ttk.Entry(self, textvariable=self.smtp_port_var).pack(fill='x', padx=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=15)

        ttk.Button(btn_frame, text="Save", command=self.save_settings).pack(side='right', padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='right')

    def save_settings(self):
        sender_email = self.sender_var.get().strip()
        sender_password = self.sender_pass_var.get().strip()
        recipient_email = self.recipient_var.get().strip()
        smtp_server = self.smtp_server_var.get().strip()
        smtp_port = self.smtp_port_var.get()

        if not (sender_email and sender_password and recipient_email and smtp_server and smtp_port):
            messagebox.showwarning("Missing Data", "All fields are required.")
            return

        save_email_settings(self.conn, sender_email, sender_password, recipient_email, smtp_server, smtp_port)
        self.callback((sender_email, sender_password, recipient_email, smtp_server, smtp_port))
        self.destroy()

def main():
    conn = init_db()
    root = tk.Tk()
    root.withdraw()  # Hide main window until login
    def on_login_success(master_pw):
        root.deiconify()
        app = PasswordManagerApp(master_pw)
        app.mainloop()

    login = LoginWindow(root, conn, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()
