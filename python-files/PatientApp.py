import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import os

# ----------- Eye Toggle Icon Widget -----------
class EyeToggle(tk.Label):
    def __init__(self, parent, entry, **kwargs):
        super().__init__(parent, **kwargs)
        self.entry = entry
        self.visible = False
        self.config(text="\U0001F441", cursor="hand2", bg="white", font=("Segoe UI", 10))
        self.bind("<Button-1>", self.toggle)
        self.place(in_=entry, relx=1.0, x=-5, rely=0.5, anchor='e', height=entry.winfo_reqheight())

    def toggle(self, _=None):
        self.visible = not self.visible
        self.entry.config(show='' if self.visible else '*')

# ----------- Database Setup -----------
DB_NAME = "patients.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        slot TEXT DEFAULT 'None'
    )
''')
conn.commit()

# ----------- Admin Auth -----------
CREDENTIALS_FILE = "credentials.txt"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE) as f:
        creds = f.read().split("\n")
        if len(creds) >= 2:
            ADMIN_USERNAME, ADMIN_PASSWORD = creds[:2]

# ----------- Patient Management Class -----------
class PatientManagement:
    slots = [True if not row else False for row in cursor.execute("SELECT slot FROM patients WHERE slot != 'None'").fetchall()] + [True] * (5 - len(cursor.execute("SELECT slot FROM patients WHERE slot != 'None'").fetchall()))

    @staticmethod
    def search_patient(patient_id):
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        return cursor.fetchone()

    @staticmethod
    def add_patient_gui():
        def create_entry(label):
            f = tk.Frame(form, bg=bg)
            f.pack(pady=6, padx=10, anchor="w")
            tk.Label(f, text=label, width=15, anchor="w", bg=bg, font=font).pack(side="left")
            e = tk.Entry(f, width=25, font=font)
            e.pack(side="left")
            return e

        def submit():
            try:
                pid = int(id_entry.get())
                age = int(age_entry.get())
            except ValueError:
                messagebox.showerror("Error", "ID and Age must be numbers.")
                return
            if PatientManagement.search_patient(pid):
                messagebox.showerror("Error", "Patient ID already exists.")
                return
            if not name_entry.get().strip() or not gender_var.get():
                messagebox.showerror("Missing Info", "Please fill in all fields.")
                return

            cursor.execute("INSERT INTO patients (id, name, age, gender) VALUES (?, ?, ?, ?)",
                           (pid, name_entry.get().strip(), age, gender_var.get()))
            conn.commit()
            messagebox.showinfo("Success", "Patient added successfully!")
            form.destroy()

        form = tk.Toplevel()
        form.title("Add Patient")
        form.geometry("400x400")
        bg, font = "#f8f9fa", ("Segoe UI", 10)
        form.config(bg=bg)
        form.grab_set()

        tk.Label(form, text="Patient Registration", font=("Segoe UI", 16, "bold"), bg=bg).pack(pady=20)
        id_entry = create_entry("Patient ID:")
        name_entry = create_entry("Name:")
        age_entry = create_entry("Age:")

        gender_var = tk.StringVar()
        g_frame = tk.Frame(form, bg=bg)
        g_frame.pack(pady=6, padx=10, anchor="w")
        tk.Label(g_frame, text="Gender:", width=15, anchor="w", bg=bg, font=font).pack(side="left")
        for gender in ["Male", "Female"]:
            tk.Radiobutton(g_frame, text=gender, variable=gender_var, value=gender, bg=bg, font=font).pack(side="left", padx=5)

        tk.Button(form, text="Submit", bg="#4CAF50", fg="white", font=("Segoe UI", 10), width=15, command=submit).pack(pady=15)

    @staticmethod
    def view_patient_gui():
        pid = simpledialog.askinteger("Search", "Enter patient ID:")
        p = PatientManagement.search_patient(pid)
        if p:
            messagebox.showinfo("Patient Record", f"Name: {p[1]}\nAge: {p[2]}\nGender: {p[3]}\nSlot: {p[4]}")
        else:
            messagebox.showerror("Not Found", "Patient not found!")

    @staticmethod
    def delete_patient_gui():
        pid = simpledialog.askinteger("Delete Patient", "Enter patient ID:")
        p = PatientManagement.search_patient(pid)
        if p:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete patient ID {pid}?")
            if confirm:
                cursor.execute("DELETE FROM patients WHERE id = ?", (pid,))
                conn.commit()
                messagebox.showinfo("Deleted", "Patient record deleted successfully.")
        else:
            messagebox.showerror("Not Found", "Patient not found!")

    @staticmethod
    def reserve_slot_gui():
        pid = simpledialog.askinteger("Reserve Slot", "Enter patient ID:")
        patient = PatientManagement.search_patient(pid)
        if not patient:
            return messagebox.showerror("Error", "Patient not found!")
        if patient[4] != "None":
            return messagebox.showinfo("Already Reserved", f"Patient already has {patient[4]}.")

        win = tk.Toplevel()
        win.title("Choose a Slot")
        win.geometry("300x320")
        win.config(bg="#f8f9fa")
        win.grab_set()

        tk.Label(win, text="Available Slots", font=("Segoe UI", 12, "bold"), bg="#f8f9fa").pack(pady=10)

        def reserve(slot_index):
            cursor.execute("UPDATE patients SET slot = ? WHERE id = ?", (f"Slot {slot_index + 1}", pid))
            conn.commit()
            messagebox.showinfo("Reserved", f"Slot {slot_index + 1} reserved.")
            win.destroy()

        for i in range(5):
            slot_time = f"{2 + i//2}:00 to {2 + (i+1)//2}:30"
            cursor.execute("SELECT COUNT(*) FROM patients WHERE slot = ?", (f"Slot {i+1}",))
            taken = cursor.fetchone()[0] > 0
            state = "disabled" if taken else "normal"
            b = tk.Button(win, text=f"Slot {i+1} ({slot_time})", width=30, state=state,
                          font=("Segoe UI", 10), bg="white", relief="groove", bd=1,
                          activebackground="#cce5ff", command=lambda i=i: reserve(i))
            b.pack(pady=4)

        tk.Label(win, text=f"Available: {5 - cursor.execute("SELECT COUNT(*) FROM patients WHERE slot != 'None'").fetchone()[0]} / 5", bg="#f8f9fa", font=("Segoe UI", 9)).pack(pady=10)

    @staticmethod
    def cancel_reservation_gui():
        pid = simpledialog.askinteger("Cancel Reservation", "Enter patient ID:")
        patient = PatientManagement.search_patient(pid)
        if not patient:
            return messagebox.showerror("Error", "Patient not found!")
        if patient[4] == "None":
            return messagebox.showinfo("No Reservation", "This patient has no slot reserved.")

        cursor.execute("UPDATE patients SET slot = 'None' WHERE id = ?", (pid,))
        conn.commit()
        messagebox.showinfo("Cancelled", "Reservation cancelled.")

    @staticmethod
    def view_reservations_gui():
        cursor.execute("SELECT id, slot FROM patients WHERE slot != 'None'")
        result = "\n".join([f"Patient ID {r[0]} reserved {r[1]}" for r in cursor.fetchall()])
        messagebox.showinfo("Reservations", result or "No reservations today.")

# ----------- Login UI -----------
def show_login():
    global ADMIN_USERNAME, ADMIN_PASSWORD

    login = tk.Tk()
    login.title("Login")
    login.geometry("400x320")
    login.config(bg="#e9f1f7")

    font_header = ("Segoe UI", 16, "bold")
    font_normal = ("Segoe UI", 10)

    tk.Label(login, text="Admin Login", font=font_header, bg="#e9f1f7").pack(pady=10)
    user_entry = tk.Entry(login, font=font_normal)
    pass_entry = tk.Entry(login, show="*", font=font_normal)

    for label, entry in [("Username:", user_entry), ("Password:", pass_entry)]:
        tk.Label(login, text=label, bg="#e9f1f7", font=font_normal).pack()
        entry.pack(ipady=3, ipadx=3, pady=2)
    EyeToggle(login, pass_entry)

    def change_password():
        cp = tk.Toplevel()
        cp.title("Change Password")
        cp.geometry("350x250")
        cp.config(bg="#f8f9fa")
        cp.grab_set()

        old = tk.Entry(cp, show="*", font=font_normal)
        new_user = tk.Entry(cp, font=font_normal)
        new_pass = tk.Entry(cp, show="*", font=font_normal)

        for text, widget in [("Old Password:", old), ("New Username (optional):", new_user), ("New Password:", new_pass)]:
            tk.Label(cp, text=text, bg="#f8f9fa", font=font_normal).pack(pady=5)
            widget.pack(ipady=2, ipadx=2)
            if 'Password' in text:
                EyeToggle(cp, widget)

        def update():
            nonlocal old, new_user, new_pass
            global ADMIN_USERNAME, ADMIN_PASSWORD
            if old.get() != ADMIN_PASSWORD:
                messagebox.showerror("Error", "Incorrect old password", parent=cp)
                return
            if new_pass.get():
                ADMIN_PASSWORD = new_pass.get()
            if new_user.get():
                ADMIN_USERNAME = new_user.get()
            with open(CREDENTIALS_FILE, 'w') as f:
                f.write(f"{ADMIN_USERNAME}\n{ADMIN_PASSWORD}")
            messagebox.showinfo("Success", "Credentials updated", parent=cp)
            cp.destroy()

        tk.Button(cp, text="Update", bg="#4CAF50", fg="white", font=font_normal, command=update).pack(pady=10)

    cp_label = tk.Label(login, text="Change Password", fg="blue", bg="#e9f1f7", cursor="hand2", font=("Segoe UI", 9, "underline"))
    cp_label.pack()
    cp_label.bind("<Button-1>", lambda _: change_password())

    def authenticate():
        if user_entry.get() == ADMIN_USERNAME and pass_entry.get() == ADMIN_PASSWORD:
            login.destroy()
            open_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    tk.Button(login, text="Login", command=authenticate, bg="#4CAF50", fg="white", font=font_normal, width=20).pack(pady=10)
    login.mainloop()

# ----------- Main App -----------
def open_main_app():
    app = tk.Tk()
    app.title("Patient Management System")
    app.geometry("500x600")
    app.config(bg="#eaf2fb")

    tk.Label(app, text="Patient Management System", font=("Segoe UI", 20, "bold"), bg="#eaf2fb", fg="#003366").pack(pady=20)
    btn_cfg = {
        "width": 30, "height": 2, "font": ("Segoe UI", 10),
        "bg": "#ffffff", "fg": "#003366", "activebackground": "#cce0ff",
        "bd": 0, "relief": "ridge"
    }
    for text, cmd in [
        ("Add Patient", PatientManagement.add_patient_gui),
        ("View Patient Record", PatientManagement.view_patient_gui),
        ("Delete Patient Record", PatientManagement.delete_patient_gui),
        ("Reserve Slot", PatientManagement.reserve_slot_gui),
        ("Cancel Reservation", PatientManagement.cancel_reservation_gui),
        ("View Today's Reservations", PatientManagement.view_reservations_gui),
        ("Logout", lambda: [app.destroy(), show_login()]),
        ("Exit", app.destroy)
    ]:
        b = tk.Button(app, text=text, command=cmd, **btn_cfg)
        b.pack(pady=8)
        b.bind("<Enter>", lambda e, b=b: b.config(bg="#dceeff"))
        b.bind("<Leave>", lambda e, b=b: b.config(bg="#ffffff"))

    app.mainloop()

# Start the app
show_login()
