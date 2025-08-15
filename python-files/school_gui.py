import tkinter as tk
from tkinter import messagebox
import os

students = {}  # Dictionary to store student names and grades
file_name = "students.txt"

# ---------- File Functions ----------
def load_students():
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            for line in f:
                name, grade = line.strip().split(",")
                students[name] = grade

def save_students():
    with open(file_name, "w") as f:
        for name, grade in students.items():
            f.write(f"{name},{grade}\n")

# ---------- Button Functions ----------
def add_student():
    name = name_entry.get().strip()
    grade = grade_entry.get().strip()
    if name and grade:
        students[name] = grade
        save_students()
        messagebox.showinfo("Success", f"{name} added with grade {grade}.")
        name_entry.delete(0, tk.END)
        grade_entry.delete(0, tk.END)
        refresh_list()
    else:
        messagebox.showwarning("Input Error", "Please enter both name and grade.")

def update_student():
    name = name_entry.get().strip()
    grade = grade_entry.get().strip()
    if name in students:
        students[name] = grade
        save_students()
        messagebox.showinfo("Success", f"{name}'s grade updated to {grade}.")
        refresh_list()
    else:
        messagebox.showerror("Error", "Student not found.")

def delete_student():
    name = name_entry.get().strip()
    if name in students:
        del students[name]
        save_students()
        messagebox.showinfo("Deleted", f"{name} has been removed.")
        refresh_list()
    else:
        messagebox.showerror("Error", "Student not found.")

def refresh_list():
    listbox.delete(0, tk.END)
    for name, grade in students.items():
        listbox.insert(tk.END, f"{name} - Grade: {grade}")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("School Management System")
root.geometry("400x400")
root.resizable(False, False)

# Labels and Entries
tk.Label(root, text="Student Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Grade:").pack()
grade_entry = tk.Entry(root)
grade_entry.pack()

# Buttons
tk.Button(root, text="Add Student", command=add_student).pack(pady=5)
tk.Button(root, text="Update Grade", command=update_student).pack(pady=5)
tk.Button(root, text="Delete Student", command=delete_student).pack(pady=5)

# Listbox
tk.Label(root, text="Student List:").pack()
listbox = tk.Listbox(root, width=40)
listbox.pack(pady=10)

# Load existing students from file
load_students()
refresh_list()

root.mainloop()
