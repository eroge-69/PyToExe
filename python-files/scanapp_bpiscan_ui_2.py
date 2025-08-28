import csv
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
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
from pyzbar.pyzbar import decode
from openpyxl import Workbook

# ============== Security / Auth Settings ==============
DB_NAME = "users_secure.db"
LOCKOUT_THRESHOLD = 3
PASSWORD_EXPIRY_DAYS = 120
GMAIL_USER = "dmzxc117@gmail.com"
GMAIL_PASSWORD = "cygavrqpnltpeqhw"  # Gmail App Password

# ============== DB Utilities ==========================
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

# ============== Main App ==============================
class BPIScanStyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BPIScan Scanner App")
        self.root.geometry("1100x720")
        self.root.configure(bg="#f0f2f5")
        self.logged_in_user = None

        pyinsane2.init()
        self.device = None
        self.image_list = []
        self.barcode_texts = []   # <-- parallel list to hold decoded barcode text per page
        self.thumb_images = []
        self.current_index = 0
        self.tk_img = None
        self.page_counter = 0
        self.page_rows = []

        init_db()
        self.login_ui()

    # ---------- Login UI ----------
    def login_ui(self):
        self.login_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=500, height=380)

        # Logo (optional)
        self.tk_logo = None
        if os.path.exists("logo.png"):
            try:
                _logo = Image.open("logo.png").resize((220, 90))
                self.tk_logo = ImageTk.PhotoImage(_logo)
            except Exception:
                self.tk_logo = None

        if self.tk_logo:
            tk.Label(self.login_frame, image=self.tk_logo, bg="#ffffff").pack(pady=(8, 0))

        tk.Label(self.login_frame, text="BPIScan Login", font=("Segoe UI", 16, "bold"), bg="#ffffff").pack(pady=10)
        tk.Label(self.login_frame, text="Username", bg="#ffffff").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password", bg="#ffffff").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        btn_frame = tk.Frame(self.login_frame, bg="#ffffff")
        btn_frame.pack(pady=12)

        tk.Button(btn_frame, text="Login", command=self.authenticate_user,
                  bg="#007acc", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        """ tk.Button(btn_frame, text="Register", command=self.register_user,
                  bg="#4caf50", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6) """
        tk.Button(self.login_frame, text="Forgot Password", command=self.forgot_password, fg="blue").pack(pady=6)

    def authenticate_user(self):
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        result = verify_user(user, pw)

        if result == "valid":
            if is_password_expired(user):
                messagebox.showinfo("Password Expired", "You must change your password.")
                self.change_password(user)
            else:
                # ✅ Generate OTP
                otp = str(random.randint(100000, 999999))

                # Fetch email for the user
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE username=?", (user,))
                row = c.fetchone()
                conn.close()

                if not row or not row[0]:
                    messagebox.showerror("Error", "No email associated with this account. Cannot send OTP.")
                    return

                email_to = row[0]

                # Send OTP via email
                try:
                    msg = EmailMessage()
                    msg['Subject'] = 'Your BPIScan Login OTP'
                    msg['From'] = GMAIL_USER
                    msg['To'] = email_to
                    msg.set_content(f"Hello {user},\n\nYour OTP code for login is: {otp}")

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(GMAIL_USER, GMAIL_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                except Exception as e:
                    messagebox.showerror("Email Failed", f"Could not send OTP.\n\n{e}")
                    return

                # Ask user to input OTP
                entered_otp = simpledialog.askstring("OTP Verification", f"Enter the OTP sent to {email_to}:")
                if entered_otp != otp:
                    messagebox.showerror("Invalid OTP", "The OTP you entered is incorrect.")
                    return

                # ✅ Success -> proceed to main UI
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
        uname = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        email = simpledialog.askstring("Email", "Enter your email address:")

        if not password_valid(pw):
            messagebox.showerror("Password", "Password must be 8+ chars with upper/lower/number/symbol.")
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

    def forgot_password(self, event=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        uname = simpledialog.askstring("Forgot Password", "Enter your username:")
        if not uname:
            conn.close()
            return

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

        otp = str(random.randint(100000, 999999))
        msg = EmailMessage()
        msg['Subject'] = 'Your OTP for Password Reset'
        msg['From'] = GMAIL_USER
        msg['To'] = email_to
        msg.set_content(f"Your OTP for resetting your password is: {otp}")

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            messagebox.showerror("Email Failed", f"Could not send OTP.\n\n{e}")
            conn.close()
            return

        entered = simpledialog.askstring("OTP Verification", f"OTP sent to {email_to}. Enter it:")
        if entered != otp:
            messagebox.showerror("Invalid OTP", "The OTP you entered is incorrect.")
            conn.close()
            return

        while True:
            new_pw = simpledialog.askstring("Reset Password", "Enter new password:", show="*")
            if not new_pw:
                conn.close()
                return
            if not password_valid(new_pw):
                messagebox.showwarning(
                    "Weak Password",
                    "Password must be at least 8 chars, include upper & lower, number, and symbol."
                )
                continue
            break

        c.execute("UPDATE users SET password=? WHERE username=?", (new_pw, uname))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Password has been reset.")

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

    # ---------- Main UI ----------
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

        """ # Thumbnail sidebar (left)
        self.thumb_frame = tk.Frame(self.root, width=220, bg="#f7f7f7")
        self.thumb_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.thumb_canvas = tk.Canvas(self.thumb_frame, bg="#f7f7f7", width=220, highlightthickness=0)
        self.thumb_scrollbar = tk.Scrollbar(self.thumb_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_container = tk.Frame(self.thumb_canvas, bg="#f7f7f7")

        self.thumb_container.bind(
            "<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
        )
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw", width=200)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)

        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y) """

        # Sidebar with 3 columns
        self.thumb_frame = tk.Frame(self.root, width=400, bg="#f1f1f1")
        self.thumb_frame.pack(side=tk.LEFT, fill=tk.Y)

        header = tk.Frame(self.thumb_frame, bg="#d9d9d9")
        header.pack(fill=tk.X)
        tk.Label(header, text="Page", width=6, bg="#d9d9d9", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text="Barcode", width=20, bg="#d9d9d9", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text="Preview", width=10, bg="#d9d9d9", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)

        self.thumb_canvas = tk.Canvas(self.thumb_frame, bg="#f1f1f1", width=400)
        self.thumb_scrollbar = tk.Scrollbar(self.thumb_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_container = tk.Frame(self.thumb_canvas)

        self.thumb_container.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_canvas.create_window((0, 0), window=self.thumb_container, anchor="nw")
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)

        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Total scanned counter at the bottom of the left panel
        self.total_label = tk.Label(self.thumb_frame, text="Total Scanned Images: 0", bg="#f1f1f1", font=("Segoe UI", 10, "bold"))
        self.total_label.pack(side=tk.BOTTOM, pady=5)

        # Preview canvas (right)
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Optional: place logo at bottom-right over root
        if self.tk_logo:
            self.logo_holder = tk.Label(self.root, image=self.tk_logo, bg="#f0f2f5")
            self.logo_holder.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-12)

    # ---------- Scanner ----------
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
        popup.geometry("340x260")
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
        # Reset
        self.image_list = []
        self.barcode_texts = []
        self.thumb_images = []
        self.current_index = 0
        self.canvas.delete("all")
        for w in self.thumb_container.winfo_children():
            w.destroy()

        if not self.device:
            self.select_device()
            if not self.device:
                return

        try:
            # Prefer ADF if present
            if "source" in self.device.options:
                try:
                    self.device.options["source"].value = "ADF"
                except Exception:
                    pass

            scan_session = self.device.scan(multiple=all_pages)

            def do_scan():
                try:
                    while True:
                        try:
                            scan_session.scan.read()
                        except EOFError:
                            if scan_session.images:
                                img = scan_session.images[-1]
                                # Append image
                                self.image_list.append(img)
                                page_index = len(self.image_list) - 1

                                # Decode barcode (in background-friendly way)
                                barcode_text = self.decode_barcodes(img) or "No barcode"
                                self.barcode_texts.append(barcode_text)

                                # UI update in main thread
                                self.root.after(0, lambda i=page_index, im=img, txt=barcode_text: self._on_page_scanned(i, im, txt))

                                self.add_row(self.current_index, barcode_text, img)

                            if not all_pages:
                                break
                        except Exception as e:
                            print("Scan error:", e)
                            break
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Scan Failed", str(e)))

            threading.Thread(target=do_scan, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Scan Error", str(e)) """

    def scan(self, all_pages=False):
        self.image_list = []
        self.page_rows = []  # reset rows
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
                except:
                    pass

            scan_session = self.device.scan(multiple=all_pages)

            def do_scan():
                page_num = 1
                try:
                    while True:
                        try:
                            scan_session.scan.read()
                        except EOFError:
                            if scan_session.images:
                                img = scan_session.images[-1]
                                self.image_list.append(img)

                                # Try to auto-detect barcode text
                                barcode_text = self.decode_barcodes(img)

                                # Add row with Page#, Barcode text, Thumbnail
                                self.add_row(img, page_num, barcode_text)

                                # Show first page
                                if page_num == 1:
                                    self.display_image(img)

                                page_num += 1

                            if not all_pages:
                                break
                        except Exception as e:
                            print("Scan error:", e)
                            break

                except Exception as e:
                    messagebox.showerror("Scan Failed", str(e))

            threading.Thread(target=do_scan).start()

        except Exception as e:
            messagebox.showerror("Scan Error", str(e))


    def _on_page_scanned(self, index, img, barcode_text):
        # Show page immediately
        self.current_index = index
        self.display_image(img)

        # Add thumbnail + barcode text below it
        self.add_thumbnail(img, index, barcode_text)

    # ---------- Display / Thumbnails ----------
    def display_image(self, image):
        self.canvas.delete("all")
        w, h = image.size
        # Scale to fit a typical 1024x600 area (leaving margins), but keep original if smaller
        scale = min(1024 / max(w, 1), 620 / max(h, 1), 1.0)
        img_resized = image.resize((max(1, int(w * scale)), max(1, int(h * scale))))
        self.tk_img = ImageTk.PhotoImage(img_resized)
        self.canvas.create_image(10, 10, anchor=tk.NW, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    """ def add_row(self, index, barcode_text, full_image):
        row = tk.Frame(self.thumb_container, bg="#f7f7f7", bd=0)
        row.pack(padx=4, pady=4, anchor="w", fill="x")

        # tk.Label(row, text=str(index+1), width=6, bg="#f7f7f7", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        entry = tk.Entry(row, width=25, font=("Segoe UI", 9))
        entry.insert(0, barcode_text if barcode_text else "No barcode")
        entry.pack(side=tk.LEFT, padx=5)

        def update_text(event=None, idx=index, entry_widget=entry):
            self.barcode_texts[idx] = entry_widget.get()
        entry.bind("<FocusOut>", update_text)
        entry.bind("<Return>", update_text)

        thumb_img = full_image.copy()
        thumb_img.thumbnail((60, 60))
        tk_thumb = ImageTk.PhotoImage(thumb_img)
        thumb_label = tk.Label(row, image=tk_thumb, bg="#f7f7f7")
        thumb_label.image = tk_thumb
        thumb_label.pack(side=tk.LEFT, padx=5)
        thumb_label.bind("<Button-1>", lambda e, i=index: self.show_page(i)) """

    def add_row(self, img, page_number, barcode_text=""):
        """
        Add a row with (page number, editable barcode entry, thumbnail) for each scanned page
        """
        row_frame = tk.Frame(self.thumb_container, bg="#f9f9f9", pady=2)
        row_frame.pack(fill=tk.X, padx=3, pady=2)

        # --- Column 1: Page Number ---
        lbl_page = tk.Label(row_frame, text=str(page_number), width=5, anchor="center", bg="#e6e6e6")
        lbl_page.pack(side=tk.LEFT, padx=2)

        # --- Column 2: Editable Barcode Text ---
        entry = tk.Entry(row_frame, width=25)
        entry.insert(0, barcode_text if barcode_text else f"Page_{page_number}")
        entry.pack(side=tk.LEFT, padx=2)

        # --- Column 3: Thumbnail ---
        thumb = img.copy()
        thumb.thumbnail((180, 180))
        tk_thumb = ImageTk.PhotoImage(thumb)

        lbl_thumb = tk.Label(row_frame, image=tk_thumb, borderwidth=1, relief="solid")
        lbl_thumb.image = tk_thumb  # keep reference
        lbl_thumb.pack(side=tk.LEFT, padx=2)

        # Make thumbnail clickable → show that page in main canvas
        lbl_thumb.bind("<Button-1>", lambda e, i=len(self.image_list): self.show_page(i-1))

        # Store this row for later access (e.g. Save)
        self.page_rows.append((entry, lbl_thumb))

        # --- Update total scanned counter ---
        self.total_label.config(text=f"Total Scanned Images: {len(self.image_list)}")


    def add_thumbnail(self, img, index, barcode_text=""):
        # Create a container frame per page (image + text under it)
        frame = tk.Frame(self.thumb_container, bg="#f7f7f7", bd=0)
        frame.pack(padx=6, pady=6, anchor="w", fill="x")

        # Image thumbnail
        thumb = img.copy()
        thumb.thumbnail((180, 180))
        tk_thumb = ImageTk.PhotoImage(thumb)
        self.thumb_images.append(tk_thumb)  # keep reference

        img_lbl = tk.Label(frame, image=tk_thumb, borderwidth=2, relief="groove", bg="#ffffff", cursor="hand2")
        img_lbl.pack(anchor="w")
        img_lbl.bind("<Button-1>", lambda e, i=index: self.show_page(i))

        # Editable barcode text field under thumbnail
        txt = barcode_text if barcode_text else "No barcode"
        entry = tk.Entry(frame, width=25, font=("Segoe UI", 9))
        entry.insert(0, txt)
        entry.pack(anchor="w", pady=(3, 0))

        # Save changes when entry loses focus or user presses Enter
        def update_text(event=None, idx=index, entry_widget=entry):
            self.barcode_texts[idx] = entry_widget.get()

        entry.bind("<FocusOut>", update_text)
        entry.bind("<Return>", update_text)


    def show_page(self, index):
        if 0 <= index < len(self.image_list):
            self.current_index = index
            self.display_image(self.image_list[index])

    # ---------- Save / Paging ----------
    """ def save_image(self):
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
                for i, im in enumerate(self.image_list):
                    im.save(f"{base_path}_page{i+1}.jpg", "JPEG")
            elif file_type == "tiff":
                for i, im in enumerate(self.image_list):
                    im.save(f"{base_path}_page{i+1}.tiff", "TIFF")

            messagebox.showinfo("Success", f"Pages saved as {file_type.upper()}")

        except Exception as e:
            messagebox.showerror("Save Failed", str(e)) """
    
    def save_image(self):
        if not self.image_list:
            messagebox.showwarning("No Pages", "No scanned pages to save.")
            return

        # Ask format
        file_type = simpledialog.askstring("Save As", "Enter format: pdf, png, jpeg, or tiff")
        if not file_type:
            return

        file_type = file_type.lower().strip()
        if file_type not in ["pdf", "png", "jpeg", "tiff"]:
            messagebox.showerror("Invalid Format", "Supported: pdf, png, jpeg, tiff")
            return

        # Select folder to save files
        folder = filedialog.askdirectory(title="Select Save Folder")
        if not folder:
            return

        try:
            used_names = set()
            saved_files = []

            # Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Scan Report"
            ws.append(["Page", "Barcode", "Filename"])  # headers

            if file_type == "pdf":
                # Save all pages into one multipage PDF
                pdf_path = os.path.join(folder, "scanned_output.pdf")
                self.image_list[0].save(
                    pdf_path, "PDF", resolution=100,
                    save_all=True, append_images=self.image_list[1:]
                )
                saved_files.append(pdf_path)

                # Add rows to Excel
                for idx, (entry, _) in enumerate(self.page_rows, start=1):
                    ws.append([idx, entry.get().strip(), os.path.basename(pdf_path)])

            else:
                # Save each page separately
                for idx, (img, (entry, _)) in enumerate(zip(self.image_list, self.page_rows), start=1):
                    base_name = entry.get().strip()
                    if not base_name:
                        base_name = f"Page_{idx}"

                    # Prevent duplicate filenames
                    original_name = base_name
                    counter = 1
                    while base_name in used_names:
                        base_name = f"{original_name}_{counter}"
                        counter += 1
                    used_names.add(base_name)

                    ext = "jpg" if file_type == "jpeg" else file_type
                    filename = os.path.join(folder, f"{base_name}.{ext}")
                    img.save(filename, file_type.upper())
                    saved_files.append(filename)

                    # Add row to Excel
                    ws.append([idx, entry.get().strip(), os.path.basename(filename)])

            # Save Excel report
            excel_path = os.path.join(folder, "scan_report.xlsx")
            wb.save(excel_path)
            saved_files.append(excel_path)

            messagebox.showinfo("Saved", f"All results saved to {folder}")
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))
    
    
        # ------------------- SAVE -------------------
    def save_all(self):
        if not self.image_list:
            messagebox.showwarning("No Data", "No scanned images to save.")
            return

        folder = filedialog.askdirectory(title="Select Folder to Save Results")
        if not folder:
            return

        try:
            # save images using barcode text as filename
            saved_filenames = []
            for i, img in enumerate(self.image_list):
                # get text from editable field
                text = self.barcode_texts[i].strip() if i < len(self.barcode_texts) else ""
                # sanitize filename (remove invalid chars)
                safe_text = re.sub(r'[^a-zA-Z0-9_-]', "_", text)
                if not safe_text:
                    safe_text = f"page_{i+1}"
                filename = f"{safe_text}.png"

                img_path = os.path.join(folder, filename)
                img.save(img_path)
                saved_filenames.append(filename)

            # save CSV
            csv_path = os.path.join(folder, "barcodes.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Page", "Barcode Text", "Filename"])
                for i, text in enumerate(self.barcode_texts):
                    writer.writerow([i + 1, text, saved_filenames[i]])

            messagebox.showinfo("Saved", f"All results saved to {folder}")
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))


    def prev_page(self):
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.display_image(self.image_list[self.current_index])

    def next_page(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image(self.image_list[self.current_index])

    # ---------- Barcode ----------
    def scan_barcode_button(self):
        if not self.image_list:
            messagebox.showwarning("No Image", "Please scan a page first.")
            return
        img = self.image_list[self.current_index]
        text = self.decode_barcodes(img) or "No barcode"
        messagebox.showinfo("Barcode", text)

    def decode_barcodes(self, pil_img):
        """
        Robust barcode reading:
        - tries multiple rotations
        - grayscale + bilateral filter + CLAHE
        - adaptive threshold pass
        Returns a single string with all {TYPE}: value lines, or "" if none.
        """
        try:
            results = []
            for angle in (0, 90, 180, 270):
                rotated = pil_img.rotate(angle, expand=True)
                img_cv = cv2.cvtColor(np.array(rotated.convert("RGB")), cv2.COLOR_RGB2BGR)

                # Pass 1: mild denoise + CLAHE
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 7, 55, 55)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                eq = clahe.apply(gray)

                # Try decoding
                found = decode(eq)
                if not found:
                    # Pass 2: adaptive threshold to enhance bars/edges
                    thr = cv2.adaptiveThreshold(eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 31, 5)
                    found = decode(thr)

                for obj in found:
                    try:
                        data = obj.data.decode("utf-8", errors="replace")
                    except Exception:
                        data = str(obj.data)
                    typ = obj.type
                    # line = f"{typ}: {data}"
                    line = f"{data}"
                    if line not in results:
                        results.append(line)

            return "\n".join(results)
        except Exception as e:
            print(f"[Barcode] Error: {e}")
            return ""

    # ---------- Zoom ----------
    def zoom_in(self):
        self.canvas.scale("all", 1.25, 1.25, 1.25, 1.25)

    def zoom_out(self):
        self.canvas.scale("all", 0.8, 0.8, 0.8, 0.8)

# ============== Run ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = BPIScanStyleApp(root)
    root.mainloop()
    pyinsane2.exit()
