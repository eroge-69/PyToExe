
import tkinter as tk

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(text_to_copy)
    root.update()  # Keeps the clipboard content after the window is closed

# Create the main window
root = tk.Tk()
root.title("Copy Text App")

# Text to be copied
text_to_copy = "NU%1q-2g"

# Create a label to display the text
label = tk.Label(root, text=text_to_copy, font=("Arial", 14))
label.pack(pady=10)

# Create a button to copy the text
copy_button = tk.Button(root, text="Copy", command=copy_to_clipboard)
copy_button.pack(pady=5)

# Run the application
root.mainloop()
