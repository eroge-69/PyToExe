import tkinter as tk
from tkinter import CENTER, SOLID, Frame, Label, ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
from PIL import Image, ImageTk
from tkinter import ttk, filedialog
import logging
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import letter, landscape
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side

class HospitalManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("AL Khidmat Foundation")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        # Load hospital GIF but do not animate yet
        try:
            self.gif_frames = []
            self.gif_index = 0
            gif = Image.open("hospital.gif")  # Replace with your hospital GIF path
            try:
                while True:
                    frame = gif.copy()
                    frame = frame.resize((50, 50), Image.LANCZOS)
                    self.gif_frames.append(ImageTk.PhotoImage(frame))
                    gif.seek(len(self.gif_frames))
            except EOFError:
                pass
            self.gif_label = tk.Label(self.root, image=self.gif_frames[0])
            self.gif_label.place(x=10, y=10)  # Position in top-left corner
            self.is_animating = False  # Flag to control hospital GIF animation
        except Exception as e:
            logging.error(f"Error loading hospital GIF: {e}")
            self.gif_label = tk.Label(self.root, text="GIF Error", bg="red", fg="white")

        try:
            self.bg_image = Image.open("Downpic.cc-2378101665.jpg")
            self.bg_image = self.bg_image.resize((1200, 700), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except Exception as e:
            logging.error(f"Error loading background image: {e}")
            self.root.config(bg="#f0f8ff")

        self.main_frame = tk.Frame(self.root, bg="#f0f8ff")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        self.db_connection = self.connect_to_database()
        self.current_user_id = None
        self.current_user_type = None
        self.navigation_stack = []
        self.role_photos = {}
        self.show_landing_screen()

    def animate_gif(self):
        if self.is_animating and self.gif_frames:
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.gif_label.configure(image=self.gif_frames[self.gif_index])
            self.root.after(100, self.animate_gif)
            
  # Only the modified show_loading_screen method is shown for brevity
    def show_loading_screen(self, callback):
        # Create a frame with white background
        self.loading_frame = tk.Frame(self.root, bg="white")
        self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.loading_frame.lift()  # Ensure loading frame is on top
        self.gif_label.lift()  # Keep hospital GIF on top

        # Flag to control heartbeat animation
        self.is_heartbeat_animating = True

        try:
            # Load and animate heartbeat GIF
            self.heartbeat_frames = []
            self.heartbeat_index = 0
            heartbeat_gif = Image.open("heart2.gif")  # Ensure correct path
            try:
                while True:
                    frame = heartbeat_gif.copy()
                    frame = frame.resize((100, 100), Image.LANCZOS)
                    self.heartbeat_frames.append(ImageTk.PhotoImage(frame))
                    heartbeat_gif.seek(len(self.heartbeat_frames))
            except EOFError:
                pass
            self.heartbeat_label = tk.Label(self.loading_frame, image=self.heartbeat_frames[0], bg="white")
            self.heartbeat_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the GIF

            def animate_heartbeat():
                if self.is_heartbeat_animating and self.heartbeat_frames:
                    try:
                        self.heartbeat_index = (self.heartbeat_index + 1) % len(self.heartbeat_frames)
                        self.heartbeat_label.configure(image=self.heartbeat_frames[self.heartbeat_index])
                        self.root.update()  # Force UI refresh to ensure smooth animation
                        self.root.after(50, animate_heartbeat)  # Reduced to 50ms for smoother animation
                        logging.debug(f"Heartbeat GIF frame: {self.heartbeat_index}")  # Debug animation
                    except tk.TclError:
                        self.is_heartbeat_animating = False
                        logging.debug("Heartbeat animation stopped due to widget destruction")

            # Start heartbeat animation
            animate_heartbeat()

            # Destroy loading frame and proceed to callback after 1 second
            def cleanup_and_proceed():
                self.is_heartbeat_animating = False
                self.heartbeat_label.destroy()  # Explicitly destroy label
                self.loading_frame.destroy()
                callback()

            self.root.after(1000, cleanup_and_proceed)

        except Exception as e:
            logging.error(f"Error loading heartbeat GIF: {e}")
            self.is_heartbeat_animating = False
            self.root.after(1000, lambda: [self.loading_frame.destroy(), callback()])  # Fallback

    # def show_loading_screen(self, callback):
    #     # Create a frame with white background
    #     self.loading_frame = tk.Frame(self.root, bg="white")
    #     self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    #     self.gif_label.lift()  # Ensure hospital GIF stays on top

    #     # Flag to control heartbeat animation
    #     self.is_heartbeat_animating = True

    #     try:
    #         # Load and animate heartbeat GIF
    #         self.heartbeat_frames = []
    #         self.heartbeat_index = 0
    #         heartbeat_gif = Image.open("heart2.gif")  # Replace with your heartbeat GIF path
    #         try:
    #             while True:
    #                 frame = heartbeat_gif.copy()
    #                 frame = frame.resize((100, 100), Image.LANCZOS)  # Resize to appropriate size
    #                 self.heartbeat_frames.append(ImageTk.PhotoImage(frame))
    #                 heartbeat_gif.seek(len(self.heartbeat_frames))
    #         except EOFError:
    #             pass
    #         self.heartbeat_label = tk.Label(self.loading_frame, image=self.heartbeat_frames[0], bg="white")
    #         self.heartbeat_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the GIF

    #         def animate_heartbeat():
    #             if self.is_heartbeat_animating and self.heartbeat_frames:
    #                 try:
    #                     self.heartbeat_index = (self.heartbeat_index + 1) % len(self.heartbeat_frames)
    #                     self.heartbeat_label.configure(image=self.heartbeat_frames[self.heartbeat_index])
    #                     self.root.after(100, animate_heartbeat)
    #                 except tk.TclError:
    #                     # Widget was destroyed, stop animation
    #                     self.is_heartbeat_animating = False

    #         # Start heartbeat animation
    #         animate_heartbeat()

    #         # Destroy loading frame and proceed to callback after 2 seconds
    #         def cleanup_and_proceed():
    #             self.is_heartbeat_animating = False  # Stop heartbeat animation
    #             self.loading_frame.destroy()
    #             callback()

    #         self.root.after(1000, cleanup_and_proceed)

    #     except Exception as e:
    #         logging.error(f"Error loading heartbeat GIF: {e}")
    #         # Fallback to a blank white screen for 2 seconds
    #         self.is_heartbeat_animating = False
    #         self.root.after(2000, lambda: [self.loading_frame.destroy(), callback()])

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()

        if not username or not password:
            def show_error():
                messagebox.showerror("Error", "Please enter both username and password")
                self.show_landing_screen()
            self.show_loading_screen(show_error)
            return

        hashed_password = self.hash_password(password)

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT user_id, password FROM users WHERE username = %s AND user_type = %s",
                (username, user_type),
            )
            user_data = cursor.fetchone()

            def handle_auth_result():
                if user_data and user_data[1] == hashed_password:
                    self.current_user_id = user_data[0]
                    self.current_user_type = user_type
                    # Start hospital GIF animation after successful login
                    self.gif_label.place_forget()  # Hide it initially
                    self.is_animating = False      # Animation off by default

                    # Show GIF in top-left corner
                    self.animate_gif()
                    # Show appropriate dashboard
                    if user_type == "admin":
                        self.show_admin_dashboard(user_data[0])
                    elif user_type == "doctor":
                        self.show_doctor_dashboard(user_data[0])
                    elif user_type == "patient":
                        self.show_patient_dashboard(user_data[0])
                    elif user_type == "staff":
                        self.show_staff_dashboard(user_data[0])
                else:
                    messagebox.showerror("Error", "Invalid username or password")
                    self.show_landing_screen()

            # Show heartbeat GIF before handling auth result
            self.show_loading_screen(handle_auth_result)

        except Error as e:
            def show_db_error():
                messagebox.showerror("Database Error", f"Failed to authenticate user: {e}")
                self.show_landing_screen()
            self.show_loading_screen(show_db_error)
            
    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mubashir@4",
                database="hospital_management_system",
            )
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            return None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    def show_landing_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        self.gif_label.place_forget()  # Hide GIF
        self.is_animating = False      # Stop GIF animation

        self.current_user_id = None
        self.current_user_type = None
        self.gif_label.lift()

        landing_frame = tk.Frame(self.main_frame, bg="#f0f8ff", padx=50, pady=50)
        landing_frame.pack(expand=True)

        tk.Label(
            landing_frame,
            text="Welcome to AL Khidmat-Hospital Portal",
            font=("Arial", 24, "bold"),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).pack(pady=(0, 40))

        roles_frame = tk.Frame(landing_frame, bg="#f0f8ff")
        roles_frame.pack()

        roles = [
            ("admin", "admin_logo.png", lambda: self.show_loading_screen(lambda: self.show_login_screen("admin"))),
            ("doctor", "doctor_logo.png", lambda: self.show_loading_screen(lambda: self.show_login_screen("doctor"))),
            ("patient", "patient_logo.png", lambda: self.show_loading_screen(lambda: self.show_login_screen("patient"))),
            ("staff", "staff_logo.png", lambda: self.show_loading_screen(lambda: self.show_login_screen("staff"))),
        ]

        for idx, (role, image_path, command) in enumerate(roles):
            try:
                if not os.path.exists(image_path):
                    logging.error(f"Image file not found: {image_path}")
                    raise FileNotFoundError(f"Image {image_path} not found")
                
                logging.debug(f"Loading image for {role}: {image_path}")
                img = Image.open(image_path)
                img = img.resize((100, 100), Image.LANCZOS)
                img_scaled = img.resize((110, 110), Image.LANCZOS)
                
                self.role_photos[role] = {
                    'normal': ImageTk.PhotoImage(img),
                    'hover': ImageTk.PhotoImage(img_scaled)
                }
                
            except Exception as e:
                logging.error(f"Failed to load image for {role}: {e}")
                self.role_photos[role] = {
                    'normal': ImageTk.PhotoImage(Image.new("RGB", (100, 100), "#cccccc")),
                    'hover': ImageTk.PhotoImage(Image.new("RGB", (110, 110), "#cccccc"))
                }
                tk.Label(
                    landing_frame,
                    text=f"{role.capitalize()} Image Missing",
                    font=("Arial", 10),
                    bg="#f0f8ff",
                    fg="#ff4500"
                ).place(x=150 * idx + 100, y=300)

            img_button = tk.Button(
                roles_frame,
                image=self.role_photos[role]['normal'],
                bg="#f0f8ff",
                borderwidth=0,
                command=command
            )
            img_button.grid(row=0, column=idx, padx=20)

            img_button.bind("<Enter>", lambda event, r=role: self.on_role_hover_enter(event, r))
            img_button.bind("<Leave>", lambda event, r=role: self.on_role_hover_leave(event, r))

            tk.Label(
                roles_frame,
                text=role.capitalize(),
                font=("Arial", 12, "bold"),
                bg="#f0f8ff",
                fg="#34495e"
            ).grid(row=1, column=idx, pady=10)

    def on_role_hover_enter(self, event, role):
        event.widget.config(image=self.role_photos[role]['hover'])

    def on_role_hover_leave(self, event, role):
        event.widget.config(image=self.role_photos[role]['normal'])

    def show_login_screen(self, user_type=""):
        self.gif_label.place_forget()  # Hide GIF
        self.is_animating = False      # Stop GIF animation

        logging.debug(f"Entering show_login_screen with user_type: {user_type}")
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.gif_label.lift()

        login_frame = tk.Frame(self.main_frame, bg="#f0f8ff", padx=50, pady=50)
        login_frame.pack(expand=True)

        tk.Label(
            login_frame,
            text="ہسپتال آن لائن پورٹل",
            font=("Noto Nastaliq Urdu", 20, "bold"),
            bg="#f0f8ff",
        ).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(login_frame, text="Username:", font=("Arial", 12), bg="#f0f8ff").grid(
            row=1, column=0, pady=5, sticky="e"
        )
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.grid(row=1, column=1, pady=5, ipadx=20)

        tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="#f0f8ff").grid(
            row=2, column=0, pady=5, sticky="e"
        )
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=2, column=1, pady=5, ipadx=20)

        tk.Label(login_frame, text="User Type:", font=("Arial", 12), bg="#f0f8ff").grid(
            row=3, column=0, pady=5, sticky="e"
        )
        user_types = ["admin", "doctor", "patient", "staff"]
        self.user_type_var = tk.StringVar(value=user_type)
        logging.debug(f"Set user_type_var to: {user_type}")
        self.user_type_dropdown = ttk.Combobox(
            login_frame,
            textvariable=self.user_type_var,
            values=user_types,
            font=("Arial", 12),
            state="readonly"
        )
        self.user_type_dropdown.set(user_type)
        self.user_type_dropdown.grid(row=3, column=1, pady=5, ipadx=20)

        login_btn = tk.Button(
            login_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            command=lambda: self.show_loading_screen(lambda:self.authenticate_user()),
        )
        login_btn.grid(row=4, column=0, columnspan=2, pady=20, ipadx=20)

        register_btn = tk.Button(
            login_frame,
            text="Register as Patient",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            command=lambda:self.show_loading_screen(lambda:self.show_patient_registration()),
        )
        register_btn.grid(row=5, column=0, columnspan=2, pady=10, ipadx=10)

        back_btn = tk.Button(
            login_frame,
            text="Back to Home",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self.show_landing_screen,
        )
        back_btn.grid(row=6, column=0, columnspan=2, pady=10, ipadx=10)

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        hashed_password = self.hash_password(password)

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT user_id, password FROM users WHERE username = %s AND user_type = %s",
                (username, user_type),
            )
            user_data = cursor.fetchone()

            if user_data and user_data[1] == hashed_password:
                self.current_user_id = user_data[0]
                self.current_user_type = user_type  # Store user type
                if user_type == "admin":
                    self.show_admin_dashboard(user_data[0])
                elif user_type == "doctor":
                    self.show_doctor_dashboard(user_data[0])
                elif user_type == "patient":
                    self.show_patient_dashboard(user_data[0])
                elif user_type == "staff":
                    self.show_staff_dashboard(user_data[0])
            else:
                messagebox.showerror("Error", "Invalid username or password")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to authenticate user: {e}")

    def show_patient_registration(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create scrollable canvas for form
        canvas = tk.Canvas(self.main_frame, bg="#f0f8ff")
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f8ff", padx=20, pady=20)

        # Configure canvas scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Style for combobox and buttons
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff")
        style.configure("TButton", padding=10)

        # Title
        tk.Label(
            scrollable_frame,
            text="Patient Registration",
            font=("Arial", 24, "bold"),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Personal information section
        tk.Label(
            scrollable_frame,
            text="Personal Information",
            font=("Arial", 16, "bold"),
            bg="#f0f8ff",
            fg="#34495e"
        ).grid(row=1, column=0, columnspan=2, pady=(10, 15), sticky="w")

        # Define form fields
        fields = [
            ("First Name:", 2),
            ("Last Name:", 3),
            ("Date of Birth (YYYY-MM-DD):", 4),
            ("Gender:", 5),
            ("Blood Type:", 6),
            ("Phone:", 7),
            ("Address:", 8)
        ]

        # Create labels for fields
        for label_text, row in fields:
            tk.Label(
                scrollable_frame,
                text=label_text,
                font=("Arial", 12),
                bg="#f0f8ff",
                fg="#2c3e50"
            ).grid(row=row, column=0, pady=8, padx=10, sticky="e")

        # Create input fields
        self.reg_first_name = tk.Entry(scrollable_frame, font=("Arial", 12), bg="#ffffff", bd=2, relief="groove")
        self.reg_first_name.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        self.reg_last_name = tk.Entry(scrollable_frame, font=("Arial", 12), bg="#ffffff", bd=2, relief="groove")
        self.reg_last_name.grid(row=3, column=1, pady=8, padx=10, sticky="w")

        self.reg_dob = tk.Entry(scrollable_frame, font=("Arial", 12), bg="#ffffff", bd=2, relief="groove")
        self.reg_dob.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        self.reg_gender = ttk.Combobox(
            scrollable_frame,
            values=["Male", "Female", "Other"],
            font=("Arial", 12),
            state="readonly"
        )
        self.reg_gender.grid(row=5, column=1, pady=8, padx=10, sticky="w")

        self.reg_blood_type = ttk.Combobox(
            scrollable_frame,
            values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            font=("Arial", 12),
            state="readonly"
        )
        self.reg_blood_type.grid(row=6, column=1, pady=8, padx=10, sticky="w")

        self.reg_phone = tk.Entry(scrollable_frame, font=("Arial", 12), bg="#ffffff", bd=2, relief="groove")
        self.reg_phone.grid(row=7, column=1, pady=8, padx=10, sticky="w")

        self.reg_address = tk.Text(scrollable_frame, font=("Arial", 12), height=3, width=30, bd=2, relief="groove")
        self.reg_address.grid(row=8, column=1, pady=8, padx=10, sticky="w")

        # Profile photo section
        tk.Label(
            scrollable_frame,
            text="Profile Photo",
            font=("Arial", 16, "bold"),
            bg="#f0f8ff",
            fg="#34495e"
        ).grid(row=9, column=0, columnspan=2, pady=(20, 15), sticky="w")

        tk.Label(
            scrollable_frame,
            text="Upload Photo:",
            font=("Arial", 12),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).grid(row=10, column=0, pady=8, padx=10, sticky="e")

        self.photo_path = tk.StringVar()  # Store photo file path
        photo_button = tk.Button(
            scrollable_frame,
            text="Choose Image",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=lambda: self.upload_photo(scrollable_frame)  # Call photo upload function
        )
        photo_button.grid(row=10, column=1, pady=8, padx=10, sticky="w")

        # Photo display label
        self.photo_label = tk.Label(scrollable_frame, bg="#f0f8ff")
        self.photo_label.grid(row=11, column=0, columnspan=2, pady=10)

        # Login credentials section
        tk.Label(
            scrollable_frame,
            text="Login Credentials",
            font=("Arial", 16, "bold"),
            bg="#f0f8ff",
            fg="#34495e"
        ).grid(row=12, column=0, columnspan=2, pady=(20, 15), sticky="w")

        tk.Label(
            scrollable_frame,
            text="Username:",
            font=("Arial", 12),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).grid(row=13, column=0, pady=8, padx=10, sticky="e")
        self.reg_username = tk.Entry(scrollable_frame, font=("Arial", 12), bg="#ffffff", bd=2, relief="groove")
        self.reg_username.grid(row=13, column=1, pady=8, padx=10, sticky="w")

        tk.Label(
            scrollable_frame,
            text="Password:",
            font=("Arial", 12),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).grid(row=14, column=0, pady=8, padx=10, sticky="e")
        self.reg_password = tk.Entry(scrollable_frame, font=("Arial", 12), show="*", bg="#ffffff", bd=2, relief="groove")
        self.reg_password.grid(row=14, column=1, pady=8, padx=10, sticky="w")

        tk.Label(
            scrollable_frame,
            text="Confirm Password:",
            font=("Arial", 12),
            bg="#f0f8ff",
            fg="#2c3e50"
        ).grid(row=15, column=0, pady=8, padx=10, sticky="e")
        self.reg_confirm_password = tk.Entry(scrollable_frame, font=("Arial", 12), show="*", bg="#ffffff", bd=2, relief="groove")
        self.reg_confirm_password.grid(row=15, column=1, pady=8, padx=10, sticky="w")

        # Buttons
        button_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
        button_frame.grid(row=16, column=0, columnspan=2, pady=20)

        register_btn = tk.Button(
            button_frame,
            text="Register",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            bd=0,
            padx=20,
            pady=10,
            command=lambda:self.show_loading_screen(lambda:self.register_patient())  # Call registration function
        )
        register_btn.pack(side="left", padx=10)

        back_btn = tk.Button(
            button_frame,
            text="Back to Login",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            bd=0,
            padx=20,
            pady=10,
            command=self.show_login_screen  # Return to login screen
        )
        back_btn.pack(side="left", padx=10)

    # Handle photo upload for registration
    def upload_photo(self, frame):
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.photo_path.set(file_path)  # Store file path
            # Load and display image
            image = Image.open(file_path)
            image = image.resize((150, 150), Image.LANCZOS)  # Resize to 150x150
            photo = ImageTk.PhotoImage(image)
            self.photo_label.configure(image=photo)
            self.photo_label.image = photo  # Keep reference to avoid garbage collection

    # Process patient registration
    def register_patient(self):
        # Get form data
        first_name = self.reg_first_name.get()
        last_name = self.reg_last_name.get()
        dob = self.reg_dob.get()
        gender = self.reg_gender.get()
        blood_type = self.reg_blood_type.get()
        phone = self.reg_phone.get()
        address = self.reg_address.get("1.0", tk.END).strip()
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm_password = self.reg_confirm_password.get()
        photo_path = self.photo_path.get() if self.photo_path.get() else None

        # Validate inputs
        if not all([first_name, last_name, dob, gender, phone, address, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required except blood type")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Validate date format
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        cursor = None
        try:
            # Ensure clean transaction state
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Check if username is unique
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Insert user into users table
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)",
                (username, hashed_password, "patient"),
            )
            user_id = cursor.lastrowid  # Get new user ID

            # Insert patient into patients table
            cursor.execute(
                """INSERT INTO patients 
                (user_id, first_name, last_name, date_of_birth, gender, blood_type, phone, address, photo_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, first_name, last_name, dob, gender, blood_type if blood_type else None, phone, address, photo_path),
            )

            self.db_connection.commit()  # Commit transaction
            messagebox.showinfo("Success", "Patient registration successful!")
            self.show_login_screen()  # Return to login screen

        except Error as e:
            self.db_connection.rollback()  # Rollback on error
            messagebox.showerror("Database Error", f"Failed to register patient: {e}")
        finally:
            if cursor:
                cursor.close()  # Close cursor

    # Placeholder methods for dashboards (unchanged)
    def show_admin_dashboard(self, user_id):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Admin dashboard frame
        dashboard_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(dashboard_frame, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=20)

        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=lambda: self.show_loading_screen(lambda: self.show_login_screen()),
        )
        logout_btn.pack(side=tk.RIGHT, padx=20)

        # Navigation
        nav_frame = tk.Frame(dashboard_frame, bg="#333", width=200)
        nav_frame.pack(fill=tk.Y, side=tk.LEFT)

        buttons = [
            ("Dashboard", lambda: self.show_admin_welcome()),
            ("Manage Doctors", lambda: self.show_manage_doctors()),
            ("Manage Patients", lambda: self.show_manage_patients()),
            ("Manage Staff", lambda: self.show_manage_staff()),
            ("View Appointments", lambda: self.show_admin_appointments()),
            ("View Reports", lambda: self.show_reports()),
            ("System Settings", lambda: self.show_system_settings()),
        ]

        for text, command in buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 12),
                bg="#333",
                fg="white",
                relief=tk.FLAT,
                command=command,
            ).pack(fill=tk.X, pady=2)

        # Main content area
        self.admin_content_frame = tk.Frame(dashboard_frame, bg="#f0f8ff")
        self.admin_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show default view
        command=lambda:self.show_loading_screen(lambda:self.show_admin_welcome())

    def show_admin_welcome(self):
        # Clear content frame
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Welcome, Admin",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=50)

        # Display some statistics
        stats_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        stats_frame.pack()

        try:
            cursor = self.db_connection.cursor()

            # Get total patients
            cursor.execute("SELECT COUNT(*) FROM patients")
            total_patients = cursor.fetchone()[0]

            # Get total doctors
            cursor.execute("SELECT COUNT(*) FROM doctors")
            total_doctors = cursor.fetchone()[0]

            # Get total staff
            cursor.execute("SELECT COUNT(*) FROM staff")
            total_staff = cursor.fetchone()[0]

            # Get today's appointments
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s",
                (today,),
            )
            today_appointments = cursor.fetchone()[0]

            # Display stats
            stats = [
                ("Total Patients", total_patients),
                ("Total Doctors", total_doctors),
                ("Total Staff", total_staff),
                ("Today's Appointments", today_appointments),
            ]

            for i, (label, value) in enumerate(stats):
                tk.Label(
                    stats_frame, text=label, font=("Arial", 14), bg="#f0f8ff"
                ).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                tk.Label(
                    stats_frame,
                    text=str(value),
                    font=("Arial", 14, "bold"),
                    bg="#f0f8ff",
                ).grid(row=i, column=1, padx=10, pady=5, sticky="w")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch statistics: {e}")
            
    def show_manage_staff(self):
        # Clear content frame
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Manage Staff",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Add staff button
        add_btn = tk.Button(
            self.admin_content_frame,
            text="Add New Staff Member",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.show_add_staff_form,
        )
        add_btn.pack(pady=10)

        # Staff table
        columns = ("ID", "Name", "Role", "Phone", "Email")
        self.staff_tree = ttk.Treeview(
            self.admin_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=150, anchor=tk.CENTER)

        self.staff_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load staff data
        self.load_staff_data()

        # Action buttons frame
        action_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        edit_btn = tk.Button(
            action_frame,
            text="Edit Staff",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.edit_staff,
           
        )
        edit_btn.grid(row=0, column=0, padx=10)

        delete_btn = tk.Button(
            action_frame,
            text="Delete Staff",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=lambda:self.show_loading_screen(lambda:self.delete_staff()),
        )
        delete_btn.grid(row=0, column=1, padx=10)

    def load_staff_data(self):
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT s.staff_id, CONCAT(s.first_name, ' ', s.last_name), s.role, s.phone, s.email
                FROM staff s
                JOIN users u ON s.user_id = u.user_id
            """
            cursor.execute(query)
            staff_members = cursor.fetchall()

            # Clear existing data
            for item in self.staff_tree.get_children():
                self.staff_tree.delete(item)

            # Insert new data
            for staff in staff_members:
                self.staff_tree.insert("", tk.END, values=staff)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load staff data: {e}")

    def show_manage_doctors(self):
        # Clear content frame
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Manage Doctors",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Add doctor button
        add_btn = tk.Button(
            self.admin_content_frame,
            text="Add New Doctor",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.show_add_doctor_form,
        )
        add_btn.pack(pady=10)

        # Doctors table
        columns = ("ID", "Name", "Specialization", "Phone", "Email")
        self.doctors_tree = ttk.Treeview(
            self.admin_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.doctors_tree.heading(col, text=col)
            self.doctors_tree.column(col, width=150, anchor=tk.CENTER)

        self.doctors_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load doctors data
        self.load_doctors_data()

        # Action buttons frame
        action_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        edit_btn = tk.Button(
            action_frame,
            text="Edit Doctor",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.edit_doctor,
        )
        edit_btn.grid(row=0, column=0, padx=10)

        delete_btn = tk.Button(
            action_frame,
            text="Delete Doctor",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.delete_doctor,
        )
        delete_btn.grid(row=0, column=1, padx=10)

    def load_doctors_data(self):
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT d.doctor_id, CONCAT(d.first_name, ' ', d.last_name), d.specialization, d.phone, d.email
                FROM doctors d
                JOIN users u ON d.user_id = u.user_id
            """
            cursor.execute(query)
            doctors = cursor.fetchall()

            # Clear existing data
            for item in self.doctors_tree.get_children():
                self.doctors_tree.delete(item)

            # Insert new data
            for doctor in doctors:
                self.doctors_tree.insert("", tk.END, values=doctor)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load doctors data: {e}")

    def show_add_doctor_form(self):
        # Create a new top-level window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Doctor")
        add_window.geometry("500x600")

        tk.Label(add_window, text="Add New Doctor", font=("Arial", 18, "bold")).pack(
            pady=10
        )

        # Form fields
        fields = [
            ("First Name:", "entry"),
            ("Last Name:", "entry"),
            ("Specialization:", "entry"),
            ("Phone:", "entry"),
            ("Email:", "entry"),
            ("Username:", "entry"),
            ("Password:", "entry", True),
            ("Confirm Password:", "entry", True),
        ]

        self.doctor_form_entries = {}

        for i, (label, field_type, *options) in enumerate(fields):
            tk.Label(add_window, text=label, font=("Arial", 12)).pack(pady=5)

            if field_type == "entry":
                show = "*" if options and options[0] else ""
                entry = tk.Entry(add_window, font=("Arial", 12), show=show)
                entry.pack(pady=5, ipadx=20)
                self.doctor_form_entries[
                    label.split(":")[0].lower().replace(" ", "_")
                ] = entry

        # Submit button
        submit_btn = tk.Button(
            add_window,
            text="Add Doctor",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.add_doctor(add_window),
        )
        submit_btn.pack(pady=20)

    def add_doctor(self, window):
        # Get all form data
        first_name = self.doctor_form_entries["first_name"].get()
        last_name = self.doctor_form_entries["last_name"].get()
        specialization = self.doctor_form_entries["specialization"].get()
        phone = self.doctor_form_entries["phone"].get()
        email = self.doctor_form_entries["email"].get()
        username = self.doctor_form_entries["username"].get()
        password = self.doctor_form_entries["password"].get()
        confirm_password = self.doctor_form_entries["confirm_password"].get()

        # Validate inputs
        if not all([first_name, last_name, specialization, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields except phone and email are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Insert user
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)",
                (username, hashed_password, "doctor"),
            )
            user_id = cursor.lastrowid

            # Insert doctor
            cursor.execute(
                """INSERT INTO doctors 
                (user_id, first_name, last_name, specialization, phone, email) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, first_name, last_name, specialization, phone, email),
            )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Doctor added successfully!")
            window.destroy()
            self.load_doctors_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to add doctor: {e}")
        finally:
            if cursor:
                cursor.close()

    def edit_doctor(self):
        selected_item = self.doctors_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doctor to edit")
            return

        doctor_id = self.doctors_tree.item(selected_item)["values"][0]

        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT d.doctor_id, d.first_name, d.last_name, d.specialization, d.phone, d.email, u.username
                FROM doctors d
                JOIN users u ON d.user_id = u.user_id
                WHERE d.doctor_id = %s
            """
            cursor.execute(query, (doctor_id,))
            doctor_data = cursor.fetchone()

            if not doctor_data:
                messagebox.showerror("Error", "Doctor not found")
                return

            # Create edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Doctor")
            edit_window.geometry("500x600")

            tk.Label(edit_window, text="Edit Doctor", font=("Arial", 18, "bold")).pack(pady=10)

            # Form fields
            fields = [
                ("First Name:", doctor_data[1]),
                ("Last Name:", doctor_data[2]),
                ("Specialization:", doctor_data[3]),
                ("Phone:", doctor_data[4]),
                ("Email:", doctor_data[5]),
                ("Username:", doctor_data[6]),
            ]

            self.edit_doctor_entries = {}

            for i, (label, value) in enumerate(fields):
                tk.Label(edit_window, text=label, font=("Arial", 12)).pack(pady=5)

                entry = tk.Entry(edit_window, font=("Arial", 12))
                entry.insert(0, value)
                entry.pack(pady=5, ipadx=20)

                self.edit_doctor_entries[
                    label.split(":")[0].lower().replace(" ", "_")
                ] = entry

            # Add password fields (optional)
            tk.Label(edit_window, text="New Password (leave blank to keep current):", font=("Arial", 12)).pack(pady=5)
            self.edit_doctor_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_doctor_password.pack(pady=5, ipadx=20)

            tk.Label(edit_window, text="Confirm New Password:", font=("Arial", 12)).pack(pady=5)
            self.edit_doctor_confirm_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_doctor_confirm_password.pack(pady=5, ipadx=20)

            # Submit button
            submit_btn = tk.Button(
                edit_window,
                text="Update Doctor",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.update_doctor(doctor_id, edit_window),
            )
            submit_btn.pack(pady=20)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch doctor data: {e}")

    def update_doctor(self, doctor_id, window):
        # Get all form data
        first_name = self.edit_doctor_entries["first_name"].get()
        last_name = self.edit_doctor_entries["last_name"].get()
        specialization = self.edit_doctor_entries["specialization"].get()
        phone = self.edit_doctor_entries["phone"].get()
        email = self.edit_doctor_entries["email"].get()
        username = self.edit_doctor_entries["username"].get()
        password = self.edit_doctor_password.get()
        confirm_password = self.edit_doctor_confirm_password.get()

        # Validate inputs
        if not all([first_name, last_name, specialization, username]):
            messagebox.showerror("Error", "First Name, Last Name, Specialization, and Username are required")
            return

        if password and password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get user_id for this doctor
            cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = %s", (doctor_id,))
            user_id = cursor.fetchone()[0]

            # Check if username exists (excluding current doctor)
            cursor.execute(
                "SELECT username FROM users WHERE username = %s AND user_id != %s",
                (username, user_id)
            )
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Update doctors table
            cursor.execute(
                """UPDATE doctors 
                SET first_name = %s, last_name = %s, specialization = %s, phone = %s, email = %s
                WHERE doctor_id = %s""",
                (first_name, last_name, specialization, phone, email, doctor_id),
            )

            # Update users table
            if password:
                hashed_password = self.hash_password(password)
                cursor.execute(
                    "UPDATE users SET username = %s, password = %s WHERE user_id = %s",
                    (username, hashed_password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = %s WHERE user_id = %s",
                    (username, user_id)
                )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Doctor updated successfully!")
            window.destroy()
            self.show_loading_screen(lambda: self.load_doctors_data())

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update doctor: {e}")
        finally:
            if cursor:
                cursor.close()
                
    def delete_doctor(self):
        selected_item = self.doctors_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doctor to delete")
            return

        doctor_id = self.doctors_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this doctor?"
        )
        if not confirm:
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get user_id for this doctor
            cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = %s", (doctor_id,))
            user_id = cursor.fetchone()[0]

            # Delete from doctors table
            cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))

            # Delete from users table
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

            self.db_connection.commit()
            messagebox.showinfo("Success", "Doctor deleted successfully!")
            self.load_doctors_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to delete doctor: {e}")
        finally:
            if cursor:
                cursor.close()

    def show_manage_patients(self):
        # Clear content frame
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Manage Patients",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Add patient button
        add_btn = tk.Button(
            self.admin_content_frame,
            text="Add New Patient",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.show_patient_registration,
        )
        add_btn.pack(pady=10)

        # Patients table
        columns = ("ID", "Name", "Gender", "Age", "Blood Type", "Phone")
        self.patients_tree = ttk.Treeview(
            self.admin_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.patients_tree.heading(col, text=col)
            self.patients_tree.column(col, width=120, anchor=tk.CENTER)

        self.patients_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load patients data
        self.load_patients_data()

        # Action buttons frame
        action_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        edit_btn = tk.Button(
            action_frame,
            text="Edit Patient",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.edit_patient,
        )
        edit_btn.grid(row=0, column=0, padx=10)

        delete_btn = tk.Button(
            action_frame,
            text="Delete Patient",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.delete_patient,
        )
        delete_btn.grid(row=0, column=1, padx=10)

    def load_patients_data(self):
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT p.patient_id, CONCAT(p.first_name, ' ', p.last_name), 
                       p.gender, TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()), 
                       p.blood_type, p.phone
                FROM patients p
                ORDER BY p.last_name, p.first_name
            """
            cursor.execute(query)
            patients = cursor.fetchall()

            # Clear existing data
            for item in self.patients_tree.get_children():
                self.patients_tree.delete(item)

            # Insert new data
            for patient in patients:
                self.patients_tree.insert("", tk.END, values=patient)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load patients data: {e}")
            
    def edit_patient(self):
        selected_item = self.patients_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient to edit")
            return

        patient_id = self.patients_tree.item(selected_item)["values"][0]

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT p.patient_id, p.first_name, p.last_name, p.date_of_birth, 
                       p.gender, p.blood_type, p.phone, p.address, u.username
                FROM patients p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.patient_id = %s""",
                (patient_id,)
            )
            patient_data = cursor.fetchone()

            if not patient_data:
                messagebox.showerror("Error", "Patient not found")
                return

            # Create edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Patient")
            edit_window.geometry("600x700")

            tk.Label(edit_window, text="Edit Patient", font=("Arial", 18, "bold")).pack(pady=10)

            # Form fields
            fields = [
                ("First Name:", patient_data[1]),
                ("Last Name:", patient_data[2]),
                ("Date of Birth (YYYY-MM-DD):", patient_data[3]),
                ("Gender:", patient_data[4]),
                ("Blood Type:", patient_data[5]),
                ("Phone:", patient_data[6]),
                ("Address:", patient_data[7]),
                ("Username:", patient_data[8]),
            ]

            self.edit_patient_entries = {}

            for i, (label, value) in enumerate(fields):
                tk.Label(edit_window, text=label, font=("Arial", 12)).pack(pady=5)

                if label == "Gender:":
                    entry = ttk.Combobox(edit_window, values=["Male", "Female", "Other"], font=("Arial", 12))
                    entry.set(value)
                elif label == "Blood Type:":
                    entry = ttk.Combobox(
                        edit_window,
                        values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                        font=("Arial", 12)
                    )
                    entry.set(value)
                elif label == "Address:":
                    entry = tk.Text(edit_window, font=("Arial", 12), height=4, width=40)
                    entry.insert("1.0", value)
                else:
                    entry = tk.Entry(edit_window, font=("Arial", 12))
                    entry.insert(0, value)

                entry.pack(pady=5, ipadx=20)
                self.edit_patient_entries[label.split(":")[0].lower().replace(" ", "_")] = entry

            # Password fields (optional)
            tk.Label(edit_window, text="New Password (leave blank to keep current):", font=("Arial", 12)).pack(pady=5)
            self.edit_patient_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_patient_password.pack(pady=5, ipadx=20)

            tk.Label(edit_window, text="Confirm New Password:", font=("Arial", 12)).pack(pady=5)
            self.edit_patient_confirm_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_patient_confirm_password.pack(pady=5, ipadx=20)

            # Submit button
            submit_btn = tk.Button(
                edit_window,
                text="Update Patient",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.update_patient(patient_id, edit_window),
            )
            submit_btn.pack(pady=20)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch patient data: {e}")

    def update_patient(self, patient_id, window):
        # Get all form data
        first_name = self.edit_patient_entries["first_name"].get()
        last_name = self.edit_patient_entries["last_name"].get()
        date_of_birth = self.edit_patient_entries["date_of_birth"].get()
        gender = self.edit_patient_entries["gender"].get()
        blood_type = self.edit_patient_entries["blood_type"].get()
        phone = self.edit_patient_entries["phone"].get()
        address = self.edit_patient_entries["address"].get("1.0", tk.END).strip()
        username = self.edit_patient_entries["username"].get()
        password = self.edit_patient_password.get()
        confirm_password = self.edit_patient_confirm_password.get()

        # Validate inputs
        if not all([first_name, last_name, date_of_birth, gender, phone, address, username]):
            messagebox.showerror("Error", "All fields except blood type are required")
            return

        if password and password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            datetime.strptime(date_of_birth, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get user_id for this patient
            cursor.execute("SELECT user_id FROM patients WHERE patient_id = %s", (patient_id,))
            user_id = cursor.fetchone()[0]

            # Check if username exists (excluding current patient)
            cursor.execute(
                "SELECT username FROM users WHERE username = %s AND user_id != %s",
                (username, user_id)
            )
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Update patients table
            cursor.execute(
                """UPDATE patients 
                SET first_name = %s, last_name = %s, date_of_birth = %s, 
                    gender = %s, blood_type = %s, phone = %s, address = %s
                WHERE patient_id = %s""",
                (first_name, last_name, date_of_birth, gender, 
                blood_type if blood_type else None, phone, address, patient_id)
            )

            # Update users table
            if password:
                hashed_password = self.hash_password(password)
                cursor.execute(
                    "UPDATE users SET username = %s, password = %s WHERE user_id = %s",
                    (username, hashed_password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = %s WHERE user_id = %s",
                    (username, user_id)
                )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Patient updated successfully!")
            window.destroy()
            self.load_patients_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update patient: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_patient(self):
        selected_item = self.patients_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient to delete")
            return

        patient_id = self.patients_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this patient? This will also delete all their medical records and appointments."
        )
        if not confirm:
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get user_id for this patient
            cursor.execute("SELECT user_id FROM patients WHERE patient_id = %s", (patient_id,))
            user_id = cursor.fetchone()[0]

            # Delete from patients table
            cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))

            # Delete from users table
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

            # Note: Related records (appointments, medical records) should be deleted 
            # automatically if foreign key constraints with ON DELETE CASCADE are set up

            self.db_connection.commit()
            messagebox.showinfo("Success", "Patient deleted successfully!")
            self.load_patients_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to delete patient: {e}")
        finally:
            if cursor:
                cursor.close()
            
    def load_staff_data(self):
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT s.staff_id, CONCAT(s.first_name, ' ', s.last_name), s.role, s.phone, s.email
                FROM staff s
                JOIN users u ON s.user_id = u.user_id
            """
            cursor.execute(query)
            staff_members = cursor.fetchall()

            # Clear existing data
            for item in self.staff_tree.get_children():
                self.staff_tree.delete(item)

            # Insert new data
            for staff in staff_members:
                self.staff_tree.insert("", tk.END, values=staff)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load staff data: {e}")

    def show_add_staff_form(self):
        # Create a new top-level window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Staff Member")
        add_window.geometry("500x600")

        tk.Label(add_window, text="Add New Staff Member", font=("Arial", 18, "bold")).pack(pady=10)

        # Form fields
        fields = [
            ("First Name:", "entry"),
            ("Last Name:", "entry"),
            ("Role:", "entry"),
            ("Phone:", "entry"),
            ("Email:", "entry"),
            ("Username:", "entry"),
            ("Password:", "entry", True),
            ("Confirm Password:", "entry", True),
        ]

        self.staff_form_entries = {}

        for i, (label, field_type, *options) in enumerate(fields):
            tk.Label(add_window, text=label, font=("Arial", 12)).pack(pady=5)

            if field_type == "entry":
                show = "*" if options and options[0] else ""
                entry = tk.Entry(add_window, font=("Arial", 12), show=show)
                entry.pack(pady=5, ipadx=20)
                self.staff_form_entries[
                    label.split(":")[0].lower().replace(" ", "_")
                ] = entry

        # Submit button
        submit_btn = tk.Button(
            add_window,
            text="Add Staff Member",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.add_staff(add_window),
        )
        submit_btn.pack(pady=20)

    def add_staff(self, window):
        # Get all form data
        first_name = self.staff_form_entries["first_name"].get()
        last_name = self.staff_form_entries["last_name"].get()
        role = self.staff_form_entries["role"].get()
        phone = self.staff_form_entries["phone"].get()
        email = self.staff_form_entries["email"].get()
        username = self.staff_form_entries["username"].get()
        password = self.staff_form_entries["password"].get()
        confirm_password = self.staff_form_entries["confirm_password"].get()

        # Validate inputs
        if not all([first_name, last_name, role, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields except phone and email are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Insert user
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)",
                (username, hashed_password, "staff"),
            )
            user_id = cursor.lastrowid

            # Insert staff
            cursor.execute(
                """INSERT INTO staff 
                (user_id, first_name, last_name, role, phone, email) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, first_name, last_name, role, phone, email),
            )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Staff member added successfully!")
            window.destroy()
            self.load_staff_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to add staff member: {e}")
        finally:
            if cursor:
                cursor.close()
       

    def edit_staff(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a staff member to edit")
            return

        staff_id = self.staff_tree.item(selected_item)["values"][0]

        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT s.staff_id, s.first_name, s.last_name, s.role, s.phone, s.email, u.username
                FROM staff s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.staff_id = %s
            """
            cursor.execute(query, (staff_id,))
            staff_data = cursor.fetchone()

            if not staff_data:
                messagebox.showerror("Error", "Staff member not found")
                return

            # Create edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Staff Member")
            edit_window.geometry("500x500")

            tk.Label(edit_window, text="Edit Staff Member", font=("Arial", 18, "bold")).pack(pady=10)

            # Form fields
            fields = [
                ("First Name:", staff_data[1]),
                ("Last Name:", staff_data[2]),
                ("Role:", staff_data[3]),
                ("Phone:", staff_data[4]),
                ("Email:", staff_data[5]),
                ("Username:", staff_data[6]),
            ]

            self.edit_staff_entries = {}

            for i, (label, value) in enumerate(fields):
                tk.Label(edit_window, text=label, font=("Arial", 12)).pack(pady=5)

                entry = tk.Entry(edit_window, font=("Arial", 12))
                entry.insert(0, value)
                entry.pack(pady=5, ipadx=20)

                self.edit_staff_entries[
                    label.split(":")[0].lower().replace(" ", "_")
                ] = entry

            # Password fields (optional)
            tk.Label(edit_window, text="New Password (leave blank to keep current):", font=("Arial", 12)).pack(pady=5)
            self.edit_staff_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_staff_password.pack(pady=5, ipadx=20)

            tk.Label(edit_window, text="Confirm New Password:", font=("Arial", 12)).pack(pady=5)
            self.edit_staff_confirm_password = tk.Entry(edit_window, font=("Arial", 12), show="*")
            self.edit_staff_confirm_password.pack(pady=5, ipadx=20)

            # Submit button
            submit_btn = tk.Button(
                edit_window,
                text="Update Staff",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.update_staff(staff_id, edit_window),
            )
            submit_btn.pack(pady=20)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch staff data: {e}")

    def update_staff(self, staff_id, window):
        # Get all form data
        first_name = self.edit_staff_entries["first_name"].get()
        last_name = self.edit_staff_entries["last_name"].get()
        role = self.edit_staff_entries["role"].get()
        phone = self.edit_staff_entries["phone"].get()
        email = self.edit_staff_entries["email"].get()
        username = self.edit_staff_entries["username"].get()
        password = self.edit_staff_password.get()
        confirm_password = self.edit_staff_confirm_password.get()

        # Validate inputs
        if not all([first_name, last_name, role, username]):
            messagebox.showerror("Error", "First Name, Last Name, Role, and Username are required")
            return

        if password and password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            # Start transaction
            self.db_connection.start_transaction()

            cursor = self.db_connection.cursor()

            # Get user_id for this staff member
            cursor.execute("SELECT user_id FROM staff WHERE staff_id = %s", (staff_id,))
            user_id = cursor.fetchone()[0]

            # Update staff table
            cursor.execute(
                """UPDATE staff 
                SET first_name = %s, last_name = %s, role = %s, phone = %s, email = %s
                WHERE staff_id = %s""",
                (first_name, last_name, role, phone, email, staff_id),
            )

            # Update users table
            if password:
                hashed_password = self.hash_password(password)
                cursor.execute(
                    "UPDATE users SET username = %s, password = %s WHERE user_id = %s",
                    (username, hashed_password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = %s WHERE user_id = %s",
                    (username, user_id)
                )

            # Commit transaction
            self.db_connection.commit()

            messagebox.showinfo("Success", "Staff member updated successfully!")
            window.destroy()
            self.load_staff_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update staff member: {e}")

    def delete_staff(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a staff member to delete")
            return

        staff_id = self.staff_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this staff member?"
        )
        if not confirm:
            return

        try:
            # Start transaction
            self.db_connection.start_transaction()

            cursor = self.db_connection.cursor()

            # Get user_id for this staff member
            cursor.execute("SELECT user_id FROM staff WHERE staff_id = %s", (staff_id,))
            user_id = cursor.fetchone()[0]

            # Delete from staff table
            cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))

            # Delete from users table
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

            # Commit transaction
            self.db_connection.commit()

            messagebox.showinfo("Success", "Staff member deleted successfully!")
            self.load_staff_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to delete staff member: {e}")

    def show_admin_appointments(self):
        # Clear content frame
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Manage Appointments",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Filter frame
        filter_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filter by:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5)

        # Date filter
        self.appointment_date_filter = tk.StringVar()
        tk.Label(filter_frame, text="Date:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=1, padx=5)
        date_entry = tk.Entry(filter_frame, textvariable=self.appointment_date_filter, font=("Arial", 12))
        date_entry.grid(row=0, column=2, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Doctor filter
        self.appointment_doctor_filter = tk.StringVar()
        tk.Label(filter_frame, text="Doctor:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=3, padx=5)
        doctor_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.appointment_doctor_filter,
            font=("Arial", 12),
            state="readonly"
        )
        doctor_combobox.grid(row=0, column=4, padx=5)
        
        # Load doctors for filter
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT doctor_id, CONCAT(first_name, ' ', last_name) FROM doctors")
            doctors = cursor.fetchall()
            doctor_combobox['values'] = ["All"] + [f"{name} (ID: {id})" for id, name in doctors]
            doctor_combobox.set("All")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load doctors: {e}")

        # Filter button
        filter_btn = tk.Button(
            filter_frame,
            text="Apply Filter",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.load_appointments_data,
        )
        filter_btn.grid(row=0, column=5, padx=10)

        # Appointments table
        columns = ("ID", "Patient", "Doctor", "Date", "Time", "Status", "Reason")
        self.appointments_tree = ttk.Treeview(
            self.admin_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=120, anchor=tk.CENTER)

        self.appointments_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load appointments data
        self.load_appointments_data()

        # Action buttons frame
        action_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        add_btn = tk.Button(
            action_frame,
            text="Add Appointment",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.show_add_appointment_form,
        )
        add_btn.grid(row=0, column=0, padx=10)

        edit_btn = tk.Button(
            action_frame,
            text="Edit Appointment",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.edit_appointment,
        )
        edit_btn.grid(row=0, column=1, padx=10)

        delete_btn = tk.Button(
            action_frame,
            text="Delete Appointment",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.delete_appointment,
        )
        delete_btn.grid(row=0, column=2, padx=10)

    def load_appointments_data(self):
        try:
            cursor = self.db_connection.cursor()
            
            # Base query
            query = """
                SELECT a.appointment_id, 
                       CONCAT(p.first_name, ' ', p.last_name),
                       CONCAT(d.first_name, ' ', d.last_name),
                       a.appointment_date,
                       a.appointment_time,
                       a.status,
                       a.reason
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
            """
            
            # Apply filters
            conditions = []
            params = []
            
            # Date filter
            date_filter = self.appointment_date_filter.get()
            if date_filter:
                try:
                    datetime.strptime(date_filter, "%Y-%m-%d")
                    conditions.append("a.appointment_date = %s")
                    params.append(date_filter)
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                    return
            
            # Doctor filter
            doctor_filter = self.appointment_doctor_filter.get()
            if doctor_filter and doctor_filter != "All":
                doctor_id = doctor_filter.split("(ID: ")[1].replace(")", "")
                conditions.append("a.doctor_id = %s")
                params.append(doctor_id)
            
            # Build final query
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY a.appointment_date, a.appointment_time"
            
            cursor.execute(query, tuple(params))
            appointments = cursor.fetchall()

            # Clear existing data
            for item in self.appointments_tree.get_children():
                self.appointments_tree.delete(item)

            # Insert new data
            for appointment in appointments:
                self.appointments_tree.insert("", tk.END, values=appointment)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load appointments: {e}")

    def show_add_appointment_form(self):
        # Create the appointment window
        self.add_appt_window = tk.Toplevel(self.root)
        self.add_appt_window.title("Admin: Add New Appointment")
        self.add_appt_window.geometry("650x650")
        self.add_appt_window.resizable(False, False)
        
        # Configure window styling
        bg_color = "#f0f8ff"
        self.add_appt_window.configure(bg=bg_color)
        
        # Header frame
        header_frame = tk.Frame(self.add_appt_window, bg="#3498db", height=70)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="Create New Appointment",
            font=("Arial", 18, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=20)

        # Main form container
        form_frame = tk.Frame(self.add_appt_window, bg=bg_color, padx=25, pady=25)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Patient Selection
        tk.Label(
            form_frame,
            text="Select Patient:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=0, column=0, pady=10, sticky="e")

        self.patient_var = tk.StringVar()
        patient_cb = ttk.Combobox(
            form_frame,
            textvariable=self.patient_var,
            font=("Arial", 12),
            state="readonly",
            width=35
        )
        patient_cb.grid(row=0, column=1, pady=10, padx=10, sticky="w")

        # Doctor Selection
        tk.Label(
            form_frame,
            text="Select Doctor:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=1, column=0, pady=10, sticky="e")

        self.doctor_var = tk.StringVar()
        doctor_cb = ttk.Combobox(
            form_frame,
            textvariable=self.doctor_var,
            font=("Arial", 12),
            state="readonly",
            width=35
        )
        doctor_cb.grid(row=1, column=1, pady=10, padx=10, sticky="w")

        # Load patients and doctors
        try:
            cursor = self.db_connection.cursor()
            
            # Load patients in format: "John Doe (ID: 1) - Phone: 1234567890"
            cursor.execute("""
                SELECT p.patient_id, p.first_name, p.last_name, p.phone 
                FROM patients p
                JOIN users u ON p.user_id = u.user_id
                ORDER BY p.last_name, p.first_name
            """)
            patients = [
                f"{first_name} {last_name} (ID: {id}) - Phone: {phone}" 
                for id, first_name, last_name, phone in cursor.fetchall()
            ]
            patient_cb['values'] = patients
            
            # Load doctors in format: "Dr. Smith (ID: 1) - Cardiology"
            cursor.execute("""
                SELECT doctor_id, first_name, last_name, specialization 
                FROM doctors 
                ORDER BY last_name, first_name
            """)
            doctors = [
                f"Dr. {first_name} {last_name} (ID: {id}) - {specialization}" 
                for id, first_name, last_name, specialization in cursor.fetchall()
            ]
            doctor_cb['values'] = doctors
            
            if not patients:
                messagebox.showwarning("Warning", "No patients found in database")
            if not doctors:
                messagebox.showwarning("Warning", "No doctors found in database")
                
            if patients:
                patient_cb.current(0)
            if doctors:
                doctor_cb.current(0)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load data: {str(e)}")
            self.add_appt_window.destroy()
            return

        # Date Selection
        tk.Label(
            form_frame,
            text="Appointment Date:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=2, column=0, pady=10, sticky="e")

        self.date_var = tk.StringVar()
        date_entry = tk.Entry(
            form_frame,
            textvariable=self.date_var,
            font=("Arial", 12),
            width=35
        )
        date_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default to today

        # Time Selection
        tk.Label(
            form_frame,
            text="Appointment Time:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=3, column=0, pady=10, sticky="e")

        self.time_var = tk.StringVar()
        time_cb = ttk.Combobox(
            form_frame,
            textvariable=self.time_var,
            font=("Arial", 12),
            values=[f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]],
            state="readonly",
            width=35
        )
        time_cb.grid(row=3, column=1, pady=10, padx=10, sticky="w")
        time_cb.current(0)  # Default to first time slot

        # Status Selection (Admin only)
        tk.Label(
            form_frame,
            text="Appointment Status:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=4, column=0, pady=10, sticky="e")

        self.status_var = tk.StringVar(value="Scheduled")
        status_cb = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            font=("Arial", 12),
            values=["Scheduled", "Confirmed", "Completed", "Cancelled"],
            state="readonly",
            width=35
        )
        status_cb.grid(row=4, column=1, pady=10, padx=10, sticky="w")

        # Reason for Visit
        tk.Label(
            form_frame,
            text="Reason:",
            font=("Arial", 12, "bold"),
            bg=bg_color
        ).grid(row=5, column=0, pady=10, sticky="ne")

        self.reason_text = tk.Text(
            form_frame,
            font=("Arial", 12),
            height=5,
            width=35,
            wrap=tk.WORD
        )
        self.reason_text.grid(row=5, column=1, pady=10, padx=10, sticky="w")

        # Button Frame
        button_frame = tk.Frame(form_frame, bg=bg_color)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        # Submit Button
        submit_btn = tk.Button(
            button_frame,
            text="CREATE APPOINTMENT",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=25,
            height=2,
            command=self.admin_create_appointment
        )
        submit_btn.pack(side=tk.RIGHT, padx=10)

        # Cancel Button
        cancel_btn = tk.Button(
            button_frame,
            text="CANCEL",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            width=15,
            height=2,
            command=self.add_appt_window.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def edit_appointment(self):
        selected_item = self.appointments_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment to edit")
            return

        appointment_id = self.appointments_tree.item(selected_item)["values"][0]

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT a.appointment_id, 
                        CONCAT(p.first_name, ' ', p.last_name, ' (ID: ', p.patient_id, ')'),
                        CONCAT(d.first_name, ' ', d.last_name, ' (ID: ', d.doctor_id, ')'),
                        a.appointment_date,
                        a.appointment_time,
                        a.status,
                        a.reason
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_id = %s""",
                (appointment_id,)
            )
            appointment_data = cursor.fetchone()

            if not appointment_data:
                messagebox.showerror("Error", "Appointment not found")
                return

            # Create edit window with scrollable frame
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Appointment")
            edit_window.geometry("600x500")
            edit_window.resizable(True, True)

            # Create main container frame
            main_frame = tk.Frame(edit_window)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Create canvas and scrollbar
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            # Configure the canvas
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Pack the canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Title
            tk.Label(
                scrollable_frame,
                text="Edit Appointment",
                font=("Arial", 18, "bold")
            ).pack(pady=10)

            # Form fields
            fields = [
                ("Patient:", appointment_data[1], False),
                ("Doctor:", appointment_data[2], False),
                ("Date (YYYY-MM-DD):", appointment_data[3], True),
                ("Time (HH:MM):", appointment_data[4], True),
                ("Status:", appointment_data[5], True),
                ("Reason:", appointment_data[6], True),
            ]

            self.edit_appointment_entries = {}

            for label, value, editable in fields:
                frame = tk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(frame, text=label, font=("Arial", 12)).pack(side=tk.LEFT)

                if not editable:
                    tk.Label(frame, text=value, font=("Arial", 12)).pack(side=tk.LEFT)
                    continue

                if label == "Status:":
                    entry = ttk.Combobox(
                        frame,
                        values=["Scheduled", "Completed", "Cancelled", "No Show"],
                        font=("Arial", 12),
                        state="readonly"
                    )
                    entry.set(value)
                elif label == "Reason:":
                    entry = tk.Text(
                        frame,
                        font=("Arial", 12),
                        height=4,
                        width=40
                    )
                    entry.insert("1.0", value)
                else:
                    entry = tk.Entry(frame, font=("Arial", 12))
                    entry.insert(0, value)

                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Create consistent key
                key = label.split(":")[0].lower().replace(" ", "_")
                self.edit_appointment_entries[key] = entry

            # Button frame
            button_frame = tk.Frame(scrollable_frame)
            button_frame.pack(pady=20)

            # Submit button
            submit_btn = tk.Button(
                button_frame,
                text="Update Appointment",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.update_appointment(appointment_id, edit_window),
            )
            submit_btn.pack(side=tk.LEFT, padx=10)

            # Cancel button
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                font=("Arial", 12),
                bg="#f44336",
                fg="white",
                command=edit_window.destroy,
            )
            cancel_btn.pack(side=tk.LEFT, padx=10)

            # Add mousewheel scrolling support
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            edit_window.bind("<MouseWheel>", _on_mousewheel)
            scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch appointment data: {e}")

    def update_appointment(self, appointment_id, edit_window):
        try:
            # Get values - adjust based on your actual widget types
            date = self.edit_appointment_entries["date_(yyyy-mm-dd)"].get()  # Entry
            time = self.edit_appointment_entries["time_(hh"].get()  # Entry
            
            # Handle different widget types correctly
            if isinstance(self.edit_appointment_entries["status"], ttk.Combobox):
                status = self.edit_appointment_entries["status"].get()  # Combobox
            else:
                status = self.edit_appointment_entries["status"].get("1.0", "end-1c")  # Text
            
            # Handle reason field based on its widget type
            reason_widget = self.edit_appointment_entries["reason"]
            if isinstance(reason_widget, (ttk.Entry, ttk.Combobox)):
                reason = reason_widget.get()  # Entry or Combobox
            else:
                reason = reason_widget.get("1.0", "end-1c")  # Text widget

            # Validate inputs
            if not all([date, time, status]):
                messagebox.showerror("Error", "Required fields are missing")
                return

            # Update database
            query = """UPDATE appointments 
                    SET date = ?, time = ?, status = ?, reason = ?
                    WHERE appointment_id = ?"""
            self.cursor.execute(query, (date, time, status, reason, appointment_id))
            self.conn.commit()

            # Refresh UI and close window
            self.display_appointments()
            edit_window.destroy()
            messagebox.showinfo("Success", "Appointment updated")

        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {str(e)}")
            
    def delete_appointment(self):
        selected_item = self.appointments_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment to delete")
            return

        appointment_id = self.appointments_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this appointment?"
        )
        if not confirm:
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            cursor.execute(
                "DELETE FROM appointments WHERE appointment_id = %s",
                (appointment_id,)
            )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Appointment deleted successfully!")
            self.load_appointments_data()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to delete appointment: {e}")
        finally:
            if cursor:
                cursor.close()
                
    def create_edit_appointment_form(self, appointment_data):
            self.edit_appointment_entries = {}
            # Date entry
            ttk.Label(edit_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5) # type: ignore
            self.edit_appointment_entries["date_(yyyy-mm-dd)"] = ttk.Entry(edit_frame)
            self.edit_appointment_entries["date_(yyyy-mm-dd)"].grid(row=0, column=1, padx=5, pady=5)
            self.edit_appointment_entries["date_(yyyy-mm-dd)"].insert(0, appointment_data['date'])
            
            # Time entry
            ttk.Label(edit_frame, text="Time (HH:MM):").grid(row=1, column=0, padx=5, pady=5) # type: ignore
            self.edit_appointment_entries["time_(hh"] = ttk.Entry(edit_frame)  # Note: Fix key naming
            self.edit_appointment_entries["time_(hh"].grid(row=1, column=1, padx=5, pady=5)
            self.edit_appointment_entries["time_(hh"].insert(0, appointment_data['time'])
            
            # Status dropdown
            ttk.Label(edit_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5)
            self.edit_appointment_entries["status"] = ttk.Combobox(edit_frame, 
                                                                values=["Scheduled", "Completed", "Cancelled"])
            self.edit_appointment_entries["status"].grid(row=2, column=1, padx=5, pady=5)
            self.edit_appointment_entries["status"].set(appointment_data['status'])
            
            # Reason entry
            ttk.Label(edit_frame, text="Reason:").grid(row=3, column=0, padx=5, pady=5)
            self.edit_appointment_entries["reason"] = ttk.Entry(edit_frame)
            self.edit_appointment_entries["reason"].grid(row=3, column=1, padx=5, pady=5)
            self.edit_appointment_entries["reason"].insert(0, appointment_data.get('reason', ''))
    


    def show_reports(self):
        """Display comprehensive hospital reports with detailed patient and financial data"""
        for widget in self.admin_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.admin_content_frame,
            text="Hospital Analytics Dashboard",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff"
        ).pack(pady=10)

        # Main filter frame
        filter_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        filter_frame.pack(pady=10, fill=tk.X)

        # Report type selection
        tk.Label(filter_frame, text="Report Type:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5, sticky='w')
        self.report_type_var = tk.StringVar(value="Patient Registrations")
        report_types = ttk.Combobox(
            filter_frame,
            textvariable=self.report_type_var,
            font=("Arial", 12),
            values=[
                "Patient Registrations",
                "Appointments Booked",
                "Revenue Details",
                "Patients Treated",
                "Patients by Blood Type",
                "Appointments by Status"
            ],
            state="readonly",
            width=20
        )
        report_types.grid(row=0, column=1, padx=5, sticky='w')

        # Date range filters
        tk.Label(filter_frame, text="From:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=2, padx=5, sticky='e')
        self.from_date_var = tk.StringVar()
        from_date = DateEntry(
            filter_frame,
            textvariable=self.from_date_var,
            font=("Arial", 12),
            date_pattern='yyyy-mm-dd',
            width=12
        )
        from_date.grid(row=0, column=3, padx=5, sticky='w')

        tk.Label(filter_frame, text="To:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=4, padx=5, sticky='e')
        self.to_date_var = tk.StringVar()
        to_date = DateEntry(
            filter_frame,
            textvariable=self.to_date_var,
            font=("Arial", 12),
            date_pattern='yyyy-mm-dd',
            width=12
        )
        to_date.grid(row=0, column=5, padx=5, sticky='w')

        # Additional filters frame
        self.additional_filters_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        self.additional_filters_frame.pack(pady=5, fill=tk.X)

        # Generate button
        filter_btn = tk.Button(
            filter_frame,
            text="Generate Report",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.load_report_data
        )
        filter_btn.grid(row=0, column=6, padx=10)

        # Treeview for report data with proper column configuration
        self.report_tree = ttk.Treeview(
            self.admin_content_frame,
            height=15
        )
        self.report_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Status bar for summary
        self.report_status = tk.Label(
            self.admin_content_frame,
            text="Ready",
            font=("Arial", 10),
            bg="#f0f8ff",
            anchor='w'
        )
        self.report_status.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Action buttons for export
        action_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        tk.Button(
            action_frame,
            text="Export to PDF",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.export_to_pdf
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            action_frame,
            text="Export to Excel",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.export_to_excel
        ).grid(row=0, column=1, padx=10)

        # Set default dates
        self.to_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.from_date_var.set((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))

        # Bind report type change
        report_types.bind("<<ComboboxSelected>>", self.update_additional_filters)
        
        # Load initial filters and data
        self.update_additional_filters()
        self.load_report_data()

    def update_additional_filters(self, event=None):
        """Update additional filters based on report type"""
        for widget in self.additional_filters_frame.winfo_children():
            widget.destroy()

        report_type = self.report_type_var.get()
        
        if report_type == "Revenue Details":
            tk.Label(self.additional_filters_frame, text="Payment Status:", bg="#f0f8ff").pack(side=tk.LEFT, padx=5)
            self.payment_status_var = tk.StringVar(value="All")
            ttk.Combobox(
                self.additional_filters_frame,
                textvariable=self.payment_status_var,
                values=["All", "Paid", "Unpaid"],
                state="readonly",
                width=10
            ).pack(side=tk.LEFT, padx=5)
            
        elif report_type == "Appointments Booked":
            tk.Label(self.additional_filters_frame, text="Status:", bg="#f0f8ff").pack(side=tk.LEFT, padx=5)
            self.appt_status_var = tk.StringVar(value="All")
            ttk.Combobox(
                self.additional_filters_frame,
                textvariable=self.appt_status_var,
                values=["All", "Scheduled", "Completed", "Cancelled"],
                state="readonly",
                width=12
            ).pack(side=tk.LEFT, padx=5)
            
        elif report_type == "Patients Treated":
            tk.Label(self.additional_filters_frame, text="Department:", bg="#f0f8ff").pack(side=tk.LEFT, padx=5)
            self.department_var = tk.StringVar(value="All")
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT DISTINCT department FROM doctors")
            departments = ["All"] + [row[0] for row in cursor.fetchall()]
            ttk.Combobox(
                self.additional_filters_frame,
                textvariable=self.department_var,
                values=departments,
                state="readonly",
                width=15
            ).pack(side=tk.LEFT, padx=5)
            cursor.close()

    def load_report_data(self):
        """Load detailed report data with patient information"""
        report_type = self.report_type_var.get()
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            self.report_data = []

            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)

            # Clear existing columns
            self.report_tree["columns"] = ()

            # Configure treeview columns dynamically based on report type
            if report_type == "Patient Registrations":
                columns = ("ID", "Registration Date", "Patient Name", "Gender", "Age", "Phone", "Email")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=120, anchor=tk.W)
                
                query = """
                    SELECT id, registration_date, name, gender, 
                        TIMESTAMPDIFF(YEAR, dob, CURDATE()) as age,
                        phone, email
                    FROM patients
                    WHERE registration_date BETWEEN %s AND %s
                    ORDER BY registration_date
                """
                cursor.execute(query, (from_date, to_date))
                results = cursor.fetchall()
                
                for row in results:
                    values = (
                        row['id'],
                        row['registration_date'].strftime('%Y-%m-%d'),
                        row['name'],
                        row['gender'],
                        row['age'],
                        row['phone'],
                        row['email']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(text=f"Total Patients Registered: {len(results)}")

            elif report_type == "Appointments Booked":
                columns = ("ID", "Date", "Patient", "Doctor", "Department", "Status", "Reason")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=120, anchor=tk.W)
                
                status = self.appt_status_var.get()
                base_query = """
                    SELECT a.id, a.appointment_date, p.name as patient_name, 
                        d.name as doctor_name, d.department, a.status, a.reason
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE a.appointment_date BETWEEN %s AND %s
                """
                params = [from_date, to_date]
                
                if status != "All":
                    base_query += " AND a.status = %s"
                    params.append(status)
                    
                base_query += " ORDER BY a.appointment_date"
                cursor.execute(base_query, tuple(params))
                results = cursor.fetchall()
                
                for row in results:
                    values = (
                        row['id'],
                        row['appointment_date'].strftime('%Y-%m-%d %H:%M'),
                        row['patient_name'],
                        row['doctor_name'],
                        row['department'],
                        row['status'],
                        row['reason']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(text=f"Total Appointments: {len(results)}")

            elif report_type == "Revenue Details":
                columns = ("ID", "Date", "Patient", "Service", "Amount", "Status", "Payment Method")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=120, anchor=tk.W)
                
                payment_status = self.payment_status_var.get()
                base_query = """
                    SELECT p.id, p.payment_date, pt.name as patient_name, 
                        s.service_name, p.amount, 
                        CASE WHEN p.paid THEN 'Paid' ELSE 'Unpaid' END as status,
                        p.payment_method
                    FROM payments p
                    JOIN patients pt ON p.patient_id = pt.id
                    JOIN services s ON p.service_id = s.id
                    WHERE p.payment_date BETWEEN %s AND %s
                """
                params = [from_date, to_date]
                
                if payment_status != "All":
                    base_query += " AND p.paid = %s"
                    params.append(1 if payment_status == "Paid" else 0)
                    
                base_query += " ORDER BY p.payment_date"
                cursor.execute(base_query, tuple(params))
                results = cursor.fetchall()
                
                total_amount = sum(row['amount'] for row in results)
                paid_amount = sum(row['amount'] for row in results if row['status'] == "Paid")
                
                for row in results:
                    values = (
                        row['id'],
                        row['payment_date'].strftime('%Y-%m-%d'),
                        row['patient_name'],
                        row['service_name'],
                        f"${row['amount']:.2f}",
                        row['status'],
                        row['payment_method']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(
                    text=f"Total Revenue: ${total_amount:.2f} | Paid: ${paid_amount:.2f} | Unpaid: ${total_amount-paid_amount:.2f}"
                )

            elif report_type == "Patients Treated":
                columns = ("ID", "Date", "Patient", "Doctor", "Department", "Diagnosis", "Treatment")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=150, anchor=tk.W)
                
                department = self.department_var.get()
                base_query = """
                    SELECT t.id, t.treatment_date, p.name as patient_name, 
                        d.name as doctor_name, d.department, 
                        t.diagnosis, t.treatment
                    FROM treatments t
                    JOIN patients p ON t.patient_id = p.id
                    JOIN doctors d ON t.doctor_id = d.id
                    WHERE t.treatment_date BETWEEN %s AND %s
                """
                params = [from_date, to_date]
                
                if department != "All":
                    base_query += " AND d.department = %s"
                    params.append(department)
                    
                base_query += " ORDER BY t.treatment_date"
                cursor.execute(base_query, tuple(params))
                results = cursor.fetchall()
                
                for row in results:
                    values = (
                        row['id'],
                        row['treatment_date'].strftime('%Y-%m-%d'),
                        row['patient_name'],
                        row['doctor_name'],
                        row['department'],
                        row['diagnosis'],
                        row['treatment']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(text=f"Total Patients Treated: {len(results)}")

            elif report_type == "Patients by Blood Type":
                columns = ("Blood Type", "Count", "Patients")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=120, anchor=tk.W)
                
                query = """
                    SELECT blood_type, COUNT(*) as count, 
                        GROUP_CONCAT(name SEPARATOR ', ') as patients
                    FROM patients
                    WHERE blood_type IS NOT NULL
                    GROUP BY blood_type
                """
                cursor.execute(query)
                results = cursor.fetchall()
                
                total_patients = sum(row['count'] for row in results)
                for row in results:
                    values = (
                        row['blood_type'],
                        row['count'],
                        row['patients']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(text=f"Total Patients with Blood Type Data: {total_patients}")

            elif report_type == "Appointments by Status":
                columns = ("Status", "Count", "Patients")
                self.report_tree["columns"] = columns
                for col in columns:
                    self.report_tree.heading(col, text=col, anchor=tk.W)  # Left-aligned headings
                    self.report_tree.column(col, width=120, anchor=tk.W)
                
                query = """
                    SELECT status, COUNT(*) as count, 
                        GROUP_CONCAT(p.name SEPARATOR ', ') as patients
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    GROUP BY status
                """
                cursor.execute(query)
                results = cursor.fetchall()
                
                total_appointments = sum(row['count'] for row in results)
                for row in results:
                    values = (
                        row['status'],
                        row['count'],
                        row['patients']
                    )
                    self.report_tree.insert("", tk.END, values=values)
                    self.report_data.append(values)
                    
                self.report_status.config(text=f"Total Appointments: {total_appointments}")

        except Error as e:
            messagebox.showerror("Database Error", 
                f"Failed to load report data: {e}\n\nPlease check your database connection and table structure.")
        finally:
            cursor.close()

    def export_to_pdf(self):
        report_type = self.report_type_var.get()
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF Report"
        )
        if not file_path:
            return

        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            header_style = styles['Heading2']
            normal_style = styles['BodyText']
            
            # Title
            title_text = f"Hospital Report: {report_type}"
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 12))
            
            # Date range
            date_range = f"Date Range: {from_date} to {to_date}"
            elements.append(Paragraph(date_range, header_style))
            elements.append(Spacer(1, 12))
            
            # Get column names from treeview
            columns = self.report_tree["columns"]
            
            # Prepare table data
            table_data = []
            
            # Add column headers
            headers = [Paragraph(col, header_style) for col in columns]
            table_data.append(headers)
            
            # Add data rows
            for item in self.report_tree.get_children():
                row = []
                for col in columns:
                    cell_value = self.report_tree.item(item, 'values')[columns.index(col)]
                    row.append(Paragraph(str(cell_value), normal_style))
                table_data.append(row)
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b5998')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Add summary from status bar
            summary = Paragraph(self.report_status.cget("text"), normal_style)
            elements.append(summary)
            
            # Add timestamp
            timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style)
            elements.append(timestamp)
            
            # Build PDF
            doc.build(elements)
            messagebox.showinfo("Success", f"PDF report saved successfully at:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def export_to_excel(self):
        """Export the current report to Excel with professional formatting"""
        report_type = self.report_type_var.get()
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel Report"
        )
        if not file_path:
            return

        try:
            # Create a workbook and add a worksheet
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = report_type[:31]  # Excel sheet name limit
            
            # Get column names from treeview
            columns = self.report_tree["columns"]
            
            # Write headers
            for col_num, column in enumerate(columns, 1):
                sheet.cell(row=1, column=col_num, value=column)
            
            # Write data rows
            for row_num, item in enumerate(self.report_tree.get_children(), 2):
                for col_num, col in enumerate(columns, 1):
                    cell_value = self.report_tree.item(item, 'values')[columns.index(col)]
                    sheet.cell(row=row_num, column=col_num, value=cell_value)
            
            # Apply formatting
            header_fill = PatternFill(start_color='3B5998', end_color='3B5998', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            border = Border(left=Side(style='thin'), 
                        right=Side(style='thin'), 
                        top=Side(style='thin'), 
                        bottom=Side(style='thin'))
            
            # Format headers
            for cell in sheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
            
            # Format data rows
            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    cell.border = border
            
            # Auto-size columns
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                sheet.column_dimensions[column_letter].width = adjusted_width
            
            # Add metadata
            sheet.cell(row=len(list(self.report_tree.get_children()))+3, column=1, 
                    value=f"Date Range: {from_date} to {to_date}")
            sheet.cell(row=len(list(self.report_tree.get_children()))+4, column=1, 
                    value=self.report_status.cget("text"))
            sheet.cell(row=len(list(self.report_tree.get_children()))+5, column=1, 
                    value=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Save workbook
            workbook.save(file_path)
            messagebox.showinfo("Success", f"Excel report saved successfully at:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Excel file: {str(e)}")
            
    def admin_create_appointment(self):
        try:
            # Get selected patient and extract ID
            patient_str = self.patient_var.get()
            if not patient_str:
                raise ValueError("Please select a patient")
            patient_id = int(patient_str.split("(ID: ")[1].split(")")[0])
            
            # Get selected doctor and extract ID
            doctor_str = self.doctor_var.get()
            if not doctor_str:
                raise ValueError("Please select a doctor")
            doctor_id = int(doctor_str.split("(ID: ")[1].split(")")[0])
            
            # Get other fields
            date = self.date_var.get()
            time = self.time_var.get()
            status = self.status_var.get()
            reason = self.reason_text.get("1.0", tk.END).strip()
            
            

            # Validate inputs
            if not all([patient_id, doctor_id, date, time, status]):
                raise ValueError("All fields are required")

            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")

            # Check if time slot is available
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT appointment_id FROM appointments 
                WHERE doctor_id = %s 
                AND appointment_date = %s 
                AND appointment_time = %s
                AND status != 'Cancelled'
            """, (doctor_id, date, time))
            
            if cursor.fetchone():
                raise ValueError("This time slot is already booked")

            # Create the appointment
            cursor.execute("""
                INSERT INTO appointments (
                    patient_id, 
                    doctor_id, 
                    appointment_date, 
                    appointment_time, 
                    status, 
                    reason
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, date, time, status, reason))
            
            self.db_connection.commit()
            messagebox.showinfo("Success", "Appointment created successfully!")
            self.add_appt_window.destroy()
            
            # Refresh appointments list if available
            if hasattr(self, 'load_appointments_data'):
                self.load_appointments_data()
                
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to create appointment: {str(e)}")
            
    def update_appointment_status(self, appointment_id, new_status):
        try:
            query = "UPDATE appointments SET status = %s WHERE id = %s"
            values = (new_status, appointment_id)
            self.db_cursor.execute(query, values)
            self.db_connection.commit()
            messagebox.showinfo("Success", "Appointment status updated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")

    def generate_report(self):
        report_type = self.report_type.get()
        start_date = self.report_start_date.get()
        end_date = self.report_end_date.get()

        # Validate dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start_date_obj > end_date_obj:
                messagebox.showerror("Error", "Start date cannot be after end date")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        try:
            cursor = self.db_connection.cursor()
            report_content = ""
            
            if report_type == "Appointments by Date":
                cursor.execute(
                    """SELECT appointment_date, COUNT(*) as count, 
                          SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                          SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
                    FROM appointments
                    WHERE appointment_date BETWEEN %s AND %s
                    GROUP BY appointment_date
                    ORDER BY appointment_date""",
                    (start_date, end_date)
                )
                results = cursor.fetchall()
                
                report_content = "Appointments by Date Report\n"
                report_content += f"Date Range: {start_date} to {end_date}\n\n"
                report_content += "Date\t\tTotal\tCompleted\tCancelled\n"
                report_content += "-" * 50 + "\n"
                
                for row in results:
                    report_content += f"{row[0]}\t{row[1]}\t{row[2]}\t\t{row[3]}\n"
                    
            elif report_type == "Appointments by Doctor":
                cursor.execute(
                    """SELECT CONCAT(d.first_name, ' ', d.last_name), 
                          COUNT(*) as count, 
                          SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
                    FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                    WHERE appointment_date BETWEEN %s AND %s
                    GROUP BY d.doctor_id
                    ORDER BY count DESC""",
                    (start_date, end_date)
                )
                results = cursor.fetchall()
                
                report_content = "Appointments by Doctor Report\n"
                report_content += f"Date Range: {start_date} to {end_date}\n\n"
                report_content += "Doctor\t\t\tTotal\tCompleted\n"
                report_content += "-" * 50 + "\n"
                
                for row in results:
                    report_content += f"{row[0]}\t{row[1]}\t{row[2]}\n"
                    
            elif report_type == "Patient Demographics":
                # Age groups
                cursor.execute(
                    """SELECT 
                          SUM(CASE WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18 THEN 1 ELSE 0 END) as under_18,
                          SUM(CASE WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 18 AND 35 THEN 1 ELSE 0 END) as 18_35,
                          SUM(CASE WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 36 AND 55 THEN 1 ELSE 0 END) as 36_55,
                          SUM(CASE WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) > 55 THEN 1 ELSE 0 END) as over_55
                    FROM patients"""
                )
                age_groups = cursor.fetchone()
                
                # Gender distribution
                cursor.execute(
                    """SELECT gender, COUNT(*) 
                    FROM patients 
                    GROUP BY gender"""
                )
                genders = cursor.fetchall()
                
                # Blood type distribution
                cursor.execute(
                    """SELECT blood_type, COUNT(*) 
                    FROM patients 
                    WHERE blood_type IS NOT NULL
                    GROUP BY blood_type"""
                )
                blood_types = cursor.fetchall()
                
                report_content = "Patient Demographics Report\n\n"
                report_content += "Age Groups:\n"
                report_content += f"Under 18: {age_groups[0]}\n"
                report_content += f"18-35: {age_groups[1]}\n"
                report_content += f"36-55: {age_groups[2]}\n"
                report_content += f"Over 55: {age_groups[3]}\n\n"
                
                report_content += "Gender Distribution:\n"
                for gender in genders:
                    report_content += f"{gender[0]}: {gender[1]}\n"
                report_content += "\n"
                
                report_content += "Blood Type Distribution:\n"
                for blood_type in blood_types:
                    report_content += f"{blood_type[0]}: {blood_type[1]}\n"
                    
            elif report_type == "Revenue Report":
                cursor.execute(
                    """SELECT 
                          SUM(CASE WHEN payment_status = 'Paid' THEN amount ELSE 0 END) as total_paid,
                          SUM(CASE WHEN payment_status = 'Pending' THEN amount ELSE 0 END) as total_pending,
                          COUNT(*) as total_bills
                    FROM billing
                    WHERE bill_date BETWEEN %s AND %s""",
                    (start_date, end_date)
                )
                billing = cursor.fetchone()
                
                report_content = "Revenue Report\n"
                report_content += f"Date Range: {start_date} to {end_date}\n\n"
                report_content += f"Total Paid: ${billing[0]:.2f}\n"
                report_content += f"Total Pending: ${billing[1]:.2f}\n"
                report_content += f"Total Bills: {billing[2]}\n"
                report_content += f"Total Revenue: ${billing[0] + billing[1]:.2f}\n"
            
            # Display report
            self.report_text.config(state=tk.NORMAL)
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report_content)
            self.report_text.config(state=tk.DISABLED)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to generate report: {e}")

    def show_system_settings(self):
            # Clear content frame
            for widget in self.admin_content_frame.winfo_children():
                widget.destroy()

            tk.Label(
                self.admin_content_frame,
                text="System Settings",
                font=("Arial", 20, "bold"),
                bg="#f0f8ff",
            ).pack(pady=10)

            # Settings frame
            settings_frame = tk.Frame(self.admin_content_frame, bg="#f0f8ff")
            settings_frame.pack(pady=20)

            # Business hours setting
            tk.Label(
                settings_frame,
                text="Business Hours:",
                font=("Arial", 12, "bold"),
                bg="#f0f8ff"
            ).grid(row=0, column=0, pady=5, sticky="w")

            # Start time
            tk.Label(settings_frame, text="Opening Time:", font=("Arial", 12), bg="#f0f8ff").grid(row=1, column=0, pady=5)
            self.opening_time = tk.Entry(settings_frame, font=("Arial", 12))
            self.opening_time.grid(row=1, column=1, pady=5)
            self.opening_time.insert(0, "08:00")

            # End time
            tk.Label(settings_frame, text="Closing Time:", font=("Arial", 12), bg="#f0f8ff").grid(row=2, column=0, pady=5)
            self.closing_time = tk.Entry(settings_frame, font=("Arial", 12))
            self.closing_time.grid(row=2, column=1, pady=5)
            self.closing_time.insert(0, "17:00")

            # Appointment duration
            tk.Label(
                settings_frame,
                text="Default Appointment Duration (minutes):",
                font=("Arial", 12),
                bg="#f0f8ff"
            ).grid(row=3, column=0, pady=5)
            self.appointment_duration = tk.Entry(settings_frame, font=("Arial", 12))
            self.appointment_duration.grid(row=3, column=1, pady=5)
            self.appointment_duration.insert(0, "30")

            # Save button
            save_btn = tk.Button(
                settings_frame,
                text="Save Settings",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=self.save_system_settings,
            )
            save_btn.grid(row=4, column=0, columnspan=2, pady=20)

    def save_system_settings(self):
            opening_time = self.opening_time.get()
            closing_time = self.closing_time.get()
            duration = self.appointment_duration.get()

            # Validate inputs
            try:
                datetime.strptime(opening_time, "%H:%M")
                datetime.strptime(closing_time, "%H:%M")
                int(duration)
            except ValueError:
                messagebox.showerror("Error", "Invalid input format. Time should be HH:MM and duration should be a number")
                return

            # In a real application, you would save these settings to a database or config file
            messagebox.showinfo("Success", "Settings saved successfully (not persisted in this demo)")
        
    def show_doctor_dashboard(self, user_id):
         # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Doctor dashboard frame
        dashboard_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(dashboard_frame, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)

        # Get doctor's name
        doctor_name = ""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT first_name, last_name FROM doctors WHERE user_id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                doctor_name = f"{result[0]} {result[1]}"
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch doctor data: {e}")

        tk.Label(
            header_frame,
            text=f"Doctor Dashboard - {doctor_name}",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=20)

        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.show_login_screen,
        )
        logout_btn.pack(side=tk.RIGHT, padx=20)

        # Navigation
        nav_frame = tk.Frame(dashboard_frame, bg="#333", width=200)
        nav_frame.pack(fill=tk.Y, side=tk.LEFT)

        buttons = [
            ("Dashboard", lambda: self.show_doctor_welcome(user_id)),
            ("My Schedule", lambda: self.show_doctor_schedule(user_id)),
            ("My Patients", lambda: self.show_doctor_patients(user_id)),
            ("Medical Records", lambda: self.show_doctor_medical_records(user_id)),
        ]

        for text, command in buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 12),
                bg="#333",
                fg="white",
                relief=tk.FLAT,
                command=command,
            ).pack(fill=tk.X, pady=2)

        # Main content area
        self.doctor_content_frame = tk.Frame(dashboard_frame, bg="#f0f8ff")
        self.doctor_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show default view
        self.show_doctor_welcome(user_id)

    def show_doctor_welcome(self, user_id):
        # Clear content frame
        for widget in self.doctor_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.doctor_content_frame,
            text="Welcome, Doctor",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=50)

        # Display today's appointments count
        try:
            cursor = self.db_connection.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get total appointments
            cursor.execute(
                """SELECT COUNT(*) FROM appointments 
                WHERE doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                AND appointment_date = %s""",
                (user_id, today)
            )
            today_appointments = cursor.fetchone()[0]
            
            # Get completed appointments
            cursor.execute(
                """SELECT COUNT(*) FROM appointments 
                WHERE doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                AND appointment_date = %s AND status = 'Completed'""",
                (user_id, today)
            )
            completed_appointments = cursor.fetchone()[0]
            
            # Display stats
            stats_frame = tk.Frame(self.doctor_content_frame, bg="#f0f8ff")
            stats_frame.pack()
            
            tk.Label(
                stats_frame,
                text="Today's Appointments:",
                font=("Arial", 14),
                bg="#f0f8ff"
            ).grid(row=0, column=0, padx=10, pady=5, sticky="e")
            
            tk.Label(
                stats_frame,
                text=str(today_appointments),
                font=("Arial", 14, "bold"),
                bg="#f0f8ff"
            ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            tk.Label(
                stats_frame,
                text="Completed:",
                font=("Arial", 14),
                bg="#f0f8ff"
            ).grid(row=1, column=0, padx=10, pady=5, sticky="e")
            
            tk.Label(
                stats_frame,
                text=str(completed_appointments),
                font=("Arial", 14, "bold"),
                bg="#f0f8ff"
            ).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch appointment data: {e}")

    def show_doctor_schedule(self, user_id):
        # Clear content frame
        for widget in self.doctor_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.doctor_content_frame,
            text="My Schedule",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Date filter
        filter_frame = tk.Frame(self.doctor_content_frame, bg="#f0f8ff")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Date:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.doctor_schedule_date = tk.Entry(filter_frame, font=("Arial", 12))
        self.doctor_schedule_date.grid(row=0, column=1, padx=5)
        self.doctor_schedule_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        filter_btn = tk.Button(
            filter_frame,
            text="Filter",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=lambda: self.load_doctor_schedule(user_id),
        )
        filter_btn.grid(row=0, column=2, padx=10)

        # Appointments table
        columns = ("ID", "Patient", "Time", "Status", "Reason")
        self.doctor_schedule_tree = ttk.Treeview(
            self.doctor_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.doctor_schedule_tree.heading(col, text=col)
            self.doctor_schedule_tree.column(col, width=150, anchor=tk.CENTER)

        self.doctor_schedule_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Action buttons frame
        action_frame = tk.Frame(self.doctor_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        complete_btn = tk.Button(
            action_frame,
            text="Mark as Completed",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.update_appointment_status(user_id, "Completed"),
        )
        complete_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(
            action_frame,
            text="Cancel Appointment",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=lambda: self.update_appointment_status(user_id, "Cancelled"),
        )
        cancel_btn.grid(row=0, column=1, padx=10)

        # Load initial schedule
        self.load_doctor_schedule(user_id)

    def load_doctor_schedule(self, user_id):
        date = self.doctor_schedule_date.get()

        # Validate date
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT a.appointment_id, 
                          CONCAT(p.first_name, ' ', p.last_name),
                          a.appointment_time,
                          a.status,
                          a.reason
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                AND a.appointment_date = %s
                ORDER BY a.appointment_time""",
                (user_id, date)
            )
            appointments = cursor.fetchall()

            # Clear existing data
            for item in self.doctor_schedule_tree.get_children():
                self.doctor_schedule_tree.delete(item)

            # Insert new data
            for appointment in appointments:
                self.doctor_schedule_tree.insert("", tk.END, values=appointment)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load schedule: {e}")

    def update_appointment_status(self, user_id, status):
        selected_item = self.doctor_schedule_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment")
            return

        appointment_id = self.doctor_schedule_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", f"Are you sure you want to mark this appointment as {status}?"
        )
        if not confirm:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE appointments SET status = %s WHERE appointment_id = %s",
                (status, appointment_id)
            )

            self.db_connection.commit()

            messagebox.showinfo("Success", f"Appointment marked as {status}")
            self.load_doctor_schedule(user_id)

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update appointment: {e}")

    def show_doctor_patients(self, user_id):
        # Clear content frame
        for widget in self.doctor_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.doctor_content_frame,
            text="My Patients",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Patients table
        columns = ("ID", "Name", "Gender", "Age", "Last Visit")
        self.doctor_patients_tree = ttk.Treeview(
            self.doctor_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.doctor_patients_tree.heading(col, text=col)
            self.doctor_patients_tree.column(col, width=120, anchor=tk.CENTER)

        self.doctor_patients_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load patients data
        self.load_doctor_patients(user_id)

        # Action buttons frame
        action_frame = tk.Frame(self.doctor_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        view_records_btn = tk.Button(
            action_frame,
            text="View Medical Records",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.view_patient_records,
        )
        view_records_btn.grid(row=0, column=0, padx=10)

    def load_doctor_patients(self, user_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT DISTINCT p.patient_id, 
                          CONCAT(p.first_name, ' ', p.last_name),
                          p.gender, 
                          TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()),
                          MAX(a.appointment_date)
                FROM patients p
                JOIN appointments a ON p.patient_id = a.patient_id
                WHERE a.doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                GROUP BY p.patient_id
                ORDER BY p.last_name, p.first_name""",
                (user_id,)
            )
            patients = cursor.fetchall()

            # Clear existing data
            for item in self.doctor_patients_tree.get_children():
                self.doctor_patients_tree.delete(item)

            # Insert new data
            for patient in patients:
                self.doctor_patients_tree.insert("", tk.END, values=patient)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load patients: {e}")

    def view_patient_records(self):
        selected_item = self.doctor_patients_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient")
            return

        patient_id = self.doctor_patients_tree.item(selected_item)["values"][0]
        self.show_doctor_medical_records(self.current_user_id, patient_id)

    def show_doctor_medical_records(self, user_id, patient_id=None):
        # Clear content frame
        for widget in self.doctor_content_frame.winfo_children():
            widget.destroy()

        if patient_id is None:
            # Show list of patients to select from
            tk.Label(
                self.doctor_content_frame,
                text="Select a patient to view medical records",
                font=("Arial", 16, "bold"),
                bg="#f0f8ff",
            ).pack(pady=10)

            # Patients table
            columns = ("ID", "Name", "Gender", "Age")
            self.records_patients_tree = ttk.Treeview(
                self.doctor_content_frame, columns=columns, show="headings", height=15
            )

            for col in columns:
                self.records_patients_tree.heading(col, text=col)
                self.records_patients_tree.column(col, width=120, anchor=tk.CENTER)

            self.records_patients_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Load patients data
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    """SELECT DISTINCT p.patient_id, 
                              CONCAT(p.first_name, ' ', p.last_name),
                              p.gender, 
                              TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE())
                    FROM patients p
                    JOIN appointments a ON p.patient_id = a.patient_id
                    WHERE a.doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                    GROUP BY p.patient_id
                    ORDER BY p.last_name, p.first_name""",
                    (user_id,)
                )
                patients = cursor.fetchall()

                # Insert data
                for patient in patients:
                    self.records_patients_tree.insert("", tk.END, values=patient)

                # Bind double click to view records
                self.records_patients_tree.bind(
                    "<Double-1>",
                    lambda e: self.show_doctor_medical_records(
                        user_id,
                        self.records_patients_tree.item(self.records_patients_tree.selection())["values"][0]
                    ))
                
            except Error as e:
                messagebox.showerror("Database Error", f"Failed to load patients: {e}")

            return

        # Show medical records for specific patient
        try:
            cursor = self.db_connection.cursor()
            
            # Get patient info
            cursor.execute(
                """SELECT CONCAT(first_name, ' ', last_name), 
                          date_of_birth, gender, blood_type
                FROM patients
                WHERE patient_id = %s""",
                (patient_id,)
            )
            patient_info = cursor.fetchone()
            
            if not patient_info:
                messagebox.showerror("Error", "Patient not found")
                return

            # Display patient info
            info_frame = tk.Frame(self.doctor_content_frame, bg="#f0f8ff")
            info_frame.pack(fill=tk.X, pady=10)

            tk.Label(
                info_frame,
                text=f"Medical Records for {patient_info[0]}",
                font=("Arial", 16, "bold"),
                bg="#f0f8ff",
            ).pack(side=tk.LEFT, padx=20)

            tk.Label(
                info_frame,
                text=f"DOB: {patient_info[1]} | Gender: {patient_info[2]} | Blood Type: {patient_info[3] or 'Unknown'}",
                font=("Arial", 12),
                bg="#f0f8ff",
            ).pack(side=tk.LEFT, padx=20)

            # Add record button
            add_btn = tk.Button(
                self.doctor_content_frame,
                text="Add Medical Record",
                font=("Arial", 12),
                bg="#4CAF50",
                fg="white",
                command=lambda: self.show_add_medical_record_form(patient_id, user_id),
            )
            add_btn.pack(pady=10)

            # Medical records table
            columns = ("Date", "Diagnosis", "Treatment", "Notes")
            self.medical_records_tree = ttk.Treeview(
                self.doctor_content_frame, columns=columns, show="headings", height=15
            )

            for col in columns:
                self.medical_records_tree.heading(col, text=col)
                self.medical_records_tree.column(col, width=150, anchor=tk.CENTER)

            self.medical_records_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Load medical records
            cursor.execute(
                """SELECT record_date, diagnosis, treatment, notes
                FROM medical_records
                WHERE patient_id = %s AND doctor_id = (SELECT doctor_id FROM doctors WHERE user_id = %s)
                ORDER BY record_date DESC""",
                (patient_id, user_id)
            )
            records = cursor.fetchall()

            # Insert records
            for record in records:
                self.medical_records_tree.insert("", tk.END, values=record)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load medical records: {e}")
            
    def show_add_medical_record_form(self, patient_id, user_id):
        # Create a new top-level window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Medical Record")
        add_window.geometry("500x500")

        tk.Label(add_window, text="Add Medical Record", font=("Arial", 18, "bold")).pack(pady=10)

        # Form fields
        fields = [
            ("Date (YYYY-MM-DD):", "entry"),
            ("Diagnosis:", "entry"),
            ("Treatment:", "entry"),
            ("Notes:", "text"),
        ]

        self.medical_record_entries = {}

        for i, (label, field_type) in enumerate(fields):
            tk.Label(add_window, text=label, font=("Arial", 12)).pack(pady=5)

            if field_type == "entry":
                entry = tk.Entry(add_window, font=("Arial", 12))
                entry.pack(pady=5, ipadx=20)
                key = label.lower().split(":")[0].strip().replace(" ", "_").replace("(", "").replace(")", "")
                self.medical_record_entries[key] = entry

            elif field_type == "text":
                text = tk.Text(add_window, font=("Arial", 12), height=5, width=40)
                text.pack(pady=5)
                self.medical_record_entries[label.split(":")[0].lower().replace(" ", "_")] = text

        # Set default date to today
        for key in self.medical_record_entries:
            if "date" in key:
                self.medical_record_entries[key].insert(0, datetime.now().strftime("%Y-%m-%d"))
                break



                # Submit button
        submit_btn = tk.Button(
            add_window,
            text="Add Record",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.add_medical_record(patient_id, user_id, add_window),
        )
        submit_btn.pack(pady=20)


    def add_medical_record(self, patient_id, user_id, window):
        # Get all form data
        date = self.medical_record_entries["date_yyyy-mm-dd"].get()
        diagnosis = self.medical_record_entries["diagnosis"].get()
        treatment = self.medical_record_entries["treatment"].get()
        notes = self.medical_record_entries["notes"].get("1.0", tk.END).strip()

        # Validate inputs
        if not all([date, diagnosis]):
            messagebox.showerror("Error", "Date and Diagnosis are required")
            return

        cursor = None
        try:
            # Validate date
            datetime.strptime(date, "%Y-%m-%d")

            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get doctor_id
            cursor.execute(
                "SELECT doctor_id FROM doctors WHERE user_id = %s",
                (user_id,)
            )
            doctor_id = cursor.fetchone()[0]

            # Insert medical record
            cursor.execute(
                """INSERT INTO medical_records 
                (patient_id, doctor_id, record_date, diagnosis, treatment, notes) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (patient_id, doctor_id, date, diagnosis, treatment, notes),
            )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Medical record added successfully!")
            window.destroy()
            self.show_doctor_medical_records(user_id, patient_id)

        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to add medical record: {e}")
        finally:
            if cursor:
                cursor.close()

    def show_patient_dashboard(self, user_id):
      # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Patient dashboard frame
        dashboard_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(dashboard_frame, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)

        # Get patient's name
        patient_name = ""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT first_name, last_name FROM patients WHERE user_id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                patient_name = f"{result[0]} {result[1]}"
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch patient data: {e}")

        tk.Label(
            header_frame,
            text=f"Patient Dashboard - {patient_name}",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=20)

        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.show_login_screen,
        )
        logout_btn.pack(side=tk.RIGHT, padx=20)

        # Navigation
        nav_frame = tk.Frame(dashboard_frame, bg="#333", width=200)
        nav_frame.pack(fill=tk.Y, side=tk.LEFT)

        buttons = [
            ("Dashboard", lambda: self.show_patient_welcome(user_id)),
            ("My Profile", lambda: self.show_patient_profile(user_id)),
            ("My Appointments", lambda: self.show_patient_appointments(user_id)),
            ("Medical Records", lambda: self.show_patient_medical_records(user_id)),
            ("Billing", lambda: self.show_patient_billing(user_id)),
            ]

        for text, command in buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 12),
                bg="#333",
                fg="white",
                relief=tk.FLAT,
                command=command,
            ).pack(fill=tk.X, pady=2)

        # Main content area
        self.patient_content_frame = tk.Frame(dashboard_frame, bg="#f0f8ff")
        self.patient_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show default view
        self.show_patient_welcome(user_id)


    def show_patient_welcome(self, user_id):
        # Clear content frame
        for widget in self.patient_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.patient_content_frame,
            text="Welcome to Your Dashboard",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=50)

        # Display upcoming appointment
        try:
            cursor = self.db_connection.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get next appointment
            cursor.execute(
                """SELECT a.appointment_date, a.appointment_time, 
                          CONCAT(d.first_name, ' ', d.last_name), a.status
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = (SELECT patient_id FROM patients WHERE user_id = %s)
                AND (a.appointment_date > %s OR (a.appointment_date = %s AND a.status = 'Scheduled'))
                ORDER BY a.appointment_date, a.appointment_time
                LIMIT 1""",
                (user_id, today, today)
            )
            next_appointment = cursor.fetchone()
            
            # Display next appointment info
            if next_appointment:
                appointment_frame = tk.Frame(self.patient_content_frame, bg="#f0f8ff")
                appointment_frame.pack(pady=10)
                
                tk.Label(
                    appointment_frame,
                    text="Your Next Appointment:",
                    font=("Arial", 14, "bold"),
                    bg="#f0f8ff"
                ).grid(row=0, column=0, columnspan=2, pady=5)
                
                tk.Label(
                    appointment_frame,
                    text="Date:",
                    font=("Arial", 12),
                    bg="#f0f8ff"
                ).grid(row=1, column=0, pady=5, sticky="e")
                
                tk.Label(
                    appointment_frame,
                    text=next_appointment[0],
                    font=("Arial", 12, "bold"),
                    bg="#f0f8ff"
                ).grid(row=1, column=1, pady=5, sticky="w")
                
                tk.Label(
                    appointment_frame,
                    text="Time:",
                    font=("Arial", 12),
                    bg="#f0f8ff"
                ).grid(row=2, column=0, pady=5, sticky="e")
                
                tk.Label(
                    appointment_frame,
                    text=next_appointment[1],
                    font=("Arial", 12, "bold"),
                    bg="#f0f8ff"
                ).grid(row=2, column=1, pady=5, sticky="w")
                
                tk.Label(
                    appointment_frame,
                    text="Doctor:",
                    font=("Arial", 12),
                    bg="#f0f8ff"
                ).grid(row=3, column=0, pady=5, sticky="e")
                
                tk.Label(
                    appointment_frame,
                    text=next_appointment[2],
                    font=("Arial", 12, "bold"),
                    bg="#f0f8ff"
                ).grid(row=3, column=1, pady=5, sticky="w")
                
                tk.Label(
                    appointment_frame,
                    text="Status:",
                    font=("Arial", 12),
                    bg="#f0f8ff"
                ).grid(row=4, column=0, pady=5, sticky="e")
                
                tk.Label(
                    appointment_frame,
                    text=next_appointment[3],
                    font=("Arial", 12, "bold"),
                    bg="#f0f8ff"
                ).grid(row=4, column=1, pady=5, sticky="w")
            else:
                tk.Label(
                    self.patient_content_frame,
                    text="You have no upcoming appointments",
                    font=("Arial", 12),
                    bg="#f0f8ff"
                ).pack(pady=10)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch appointment data: {e}")
            
    def show_patient_profile(self, user_id):
        # Clear content frame
        for widget in self.patient_content_frame.winfo_children():
            widget.destroy()

        # Main profile container
        profile_container = tk.Frame(self.patient_content_frame, bg="#f8f9fa", padx=20, pady=20)
        profile_container.pack(fill=tk.BOTH, expand=True)

        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.username 
                FROM patients p 
                JOIN users u ON p.user_id = u.user_id 
                WHERE p.user_id = %s
            """, (user_id,))
            patient_data = cursor.fetchone()

            if patient_data:
                # Profile Header with icon
                header_frame = tk.Frame(profile_container, bg="#ffffff", bd=2, relief=tk.GROOVE)
                header_frame.pack(fill=tk.X, pady=(0, 20))
                
                tk.Label(
                    header_frame,
                    text=" My Profile",
                    font=("Arial", 16, "bold"),
                    bg="#ffffff",
                    fg="#2c3e50",
                    padx=10,
                    pady=10
                ).pack(side=tk.LEFT)
                
                # Edit button with icon
                edit_btn = tk.Button(
                    header_frame,
                    text="✏️ Edit",
                    font=("Arial", 10),
                    bg="#3498db",
                    fg="white",
                    bd=0,
                    command=lambda: self.show_edit_profile(user_id)
                )
                edit_btn.pack(side=tk.RIGHT, padx=10)

                # Profile content in card style
                content_frame = tk.Frame(profile_container, bg="#ffffff", bd=2, relief=tk.GROOVE)
                content_frame.pack(fill=tk.BOTH, expand=True)

                # Personal Info Section
                personal_frame = tk.LabelFrame(
                    content_frame,
                    text=" Personal Information ",
                    font=("Arial", 12, "bold"),
                    bg="#ffffff",
                    fg="#2c3e50",
                    padx=10,
                    pady=10
                )
                personal_frame.pack(fill=tk.X, padx=10, pady=10)

                # Profile picture placeholder (you can replace with actual image)
                profile_pic = tk.Label(
                    personal_frame,
                    text="👤",
                    font=("Arial", 48),
                    bg="#ecf0f1",
                    width=5,
                    height=2,
                    bd=0
                )
                profile_pic.grid(row=0, column=0, rowspan=5, padx=10, pady=10, sticky="n")

                # Patient details
                details = [
                    ("Full Name:", f"{patient_data['first_name']} {patient_data['last_name']}"),
                    ("Date of Birth:", patient_data['date_of_birth']),
                    ("Gender:", patient_data['gender']),
                    ("Blood Type:", patient_data['blood_type'] or "Not specified"),
                    ("Phone:", patient_data['phone']),
                    ("Username:", patient_data['username'])
                ]

                for i, (label, value) in enumerate(details):
                    tk.Label(
                        personal_frame,
                        text=label,
                        font=("Arial", 10, "bold"),
                        bg="#ffffff",
                        fg="#7f8c8d"
                    ).grid(row=i, column=1, sticky="e", padx=5, pady=2)
                    
                    tk.Label(
                        personal_frame,
                        text=value,
                        font=("Arial", 10),
                        bg="#ffffff",
                        fg="#2c3e50"
                    ).grid(row=i, column=2, sticky="w", padx=5, pady=2)

                # Address Section
                address_frame = tk.LabelFrame(
                    content_frame,
                    text=" Address ",
                    font=("Arial", 12, "bold"),
                    bg="#ffffff",
                    fg="#2c3e50",
                    padx=10,
                    pady=10
                )
                address_frame.pack(fill=tk.X, padx=10, pady=10)

                address_text = tk.Text(
                    address_frame,
                    font=("Arial", 10),
                    bg="#ffffff",
                    fg="#2c3e50",
                    height=4,
                    width=50,
                    wrap=tk.WORD,
                    bd=0
                )
                address_text.insert(tk.END, patient_data['address'])
                address_text.config(state=tk.DISABLED)
                address_text.pack(fill=tk.X, padx=5, pady=5)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load profile: {e}")
            
    def update_patient_profile(self, user_id, window):
        # Get all form data using the consistent naming
        # ===== CHANGED THESE LINES =====
        first_name = self.edit_profile_entries["first_name"].get()
        last_name = self.edit_profile_entries["last_name"].get()
        dob = self.edit_profile_entries["date_of_birth"].get()
        gender = self.edit_profile_entries["gender"].get()
        blood_type = self.edit_profile_entries["blood_type"].get()
        phone = self.edit_profile_entries["phone"].get()
        address = self.edit_profile_entries["address"].get("1.0", tk.END).strip()
        username = self.edit_profile_entries["username"].get()
        new_password = self.edit_profile_entries["new_password"].get()
        confirm_password = self.edit_profile_entries["confirm_password"].get()
        # ===== END OF CHANGES =====

        # Validate inputs
        if not all([first_name, last_name, dob, gender, phone, address, username]):
            messagebox.showerror("Error", "All fields except blood type are required")
            return

        if new_password and new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        cursor = None
        try:
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
            
            self.db_connection.start_transaction()
            cursor = self.db_connection.cursor()
            
            # Get patient_id
            cursor.execute("SELECT patient_id FROM patients WHERE user_id = %s", (user_id,))
            patient_id = cursor.fetchone()[0]

            # Check if username exists (excluding current user)
            cursor.execute(
                "SELECT username FROM users WHERE username = %s AND user_id != %s",
                (username, user_id)
            )
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Update patients table
            cursor.execute(
                """UPDATE patients 
                SET first_name = %s, last_name = %s, date_of_birth = %s, 
                    gender = %s, blood_type = %s, phone = %s, address = %s
                WHERE patient_id = %s""",
                (first_name, last_name, dob, gender, 
                blood_type if blood_type else None, phone, address, patient_id)
            )

            # Update users table
            if new_password:
                hashed_password = self.hash_password(new_password)
                cursor.execute(
                    "UPDATE users SET username = %s, password = %s WHERE user_id = %s",
                    (username, hashed_password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = %s WHERE user_id = %s",
                    (username, user_id)
                )

            self.db_connection.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            window.destroy()
            self.show_patient_profile(user_id)  # Refresh profile view

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update profile: {e}")
        finally:
            if cursor:
                cursor.close()
                        
    def show_edit_profile(self, user_id):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")
        edit_window.geometry("600x700")
        edit_window.configure(bg="#f8f9fa")

        # Header
        header = tk.Frame(edit_window, bg="#3498db", height=80)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Edit Profile",
            font=("Arial", 18, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=20)

        # Main form container
        form_container = tk.Frame(edit_window, bg="#f8f9fa", padx=20, pady=20)
        form_container.pack(fill=tk.BOTH, expand=True)

        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.username 
                FROM patients p 
                JOIN users u ON p.user_id = u.user_id 
                WHERE p.user_id = %s
            """, (user_id,))
            patient_data = cursor.fetchone()

            if patient_data:
                # ===== CHANGED THIS SECTION =====
                # Form fields with consistent naming
                fields = [
                    ("First Name", "entry", patient_data['first_name']),
                    ("Last Name", "entry", patient_data['last_name']),
                    ("Date of Birth", "entry", patient_data['date_of_birth']),  # Simplified label
                    ("Gender", "combobox", patient_data['gender'], ["Male", "Female", "Other"]),
                    ("Blood Type", "combobox", patient_data['blood_type'], 
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                    ("Phone", "entry", patient_data['phone']),
                    ("Address", "text", patient_data['address']),
                    ("Username", "entry", patient_data['username']),
                    ("New Password", "password", ""),
                    ("Confirm Password", "password", "")
                ]
                # ===== END OF CHANGES =====

                self.edit_profile_entries = {}

                for i, (label, field_type, default_value, *options) in enumerate(fields):
                    # Field container
                    field_frame = tk.Frame(form_container, bg="#f8f9fa")
                    field_frame.pack(fill=tk.X, pady=5)

                    # Label
                    tk.Label(
                        field_frame,
                        text=label + ":",  # Add colon here for display
                        font=("Arial", 10, "bold"),
                        bg="#f8f9fa",
                        fg="#2c3e50",
                        width=25,
                        anchor="e"
                    ).pack(side=tk.LEFT, padx=5)

                    # Input field
                    if field_type == "entry":
                        entry = tk.Entry(
                            field_frame,
                            font=("Arial", 10),
                            bd=1,
                            relief=tk.SOLID
                        )
                        entry.insert(0, default_value)
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    elif field_type == "combobox":
                        entry = ttk.Combobox(
                            field_frame,
                            font=("Arial", 10),
                            values=options[0],
                            state="readonly"
                        )
                        entry.set(default_value or "")
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    elif field_type == "text":
                        entry = tk.Text(
                            field_frame,
                            font=("Arial", 10),
                            height=4,
                            bd=1,
                            relief=tk.SOLID
                        )
                        entry.insert("1.0", default_value)
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    elif field_type == "password":
                        entry = tk.Entry(
                            field_frame,
                            font=("Arial", 10),
                            show="*",
                            bd=1,
                            relief=tk.SOLID
                        )
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

                    # ===== CHANGED THIS LINE =====
                    field_name = label.lower().replace(" ", "_")
                    self.edit_profile_entries[field_name] = entry
                    # ===== END OF CHANGE =====

                # Button container
                button_frame = tk.Frame(form_container, bg="#f8f9fa", pady=20)
                button_frame.pack(fill=tk.X)

                # Save button
                save_btn = tk.Button(
                    button_frame,
                    text="Save Changes",
                    font=("Arial", 12, "bold"),
                    bg="#2ecc71",
                    fg="white",
                    bd=0,
                    padx=20,
                    pady=5,
                    command=lambda: self.update_patient_profile(user_id, edit_window)
                )
                save_btn.pack(side=tk.RIGHT, padx=10)

                # Cancel button
                cancel_btn = tk.Button(
                    button_frame,
                    text="Cancel",
                    font=("Arial", 12),
                    bg="#e74c3c",
                    fg="white",
                    bd=0,
                    padx=20,
                    pady=5,
                    command=edit_window.destroy
                )
                cancel_btn.pack(side=tk.RIGHT)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load profile: {e}")
            

    def show_patient_appointments(self, user_id):
        # Clear content frame
        for widget in self.patient_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.patient_content_frame,
            text="My Appointments",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # New appointment button
        new_btn = tk.Button(
            self.patient_content_frame,
            text="Schedule New Appointment",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.show_schedule_appointment_form(user_id),
        )
        new_btn.pack(pady=10)

        # Appointments table
        columns = ("ID", "Date", "Time", "Doctor", "Status", "Reason")
        self.patient_appointments_tree = ttk.Treeview(
            self.patient_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.patient_appointments_tree.heading(col, text=col)
            self.patient_appointments_tree.column(col, width=120, anchor=tk.CENTER)

        self.patient_appointments_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load appointments data
        self.load_patient_appointments(user_id)

        # Action buttons frame
        action_frame = tk.Frame(self.patient_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        cancel_btn = tk.Button(
            action_frame,
            text="Cancel Appointment",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=lambda: self.cancel_patient_appointment(user_id),
        )
        cancel_btn.grid(row=0, column=0, padx=10)


    def show_medical_records(patient_id, host, database, user, password):
        """Display comprehensive medical records in a scrollable window"""
        try:
            # Connect to database
            conn = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            
            # Create main window
            window = tk.Toplevel()
            window.title(f"Medical Records - Patient ID: {patient_id}")
            window.geometry("900x600")
            
            # Create main frame with scrollbar
            main_frame = tk.Frame(window)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Fetch patient data
            cursor = conn.cursor(dictionary=True)
            
            # Get patient info
            cursor.execute("""
                SELECT first_name, last_name, date_of_birth, gender, blood_type 
                FROM patients WHERE patient_id = %s
            """, (patient_id,))
            patient_info = cursor.fetchone()
            
            # Display patient info at top
            info_frame = tk.LabelFrame(scrollable_frame, text="Patient Information", padx=10, pady=10)
            info_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(info_frame, text=f"Name: {patient_info['first_name']} {patient_info['last_name']}").pack(anchor="w")
            tk.Label(info_frame, text=f"DOB: {patient_info['date_of_birth']}").pack(anchor="w")
            tk.Label(info_frame, text=f"Gender: {patient_info['gender']}").pack(anchor="w")
            tk.Label(info_frame, text=f"Blood Type: {patient_info['blood_type']}").pack(anchor="w")
            
            # Get medical records with doctor info
            cursor.execute("""
                SELECT mr.*, d.first_name AS doctor_first_name, 
                    d.last_name AS doctor_last_name, d.specialization
                FROM medical_records mr
                JOIN doctors d ON mr.doctor_id = d.doctor_id
                WHERE mr.patient_id = %s
                ORDER BY mr.record_date DESC
            """, (patient_id,))
            medical_records = cursor.fetchall()
            
            # Medical Records Section
            if medical_records:
                med_frame = tk.LabelFrame(scrollable_frame, text="Medical Records", padx=10, pady=10)
                med_frame.pack(fill="x", padx=10, pady=5)
                
                for record in medical_records:
                    record_frame = tk.Frame(med_frame, relief="groove", borderwidth=1, padx=5, pady=5)
                    record_frame.pack(fill="x", pady=3)
                    
                    tk.Label(record_frame, 
                            text=f"Date: {record['record_date']} | Doctor: Dr. {record['doctor_first_name']} {record['doctor_last_name']} ({record['specialization']})",
                            font=('Arial', 10, 'bold')).pack(anchor="w")
                    
                    tk.Label(record_frame, text=f"Diagnosis: {record['diagnosis']}").pack(anchor="w")
                    if record['treatment']:
                        tk.Label(record_frame, text=f"Treatment: {record['treatment']}").pack(anchor="w")
                    if record['notes']:
                        tk.Label(record_frame, text=f"Notes: {record['notes']}").pack(anchor="w")
                    
                    tk.Label(record_frame, text="-"*80, fg="gray").pack(anchor="w")
            else:
                tk.Label(scrollable_frame, text="No medical records found").pack()
            
            # Get appointments
            cursor.execute("""
                SELECT a.*, d.first_name AS doctor_first_name, 
                    d.last_name AS doctor_last_name, d.specialization
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (patient_id,))
            appointments = cursor.fetchall()
            
            # Appointments Section
            if appointments:
                app_frame = tk.LabelFrame(scrollable_frame, text="Appointments", padx=10, pady=10)
                app_frame.pack(fill="x", padx=10, pady=5)
                
                for app in appointments:
                    app_subframe = tk.Frame(app_frame, relief="groove", borderwidth=1, padx=5, pady=5)
                    app_subframe.pack(fill="x", pady=3)
                    
                    tk.Label(app_subframe, 
                            text=f"Date: {app['appointment_date']} {app['appointment_time']} | Status: {app['status'].title()}",
                            font=('Arial', 10, 'bold')).pack(anchor="w")
                    
                    tk.Label(app_subframe, 
                            text=f"Doctor: Dr. {app['doctor_first_name']} {app['doctor_last_name']} ({app['specialization']})").pack(anchor="w")
                    
                    if app['reason']:
                        tk.Label(app_subframe, text=f"Reason: {app['reason']}").pack(anchor="w")
                    
                    tk.Label(app_subframe, text="-"*80, fg="gray").pack(anchor="w")
            
            # Get billing information
            cursor.execute("""
                SELECT b.*, p.payment_id, p.amount AS payment_amount, 
                    p.payment_method, p.payment_date, p.transaction_reference
                FROM billing b
                LEFT JOIN payments p ON b.bill_id = p.bill_id
                WHERE b.patient_id = %s
                ORDER BY b.bill_date DESC
            """, (patient_id,))
            billing_records = cursor.fetchall()
            
            # Billing Section
            if billing_records:
                bill_frame = tk.LabelFrame(scrollable_frame, text="Billing History", padx=10, pady=10)
                bill_frame.pack(fill="x", padx=10, pady=5)
                
                for bill in billing_records:
                    bill_subframe = tk.Frame(bill_frame, relief="groove", borderwidth=1, padx=5, pady=5)
                    bill_subframe.pack(fill="x", pady=3)
                    
                    tk.Label(bill_subframe, 
                            text=f"Bill Date: {bill['bill_date']} | Amount: ${bill['amount']} | Status: {bill['status']}",
                            font=('Arial', 10, 'bold')).pack(anchor="w")
                    
                    if bill['description']:
                        tk.Label(bill_subframe, text=f"Description: {bill['description']}").pack(anchor="w")
                    
                    if bill['payment_id']:
                        tk.Label(bill_subframe, 
                                text=f"Payment: ${bill['payment_amount']} via {bill['payment_method']} on {bill['payment_date']}").pack(anchor="w")
                    
                    tk.Label(bill_subframe, text="-"*80, fg="gray").pack(anchor="w")
            
            # Close database connection
            cursor.close()
            conn.close()
            
        except Error as e:
            error_window = tk.Toplevel()
            error_window.title("Database Error")
            tk.Label(error_window, text=f"Failed to load medical records:\n{str(e)}", fg="red").pack()
            tk.Button(error_window, text="OK", command=error_window.destroy).pack()




            
    def load_patient_appointments(self, user_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT a.appointment_id, a.appointment_date, a.appointment_time,
                        CONCAT(d.first_name, ' ', d.last_name), a.status, a.reason
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = (SELECT patient_id FROM patients WHERE user_id = %s)
                ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
                (user_id,)
            )
            appointments = cursor.fetchall()

            # Clear existing data
            for item in self.patient_appointments_tree.get_children():
                self.patient_appointments_tree.delete(item)

            # Insert new data
            for appointment in appointments:
                self.patient_appointments_tree.insert("", tk.END, values=appointment)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load appointments: {e}")

    def show_schedule_appointment_form(self, user_id):
        # Create appointment booking window
        add_window = tk.Toplevel(self.root)
        add_window.title("Schedule Appointment")
        add_window.geometry("500x500")
        add_window.resizable(False, False)
        
        # Styling
        bg_color = "#f0f8ff"
        add_window.configure(bg=bg_color)
        
        # Header
        header_frame = tk.Frame(add_window, bg="#3498db", height=60)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="Book New Appointment",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)

        # Main form container
        form_frame = tk.Frame(add_window, bg=bg_color, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Doctor Selection
        tk.Label(
            form_frame,
            text="Select Doctor:",
            font=("Arial", 12),
            bg=bg_color
        ).grid(row=0, column=0, pady=5, sticky="e")

        self.doctor_var = tk.StringVar()
        doctor_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.doctor_var,
            font=("Arial", 12),
            state="readonly",
            width=25
        )
        doctor_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        # Load doctors into combobox
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT doctor_id, CONCAT(first_name, ' ', last_name, ' - ', specialization) 
                FROM doctors
            """)
            doctors = cursor.fetchall()
            
            # Format: "Dr. Name - Specialty (ID: 123)"
            doctor_list = [f"{name} (ID: {id})" for id, name in doctors]
            doctor_combobox['values'] = doctor_list
            
            if doctor_list:
                doctor_combobox.current(0)
            else:
                messagebox.showwarning("No Doctors", "No doctors available for appointments")
                add_window.destroy()
                return
                
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load doctors: {e}")
            add_window.destroy()
            return

        # Date Selection
        tk.Label(
            form_frame,
            text="Appointment Date:",
            font=("Arial", 12),
            bg=bg_color
        ).grid(row=1, column=0, pady=5, sticky="e")

        self.date_var = tk.StringVar()
        date_entry = tk.Entry(
            form_frame,
            textvariable=self.date_var,
            font=("Arial", 12),
            width=25
        )
        date_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default to today

        # Time Selection
        tk.Label(
            form_frame,
            text="Appointment Time:",
            font=("Arial", 12),
            bg=bg_color
        ).grid(row=2, column=0, pady=5, sticky="e")

        self.time_var = tk.StringVar()
        time_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.time_var,
            font=("Arial", 12),
            values=["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00"],
            state="readonly",
            width=25
        )
        time_combobox.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        time_combobox.current(0)  # Default to first time slot

        # Reason for Visit
        tk.Label(
            form_frame,
            text="Reason:",
            font=("Arial", 12),
            bg=bg_color
        ).grid(row=3, column=0, pady=5, sticky="ne")

        self.reason_text = tk.Text(
            form_frame,
            font=("Arial", 12),
            height=4,
            width=30,
            wrap=tk.WORD
        )
        self.reason_text.grid(row=3, column=1, pady=5, padx=5, sticky="w")

        # Submit Button
        submit_btn = tk.Button(
            form_frame,
            text="Book Appointment",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            command=lambda: self.schedule_appointment(user_id, add_window)
        )
        submit_btn.grid(row=4, column=1, pady=20, sticky="e")

        # Cancel Button
        cancel_btn = tk.Button(
            form_frame,
            text="Cancel",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            width=10,
            command=add_window.destroy
        )
        cancel_btn.grid(row=4, column=0, pady=20, sticky="w")
        
    def schedule_appointment(self, user_id, window):
            try:
                # Get selected doctor (extract ID from combobox)
                doctor_str = self.doctor_var.get()
                doctor_id = int(doctor_str.split("(ID: ")[1].replace(")", ""))
                
                date = self.date_var.get()
                time = self.time_var.get()
                reason = self.reason_text.get("1.0", tk.END).strip()

                # Validate inputs
                if not all([doctor_id, date, time]):
                    messagebox.showerror("Error", "Please fill all required fields")
                    return

                # Get patient_id from user_id
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT patient_id FROM patients WHERE user_id = %s", (user_id,))
                patient_id = cursor.fetchone()[0]

                # Check if time slot is available
                cursor.execute("""
                    SELECT appointment_id FROM appointments 
                    WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
                """, (doctor_id, date, time))
                
                if cursor.fetchone():
                    messagebox.showerror("Error", "This time slot is already booked")
                    return

                # Book appointment
                cursor.execute("""
                    INSERT INTO appointments 
                    (patient_id, doctor_id, appointment_date, appointment_time, status, reason)
                    VALUES (%s, %s, %s, %s, 'Scheduled', %s)
                """, (patient_id, doctor_id, date, time, reason))
                
                self.db_connection.commit()
                messagebox.showinfo("Success", "Appointment booked successfully!")
                window.destroy()
                
                # Refresh appointments view if needed
                if hasattr(self, 'show_patient_appointments'):
                    self.show_patient_appointments(user_id)
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
            except Error as e:
                self.db_connection.rollback()
                messagebox.showerror("Database Error", f"Failed to book appointment: {str(e)}")
        

    def cancel_patient_appointment(self, user_id):
        selected_item = self.patient_appointments_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment to cancel")
            return
        appointment_id = self.patient_appointments_tree.item(selected_item)["values"][0]
        status = self.patient_appointments_tree.item(selected_item)["values"][4]

        # Make status check case-insensitive
        if status.lower() != "scheduled":
            messagebox.showerror("Error", "Only scheduled appointments can be cancelled")
            return
        confirm = messagebox.askyesno(
            "Confirm", "Are you sure you want to cancel this appointment?"
        )
        if not confirm:
            return

        try:
            cursor = self.db_connection.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s AND status = 'Scheduled'",
                (appointment_id,)
            )

            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Appointment could not be cancelled. It may have already been processed.")
            else:
                self.db_connection.commit()
                messagebox.showinfo("Success", "Appointment cancelled successfully!")
            
            # Refresh the appointments list
            self.load_patient_appointments(user_id)

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to cancel appointment: {e}")

    def show_patient_medical_records(self, user_id):
        # Clear the frame
        for widget in self.patient_content_frame.winfo_children():
            widget.destroy()

        # Get patient_id
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT patient_id FROM patients WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Patient not found.")
                return
            patient_id = result[0]
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching patient ID: {e}")
            return

        # Title
        tk.Label(
            self.patient_content_frame,
            text="My Medical Records",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff"
        ).pack(pady=10)

        # Table of short summaries
        columns = ("Date", "Doctor", "Diagnosis")
        self.patient_records_tree = ttk.Treeview(
            self.patient_content_frame, columns=columns, show="headings", height=15
        )
        for col in columns:
            self.patient_records_tree.heading(col, text=col)
            self.patient_records_tree.column(col, anchor=tk.CENTER, width=200)

        self.patient_records_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Fetch records
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT mr.record_date, mr.diagnosis, mr.treatment, mr.notes,
                    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
                    d.specialization
                FROM medical_records mr
                JOIN doctors d ON mr.doctor_id = d.doctor_id
                WHERE mr.patient_id = %s
                ORDER BY mr.record_date DESC
            """, (patient_id,))
            records = cursor.fetchall()

            if not records:
                messagebox.showinfo("No Records", "No medical records found.")
                return

            self.medical_record_data = records  # Save for use in detail view

            # Insert short version into tree
            for record in records:
                self.patient_records_tree.insert(
                    "", tk.END,
                    values=(record["record_date"], record["doctor_name"], record["diagnosis"])
                )

            # Bind double-click to view details
            self.patient_records_tree.bind("<Double-1>", lambda e: self.view_medical_record_details())

        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching records: {e}")
        
    def view_medical_record_details(self):
        selected_item = self.patient_records_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record.")
            return

        index = self.patient_records_tree.index(selected_item)
        record = self.medical_record_data[index]

        # Create a details popup
        details_window = tk.Toplevel(self.root)
        details_window.title("Medical Record Details")
        details_window.geometry("600x500")

        tk.Label(
            details_window,
            text="Medical Record Details",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        frame = tk.Frame(details_window)
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Basic info
        info_text = (
            f"Date: {record['record_date']}\n"
            f"Doctor: {record['doctor_name']} ({record['specialization']})\n"
            f"Diagnosis: {record['diagnosis']}\n"
        )
        tk.Label(frame, text=info_text, font=("Arial", 12), justify="left").pack(anchor="w", pady=5)

        # Treatment
        if record["treatment"]:
            tk.Label(frame, text="Treatment:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
            treatment_box = tk.Text(frame, font=("Arial", 12), height=4, wrap=tk.WORD)
            treatment_box.insert("1.0", record["treatment"])
            treatment_box.config(state=tk.DISABLED)
            treatment_box.pack(fill=tk.X)

        # Notes
        if record["notes"]:
            tk.Label(frame, text="Notes:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
            notes_box = tk.Text(frame, font=("Arial", 12), height=5, wrap=tk.WORD)
            notes_box.insert("1.0", record["notes"])
            notes_box.config(state=tk.DISABLED)
            notes_box.pack(fill=tk.BOTH, expand=True)


    def show_patient_billing(self, user_id):
        # Clear content frame
        for widget in self.patient_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.patient_content_frame,
            text="My Billing Information",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Billing table
        columns = ("Bill ID", "Date", "Amount", "Status", "Description")
        self.patient_bills_tree = ttk.Treeview(
            self.patient_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.patient_bills_tree.heading(col, text=col)
            self.patient_bills_tree.column(col, width=120, anchor=tk.CENTER)

        self.patient_bills_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load billing data
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT bill_id, bill_date, amount, payment_status, description
                FROM billing
                WHERE patient_id = (SELECT patient_id FROM patients WHERE user_id = %s)
                ORDER BY bill_date DESC""",
                (user_id,)
            )
            bills = cursor.fetchall()

            # Insert bills
            for bill in bills:
                self.patient_bills_tree.insert("", tk.END, values=bill)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load billing information: {e}")

        # Action buttons frame
        action_frame = tk.Frame(self.patient_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        pay_btn = tk.Button(
            action_frame,
            text="Pay Bill",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.pay_bill,
        )
        pay_btn.grid(row=0, column=0, padx=10)

    def pay_bill(self):
        selected_item = self.patient_bills_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a bill to pay")
            return

        bill_id = self.patient_bills_tree.item(selected_item)["values"][0]
        status = self.patient_bills_tree.item(selected_item)["values"][3]
        amount = self.patient_bills_tree.item(selected_item)["values"][2]

        if status == "Paid":
            messagebox.showerror("Error", "This bill has already been paid")
            return

        confirm = messagebox.askyesno(
            "Confirm", f"Are you sure you want to pay this bill of ${amount:.2f}?"
        )
        if not confirm:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE billing SET payment_status = 'Paid' WHERE bill_id = %s",
                (bill_id,)
            )

            self.db_connection.commit()

            messagebox.showinfo("Success", "Bill paid successfully!")
            
            # Reload billing data
            self.show_patient_billing(self.current_user_id)

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to pay bill: {e}")


    def show_staff_dashboard(self, user_id):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Staff dashboard frame
        dashboard_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(dashboard_frame, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)

        # Get staff member's name
        staff_name = ""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT first_name, last_name FROM staff WHERE user_id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                staff_name = f"{result[0]} {result[1]}"
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch staff data: {e}")

        tk.Label(
            header_frame,
            text=f"Staff Dashboard - {staff_name}",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=20)

        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.show_login_screen,
        )
        logout_btn.pack(side=tk.RIGHT, padx=20)

        # Navigation
        nav_frame = tk.Frame(dashboard_frame, bg="#333", width=200)
        nav_frame.pack(fill=tk.Y, side=tk.LEFT)

        buttons = [
            ("Dashboard", lambda: self.show_staff_welcome(user_id)),
            ("Manage Appointments", lambda: self.show_staff_appointments(user_id)),
            ("Manage Billing", lambda: self.show_staff_billing(user_id)),
            ("Patient Registration", lambda: self.show_patient_registration()),
        ]

        for text, command in buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 12),
                bg="#333",
                fg="white",
                relief=tk.FLAT,
                command=command,
            ).pack(fill=tk.X, pady=2)

        # Main content area
        self.staff_content_frame = tk.Frame(dashboard_frame, bg="#f0f8ff")
        self.staff_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show default view
        self.show_staff_welcome(user_id)

    def show_staff_welcome(self, user_id):
        # Clear content frame
        for widget in self.staff_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.staff_content_frame,
            text="Welcome, Staff Member",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=50)

        # Display today's appointments count
        try:
            cursor = self.db_connection.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get total appointments
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s",
                (today,)
            )
            today_appointments = cursor.fetchone()[0]
            
            # Get completed appointments
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s AND status = 'Completed'",
                (today,)
            )
            completed_appointments = cursor.fetchone()[0]
            
            # Display stats
            stats_frame = tk.Frame(self.staff_content_frame, bg="#f0f8ff")
            stats_frame.pack()
            
            tk.Label(
                stats_frame,
                text="Today's Appointments:",
                font=("Arial", 14),
                bg="#f0f8ff"
            ).grid(row=0, column=0, padx=10, pady=5, sticky="e")
            
            tk.Label(
                stats_frame,
                text=str(today_appointments),
                font=("Arial", 14, "bold"),
                bg="#f0f8ff"
            ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            tk.Label(
                stats_frame,
                text="Completed:",
                font=("Arial", 14),
                bg="#f0f8ff"
            ).grid(row=1, column=0, padx=10, pady=5, sticky="e")
            
            tk.Label(
                stats_frame,
                text=str(completed_appointments),
                font=("Arial", 14, "bold"),
                bg="#f0f8ff"
            ).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch appointment data: {e}")

    def show_staff_appointments(self, user_id):
        # Clear content frame
        for widget in self.staff_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.staff_content_frame,
            text="Manage Appointments",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Filter frame
        filter_frame = tk.Frame(self.staff_content_frame, bg="#f0f8ff")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Date:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.staff_appointment_date = tk.Entry(filter_frame, font=("Arial", 12))
        self.staff_appointment_date.grid(row=0, column=1, padx=5)
        self.staff_appointment_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        filter_btn = tk.Button(
            filter_frame,
            text="Filter",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=lambda: self.load_staff_appointments(),
        )
        filter_btn.grid(row=0, column=2, padx=10)

        # Appointments table
        columns = ("ID", "Patient", "Doctor", "Time", "Status", "Reason")
        self.staff_appointments_tree = ttk.Treeview(
            self.staff_content_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.staff_appointments_tree.heading(col, text=col)
            self.staff_appointments_tree.column(col, width=120, anchor=tk.CENTER)

        self.staff_appointments_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Action buttons frame
        action_frame = tk.Frame(self.staff_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        complete_btn = tk.Button(
            action_frame,
            text="Mark as Completed",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.update_staff_appointment_status("Completed"),
        )
        complete_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(
            action_frame,
            text="Cancel Appointment",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=lambda: self.update_staff_appointment_status("Cancelled"),
        )
        cancel_btn.grid(row=0, column=1, padx=10)

        # Load initial appointments
        self.load_staff_appointments()

    def load_staff_appointments(self):
        date = self.staff_appointment_date.get()

        # Validate date
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """SELECT a.appointment_id, 
                          CONCAT(p.first_name, ' ', p.last_name),
                          CONCAT(d.first_name, ' ', d.last_name),
                          a.appointment_time,
                          a.status,
                          a.reason
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_date = %s
                ORDER BY a.appointment_time""",
                (date,)
            )
            appointments = cursor.fetchall()

            # Clear existing data
            for item in self.staff_appointments_tree.get_children():
                self.staff_appointments_tree.delete(item)

            # Insert new data
            for appointment in appointments:
                self.staff_appointments_tree.insert("", tk.END, values=appointment)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load appointments: {e}")

    def update_staff_appointment_status(self, status):
        selected_item = self.staff_appointments_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment")
            return

        appointment_id = self.staff_appointments_tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno(
            "Confirm", f"Are you sure you want to mark this appointment as {status}?"
        )
        if not confirm:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE appointments SET status = %s WHERE appointment_id = %s",
                (status, appointment_id)
            )

            self.db_connection.commit()

            messagebox.showinfo("Success", f"Appointment marked as {status}")
            self.load_staff_appointments()

        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update appointment: {e}")

    def show_staff_billing(self, user_id):
        # Clear content frame
        for widget in self.staff_content_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.staff_content_frame,
            text="Manage Billing",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
        ).pack(pady=10)

        # Filter frame
        filter_frame = tk.Frame(self.staff_content_frame, bg="#f0f8ff")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Patient:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.billing_patient_var = tk.StringVar()
        patient_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.billing_patient_var,
            font=("Arial", 12),
            state="readonly",
            width=30
        )
        patient_cb.grid(row=0, column=1, padx=5)

        # Load patients
        try:
            # Ensure no transaction is active before starting
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
                
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT patient_id, CONCAT(first_name, ' ', last_name) FROM patients ORDER BY last_name, first_name")
            patients = [f"{name} (ID: {pid})" for pid, name in cursor.fetchall()]
            patient_cb['values'] = patients
            if patients:
                patient_cb.current(0)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load patients: {e}")

        # Add bill button
        tk.Button(
            filter_frame,
            text="Add New Bill",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.show_add_bill_form,
        ).grid(row=0, column=2, padx=10)

        # Billing table
        columns = ("Bill ID", "Patient", "Date", "Amount", "Status", "Description")
        self.staff_bills_tree = ttk.Treeview(
            self.staff_content_frame, 
            columns=columns, 
            show="headings", 
            height=15
        )

        for col in columns:
            self.staff_bills_tree.heading(col, text=col)
            self.staff_bills_tree.column(col, width=120, anchor=tk.CENTER)

        self.staff_bills_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.load_staff_bills()

        # Action buttons
        action_frame = tk.Frame(self.staff_content_frame, bg="#f0f8ff")
        action_frame.pack(pady=10)

        tk.Button(
            action_frame,
            text="Mark as Paid",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=lambda: self.update_bill_status("Paid"),
        ).grid(row=0, column=0, padx=10)

    def show_add_bill_form(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Bill")
        add_window.geometry("500x500")

        tk.Label(add_window, text="Add New Bill", font=("Arial", 18, "bold")).pack(pady=10)

        # Form fields
        fields = [
            ("Patient:", "combobox"),
            ("Amount:", "entry"),
            ("Description:", "text"),
            ("Payment Status:", "combobox", "Pending", ["Pending", "Paid"]),
        ]

        self.bill_form_entries = {}

        try:
            # Ensure clean transaction state
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
                
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT patient_id, CONCAT(first_name, ' ', last_name) FROM patients ORDER BY last_name, first_name")
            patients = [f"{name} (ID: {pid})" for pid, name in cursor.fetchall()]
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load patients: {e}")
            add_window.destroy()
            return

        for label, field_type, *opts in fields:
            tk.Label(add_window, text=label, font=("Arial", 12)).pack(pady=5)
            entry = None

            if field_type == "entry":
                entry = tk.Entry(add_window, font=("Arial", 12))
            elif field_type == "combobox":
                entry = ttk.Combobox(add_window, font=("Arial", 12), state="readonly")
                entry['values'] = patients if label == "Patient:" else opts[1]
                entry.set(opts[0] if opts else "")
            elif field_type == "text":
                entry = tk.Text(add_window, font=("Arial", 12), height=4, width=40)

            if entry:
                entry.pack(pady=5, ipadx=20)
                self.bill_form_entries[label.split(":")[0].lower().replace(" ", "_")] = entry

        tk.Button(
            add_window,
            text="Add Bill",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.add_bill(add_window),
        ).pack(pady=20)

    def add_bill(self, window):
        try:
            # Get form data
            patient_str = self.bill_form_entries["patient"].get()
            patient_id = int(patient_str.split("(ID: ")[1].replace(")", ""))
            amount = float(self.bill_form_entries["amount"].get())
            description = self.bill_form_entries["description"].get("1.0", tk.END).strip()
            status = self.bill_form_entries["payment_status"].get()

            # Validation
            if not all([patient_id, amount, description, status]):
                raise ValueError("All fields are required")
            if amount <= 0:
                raise ValueError("Amount must be positive")

            # Ensure clean transaction state
            if self.db_connection.in_transaction:
                self.db_connection.rollback()

            cursor = self.db_connection.cursor()
            self.db_connection.start_transaction()
            
            cursor.execute(
                """
                INSERT INTO billing (patient_id, bill_date, amount, description, payment_status)
                VALUES (%s, CURDATE(), %s, %s, %s)
                """,
                (patient_id, amount, description, status)
            )
            
            self.db_connection.commit()
            messagebox.showinfo("Success", "Bill added successfully!")
            window.destroy()
            self.load_staff_bills()  # Refresh the bills list
            
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to add bill: {e}")

    def load_staff_bills(self):
        try:
            # Ensure clean transaction state
            if self.db_connection.in_transaction:
                self.db_connection.rollback()
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT b.bill_id, 
                    CONCAT(p.first_name, ' ', p.last_name),
                    b.bill_date,
                    b.amount,
                    b.payment_status,
                    b.description
                FROM billing b
                JOIN patients p ON b.patient_id = p.patient_id
                ORDER BY b.bill_date DESC
            """)
            bills = cursor.fetchall()

            # Clear existing data
            for item in self.staff_bills_tree.get_children():
                self.staff_bills_tree.delete(item)

            # Insert new data
            for bill in bills:
                self.staff_bills_tree.insert("", tk.END, values=bill)

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load bills: {e}")

    def update_bill_status(self, status):
        selected_item = self.staff_bills_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a bill")
            return

        bill_id = self.staff_bills_tree.item(selected_item)["values"][0]
        current_status = self.staff_bills_tree.item(selected_item)["values"][4]

        if current_status == "Paid":
            messagebox.showinfo("Info", "This bill is already paid")
            return

        confirm = messagebox.askyesno("Confirm", f"Mark this bill as {status}?")
        if not confirm:
            return

        try:
            # Ensure clean transaction state
            if self.db_connection.in_transaction:
                self.db_connection.rollback()

            cursor = self.db_connection.cursor()
            self.db_connection.start_transaction()
            
            cursor.execute(
                "UPDATE billing SET payment_status = %s WHERE bill_id = %s", 
                (status, bill_id)
            )
            
            self.db_connection.commit()
            messagebox.showinfo("Success", f"Bill marked as {status}")
            self.load_staff_bills()  # Refresh the bills list
            
        except Error as e:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update bill: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalManagementSystem(root)
    root.mainloop()