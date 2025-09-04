import random
import string
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class PasswordTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Password Guardian")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f8ff')
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        
        self.setup_ui()
        
    def setup_styles(self):
        # Configure styles
        self.style.configure('TFrame', background='#f0f8ff')
        self.style.configure('TLabel', background='#f0f8ff', font=('Arial', 10))
        self.style.configure('Title.TLabel', background='#f0f8ff', font=('Arial', 16, 'bold'))
        self.style.configure('Strength.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Generate.TButton', background='#4CAF50', foreground='white')
        self.style.configure('Copy.TButton', background='#2196F3', foreground='white')
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TNotebook', background='#f0f8ff')
        self.style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
    def setup_ui(self):
        # Main title
        title_label = ttk.Label(self.root, text="🔒 Password Guardian", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=20, expand=True, fill='both')
        
        # Evaluate password frame
        eval_frame = ttk.Frame(notebook, padding=15)
        eval_frame.pack(fill='both', expand=True)
        
        ttk.Label(eval_frame, text="Enter your password to check its strength:").pack(pady=5, anchor='w')
        
        # Password entry with show/hide toggle
        entry_frame = ttk.Frame(eval_frame)
        entry_frame.pack(pady=5, fill='x')
        
        self.password_entry = ttk.Entry(entry_frame, width=40, font=('Arial', 11))
        self.password_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.password_entry.bind('<KeyRelease>', self.realtime_check)
        
        self.show_password = tk.BooleanVar(value=False)
        ttk.Checkbutton(entry_frame, text="Show", variable=self.show_password, 
                       command=self.toggle_password_visibility).pack(side='right')
        
        # Strength meter
        strength_frame = ttk.Frame(eval_frame)
        strength_frame.pack(pady=10, fill='x')
        
        ttk.Label(strength_frame, text="Strength:").pack(side='left')
        self.strength_label = ttk.Label(strength_frame, text="", style='Strength.TLabel')
        self.strength_label.pack(side='left', padx=5)
        
        # Strength progress bar
        self.strength_bar = ttk.Progressbar(eval_frame, maximum=100, mode='determinate')
        self.strength_bar.pack(pady=5, fill='x')
        
        # Suggestions box
        ttk.Label(eval_frame, text="Suggestions:").pack(pady=(15, 5), anchor='w')
        
        suggestion_frame = ttk.Frame(eval_frame)
        suggestion_frame.pack(fill='both', expand=True)
        
        self.suggestions_text = tk.Text(suggestion_frame, height=6, width=50, font=('Arial', 9),
                                       bg='#fffaf0', relief='solid', bd=1, wrap='word')
        scrollbar = ttk.Scrollbar(suggestion_frame, orient='vertical', command=self.suggestions_text.yview)
        self.suggestions_text.configure(yscrollcommand=scrollbar.set)
        
        self.suggestions_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Suggested passwords
        ttk.Label(eval_frame, text="Suggested strong passwords:").pack(pady=(15, 5), anchor='w')
        
        self.suggested_passwords = []
        for i in range(3):
            suggested_frame = ttk.Frame(eval_frame)
            suggested_frame.pack(fill='x', pady=2)
            
            password_var = tk.StringVar()
            self.suggested_passwords.append(password_var)
            
            ttk.Entry(suggested_frame, textvariable=password_var, 
                     font=('Consolas', 10), state='readonly', width=30).pack(side='left', fill='x', expand=True, padx=(0, 5))
            ttk.Button(suggested_frame, text="Copy", width=8,
                      command=lambda var=password_var: self.copy_suggested(var)).pack(side='right')
        
        # Generate password frame
        gen_frame = ttk.Frame(notebook, padding=15)
        gen_frame.pack(fill='both', expand=True)
        
        ttk.Label(gen_frame, text="Generate a strong password:").pack(pady=5, anchor='w')
        
        options_frame = ttk.Frame(gen_frame)
        options_frame.pack(pady=10, fill='x')
        
        ttk.Label(options_frame, text="Length:").grid(row=0, column=0, sticky='w', pady=5)
        self.length_var = tk.IntVar(value=14)
        length_spin = ttk.Spinbox(options_frame, from_=8, to=30, 
                                 textvariable=self.length_var, width=10)
        length_spin.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Options
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Uppercase Letters (A-Z)", 
                       variable=self.upper_var).grid(row=1, column=0, sticky='w', columnspan=2, pady=2)
        ttk.Checkbutton(options_frame, text="Lowercase Letters (a-z)", 
                       variable=self.lower_var).grid(row=2, column=0, sticky='w', columnspan=2, pady=2)
        ttk.Checkbutton(options_frame, text="Digits (0-9)", 
                       variable=self.digits_var).grid(row=1, column=1, sticky='w', columnspan=2, pady=2)
        ttk.Checkbutton(options_frame, text="Special Characters (!@#$)", 
                       variable=self.special_var).grid(row=2, column=1, sticky='w', columnspan=2, pady=2)
        
        ttk.Button(gen_frame, text="Generate Password", style='Generate.TButton',
                  command=self.generate_password).pack(pady=15)
        
        self.generated_password = tk.StringVar()
        password_display_frame = ttk.Frame(gen_frame)
        password_display_frame.pack(fill='x', pady=10)
        
        ttk.Entry(password_display_frame, textvariable=self.generated_password, 
                 font=('Consolas', 12), state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(password_display_frame, text="Copy", style='Copy.TButton',
                  command=self.copy_to_clipboard).pack(side='right')
        
        # Strength indicator for generated password
        gen_strength_frame = ttk.Frame(gen_frame)
        gen_strength_frame.pack(fill='x', pady=5)
        
        ttk.Label(gen_strength_frame, text="Strength:").pack(side='left')
        self.gen_strength_label = ttk.Label(gen_strength_frame, text="", style='Strength.TLabel')
        self.gen_strength_label.pack(side='left', padx=5)
        
        # Add tabs to notebook
        notebook.add(eval_frame, text="Check Password")
        notebook.add(gen_frame, text="Generate Password")
        
        # Generate initial suggested passwords
        self.update_suggested_passwords()
        
    def toggle_password_visibility(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")
    
    def realtime_check(self, event=None):
        password = self.password_entry.get()
        if password:
            strength, score, feedback = self.check_password_strength(password)
            
            # Update strength label with color
            colors = {
                "Very Weak": "#ff0000",
                "Weak": "#ff5500",
                "Moderate": "#ffaa00",
                "Strong": "#55aa00",
                "Very Strong": "#00aa00"
            }
            
            self.strength_label.config(text=strength, foreground=colors.get(strength, "black"))
            self.strength_bar['value'] = score
            
            # Update suggestions
            self.suggestions_text.delete(1.0, tk.END)
            if feedback:
                self.suggestions_text.insert(1.0, "\n\n".join(feedback))
            else:
                self.suggestions_text.insert(1.0, "✅ Excellent! Your password meets all strength criteria!")
        else:
            self.strength_label.config(text="")
            self.strength_bar['value'] = 0
            self.suggestions_text.delete(1.0, tk.END)
    
    def check_password_strength(self, password):
        score = 0
        feedback = []
        max_score = 7
        
        # Length check
        if len(password) >= 16:
            score += 2
        elif len(password) >= 12:
            score += 1.5
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("❌ Password should be at least 8 characters long")
        
        # Upper case letters
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("❌ Add uppercase letters (A-Z)")
        
        # Lower case letters
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("❌ Add lowercase letters (a-z)")
        
        # Digits
        if re.search(r'[0-9]', password):
            score += 1
        else:
            feedback.append("❌ Add numbers (0-9)")
        
        # Special characters
        if re.search(r'[^A-Za-z0-9]', password):
            score += 1
        else:
            feedback.append("❌ Add special characters (!, @, #, $, etc.)")
        
        # Deductions for common patterns
        common_patterns = [
            "123", "abc", "qwerty", "password", "admin", "welcome", "login", "letmein"
        ]
        lower_password = password.lower()
        for pattern in common_patterns:
            if pattern in lower_password:
                score -= 0.5
                feedback.append(f"❌ Avoid common pattern: '{pattern}'")
                break
        
        # Calculate percentage for progress bar
        percentage = (score / max_score) * 100
        
        # Determine strength
        if percentage <= 20:
            strength = "Very Weak"
        elif percentage <= 40:
            strength = "Weak"
        elif percentage <= 60:
            strength = "Moderate"
        elif percentage <= 80:
            strength = "Strong"
        else:
            strength = "Very Strong"
        
        return strength, percentage, feedback
    
    def generate_password(self):
        # Check if at least one character set is selected
        if not (self.upper_var.get() or self.lower_var.get() or 
                self.digits_var.get() or self.special_var.get()):
            messagebox.showwarning("Selection Error", 
                                  "Please select at least one character type")
            return
            
        length = self.length_var.get()
        characters = ""
        
        if self.upper_var.get():
            characters += string.ascii_uppercase
        if self.lower_var.get():
            characters += string.ascii_lowercase
        if self.digits_var.get():
            characters += string.digits
        if self.special_var.get():
            characters += "!@#$%^&*()_-+=[]{}|;:,.<>?"
        
        # Generate password
        password = ''.join(random.choice(characters) for _ in range(length))
        self.generated_password.set(password)
        
        # Show strength of generated password
        strength, _, _ = self.check_password_strength(password)
        colors = {
            "Very Weak": "#ff0000",
            "Weak": "#ff5500",
            "Moderate": "#ffaa00",
            "Strong": "#55aa00",
            "Very Strong": "#00aa00"
        }
        self.gen_strength_label.config(text=strength, foreground=colors.get(strength, "black"))
    
    def update_suggested_passwords(self):
        # Generate 3 strong password suggestions
        for i in range(3):
            length = random.randint(12, 16)
            # Always include all character types for suggestions
            characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
            password = ''.join(random.choice(characters) for _ in range(length))
            self.suggested_passwords[i].set(password)
    
    def copy_to_clipboard(self):
        password = self.generated_password.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Copy Error", "No password to copy")
    
    def copy_suggested(self, var):
        password = var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Suggested password copied to clipboard!")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordTool()
    app.run()