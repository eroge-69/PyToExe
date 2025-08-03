import tkinter as tk
from tkinter import messagebox
import random

# Function to generate random number
def generate_random():
    try:
        num1 = int(entry1.get())
        num2 = int(entry2.get())
        rand_num = random.randint(min(num1, num2), max(num1, num2))
        result_label.config(text=f"Random Number: {rand_num}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid integers.")

# Create the main window
root = tk.Tk()
root.title("Random Number Generator")

# Create and place widgets
tk.Label(root, text="Enter first number:").grid(row=0, column=0, padx=10, pady=5)
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Enter second number:").grid(row=1, column=0, padx=10, pady=5)
entry2 = tk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=5)

generate_button = tk.Button(root, text="Generate", command=generate_random)
generate_button.grid(row=2, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="Random Number: ")
result_label.grid(row=3, column=0, columnspan=2, pady=10)

# Run the GUI loop
root.mainloop()
