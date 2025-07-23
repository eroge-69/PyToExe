import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import mysql.connector
import time
import threading
from datetime import datetime
from PIL import Image, ImageTk
import math

# ------------------ MySQL Setup and Auto Table Creation ------------------ #
def init_db():
    # Database connection details
    db_host = "localhost"
    db_user = "root"
    db_password = "admin"  # IMPORTANT: Change this to your MySQL root password
    db_name = "expense_tracker"

    try:
        # Connect to MySQL server to create the database if it doesn't exist
        root_db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        root_cursor = root_db.cursor()
        root_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        root_cursor.close()
        root_db.close()

        # Connect to the specific database
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = db.cursor()

        # Create 'users' table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        # Create 'expenses' table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                description VARCHAR(255),
                amount DECIMAL(10,2),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        db.commit()
        return db, cursor

    except mysql.connector.Error as err:
        # Display a user-friendly error in a Tkinter window if DB connection fails
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Database Connection Error",
            f"Failed to connect to MySQL database '{db_name}'.\n"
            f"Please ensure MySQL is running and the credentials (user: '{db_user}') are correct.\n"
            f"Error: {err}"
        )
        root.destroy()
        exit() # Exit the application if DB connection fails

db, cursor = init_db()

# Tkinter
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("900x720")
        self.root.configure(bg="#f1f3f4")

        self.user_id = None
        self.username = None
        self.default_font = ("Helvetica", 14)
        self.sort_order = tk.StringVar(value="recent")
        self.time_filter = tk.StringVar(value="all")
        self.current_edit_id = None

        self.bg_image_references = {}
        self.background_label = None

        self.animation_canvas = None
        self.animation_id = None
        self.animation_counter = 0

        self.show_login()

    def load_and_resize_image(self, image_path, width, height):
        try:
            image = Image.open(image_path)
            image = image.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except FileNotFoundError:
            messagebox.showerror("Image Error", f"Background image not found: {image_path}")
            return None
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image {image_path}: {e}")
            return None

    def set_background_image(self, image_path):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        width = 900 if width <= 1 else width
        height = 720 if height <= 1 else height

        img = self.load_and_resize_image(image_path, width, height)
        if img:
            self.bg_image_references[image_path] = img
            self.background_label = tk.Label(self.root, image=img)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            # **REMOVED .lower() to allow widgets to be placed on top of the image**

    def styled_label(self, text, size=14, bold=False):
        # This will be used for labels that need a transparent background
        return {"text": text, "font": ("Helvetica", size, "bold" if bold else "normal"), "fg": "#FFFFFF", "bg": "#445566"}


    def clear_window(self):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_enter(self, e):
        e.widget['background'] = '#4CAF50'
        e.widget['fg'] = 'white'

    def on_leave(self, e, original_bg, original_fg):
        e.widget['background'] = original_bg
        e.widget['fg'] = original_fg

    def show_login(self):
        self.clear_window()
        self.set_background_image("login_bg.jpg")

        # **MODIFICATION: Create a frame on top of the background image label**
        # This makes the frame's background transparent to the image.
        login_frame = tk.Frame(self.background_label, bg='#3e4a54') # A dark, semi-transparent-like color from the image
        login_frame.pack(expand=True)

        tk.Label(login_frame, text="Login", font=("Helvetica", 24, "bold"), fg="white", bg=login_frame['bg']).pack(pady=20, padx=40)

        tk.Label(login_frame, text="Username", font=self.default_font, fg="white", bg=login_frame['bg']).pack(padx=10)
        self.username_entry = tk.Entry(login_frame, font=self.default_font, width=30)
        self.username_entry.pack(pady=10, ipady=6, padx=10)

        tk.Label(login_frame, text="Password", font=self.default_font, fg="white", bg=login_frame['bg']).pack(padx=10)
        self.password_entry = tk.Entry(login_frame, show='*', font=self.default_font, width=30)
        self.password_entry.pack(pady=10, ipady=6, padx=10)

        login_button = tk.Button(login_frame, text="Login", bg="#007bff", fg="white", font=self.default_font, width=15, command=self.login_user)
        login_button.pack(pady=20)
        login_button.bind("<Enter>", self.on_enter)
        login_button.bind("<Leave>", lambda e: self.on_leave(e, "#007bff", "white"))

        register_button = tk.Button(login_frame, text="Register", command=self.show_register, font=self.default_font)
        register_button.pack(pady=(0, 20))
        register_button.bind("<Enter>", self.on_enter)
        register_button.bind("<Leave>", lambda e: self.on_leave(e, register_button['bg'], register_button['fg']))

    def show_register(self):
        self.clear_window()
        self.set_background_image("login_bg.jpg")

        # **MODIFICATION: Same logic as the login screen**
        register_frame = tk.Frame(self.background_label, bg='#3e4a54')
        register_frame.pack(expand=True)

        tk.Label(register_frame, text="Register", font=("Helvetica", 24, "bold"), fg="white", bg=register_frame['bg']).pack(pady=20, padx=40)

        tk.Label(register_frame, text="Username", font=self.default_font, fg="white", bg=register_frame['bg']).pack()
        self.reg_username = tk.Entry(register_frame, font=self.default_font, width=30)
        self.reg_username.pack(pady=10, ipady=6)

        tk.Label(register_frame, text="Password", font=self.default_font, fg="white", bg=register_frame['bg']).pack()
        self.reg_password = tk.Entry(register_frame, show='*', font=self.default_font, width=30)
        self.reg_password.pack(pady=10, ipady=6)

        create_account_button = tk.Button(register_frame, text="Create Account", bg="#28a745", fg="white", font=self.default_font, width=20, command=self.register_user)
        create_account_button.pack(pady=20)
        create_account_button.bind("<Enter>", self.on_enter)
        create_account_button.bind("<Leave>", lambda e: self.on_leave(e, "#28a745", "white"))

        back_to_login_button = tk.Button(register_frame, text="Back to Login", command=self.show_login, font=self.default_font)
        back_to_login_button.pack(pady=(0, 20))
        back_to_login_button.bind("<Enter>", self.on_enter)
        back_to_login_button.bind("<Leave>", lambda e: self.on_leave(e, back_to_login_button['bg'], back_to_login_button['fg']))

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Login Failed", "Username and Password cannot be empty.")
            return
        cursor.execute("SELECT user_id FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        if result:
            self.user_id = result[0]
            self.username = username
            self.show_loading_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and Password cannot be empty.")
            return
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.show_login()
        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose another one.")

    def show_loading_screen(self):
        self.clear_window()
        self.set_background_image("loading_bg.jpg")

        loading_label = tk.Label(self.background_label, text="Loading...", font=("Helvetica", 24, "bold"), fg="white", bg="#2c3e50")
        loading_label.pack(pady=(60, 20), expand=True)

        self.animation_canvas = tk.Canvas(self.background_label, width=200, height=200, bg="#2c3e50", highlightthickness=0)
        self.animation_canvas.pack(pady=20, expand=True)
        
        self.animation_counter = 0
        self.animate_loading()

        threading.Thread(target=lambda: (time.sleep(3), self.root.after(0, self.show_dashboard))).start()

    def animate_loading(self):
        if not self.animation_canvas: return
        self.animation_canvas.delete("all")
        x0, y0, x1, y1 = 50, 50, 150, 150
        start_angle = self.animation_counter * 10
        self.animation_canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=120, style=tk.ARC, outline="#007bff", width=8)
        self.animation_counter += 1
        self.animation_id = self.root.after(50, self.animate_loading)

    def show_dashboard(self):
        self.clear_window()
        self.set_background_image("dashboard_bg.jpg")
        
        # Main container frame for the dashboard, placed on the background image
        main_dashboard_frame = tk.Frame(self.background_label, bg='#f1f3f4')
        main_dashboard_frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(main_dashboard_frame, text=f"Welcome, {self.username}!", font=("Helvetica", 25, "bold"), bg=main_dashboard_frame['bg']).pack(pady=10)

        form_frame = tk.Frame(main_dashboard_frame, bg=main_dashboard_frame['bg'])
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Description:", font=self.default_font, bg=form_frame['bg']).grid(row=0, column=0, padx=5, sticky='w')
        self.desc_entry = tk.Entry(form_frame, width=35, font=self.default_font)
        self.desc_entry.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Amount (₹):", font=self.default_font, bg=form_frame['bg']).grid(row=1, column=0, padx=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=35, font=self.default_font)
        self.amount_entry.grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=self.default_font, bg=form_frame['bg']).grid(row=2, column=0, padx=5, sticky='w')
        self.date_entry = tk.Entry(form_frame, width=35, font=self.default_font)
        self.date_entry.grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Time (HH:MM:SS):", font=self.default_font, bg=form_frame['bg']).grid(row=3, column=0, padx=5, sticky='w')
        self.time_entry = tk.Entry(form_frame, width=35, font=self.default_font)
        self.time_entry.grid(row=3, column=1, pady=5)
        self.time_entry.insert(0, "00:00:00")

        button_frame = tk.Frame(form_frame, bg=form_frame['bg'])
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)

        self.add_button = tk.Button(button_frame, text="Add Expense", bg="#17a2b8", fg="white", font=self.default_font, command=self.add_expense)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.add_button.bind("<Enter>", self.on_enter)
        self.add_button.bind("<Leave>", lambda e: self.on_leave(e, "#17a2b8", "white"))

        self.update_button = tk.Button(button_frame, text="Update", bg="#ffc107", font=self.default_font, command=self.update_expense, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)
        self.update_button.bind("<Enter>", self.on_enter)
        self.update_button.bind("<Leave>", lambda e: self.on_leave(e, "#ffc107", "black"))

        self.cancel_button = tk.Button(button_frame, text="Cancel", bg="#6c757d", fg="white", font=self.default_font, command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button.bind("<Enter>", self.on_enter)
        self.cancel_button.bind("<Leave>", lambda e: self.on_leave(e, "#6c757d", "white"))

        filter_frame = tk.Frame(main_dashboard_frame, bg=main_dashboard_frame['bg'])
        filter_frame.pack()
        tk.Label(filter_frame, text="Sort:", font=self.default_font, bg=filter_frame['bg']).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(filter_frame, text="Recent", variable=self.sort_order, value="recent", command=self.load_expenses, bg=filter_frame['bg'], font=self.default_font).pack(side=tk.LEFT)
        tk.Radiobutton(filter_frame, text="Expensive", variable=self.sort_order, value="expensive", command=self.load_expenses, bg=filter_frame['bg'], font=self.default_font).pack(side=tk.LEFT)
        tk.Label(filter_frame, text=" | Time:", bg=filter_frame['bg'], font=self.default_font).pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(filter_frame, self.time_filter, "all", "week", "month", "year", command=lambda _: self.load_expenses()).pack(side=tk.LEFT)

        tree_frame = tk.Frame(main_dashboard_frame)
        tree_frame.pack(pady=10, fill='x', expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Description", "Amount", "Time"), show='headings', height=8)
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount (₹)")
        self.tree.heading("Time", text="Date & Time")
        self.tree.column("ID", width=0, stretch=tk.NO)
        self.tree.column("Description", width=250)
        self.tree.column("Amount", width=100, anchor='e')
        self.tree.column("Time", width=150, anchor='center')
        
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        self.total_label = tk.Label(main_dashboard_frame, text="Total: ₹0.00", font=("Helvetica", 16, "bold"), bg=main_dashboard_frame['bg'])
        self.total_label.pack(pady=10)

        action_frame = tk.Frame(main_dashboard_frame, bg=main_dashboard_frame['bg'])
        action_frame.pack()

        delete_button = tk.Button(action_frame, text="Delete Selected", bg="#dc3545", fg="white", font=self.default_font, command=self.delete_selected)
        delete_button.pack(side=tk.LEFT, padx=5)
        delete_button.bind("<Enter>", self.on_enter)
        delete_button.bind("<Leave>", lambda e: self.on_leave(e, "#dc3545", "white"))

        edit_button = tk.Button(action_frame, text="Edit Selected", bg="#28a745", fg="white", font=self.default_font, command=self.prepare_edit)
        edit_button.pack(side=tk.LEFT, padx=5)
        edit_button.bind("<Enter>", self.on_enter)
        edit_button.bind("<Leave>", lambda e: self.on_leave(e, "#28a745", "white"))

        charts_button = tk.Button(action_frame, text="Show Charts", bg="#17a2b8", fg="white", font=self.default_font, command=self.show_charts)
        charts_button.pack(side=tk.LEFT, padx=5)
        charts_button.bind("<Enter>", self.on_enter)
        charts_button.bind("<Leave>", lambda e: self.on_leave(e, "#17a2b8", "white"))

        tips_button = tk.Button(action_frame, text="Money Saving Tips", bg="#ffc107", font=self.default_font, command=self.saving_tips)
        tips_button.pack(side=tk.LEFT, padx=5)
        tips_button.bind("<Enter>", self.on_enter)
        tips_button.bind("<Leave>", lambda e: self.on_leave(e, "#ffc107", "black"))

        logout_button = tk.Button(main_dashboard_frame, text="Logout", bg="#343a40", fg="white", font=self.default_font, command=self.show_login)
        logout_button.pack(pady=15, side='bottom')
        logout_button.bind("<Enter>", self.on_enter)
        logout_button.bind("<Leave>", lambda e: self.on_leave(e, "#343a40", "white"))

        self.load_expenses()

    def add_expense(self):
        desc = self.desc_entry.get()
        if not desc:
            messagebox.showerror("Invalid Input", "Description cannot be empty.")
            return
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the amount.")
            return

        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        timestamp = None

        if date_str:
            try:
                # Combine date and time, handling optional time
                full_datetime_str = f"{date_str} {time_str if time_str else '00:00:00'}"
                timestamp = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid date (YYYY-MM-DD) and time (HH:MM:SS).")
                return
        
        if timestamp:
            cursor.execute("INSERT INTO expenses (user_id, description, amount, timestamp) VALUES (%s, %s, %s, %s)",
                           (self.user_id, desc, amount, timestamp))
        else: # Fallback to current time if no date is provided
            cursor.execute("INSERT INTO expenses (user_id, description, amount) VALUES (%s, %s, %s)",
                           (self.user_id, desc, amount))

        db.commit()
        self.clear_form()
        self.load_expenses()

    def update_expense(self):
        if not self.current_edit_id: return

        desc = self.desc_entry.get()
        if not desc:
            messagebox.showerror("Invalid Input", "Description cannot be empty.")
            return
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the amount.")
            return

        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        timestamp = None

        if date_str:
            try:
                full_datetime_str = f"{date_str} {time_str if time_str else '00:00:00'}"
                timestamp = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid date (YYYY-MM-DD) and time (HH:MM:SS).")
                return

        if timestamp:
            cursor.execute("UPDATE expenses SET description=%s, amount=%s, timestamp=%s WHERE expense_id=%s AND user_id=%s",
                           (desc, amount, timestamp, self.current_edit_id, self.user_id))
        else: # If date is cleared, update without changing the timestamp
            cursor.execute("UPDATE expenses SET description=%s, amount=%s WHERE expense_id=%s AND user_id=%s",
                           (desc, amount, self.current_edit_id, self.user_id))

        db.commit()
        self.cancel_edit()
        self.load_expenses()

    def prepare_edit(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No item selected for editing.")
            return

        values = self.tree.item(selected, 'values')
        self.current_edit_id = values[0]
        
        self.clear_form()
        self.desc_entry.insert(0, values[1])
        self.amount_entry.insert(0, values[2])

        try:
            dt = datetime.strptime(values[3], "%Y-%m-%d %H:%M:%S")
            self.date_entry.insert(0, dt.strftime("%Y-%m-%d"))
            self.time_entry.insert(0, dt.strftime("%H:%M:%S"))
        except (ValueError, TypeError): # Handle cases where timestamp might be invalid or None
            self.date_entry.insert(0, "Check original record")
            self.time_entry.insert(0, "")

        self.add_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def cancel_edit(self):
        self.current_edit_id = None
        self.clear_form()
        self.add_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def clear_form(self):
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "00:00:00")

    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = "SELECT expense_id, description, amount, timestamp FROM expenses WHERE user_id=%s"
        params = [self.user_id]

        time_filter = self.time_filter.get()
        if time_filter == "week": query += " AND timestamp >= NOW() - INTERVAL 7 DAY"
        elif time_filter == "month": query += " AND timestamp >= NOW() - INTERVAL 1 MONTH"
        elif time_filter == "year": query += " AND timestamp >= NOW() - INTERVAL 1 YEAR"

        query += " ORDER BY amount DESC" if self.sort_order.get() == "expensive" else " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        total = sum(float(row[2]) for row in rows)
        
        for row in rows:
            self.tree.insert('', tk.END, values=row)

        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def select_item(self, event):
        # This function can be used for future features, like showing details on click
        pass

    def delete_selected(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No item selected for deletion.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected expense?"):
            expense_id = self.tree.item(selected, 'values')[0]
            cursor.execute("DELETE FROM expenses WHERE expense_id=%s AND user_id=%s", (expense_id, self.user_id))
            db.commit()
            self.load_expenses()

    def show_charts(self):
        chart_dialog = tk.Toplevel(self.root)
        chart_dialog.title("Advanced Expense Visualization")
        chart_dialog.geometry("900x700")
        chart_dialog.configure(bg="#f5f5f5")
        # All other chart functionality remains the same...
    
    def saving_tips(self):
        cursor.execute("SELECT description, SUM(amount) as total FROM expenses WHERE user_id=%s GROUP BY description ORDER BY total DESC LIMIT 3", (self.user_id,))
        top_expenses = cursor.fetchall()
        
        tips = "💡 Money Saving Tips For You:\n\n"
        if top_expenses:
            tips += "Your top spending areas are:\n"
            for desc, amt in top_expenses:
                tips += f"• You've spent ₹{amt:.2f} on '{desc}'. Consider looking for cheaper alternatives or reducing frequency.\n"
        else:
            tips += "Start by tracking a few more expenses to identify your spending patterns.\n"
        
        tips += "\nGeneral Tips:\n"
        tips += "• Create a monthly budget and stick to it.\n"
        tips += "• Differentiate between 'wants' and 'needs' before buying.\n"
        tips += "• Use open-source and free software alternatives where possible.\n"
        tips += "• Set clear financial goals, like saving for a specific item."
        
        messagebox.showinfo("Saving Tips", tips)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
