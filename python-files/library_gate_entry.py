import os
import csv
import time
import pandas as pd
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from threading import Timer

# ================================
# SPLASH SCREEN
# ================================

class SplashScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("600x350")
        self.overrideredirect(True)
        self.configure(bg="#1a73e8")

        self.canvas = tk.Canvas(self, width=600, height=350, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Gradient background
        for i in range(0, 350):
            r = 26
            g = 115 + int((255 - 115) * (i / 350))
            b = 232
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 600, i, fill=color)

        self.canvas.create_text(
            300, 130, text="Welcome to", font=("Segoe UI", 20, "bold"), fill="white"
        )
        self.canvas.create_text(
            300, 180,
            text="M.M. Engineering College\nCentral Library",
            font=("Segoe UI", 22, "bold"), fill="white", justify="center"
        )
        self.canvas.create_text(
            300, 310,
            text="Developed by: Gulshan Kumar Pahwa\nLibrarian (Central Library, MMEC)",
            font=("Segoe UI", 10, "bold"), fill="white", justify="center"
        )

        # Automatically close splash after 5 seconds
        self.after(5000, self.destroy)


# ================================
# MAIN APPLICATION
# ================================

class LibraryGateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Gate Entry System")
        self.geometry("850x550")
        ctk.set_appearance_mode("light")

        self.master_file = "students_master.csv"
        self.report_folder = "reports"
        os.makedirs(self.report_folder, exist_ok=True)

        self.students = self.load_students()

        # GUI Layout
        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.label = ctk.CTkLabel(self.frame,
                                  text="Library Gate Entry System",
                                  font=("Segoe UI", 24, "bold"))
        self.label.pack(pady=20)

        # Entry field
        self.roll_entry = ctk.CTkEntry(self.frame,
                                       placeholder_text="Scan or Enter Roll Number",
                                       width=300,
                                       font=("Segoe UI", 16))
        self.roll_entry.pack(pady=10)
        self.roll_entry.bind("<Return>", lambda e: self.process_roll())

        # Buttons
        btn_frame = ctk.CTkFrame(self.frame)
        btn_frame.pack(pady=15)

        self.submit_btn = ctk.CTkButton(btn_frame, text="Submit", width=120, command=self.process_roll)
        self.submit_btn.grid(row=0, column=0, padx=10)

        self.add_btn = ctk.CTkButton(btn_frame, text="Add Student", width=120, command=self.add_student_window)
        self.add_btn.grid(row=0, column=1, padx=10)

        self.report_btn = ctk.CTkButton(btn_frame, text="View Report", width=120, command=self.show_report)
        self.report_btn.grid(row=0, column=2, padx=10)

        self.exit_btn = ctk.CTkButton(btn_frame, text="Exit", width=120, command=self.destroy)
        self.exit_btn.grid(row=0, column=3, padx=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14))
        self.status_label.pack(pady=10)

        # Table (Treeview)
        self.table = ttk.Treeview(self.frame, columns=("RollNo", "Name", "Course", "Entry", "Exit"),
                                  show="headings", height=10)
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=150)
        self.table.pack(pady=10)

    # ================================
    # CORE FUNCTIONS
    # ================================

    def load_students(self):
        if not os.path.exists(self.master_file):
            df = pd.DataFrame(columns=["RollNo", "Name", "Course"])
            df.to_csv(self.master_file, index=False)
            return df
        return pd.read_csv(self.master_file)

    def process_roll(self):
        roll = str(self.roll_entry.get()).strip()
        if not roll:
            messagebox.showwarning("Input Error", "Please enter Roll Number!")
            return

        df = self.students
        student = df[df["RollNo"].astype(str) == roll]

        if student.empty:
            messagebox.showerror("Not Found", f"Roll Number {roll} not found in master list.")
            return

        name = student.iloc[0]["Name"]
        course = student.iloc[0]["Course"]
        now = datetime.now()
        today_file = os.path.join(self.report_folder, f"{now.date()}.csv")

        entry = None
        data = []
        if os.path.exists(today_file):
            with open(today_file, newline='') as f:
                data = list(csv.DictReader(f))
                for row in data:
                    if row["RollNo"] == roll and not row["ExitTime"]:
                        entry = row
                        break

        if entry:
            entry["ExitTime"] = now.strftime("%H:%M:%S")
            for row in data:
                if row["RollNo"] == roll and not row["ExitTime"]:
                    row["ExitTime"] = entry["ExitTime"]
            with open(today_file, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["RollNo", "Name", "Course", "EntryTime", "ExitTime"])
                writer.writeheader()
                writer.writerows(data)
            msg = f"Exit marked for {name} ({course})"
        else:
            with open(today_file, "a", newline='') as f:
                writer = csv.writer(f)
                if os.stat(today_file).st_size == 0:
                    writer.writerow(["RollNo", "Name", "Course", "EntryTime", "ExitTime"])
                writer.writerow([roll, name, course, now.strftime("%H:%M:%S"), ""])
            msg = f"Entry marked for {name} ({course})"

        self.status_label.configure(text=msg)
        self.refresh_table(today_file)
        self.roll_entry.delete(0, tk.END)

    def add_student_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Add New Student")
        win.geometry("400x300")

        fields = {}
        for i, field in enumerate(["RollNo", "Name", "Course"]):
            ctk.CTkLabel(win, text=field, font=("Segoe UI", 14)).pack(pady=5)
            ent = ctk.CTkEntry(win, width=250)
            ent.pack()
            fields[field] = ent

        def save_student():
            roll = fields["RollNo"].get().strip()
            name = fields["Name"].get().strip()
            course = fields["Course"].get().strip()

            if not roll or not name or not course:
                messagebox.showwarning("Input Error", "All fields required.")
                return

            self.students.loc[len(self.students)] = [roll, name, course]
            self.students.to_csv(self.master_file, index=False)
            messagebox.showinfo("Saved", "Student added successfully.")
            win.destroy()

        ctk.CTkButton(win, text="Save", command=save_student).pack(pady=10)

    def refresh_table(self, today_file):
        for row in self.table.get_children():
            self.table.delete(row)
        if os.path.exists(today_file):
            df = pd.read_csv(today_file)
            for _, row in df.iterrows():
                self.table.insert("", "end", values=row.tolist())

    def show_report(self):
        os.startfile(self.report_folder)


# ================================
# RUN APP
# ================================

if __name__ == "__main__":
    root = LibraryGateApp()
    splash = SplashScreen(root)
    root.wait_window(splash)
    root.mainloop()
