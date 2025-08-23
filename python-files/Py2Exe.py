import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


class PyToExeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Python to EXE Converter")
        self.root.geometry("500x300")
        self.root.configure(bg="#f0f0f0")
        
        
        self.file_label = tk.Label(root, text="Select Python File:", bg="#f0f0f0")
        self.file_label.pack(pady=10)
        
        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.pack(pady=5)
        
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file, bg="#4CAF50", fg="white")
        self.browse_button.pack(pady=5)
        
        
        self.option_frame = tk.Frame(root, bg="#f0f0f0")
        self.option_frame.pack(pady=10)
        
        self.console_var = tk.IntVar()
        self.console_check = tk.Checkbutton(self.option_frame, text="Console Application", variable=self.console_var, bg="#f0f0f0")
        self.console_check.grid(row=0, column=0, padx=10)
        
        self.onefile_var = tk.IntVar(value=1)
        self.onefile_check = tk.Checkbutton(self.option_frame, text="One File", variable=self.onefile_var, bg="#f0f0f0")
        self.onefile_check.grid(row=0, column=1, padx=10)
        
        self.icon_label = tk.Label(self.option_frame, text="Icon File:", bg="#f0f0f0")
        self.icon_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.icon_entry = tk.Entry(self.option_frame, width=30)
        self.icon_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.icon_button = tk.Button(self.option_frame, text="Browse", command=self.browse_icon, bg="#4CAF50", fg="white")
        self.icon_button.grid(row=1, column=2, padx=10, pady=10)
        
        
        self.convert_button = tk.Button(root, text="Convert to EXE", command=self.convert_to_exe, bg="#2196F3", fg="white", width=20)
        self.convert_button.pack(pady=20)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        self.file_entry.insert(0, file_path)
    
    def browse_icon(self):
        icon_path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        self.icon_entry.insert(0, icon_path)
    
    def convert_to_exe(self):
        file_path = self.file_entry.get()
        if not file_path.endswith(".py"):
            messagebox.showerror("Error", "Please select a valid Python file.")
            return
        
        command = ["pyinstaller"]
        
        if self.console_var.get() == 0:
            command.append("--windowed")
        if self.onefile_var.get() == 1:
            command.append("--onefile")
        
        icon_path = self.icon_entry.get()
        if icon_path:
            command.extend(["--icon", icon_path])
        
        command.append(file_path)
        
        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Conversion completed successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Conversion failed. Please check the details and try again.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PyToExeConverter(root)
    root.mainloop()
