import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import mysql.connector
from datetime import datetime
import hashlib
from openpyxl import Workbook
from tkcalendar import DateEntry  # For calendar date selection

# === Database connection config ===
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='gateway01.eu-central-1.prod.aws.tidbcloud.com',
            port=4000,
            user='XP2fQd5CAy3maYy.root',
            password='QjDJdmTWKqUrig9r',
            database='stb_system',
            ssl_ca=r'D:\PYTHON\STB PROJECT\isrgrootx1.pem'
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Connection Error", str(e))
        return None

SESSION_USER = None
summary_labels = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_dealer_name(code):
    if not code:
        return ""
    db = connect_db()
    if db is None:
        return ""
    cursor = db.cursor()
    try:
        cursor.execute("SELECT dealer_name FROM dealers WHERE LOWER(dealer_code) = %s", (code.lower(),))
        row = cursor.fetchone()
        return row[0] if row else ""
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching dealer name:\n{str(e)}")
        return ""
    finally:
        cursor.close()
        db.close()

def load_stbs_from_file(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def normalize_status(status):
    """Normalize status strings to consistent casing and spacing."""
    status_map = {
        "in stock": "In Stock",
        "delivered": "Delivered",
        "faulty": "Faulty"
    }
    return status_map.get(status.lower(), status)

def update_summary():
    db = connect_db()
    if db is None:
        return
    cursor = db.cursor()
    counts = {"In Stock": 0, "Delivered": 0, "Faulty": 0}
    try:
        cursor.execute("SELECT LOWER(TRIM(status)), COUNT(*) FROM stock GROUP BY LOWER(TRIM(status))")
        for status, count in cursor.fetchall():
            norm_status = normalize_status(status)
            counts[norm_status] = count
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error loading summary:\n{str(e)}")
    finally:
        cursor.close()
        db.close()
    for key in ["In Stock", "Delivered", "Faulty"]:
        if key in summary_labels:
            def update_label(text=counts.get(key, 0), label=summary_labels[key]):
                label.config(text=str(text))
            root.after_idle(update_label)
    root.after(5000, update_summary)

def perform_action(action_type, dealer, stb_list, done_by):
    db = connect_db()
    if db is None:
        return []
    cursor = db.cursor()
    missing = []
    try:
        for stb in stb_list:
            cursor.execute("SELECT 1 FROM stock WHERE stb_no = %s", (stb,))
            if cursor.fetchone():
                if action_type == "Issue":
                    cursor.execute("UPDATE stock SET status = %s, dealer_code = %s WHERE stb_no = %s", (normalize_status("Delivered"), dealer, stb))
                elif action_type == "Return":
                    cursor.execute("UPDATE stock SET status = %s, dealer_code = NULL WHERE stb_no = %s", (normalize_status("In Stock"), stb))
                elif action_type == "Faulty":
                    cursor.execute("UPDATE stock SET status = %s, dealer_code = NULL WHERE stb_no = %s", (normalize_status("Faulty"), stb))
                cursor.execute(
                    "INSERT INTO logs (action, stb_no, dealer, timestamp, done_by) VALUES (%s, %s, %s, %s, %s)",
                    (action_type, stb, dealer if dealer else '', datetime.now(), done_by)
                )
            else:
                missing.append(stb)
        db.commit()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Transaction failed:\n{str(e)}")
    finally:
        cursor.close()
        db.close()
    update_summary()
    return missing

def replace_stbs_combined(path, dealer, done_by):
    with open(path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    if '---' not in lines:
        messagebox.showerror("Format Error", "Separator '---' not found between old and new STBs.")
        return [], []
    sep_index = lines.index('---')
    old_stbs = lines[:sep_index]
    new_stbs = lines[sep_index + 1:]
    db = connect_db()
    if db is None:
        return [], []
    cursor = db.cursor()
    missing = []
    try:
        for stb in old_stbs:
            cursor.execute("SELECT 1 FROM stock WHERE stb_no = %s", (stb,))
            if cursor.fetchone():
                cursor.execute("UPDATE stock SET status = %s, dealer_code = NULL WHERE stb_no = %s", (normalize_status("In Stock"), stb))
                cursor.execute(
                    "INSERT INTO logs (action, stb_no, dealer, timestamp, done_by) VALUES (%s, %s, %s, %s, %s)",
                    ("Replace_Return", stb, dealer, datetime.now(), done_by)
                )
            else:
                missing.append(stb)
        for stb in new_stbs:
            cursor.execute("SELECT 1 FROM stock WHERE stb_no = %s", (stb,))
            if cursor.fetchone():
                cursor.execute("UPDATE stock SET status = %s, dealer_code = %s WHERE stb_no = %s", (normalize_status("Delivered"), dealer, stb))
                cursor.execute(
                    "INSERT INTO logs (action, stb_no, dealer, timestamp, done_by) VALUES (%s, %s, %s, %s, %s)",
                    ("Replace_Issue", stb, dealer, datetime.now(), done_by)
                )
            else:
                missing.append(stb)
        db.commit()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Replace transaction failed:\n{str(e)}")
    finally:
        cursor.close()
        db.close()
    update_summary()
    return old_stbs + new_stbs, missing

def create_action_tab(tab, action_type, require_dealer_code=True):
    tab.configure(bg="#ffffff")
    dealer_code_entry = None
    dealer_name_label = None
    if require_dealer_code:
        tk.Label(tab, text="Dealer Code", font=("Segoe UI", 16, "bold"), bg="#ffffff").pack(pady=(20, 5))
        dealer_code_entry = tk.Entry(tab, font=("Segoe UI", 16), width=40, bd=2, relief=tk.SOLID)
        dealer_code_entry.pack()
        dealer_name_label = tk.Label(tab, text="", font=("Segoe UI", 14), fg="blue", bg="#ffffff")
        dealer_name_label.pack(pady=(5, 10))
        def on_dealer_code_change(event):
            code = dealer_code_entry.get().strip()
            name = get_dealer_name(code)
            dealer_name_label.config(text=f"Dealer Name: {name}" if name else "Dealer not found")
        dealer_code_entry.bind("<KeyRelease>", on_dealer_code_change)
    display = tk.Label(tab, text="No file selected", font=("Segoe UI", 14), bg="#ffffff", fg="dimgray")
    display.pack(pady=(10, 5))
    def browse():
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            tab.stbs = load_stbs_from_file(path)
            display.config(text=f"{len(tab.stbs)} STBs loaded")
            tab.path = path
    def submit():
        if require_dealer_code:
            dealer_code = dealer_code_entry.get().strip()
            dealer_name = get_dealer_name(dealer_code)
            if not dealer_code or not dealer_name:
                messagebox.showerror("Missing", "Valid Dealer Code is required.")
                return
        else:
            dealer_code = ""
            dealer_name = ""
        if not hasattr(tab, "stbs"):
            messagebox.showerror("Missing", "Load STB numbers first.")
            return
        missing_list = perform_action(action_type, dealer_code, tab.stbs, SESSION_USER)
        if missing_list:
            messagebox.showwarning("Missing STBs", "\n".join(missing_list))
        else:
            messagebox.showinfo("Success", f"{action_type} Completed.")
        update_summary()
    tk.Button(tab, text="Select STB File", font=("Segoe UI", 16, "bold"),
              bg="#007acc", fg="white", activebackground="#005f99",
              activeforeground="white", command=browse).pack(pady=(20, 8), ipadx=10, ipady=5)
    tk.Button(tab, text=f"{action_type} STBs", font=("Segoe UI", 16, "bold"),
              bg="#28a745", fg="white", activebackground="#1e7e34",
              activeforeground="white", command=submit).pack(pady=(0, 20), ipadx=10, ipady=5)

def create_replace_tab(tab):
    tab.configure(bg="#ffffff")
    tk.Label(tab, text="Dealer Code", font=("Segoe UI", 16, "bold"), bg="#ffffff").pack(pady=(20, 5))
    dealer_code_entry = tk.Entry(tab, font=("Segoe UI", 16), width=40, bd=2, relief=tk.SOLID)
    dealer_code_entry.pack()
    dealer_name_label = tk.Label(tab, text="", font=("Segoe UI", 14), fg="blue", bg="#ffffff")
    dealer_name_label.pack(pady=(5, 10))
    def on_dealer_code_change(event):
        code = dealer_code_entry.get().strip()
        name = get_dealer_name(code)
        dealer_name_label.config(text=f"Dealer Name: {name}" if name else "Dealer not found")
    dealer_code_entry.bind("<KeyRelease>", on_dealer_code_change)
    file_display = tk.Label(tab, text="No replace file selected", font=("Segoe UI", 14), bg="#ffffff", fg="dimgray")
    file_display.pack(pady=(10, 5))
    def load_file():
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            tab.path = path
            with open(path, 'r') as f:
                lines = f.readlines()
            file_display.config(text=f"{len(lines)} lines loaded")
    def submit():
        if not hasattr(tab, "path"):
            messagebox.showerror("Missing", "No file selected.")
            return
        dealer_code = dealer_code_entry.get().strip()
        dealer_name = get_dealer_name(dealer_code)
        if not dealer_code or not dealer_name:
            messagebox.showerror("Missing", "Valid Dealer Code is required.")
            return
        stbs, missing = replace_stbs_combined(tab.path, dealer_code, SESSION_USER)
        if missing:
            messagebox.showwarning("Missing STBs", "\n".join(missing))
        else:
            messagebox.showinfo("Success", "Replace completed.")
        update_summary()
    tk.Button(tab, text="Select Replace File", font=("Segoe UI", 16, "bold"),
              bg="#007acc", fg="white", activebackground="#005f99",
              activeforeground="white", command=load_file).pack(pady=(20, 8), ipadx=10, ipady=5)
    tk.Button(tab, text="Submit Replace", font=("Segoe UI", 16, "bold"),
              bg="#28a745", fg="white", activebackground="#1e7e34",
              activeforeground="white", command=submit).pack(pady=(0, 20), ipadx=10, ipady=5)

def setup_summary_tab(tab):
    tab.configure(bg="#ffffff")
    tk.Label(tab, text="Real-time STB Summary", font=("Segoe UI", 36, "bold"), bg="#ffffff", fg="#333").pack(pady=40)
    container = tk.Frame(tab, bg="#f9fafb", bd=0)
    container.pack(padx=80, pady=20, fill=tk.X)
    for status in ["In Stock", "Delivered", "Faulty"]:
        card = tk.Frame(container, bg="white", bd=1, relief=tk.SOLID)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=15, pady=10)
        card.config(highlightthickness=0)
        card.config(bd=4)
        tk.Label(card, text=status, font=("Segoe UI", 22, "bold"), bg="white", fg="#333").pack(pady=(25,10))
        summary_labels[status] = tk.Label(card, text="0", font=("Segoe UI", 48, "bold"), bg="white", fg="#1f2937")
        summary_labels[status].pack(pady=(0,25))

def setup_search_tab(tab):
    tab.configure(bg="#ffffff")
    tk.Label(tab, text="Search STB", font=("Segoe UI", 36, "bold"), bg="#ffffff", fg="#333").pack(pady=40)
    entry = tk.Entry(tab, font=("Segoe UI", 18), width=50, bd=2, relief=tk.SOLID)
    entry.pack(pady=20)
    result = tk.Label(tab, text="", bg="white", font=("Segoe UI", 16), justify=tk.LEFT,
                      relief=tk.SOLID, bd=1, padx=15, pady=12)
    result.pack(pady=20, fill=tk.X, padx=80)
    def search():
        stb = entry.get().strip()
        if not stb:
            messagebox.showerror("Missing", "Enter STB Number")
            return
        db = connect_db()
        if db is None:
            return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT stb_no, status, dealer_code FROM stock WHERE stb_no = %s", (stb,))
            row = cursor.fetchone()
            if row:
                # Reflected dealer_code only as requested
                dealer_code_display = row[2] if row[2] else "N/A"
                result.config(text=f"STB: {row[0]}\nStatus: {normalize_status(row[1])}\nDealer Code: {dealer_code_display}")
            else:
                result.config(text="STB not found.")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Search failed:\n{str(e)}")
        finally:
            cursor.close()
            db.close()
    tk.Button(tab, text="Search", font=("Segoe UI", 18, "bold"), bg="#007acc", fg="white",
              activebackground="#005f99", activeforeground="white", command=search).pack(pady=25, ipadx=25, ipady=12)

def setup_logs_tab(tab):
    tab.configure(bg="#ffffff")
    tk.Label(tab, text="Transaction Logs", font=("Segoe UI", 36, "bold"), bg="#ffffff", fg="#333").pack(pady=30)
    filter_frame = tk.Frame(tab, bg="#ffffff")
    filter_frame.pack(pady=20)
    tk.Label(filter_frame, text="Start Date:", font=("Segoe UI", 14), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    start_entry = DateEntry(filter_frame, font=("Segoe UI", 14), width=15, bd=2, relief=tk.SOLID,
                            background='white', foreground='black', borderwidth=1)
    start_entry.pack(side=tk.LEFT, padx=10)
    tk.Label(filter_frame, text="End Date:", font=("Segoe UI", 14), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    end_entry = DateEntry(filter_frame, font=("Segoe UI", 14), width=15, bd=2, relief=tk.SOLID,
                          background='white', foreground='black', borderwidth=1)
    end_entry.pack(side=tk.LEFT, padx=10)
    search_btn = tk.Button(filter_frame, text="Search Logs", font=("Segoe UI", 14, "bold"),
                           bg="#007acc", fg="white", activebackground="#005f99", activeforeground="white")
    search_btn.pack(side=tk.LEFT, padx=10)
    cols = ("Timestamp", "Action", "STB", "Dealer", "User")
    table = ttk.Treeview(tab, columns=cols, show="headings", height=20)
    for col in cols:
        table.heading(col, text=col)
        table.column(col, anchor=tk.CENTER, minwidth=100, width=170)
    table.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)
    def load_logs():
        for row in table.get_children():
            table.delete(row)
        start = start_entry.get_date()
        end = end_entry.get_date()
        db = connect_db()
        if db is None:
            return
        cursor = db.cursor()
        query = "SELECT timestamp, action, stb_no, dealer, done_by FROM logs"
        try:
            if start and end:
                start_str = start.strftime('%Y-%m-%d')
                end_str = end.strftime('%Y-%m-%d')
                query += " WHERE DATE(timestamp) BETWEEN %s AND %s ORDER BY timestamp DESC"
                cursor.execute(query, (start_str, end_str))
            else:
                cursor.execute(query + " ORDER BY timestamp DESC")
            for row in cursor.fetchall():
                table.insert("", tk.END, values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load logs:\n{str(e)}")
        finally:
            cursor.close()
            db.close()
    def export_logs():
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        wb = Workbook()
        ws = wb.active
        ws.append(cols)
        for row in table.get_children():
            ws.append(table.item(row)['values'])
        wb.save(path)
        messagebox.showinfo("Exported", f"Logs exported to {path}")
    search_btn.config(command=load_logs)
    export_btn = tk.Button(tab, text="Export to Excel", font=("Segoe UI", 14, "bold"),
                           bg="#28a745", fg="white", activebackground="#1e7e34", activeforeground="white",
                           command=export_logs)
    export_btn.pack(pady=15, ipadx=15, ipady=8)

def logout():
    global SESSION_USER
    confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    if confirm:
        SESSION_USER = None
        notebook.pack_forget()
        login_frame.pack(pady=150)
        logout_button.pack_forget()
        entry_user.delete(0, tk.END)
        entry_pass.delete(0, tk.END)

root = tk.Tk()
root.title("METROCAST ARRAY STB Transaction System")
root.geometry("1280x960")
root.configure(bg="#ffffff")

top_frame = tk.Frame(root, bg="#ffffff")
top_frame.pack(fill=tk.X, side=tk.TOP)
logout_button = tk.Button(top_frame, text="Logout", font=("Segoe UI", 12, "bold"),
                          bg="#f44336", fg="white", activebackground="#ba000d",
                          activeforeground="white", command=logout)

login_frame = tk.Frame(root, bg="#ffffff")
login_frame.pack(pady=150)

tk.Label(login_frame, text="Username", font=("Segoe UI", 18, "bold"),
         bg="#ffffff", fg="#6b7280").pack(pady=8)
entry_user = tk.Entry(login_frame, font=("Segoe UI", 16), width=30, bd=2, relief=tk.SOLID)
entry_user.pack(pady=5)
tk.Label(login_frame, text="Password", font=("Segoe UI", 18, "bold"),
         bg="#ffffff", fg="#6b7280").pack(pady=8)
entry_pass = tk.Entry(login_frame, show="*", font=("Segoe UI", 16), width=30, bd=2, relief=tk.SOLID)
entry_pass.pack(pady=5)

def login():
    global SESSION_USER
    user = entry_user.get().strip()
    pwd = entry_pass.get().strip()
    if not user or not pwd:
        messagebox.showerror("Input Error", "Please enter username and password.")
        return
    db = connect_db()
    if db is None:
        return
    cursor = db.cursor()
    hashed_pwd = hash_password(pwd)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user, hashed_pwd))
        if cursor.fetchone():
            SESSION_USER = user
            login_frame.pack_forget()
            logout_button.pack(anchor='ne', padx=20, pady=10)
            notebook.pack(fill="both", expand=True, padx=20, pady=20)
            update_summary()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        db.close()

tk.Button(login_frame, text="Login", font=("Segoe UI", 16, "bold"),
          bg="#000000", fg="white", activebackground="#333333",
          activeforeground="white", command=login).pack(pady=25, ipadx=10, ipady=8)

notebook = ttk.Notebook(root)

tabs = {}
tab_order = ["Search", "Issue", "Return", "Replace", "Faulty", "Summary", "Logs"]
for tab_name in tab_order:
    tabs[tab_name] = tk.Frame(notebook, bg="#ffffff")
    notebook.add(tabs[tab_name], text=tab_name)

create_action_tab(tabs["Issue"], "Issue", require_dealer_code=True)
create_action_tab(tabs["Return"], "Return", require_dealer_code=False)
create_replace_tab(tabs["Replace"])
create_action_tab(tabs["Faulty"], "Faulty", require_dealer_code=False)
setup_summary_tab(tabs["Summary"])
setup_search_tab(tabs["Search"])
setup_logs_tab(tabs["Logs"])

root.mainloop()