import tkinter as tk
from tkinter import messagebox
import random
import string

def generate_code(length=8):
    # Define the character set to include uppercase letters, digits, and the '*' symbol
    characters = string.ascii_uppercase + string.digits + "*"
    
    # Ensure the '*' character is included in the generated code
    code = ''.join(random.choices(characters, k=length-1)) + '*'
    
    return code

def validate_number(value):
    digits_only = value.replace(" ", "")
    if not digits_only.isdigit():
        return False
    if digits_only.startswith('0') and len(digits_only) == 10:
        return True
    elif digits_only.startswith('5') and len(digits_only) == 9:
        return True
    return False

def on_generate():
    value = number_entry.get()
    digits_only = value.replace(" ", "")
    if not validate_number(digits_only):
        messagebox.showerror("Error", "Incorrect number")
        return
    code = generate_code()
    code_entry.config(state="normal")
    code_entry.delete(0, tk.END)
    code_entry.insert(0, code)
    code_entry.config(state="readonly")

def on_login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "dldlogin" and password == "agency1":
        login_window.destroy()
        main_window()
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password")

def main_window():
    main_win = tk.Tk()
    main_win.title("Enter a Number")
    main_win.geometry("400x200")
    main_win.resizable(False, False)

    tk.Label(main_win, text="Enter a number:").pack(pady=5)

    global number_entry
    number_entry = tk.Entry(main_win)
    number_entry.pack(pady=5)

    global code_entry
    code_entry = tk.Entry(main_win, state="readonly", width=20)
    code_entry.pack(pady=5)

    tk.Button(main_win, text="Generate Code", command=on_generate).pack(pady=5)

    main_win.mainloop()

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x200")
login_window.resizable(False, False)

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

tk.Button(login_window, text="Login", command=on_login).pack(pady=10)

login_window.mainloop()
