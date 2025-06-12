
import tkinter as tk
from tkinter import messagebox

def submit_action():
    user_input = entry.get()
    messagebox.showinfo("Submission Received", f"You entered: {user_input}")

# Create the main window
root = tk.Tk()
root.title("Sample Tkinter Form")
root.geometry("300x150")

# Create a label
label = tk.Label(root, text="Enter your name:")
label.pack(pady=10)

# Create a text entry field
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

# Create a submit button
submit_button = tk.Button(root, text="Submit", command=submit_action)
submit_button.pack(pady=10)

# Run the application
root.mainloop()
