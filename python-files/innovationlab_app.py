import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import sqlite3
import hashlib
import os
import shutil
import datetime

DB_FILE = "innovationlab_app.db"
DOC_FOLDER = "user_documents"
RESET_KEYWORD = "NlNiykyk"

# Professional, Google-flavored soft theme
BG_MAIN = "#e3f2fd"        # skyblue
BG_CARD = "#ffffff"        # white card
COLOR_HEADER = "#1967d2"   # Google blue
COLOR_ACCENT = "#039be5"   # cyan/blue accent
COLOR_BTN = "#1976d2"
COLOR_BTN_FG = "#fff"
COLOR_BTN_HOVER = "#0353a4"
FONT_FAMILY = "Segoe UI"

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        file_path TEXT,
        title TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        author TEXT,
        publication TEXT,
        edition TEXT,
        price REAL,
        unique_id TEXT UNIQUE,
        status TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        designation TEXT,
        year_enrolled TEXT,
        current_year TEXT,
        remarks TEXT
    )''')
    if not os.path.exists(DOC_FOLDER):
        os.makedirs(DOC_FOLDER)
    c.execute("SELECT * FROM users WHERE username = 'NIRAJ'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ("NIRAJ", hash_password("admin123"), "Admin"))
    conn.commit()
    conn.close()

class InnovationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Innovation Lab System")
        self.root.configure(bg=BG_MAIN)
        self.current_user = None
        self.user_id = None
        self.role = None
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', font=(FONT_FAMILY,11), rowheight=25, background="#eaf6fd", fieldbackground="#eaf6fd", foreground="#274472")
        style.map('Treeview', background=[('selected',COLOR_ACCENT)], foreground=[('selected',COLOR_BTN_FG)])
        style.configure('Treeview.Heading', font=(FONT_FAMILY,12,'bold'), background=COLOR_BTN, foreground=COLOR_BTN_FG)
        self.login_screen()

    def login_screen(self):
        self.clear_root()
        self.root.configure(bg=BG_MAIN)
        frame = tk.Frame(self.root, padx=32, pady=32, bg=BG_CARD)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(
            frame, text="INSTRUMENTATION & CONTROL",
            font=(FONT_FAMILY, 17, "bold"),
            fg=COLOR_HEADER, bg=BG_CARD
        ).pack(pady=(1, 14))
        tk.Label(frame, text="Login", font=(FONT_FAMILY, 15, "bold"),
                 fg=COLOR_HEADER, bg=BG_CARD).pack(pady=(0, 13))
        tk.Label(frame, text="Username", font=(FONT_FAMILY, 12), bg=BG_CARD).pack(anchor="w", pady=(0,2))
        self.uname_entry = tk.Entry(frame, font=(FONT_FAMILY, 12))
        self.uname_entry.pack(pady=(0,8), fill="x")
        tk.Label(frame, text="Password", font=(FONT_FAMILY, 12), bg=BG_CARD).pack(anchor="w", pady=(0,2))
        self.pwd_entry = tk.Entry(frame, show="*", font=(FONT_FAMILY, 12))
        self.pwd_entry.pack(pady=(0,12), fill="x")
        btn_login = tk.Button(frame, text="Login", command=self.try_login,
                              font=(FONT_FAMILY, 12, "bold"),
                              bg=COLOR_BTN, fg=COLOR_BTN_FG, activebackground=COLOR_BTN_HOVER)
        btn_login.pack(fill="x", pady=(3,2))
        btn_forgot = tk.Button(frame, text="Forgot Password?", command=self.password_reset_popup,
                               font=(FONT_FAMILY, 10, "underline"),
                               fg=COLOR_ACCENT, cursor="hand2", bg=BG_CARD, relief="flat", bd=0)
        btn_forgot.pack(anchor="e", pady=(9,0))
    
    def try_login(self):
        uname = self.uname_entry.get().strip()
        pwd = self.pwd_entry.get()
        if not uname or not pwd:
            messagebox.showerror("Error", "Please enter username and password")
            return
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (uname,))
            row = c.fetchone()
            conn.close()
            if row and hash_password(pwd) == row[1]:
                self.user_id, self.current_user, self.role = row[0], uname, row[2]
                self.main_dashboard()
            else:
                messagebox.showerror("Error", "Login failed")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected Error: {str(e)}")
    
    def password_reset_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Password Reset")
        popup.transient(self.root)
        tk.Label(popup, text="Enter your username:").grid(row=0, column=0, sticky="e", pady=2)
        uname_entry = tk.Entry(popup)
        uname_entry.grid(row=0, column=1, pady=2)
        tk.Label(popup, text="Reset Keyword:").grid(row=1, column=0, sticky="e", pady=2)
        keyword_entry = tk.Entry(popup, show="*")
        keyword_entry.grid(row=1, column=1, pady=2)
        tk.Label(popup, text="New Password:").grid(row=2, column=0, sticky="e", pady=2)
        pwd1_entry = tk.Entry(popup, show="*")
        pwd1_entry.grid(row=2, column=1, pady=2)
        tk.Label(popup, text="Confirm Password:").grid(row=3, column=0, sticky="e", pady=2)
        pwd2_entry = tk.Entry(popup, show="*")
        pwd2_entry.grid(row=3, column=1, pady=2)
        def do_reset():
            uname = uname_entry.get().strip()
            keyword = keyword_entry.get().strip()
            pwd1 = pwd1_entry.get()
            pwd2 = pwd2_entry.get()
            if not uname or not keyword or not pwd1 or not pwd2:
                messagebox.showerror("Error", "All fields required.", parent=popup)
                return
            if keyword != RESET_KEYWORD:
                messagebox.showerror("Error", "Incorrect reset keyword.", parent=popup)
                return
            if pwd1 != pwd2:
                messagebox.showerror("Error", "Passwords do not match.", parent=popup)
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (uname,))
            userrow = c.fetchone()
            if not userrow:
                messagebox.showerror("Error", "No such user.", parent=popup)
                conn.close()
                return
            c.execute("UPDATE users SET password_hash=? WHERE username=?",
                      (hash_password(pwd1), uname))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password reset successful.", parent=popup)
            popup.destroy()
        tk.Button(popup, text="Reset Password", command=do_reset).grid(row=4, column=0, columnspan=2, pady=8)

    def main_dashboard(self):
        self.clear_root()
        self.root.configure(bg=BG_MAIN)
        frame = tk.Frame(self.root, padx=16, pady=16, bg=BG_CARD)
        frame.pack(padx=40, pady=30, fill="both", expand=True)
        tk.Label(frame, text=f"Welcome, {self.current_user} ({self.role})", font=(FONT_FAMILY, 15, "bold"),
                 fg=COLOR_HEADER, bg=BG_CARD).pack(pady=8)
        tk.Button(frame, text="🗂️ Workspace", font=(FONT_FAMILY,12), bg=COLOR_ACCENT, fg="white", command=self.user_workspace).pack(pady=7, fill="x")
        if self.role.lower() == "library":
            tk.Button(frame, text="📚 Book Management", font=(FONT_FAMILY,12), bg=COLOR_ACCENT, fg="white", command=self.library_books).pack(pady=7, fill="x")
        if self.role.lower() == "innovationlab":
            tk.Button(frame, text="👥 Members", font=(FONT_FAMILY,12), bg=COLOR_ACCENT, fg="white", command=self.member_management).pack(pady=7, fill="x")
        if self.role == "Admin":
            tk.Button(frame, text="👤 Admin: Manage Users", font=(FONT_FAMILY,12), bg=COLOR_ACCENT, fg="white", command=self.admin_panel).pack(pady=7, fill="x")
        tk.Button(frame, text="Logout", font=(FONT_FAMILY,12), command=self.login_screen, bg="#ffedc6", fg="#1967d2").pack(pady=30, fill="x")

    def user_workspace(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=15, pady=15, bg=BG_MAIN)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=f"Workspace: {self.current_user} ({self.role})", font=(FONT_FAMILY, 13), bg=BG_MAIN, fg=COLOR_HEADER).pack(pady=10)
        docs = self.get_user_docs(self.user_id)
        listbox = tk.Listbox(frame, width=60, font=(FONT_FAMILY,10))
        for doc in docs:
            listbox.insert("end", f"{doc[0]}. {doc[2]} ({doc[3][:19]})")
        listbox.pack(pady=5)
        btn_frame = tk.Frame(frame, bg=BG_MAIN)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Upload Document", command=lambda:self.upload_doc(listbox), font=(FONT_FAMILY,10)).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Download", command=lambda:self.download_doc(listbox), font=(FONT_FAMILY,10)).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Delete", command=lambda:self.delete_doc(listbox), font=(FONT_FAMILY,10)).pack(side="left", padx=6)
        tk.Button(frame, text="⬅️ Back", command=self.main_dashboard, font=(FONT_FAMILY,11,"bold"), bg="#f3eaf7", fg=COLOR_ACCENT).pack(pady=10)
    def get_user_docs(self, user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if self.role == "Admin":
            c.execute("SELECT * FROM documents")
        else:
            c.execute("SELECT * FROM documents WHERE owner_id = ?", (user_id,))
        docs = c.fetchall()
        conn.close()
        return docs

    def upload_doc(self, listbox):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        title = simpledialog.askstring("Title", "Enter Document Title:", parent=self.root)
        if not title: return
        userdir = os.path.join(DOC_FOLDER, str(self.user_id))
        if not os.path.exists(userdir):
            os.makedirs(userdir)
        fname = os.path.basename(filepath)
        saved_path = os.path.join(userdir, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{fname}")
        try:
            shutil.copy2(filepath, saved_path)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO documents (owner_id, file_path, title) VALUES (?, ?, ?)",
                      (self.user_id, saved_path, title))
            conn.commit()
            conn.close()
            messagebox.showinfo("Uploaded", "Document uploaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"File upload error: {str(e)}")
        self.user_workspace()

    def download_doc(self, listbox):
        idx = listbox.curselection()
        if not idx: return
        doc_id = int(listbox.get(idx).split(".")[0])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
        row = c.fetchone()
        conn.close()
        if row:
            if not os.path.exists(row[0]):
                messagebox.showerror("Error", "File missing.")
                return
            target = filedialog.asksaveasfilename(initialfile=os.path.basename(row[0]))
            if target:
                try:
                    shutil.copy2(row[0], target)
                    messagebox.showinfo("Downloaded", "File saved successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"File download error: {str(e)}")

    def delete_doc(self, listbox):
        idx = listbox.curselection()
        if not idx: return
        doc_id = int(listbox.get(idx).split(".")[0])
        confirm = messagebox.askyesno("Confirm", "Delete this document?")
        if confirm:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
            row = c.fetchone()
            if row and os.path.exists(row[0]):
                try:
                    os.remove(row[0])
                except Exception:
                    pass
            c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()
            self.user_workspace()

    # -------- MEMBERS MANAGEMENT FOR INNOVATION LAB -----
    def member_management(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=15, pady=15, bg=BG_MAIN)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Innovation Lab Members", font=(FONT_FAMILY, 15, "bold"), bg=BG_MAIN, fg=COLOR_HEADER).pack(pady=6)
        columns = ("srno", "name", "designation", "year_enrolled", "current_year", "remarks")
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading("srno", text="SR NO.")
        tree.heading("name", text="Name")
        tree.heading("designation", text="Designation")
        tree.heading("year_enrolled", text="Year Enrolled")
        tree.heading("current_year", text="Current Academic Year")
        tree.heading("remarks", text="Remarks")
        for col in columns:
            tree.column(col, width=120)
        tree.pack(fill="x", expand=True, pady=5)
        self.populate_members(tree)
        btnfrm = tk.Frame(frame, bg=BG_MAIN)
        btnfrm.pack(pady=8)
        tk.Button(btnfrm, text="Add Member", command=lambda:self.add_member(tree), font=(FONT_FAMILY,10)).pack(side="left", padx=5)
        tk.Button(btnfrm, text="Edit Member", command=lambda:self.edit_member(tree), font=(FONT_FAMILY,10)).pack(side="left", padx=5)
        tk.Button(btnfrm, text="Delete Member", command=lambda:self.delete_member(tree), font=(FONT_FAMILY,10)).pack(side="left", padx=5)
        tk.Button(frame, text="⬅️ Back", command=self.main_dashboard, font=(FONT_FAMILY,11,"bold"), bg="#f3eaf7", fg=COLOR_ACCENT).pack(pady=10)

    def populate_members(self, tree):
        for i in tree.get_children(): tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM members")
        all_rows = c.fetchall()
        for idx, row in enumerate(all_rows, 1):
            tree.insert("", "end", values=(idx, row[1], row[2], row[3], row[4], row[5]))
        conn.close()

    def add_member(self, tree):
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Add Member")
        fields = ["Name", "Designation", "Year Enrolled", "Current Academic Year", "Remarks"]
        entries = []
        for i, f in enumerate(fields):
            tk.Label(popup, text=f).grid(row=i, column=0, pady=2, sticky="e")
            e = tk.Entry(popup, width=38)
            e.grid(row=i, column=1, padx=8, pady=2)
            entries.append(e)
        def on_ok():
            values = [ent.get().strip() for ent in entries]
            if not values[0] or not values[1] or not values[2] or not values[3]:
                messagebox.showerror("Error", "Name, Designation, Year Enrolled & Current Academic Year are required.", parent=popup)
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO members (name, designation, year_enrolled, current_year, remarks) VALUES (?, ?, ?, ?, ?)",
                      (values[0], values[1], values[2], values[3], values[4]))
            conn.commit()
            conn.close()
            popup.destroy()
            self.populate_members(tree)
        tk.Button(popup, text="OK", command=on_ok).grid(row=len(fields), column=0, columnspan=2, pady=9)

    def edit_member(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "No member selected!")
            return
        row_vals = tree.item(sel[0])["values"]
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Edit Member")
        labels = ["Name", "Designation", "Year Enrolled", "Current Academic Year", "Remarks"]
        entries = []
        for i, f in enumerate(labels):
            tk.Label(popup, text=f).grid(row=i, column=0, pady=2, sticky="e")
            e = tk.Entry(popup, width=38)
            e.grid(row=i, column=1, padx=8, pady=2)
            if row_vals[i+1]:
                e.insert(0, row_vals[i+1])
            entries.append(e)
        def on_ok():
            values = [ent.get().strip() for ent in entries]
            if not values[0] or not values[1] or not values[2] or not values[3]:
                messagebox.showerror("Error", "Name, Designation, Year Enrolled & Current Academic Year are required.", parent=popup)
                return
            srno = int(row_vals[0])-1
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id FROM members")
            all_ids = [row[0] for row in c.fetchall()]
            if srno < 0 or srno >= len(all_ids):
                messagebox.showerror("Error", "Member not found in database.", parent=popup)
                conn.close()
                popup.destroy()
                return
            real_id = all_ids[srno]
            c.execute('''UPDATE members SET name=?, designation=?, year_enrolled=?, current_year=?, remarks=? WHERE id=?''',
                      (values[0], values[1], values[2], values[3], values[4], real_id))
            conn.commit()
            conn.close()
            popup.destroy()
            self.populate_members(tree)
        tk.Button(popup, text="OK", command=on_ok).grid(row=len(labels), column=0, columnspan=2, pady=9)

    def delete_member(self, tree):
        sel = tree.selection()
        if not sel: return
        row_vals = tree.item(sel[0])["values"]
        if not messagebox.askyesno("Delete", "Delete selected member?"): return
        srno = int(row_vals[0])-1
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id FROM members")
        all_ids = [row[0] for row in c.fetchall()]
        if srno < 0 or srno >= len(all_ids):
            messagebox.showerror("Error", "Member not found in database.")
            conn.close()
            return
        real_id = all_ids[srno]
        c.execute("DELETE FROM members WHERE id=?", (real_id,))
        conn.commit()
        conn.close()
        self.populate_members(tree)

    # -------- BOOK MANAGEMENT (Library role) --------
    def library_books(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=12, pady=12, bg=BG_MAIN)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Library Book Management", font=(FONT_FAMILY, 15, "bold"),
                 bg=BG_MAIN, fg=COLOR_HEADER).pack(pady=6)
        columns = ("id", "name", "author", "publication", "edition", "price", "unique_id", "status")
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=110)
        tree.pack(pady=5, fill="x", expand=True)
        self.populate_books(tree)
        btnfrm = tk.Frame(frame)
        btnfrm.pack(pady=8)
        tk.Button(btnfrm, text="Add Book", command=lambda:self.add_book(tree)).pack(side="left", padx=3)
        tk.Button(btnfrm, text="Edit Book", command=lambda:self.edit_book(tree)).pack(side="left", padx=3)
        tk.Button(btnfrm, text="Delete Book", command=lambda:self.delete_book(tree)).pack(side="left", padx=3)
        tk.Button(frame, text="⬅️ Back", command=self.main_dashboard).pack(pady=6)
    def populate_books(self, tree):
        for i in tree.get_children(): tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
    def add_book(self, tree):
        data = self.book_form()
        if data:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute(
                "INSERT INTO books (name, author, publication, edition, price, unique_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Unique ID already exists!")
            conn.close()
            self.populate_books(tree)
    def edit_book(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No book selected")
            return
        vals = tree.item(selected[0])["values"]
        data = self.book_form(vals)
        if data:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute(
                    "UPDATE books SET name=?, author=?, publication=?, edition=?, price=?, unique_id=?, status=? WHERE id=?",
                    data + (vals[0],))
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Unique ID already exists!")
            conn.close()
            self.populate_books(tree)
    def delete_book(self, tree):
        selected = tree.selection()
        if not selected: return
        vals = tree.item(selected[0])["values"]
        confirm = messagebox.askyesno("Confirm", "Delete this book?")
        if confirm:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE id=?", (vals[0],))
            conn.commit()
            conn.close()
            self.populate_books(tree)
    def book_form(self, default=None):
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Book Entry")
        fields = ["Name", "Author", "Publication", "Edition", "Price (₹)", "Unique ID", "Status (Purchased/Donated)"]
        entries = []
        for i, f in enumerate(fields):
            tk.Label(popup, text=f).grid(row=i, column=0, pady=2, sticky="e")
            e = tk.Entry(popup, width=40)
            e.grid(row=i, column=1, padx=8, pady=2)
            if default:
                e.insert(0, default[i+1])
            entries.append(e)
        result = []
        def on_ok():
            val = [entries[i].get().strip() for i in range(len(entries))]
            if not all(val):
                messagebox.showerror("Error", "Fill all fields", parent=popup)
                return
            try:
                val[4] = float(val[4])
            except:
                messagebox.showerror("Error", "Invalid price", parent=popup)
                return
            result.extend(val)
            popup.destroy()
        tk.Button(popup, text="OK", command=on_ok).grid(row=len(fields), column=0, columnspan=2, pady=7)
        self.root.wait_window(popup)
        if result:
            return tuple(result)
        return None

    ###### ADMIN PANEL ######
    def admin_panel(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=12, pady=12, bg=BG_MAIN)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Admin Panel: Manage Users", font=(FONT_FAMILY, 15, "bold"),
                 bg=BG_MAIN, fg=COLOR_HEADER).pack(pady=6)
        columns = ("id", "username", "role")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode='browse')
        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=140)
        tree.pack(pady=6, fill="both", expand=True)
        self.populate_users(tree)
        btnfrm = tk.Frame(frame, bg=BG_MAIN)
        btnfrm.pack(pady=5)
        tk.Button(btnfrm, text="Add User", command=lambda:self.add_user(tree), font=(FONT_FAMILY, 10)).pack(side="left", padx=5)
        tk.Button(btnfrm, text="Edit User", command=lambda:self.edit_user(tree), font=(FONT_FAMILY, 10)).pack(side="left", padx=5)
        tk.Button(btnfrm, text="Delete User", command=lambda:self.del_user(tree), font=(FONT_FAMILY, 10)).pack(side="left", padx=5)
        tk.Button(frame, text="⬅️ Back", command=self.main_dashboard, font=(FONT_FAMILY,11,"bold"), bg="#f3eaf7", fg=COLOR_ACCENT).pack(pady=10)
    def populate_users(self, tree):
        for i in tree.get_children(): tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
    def add_user(self, tree):
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Add User")
        tk.Label(popup, text="Username:", font=(FONT_FAMILY,11)).grid(row=0, column=0, sticky="e", pady=2)
        ent_uname = tk.Entry(popup, font=(FONT_FAMILY,11))
        ent_uname.grid(row=0, column=1, pady=2, padx=8)
        tk.Label(popup, text="Password:", font=(FONT_FAMILY,11)).grid(row=1, column=0, sticky="e", pady=2)
        ent_pwd = tk.Entry(popup, show="*", font=(FONT_FAMILY,11))
        ent_pwd.grid(row=1, column=1, pady=2, padx=8)
        tk.Label(popup, text="Role:", font=(FONT_FAMILY,11)).grid(row=2, column=0, sticky="e", pady=2)
        role_cbox = ttk.Combobox(popup, values=["Secretary", "President", "Treasurer", "InnovationLab", "Library", "Other"], state="readonly", font=(FONT_FAMILY,11))
        role_cbox.grid(row=2, column=1, pady=2, padx=8)
        role_cbox.set("Secretary")
        other_role_ent = tk.Entry(popup, font=(FONT_FAMILY,11))
        other_role_label = tk.Label(popup, text="If Other, specify:", font=(FONT_FAMILY,11))
        def show_other(e):
            if role_cbox.get() == "Other":
                other_role_label.grid(row=3, column=0, sticky="e", pady=2)
                other_role_ent.grid(row=3, column=1, pady=2, padx=8)
            else:
                other_role_label.grid_remove()
                other_role_ent.grid_remove()
        role_cbox.bind("<<ComboboxSelected>>", show_other)
        def on_ok():
            uname = ent_uname.get().strip()
            pwd = ent_pwd.get()
            role = role_cbox.get()
            if role == "Other":
                role = other_role_ent.get().strip()
            if not uname or not pwd or not role:
                messagebox.showerror("Error", "All fields required.", parent=popup)
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          (uname, hash_password(pwd), role))
                conn.commit()
                conn.close()
                popup.destroy()
                self.populate_users(tree)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists", parent=popup)
                conn.close()
        tk.Button(popup, text="OK", command=on_ok, font=(FONT_FAMILY, 11)).grid(row=4, column=0, columnspan=2, pady=10)
    def edit_user(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "No user selected.", parent=self.root)
            return
        vals = tree.item(sel[0])["values"]
        user_id, username, role = vals
        if username == "NIRAJ":
            messagebox.showerror("Error", "Cannot edit admin user.", parent=self.root)
            return
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Edit User")
        tk.Label(popup, text="Username:", font=(FONT_FAMILY,11)).grid(row=0, column=0, sticky="e", pady=2)
        ent_uname = tk.Entry(popup, font=(FONT_FAMILY,11))
        ent_uname.insert(0, username)
        ent_uname.grid(row=0, column=1, pady=2, padx=8)
        tk.Label(popup, text="Password (leave blank = no change):", font=(FONT_FAMILY,11)).grid(row=1, column=0, sticky="e", pady=2)
        ent_pwd = tk.Entry(popup, show="*", font=(FONT_FAMILY,11))
        ent_pwd.grid(row=1, column=1, pady=2, padx=8)
        tk.Label(popup, text="Role:", font=(FONT_FAMILY,11)).grid(row=2, column=0, sticky="e", pady=2)
        role_cbox = ttk.Combobox(popup, values=["Secretary", "President", "Treasurer", "InnovationLab", "Library", "Other"], state="readonly", font=(FONT_FAMILY,11))
        role_cbox.grid(row=2, column=1, pady=2, padx=8)
        if role in ["Secretary", "President", "Treasurer", "InnovationLab", "Library"]:
            role_cbox.set(role)
        else:
            role_cbox.set("Other")
        other_role_ent = tk.Entry(popup, font=(FONT_FAMILY,11))
        other_role_label = tk.Label(popup, text="If Other, specify:", font=(FONT_FAMILY,11))
        if role not in ["Secretary", "President", "Treasurer", "InnovationLab", "Library"]:
            other_role_label.grid(row=3, column=0, sticky="e", pady=2)
            other_role_ent.grid(row=3, column=1, pady=2, padx=8)
            other_role_ent.insert(0, role)
        else:
            other_role_label.grid_remove()
            other_role_ent.grid_remove()
        def show_other(e):
            if role_cbox.get() == "Other":
                other_role_label.grid(row=3, column=0, sticky="e", pady=2)
                other_role_ent.grid(row=3, column=1, pady=2, padx=8)
            else:
                other_role_label.grid_remove()
                other_role_ent.grid_remove()
        role_cbox.bind("<<ComboboxSelected>>", show_other)
        def on_ok():
            new_uname = ent_uname.get().strip()
            new_pwd = ent_pwd.get()
            new_role = role_cbox.get()
            if new_role == "Other":
                new_role = other_role_ent.get().strip()
            if not new_uname or not new_role:
                messagebox.showerror("Error", "Username and role required.", parent=popup)
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                if new_pwd:
                    c.execute(
                        "UPDATE users SET username=?, password_hash=?, role=? WHERE id=?",
                        (new_uname, hash_password(new_pwd), new_role, user_id)
                    )
                else:
                    c.execute(
                        "UPDATE users SET username=?, role=? WHERE id=?",
                        (new_uname, new_role, user_id)
                    )
                conn.commit()
                conn.close()
                popup.destroy()
                self.populate_users(tree)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists", parent=popup)
                conn.close()
        tk.Button(popup, text="OK", command=on_ok, font=(FONT_FAMILY, 11)).grid(row=5, column=0, columnspan=2, pady=10)
    def del_user(self, tree):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])["values"]
        user_id, username, role = vals
        if username == "NIRAJ":
            messagebox.showerror("Error", "Cannot delete the admin user.", parent=self.root)
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete user {username}?", parent=self.root):
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        c.execute("DELETE FROM documents WHERE owner_id=?", (user_id,))
        conn.commit()
        conn.close()
        self.populate_users(tree)

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.geometry("920x650")
    app = InnovationApp(root)
    root.mainloop()
