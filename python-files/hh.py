import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from ttkthemes import ThemedTk
import itertools
import random
import string
from datetime import datetime
import os

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator Pro")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('arc')  # Modern theme
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Password Generator Pro", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Personal information frame
        info_frame = ttk.LabelFrame(main_frame, text="Personal Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Input fields
        ttk.Label(info_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.first_name = ttk.Entry(info_frame, width=30)
        self.first_name.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(info_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.last_name = ttk.Entry(info_frame, width=30)
        self.last_name.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(info_frame, text="Birth Year:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.birth_year = ttk.Entry(info_frame, width=30)
        self.birth_year.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(info_frame, text="Special Word:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.special_word = ttk.Entry(info_frame, width=30)
        self.special_word.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(info_frame, text="Other Special Word:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.other_special = ttk.Entry(info_frame, width=30)
        self.other_special.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Strength level
        strength_frame = ttk.LabelFrame(main_frame, text="Password Strength", padding="10")
        strength_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.strength = tk.StringVar(value="2")
        ttk.Radiobutton(strength_frame, text="Basic (100-500 passwords)", 
                       variable=self.strength, value="1").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(strength_frame, text="Advanced (500-2000 passwords)", 
                       variable=self.strength, value="2").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(strength_frame, text="Extreme (2000-5000+ passwords)", 
                       variable=self.strength, value="3").grid(row=2, column=0, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.generate_btn = ttk.Button(button_frame, text="Generate Passwords", 
                                      command=self.generate_passwords)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="Save to File", 
                                  command=self.save_passwords, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Generated Passwords", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=70, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Store generated passwords
        self.passwords = []
        
    def generate_passwords(self):
        # Get user data
        user_data = {
            'first_name': self.first_name.get().strip(),
            'last_name': self.last_name.get().strip(),
            'birth_year': self.birth_year.get().strip(),
            'special_word': self.special_word.get().strip(),
            'other_special': self.other_special.get().strip(),
            'strength': self.strength.get()
        }
        
        # Validate input
        if not any([user_data['first_name'], user_data['last_name'], 
                   user_data['special_word'], user_data['other_special']]):
            messagebox.showerror("Input Error", "Please enter at least one personal information field.")
            return
            
        # Generate passwords (using the same functions from the console version)
        try:
            self.passwords = self._generate_passwords(user_data)
            
            # Display sample in results area
            self.results_text.delete(1.0, tk.END)
            sample_size = min(50, len(self.passwords))
            sample = random.sample(self.passwords, sample_size)
            
            self.results_text.insert(tk.END, f"Generated {len(self.passwords):,} passwords!\n\n")
            self.results_text.insert(tk.END, f"Sample of {sample_size} passwords:\n")
            self.results_text.insert(tk.END, "="*50 + "\n")
            
            for i, pwd in enumerate(sample, 1):
                self.results_text.insert(tk.END, f"{i:2d}. {pwd}\n")
                
            self.save_btn.config(state=tk.NORMAL)
            self.status.config(text=f"Generated {len(self.passwords):,} passwords successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status.config(text="Error generating passwords")
    
    def _generate_passwords(self, data):
        # This would be the same generate_passwords function from your console version
        # Implementation omitted for brevity
        pass
        
    def save_passwords(self):
        if not self.passwords:
            messagebox.showwarning("No Passwords", "No passwords to save. Generate passwords first.")
            return
            
        # Save to file (using the same function from your console version)
        try:
            user_data = {
                'first_name': self.first_name.get().strip(),
                'last_name': self.last_name.get().strip(),
                'birth_year': self.birth_year.get().strip(),
                'special_word': self.special_word.get().strip(),
                'other_special': self.other_special.get().strip()
            }
            
            filename = self._save_passwords(self.passwords, user_data)
            messagebox.showinfo("Success", f"Passwords saved to:\n{filename}")
            self.status.config(text=f"Passwords saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save passwords: {str(e)}")
            self.status.config(text="Error saving passwords")
    
    def _save_passwords(self, passwords, user_data):
        # This would be the same save_passwords function from your console version
        # Implementation omitted for brevity
        pass

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Using a modern theme
    app = PasswordGeneratorApp(root)
    root.mainloop()