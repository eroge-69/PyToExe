import tkinter as tk
from tkinter import messagebox
import urllib.parse
import pyperclip

def paste_from_clipboard():
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, pyperclip.paste())

def generate_link():
    file_path = file_path_entry.get().strip()
    page = page_entry.get().strip()

    if not file_path or not page.isdigit():
        messagebox.showerror("Error", "Please enter a valid file path and page number.")
        return

    file_path_uri = file_path.replace("\\", "/")  # Windows to URL style
    file_path_uri = urllib.parse.quote(file_path_uri)  # Encode spaces and special chars

    final_link = f"file:///{file_path_uri}#page={page}"
    pyperclip.copy(final_link)
    messagebox.showinfo("Success", f"Your link has been copied to clipboard:\n\n{final_link}")

# GUI setup
root = tk.Tk()
root.title("PDF Page Link Generator")
root.geometry("500x200")
root.resizable(False, False)

tk.Label(root, text="PDF File Path:").pack(pady=5)
file_path_entry = tk.Entry(root, width=60)
file_path_entry.pack()

tk.Button(root, text="Paste from Clipboard", command=paste_from_clipboard).pack(pady=5)

tk.Label(root, text="Page Number:").pack(pady=5)
page_entry = tk.Entry(root, width=10)
page_entry.pack()

tk.Button(root, text="Generate Link", command=generate_link).pack(pady=10)

root.mainloop()
