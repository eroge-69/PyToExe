import random
import csv
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import math
import subprocess
import os
import sys
import tempfile

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("600x650")
        self.root.resizable(True, True)
        
        # Apply a modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#f0f0f0"
        self.frame_bg = "#ffffff"
        self.accent_color = "#4a6fa5"
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style.configure("Card.TFrame", background=self.frame_bg)
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground=self.accent_color)
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20", style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Password Generator", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Configuration notebook (tabs)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Basic options tab
        basic_frame = ttk.Frame(notebook, padding="15")
        notebook.add(basic_frame, text="Basic Options")
        
        # Password count and length
        count_frame = ttk.Frame(basic_frame)
        count_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(count_frame, text="Number of passwords:").pack(side=tk.LEFT)
        self.entry_count = ttk.Entry(count_frame, width=10)
        self.entry_count.pack(side=tk.RIGHT)
        self.entry_count.insert(0, "10")
        
        length_frame = ttk.Frame(basic_frame)
        length_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(length_frame, text="Password length:").pack(side=tk.LEFT)
        self.entry_length = ttk.Entry(length_frame, width=10)
        self.entry_length.pack(side=tk.RIGHT)
        self.entry_length.insert(0, "12")
        
        # Character options
        options_frame = ttk.LabelFrame(basic_frame, text="Character Sets", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=True)
        self.var_numbers = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=True)
        self.var_space = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Lowercase letters (a-z)", variable=self.var_lower).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Uppercase letters (A-Z)", variable=self.var_upper).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.var_numbers).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Common symbols (!@#$%^&*)", variable=self.var_symbols).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Include space", variable=self.var_space).pack(anchor=tk.W, pady=2)
        
        # Custom characters tab
        custom_frame = ttk.Frame(notebook, padding="15")
        notebook.add(custom_frame, text="Custom Characters")
        
        ttk.Label(custom_frame, text="Specify custom characters to include:").pack(anchor=tk.W, pady=(0, 10))
        
        self.var_custom = tk.BooleanVar(value=False)
        ttk.Checkbutton(custom_frame, text="Use custom characters instead of predefined sets", 
                       variable=self.var_custom, command=self.toggle_custom).pack(anchor=tk.W, pady=(0, 10))
        
        self.custom_chars_frame = ttk.Frame(custom_frame)
        self.custom_chars_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.custom_chars_frame, text="Custom characters:").pack(anchor=tk.W)
        self.entry_custom_chars = ttk.Entry(self.custom_chars_frame)
        self.entry_custom_chars.pack(fill=tk.X, pady=(5, 0))
        self.entry_custom_chars.insert(0, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")
        
        # Preview of custom characters
        preview_frame = ttk.Frame(custom_frame)
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(preview_frame, text="Character preview:").pack(anchor=tk.W)
        self.preview_text = tk.Text(preview_frame, height=3, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.X, pady=(5, 0))
        self.preview_text.insert("1.0", self.entry_custom_chars.get())
        self.preview_text.config(state=tk.DISABLED)
        
        # Button to update preview
        ttk.Button(custom_frame, text="Update Preview", command=self.update_preview).pack(anchor=tk.W, pady=(0, 10))
        
        # Initially disable custom chars
        self.toggle_custom()
        
        # Output options
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.var_open_cmd = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Open command prompt to display passwords", variable=self.var_open_cmd).pack(anchor=tk.W, pady=2)
        
        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate Passwords", command=self.generate_passwords, style="Accent.TButton")
        generate_btn.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to generate passwords")
        self.status_label.pack()
        
    def toggle_custom(self):
        if self.var_custom.get():
            state = "normal"
        else:
            state = "disabled"
            
        for child in self.custom_chars_frame.winfo_children():
            child.configure(state=state)
            
    def update_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", self.entry_custom_chars.get())
        self.preview_text.config(state=tk.DISABLED)
        
    def generate_passwords(self):
        try:
            count = int(self.entry_count.get())
            length = int(self.entry_length.get())
            
            if count <= 0 or length <= 0:
                messagebox.showerror("Error", "Count and length must be positive integers.")
                return
                
            # Get character set
            if self.var_custom.get():
                chars = self.entry_custom_chars.get()
                if not chars:
                    messagebox.showerror("Error", "Enter at least one custom character.")
                    return
            else:
                chars = ""
                if self.var_lower.get(): chars += "abcdefghijklmnopqrstuvwxyz"
                if self.var_upper.get(): chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                if self.var_numbers.get(): chars += "0123456789"
                if self.var_symbols.get(): chars += "!@#$%^&*"
                if self.var_space.get(): chars += " "
                
                if not chars:
                    messagebox.showerror("Error", "Select at least one character type.")
                    return
            
            # Generate passwords
            passwords = []
            for _ in range(count):
                password = "".join(random.choice(chars) for _ in range(length))
                passwords.append(password)
            
            # Save to file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv", 
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")], 
                title="Save passwords to file"
            )
            
            if not filename:
                return  # User canceled
                
            # Calculate how many columns we need for Excel
            max_rows = 1048576  # Excel row limit
            columns_needed = math.ceil(count / max_rows)
            
            # Write to CSV
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                
                # Write passwords in columns
                for i in range(0, count, max_rows):
                    column = passwords[i:i+max_rows]
                    # Pad with empty strings if needed
                    if len(column) < max_rows:
                        column.extend([""] * (max_rows - len(column)))
                    writer.writerow(column)
            
            # Show success message
            self.status_label.config(text=f"Generated {count} passwords saved to {filename}")
            messagebox.showinfo("Success", f"{count} passwords saved to {filename}")
            
            # Open command prompt to display passwords if requested
            if self.var_open_cmd.get():
                self.show_in_command_prompt(passwords, filename)
                
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers for count and length.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def show_in_command_prompt(self, passwords, filename):
        """Display passwords in a command prompt window"""
        try:
            # Create a temporary batch file
            batch_content = "@echo off\n"
            batch_content += "title Password Generator Output\n"
            batch_content += "echo ============================================\n"
            batch_content += "echo          PASSWORD GENERATOR OUTPUT\n"
            batch_content += "echo ============================================\n"
            batch_content += f"echo Generated: {len(passwords)} passwords\n"
            batch_content += f"echo Saved to: {filename}\n"
            batch_content += "echo.\n"
            batch_content += "echo Passwords:\n"
            batch_content += "echo --------------------------------------------\n"
            
            for i, password in enumerate(passwords, 1):
                batch_content += f"echo {i:3d}. {password}\n"
            
            batch_content += "echo --------------------------------------------\n"
            batch_content += "echo Press any key to exit...\n"
            batch_content += "pause >nul\n"
            
            # Create temporary batch file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
                f.write(batch_content)
                temp_batch = f.name
            
            # Execute the batch file in a new command window
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'start cmd /k "{temp_batch}"', shell=True)
            else:  # macOS/Linux - though this is primarily for Windows
                subprocess.Popen(['xterm', '-e', temp_batch])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open command prompt: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()