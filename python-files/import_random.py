import tkinter as tk
from tkinter import messagebox
import random
import string

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def save_credentials(description, username, password):
    if not username or not password:
        messagebox.showwarning("Warning", "Description and Username and Password cannot be empty.")
        return
    try:
        with open("passwords.txt", "a") as f:
            f.write(f"Description: {description}, Username: {username}, Password: {password}\n")
        messagebox.showinfo("Success", "Credentials saved successfully!")
    except IOError:
        messagebox.showerror("Error", "Could not save credentials to file.")

def create_gui():
    root = tk.Tk()
    root.title("Password Generator")

    # Description
    tk.Label(root, text="Description:").grid(row=0, column=0, padx=10, pady=5)
    description_entry = tk.Entry(root, width=30)
    description_entry.grid(row=0, column=1, padx=10, pady=5)

    # Username
    tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(root, width=30)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    # Password Length
    tk.Label(root, text="Password Length:").grid(row=2, column=0, padx=10, pady=5)
    length_entry = tk.Entry(root, width=30)
    length_entry.insert(0, "12") # Default length
    length_entry.grid(row=2, column=1, padx=10, pady=5)

    # Generated Password Display
    tk.Label(root, text="Generated Password:").grid(row=3, column=0, padx=10, pady=5)
    password_display = tk.Entry(root, width=30, state="readonly")
    password_display.grid(row=3, column=1, padx=10, pady=5)

    def on_generate():
        try:
            length = int(length_entry.get())
            if length <= 0:
                messagebox.showwarning("Warning", "Password length must be a positive number.")
                return
            generated_pwd = generate_password(length)
            password_display.config(state="normal")
            password_display.delete(0, tk.END)
            password_display.insert(0, generated_pwd)
            password_display.config(state="readonly")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number for password length.")

    def on_save():
        description = description_entry.get()
        username = username_entry.get()
        password = password_display.get() 
        save_credentials(description, username, password)

    # Buttons
    generate_button = tk.Button(root, text="Generate Password", command=on_generate)
    generate_button.grid(row=4, column=0, columnspan=2, pady=10)

    save_button = tk.Button(root, text="Save Credentials", command=on_save)
    save_button.grid(row=5, column=0, columnspan=2, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()