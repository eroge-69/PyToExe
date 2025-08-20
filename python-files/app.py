
import os
import sys
import bcrypt
import threading
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector as mysql
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "crmdb"),
    user=os.getenv("DB_USER", "crmuser"),
    password=os.getenv("DB_PASS", ""),
    autocommit=True
)

def get_conn():
    return mysql.connect(**DB_CFG)

def hash_pw(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

def check_pw(pw: str, pw_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), pw_hash)
    except Exception:
        return False

def create_admin(username, password):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            print("User already exists")
            return
        cur.execute("INSERT INTO users(username, password_hash) VALUES(%s,%s)",
                    (username, hash_pw(password)))
        conn.commit()
        print("Admin user created.")
    except Error as e:
        print("DB error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

class LoginWindow(Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Login - Simple CRM")
        self.resizable(False, False)
        self.on_success = on_success

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Username").grid(row=0, column=0, sticky="w", pady=4)
        self.username = ttk.Entry(frm, width=26)
        self.username.grid(row=0, column=1, pady=4)

        ttk.Label(frm, text="Password").grid(row=1, column=0, sticky="w", pady=4)
        self.password = ttk.Entry(frm, width=26, show="*")
        self.password.grid(row=1, column=1, pady=4)

        btn = ttk.Button(frm, text="Login", command=self.login)
        btn.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")

        self.bind("<Return>", lambda e: self.login())
        self.username.focus()

    def login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showwarning("Required", "Enter username and password")
            return
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT user_id, password_hash FROM users WHERE username=%s", (u,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Login failed", "Invalid username or password")
                return
            uid, pw_hash = row[0], row[1]
            if isinstance(pw_hash, str):
                pw_hash = pw_hash.encode("utf-8")
            if check_pw(p, pw_hash):
                self.destroy()
                self.on_success(uid, u)
            else:
                messagebox.showerror("Login failed", "Invalid username or password")
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass

class FollowupPopup(Toplevel):
    def __init__(self, master, due_items):
        super().__init__(master)
        self.title("Follow-ups Due")
        self.geometry("620x280")
        self.resizable(True, True)
        cols = ("lead_id", "name", "status", "follow_up_at", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_"," ").title())
            self.tree.column(c, width=120)
        self.tree.pack(fill=BOTH, expand=True, padx=8, pady=8)
        for item in due_items:
            self.tree.insert("", END, values=item)

class CRMApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple CRM - Tkinter + MySQL")
        self.geometry("980x640")
        self.current_user_id = None
        self.current_username = None

        style = ttk.Style(self)
        # Use default theme; can be customized

        # Menu
        menubar = Menu(self)
        account_menu = Menu(menubar, tearoff=0)
        account_menu.add_command(label="Logout", command=self.logout)
        account_menu.add_separator()
        account_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Account", menu=account_menu)
        self.config(menu=menubar)

        # Top frames
        top = ttk.Frame(self, padding=8)
        top.pack(side=TOP, fill=X)

        self.lbl_user = ttk.Label(top, text="Not logged in")
        self.lbl_user.pack(side=LEFT)

        self.btn_add = ttk.Button(top, text="Add Lead", command=self.open_add_form)
        self.btn_add.pack(side=RIGHT, padx=4)

        self.btn_followups = ttk.Button(top, text="Show Follow-ups", command=self.show_followups_popup)
        self.btn_followups.pack(side=RIGHT, padx=4)

        # Dashboard tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=BOTH, expand=True, padx=8, pady=8)

        self.tab_dashboard = ttk.Frame(self.tabs)
        self.tab_allleads = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_dashboard, text="Dashboard")
        self.tabs.add(self.tab_allleads, text="All Leads")

        # Dashboard - Hot leads
        self.hot_tree = ttk.Treeview(self.tab_dashboard, columns=("lead_id","name","phone","follow_up_at","status"), show="headings")
        for c in ("lead_id","name","phone","follow_up_at","status"):
            self.hot_tree.heading(c, text=c.replace("_"," ").title())
            self.hot_tree.column(c, width=150 if c!="lead_id" else 80)
        self.hot_tree.pack(fill=BOTH, expand=True, padx=8, pady=8)

        # All leads table
        self.all_tree = ttk.Treeview(self.tab_allleads, columns=("lead_id","name","phone","address","status","follow_up_at"), show="headings")
        for c in ("lead_id","name","phone","address","status","follow_up_at"):
            self.all_tree.heading(c, text=c.replace("_"," ").title())
            self.all_tree.column(c, width=150 if c!="lead_id" else 80)
        self.all_tree.pack(fill=BOTH, expand=True, padx=8, pady=8)

        # Context menu for edit/delete
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Edit Lead", command=self.edit_selected)
        self.menu.add_command(label="Delete Lead", command=self.delete_selected)
        self.all_tree.bind("<Button-3>", self.popup_menu)

        # Kick off login
        self.after(200, self.show_login)

        # Start background checker
        self.poll_followups()

    # --- UI callbacks ---
    def popup_menu(self, event):
        iid = self.all_tree.identify_row(event.y)
        if iid:
            self.all_tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def show_login(self):
        def on_success(uid, uname):
            self.current_user_id = uid
            self.current_username = uname
            self.lbl_user.config(text=f"Logged in as: {uname}")
            self.refresh_tables()

        LoginWindow(self, on_success)

    def logout(self):
        self.current_user_id = None
        self.current_username = None
        self.lbl_user.config(text="Not logged in")
        self.hot_tree.delete(*self.hot_tree.get_children())
        self.all_tree.delete(*self.all_tree.get_children())
        self.show_login()

    def refresh_tables(self):
        # Hot leads
        for t in (self.hot_tree, self.all_tree):
            t.delete(*t.get_children())

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT lead_id, name, phone, 
                       DATE_FORMAT(follow_up_at, '%Y-%m-%d %H:%i'),
                       status
                FROM leads WHERE status='Hot'
                ORDER BY COALESCE(follow_up_at, '2999-12-31') ASC, created_at DESC
            """)
            for row in cur.fetchall():
                self.hot_tree.insert("", END, values=row)

            cur.execute("""
                SELECT lead_id, name, phone, address, status, 
                       DATE_FORMAT(follow_up_at, '%Y-%m-%d %H:%i')
                FROM leads
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
            """)
            for row in cur.fetchall():
                self.all_tree.insert("", END, values=row)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass

    def open_add_form(self, existing=None):
        AddEditLead(self, self.current_user_id, on_save=self.refresh_tables, existing=existing)

    def edit_selected(self):
        sel = self.all_tree.selection()
        if not sel:
            return
        lead_id = self.all_tree.item(sel[0])["values"][0]
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM leads WHERE lead_id=%s", (lead_id,))
            row = cur.fetchone()
        except Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass
        if row:
            self.open_add_form(existing=row)

    def delete_selected(self):
        sel = self.all_tree.selection()
        if not sel:
            return
        lead_id = self.all_tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete lead #{lead_id}?"):
            return
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM leads WHERE lead_id=%s", (lead_id,))
            conn.commit()
            self.refresh_tables()
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    # --- Follow-up logic ---
    def poll_followups(self):
        try:
            now = datetime.now()
            horizon = now + timedelta(minutes=15)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT lead_id, name, status, 
                       DATE_FORMAT(follow_up_at, '%%Y-%%m-%%d %%H:%%i') as fu, phone
                FROM leads
                WHERE follow_up_at IS NOT NULL
                  AND follow_up_at BETWEEN %s AND %s
                ORDER BY follow_up_at ASC
            """, (now, horizon))
            rows = cur.fetchall()
            if rows:
                FollowupPopup(self, rows)
        except Error:
            pass
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass
        # Check every 60s
        self.after(60000, self.poll_followups)

    def show_followups_popup(self):
        try:
            now = datetime.now()
            horizon = now + timedelta(days=7)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT lead_id, name, status, 
                       DATE_FORMAT(follow_up_at, '%%Y-%%m-%%d %%H:%%i') as fu, phone
                FROM leads
                WHERE follow_up_at IS NOT NULL
                  AND follow_up_at <= %s
                ORDER BY follow_up_at ASC
            """, (horizon,))
            rows = cur.fetchall()
            FollowupPopup(self, rows)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass

class AddEditLead(Toplevel):
    def __init__(self, master, user_id, on_save, existing=None):
        super().__init__(master)
        self.title("Add Lead" if existing is None else f"Edit Lead #{existing['lead_id']}")
        self.resizable(False, False)
        self.user_id = user_id
        self.on_save = on_save
        self.existing = existing

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # Fields
        ttk.Label(frm, text="Name*").grid(row=0, column=0, sticky="w", pady=4)
        self.e_name = ttk.Entry(frm, width=40)
        self.e_name.grid(row=0, column=1, pady=4, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Phone").grid(row=1, column=0, sticky="w", pady=4)
        self.e_phone = ttk.Entry(frm, width=40)
        self.e_phone.grid(row=1, column=1, pady=4, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Address").grid(row=2, column=0, sticky="w", pady=4)
        self.e_address = ttk.Entry(frm, width=40)
        self.e_address.grid(row=2, column=1, pady=4, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Description").grid(row=3, column=0, sticky="nw", pady=4)
        self.t_desc = Text(frm, width=40, height=4)
        self.t_desc.grid(row=3, column=1, pady=4, columnspan=2, sticky="ew")

        ttk.Label(frm, text="Status").grid(row=4, column=0, sticky="w", pady=4)
        self.cb_status = ttk.Combobox(frm, values=["Hot", "Warm", "Cold"], state="readonly", width=18)
        self.cb_status.current(1)
        self.cb_status.grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(frm, text="Follow-up Date").grid(row=5, column=0, sticky="w", pady=4)
        self.d_follow = DateEntry(frm, width=16, date_pattern="yyyy-mm-dd")
        self.d_follow.grid(row=5, column=1, sticky="w", pady=4)

        ttk.Label(frm, text="Time (HH:MM)").grid(row=5, column=2, sticky="w", pady=4)
        self.e_time = ttk.Entry(frm, width=10)
        self.e_time.insert(0, "10:00")

        self.e_time.grid(row=5, column=3, sticky="w", pady=4)

        btn = ttk.Button(frm, text="Save", command=self.save)
        btn.grid(row=6, column=0, columnspan=4, pady=10, sticky="ew")

        if existing:
            self.populate(existing)

    def populate(self, row):
        self.e_name.insert(0, row["name"] or "")
        self.e_phone.insert(0, row["phone"] or "")
        self.e_address.insert(0, row["address"] or "")
        self.t_desc.insert("1.0", row["description"] or "")
        self.cb_status.set(row["status"] or "Warm")
        if row["follow_up_at"]:
            try:
                dt = row["follow_up_at"]
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                self.d_follow.set_date(dt.date())
                self.e_time.delete(0, END)
                self.e_time.insert(0, dt.strftime("%H:%M"))
            except Exception:
                pass

    def save(self):
        name = self.e_name.get().strip()
        phone = self.e_phone.get().strip()
        address = self.e_address.get().strip()
        desc = self.t_desc.get("1.0", END).strip()
        status = self.cb_status.get()
        date_str = self.d_follow.get_date().strftime("%Y-%m-%d")
        time_str = self.e_time.get().strip() or "10:00"

        if not name:
            messagebox.showwarning("Validation", "Name is required")
            return
        try:
            follow_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showwarning("Validation", "Time must be HH:MM (24h)")
            return

        try:
            conn = get_conn()
            cur = conn.cursor()
            if self.existing:
                cur.execute("""
                    UPDATE leads SET name=%s, phone=%s, address=%s, description=%s,
                        status=%s, follow_up_at=%s
                    WHERE lead_id=%s
                """, (name, phone, address, desc, status, follow_dt, self.existing["lead_id"]))
            else:
                cur.execute("""
                    INSERT INTO leads(name, phone, address, description, status, follow_up_at, created_by)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                """, (name, phone, address, desc, status, follow_dt, self.user_id))
            conn.commit()
            self.destroy()
            self.on_save()
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass

def main():
    # Admin creation mode
    if len(sys.argv) == 4 and sys.argv[1] == "--create-admin":
        create_admin(sys.argv[2], sys.argv[3])
        return

    app = CRMApp()
    app.mainloop()

if __name__ == "__main__":
    main()
