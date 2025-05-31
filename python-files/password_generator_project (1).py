
import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


def generate_password():
    length = int(length_var.get())
    use_upper = upper_var.get()
    use_lower = lower_var.get()
    use_digits = number_var.get()
    use_symbols = symbol_var.get()

    characters = ''
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters:
        messagebox.showwarning("Warning", "Please select at least one character set!")
        return

    password = ''.join(random.choice(characters) for _ in range(length))
    password_var.set(password)


def copy_password():
    root.clipboard_clear()
    root.clipboard_append(password_var.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")


def toggle_theme():
    current = style.theme_use()
    new_theme = "alt" if current == "clam" else "clam"
    style.theme_use(new_theme)
    apply_theme(new_theme)

def apply_theme(theme):
    if theme == "clam":
        root.configure(bg="#121212")
        style.configure("TLabel", background="#121212", foreground="white")
        style.configure("TButton", background="#00ff99", foreground="black", font=("Consolas", 10, "bold"))
        style.configure("TCheckbutton", background="#121212", foreground="white")
    else:
        root.configure(bg="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5", foreground="black")
        style.configure("TButton", background="green", foreground="white", font=("Consolas", 10, "bold"))
        style.configure("TCheckbutton", background="#f5f5f5", foreground="black")


root = tk.Tk()
root.title("🔐 Advanced Password Generator")
root.geometry("600x500")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")
apply_theme("clam")


password_var = tk.StringVar()
length_var = tk.IntVar(value=20)
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
number_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=False)


ttk.Label(root, text="🔐 Generate a Secure Password", font=("Consolas", 18, "bold")).pack(pady=15)

password_entry = ttk.Entry(root, textvariable=password_var, font=("Consolas", 14), width=45)
password_entry.pack(pady=5)

ttk.Button(root, text="📋 Copy Password", command=copy_password).pack(pady=5)

ttk.Separator(root).pack(fill="x", pady=15)

ttk.Label(root, text="⚙️ Customize Password", font=("Consolas", 14, "bold")).pack(pady=5)

frame = ttk.Frame(root)
frame.pack(pady=10)


ttk.Checkbutton(frame, text="Include Uppercase (A-Z)", variable=upper_var).grid(row=0, column=0, sticky='w', padx=15, pady=4)
ttk.Checkbutton(frame, text="Include Lowercase (a-z)", variable=lower_var).grid(row=1, column=0, sticky='w', padx=15, pady=4)
ttk.Checkbutton(frame, text="Include Numbers (0-9)", variable=number_var).grid(row=2, column=0, sticky='w', padx=15, pady=4)
ttk.Checkbutton(frame, text="Include Symbols (!@#)", variable=symbol_var).grid(row=3, column=0, sticky='w', padx=15, pady=4)


ttk.Label(frame, text="🔢 Password Length:").grid(row=0, column=1, padx=30, pady=5)
length_slider = ttk.Scale(frame, from_=4, to=50, orient='horizontal', variable=length_var)
length_slider.grid(row=1, column=1, rowspan=2, pady=10, padx=10)


ttk.Button(root, text="⚡ Generate Password", command=generate_password).pack(pady=15)


theme_button = ttk.Button(root, text="🌙 Toggle Theme", command=toggle_theme)
theme_button.pack()


ttk.Label(root, text="✍️ Created by pritom.en", font=("Consolas", 11, "italic")).pack(side="bottom", pady=15)

root.mainloop()

