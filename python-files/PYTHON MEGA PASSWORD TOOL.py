
import sys
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or higher.")
    sys.exit(1)

from collections import Counter
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PasswordProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Processor")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        # Style for professional look
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TRadiobutton", font=("Helvetica", 12), background="#f0f0f0")
        
        # Input file selection
        self.input_file = tk.StringVar()
        ttk.Label(root, text="Input File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.input_entry = ttk.Entry(root, textvariable=self.input_file, width=40)
        self.input_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(root, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=10, pady=10)
        
        # Output file name
        self.output_file = tk.StringVar()
        ttk.Label(root, text="Output File Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.output_entry = ttk.Entry(root, textvariable=self.output_file, width=40)
        self.output_entry.grid(row=1, column=1, padx=10, pady=10)
        self.output_entry.insert(0, "output.txt")  # Default name
        
        # Processing options
        ttk.Label(root, text="Processing Option:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        self.option = tk.IntVar(value=1)
        ttk.Radiobutton(root, text="1. All passwords (most to least used)", variable=self.option, value=1).grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(root, text="2. Passwords used 2+ times", variable=self.option, value=2).grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(root, text="3. Custom minimum uses", variable=self.option, value=3).grid(row=4, column=1, sticky="w")
        
        # Custom min count entry (hidden initially)
        self.custom_frame = tk.Frame(root, bg="#f0f0f0")
        self.custom_frame.grid(row=5, column=1, sticky="w")
        ttk.Label(self.custom_frame, text="Min uses:").pack(side="left", padx=5)
        self.custom_min = tk.IntVar(value=3)
        self.custom_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_min, width=5)
        self.custom_entry.pack(side="left")
        self.custom_frame.grid_remove()  # Hide initially
        
        # Bind option change to show/hide custom entry
        self.option.trace("w", self.toggle_custom)
        
        # Process button
        ttk.Button(root, text="Process", command=self.process).grid(row=6, column=1, pady=20)
        
        # Status label
        self.status = ttk.Label(root, text="", font=("Helvetica", 10), background="#f0f0f0")
        self.status.grid(row=7, column=0, columnspan=3, pady=10)

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)

    def toggle_custom(self, *args):
        if self.option.get() == 3:
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()

    def process(self):
        input_path = self.input_file.get()
        output_name = self.output_file.get().strip()
        
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        if not output_name:
            messagebox.showerror("Error", "Please enter an output file name.")
            return
        
        # Ensure output has .txt extension
        if not output_name.lower().endswith('.txt'):
            output_name += '.txt'
        
        # Output path: same directory as input or current dir if not
        output_dir = os.path.dirname(input_path) if input_path else os.getcwd()
        output_path = os.path.join(output_dir, output_name)
        
        # Determine min_count
        option = self.option.get()
        if option == 1:
            min_count = 1
        elif option == 2:
            min_count = 2
        elif option == 3:
            try:
                min_count = self.custom_min.get()
                if min_count < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Custom min uses must be a positive integer.")
                return
        else:
            messagebox.showerror("Error", "Invalid option selected.")
            return
        
        # Process the file
        success = self.process_password_file(input_path, output_path, min_count)
        if success:
            self.status.config(text=f"Processing complete. Output saved to {output_path}")
        else:
            self.status.config(text="Processing failed. See console for details.")

    def process_password_file(self, input_file, output_file, min_count):
        passwords = []
        
        # Read input (read-only, no destruction)
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            password = parts[1].strip()
                            if password:
                                passwords.append(password)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
            return False
        
        if not passwords:
            messagebox.showinfo("Info", "No valid passwords found in the file.")
            return False
        
        # Count and sort
        freq_counter = Counter(passwords)
        sorted_passwords = sorted(
            [(pwd, count) for pwd, count in freq_counter.items() if count >= min_count],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Write output
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for password, _ in sorted_passwords:
                    f.write(f"{password}\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error writing to output file: {e}")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordProcessorApp(root)
    root.mainloop()
