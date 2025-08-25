import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import string

class PasswordEnhancer:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Enhancer Pro")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#34495e")
        style.configure("TLabel", background="#34495e", foreground="#ecf0f1", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10), background="#3498db")
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground="#3498db")
        style.configure("Status.TLabel", font=("Arial", 9), foreground="#bdc3c7")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header = ttk.Label(main_frame, text="🔒 Password Enhancer Pro", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Password input
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        input_label = ttk.Label(input_frame, text="Enter your password:")
        input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(input_frame, textvariable=self.password_var, width=30, show="•", font=("Arial", 11))
        password_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        password_entry.focus()
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Enhancement Options", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Minimum length option
        length_label = ttk.Label(options_frame, text="Minimum length:")
        length_label.grid(row=0, column=0, sticky=tk.W)
        
        self.length_var = tk.IntVar(value=8)
        length_spinbox = ttk.Spinbox(options_frame, from_=6, to=20, width=5, textvariable=self.length_var)
        length_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Character types option
        self.use_letters = tk.BooleanVar(value=True)
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Include letters", variable=self.use_letters).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Checkbutton(options_frame, text="Include numbers", variable=self.use_numbers).grid(row=1, column=1, sticky=tk.W, pady=(5, 0), padx=(10, 0))
        ttk.Checkbutton(options_frame, text="Include symbols", variable=self.use_symbols).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=(10, 15))
        
        enhance_btn = ttk.Button(buttons_frame, text="Enhance Password", command=self.enhance_password)
        enhance_btn.grid(row=0, column=0, padx=(0, 10))
        
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_all)
        clear_btn.grid(row=0, column=1)
        
        # Result area
        result_frame = ttk.LabelFrame(main_frame, text="Enhancement Process", padding="10")
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.result_text = tk.Text(result_frame, height=12, width=60, state=tk.DISABLED, 
                                  bg="#2c3e50", fg="#ecf0f1", font=("Consolas", 10), relief=tk.FLAT)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to enhance your password")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", 
                              relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def get_character_set(self):
        """Generate character set based on user selection"""
        chars = ""
        if self.use_letters.get():
            chars += string.ascii_letters  # a-z and A-Z
        if self.use_numbers.get():
            chars += string.digits  # 0-9
        if self.use_symbols.get():
            chars += "!@#$%^&*()_-+=[]{}|;:,.<>?/"  # Special symbols
        
        # If no character type is selected, default to all
        if not chars:
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=[]{}|;:,.<>?"
            
        return chars
    
    def enhance_password(self):
        password = self.password_var.get().strip()
        min_length = self.length_var.get()
        
        if not password:
            messagebox.showwarning("Input Error", "Please enter a password first.")
            return
        
        # Clear previous result
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # Display original password
        self.result_text.insert(tk.END, f"Original password: {password}\n")
        self.result_text.insert(tk.END, f"Minimum length: {min_length} characters\n")
        self.result_text.insert(tk.END, "-" * 50 + "\n\n")
        self.result_text.see(tk.END)
        self.root.update()
        
        # Enhance password if too short
        if len(password) < min_length:
            self.status_var.set("Enhancing password...")
            chars = self.get_character_set()
            
            # Show what character types are being used
            char_info = "Using: "
            if self.use_letters.get():
                char_info += "letters, "
            if self.use_numbers.get():
                char_info += "numbers, "
            if self.use_symbols.get():
                char_info += "symbols, "
            char_info = char_info.rstrip(", ") + "\n"
            
            self.result_text.insert(tk.END, char_info)
            self.result_text.see(tk.END)
            self.root.update()
            time.sleep(0.5)
            
            while len(password) < min_length:
                random_char = random.choice(chars)
                password += random_char
                
                # Display the enhancement process
                self.result_text.insert(tk.END, f"Added '{random_char}'. Current: {password}\n")
                self.result_text.see(tk.END)
                self.root.update()
                
                time.sleep(0.2)
            
            self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.result_text.insert(tk.END, f"Final enhanced password: {password}\n")
        else:
            self.result_text.insert(tk.END, "Password is already strong! No enhancement needed.")
        
        # Disable text widget for editing
        self.result_text.config(state=tk.DISABLED)
        self.status_var.set("Password enhancement complete")
    
    def clear_all(self):
        """Clear all fields"""
        self.password_var.set("")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.status_var.set("Ready to enhance your password")

def main():
    root = tk.Tk()
    app = PasswordEnhancer(root)
    root.mainloop()

if __name__ == "__main__":
    main()