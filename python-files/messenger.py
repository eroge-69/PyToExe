import tkinter as tk
from tkinter import messagebox
import json
import os

# Mock database (in-memory dictionary for simplicity)
users = {}

# Save users to a JSON file (simulating a database)
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

# Load users from JSON file
def load_users():
    global users
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)

# Main Application Window
class MessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Messenger")
        self.root.geometry("400x500")
        self.show_login_window()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_window(self):
        self.clear_window()
        self.root.title("Login")
        
        tk.Label(self.root, text="Username").pack(pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        
        tk.Label(self.root, text="Password").pack(pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.show_register_window).pack(pady=10)

    def show_register_window(self):
        self.clear_window()
        self.root.title("Register")
        
        tk.Label(self.root, text="Username").pack(pady=10)
        self.reg_username_entry = tk.Entry(self.root)
        self.reg_username_entry.pack()
        
        tk.Label(self.root, text="Password").pack(pady=10)
        self.reg_password_entry = tk.Entry(self.root, show="*")
        self.reg_password_entry.pack()
        
        tk.Label(self.root, text="Confirm Password").pack(pady=10)
        self.reg_confirm_password_entry = tk.Entry(self.root, show="*")
        self.reg_confirm_password_entry.pack()
        
        tk.Button(self.root, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.show_login_window).pack(pady=10)

    def show_chat_window(self, username):
        self.clear_window()
        self.root.title(f"Messenger - {username}")
        
        tk.Label(self.root, text=f"Welcome, {username}!").pack(pady=10)
        
        self.chat_display = tk.Text(self.root, height=15, width=40, state="disabled")
        self.chat_display.pack(pady=10)
        
        tk.Label(self.root, text="Message").pack()
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.pack()
        
        tk.Button(self.root, text="Send", command=self.send_message).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.show_login_window).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if username in users and users[username] == password:
            messagebox.showinfo("Success", "Login successful!")
            self.show_chat_window(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return
        
        users[username] = password
        save_users()
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.show_login_window()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.chat_display.config(state="normal")
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.chat_display.config(state="disabled")
            self.message_entry.delete(0, tk.END)
            # Simulate receiving a message (for demo purposes)
            self.chat_display.config(state="normal")
            self.chat_display.insert(tk.END, f"Friend: Hi! I got your message: {message}\n")
            self.chat_display.config(state="disabled")

if __name__ == "__main__":
    load_users()
    root = tk.Tk()
    app = MessengerApp(root)
    root.mainloop()