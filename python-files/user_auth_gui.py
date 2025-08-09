# user_auth_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import hashlib
import threading
import re

# MongoDB connection
MONGO_URI = "mongodb+srv://aparna02081212:1ZrIzqriY3aotFQK@imageencryptcluster.yzxfdfw.mongodb.net/?retryWrites=true&w=majority&appName=ImageEncryptCluster"

class UserAuthWindow:
    def __init__(self, parent, success_callback):
        self.parent = parent
        self.success_callback = success_callback
        
        # Create auth window
        self.window = tk.Toplevel(parent)
        self.window.title("🔐 User Authentication")
        self.window.geometry("500x650")
        self.window.configure(bg='#1e1e2e')
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # MongoDB connection
        self.client = None
        self.db = None
        self.users_col = None
        
        # Setup styles
        self.setup_styles()
        
        # Create interface
        self.create_interface()
        
        # Connect to database
        self.connect_to_database()
        
    def center_window(self):
        """Center the authentication window on screen"""
        self.window.update_idletasks()
        width = 500
        height = 650
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure('Auth.TButton',
                       background='#7c3aed',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12),
                       relief='flat')
        style.map('Auth.TButton',
                 background=[('active', '#8b5cf6'),
                            ('pressed', '#6d28d9')])
        
        # Register button style (different color to make it stand out)
        style.configure('Register.TButton',
                       background='#10b981',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12),
                       relief='flat')
        style.map('Register.TButton',
                 background=[('active', '#34d399'),
                            ('pressed', '#059669')])
        
        style.configure('Secondary.TButton',
                       background='#6b7280',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))
        style.map('Secondary.TButton',
                 background=[('active', '#9ca3af'),
                            ('pressed', '#4b5563')])
        
        # Entry styles
        style.configure('Auth.TEntry',
                       fieldbackground='#374151',
                       foreground='white',
                       borderwidth=2,
                       insertcolor='white',
                       padding=(10, 8))
        
        # Label styles
        style.configure('AuthTitle.TLabel',
                       background='#1e1e2e',
                       foreground='#a855f7',
                       font=('Helvetica', 24, 'bold'))
        
        style.configure('AuthSubtitle.TLabel',
                       background='#1e1e2e',
                       foreground='#d1d5db',
                       font=('Helvetica', 14))
        
        style.configure('AuthLabel.TLabel',
                       background='#1e1e2e',
                       foreground='#f3f4f6',
                       font=('Helvetica', 11))
        
    def create_interface(self):
        """Create the authentication interface"""
        # Main container
        main_frame = tk.Frame(self.window, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔐 Image Encryption", 
                               style='AuthTitle.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Secure Authentication Required", 
                                  style='AuthSubtitle.TLabel')
        subtitle_label.pack(pady=(0, 40))
        
        # Tab-like interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Login frame
        self.login_frame = tk.Frame(self.notebook, bg='#1e1e2e')
        self.notebook.add(self.login_frame, text="  🔓 Login  ")
        
        # Register frame
        self.register_frame = tk.Frame(self.notebook, bg='#1e1e2e')
        self.notebook.add(self.register_frame, text="  📝 Register  ")
        
        # Create login interface
        self.create_login_interface()
        
        # Create register interface
        self.create_register_interface()
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", 
                                     style='AuthLabel.TLabel')
        self.status_label.pack(pady=(20, 0))
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        
        if "Login" in tab_text:
            self.window.after(100, lambda: self.login_username.focus())
        elif "Register" in tab_text:
            self.window.after(100, lambda: self.register_username.focus())
        
    def create_login_interface(self):
        """Create login interface"""
        # Login form container
        login_container = tk.Frame(self.login_frame, bg='#1e1e2e')
        login_container.pack(fill='both', expand=True, padx=20, pady=30)
        
        # Welcome text
        welcome_label = ttk.Label(login_container, text="Welcome Back!", 
                                 style='AuthSubtitle.TLabel')
        welcome_label.pack(pady=(0, 30))
        
        # Username field
        ttk.Label(login_container, text="Username:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.login_username = ttk.Entry(login_container, style='Auth.TEntry', font=('Helvetica', 12))
        self.login_username.pack(fill='x', pady=(0, 20))
        
        # Password field
        ttk.Label(login_container, text="Password:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.login_password = ttk.Entry(login_container, show="*", style='Auth.TEntry', font=('Helvetica', 12))
        self.login_password.pack(fill='x', pady=(0, 30))
        
        # Login button
        login_btn = ttk.Button(login_container, text="🔓 Sign In", 
                              command=self.handle_login, style='Auth.TButton')
        login_btn.pack(fill='x', pady=(0, 20))
        
        # Register link
        register_link = tk.Label(login_container, text="Don't have an account? Register here", 
                               bg='#1e1e2e', fg='#8b5cf6', font=('Helvetica', 10, 'underline'),
                               cursor='hand2')
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.notebook.select(1))
        
        # Bind Enter key
        self.login_username.bind('<Return>', lambda e: self.login_password.focus())
        self.login_password.bind('<Return>', lambda e: self.handle_login())
        
    def create_register_interface(self):
        """Create registration interface"""
        # Register form container
        register_container = tk.Frame(self.register_frame, bg='#1e1e2e')
        register_container.pack(fill='both', expand=True, padx=20, pady=20)  # Reduced top padding
        
        # Welcome text
        welcome_label = ttk.Label(register_container, text="Create New Account", 
                                 style='AuthSubtitle.TLabel')
        welcome_label.pack(pady=(0, 15))  # Reduced padding
        
        # Username field
        ttk.Label(register_container, text="Username:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.register_username = ttk.Entry(register_container, style='Auth.TEntry', font=('Helvetica', 12))
        self.register_username.pack(fill='x', pady=(0, 12))  # Reduced padding
        
        # Email field
        ttk.Label(register_container, text="Email:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.register_email = ttk.Entry(register_container, style='Auth.TEntry', font=('Helvetica', 12))
        self.register_email.pack(fill='x', pady=(0, 12))  # Reduced padding
        
        # Password field
        ttk.Label(register_container, text="Password:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.register_password = ttk.Entry(register_container, show="*", style='Auth.TEntry', font=('Helvetica', 12))
        self.register_password.pack(fill='x', pady=(0, 12))  # Reduced padding
        
        # Confirm password field
        ttk.Label(register_container, text="Confirm Password:", style='AuthLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.register_confirm = ttk.Entry(register_container, show="*", style='Auth.TEntry', font=('Helvetica', 12))
        self.register_confirm.pack(fill='x', pady=(0, 20))  # Reduced padding
        
        # Register button with distinct styling
        register_btn = ttk.Button(register_container, text="📝 Create Account", 
                                 command=self.handle_register, style='Register.TButton')
        register_btn.pack(fill='x', pady=(0, 15))
        
        # Add some debug info to ensure button is visible
        debug_label = tk.Label(register_container, text="↑ Register Button Above ↑", 
                              bg='#1e1e2e', fg='#6b7280', font=('Helvetica', 8))
        debug_label.pack(pady=(0, 10))
        
        # Login link
        login_link = tk.Label(register_container, text="Already have an account? Sign in here", 
                             bg='#1e1e2e', fg='#8b5cf6', font=('Helvetica', 10, 'underline'),
                             cursor='hand2')
        login_link.pack()
        login_link.bind("<Button-1>", lambda e: self.notebook.select(0))
        
        # Bind Enter key for registration fields
        self.register_username.bind('<Return>', lambda e: self.register_email.focus())
        self.register_email.bind('<Return>', lambda e: self.register_password.focus())
        self.register_password.bind('<Return>', lambda e: self.register_confirm.focus())
        self.register_confirm.bind('<Return>', lambda e: self.handle_register())
        
        # Add a test button to verify the register function works
        test_btn = ttk.Button(register_container, text="🧪 Test Register Function", 
                             command=lambda: messagebox.showinfo("Test", "Register function is working!"),
                             style='Secondary.TButton')
        test_btn.pack(fill='x', pady=(10, 0))
        
    def connect_to_database(self):
        """Connect to MongoDB database"""
        def connect():
            try:
                self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                self.db = self.client["image_encryption"]
                self.users_col = self.db["users"]
                # Test connection
                self.client.admin.command('ismaster')
                self.window.after(0, lambda: self.update_status("✅ Connected to database", "success"))
            except Exception as e:
                error_msg = str(e)
                self.window.after(0, lambda: self.update_status(f"❌ Database connection failed: {error_msg}", "error"))
        
        self.update_status("🔄 Connecting to database...", "info")
        threading.Thread(target=connect, daemon=True).start()
        
    def update_status(self, message, status_type="info"):
        """Update status message"""
        colors = {
            "success": "#10b981",
            "error": "#ef4444",
            "info": "#3b82f6"
        }
        
        self.status_label.config(text=message)
        # Update label color based on status type
        style = ttk.Style()
        style.configure('Status.TLabel',
                       background='#1e1e2e',
                       foreground=colors.get(status_type, "#f3f4f6"),
                       font=('Helvetica', 10))
        self.status_label.config(style='Status.TLabel')
        
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def handle_login(self):
        """Handle login process"""
        if self.users_col is None:
            messagebox.showerror("Error", "Database not connected!")
            return
            
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        def login_thread():
            try:
                hashed_pw = self.hash_password(password)
                user = self.users_col.find_one({"username": username, "password_hash": hashed_pw})
                
                if user:
                    user_data = {"username": username, "email": user["email"]}
                    self.window.after(0, lambda: self.on_login_success(user_data))
                else:
                    self.window.after(0, lambda: messagebox.showerror("Error", "Invalid username or password!"))
                    self.window.after(0, lambda: self.update_status("❌ Login failed", "error"))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Error", f"Login failed: {str(e)}"))
                self.window.after(0, lambda: self.update_status("❌ Login failed", "error"))
        
        self.update_status("🔄 Logging in...", "info")
        threading.Thread(target=login_thread, daemon=True).start()
        
    def handle_register(self):
        """Handle registration process"""
        print("Register button clicked!")  # Debug print
        
        if self.users_col is None:
            messagebox.showerror("Error", "Database not connected!")
            return
            
        username = self.register_username.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        
        print(f"Registration data: {username}, {email}, password_length: {len(password)}")  # Debug print
        
        # Validation
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long!")
            return
            
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
            
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return
            
        def register_thread():
            try:
                # Check if username exists
                existing_user = self.users_col.find_one({"username": username})
                if existing_user:
                    self.window.after(0, lambda: messagebox.showerror("Error", "Username already exists!"))
                    self.window.after(0, lambda: self.update_status("❌ Username already exists", "error"))
                    return
                
                # Check if email exists
                existing_email = self.users_col.find_one({"email": email})
                if existing_email:
                    self.window.after(0, lambda: messagebox.showerror("Error", "Email already registered!"))
                    self.window.after(0, lambda: self.update_status("❌ Email already registered", "error"))
                    return
                
                # Create user
                hashed_pw = self.hash_password(password)
                self.users_col.insert_one({
                    "username": username,
                    "password_hash": hashed_pw,
                    "email": email
                })
                
                self.window.after(0, lambda: self.on_register_success(username))
                
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Error", f"Registration failed: {str(e)}"))
                self.window.after(0, lambda: self.update_status("❌ Registration failed", "error"))
        
        self.update_status("🔄 Creating account...", "info")
        threading.Thread(target=register_thread, daemon=True).start()
        
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.update_status(f"✅ Welcome back, {user_data['username']}!", "success")
        self.window.after(1500, lambda: self.close_and_continue(user_data))
        
    def on_register_success(self, username):
        """Handle successful registration"""
        self.update_status(f"✅ Account created successfully!", "success")
        messagebox.showinfo("Success", f"Welcome {username}!\n\nYour account has been created successfully.\nPlease login with your credentials.")
        # Switch to login tab after successful registration
        self.notebook.select(0)
        self.login_username.delete(0, 'end')
        self.login_username.insert(0, username)
        self.login_password.focus()
        
    def close_and_continue(self, user_data):
        """Close auth window and continue to main app"""
        self.window.destroy()
        self.success_callback(user_data)
        
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.window.destroy()
            self.parent.quit()

if __name__ == "__main__":
    # Test the authentication window
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    def on_success(user_data):
        print(f"Authentication successful: {user_data}")
        root.quit()
    
    auth = UserAuthWindow(root, on_success)
    root.mainloop()