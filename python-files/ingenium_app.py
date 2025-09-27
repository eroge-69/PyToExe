# =================================================================================
#  Face Recognition Application with Enhanced Modern UX Design (Version 4.0)
# =================================================================================
#
#  - Features modern Material Design inspired UI
#  - Smooth animations and transitions
#  - User-friendly icons and visual feedback
#  - Improved accessibility and user experience
#  - Professional gradient backgrounds and shadows
#
# =================================================================================

# --- GUI and Threading Imports ---
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import math

# --- NEW Imports for User Management ---
import json
import hashlib
from datetime import datetime
import random
import string

# --- Original Backend Imports ---
import face_recognition
import os
import smtplib
from email.mime.text import MIMEText
import gdown
import shutil

# =================================================================================
# PART 1: USER MANAGEMENT & UTILITIES (Same as original)
# =================================================================================

USER_DATA_FILE = "users.json"

def hash_password(password):
    """Hashes a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_reset_code():
    """Generates a 6-digit random code."""
    return "".join(random.choices(string.digits, k=6))

def load_user_data():
    """Loads user data from the JSON file."""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_user_data(data):
    """Saves user data to the JSON file."""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =================================================================================
# PART 2: ENHANCED UI UTILITIES & ANIMATIONS
# =================================================================================

class AnimatedButton(tk.Button):
    """Custom button with hover animations"""
    def __init__(self, parent, **kwargs):
        self.original_bg = kwargs.get('bg', '#1abc9c')
        self.hover_bg = kwargs.pop('hover_bg', '#16a085')  # Remove hover_bg from kwargs
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(relief='flat', borderwidth=0, cursor='hand2')
        
    def on_enter(self, e):
        self.configure(bg=self.hover_bg)
        
    def on_leave(self, e):
        self.configure(bg=self.original_bg)

class ModernEntry(tk.Entry):
    """Custom entry with modern styling"""
    def __init__(self, parent, placeholder="", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = '#95a5a6'
        self.default_fg_color = kwargs.get('fg', '#2c3e50')
        
        super().__init__(parent, **kwargs)
        self.configure(relief='flat', borderwidth=2, highlightthickness=0)
        
        if placeholder:
            self.put_placeholder()
            
        self.bind('<FocusIn>', self.focus_in)
        self.bind('<FocusOut>', self.focus_out)
        
    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self.configure(fg=self.placeholder_color)
        
    def focus_in(self, *args):
        if self.get() == self.placeholder:
            self.delete('0', 'end')
            self.configure(fg=self.default_fg_color)
            
    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()

def create_gradient_frame(parent, color1="#1abc9c", color2="#3498db", width=400, height=300):
    """Creates a frame with gradient background"""
    frame = tk.Frame(parent, width=width, height=height)
    canvas = tk.Canvas(frame, width=width, height=height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Create gradient
    for i in range(height):
        ratio = i / height
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)
    
    return frame, canvas

# =================================================================================
# PART 3: BACKEND LOGIC (Same as original)
# =================================================================================

def download_images_from_gdrive(folder_url, output_path, log_callback):
    log_callback(f"🔽 Downloading images from Google Drive folder...")
    try:
        os.makedirs(output_path, exist_ok=True)
        gdown.download_folder(folder_url, output=output_path, quiet=False, use_cookies=False)
        log_callback(f"✅ Successfully downloaded images to {output_path}")
        return True
    except Exception as e:
        log_callback(f"❌ Error downloading from Google Drive: {e}")
        return False

def send_email(subject, body, sender, receiver, password, log_callback=print):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, receiver, msg.as_string())
        if log_callback:
            log_callback("📧 Email sent successfully!")
        return "Email sent successfully."
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Error sending email: {e}")
        return f"Error sending email: {e}"

def write_output_file(filepath, content, log_callback):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        log_callback(f"💾 Result written to {filepath}")
    except Exception as e:
        log_callback(f"❌ Error writing to output file: {e}")

def load_target_encodings(folder_path, log_callback):
    target_encodings = []
    log_callback(f"🔍 Loading target faces from {folder_path}...")
    if not os.path.isdir(folder_path):
        log_callback(f"❌ Error: Target images folder not found at {folder_path}")
        return []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    target_encodings.append(encodings[0])
                    log_callback(f"✅ Processed {filename}")
            except Exception as e:
                log_callback(f"⚠️ Warning: Could not process target image {filename}. Error: {e}")
    return target_encodings

def clear_folder(folder_path, log_callback):
    log_callback(f"🧹 Clearing the contents of {folder_path}...")
    if os.path.isdir(folder_path):
        try:
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
            log_callback(f"✅ Folder '{folder_path}' cleared successfully.")
        except Exception as e:
            log_callback(f"❌ Error clearing folder {folder_path}: {e}")

def face_recognition_main_logic(config, log_callback):
    INPUT_IMAGES_FOLDER = os.path.join(os.path.expanduser('~'), "face_rec_temp_downloads")
    try:
        if not download_images_from_gdrive(config['gdrive_url'], INPUT_IMAGES_FOLDER, log_callback):
            result_message = "Failed to download images from Google Drive."
            write_output_file(config['output_filepath'], result_message, log_callback)
            return

        target_face_encodings = load_target_encodings(config['target_folder'], log_callback)
        if not target_face_encodings:
            result_message = f"Error: No faces could be encoded from the target folder."
            write_output_file(config['output_filepath'], result_message, log_callback)
            return

        log_callback(f"🎯 Successfully loaded {len(target_face_encodings)} face encodings.")
        target_person_detected = False
        detection_details = []

        if not os.path.isdir(INPUT_IMAGES_FOLDER):
            result_message = f"Error: Input images folder not found."
            write_output_file(config['output_filepath'], result_message, log_callback)
            return

        log_callback(f"🔍 Scanning images in: {INPUT_IMAGES_FOLDER}")
        for filename in os.listdir(INPUT_IMAGES_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(INPUT_IMAGES_FOLDER, filename)
                log_callback(f"📷 Processing {filename}...")
                try:
                    unknown_image = face_recognition.load_image_file(image_path)
                    unknown_encodings = face_recognition.face_encodings(unknown_image)
                    if unknown_encodings:
                        image_had_match = False
                        for unknown_encoding in unknown_encodings:
                            if True in face_recognition.compare_faces(target_face_encodings, unknown_encoding):
                                target_person_detected = True
                                image_had_match = True
                                log_callback(f"🎉 MATCH FOUND in {filename}!")
                                break
                        detection_details.append(f"Target person {'✅ DETECTED' if image_had_match else '❌ NOT detected'} in: {filename}")
                    else:
                        detection_details.append(f"👤 No faces found in: {filename}")
                except Exception as e:
                    log_callback(f"⚠️ Could not process {filename}. Error: {e}")

        if target_person_detected:
            final_message = "🎉 Target person was detected.\n\n" + "\n".join(detection_details)
            log_callback("\n🎉 Target person was found. No email will be sent.")
        else:
            final_message = "❌ Target person was not detected.\n\n" + "\n".join(detection_details)
            log_callback("\n❌ Target person was NOT found. Sending email notification...")
            email_status = send_email("Face Rec Update: Target Not Found", "Target not found in scanned images.", config['sender_email'], config['receiver_email'], config['sender_password'], log_callback)
            final_message += f"\n\n📧 Email Notification Status: {email_status}"
        write_output_file(config['output_filepath'], final_message, log_callback)
    finally:
        clear_folder(INPUT_IMAGES_FOLDER, log_callback)
        log_callback("\n✅ Process finished.")

# =================================================================================
# PART 4: ENHANCED GRAPHICAL USER INTERFACE
# =================================================================================

class FaceRecApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AMU Face Recognition Suite")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        self.configure(bg="#ecf0f1")
        self.current_user = None

        # Load app icon if available
        try:
            self.iconphoto(True, tk.PhotoImage(file="app_icon.png"))
        except:
            pass

        # Create main container with padding
        self.main_container = tk.Frame(self, bg="#ecf0f1")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        container = tk.Frame(self.main_container, bg="#ffffff", relief="raised", borderwidth=2)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, SignUpPage, ForgotPasswordPage, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        # Main container
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True)

        # Left side - Welcome panel with gradient
        left_panel, left_canvas = create_gradient_frame(main_container, "#667eea", "#764ba2", 500, 800)
        left_panel.pack(side="left", fill="y")

        # Add logo/icon to left panel
        try:
            logo_img = Image.open("logo.png").resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            left_canvas.create_image(250, 150, image=self.logo_photo)
        except:
            # Create a simple circular logo if image not found
            left_canvas.create_oval(190, 90, 310, 210, fill="#ffffff", width=3, outline="#ffffff")
            left_canvas.create_text(250, 150, text="AMU", fill="#667eea", font=("Helvetica", 32, "bold"))

        # Welcome text on gradient
        left_canvas.create_text(250, 280, text="AMU Face Recognition", fill="#ffffff", 
                               font=("Helvetica", 28, "bold"), anchor="center")
        left_canvas.create_text(250, 320, text="Intelligent Security Suite", fill="#ffffff", 
                               font=("Helvetica", 14), anchor="center")
        left_canvas.create_text(250, 380, text="Secure • Reliable • Fast", fill="#ffffff", 
                               font=("Helvetica", 12), anchor="center")

        # Add floating icons/decorations
        self.add_floating_elements(left_canvas)

        # Right side - Login form
        right_panel = tk.Frame(main_container, bg="#ffffff")
        right_panel.pack(side="right", fill="both", expand=True, padx=40)

        # Center the login form
        login_container = tk.Frame(right_panel, bg="#ffffff")
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = tk.Frame(login_container, bg="#ffffff")
        header_frame.pack(pady=30)

        # Login icon
        try:
            login_icon = Image.open("login_icon.png").resize((64, 64), Image.Resampling.LANCZOS)
            self.login_icon_photo = ImageTk.PhotoImage(login_icon)
            tk.Label(header_frame, image=self.login_icon_photo, bg="#ffffff").pack(pady=(0, 10))
        except:
            pass

        tk.Label(header_frame, text="Welcome Back!", font=("Helvetica", 24, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack()
        tk.Label(header_frame, text="Please sign in to your account", font=("Helvetica", 12), 
                fg="#7f8c8d", bg="#ffffff").pack(pady=(5, 0))

        # Form fields
        form_frame = tk.Frame(login_container, bg="#ffffff")
        form_frame.pack(pady=20)

        # Username field
        tk.Label(form_frame, text="Username", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_user = ModernEntry(form_frame, placeholder="Enter your username", 
                                     font=("Helvetica", 12), width=35, bg="#f8f9fa", 
                                     fg="#2c3e50", relief="solid", bd=1)
        self.entry_user.pack(pady=(0, 15), ipady=8)

        # Password field
        tk.Label(form_frame, text="Password", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_pass = ModernEntry(form_frame, placeholder="Enter your password", 
                                     show="*", font=("Helvetica", 12), width=35, 
                                     bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1)
        self.entry_pass.pack(pady=(0, 20), ipady=8)

        # Login button
        login_btn = AnimatedButton(form_frame, text="SIGN IN", font=("Helvetica", 12, "bold"), 
                                  bg="#667eea", fg="white", hover_bg="#5a67d8", width=30, 
                                  command=self.login_user)
        login_btn.pack(pady=10, ipady=10)

        # Links
        links_frame = tk.Frame(form_frame, bg="#ffffff")
        links_frame.pack(pady=15)

        forgot_btn = tk.Button(links_frame, text="Forgot Password?", font=("Helvetica", 10), 
                              fg="#667eea", bg="#ffffff", borderwidth=0, cursor="hand2",
                              command=lambda: controller.show_frame("ForgotPasswordPage"))
        forgot_btn.pack()

        # Divider
        divider_frame = tk.Frame(form_frame, bg="#ffffff")
        divider_frame.pack(pady=15, fill="x")
        tk.Frame(divider_frame, height=1, bg="#dee2e6").pack(fill="x", pady=10)
        tk.Label(divider_frame, text="Don't have an account?", font=("Helvetica", 10), 
                fg="#6c757d", bg="#ffffff").pack()

        # Sign up button
        signup_btn = AnimatedButton(form_frame, text="CREATE ACCOUNT", 
                                   font=("Helvetica", 11, "bold"), bg="#28a745", 
                                   fg="white", hover_bg="#218838", width=30,
                                   command=lambda: controller.show_frame("SignUpPage"))
        signup_btn.pack(pady=10, ipady=8)

    def add_floating_elements(self, canvas):
        """Add decorative floating elements to the gradient background"""
        # Add some geometric shapes for visual appeal
        canvas.create_oval(80, 450, 120, 490, fill="", outline="#ffffff", width=2)
        canvas.create_rectangle(350, 500, 380, 530, fill="", outline="#ffffff", width=2)
        canvas.create_oval(400, 200, 430, 230, fill="#ffffff", outline="")

    def login_user(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        # Remove placeholder text if present
        if username == "Enter your username":
            username = ""
        if password == "Enter your password":
            password = ""
            
        users = load_user_data()

        if username in users and users[username]['password_hash'] == hash_password(password):
            self.controller.current_user = username

            # Update last login timestamp
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            users[username]['last_login'] = now
            save_user_data(users)

            # Update the welcome message on the main page before showing it
            self.controller.frames["MainPage"].update_welcome_message()
            self.show_success_animation()
        else:
            self.show_error_message("Invalid username or password")

    def show_success_animation(self):
        """Show success message and transition to main page"""
        success_label = tk.Label(self, text="✅ Login Successful!", 
                                font=("Helvetica", 14, "bold"), fg="#28a745", bg="#ffffff")
        success_label.place(relx=0.75, rely=0.1, anchor="center")
        
        def transition():
            success_label.destroy()
            self.controller.show_frame("MainPage")
        
        self.after(1500, transition)

    def show_error_message(self, message):
        """Show error message with animation"""
        error_label = tk.Label(self, text=f"❌ {message}", 
                              font=("Helvetica", 12, "bold"), fg="#dc3545", bg="#ffffff")
        error_label.place(relx=0.75, rely=0.1, anchor="center")
        
        def remove_error():
            error_label.destroy()
        
        self.after(3000, remove_error)

class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        # Main container
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True)

        # Create signup form in center
        signup_container = tk.Frame(main_container, bg="#ffffff")
        signup_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header with icon
        header_frame = tk.Frame(signup_container, bg="#ffffff")
        header_frame.pack(pady=30)

        try:
            signup_icon = Image.open("signup_icon.png").resize((64, 64), Image.Resampling.LANCZOS)
            self.signup_icon_photo = ImageTk.PhotoImage(signup_icon)
            tk.Label(header_frame, image=self.signup_icon_photo, bg="#ffffff").pack(pady=(0, 10))
        except:
            pass

        tk.Label(header_frame, text="Create Account", font=("Helvetica", 28, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack()
        tk.Label(header_frame, text="Join our secure face recognition platform", 
                font=("Helvetica", 12), fg="#7f8c8d", bg="#ffffff").pack(pady=(5, 0))

        # Form
        form_frame = tk.Frame(signup_container, bg="#ffffff")
        form_frame.pack(pady=20)

        # Username field
        tk.Label(form_frame, text="Username", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_user = ModernEntry(form_frame, placeholder="Choose a username", 
                                     font=("Helvetica", 12), width=35, bg="#f8f9fa", 
                                     fg="#2c3e50", relief="solid", bd=1)
        self.entry_user.pack(pady=(0, 15), ipady=8)

        # Email field
        tk.Label(form_frame, text="Email Address", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_email = ModernEntry(form_frame, placeholder="Enter your email", 
                                      font=("Helvetica", 12), width=35, bg="#f8f9fa", 
                                      fg="#2c3e50", relief="solid", bd=1)
        self.entry_email.pack(pady=(0, 15), ipady=8)

        # Password field
        tk.Label(form_frame, text="Password", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_pass = ModernEntry(form_frame, placeholder="Create a password", 
                                     show="*", font=("Helvetica", 12), width=35, 
                                     bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1)
        self.entry_pass.pack(pady=(0, 20), ipady=8)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.pack(pady=20)

        register_btn = AnimatedButton(btn_frame, text="CREATE ACCOUNT", 
                                     font=("Helvetica", 12, "bold"), bg="#28a745", 
                                     fg="white", hover_bg="#218838", width=25,
                                     command=self.register_user)
        register_btn.pack(pady=5, ipady=10)

        back_btn = AnimatedButton(btn_frame, text="BACK TO LOGIN", 
                                 font=("Helvetica", 11), bg="#6c757d", 
                                 fg="white", hover_bg="#5a6268", width=25,
                                 command=lambda: controller.show_frame("LoginPage"))
        back_btn.pack(pady=5, ipady=8)

    def register_user(self):
        username = self.entry_user.get()
        email = self.entry_email.get()
        password = self.entry_pass.get()
        
        # Remove placeholder text if present
        if username == "Choose a username":
            username = ""
        if email == "Enter your email":
            email = ""
        if password == "Create a password":
            password = ""
            
        users = load_user_data()

        if not username or not password or not email:
            self.show_error_message("All fields are required.")
            return
        if username in users:
            self.show_error_message("Username already exists.")
            return

        users[username] = {
            'email': email,
            'password_hash': hash_password(password),
            'last_login': None,
            'reset_code': None
        }
        save_user_data(users)
        self.show_success_message("Account created successfully!")
        self.controller.show_frame("LoginPage")

    def show_error_message(self, message):
        error_label = tk.Label(self, text=f"❌ {message}", 
                              font=("Helvetica", 12, "bold"), fg="#dc3545", bg="#ffffff")
        error_label.place(relx=0.5, rely=0.1, anchor="center")
        self.after(3000, error_label.destroy)

    def show_success_message(self, message):
        success_label = tk.Label(self, text=f"✅ {message}", 
                                font=("Helvetica", 12, "bold"), fg="#28a745", bg="#ffffff")
        success_label.place(relx=0.5, rely=0.1, anchor="center")
        self.after(2000, success_label.destroy)

class ForgotPasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.users = load_user_data()
        self.username_to_reset = None

        # Main container
        self.main_container = tk.Frame(self, bg="#ffffff")
        self.main_container.pack(fill="both", expand=True)

        self.create_email_widgets()

    def create_email_widgets(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Center container
        center_container = tk.Frame(self.main_container, bg="#ffffff")
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = tk.Frame(center_container, bg="#ffffff")
        header_frame.pack(pady=30)

        try:
            forgot_icon = Image.open("forgot_password_icon.png").resize((64, 64), Image.Resampling.LANCZOS)
            self.forgot_icon_photo = ImageTk.PhotoImage(forgot_icon)
            tk.Label(header_frame, image=self.forgot_icon_photo, bg="#ffffff").pack(pady=(0, 10))
        except:
            pass

        tk.Label(header_frame, text="Forgot Password?", font=("Helvetica", 24, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack()
        tk.Label(header_frame, text="Enter your email to receive a reset code", 
                font=("Helvetica", 12), fg="#7f8c8d", bg="#ffffff").pack(pady=(5, 0))

        # Form
        form_frame = tk.Frame(center_container, bg="#ffffff")
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Email Address", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_email = ModernEntry(form_frame, placeholder="Enter your email", 
                                      font=("Helvetica", 12), width=35, bg="#f8f9fa", 
                                      fg="#2c3e50", relief="solid", bd=1)
        self.entry_email.pack(pady=(0, 20), ipady=8)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.pack(pady=20)

        send_btn = AnimatedButton(btn_frame, text="SEND RESET CODE", 
                                 font=("Helvetica", 12, "bold"), bg="#007bff", 
                                 fg="white", hover_bg="#0056b3", width=25,
                                 command=self.send_reset_code)
        send_btn.pack(pady=5, ipady=10)

        back_btn = AnimatedButton(btn_frame, text="BACK TO LOGIN", 
                                 font=("Helvetica", 11), bg="#6c757d", 
                                 fg="white", hover_bg="#5a6268", width=25,
                                 command=lambda: self.controller.show_frame("LoginPage"))
        back_btn.pack(pady=5, ipady=8)

    def create_reset_widgets(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Center container
        center_container = tk.Frame(self.main_container, bg="#ffffff")
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = tk.Frame(center_container, bg="#ffffff")
        header_frame.pack(pady=30)

        try:
            reset_icon = Image.open("reset_password_icon.png").resize((64, 64), Image.Resampling.LANCZOS)
            self.reset_icon_photo = ImageTk.PhotoImage(reset_icon)
            tk.Label(header_frame, image=self.reset_icon_photo, bg="#ffffff").pack(pady=(0, 10))
        except:
            pass

        tk.Label(header_frame, text="Reset Password", font=("Helvetica", 24, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack()
        tk.Label(header_frame, text="Enter the code sent to your email and your new password", 
                font=("Helvetica", 12), fg="#7f8c8d", bg="#ffffff").pack(pady=(5, 0))

        # Form
        form_frame = tk.Frame(center_container, bg="#ffffff")
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Reset Code", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_code = ModernEntry(form_frame, placeholder="Enter 6-digit code", 
                                     font=("Helvetica", 12), width=35, bg="#f8f9fa", 
                                     fg="#2c3e50", relief="solid", bd=1)
        self.entry_code.pack(pady=(0, 15), ipady=8)

        tk.Label(form_frame, text="New Password", font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        self.entry_new_pass = ModernEntry(form_frame, placeholder="Enter new password", 
                                         show="*", font=("Helvetica", 12), width=35, 
                                         bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1)
        self.entry_new_pass.pack(pady=(0, 20), ipady=8)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.pack(pady=20)

        reset_btn = AnimatedButton(btn_frame, text="RESET PASSWORD", 
                                  font=("Helvetica", 12, "bold"), bg="#28a745", 
                                  fg="white", hover_bg="#218838", width=25,
                                  command=self.reset_password)
        reset_btn.pack(pady=5, ipady=10)

        back_btn = AnimatedButton(btn_frame, text="BACK TO LOGIN", 
                                 font=("Helvetica", 11), bg="#6c757d", 
                                 fg="white", hover_bg="#5a6268", width=25,
                                 command=lambda: self.controller.show_frame("LoginPage"))
        back_btn.pack(pady=5, ipady=8)

    def send_reset_code(self):
        email = self.entry_email.get()
        if email == "Enter your email":
            email = ""
            
        self.users = load_user_data()

        for username, data in self.users.items():
            if data.get('email') == email:
                self.username_to_reset = username
                reset_code = generate_reset_code()
                self.users[username]['reset_code'] = reset_code
                save_user_data(self.users)

                # Email configuration notice
                sender_email = "your_email@gmail.com"
                sender_password = "your_app_password"

                if sender_email == "your_email@gmail.com" or sender_password == "your_app_password":
                    self.show_error_message("Email configuration required. Please configure sender email in the code.")
                    return

                email_status = send_email("Password Reset Code", f"Your password reset code is: {reset_code}", 
                                        sender_email, email, sender_password, log_callback=None)
                if "Error" in email_status:
                    self.show_error_message(f"Could not send email. {email_status}")
                else:
                    self.show_success_message("Reset code sent to your email!")
                    self.create_reset_widgets()
                return

        self.show_error_message("Email not found in our database.")

    def reset_password(self):
        code = self.entry_code.get()
        new_password = self.entry_new_pass.get()

        if code == "Enter 6-digit code":
            code = ""
        if new_password == "Enter new password":
            new_password = ""

        if not new_password:
            self.show_error_message("Password cannot be empty.")
            return

        if self.users[self.username_to_reset]['reset_code'] == code:
            self.users[self.username_to_reset]['password_hash'] = hash_password(new_password)
            self.users[self.username_to_reset]['reset_code'] = None
            save_user_data(self.users)
            self.show_success_message("Password reset successful!")
            self.create_email_widgets()
            self.controller.show_frame("LoginPage")
        else:
            self.show_error_message("Invalid reset code.")

    def show_error_message(self, message):
        error_label = tk.Label(self, text=f"❌ {message}", 
                              font=("Helvetica", 12, "bold"), fg="#dc3545", bg="#ffffff")
        error_label.place(relx=0.5, rely=0.1, anchor="center")
        self.after(3000, error_label.destroy)

    def show_success_message(self, message):
        success_label = tk.Label(self, text=f"✅ {message}", 
                                font=("Helvetica", 12, "bold"), fg="#28a745", bg="#ffffff")
        success_label.place(relx=0.5, rely=0.1, anchor="center")
        self.after(2000, success_label.destroy)

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8f9fa")
        self.controller = controller

        # Create header with gradient background
        header_container = tk.Frame(self, bg="#ffffff", relief="raised", borderwidth=1)
        header_container.pack(fill="x", padx=10, pady=(10, 0))

        header_frame, header_canvas = create_gradient_frame(header_container, "#667eea", "#764ba2", 1180, 80)
        header_frame.pack(fill="x")

        # Welcome message - Fixed the bg issue
        self.welcome_label = tk.Label(header_frame, text="", fg="white", 
                                     font=("Helvetica", 14, "bold"))
        self.welcome_label.place(relx=0.02, rely=0.5, anchor="w")
        # Set transparent background after creation
        self.welcome_label.config(bg=header_frame.cget('bg'))

        # Header buttons - Fixed the bg issue
        btn_frame = tk.Frame(header_frame)
        btn_frame.place(relx=0.98, rely=0.5, anchor="e")
        # Set transparent background after creation
        btn_frame.config(bg=header_frame.cget('bg'))

        new_scan_btn = AnimatedButton(btn_frame, text="🔍 New Scan Profile", 
                                     font=("Helvetica", 11, "bold"), bg="#28a745", 
                                     fg="white", hover_bg="#218838",
                                     command=self.open_new_scan_window)
        new_scan_btn.pack(side="right", padx=5)

        logout_btn = AnimatedButton(btn_frame, text="🚪 Logout", 
                                   font=("Helvetica", 10), bg="#dc3545", 
                                   fg="white", hover_bg="#c82333",
                                   command=self.logout_user)
        logout_btn.pack(side="right", padx=5)

        # Main content area
        content_frame = tk.Frame(self, bg="#f8f9fa")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Dashboard cards
        dashboard_frame = tk.Frame(content_frame, bg="#f8f9fa")
        dashboard_frame.pack(fill="x", pady=(0, 10))

        self.create_dashboard_cards(dashboard_frame)

        # Log output area with modern design
        log_container = tk.Frame(content_frame, bg="#ffffff", relief="raised", borderwidth=1)
        log_container.pack(fill="both", expand=True)

        # Log header
        log_header = tk.Frame(log_container, bg="#343a40", height=50)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)

        tk.Label(log_header, text="🔄 Live Process Monitor", font=("Helvetica", 14, "bold"), 
                fg="white", bg="#343a40").place(relx=0.02, rely=0.5, anchor="w")

        # Clear log button
        clear_btn = AnimatedButton(log_header, text="🗑️ Clear Log", 
                                  font=("Helvetica", 9), bg="#6c757d", 
                                  fg="white", hover_bg="#5a6268",
                                  command=self.clear_log)
        clear_btn.place(relx=0.98, rely=0.5, anchor="e")

        # Log text area
        log_text_frame = tk.Frame(log_container, bg="#ffffff")
        log_text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(log_text_frame, height=20, state="disabled", 
                               bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10),
                               insertbackground="#00ff00", selectbackground="#333333")
        self.log_text.pack(side="left", fill="both", expand=True)

        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_text_frame, command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_text['yscrollcommand'] = log_scrollbar.set

        # Configure log text tags for different message types
        self.log_text.tag_configure("success", foreground="#28a745")
        self.log_text.tag_configure("error", foreground="#dc3545")
        self.log_text.tag_configure("warning", foreground="#ffc107")
        self.log_text.tag_configure("info", foreground="#17a2b8")

        self.log_queue = queue.Queue()
        self.after(100, self.process_log_queue)

    def create_dashboard_cards(self, parent):
        """Create dashboard cards showing stats"""
        cards_data = [
            {"title": "Total Scans", "value": "0", "icon": "📊", "color": "#007bff"},
            {"title": "Successful Detections", "value": "0", "icon": "✅", "color": "#28a745"},
            {"title": "Failed Detections", "value": "0", "icon": "❌", "color": "#dc3545"},
            {"title": "Last Scan", "value": "Never", "icon": "🕐", "color": "#6f42c1"}
        ]

        cards_frame = tk.Frame(parent, bg="#f8f9fa")
        cards_frame.pack(fill="x")

        for i, card_data in enumerate(cards_data):
            card = self.create_dashboard_card(cards_frame, card_data)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            cards_frame.grid_columnconfigure(i, weight=1)

    def create_dashboard_card(self, parent, data):
        """Create individual dashboard card"""
        card = tk.Frame(parent, bg="#ffffff", relief="raised", borderwidth=1)
        
        # Card content
        content_frame = tk.Frame(card, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Icon and title
        header_frame = tk.Frame(content_frame, bg="#ffffff")
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=data["icon"], font=("Helvetica", 24), 
                bg="#ffffff").pack(side="left")
        tk.Label(header_frame, text=data["title"], font=("Helvetica", 12, "bold"), 
                fg="#6c757d", bg="#ffffff").pack(side="right")

        # Value
        tk.Label(content_frame, text=data["value"], font=("Helvetica", 20, "bold"), 
                fg=data["color"], bg="#ffffff").pack(anchor="w", pady=(5, 0))

        return card

    def update_welcome_message(self):
        """Updates the header with user info after login."""
        users = load_user_data()
        username = self.controller.current_user
        last_login = users.get(username, {}).get('last_login', 'Never')
        self.welcome_label.config(text=f"👋 Welcome back, {username}  |  Last Login: {last_login}")

    def logout_user(self):
        """Handle user logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.controller.current_user = None
            self.controller.show_frame("LoginPage")

    def clear_log(self):
        """Clear the log output"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def log_message(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state="normal")
                
                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                timestamped_message = f"[{timestamp}] {message}"
                
                # Determine message type and apply appropriate tag
                if "✅" in message or "Success" in message:
                    tag = "success"
                elif "❌" in message or "Error" in message:
                    tag = "error"
                elif "⚠️" in message or "Warning" in message:
                    tag = "warning"
                elif "🔍" in message or "📧" in message or "🎯" in message:
                    tag = "info"
                else:
                    tag = None

                self.log_text.insert(tk.END, timestamped_message + "\n", tag)
                self.log_text.see(tk.END)
                self.log_text.config(state="disabled")
        except queue.Empty:
            self.after(100, self.process_log_queue)

    def open_new_scan_window(self):
        NewScanWindow(self)

    def start_scan_thread(self, config):
        self.clear_log()
        self.log_message("🚀 Initializing new scan process...")
        thread = threading.Thread(target=face_recognition_main_logic, args=(config, self.log_message))
        thread.daemon = True
        thread.start()

class NewScanWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("🔍 Create New Scan Profile")
        self.geometry("650x700")
        self.configure(bg="#f8f9fa")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        # Center the window
        self.center_window()

        # Header with gradient
        header_frame, header_canvas = create_gradient_frame(self, "#667eea", "#764ba2", 650, 80)
        header_frame.pack(fill="x")

        header_canvas.create_text(325, 40, text="🔍 New Scan Profile", fill="white", 
                                 font=("Helvetica", 20, "bold"), anchor="center")

        # Main content
        main_frame = tk.Frame(self, bg="#ffffff", relief="raised", borderwidth=1)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Scrollable content
        canvas = tk.Canvas(main_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_form_sections(scrollable_frame)

        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

    def create_form_sections(self, parent):
        """Create organized form sections"""
        # Target Images Section
        target_section = self.create_section(parent, "🎯 Target Images Configuration", 0)
        self.target_folder_entry = self.create_folder_field(target_section, 
            "Target Images Folder:", "Select folder containing reference images", 0)

        # Google Drive Section  
        gdrive_section = self.create_section(parent, "☁️ Google Drive Configuration", 1)
        self.gdrive_url_entry = self.create_text_field(gdrive_section,
            "Google Drive Folder URL:", "Paste the shareable Google Drive folder URL", 0)

        # Output Section
        output_section = self.create_section(parent, "📁 Output Configuration", 2)
        self.output_folder_entry = self.create_folder_field(output_section,
            "Output Folder:", "Select where to save scan results", 0)

        # Email Section
        email_section = self.create_section(parent, "📧 Email Notification Settings", 3)
        
        self.sender_email_entry = self.create_text_field(email_section,
            "Sender Email (Gmail):", "your_email@gmail.com", 0)
        
        self.receiver_email_entry = self.create_text_field(email_section,
            "Notification Email:", "recipient@example.com", 1)
        
        self.password_entry = self.create_text_field(email_section,
            "Gmail App Password:", "Generated app-specific password", 2, True)

        # Add info text for email setup
        info_frame = tk.Frame(email_section, bg="#ffffff")
        info_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5)
        
        info_text = ("💡 To use email notifications:\n"
                    "1. Enable 2-factor authentication on Gmail\n"
                    "2. Generate an App Password (not your regular password)\n"
                    "3. Use that App Password in the field above")
        
        tk.Label(info_frame, text=info_text, font=("Helvetica", 9), 
                fg="#6c757d", bg="#ffffff", justify="left").pack(anchor="w")

        # Buttons Section
        buttons_frame = tk.Frame(parent, bg="#ffffff")
        buttons_frame.grid(row=4, column=0, sticky="ew", pady=30, padx=20)

        AnimatedButton(buttons_frame, text="🚀 START SCAN", 
                      font=("Helvetica", 14, "bold"), bg="#28a745", 
                      fg="white", hover_bg="#218838", width=20,
                      command=self.save_and_start).pack(side="left", padx=10, ipady=12)

        AnimatedButton(buttons_frame, text="❌ CANCEL", 
                      font=("Helvetica", 12), bg="#6c757d", 
                      fg="white", hover_bg="#5a6268", width=15,
                      command=self.destroy).pack(side="right", padx=10, ipady=10)

    def create_section(self, parent, title, row):
        """Create a section with title and frame"""
        section_frame = tk.LabelFrame(parent, text=title, font=("Helvetica", 12, "bold"),
                                     fg="#2c3e50", bg="#ffffff", padx=15, pady=10)
        section_frame.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        parent.grid_columnconfigure(0, weight=1)
        return section_frame

    def create_folder_field(self, parent, label, placeholder, row):
        """Create folder selection field"""
        tk.Label(parent, text=label, font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").grid(row=row, column=0, sticky="w", pady=(0, 5))
        
        entry_frame = tk.Frame(parent, bg="#ffffff")
        entry_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))
        entry_frame.grid_columnconfigure(0, weight=1)
        
        entry = ModernEntry(entry_frame, placeholder=placeholder, font=("Helvetica", 10), 
                           bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=6)
        
        browse_btn = AnimatedButton(entry_frame, text="📁 Browse", 
                                   font=("Helvetica", 10), bg="#007bff", 
                                   fg="white", hover_bg="#0056b3",
                                   command=lambda: self.browse_folder(entry))
        browse_btn.grid(row=0, column=1, ipady=6)
        
        return entry

    def create_text_field(self, parent, label, placeholder, row, is_password=False):
        """Create text input field"""
        tk.Label(parent, text=label, font=("Helvetica", 11, "bold"), 
                fg="#2c3e50", bg="#ffffff").grid(row=row*2, column=0, sticky="w", pady=(0, 5))
        
        entry = ModernEntry(parent, placeholder=placeholder, font=("Helvetica", 10), 
                           bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1)
        if is_password:
            entry.configure(show="*")
            
        entry.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 10), ipady=6)
        parent.grid_columnconfigure(0, weight=1)
        
        return entry

    def browse_folder(self, entry_widget):
        """Handle folder browsing"""
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_path)

    def save_and_start(self):
        """Validate and start the scan process"""
        # Get values and handle placeholders
        target_folder = self.target_folder_entry.get()
        if target_folder == "Select folder containing reference images":
            target_folder = ""
            
        gdrive_url = self.gdrive_url_entry.get()
        if gdrive_url == "Paste the shareable Google Drive folder URL":
            gdrive_url = ""
            
        output_folder = self.output_folder_entry.get()
        if output_folder == "Select where to save scan results":
            output_folder = ""
            
        sender_email = self.sender_email_entry.get()
        if sender_email == "your_email@gmail.com":
            sender_email = ""
            
        receiver_email = self.receiver_email_entry.get()
        if receiver_email == "recipient@example.com":
            receiver_email = ""
            
        sender_password = self.password_entry.get()
        if sender_password == "Generated app-specific password":
            sender_password = ""

        config = {
            'target_folder': target_folder,
            'gdrive_url': gdrive_url,
            'output_filepath': os.path.join(output_folder, "detection_result.txt") if output_folder else "",
            'sender_email': sender_email,
            'receiver_email': receiver_email,
            'sender_password': sender_password
        }

        # Validation
        if not all(config.values()):
            self.show_error("All fields are required. Please fill in all information.")
            return

        if not os.path.isdir(target_folder):
            self.show_error("Target folder does not exist. Please select a valid folder.")
            return

        if not os.path.isdir(output_folder):
            self.show_error("Output folder does not exist. Please select a valid folder.")
            return

        # Success message and start scan
        self.show_success("Configuration saved! Starting scan process...")
        self.master.start_scan_thread(config)
        self.after(1500, self.destroy)

    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Configuration Error", message)

    def show_success(self, message):
        """Show success message"""
        success_label = tk.Label(self, text=f"✅ {message}", 
                                font=("Helvetica", 12, "bold"), fg="#28a745", bg="#f8f9fa")
        success_label.place(relx=0.5, rely=0.95, anchor="center")

if __name__ == "__main__":
    app = FaceRecApp()
    app.mainloop()