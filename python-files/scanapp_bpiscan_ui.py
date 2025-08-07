import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from tkinter import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageTk
import pyinsane2
import threading
import os
import sys
import sqlite3
import smtplib
from email.message import EmailMessage
import re
from datetime import datetime, timedelta
import random
import numpy as np
import cv2
from ctypes import cdll
from pyzbar.pyzbar import decode


# DB_NAME = "users.db"
DB_NAME = "users_secure.db"
LOCKOUT_THRESHOLD = 3
PASSWORD_EXPIRY_DAYS = 120
GMAIL_USER = "dmzxc117@gmail.com"
GMAIL_PASSWORD = "cygavrqpnltpeqhw"  # Replace with Gmail App Password

# Explicitly load the barcode DLL
dll_path = os.path.join(os.path.dirname(__file__), "libzbar-64.dll")
cdll.LoadLibrary(dll_path)

""" def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close() """

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        password1 TEXT,
        password2 TEXT,
        email TEXT,
        last_changed TEXT,
        attempts INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

""" def save_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False """

def send_otp_email(to_email, otp_code):
    msg = EmailMessage()
    msg['Subject'] = 'Your BPIScan OTP Code'
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg.set_content(f"Your OTP code is: {otp_code}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASSWORD)
        smtp.send_message(msg)

def save_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO users (username, password, password1, password2, last_changed) VALUES (?, ?, '', '', ?)",
              (username, password, now))
    conn.commit()
    conn.close()

""" def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None """

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password, attempts, locked, last_changed FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "not_found"
    current_pwd, attempts, locked, last_changed = row
    if locked:
        return "locked"
    if password == current_pwd:
        reset_attempts(username)
        return "valid"
    else:
        increment_attempts(username, attempts)
        return "invalid"
    
def increment_attempts(username, attempts):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if attempts + 1 >= LOCKOUT_THRESHOLD:
        c.execute("UPDATE users SET attempts=?, locked=1 WHERE username=?", (attempts + 1, username))
    else:
        c.execute("UPDATE users SET attempts=? WHERE username=?", (attempts + 1, username))
    conn.commit()
    conn.close()

def reset_attempts(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET attempts=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def is_password_expired(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT last_changed FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        last_changed = datetime.fromisoformat(row[0])
        return datetime.now() - last_changed > timedelta(days=120)
    return False

def update_password(username, new_pwd):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("SELECT password, password1 FROM users WHERE username=?", (username,))
    current, p1 = c.fetchone()
    c.execute("UPDATE users SET password=?, password1=?, password2=?, last_changed=? WHERE username=?",
              (new_pwd, current, p1, now, username))
    conn.commit()
    conn.close()

def password_valid(pwd):
    return (
        len(pwd) >= 8 and
        re.search(r"[A-Z]", pwd) and
        re.search(r"[a-z]", pwd) and
        re.search(r"[0-9]", pwd) and
        re.search(r"[^a-zA-Z0-9]", pwd)
    )

def otp_prompt():
    otp = str(random.randint(100000, 999999))
    messagebox.showinfo("OTP Verification", f"Your OTP code: {otp}")
    entered = simpledialog.askstring("OTP", "Enter the OTP sent:")
    return entered == otp

class BPIScanStyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BPIScan Scanner App")
        self.root.geometry("950x680")
        self.root.configure(bg="#f0f2f5")
        self.logged_in_user = None

        pyinsane2.init()
        self.device = None
        self.image_list = []
        self.thumb_images = []
        self.current_index = 0
        self.tk_img = None

        init_db()
        self.login_ui()

    def login_ui(self):
        self.login_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=320)

        self.logo_img = Image.open("logo.png")  # Or a full path if needed
        self.logo_img = self.logo_img.resize((200, 80), Image.ANTIALIAS)  # Resize if needed
        self.tk_logo = ImageTk.PhotoImage(self.logo_img)

        tk.Label(self.login_frame, image=self.tk_logo, bg="#ffffff").pack(pady=(5, 0))


        tk.Label(self.login_frame, text="BPIScan Login", font=("Segoe UI", 14), bg="#ffffff").pack(pady=10)
        tk.Label(self.login_frame, text="Username", bg="#ffffff").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password", bg="#ffffff").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        btn_frame = tk.Frame(self.login_frame, bg="#ffffff")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Login", command=self.authenticate_user,
                  bg="#007acc", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Register", command=self.register_user,
                  bg="#4caf50", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Forgot Password", command=self.forgot_password, fg="blue").pack(pady=5)

    def authenticate_user(self):
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        result = verify_user(user, pw)

        if result == "valid":
            if is_password_expired(user):
                messagebox.showinfo("Password Expired", "You must change your password.")
                self.change_password(user)
            else:
                messagebox.showinfo("Login", f"Welcome, {user}")
                self.logged_in_user = user
                self.login_frame.destroy()
                self.setup_ui()
        elif result == "locked":
            messagebox.showerror("Account Locked", "Too many invalid attempts. Account is locked.")
        elif result == "invalid":
            messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showerror("Not Found", "Account does not exist.")


    def register_user(self):
        """ user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        if not password_valid(pw):
            messagebox.showerror("Weak Password", "Password must be at least 8 characters, include upper/lowercase, numbers, and special characters.")
            return
        if verify_user(user, pw) != "not_found":
            messagebox.showerror("Exists", "Username already exists.")
            return
        save_user(user, pw)
        messagebox.showinfo("Registered", "User registered successfully.") """
        uname = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        email = simpledialog.askstring("Email", "Enter your email address:")

        if not password_valid(pw):
            messagebox.showerror("Password", "Password must be 8+ characters and include uppercase, lowercase, number, and special character.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, email, last_changed) VALUES (?, ?, ?, ?)",
                      (uname, pw, email, datetime.now().isoformat()))
            conn.commit()
            messagebox.showinfo("Registered", "Account created.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    """ def forgot_password(event=None):
        conn = sqlite3.connect("users_secure.db")
        c = conn.cursor()

        username = simpledialog.askstring("Forgot Password", "Enter your username:")
        if not username:
            return

        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()

        if not user:
            messagebox.showerror("Error", "Username not found.")
            conn.close()
            return

        # Prompt for new password
        while True:
            new_pw = simpledialog.askstring("Reset Password", "Enter your new password:", show="*")
            if not new_pw:
                return
            if not password_valid(new_pw):
                messagebox.showerror(
                    "Weak Password",
                    "Password must:\n• Be at least 8 characters\n• Include uppercase, lowercase, number, and symbol"
                )
                continue
            break

        c.execute("UPDATE users SET password=? WHERE username=?", (new_pw, username))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Password has been reset.") """
    
    def forgot_password(event=None):
        conn = sqlite3.connect("users_secure.db")
        c = conn.cursor()

        # Ask for username
        uname = simpledialog.askstring("Forgot Password", "Enter your username:")
        if not uname:
            return

        # Get email from DB
        c.execute("SELECT email FROM users WHERE username=?", (uname,))
        result = c.fetchone()

        if not result:
            messagebox.showerror("Error", "Username not found.")
            conn.close()
            return

        email_to = result[0]
        if not email_to:
            messagebox.showerror("Error", "No email associated with this account.")
            conn.close()
            return

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Compose email
        msg = EmailMessage()
        msg['Subject'] = 'Your OTP for Password Reset'
        msg['From'] = GMAIL_USER
        msg['To'] = email_to
        msg.set_content(f"Hello,\n\nYour OTP for resetting your password is: {otp}\n\nIf you did not request this, ignore this message.")

        try:
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            messagebox.showerror("Email Failed", f"Could not send OTP.\n\n{e}")
            conn.close()
            return

        # Ask user to input the OTP
        entered_otp = simpledialog.askstring("OTP Verification", f"OTP sent to {email_to}. Enter it here:")
        if entered_otp != otp:
            messagebox.showerror("Invalid OTP", "The OTP you entered is incorrect.")
            conn.close()
            return

        # Ask for new password
        while True:
            new_pw = simpledialog.askstring("Reset Password", "Enter new password:", show="*")
            if not new_pw:
                return
            if not password_valid(new_pw):
                messagebox.showwarning(
                    "Weak Password",
                    "Password must:\n• Be at least 8 characters\n• Include uppercase & lowercase\n• Include a number\n• Include a special character"
                )
                continue
            break

        # Update password in DB
        c.execute("UPDATE users SET password=? WHERE username=?", (new_pw, uname))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Password has been successfully reset.")

    def change_password(self, user):
        if not otp_prompt():
            messagebox.showerror("OTP Failed", "OTP did not match.")
            return

        new_pw = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if not password_valid(new_pw):
            messagebox.showerror("Weak Password", "Password does not meet policy.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT password, password1, password2 FROM users WHERE username=?", (user,))
        old, p1, p2 = c.fetchone()
        conn.close()

        if new_pw in [old, p1, p2]:
            messagebox.showerror("Reused Password", "You cannot reuse the last 3 passwords.")
            return

        update_password(user, new_pw)
        messagebox.showinfo("Password Changed", "Your password was updated.")

    def logout(self):
        self.root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

        topbar = tk.Frame(self.root, bg="#007acc")
        topbar.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(topbar, text="BPIScan Scanner App", font=("Segoe UI", 14, "bold"),
                               bg="#007acc", fg="white")
        title_label.pack(side=tk.LEFT, padx=10, pady=10)

        user_label = tk.Label(topbar, text=f"User: {self.logged_in_user}",
                              bg="#007acc", fg="white", font=("Segoe UI", 10))
        user_label.pack(side=tk.RIGHT, padx=10)

        logout_btn = tk.Button(topbar, text="Logout", bg="#f44336", fg="white", command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=10)

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="Select Scanner", command=self.select_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Scan One", command=self.scan_single).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Scan All", command=self.scan_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Scan Barcode", command=self.scan_barcode_button).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Prev", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save As", command=self.save_image).pack(side=tk.LEFT, padx=5)

        # Thumbnail sidebar
        self.thumb_frame = tk.Frame(self.root, width=150, bg="#f1f1f1")
        self.thumb_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.thumb_canvas = tk.Canvas(self.thumb_frame, bg="#f1f1f1", width=150)
        self.thumb_scrollbar = tk.Scrollbar(self.thumb_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_container = tk.Frame(self.thumb_canvas)

        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)

        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Preview canvas
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        """ self.canvas = tk.Canvas(self.root, bg="white", width=900, height=540)
        self.canvas.pack(padx=10, pady=10, expand=True) """

        # Frame to hold the logo at the bottom right
        self.logo_holder = tk.Label(self.root, image=self.tk_logo, bg="white")
        self.logo_holder.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # bottom-right with margin

        # Bottom frame to hold logo outside the canvas
        bottom_frame = tk.Frame(self.root, bg="#f0f2f5")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 10))

        # Load and display logo
        """ self.dash_logo = Image.open("logo.png")
        self.dash_logo = self.dash_logo.resize((200, 100), Image.ANTIALIAS)
        self.tk_dash_logo = ImageTk.PhotoImage(self.dash_logo)

        logo_label = tk.Label(bottom_frame, image=self.tk_dash_logo, bg="#f0f2f5")
        logo_label.pack(side=tk.RIGHT, padx=10) """


        # Add dashboard logo
        """ self.dash_logo = Image.open("logo.png")
        self.dash_logo = self.dash_logo.resize((200, 100), Image.ANTIALIAS)
        self.tk_dash_logo = ImageTk.PhotoImage(self.dash_logo)
        self.canvas.create_image(890, 530, image=self.tk_dash_logo, anchor=tk.SE)
 """
    def select_device(self):
        devices = pyinsane2.get_devices()
        if not devices:
            messagebox.showerror("No Scanner", "No scanners found.")
            return

        def on_select(event):
            index = listbox.curselection()[0]
            self.device = devices[index]
            popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.title("Select Scanner")
        popup.geometry("300x200")
        tk.Label(popup, text="Double-click to select scanner:", font=("Segoe UI", 10)).pack(pady=5)

        listbox = tk.Listbox(popup, font=("Segoe UI", 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for d in devices:
            listbox.insert(tk.END, d.name)

        listbox.bind("<Double-1>", on_select)

    def scan_single(self):
        self.scan(all_pages=False)

    def scan_all(self):
        self.scan(all_pages=True)

    """ def scan(self, all_pages=False):
        self.image_list = []
        self.current_index = 0
        self.canvas.delete("all")

        if not self.device:
            self.select_device()
            if not self.device:
                return

        try:
            # Set source to ADF if available
            if "source" in self.device.options:
                try:
                    self.device.options["source"].value = "ADF"
                    print("ADF source selected.")
                except Exception as e:
                    print("Cannot set ADF:", e)

            scan_session = self.device.scan(multiple=all_pages)

            def do_scan():
                try:
                    while True:
                        try:
                            scan_session.scan.read()
                        except EOFError:
                            if scan_session.images:
                                img = scan_session.images[-1]
                                self.image_list.append(img)
                                print(f"Scanned page {len(self.image_list)}")
                            if not all_pages:
                                break
                        except Exception as e:
                            print("Scan error:", e)
                            break
                    if self.image_list:
                        self.display_image(self.image_list[0])
                        print(f"Total pages scanned: {len(self.image_list)}")
                    else:
                        messagebox.showinfo("Scan", "No pages were scanned.")
                except Exception as e:
                    messagebox.showerror("Scan Failed", str(e))

            threading.Thread(target=do_scan).start()

        except Exception as e:
            messagebox.showerror("Scan Error", str(e)) """
    
    def scan(self, all_pages=False):
        self.image_list = []
        self.thumb_images = []
        self.current_index = 0
        self.canvas.delete("all")
        for widget in self.thumb_container.winfo_children():
            widget.destroy()

        if not self.device:
            self.select_device()
            if not self.device:
                return

        try:
            # Set source to ADF if available
            if "source" in self.device.options:
                try:
                    self.device.options["source"].value = "ADF"
                    print("ADF source selected.")
                except Exception as e:
                    print("Cannot set ADF:", e)

            scan_session = self.device.scan(multiple=all_pages)

            def do_scan():
                try:
                    while True:
                        try:
                            scan_session.scan.read()
                        except EOFError:
                            if scan_session.images:
                                img = scan_session.images[-1]
                                self.image_list.append(img)
                                self.current_index = len(self.image_list) - 1
                                self.display_image(img)
                                self.add_thumbnail(img, self.current_index)
                            if not all_pages:
                                break
                        except Exception as e:
                            print("Scan error:", e)
                            break
                    if self.image_list:
                        self.display_image(self.image_list[0])
                        print(f"Total pages scanned: {len(self.image_list)}")
                    else:
                        messagebox.showinfo("Scan", "No pages were scanned.")
                except Exception as e:
                    messagebox.showerror("Scan Failed", str(e))

            threading.Thread(target=do_scan).start()

        except Exception as e:
            messagebox.showerror("Scan Error", str(e))

    def display_image(self, image):
        self.canvas.delete("all")
        w, h = image.size
        scale = min(900 / w, 540 / h, 1.0)
        img_resized = image.resize((int(w * scale), int(h * scale)), Image.ANTIALIAS)
        self.tk_img = ImageTk.PhotoImage(img_resized)
        self.canvas.create_image(10, 10, anchor=tk.NW, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def add_thumbnail(self, img, index):
        thumb = img.copy()
        thumb.thumbnail((120, 120))
        tk_thumb = ImageTk.PhotoImage(thumb)
        self.thumb_images.append(tk_thumb)

        lbl = tk.Label(self.thumb_container, image=tk_thumb, borderwidth=2, relief="groove")
        lbl.pack(padx=4, pady=4)
        lbl.bind("<Button-1>", lambda e, i=index: self.show_page(i))

    def show_page(self, index):
        self.current_index = index
        self.display_image(self.image_list[index])

    def update_thumbnail_list(self):
        self.thumb_listbox.delete(0, tk.END)
        for i in range(len(self.image_list)):
            self.thumb_listbox.insert(tk.END, f"Page {i+1}")

    def on_thumbnail_click(self, event):
        selection = self.thumb_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.image_list):
                self.current_index = index
                self.display_image(self.image_list[index])

    def save_image(self):
        if not self.image_list:
            messagebox.showwarning("No Pages", "No scanned pages to save.")
            return

        file_type = simpledialog.askstring("Save As", "Enter file type: pdf, tiff, or jpeg")
        if not file_type:
            return

        file_type = file_type.lower().strip()
        if file_type not in ["pdf", "tiff", "jpeg"]:
            messagebox.showerror("Invalid Format", "Supported formats: pdf, tiff, jpeg")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{file_type}",
            filetypes=[("PDF file", "*.pdf"), ("TIFF file", "*.tiff"), ("JPEG file", "*.jpg")],
            title="Save As"
        )
        if not file_path:
            return

        try:
            base_path, _ = os.path.splitext(file_path)

            if file_type == "pdf":
                self.image_list[0].save(file_path, "PDF", resolution=100, save_all=True, append_images=self.image_list[1:])
            elif file_type == "jpeg":
                for i, img in enumerate(self.image_list):
                    img.save(f"{base_path}_page{i+1}.jpg", "JPEG")
            elif file_type == "tiff":
                for i, img in enumerate(self.image_list):
                    img.save(f"{base_path}_page{i+1}.tiff", "TIFF")

            messagebox.showinfo("Success", f"Pages saved as {file_type.upper()}")

        except Exception as e:
            messagebox.showerror("Save Failed", str(e))

    def prev_page(self):
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.display_image(self.image_list[self.current_index])
            self.thumb_listbox.selection_clear(0, tk.END)
            self.thumb_listbox.selection_set(self.current_index)

    def next_page(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image(self.image_list[self.current_index])
            self.thumb_listbox.selection_clear(0, tk.END)
            self.thumb_listbox.selection_set(self.current_index)

    def extract_barcode_text(self, img):
        try:
            for angle in [0, 90, 180, 270]:
                rotated = img.rotate(angle, expand=True)
                img_cv = cv2.cvtColor(np.array(rotated.convert("RGB")), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                barcodes = decode(gray)
                if barcodes:
                    results = []
                    for barcode in barcodes:
                        barcode_data = barcode.data.decode("utf-8")
                        barcode_type = barcode.type
                        results.append(f"{barcode_type}: {barcode_data}")
                    return "\n".join(results)
            return ""
        except Exception as e:
            print(f"Error decoding barcode: {e}")
            return ""

    def scan_barcode_button(self):
        if not self.image_list:
            messagebox.showwarning("No Image", "Please scan a page first.")
            return

        img = self.image_list[self.current_index]
        text = self.extract_barcode_text(img)

        if text:
            messagebox.showinfo("Barcode", text)
        else:
            messagebox.showinfo("Barcode", "No barcode detected.")

    def zoom_in(self):
        self.canvas.scale("all", 0, 0, 1.25, 1.25)

    def zoom_out(self):
        self.canvas.scale("all", 0, 0, 0.8, 0.8)

if __name__ == "__main__":
    root = tk.Tk()
    app = BPIScanStyleApp(root)
    root.mainloop()
    pyinsane2.exit()
