import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3

# Create database
conn = sqlite3.connect("college.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll TEXT,
    course TEXT,
    email TEXT
)
""")
# Add default login
cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ('admin', 'admin123'))
conn.commit()
conn.close()

# Login Window
class LoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("College Management System - Login")
        self.master.geometry("400x500")
        self.master.config(bg="#dceefc")

        logo = Image.open("logo.png")
        logo = logo.resize((100, 100))
        self.logo_img = ImageTk.PhotoImage(logo)
        tk.Label(master, image=self.logo_img, bg="#dceefc").pack(pady=10)

        tk.Label(master, text="Username", bg="#dceefc", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        tk.Label(master, text="Password", bg="#dceefc", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(master, show='*')
        self.password_entry.pack()

        tk.Button(master, text="Login", command=self.login, bg="skyblue").pack(pady=20)

    def login(self):
        uname = self.username_entry.get()
        pwd = self.password_entry.get()

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.master.destroy()
            MainApp()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

# Main Application Window
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("College Management System")
        self.root.geometry("600x500")
        self.root.config(bg="#e0ffe0")

        tk.Label(self.root, text="Student Registration", font=("Arial", 16, "bold"), bg="#e0ffe0").pack(pady=10)

        self.entries = {}
        for label in ["Name", "Roll No", "Course", "Email"]:
            tk.Label(self.root, text=label, font=("Arial", 12), bg="#e0ffe0").pack()
            entry = tk.Entry(self.root, width=40)
            entry.pack(pady=5)
            self.entries[label.lower()] = entry

        tk.Button(self.root, text="Save Student", command=self.save_student, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit, bg="red", fg="white").pack()

        self.root.mainloop()

    def save_student(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if all(data.values()):
            conn = sqlite3.connect("college.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, roll, course, email) VALUES (?, ?, ?, ?)",
                           (data['name'], data['roll no'], data['course'], data['email']))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Student data saved!")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
