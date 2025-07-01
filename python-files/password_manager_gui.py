import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import hashlib
from cryptography.fernet import Fernet
import base64

AUTH_FILE = "auth.json"
DATA_FILE = "storage.json"

# --------- AUTH ---------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_registered():
    return os.path.exists(AUTH_FILE)

def register_master(password):
    with open(AUTH_FILE, 'w') as f:
        json.dump({"master": hash_password(password)}, f)

def validate_master(input_password):
    if not is_registered():
        return False
    with open(AUTH_FILE, 'r') as f:
        data = json.load(f)
        return data["master"] == hash_password(input_password)

# --------- ENCRYPTION ---------
def generate_key(master_password):
    digest = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def get_fernet(master_password):
    key = generate_key(master_password)
    return Fernet(key)

# --------- DATA STORAGE ---------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def add_entry(site, username, password, fernet):
    encrypted_pw = fernet.encrypt(password.encode()).decode()
    data = load_data()
    data.append({"site": site, "username": username, "password": encrypted_pw})
    save_data(data)

def decrypt_entries(fernet):
    data = load_data()
    decrypted = []
    for entry in data:
        decrypted_pw = fernet.decrypt(entry["password"].encode()).decode()
        decrypted.append({"site": entry["site"], "username": entry["username"], "password": decrypted_pw})
    return decrypted

# --------- GUI ---------
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Password Manager")
        self.root.geometry("400x300")
        self.fernet = None
        self.master_password = ""
        self.init_login()

    def init_login(self):
        self.clear_window()

        label = tk.Label(self.root, text="🔐 Welcome to Password Manager", font=("Arial", 14))
        label.pack(pady=10)

        if not is_registered():
            tk.Label(self.root, text="Set a Master Password:").pack()
            self.pass_entry = tk.Entry(self.root, show="*")
            self.pass_entry.pack()
            tk.Button(self.root, text="Register", command=self.register).pack(pady=5)
        else:
            tk.Label(self.root, text="Enter Master Password:").pack()
            self.pass_entry = tk.Entry(self.root, show="*")
            self.pass_entry.pack()
            tk.Button(self.root, text="Login", command=self.login).pack(pady=5)

    def register(self):
        pw = self.pass_entry.get()
        if len(pw) < 4:
            messagebox.showerror("Error", "Password too short.")
            return
        register_master(pw)
        messagebox.showinfo("Success", "Registered successfully!")
        self.init_login()

    def login(self):
        pw = self.pass_entry.get()
        if validate_master(pw):
            self.master_password = pw
            self.fernet = get_fernet(pw)
            self.init_main_menu()
        else:
            messagebox.showerror("Error", "Invalid password.")

    def init_main_menu(self):
        self.clear_window()
        tk.Label(self.root, text="🔐 Password Manager", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Add New Password", command=self.add_password_window).pack(pady=5)
        tk.Button(self.root, text="View Saved Passwords", command=self.view_passwords_window).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.init_login).pack(pady=20)

    def add_password_window(self):
        site = simpledialog.askstring("Site", "Enter site name:")
        username = simpledialog.askstring("Username", "Enter username/email:")
        password = simpledialog.askstring("Password", "Enter password:")

        if site and username and password:
            add_entry(site, username, password, self.fernet)
            messagebox.showinfo("Saved", "Password saved!")

    def view_passwords_window(self):
        entries = decrypt_entries(self.fernet)
        top = tk.Toplevel(self.root)
        top.title("Saved Passwords")
        top.geometry("400x300")

        for entry in entries:
            frame = tk.Frame(top)
            frame.pack(pady=5)
            tk.Label(frame, text=f"🔹 {entry['site']}", font=("Arial", 10, "bold")).pack(anchor='w')
            tk.Label(frame, text=f"Username: {entry['username']}").pack(anchor='w')
            tk.Label(frame, text=f"Password: {entry['password']}").pack(anchor='w')

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
