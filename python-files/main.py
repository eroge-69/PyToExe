import tkinter as tk
from tkinter import messagebox

MAX_LENGTH = 16  # this is the buffer part

# Dummy in-memory file storage
file_storage = []

def compress_file():
    filename = entry.get().strip()
    if len(filename) == 0:
        messagebox.showwarning("Input Error", "Please enter a filename!")
        return

    if len(filename) > MAX_LENGTH:
        messagebox.showerror("Overflow!", "Buffer overflow detected! Input too long!")
        return

    # Simulate compression
    compressed_size = len(filename) * 42  # Dummy computation
    file_storage.append((filename, compressed_size))
    messagebox.showinfo("Success", f"Compressing '{filename}'\nCompressed size: {compressed_size} bytes")
    entry.delete(0, tk.END)

def list_files():
    if not file_storage:
        messagebox.showinfo("Files", "No files have been compressed yet.")
        return

    files_list = "\n".join([f"{name} ({size} bytes)" for name, size in file_storage])
    messagebox.showinfo("Compressed Files", files_list)

def decompress_file():
    if not file_storage:
        messagebox.showinfo("Decompress", "No files to decompress.")
        return

    filename = entry.get().strip()
    for i, (name, size) in enumerate(file_storage):
        if name == filename:
            file_storage.pop(i)
            messagebox.showinfo("Decompressed", f"File '{filename}' decompressed successfully!")
            entry.delete(0, tk.END)
            return
    messagebox.showwarning("Not Found", f"No compressed file named '{filename}' found.")

# GUI setup
root = tk.Tk()
root.title("Mini Zipper Demo")
root.geometry("350x250")  # Window size

tk.Label(root, text="Mini Zipper Tool", font=("Helvetica", 16, "bold")).pack(pady=10)
tk.Label(root, text="Enter filename:").pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

# Buttons
tk.Button(root, text="Compress", width=15, command=compress_file).pack(pady=5)
tk.Button(root, text="Decompress", width=15, command=decompress_file).pack(pady=5)
tk.Button(root, text="List Compressed Files", width=20, command=list_files).pack(pady=5)

tk.Label(root, text="*Max filename length = 16 characters*", font=("Helvetica", 8, "italic")).pack(pady=10)

root.mainloop()
