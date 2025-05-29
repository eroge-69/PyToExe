import tkinter as tk
from tkinter import messagebox
import webbrowser

def check_word(event=None):
    user_input = entry.get().lower()  # Convert to lowercase for case-insensitive check
    if user_input == "564217":
        webbrowser.open('https://www.youtube.com/')
        entry.delete(0, tk.END)  # Clear the entry box
    elif user_input == "0156028":
        webbrowser.open("https://disk.yandex.ru/d/e1uN6eIxhbM0rw")

# Create main window
root = tk.Tk()
root.title("???")
root.resizable(0,0)

# Create label
label = tk.Label(root, text="Введите пароль:")
label.pack(pady=10)

# Create entry box
entry = tk.Entry(root, width=30)
entry.pack(pady=5)
entry.bind("<Return>", check_word)  # Check when Enter is pressed
entry.focus()  # Focus on entry box immediately

# Create check button
check_button = tk.Button(root, text="Check", command=check_word)
check_button.pack(pady=10)

# Run the application
root.mainloop()