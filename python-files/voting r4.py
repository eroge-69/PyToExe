import tkinter as tk
from tkinter import messagebox
import sqlite3
import random

# --- Database Setup ---
voter_conn = sqlite3.connect("voters.db")
voter_cursor = voter_conn.cursor()
voter_cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters (
        voter_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        fingerprint_template TEXT UNIQUE NOT NULL
    )
""")
voter_conn.commit()

# --- Helper Functions ---
def generate_voter_id():
    return "VOTER" + str(random.randint(1000, 9999))

def scan_fingerprint():
    # Simulate fingerprint scan
    return "FP" + str(random.randint(10000, 99999))

# --- Admin Panel ---
def open_admin_menu():
    admin_window = tk.Toplevel()
    admin_window.title("Admin Panel")
    admin_window.geometry("400x300")

    tk.Label(admin_window, text="Register New Voter", font=("Arial", 14)).pack(pady=10)

    tk.Label(admin_window, text="Voter Name:").pack()
    name_entry = tk.Entry(admin_window)
    name_entry.pack(pady=5)

    def save_voter():
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter the voter's name.")
            return
        vid = generate_voter_id()
        fp = scan_fingerprint()
        try:
            voter_cursor.execute(
                "INSERT INTO voters (voter_id, name, fingerprint_template) VALUES (?, ?, ?)",
                (vid, name, fp)
            )
            voter_conn.commit()
            messagebox.showinfo(
                "Success",
                f"✅ Voter Registered!\n\nName: {name}\nVoter ID: {vid}\nFingerprint: {fp}"
            )
            name_entry.delete(0, tk.END)  # Clear for next entry
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "⚠️ Fingerprint already exists.")

    def view_results():
        voter_cursor.execute("SELECT * FROM voters")
        records = voter_cursor.fetchall()
        result_text = "\n".join([f"{r[0]} | {r[1]} | {r[2]}" for r in records])
        messagebox.showinfo("Registered Voters", result_text if result_text else "No voters registered yet.")

    def logout():
        admin_window.destroy()

    tk.Button(admin_window, text="Save Voter", command=save_voter).pack(pady=10)
    tk.Button(admin_window, text="View Voter List", command=view_results).pack(pady=5)
    tk.Button(admin_window, text="Logout", command=logout).pack(pady=5)

# --- Login Window ---
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "admin123":
        root.destroy()
        open_admin_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

root = tk.Tk()
root.title("Fingerprint Voting System")
root.geometry("300x200")

tk.Label(root, text="Admin Login", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack(pady=10)

root.mainloop()
