# main.py
# Complete Real Estate + Accounts Desktop App
# Requires: Python 3.x, Tkinter (bundled)
# Optional: reportlab for PDF generation (pip install reportlab)

import sqlite3, os, tempfile, webbrowser
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox

DB = "real_estate.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )""")
    c.execute("INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, 'admin', '2233')")
    conn.commit()
    conn.close()

init_db()

root = Tk(); root.withdraw()

def show_login():
    login = Toplevel()
    login.title("Admin Login")
    login.geometry("360x240")
    login.resizable(False, False)
    Label(login, text="Real Estate System — Admin Login", font=('Arial',12,'bold')).pack(pady=10)
    Label(login, text="Username").pack()
    user_ent = Entry(login); user_ent.pack()
    Label(login, text="Password").pack()
    pass_ent = Entry(login, show='*'); pass_ent.pack()
    def try_login():
        u = user_ent.get().strip(); p = pass_ent.get().strip()
        c = sqlite3.connect(DB).cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (u,p))
        r = c.fetchall()
        c.connection.close()
        if r:
            login.destroy(); main_window()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password")
    Button(login, text="Login", command=try_login).pack(pady=10)
    Label(login, text="Default: admin / 2233", fg='gray').pack()
    login.transient(root); login.grab_set(); root.wait_window(login)

def main_window():
    root.deiconify()
    root.title("Real Estate & Accounts System")
    root.geometry("1200x760")
    Label(root, text="Welcome to Real Estate Management + Accounts System", font=('Arial',16,'bold')).pack(pady=20)

show_login()
root.mainloop()
