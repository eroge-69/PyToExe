import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess

# ------------------- Database Setup -------------------
def init_db():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            father_name TEXT,
            task TEXT,
            date TEXT,
            fee TEXT,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ------------------- Save Client Data -------------------
def save_data():
    # Validate required fields
    if not name_entry.get().strip() or not father_name_entry.get().strip() or not task_entry.get().strip():
        messagebox.showerror("Error", "د مشتری نوم، د پلار نوم، او د کار نوعیت باید ډک شي.")
        return

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clients (name, father_name, task, date, fee, file_path) VALUES (?, ?, ?, ?, ?, ?)",
        (
            name_entry.get(),
            father_name_entry.get(),
            task_entry.get(),
            date_entry.get(),
            fee_entry.get(),
            file_path_var.get()
        )
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Save", "معلومات خوندي شول!")
    clear_form()

# ------------------- Search Client -------------------
def search_data():
    query = search_entry.get()
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM clients 
        WHERE name LIKE ? OR father_name LIKE ? OR task LIKE ?
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    result = cursor.fetchone()
    conn.close()

    if result:
        name_entry.delete(0, tk.END)
        name_entry.insert(0, result[1])
        father_name_entry.delete(0, tk.END)
        father_name_entry.insert(0, result[2])
        task_entry.delete(0, tk.END)
        task_entry.insert(0, result[3])
        date_entry.delete(0, tk.END)
        date_entry.insert(0, result[4])
        fee_entry.delete(0, tk.END)
        fee_entry.insert(0, result[5])
        file_path_var.set(result[6])
    else:
        messagebox.showinfo("Search", "مشتری ونه موندل شو!")

# ------------------- Upload File -------------------
def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)

# ------------------- Open File -------------------
def open_file():
    file_path = file_path_var.get()
    if os.path.isfile(file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"فایل نشو خلاصولی: {e}")
    else:
        messagebox.showerror("Error", "فایل ونه موندل شو!")

# ------------------- Clear Form -------------------
def clear_form():
    for entry in entries.values():
        entry.delete(0, tk.END)
    file_path_var.set('')

# ------------------- Initialize GUI -------------------
init_db()

root = tk.Tk()
root.title("د حقوقي خدماتو مشتریانو ډیټابیس")
root.configure(bg='#003366')
root.geometry("700x500")

font_style = ("_PDMS_Kalam", 18)
label_color = "#FFFFFF"
entry_bg = "#F0F8FF"
button_color = "#4B0082"
button_fg = "#FFFFFF"
search_bg = "#4682B4"
frame_bg = "#2F4F4F"

frame = tk.Frame(root, bg=frame_bg)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20, anchor='e')

# ------------------- Input Fields -------------------
fields = [
    ("د مشتری نوم *", "name"),
    ("د پلار نوم *", "father_name"),
    ("د کار نوعیت *", "task"),
    ("نېټه", "date"),
    ("حق الزحمه", "fee")
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    label = tk.Label(frame, text=label_text, font=font_style, bg=frame_bg, fg=label_color, anchor='e')
    label.grid(row=i, column=2, sticky='e', padx=5, pady=5)

    entry = tk.Entry(frame, font=font_style, bg=entry_bg, justify='right')
    entry.grid(row=i, column=1, sticky='e', padx=5, pady=5)
    entries[var_name] = entry

name_entry = entries['name']
father_name_entry = entries['father_name']
task_entry = entries['task']
date_entry = entries['date']
fee_entry = entries['fee']

# ------------------- File Upload/Open -------------------
file_path_var = tk.StringVar()

tk.Button(frame, text="فایل پورته کول", font=font_style, bg=button_color, fg=button_fg, command=upload_file).grid(row=5, column=2, sticky='e', padx=5, pady=5)
tk.Label(frame, textvariable=file_path_var, bg=frame_bg, fg=label_color, font=("Bahij Naskh", 14), anchor='e').grid(row=5, column=1, sticky='e', padx=5, pady=5)
tk.Button(frame, text="فایل خلاصول", font=font_style, bg=button_color, fg=button_fg, command=open_file).grid(row=6, column=2, sticky='e', padx=5, pady=5)

# ------------------- Save Button Only -------------------
tk.Button(frame, text="خوندي کول", font=font_style, bg="#228B22", fg=button_fg, command=save_data).grid(row=7, column=2, sticky='e', padx=5, pady=15)

# ------------------- Search Section -------------------
search_frame = tk.Frame(root, bg=root['bg'])
search_frame.pack(side=tk.BOTTOM, anchor='e', padx=20, pady=10)

tk.Label(search_frame, text="لټون:", font=font_style, bg=root['bg'], fg=label_color, anchor='e').pack(side=tk.RIGHT)
search_entry = tk.Entry(search_frame, font=font_style, bg=search_bg, fg=label_color, justify='right')
search_entry.pack(side=tk.RIGHT, padx=5)
tk.Button(search_frame, text="لټون", font=font_style, bg=button_color, fg=button_fg, command=search_data).pack(side=tk.RIGHT, padx=5)

root.mainloop()
