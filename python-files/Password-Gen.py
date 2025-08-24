import secrets
import tkinter as tk
from tkinter import messagebox

# Character pools
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
digits = "0123456789"

def generate_word(length=8, include_digits=True):
    """
    Generate a pronounceable, word-like password.
    Alternates consonants and vowels, randomly capitalizes letters.
    Optionally appends digits at the end.
    """
    result = ""
    use_consonant = True  # start with consonant

    for _ in range(length):
        if use_consonant:
            char = secrets.choice(consonants)
        else:
            char = secrets.choice(vowels)
        # Randomly uppercase about 50% of letters
        if secrets.randbelow(2) == 1:
            char = char.upper()
        result += char
        use_consonant = not use_consonant  # alternate

    if include_digits:
        # append 1–2 digits for extra security
        for _ in range(2):
            result += secrets.choice(digits)

    return result

def on_generate():
    try:
        length = int(length_var.get())
        if length < 1 or length > 50:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a number between 1 and 50")
        return

    password = generate_word(length, include_digits=True)
    password_var.set(password)

    # Save to file as backup
    with open("password.txt", "w") as f:
        f.write(password)

# Create GUI
root = tk.Tk()
root.title("Word-Like Password Generator")
root.resizable(False, False)

# Length input
tk.Label(root, text="Password length (letters only, 1–50):").pack(padx=10, pady=(10,0))
length_var = tk.StringVar(value="8")
length_entry = tk.Entry(root, textvariable=length_var, width=5, justify='center')
length_entry.pack(padx=10, pady=(0,10))

# Generate button
generate_btn = tk.Button(root, text="Generate Password", command=on_generate)
generate_btn.pack(padx=10, pady=(0,10))

# Read-only password display
tk.Label(root, text="Your new password:").pack(padx=10, pady=(0,0))
password_var = tk.StringVar()
password_entry = tk.Entry(root, textvariable=password_var, width=30, justify='center', state='readonly')
password_entry.pack(padx=10, pady=(0,10))

# Close button
close_btn = tk.Button(root, text="Close", command=root.destroy)
close_btn.pack(pady=(0,10))

root.mainloop()
