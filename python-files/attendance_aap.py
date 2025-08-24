Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import tkinter as tk
... from tkinter import filedialog, messagebox
... from tkinter import PhotoImage
... from PIL import Image, ImageTk
... import sqlite3
... import os
... 
... # Database Setup
... conn = sqlite3.connect('attendance.db')
... c = conn.cursor()
... c.execute('''
... CREATE TABLE IF NOT EXISTS employees (
...     id INTEGER PRIMARY KEY AUTOINCREMENT,
...     name TEXT,
...     mobile TEXT,
...     aadhaar TEXT,
...     location TEXT,
...     photo_path TEXT
... )
... ''')
... conn.commit()
... 
... # GUI Window
... root = tk.Tk()
... root.title('Employee Attendance Software')
... 
... # Functions
... def select_photo():
...     file_path = filedialog.askopenfilename(
...         filetypes=[("Image files", "*.jpg *.jpeg *.png")])
...     if file_path:
...         photo_path_var.set(file_path)
...         photo_label.config(text=os.path.basename(file_path))
... 
... def save_employee():
...     name = name_entry.get()
...     mobile = mobile_entry.get()
    aadhaar = aadhaar_entry.get()
    location = location_entry.get()
    photo_path = photo_path_var.get()

    if not (name and mobile and aadhaar and location and photo_path):
        messagebox.showerror("Error", "Saare fields bharein!")
        return

    c.execute("INSERT INTO employees (name, mobile, aadhaar, location, photo_path) VALUES (?, ?, ?, ?, ?)",
              (name, mobile, aadhaar, location, photo_path))
    conn.commit()
    messagebox.showinfo("Success", "Employee data save ho gaya.")
    clear_form()

def clear_form():
    name_entry.delete(0, tk.END)
    mobile_entry.delete(0, tk.END)
    aadhaar_entry.delete(0, tk.END)
    location_entry.delete(0, tk.END)
    photo_path_var.set('')
    photo_label.config(text='No photo selected')


# GUI Layout
tk.Label(root, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Mobile No:").grid(row=1, column=0)
mobile_entry = tk.Entry(root)
mobile_entry.grid(row=1, column=1)

tk.Label(root, text="Aadhaar No:").grid(row=2, column=0)
aadhaar_entry = tk.Entry(root)
aadhaar_entry.grid(row=2, column=1)

tk.Label(root, text="Location:").grid(row=3, column=0)
location_entry = tk.Entry(root)
location_entry.grid(row=3, column=1)

photo_path_var = tk.StringVar()
tk.Button(root, text="Select Photo", command=select_photo).grid(row=4, column=0)
photo_label = tk.Label(root, text="No photo selected")
photo_label.grid(row=4, column=1)

tk.Button(root, text="Save Employee", command=save_employee).grid(row=5, column=0, columnspan=2)

root.mainloop()import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import sqlite3
import os

# Database Setup
conn = sqlite3.connect('attendance.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    aadhaar TEXT,
    location TEXT,
    photo_path TEXT
)
''')
conn.commit()

# GUI Window
root = tk.Tk()
root.title('Employee Attendance Software')

# Functions
def select_photo():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        photo_path_var.set(file_path)
        photo_label.config(text=os.path.basename(file_path))

def save_employee():
    name = name_entry.get()
    mobile = mobile_entry.get()
    aadhaar = aadhaar_entry.get()
    location = location_entry.get()
    photo_path = photo_path_var.get()

    if not (name and mobile and aadhaar and location and photo_path):
        messagebox.showerror("Error", "Saare fields bharein!")
        return

    c.execute("INSERT INTO employees (name, mobile, aadhaar, location, photo_path) VALUES (?, ?, ?, ?, ?)",
              (name, mobile, aadhaar, location, photo_path))
    conn.commit()
    messagebox.showinfo("Success", "Employee data save ho gaya.")
    clear_form()

def clear_form():
    name_entry.delete(0, tk.END)
    mobile_entry.delete(0, tk.END)
    aadhaar_entry.delete(0, tk.END)
    location_entry.delete(0, tk.END)
    photo_path_var.set('')
    photo_label.config(text='No photo selected')


# GUI Layout
tk.Label(root, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Mobile No:").grid(row=1, column=0)
mobile_entry = tk.Entry(root)
mobile_entry.grid(row=1, column=1)

tk.Label(root, text="Aadhaar No:").grid(row=2, column=0)
aadhaar_entry = tk.Entry(root)
aadhaar_entry.grid(row=2, column=1)

tk.Label(root, text="Location:").grid(row=3, column=0)
location_entry = tk.Entry(root)
location_entry.grid(row=3, column=1)

photo_path_var = tk.StringVar()
tk.Button(root, text="Select Photo", command=select_photo).grid(row=4, column=0)
photo_label = tk.Label(root, text="No photo selected")
photo_label.grid(row=4, column=1)

tk.Button(root, text="Save Employee", command=save_employee).grid(row=5, column=0, columnspan=2)

