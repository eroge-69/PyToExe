import tkinter as tk
from tkinter import messagebox

# Function to convert text to numbers
def text_to_numbers(text):
    numbers = []
    for char in text.upper():
        if char.isalpha():
            numbers.append(ord(char) - 64)  # A=1, B=2 ...
        elif char == " ":
            numbers.append("|")  # space ko | se replace kar diya
        else:
            numbers.append(char)  # Other symbols remain same
    return numbers

# Function to convert numbers back to text
def numbers_to_text(numbers):
    text = ""
    for num in numbers:
        if isinstance(num, int):
            text += chr(num + 64)
        elif num == "|":
            text += " "  # | ko wapas space bana diya
        else:
            text += str(num)
    return text

# Encrypt function
def encrypt():
    try:
        key = int(key_entry.get())
        text = input_entry.get()
        numbers = text_to_numbers(text)
        encrypted = []
        for n in numbers:
            if isinstance(n, int):
                encrypted.append(n * key)
            else:
                encrypted.append(n)
        output_entry.delete(0, tk.END)
        output_entry.insert(0, ' '.join(map(str, encrypted)))
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid key!")

# Decrypt function
def decrypt():
    try:
        key = int(key_entry.get())
        encrypted_text = input_entry.get().split()
        decrypted_numbers = []
        for item in encrypted_text:
            if item.isdigit():
                decrypted_numbers.append(int(item) // key)
            elif item == "|":
                decrypted_numbers.append("|")
            else:
                decrypted_numbers.append(item)
        decrypted_text = numbers_to_text(decrypted_numbers)
        output_entry.delete(0, tk.END)
        output_entry.insert(0, decrypted_text)
    except ValueError:
        messagebox.showerror("Error", "Invalid input or key!")

# GUI setup
root = tk.Tk()
root.title("Encryption & Decryption Tool")
root.geometry("500x320")

# Input field
tk.Label(root, text="Enter Text / Encrypted Code:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()

# Key field
tk.Label(root, text="Enter Key (number):").pack()
key_entry = tk.Entry(root, width=20)
key_entry.pack()

# Buttons
encrypt_btn = tk.Button(root, text="Encrypt", command=encrypt, bg="lightgreen")
encrypt_btn.pack(pady=5)

decrypt_btn = tk.Button(root, text="Decrypt", command=decrypt, bg="lightblue")
decrypt_btn.pack(pady=5)

# Output field
tk.Label(root, text="Output:").pack()
output_entry = tk.Entry(root, width=50)
output_entry.pack()

# Footer text
footer = tk.Label(root, text="Developed By Waqas Zafar & Ahmad", fg="gray", font=("Arial", 10))
footer.pack(side="bottom", pady=10)

root.mainloop()
