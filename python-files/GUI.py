import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def select_file(var, label):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xlsm")])
    if file_path:
        var.set(file_path)
        label.config(text=file_path)

def run_gl_migration():
    file1 = file1_var.get()
    file2 = file2_var.get()
    file3 = file3_var.get()

    if not file1 or not file2 or not file3:
        messagebox.showerror("Error", "All three files must be selected.")
        return

    subprocess.run(['python', 'GL Migration.py', file1, file2, file3])
    messagebox.showinfo("Success","GL Migration Checklist is ready.")
    root.destroy() #close the main file prompt window

# Create the main window
root = tk.Tk()
root.title("File Selector")

# Variables to store file paths
file1_var = tk.StringVar()
file2_var = tk.StringVar()
file3_var = tk.StringVar()

# Create and place widgets
tk.Label(root, text="Select CCW file:").grid(row=0, column=0, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: select_file(file1_var, file1_label)).grid(row=0, column=1, padx=10, pady=5)
file1_label = tk.Label(root, text="")
file1_label.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Select GLPortal file:").grid(row=1, column=0, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: select_file(file2_var, file2_label)).grid(row=1, column=1, padx=10, pady=5)
file2_label = tk.Label(root, text="")
file2_label.grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Select Checklist file:").grid(row=2, column=0, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: select_file(file3_var, file3_label)).grid(row=2, column=1, padx=10, pady=5)
file3_label = tk.Label(root, text="")
file3_label.grid(row=2, column=2, padx=10, pady=5)

tk.Button(root, text="Run GL Migration", command=run_gl_migration).grid(row=3, column=0, columnspan=3, pady=20)

# Run the Tkinter event loop
root.mainloop()