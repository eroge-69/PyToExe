import mysql.connector
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox
import sys
import io
import logging
import os
from dotenv import load_dotenv
from akharajat import main as akharajat_main
from report import main as report_main
import time
import uuid
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='sales_system.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Database connection with improved error handling and pooling
def connect_db(max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "mandi_sales"),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                connection_timeout=10,
                autocommit=False
            )
            logging.info("Database connection established")
            return conn
        except mysql.connector.Error as e:
            error_code = e.errno if hasattr(e, 'errno') else None
            error_msg = {
                1045: "غلط صارف نام یا پاس ورڈ",
                1049: "ڈیٹابیس نہیں ملا",
                None: f"ڈیٹابیس خطا: {str(e)}"
            }.get(error_code, f"ڈیٹابیس خطا: {str(e)}")
            logging.error(f"Database connection attempt {attempt + 1} failed: {error_msg}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                messagebox.showerror("خطا", error_msg)
                return None

# Create database and tables with schema version check
def setup_database():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS mandi_sales CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logging.info("Database 'mandi_sales' created or already exists")
        conn.commit()
    except mysql.connector.Error as e:
        logging.error(f"Initial database setup failed: {str(e)}")
        messagebox.showerror("خطا", f"ڈیٹابیس سیٹ اپ ناکام: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    conn = connect_db()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            # Create schema_version table to track database version
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INT PRIMARY KEY,
                    applied_at DATETIME
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Check current schema version
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            current_version = cursor.fetchone()
            current_version = current_version[0] if current_version else 0

            if current_version < 1:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        INDEX idx_name (name)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_id INT,
                        quantity FLOAT NOT NULL,
                        unit_price FLOAT NOT NULL,
                        total_amount FLOAT NOT NULL,
                        paid_amount FLOAT DEFAULT 0,
                        due_amount FLOAT DEFAULT 0,
                        sale_date DATETIME,
                        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                        INDEX idx_customer_id (customer_id)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS payments (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_id INT,
                        paid_amount FLOAT NOT NULL,
                        remaining_due FLOAT NOT NULL,
                        payment_date DATETIME,
                        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                        INDEX idx_customer_id (customer_id)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                cursor.execute("INSERT INTO schema_version (version, applied_at) VALUES (1, %s)", (datetime.now(),))
                conn.commit()
                logging.info("Database tables created or already exist")
    except mysql.connector.Error as e:
        logging.error(f"Table creation failed: {str(e)}")
        messagebox.showerror("خطا", f"ڈیٹابیس سیٹ اپ ناکام: {str(e)}")
        conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()

# Autocomplete Entry Widget with debouncing
class AutocompleteEntry(ctk.CTkEntry):
    def __init__(self, master, suggestions_callback, allow_new=True, **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions_callback = suggestions_callback
        self.allow_new = allow_new
        self.suggestions = []
        self.suggestion_menu = None
        self.selected_index = -1
        self.last_search = ""
        self.debounce_timer = None
        self.bind("<KeyRelease>", self.check_input)
        self.bind("<FocusOut>", self.hide_suggestions)
        self.bind("<Return>", self.select_suggestion)
        self.bind("<Down>", self.move_down)
        self.bind("<Up>", self.move_up)

    def check_input(self, event=None):
        if self.debounce_timer:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(300, self._process_input)

    def _process_input(self):
        value = self.get().strip()
        if value != self.last_search:
            self.last_search = value
            if value:
                self.suggestions = self.suggestions_callback(value.lower())
                self.selected_index = -1
                self.show_suggestions()
            else:
                self.hide_suggestions()

    def show_suggestions(self):
        if self.suggestions:
            if self.suggestion_menu:
                self.suggestion_menu.destroy()
            self.suggestion_menu = ctk.CTkFrame(self.master, corner_radius=5, fg_color="#F0F0F0")
            self.suggestion_menu.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height(), width=self.winfo_width())
            for i, suggestion in enumerate(self.suggestions):
                btn = ctk.CTkButton(
                    self.suggestion_menu,
                    text=suggestion,
                    font=("Nafees", 14),
                    anchor="e",
                    command=lambda s=suggestion: self.set_suggestion(s),
                    fg_color="#F0F0F0",
                    hover_color="#D0D0D0",
                    text_color="#1A2526"
                )
                btn.pack(fill="x", pady=2)
                btn.bind("<Enter>", lambda e, idx=i: self.highlight_suggestion(idx))
            if self.suggestions:
                self.suggestion_menu.winfo_children()[0].focus_set()

    def hide_suggestions(self, event=None):
        if self.suggestion_menu:
            self.suggestion_menu.destroy()
            self.suggestion_menu = None
            self.selected_index = -1

    def set_suggestion(self, suggestion):
        self.delete(0, ctk.END)
        self.insert(0, suggestion)
        self.hide_suggestions()
        self.focus_set()

    def select_suggestion(self, event):
        if self.suggestion_menu and self.selected_index >= 0:
            suggestion = self.suggestions[self.selected_index]
            self.set_suggestion(suggestion)
            if self.master.focus_get() == self:
                self.master.focus_next().focus_set()
        elif self.allow_new and self.get().strip():
            self.hide_suggestions()
            self.master.focus_next().focus_set()

    def highlight_suggestion(self, index):
        self.selected_index = index
        if self.suggestion_menu:
            for i, child in enumerate(self.suggestion_menu.winfo_children()):
                child.configure(fg_color="#D0D0D0" if i == index else "#F0F0F0")

    def move_down(self, event):
        if self.suggestion_menu and self.suggestions:
            self.selected_index = min(self.selected_index + 1, len(self.suggestions) - 1)
            self.highlight_suggestion(self.selected_index)

    def move_up(self, event):
        if self.suggestion_menu and self.suggestions:
            self.selected_index = max(self.selected_index - 1, -1)
            if self.selected_index == -1:
                self.focus_set()
            else:
                self.highlight_suggestion(self.selected_index)

# Custom Grid Display
class CustomGrid:
    def __init__(self, master, columns, font, on_click=None, on_double_click=None):
        self.master = master
        self.columns = columns
        self.font = font
        self.on_click = on_click
        self.on_double_click = on_double_click
        self.rows = []
        self.header_frame = None
        self.data_frame = None
        self.canvas = None
        self.v_scrollbar = None
        self.h_scrollbar = None
        self.selected_row = None

    def create(self):
        self.canvas = ctk.CTkCanvas(self.master, highlightthickness=0, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = ctk.CTkScrollbar(self.master, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ctk.CTkScrollbar(self.master, orientation="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.header_frame = ctk.CTkFrame(self.canvas, fg_color="#F5F5F5")
        self.data_frame = ctk.CTkFrame(self.canvas, fg_color="white")
        self.canvas.create_window((0, 0), window=self.header_frame, anchor="nw")
        self.canvas.create_window((0, 40), window=self.data_frame, anchor="nw")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        window_width = self.master.winfo_width() or 800
        col_width = max(100, window_width // (len(self.columns) + 1))
        for col_idx, col_name in enumerate(reversed(self.columns)):
            ctk.CTkLabel(
                self.header_frame,
                text=col_name,
                font=self.font,
                anchor="e",
                text_color="#1A2526",
                width=col_width,
                height=40
            ).grid(row=0, column=col_idx, padx=5, pady=5, sticky="ew")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_vertical)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_horizontal)
        self.master.bind("<Configure>", self._resize_columns)

    def _on_mousewheel_vertical(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_horizontal(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _resize_columns(self, event):
        if not self.columns:
            return
        window_width = self.master.winfo_width() or 800
        col_width = max(100, window_width // (len(self.columns) + 1))
        for col_idx in range(len(self.columns)):
            self.header_frame.grid_columnconfigure(col_idx, minsize=col_width)
        for row in self.rows:
            for col_idx, widget in enumerate(row):
                widget.configure(width=col_width)
        self.data_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_data(self, data):
        for row in self.rows:
            for widget in row:
                widget.destroy()
        self.rows = []
        self.selected_row = None

        window_width = self.master.winfo_width() or 800
        col_width = max(100, window_width // (len(self.columns) + 1))

        for row_idx, row_data in enumerate(data):
            row_widgets = []
            for col_idx, value in enumerate(reversed(row_data[1:])):  # Skip ID
                label = ctk.CTkLabel(
                    self.data_frame,
                    text=str(value),
                    font=self.font,
                    anchor="e",
                    text_color="#1A2526",
                    width=col_width,
                    height=30
                )
                label.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="ew")
                if self.on_click:
                    label.bind("<Button-1>", lambda e, idx=row_idx, id=row_data[0]: self.on_click(idx, id))
                if self.on_double_click:
                    label.bind("<Double-1>", lambda e, id=row_data[0]: self.on_double_click(id))
                row_widgets.append(label)
            self.rows.append(row_widgets)

        self.data_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def select_row(self, row_idx):
        if self.selected_row is not None and self.selected_row < len(self.rows):
            for widget in self.rows[self.selected_row]:
                widget.configure(fg_color="white")
        self.selected_row = row_idx
        if row_idx < len(self.rows):
            for widget in self.rows[row_idx]:
                widget.configure(fg_color="#E8ECEF")

# Main Application
class SalesSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Techspire-Muntazir Abbas Haider")
        self.root.geometry("1250x610")
        self.root.minsize(1100, 610)

        self.urdu_font = ("Nafees", 14)
        self.header_font = ("Nafees", 16, "bold")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=10, fg_color="#E8ECEF")
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="ایم ریاض اینڈ کو",
            font=("Nafees", 22, "bold"),
            text_color="#FFFFFF",
            fg_color="#1F2937",
            corner_radius=25,
            height=60,
            anchor="center"
        ).pack(pady=30, padx=30, fill="x")

        self.menu_buttons = []
        menu_items = [
            ("ڈیش بورڈ", self.show_dashboard),
            ("سیل ریکارڈ", self.show_sale),
            ("بقایا جات", self.show_dues),
            ("ادائیگی کی تاریخ", self.show_payment_history),
            ("اخراجات", self.show_akharajat),
            ("رپورٹ", self.show_report)
        ]
        for text, command in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=self.urdu_font,
                anchor="e",
                command=command,
                corner_radius=10,
                fg_color="#0078D7",
                hover_color="#005BB5",
                text_color="white",
                height=40
            )
            btn.pack(pady=8, padx=15, fill="x")
            self.menu_buttons.append(btn)

        ctk.CTkLabel(
            self.sidebar,
            text="Software Developed by Techspire\n© All Rights Reserved\n📞 0348-6991605\n🟢 WhatsApp: 0348-7958032",
            font=("Segoe UI", 14, "bold"),
            anchor="center",
            justify="left",
            text_color="#1A2526"
        ).pack(side="bottom", pady=5, fill="both", padx=5)

        # Main content frame
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="white")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_view = None
        self.items = []
        self.item_widgets = []
        self.total_bill_var = ctk.StringVar(value="کل بل: 0")
        self.customer_suggestions_cache = []
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        self.current_view = "dashboard"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "ڈیش بورڈ" else "#E8ECEF", text_color="white" if btn.cget("text") == "ڈیش بورڈ" else "#1A2526")

        dashboard_frame = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="white")
        dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        dashboard_frame.grid_rowconfigure(2, weight=1)
        dashboard_frame.grid_columnconfigure(0, weight=1)

        summary_frame = ctk.CTkFrame(dashboard_frame, corner_radius=10, fg_color="#F5F5F5")
        summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.total_sales_label = ctk.CTkLabel(
            summary_frame, text="کل کل سیل: 0", font=self.urdu_font, anchor="e", text_color="#1A2526"
        )
        self.total_sales_label.grid(row=0, column=2, padx=20, pady=10)

        self.total_paid_label = ctk.CTkLabel(
            summary_frame, text="کل کل ادا شدہ رقم: 0", font=self.urdu_font, anchor="e", text_color="#1A2526"
        )
        self.total_paid_label.grid(row=0, column=1, padx=20, pady=10)

        self.total_due_label = ctk.CTkLabel(
            summary_frame, text="کل کل بقایا: 0", font=self.urdu_font, anchor="e", text_color="#1A2526"
        )
        self.total_due_label.grid(row=0, column=0, padx=20, pady=10)

        search_frame = ctk.CTkFrame(dashboard_frame, corner_radius=10, fg_color="#F5F5F5")
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="صارف تلاش کریں", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.search_entry = AutocompleteEntry(
            search_frame,
            suggestions_callback=self.get_customer_suggestions,
            font=self.urdu_font,
            width=150,
            justify="right",
            placeholder_text="صارف کا نام درج کریں",
            allow_new=False
        )
        self.search_entry.grid(row=0, column=2, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_dashboard)
        self.search_entry.bind("<Return>", lambda e: self.time_period_button.focus_set())

        ctk.CTkLabel(search_frame, text="وقت کی مدت", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.time_period_button = ctk.CTkSegmentedButton(
            search_frame,
            values=["آج", "اس ہفتے", "اس ماہ"],
            font=self.urdu_font,
            command=lambda value: self.update_dashboard(None)
        )
        self.time_period_button.set("آج")  # Default to Today
        self.time_period_button.grid(row=0, column=0, padx=5, pady=5)

        self.dashboard_grid_frame = ctk.CTkFrame(dashboard_frame, fg_color="white")
        self.dashboard_grid_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.dashboard_grid_frame.grid_rowconfigure(0, weight=1)
        self.dashboard_grid_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_grid = CustomGrid(
            self.dashboard_grid_frame,
            columns=["تاریخ و وقت", "صارف", "مقدار", "فی یونٹ قیمت", "کل بل", "ادا شدہ رقم"],
            font=self.urdu_font,
            on_click=self.select_sale_row,
            on_double_click=self.edit_delete_sale
        )
        self.dashboard_grid.create()

        self.update_dashboard(None)

    def update_dashboard(self, event):
        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                # Determine date range based on time period
                time_period = self.time_period_button.get() if hasattr(self, 'time_period_button') else "آج"
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if time_period == "آج":
                    start_date = today
                    end_date = today.replace(hour=23, minute=59, second=59)
                elif time_period == "اس ہفتے":
                    # Start from Monday of the current week
                    start_date = today - timedelta(days=today.weekday())
                    end_date = today.replace(hour=23, minute=59, second=59)
                else:  # "اس ماہ"
                    start_date = today.replace(day=1)
                    end_date = today.replace(hour=23, minute=59, second=59)

                # Build SQL query
                query = """
                    SELECT s.id, s.sale_date, c.name, s.quantity, s.unit_price, s.total_amount, s.paid_amount
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id
                    WHERE s.sale_date BETWEEN %s AND %s
                """
                params = [start_date, end_date]
                search_text = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
                if search_text:
                    query += " AND LOWER(c.name) LIKE %s"
                    params.append(f"%{search_text}%")
                query += " ORDER BY s.sale_date DESC LIMIT 100"

                # Fetch data
                cursor.execute(query, params)
                data = [(row[0], row[1].strftime("%Y-%m-%d %H:%M"), row[2], f"{row[3]:.2f}",
                         f"{row[4]:.2f}", f"{row[5]:.2f}", f"{row[6]:.2f}") for row in cursor.fetchall()]
                self.dashboard_grid.data = data
                self.dashboard_grid.update_data(data)

                # Calculate totals for the filtered data
                totals_query = """
                    SELECT SUM(s.total_amount), SUM(s.paid_amount), SUM(s.due_amount)
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id
                    WHERE s.sale_date BETWEEN %s AND %s
                """
                totals_params = [start_date, end_date]
                if search_text:
                    totals_query += " AND LOWER(c.name) LIKE %s"
                    totals_params.append(f"%{search_text}%")
                cursor.execute(totals_query, totals_params)
                totals = cursor.fetchone()
                self.total_sales_label.configure(text=f"کل کل سیل: {totals[0] or 0:.2f}")
                self.total_paid_label.configure(text=f"کل کل ادا شدہ رقم: {totals[1] or 0:.2f}")
                self.total_due_label.configure(text=f"کل کل بقایا: {totals[2] or 0:.2f}")

                logging.info(f"Dashboard updated with {len(data)} records for period: {time_period}")
        except mysql.connector.Error as e:
            logging.error(f"Dashboard update failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def show_sale(self):
        self.clear_content()
        self.current_view = "sale"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "سیل ریکارڈ" else "#E8ECEF", text_color="white" if btn.cget("text") == "سیل ریکارڈ" else "#1A2526")

        form_frame = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="white")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="صارف کا نام", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.customer_entry = AutocompleteEntry(
            form_frame,
            suggestions_callback=self.get_customer_suggestions,
            font=self.urdu_font,
            width=300,
            justify="right",
            placeholder_text="صارف کا نام درج کریں"
        )
        self.customer_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.customer_entry.focus_set()
        self.customer_entry.bind("<Return>", lambda e: self.quantity.focus_set())

        self.single_item_frame = ctk.CTkFrame(form_frame, corner_radius=10, fg_color="#F5F5F5")
        self.single_item_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(self.single_item_frame, text="مقدار", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=3, padx=10, pady=5, sticky="e")
        self.quantity = ctk.CTkEntry(self.single_item_frame, font=self.urdu_font, width=100, justify="right", placeholder_text="مقدار")
        self.quantity.grid(row=0, column=2, padx=10, pady=5)
        self.quantity.bind("<Return>", lambda e: self.unit_price.focus_set())
        self.quantity.bind("<KeyRelease>", self.update_total_bill)

        ctk.CTkLabel(self.single_item_frame, text="فی یونٹ قیمت", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.unit_price = ctk.CTkEntry(self.single_item_frame, font=self.urdu_font, width=100, justify="right", placeholder_text="فی یونٹ قیمت")
        self.unit_price.grid(row=0, column=0, padx=10, pady=5)
        self.unit_price.bind("<Return>", lambda e: self.paid_amount.focus_set())
        self.unit_price.bind("<KeyRelease>", self.update_total_bill)

        self.items = []
        self.item_widgets = []

        self.total_bill_var.set("کل بل: 0")
        ctk.CTkLabel(form_frame, textvariable=self.total_bill_var, font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=2, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(form_frame, text="ادائیگی کی رقم (اختیاری)", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.paid_amount = ctk.CTkEntry(form_frame, font=self.urdu_font, width=300, justify="right", placeholder_text="اختیاری ادا شدہ رقم")
        self.paid_amount.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.paid_amount.bind("<Return>", lambda e: self.record_sale())

        button_frame = ctk.CTkFrame(form_frame, fg_color="white")
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ctk.CTkButton(
            button_frame,
            text="سیل ریکارڈ کریں",
            font=self.urdu_font,
            command=self.record_sale,
            corner_radius=8,
            fg_color="#0078D7",
            hover_color="#005BB5"
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame,
            text="اضافی آئٹم شامل کریں",
            font=self.urdu_font,
            command=self.add_item_row,
            corner_radius=8,
            fg_color="#0078D7",
            hover_color="#005BB5"
        ).grid(row=0, column=1, padx=5)

    def add_item_row(self):
        row_idx = len(self.items) + 1
        quantity_entry = ctk.CTkEntry(self.single_item_frame, font=self.urdu_font, width=100, justify="right", placeholder_text="مقدار")
        unit_price_entry = ctk.CTkEntry(self.single_item_frame, font=self.urdu_font, width=100, justify="right", placeholder_text="فی یونٹ قیمت")
        remove_button = ctk.CTkButton(
            self.single_item_frame,
            text="ہٹائیں",
            font=self.urdu_font,
            width=80,
            command=lambda: self.remove_item_row(row_idx - 1, quantity_entry, unit_price_entry, remove_button),
            corner_radius=8,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )

        ctk.CTkLabel(self.single_item_frame, text="مقدار", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=row_idx, column=3, padx=10, pady=5, sticky="e")
        quantity_entry.grid(row=row_idx, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.single_item_frame, text="فی یونٹ قیمت", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        unit_price_entry.grid(row=row_idx, column=0, padx=10, pady=5)
        remove_button.grid(row=row_idx, column=4, padx=10, pady=5)

        quantity_entry.bind("<KeyRelease>", self.update_total_bill)
        unit_price_entry.bind("<KeyRelease>", self.update_total_bill)
        quantity_entry.bind("<Return>", lambda e: unit_price_entry.focus_set())
        unit_price_entry.bind("<Return>", lambda e: self.paid_amount.focus_set())

        self.items.append((quantity_entry, unit_price_entry))
        self.item_widgets.append((quantity_entry, unit_price_entry, remove_button))

    def remove_item_row(self, index, quantity_entry, unit_price_entry, remove_button):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            quantity_entry.destroy()
            unit_price_entry.destroy()
            remove_button.destroy()
            self.item_widgets.pop(index)

            for i, (q_entry, p_entry, r_button) in enumerate(self.item_widgets):
                row_idx = i + 1
                ctk.CTkLabel(self.single_item_frame, text="مقدار", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=row_idx, column=3, padx=10, pady=5, sticky="e")
                q_entry.grid(row=row_idx, column=2, padx=10, pady=5)
                ctk.CTkLabel(self.single_item_frame, text="فی یونٹ قیمت", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
                p_entry.grid(row=row_idx, column=0, padx=10, pady=5)
                r_button.grid(row=row_idx, column=4, padx=10, pady=5)
                r_button.configure(command=lambda idx=i: self.remove_item_row(idx, q_entry, p_entry, r_button))

            self.update_total_bill()

    def update_total_bill(self, event=None):
        try:
            total = 0
            quantity = self.quantity.get().strip()
            unit_price = self.unit_price.get().strip()
            if quantity and unit_price:
                q = float(quantity)
                p = float(unit_price)
                if q > 0 and p > 0:
                    total += q * p
            for q_entry, p_entry in self.items:
                q = q_entry.get().strip()
                p = p_entry.get().strip()
                if q and p:
                    q_val = float(q)
                    p_val = float(p)
                    if q_val > 0 and p_val > 0:
                        total += q_val * p_val
            self.total_bill_var.set(f"کل بل: {total:.2f}")
        except ValueError:
            self.total_bill_var.set("کل بل: 0")

    def show_dues(self):
        self.clear_content()
        self.current_view = "dues"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "بقایا جات" else "#E8ECEF", text_color="white" if btn.cget("text") == "بقایا جات" else "#1A2526")

        dues_frame = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="white")
        dues_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        dues_frame.grid_rowconfigure(2, weight=1)
        dues_frame.grid_columnconfigure(0, weight=1)

        search_frame = ctk.CTkFrame(dues_frame, corner_radius=10, fg_color="#F5F5F5")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="صارف تلاش کریں", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.due_search_entry = AutocompleteEntry(
            search_frame,
            suggestions_callback=self.get_customer_suggestions,
            font=self.urdu_font,
            width=200,
            justify="right",
            placeholder_text="صارف کا نام درج کریں",
            allow_new=False
        )
        self.due_search_entry.grid(row=0, column=0, padx=10, pady=5)
        self.due_search_entry.bind("<KeyRelease>", self.update_dues)

        payment_frame = ctk.CTkFrame(dues_frame, corner_radius=10, fg_color="#F5F5F5")
        payment_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(payment_frame, text="صارف کا نام", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.due_customer_entry = AutocompleteEntry(
            payment_frame,
            suggestions_callback=self.get_customer_suggestions,
            font=self.urdu_font,
            width=200,
            justify="right",
            placeholder_text="صارف کا نام درج کریں"
        )
        self.due_customer_entry.grid(row=0, column=1, padx=10, pady=10)
        self.due_customer_entry.bind("<Return>", lambda e: self.payment_amount.focus_set())

        ctk.CTkLabel(payment_frame, text="ادائیگی کی رقم", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.payment_amount = ctk.CTkEntry(payment_frame, font=self.urdu_font, width=200, justify="right", placeholder_text="ادائیگی کی رقم")
        self.payment_amount.grid(row=0, column=0, padx=10, pady=10)
        self.payment_amount.bind("<Return>", lambda e: self.record_payment())

        ctk.CTkButton(
            payment_frame,
            text="ادائیگی ریکارڈ کریں",
            font=self.urdu_font,
            command=self.record_payment,
            corner_radius=8,
            fg_color="#0078D7",
            hover_color="#005BB5"
        ).grid(row=1, column=0, columnspan=3, pady=10)

        self.dues_grid_frame = ctk.CTkFrame(dues_frame, fg_color="white")
        self.dues_grid_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.dues_grid_frame.grid_rowconfigure(0, weight=1)
        self.dues_grid_frame.grid_columnconfigure(0, weight=1)

        self.dues_grid = CustomGrid(
            self.dues_grid_frame,
            columns=["صارف", "بقایا"],
            font=self.urdu_font,
            on_click=self.select_due_row,
            on_double_click=self.load_customer_from_dues
        )
        self.dues_grid.create()

        self.update_dues(None)

    def show_payment_history(self):
        self.clear_content()
        self.current_view = "payment_history"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "ادائیگی کی تاریخ" else "#E8ECEF", text_color="white" if btn.cget("text") == "ادائیگی کی تاریخ" else "#1A2526")

        history_frame = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="white")
        history_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        history_frame.grid_rowconfigure(1, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        search_frame = ctk.CTkFrame(history_frame, corner_radius=10, fg_color="#F5F5F5")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="صارف تلاش کریں", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.payment_search_entry = AutocompleteEntry(
            search_frame,
            suggestions_callback=self.get_customer_suggestions,
            font=self.urdu_font,
            width=150,
            justify="right",
            placeholder_text="صارف کا نام درج کریں",
            allow_new=False
        )
        self.payment_search_entry.grid(row=0, column=2, padx=5, pady=5)
        self.payment_search_entry.bind("<KeyRelease>", self.update_payment_history)
        self.payment_search_entry.bind("<Return>", lambda e: self.payment_time_period_button.focus_set())

        ctk.CTkLabel(search_frame, text="وقت کی مدت", font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.payment_time_period_button = ctk.CTkSegmentedButton(
            search_frame,
            values=["آج", "اس ہفتے", "اس ماہ"],
            font=self.urdu_font,
            command=lambda value: self.update_payment_history(None)
        )
        self.payment_time_period_button.set("آج")  # Default to Today
        self.payment_time_period_button.grid(row=0, column=0, padx=5, pady=5)

        self.payment_grid_frame = ctk.CTkFrame(history_frame, fg_color="white")
        self.payment_grid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.payment_grid_frame.grid_rowconfigure(0, weight=1)
        self.payment_grid_frame.grid_columnconfigure(0, weight=1)

        self.payment_grid = CustomGrid(
            self.payment_grid_frame,
            columns=["تاریخ و وقت", "صارف", "ادا شدہ رقم", "باقی بل"],
            font=self.urdu_font,
            on_click=self.select_payment_row,
            on_double_click=self.edit_delete_payment
        )
        self.payment_grid.create()

        self.update_payment_history(None)

    def show_akharajat(self):
        self.clear_content()
        self.current_view = "akharajat"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "اخراجات" else "#E8ECEF", text_color="white" if btn.cget("text") == "اخراجات" else "#1A2526")

        try:
            akharajat_main(self.content_frame, self.urdu_font)
        except Exception as e:
            logging.error(f"Akharajat module error: {str(e)}")
            messagebox.showerror("خطا", f"اخراجات لوڈ کرنے میں خطا: {str(e)}", parent=self.root)
            ctk.CTkLabel(
                self.content_frame,
                text="اخراجات ماڈیول لوڈ نہیں ہو سکا",
                font=self.urdu_font,
                text_color="#D32F2F"
            ).pack(pady=20)

    def show_report(self):
        self.clear_content()
        self.current_view = "report"
        for btn in self.menu_buttons:
            btn.configure(fg_color="#0078D7" if btn.cget("text") == "رپورٹ" else "#E8ECEF", text_color="white" if btn.cget("text") == "رپورٹ" else "#1A2526")

        try:
            report_main(self.content_frame, self.urdu_font)
        except Exception as e:
            logging.error(f"Report module error: {str(e)}")
            messagebox.showerror("خطا", f"رپورٹ لوڈ کرنے میں خطا: {str(e)}", parent=self.root)
            ctk.CTkLabel(
                self.content_frame,
                text="رپورٹ ماڈیول لوڈ نہیں ہو سکا",
                font=self.urdu_font,
                text_color="#D32F2F"
            ).pack(pady=20)

    def get_customer_suggestions(self, search_text):
        conn = connect_db()
        if conn is None:
            return []
        try:
            with conn.cursor() as cursor:
                if not search_text:
                    cursor.execute("SELECT name FROM customers ORDER BY name LIMIT 10")
                else:
                    cursor.execute("SELECT name FROM customers WHERE LOWER(name) LIKE %s ORDER BY name LIMIT 10", (f"%{search_text}%",))
                suggestions = [row[0] for row in cursor.fetchall()]
                self.customer_suggestions_cache = suggestions
                return suggestions
        except mysql.connector.Error as e:
            logging.error(f"Customer suggestions query failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def validate_amount(self, value, field_name, max_value=None, allow_zero=False):
        try:
            if not value.strip():
                if allow_zero:
                    return 0
                raise ValueError
            value = float(value)
            if value < 0:
                messagebox.showerror("خطا", f"{field_name} منفی نہیں ہو سکتی!", parent=self.root)
                return None
            if not allow_zero and value == 0:
                messagebox.showerror("خطا", f"{field_name} صفر نہیں ہو سکتی!", parent=self.root)
                return None
            if max_value is not None and value > max_value:
                messagebox.showerror("خطا", f"{field_name} بقایا ({max_value:.2f}) سے زیادہ نہیں ہو سکتی!", parent=self.root)
                return None
            return value
        except ValueError:
            messagebox.showerror("خطا", f"براہ کرم درست {field_name} درج کریں!", parent=self.root)
            return None

    def record_sale(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            name = self.customer_entry.get().strip()
            if not name:
                messagebox.showerror("خطا", "صارف کا نام درج کریں!", parent=self.root)
                return

            items = []
            quantity = self.validate_amount(self.quantity.get(), "مقدار", allow_zero=False)
            unit_price = self.validate_amount(self.unit_price.get(), "فی یونٹ قیمت", allow_zero=False)
            if quantity is None or unit_price is None:
                return
            if quantity > 0 and unit_price > 0:
                items.append((quantity, unit_price))

            for q_entry, p_entry in self.items:
                q = self.validate_amount(q_entry.get(), "مقدار", allow_zero=False)
                p = self.validate_amount(p_entry.get(), "فی یونٹ قیمت", allow_zero=False)
                if q is None or p is None:
                    return
                if q > 0 and p > 0:
                    items.append((q, p))

            if not items:
                messagebox.showerror("خطا", "کم از کم ایک آئٹم درج کریں!", parent=self.root)
                return

            paid = self.validate_amount(self.paid_amount.get(), "ادائیگی کی رقم", allow_zero=True)
            if paid is None:
                return

            total = sum(q * p for q, p in items)
            if paid > total:
                messagebox.showerror("خطا", f"ادائیگی کی رقم کل بل ({total:.2f}) سے زیادہ نہیں ہو سکتی!", parent=self.root)
                return

            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM customers WHERE name = %s", (name,))
                customer = cursor.fetchone()
                if not customer:
                    cursor.execute("INSERT INTO customers (name) VALUES (%s)", (name,))
                    conn.commit()
                    cursor.execute("SELECT id FROM customers WHERE name = %s", (name,))
                    customer = cursor.fetchone()

                customer_id = customer[0]
                sale_date = datetime.now()

                # Record each item as a separate sale for better tracking
                for quantity, unit_price in items:
                    total_amount = quantity * unit_price
                    due = total_amount - (paid if paid > 0 else 0)
                    cursor.execute("""
                        INSERT INTO sales (customer_id, quantity, unit_price, total_amount, paid_amount, due_amount, sale_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (customer_id, quantity, unit_price, total_amount, min(paid, total_amount), due, sale_date))
                    paid -= min(paid, total_amount)  # Deduct paid amount for this sale
                    if paid <= 0:
                        paid = 0

                if paid > 0:  # Record any initial payment
                    cursor.execute("""
                        INSERT INTO payments (customer_id, paid_amount, remaining_due, payment_date)
                        VALUES (%s, %s, %s, %s)
                    """, (customer_id, paid, total - paid, sale_date))

                conn.commit()
                logging.info(f"Sale recorded: customer_id={customer_id}, total={total}, paid={paid}")

            messagebox.showinfo("کامیابی", "سیل کامیابی سے ریکارڈ کی گئی!", parent=self.root)

            self.customer_entry.delete(0, ctk.END)
            self.quantity.delete(0, ctk.END)
            self.unit_price.delete(0, ctk.END)
            self.paid_amount.delete(0, ctk.END)
            for q_entry, p_entry, r_button in self.item_widgets:
                q_entry.destroy()
                p_entry.destroy()
                r_button.destroy()
            self.items = []
            self.item_widgets = []
            self.total_bill_var.set("کل بل: 0")
            self.customer_entry.focus_set()
            self.update_all_sections()

        except mysql.connector.Error as e:
            logging.error(f"Sale recording failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def select_sale_row(self, row_idx, sale_id):
        self.dashboard_grid.select_row(row_idx)

    def select_payment_row(self, row_idx, payment_id):
        self.payment_grid.select_row(row_idx)

    def select_due_row(self, row_idx, customer_id):
        self.dues_grid.select_row(row_idx)

    def edit_delete_sale(self, sale_id):
        if not sale_id:
            messagebox.showerror("خطا", "براہ کرم ایک سیل منتخب کریں!", parent=self.root)
            return

        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.quantity, s.unit_price, s.paid_amount, c.name
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id
                    WHERE s.id = %s
                """, (sale_id,))
                sale = cursor.fetchone()
                if not sale:
                    messagebox.showerror("خطا", "سیل نہیں ملی!", parent=self.root)
                    return

                quantity, unit_price, paid_amount, customer_name = sale

                edit_window = ctk.CTkToplevel(self.root)
                edit_window.title("سیل ترمیم/حذف کریں")
                edit_window.geometry("400x250")
                edit_window.transient(self.root)
                edit_window.grab_set()
                edit_window.update_idletasks()
                width = edit_window.winfo_width()
                height = edit_window.winfo_height()
                x = (self.root.winfo_screenwidth() // 2) - (width // 2)
                y = (self.root.winfo_screenheight() // 2) - (height // 2)
                edit_window.geometry(f"+{x}+{y}")

                ctk.CTkLabel(edit_window, text="صارف کا نام", font=self.urdu_font, anchor="e").grid(row=0, column=1, padx=10, pady=10, sticky="e")
                ctk.CTkLabel(edit_window, text=customer_name, font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=0, padx=10, pady=10, sticky="e")

                ctk.CTkLabel(edit_window, text="مقدار", font=self.urdu_font, anchor="e").grid(row=1, column=1, padx=10, pady=10, sticky="e")
                quantity_entry = ctk.CTkEntry(edit_window, font=self.urdu_font, width=200, justify="right")
                quantity_entry.grid(row=1, column=0, padx=10, pady=10)
                quantity_entry.insert(0, str(quantity))
                quantity_entry.bind("<Return>", lambda e: unit_price_entry.focus_set())

                ctk.CTkLabel(edit_window, text="فی یونٹ قیمت", font=self.urdu_font, anchor="e").grid(row=2, column=1, padx=10, pady=10, sticky="e")
                unit_price_entry = ctk.CTkEntry(edit_window, font=self.urdu_font, width=200, justify="right")
                unit_price_entry.grid(row=2, column=0, padx=10, pady=10)
                unit_price_entry.insert(0, str(unit_price))

                def save_changes():
                    try:
                        new_quantity = self.validate_amount(quantity_entry.get(), "مقدار", allow_zero=False)
                        new_unit_price = self.validate_amount(unit_price_entry.get(), "فی یونٹ قیمت", allow_zero=False)
                        if new_quantity is None or new_unit_price is None:
                            return

                        new_total = new_quantity * new_unit_price
                        new_due = new_total - paid_amount
                        if new_due < 0:
                            messagebox.showerror("خطا", f"نیا کل بل ({new_total:.2f}) ادا شدہ رقم ({paid_amount:.2f}) سے کم نہیں ہو سکتا!", parent=edit_window)
                            return

                        with connect_db() as conn2:
                            if conn2 is None:
                                return
                            with conn2.cursor() as cursor2:
                                cursor2.execute("""
                                    UPDATE sales
                                    SET quantity = %s, unit_price = %s, total_amount = %s, due_amount = %s
                                    WHERE id = %s
                                """, (new_quantity, new_unit_price, new_total, new_due, sale_id))
                                conn2.commit()
                                logging.info(f"Sale edited: id={sale_id}, total={new_total}, due={new_due}")

                        messagebox.showinfo("کامیابی", "سیل کامیابی سے ترمیم کی گئی!", parent=edit_window)
                        edit_window.destroy()
                        self.update_all_sections()
                    except mysql.connector.Error as e:
                        logging.error(f"Sale edit failed: {str(e)}")
                        messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=edit_window)
                        conn2.rollback()

                def delete_sale():
                    if messagebox.askyesno("تصدیق", "کیا آپ واقعی اس سیل کو حذف کرنا چاہتے ہیں؟", parent=edit_window):
                        try:
                            with connect_db() as conn2:
                                if conn2 is None:
                                    return
                                with conn2.cursor() as cursor2:
                                    cursor2.execute("DELETE FROM sales WHERE id = %s", (sale_id,))
                                    conn2.commit()
                                    logging.info(f"Sale deleted: id={sale_id}")
                            messagebox.showinfo("کامیابی", "سیل کامیابی سے حذف کی گئی!", parent=edit_window)
                            edit_window.destroy()
                            self.update_all_sections()
                        except mysql.connector.Error as e:
                            logging.error(f"Sale deletion failed: {str(e)}")
                            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=edit_window)
                            conn2.rollback()

                ctk.CTkButton(
                    edit_window,
                    text="محفوظ کریں",
                    font=self.urdu_font,
                    command=save_changes,
                    corner_radius=8,
                    fg_color="#0078D7",
                    hover_color="#005BB5"
                ).grid(row=3, column=0, padx=5, pady=10)

                ctk.CTkButton(
                    edit_window,
                    text="حذف کریں",
                    font=self.urdu_font,
                    command=delete_sale,
                    corner_radius=8,
                    fg_color="#D32F2F",
                    hover_color="#B71C1C"
                ).grid(row=3, column=1, padx=5, pady=10)

        except mysql.connector.Error as e:
            logging.error(f"Sale edit/delete query failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def edit_delete_payment(self, payment_id):
        if not payment_id:
            messagebox.showerror("خطا", "براہ کرم ایک ادائیگی منتخب کریں!", parent=self.root)
            return

        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.paid_amount, c.name, p.customer_id, p.remaining_due
                    FROM payments p
                    JOIN customers c ON p.customer_id = c.id
                    WHERE p.id = %s
                """, (payment_id,))
                payment = cursor.fetchone()
                if not payment:
                    messagebox.showerror("خطا", "ادائیگی نہیں ملی!", parent=self.root)
                    return

                old_paid, customer_name, customer_id, remaining_due = payment

                edit_window = ctk.CTkToplevel(self.root)
                edit_window.title("ادائیگی ترمیم/حذف کریں")
                edit_window.geometry("400x200")
                edit_window.transient(self.root)
                edit_window.grab_set()
                edit_window.update_idletasks()
                width = edit_window.winfo_width()
                height = edit_window.winfo_height()
                x = (self.root.winfo_screenwidth() // 2) - (width // 2)
                y = (self.root.winfo_screenheight() // 2) - (height // 2)
                edit_window.geometry(f"+{x}+{y}")

                ctk.CTkLabel(edit_window, text="صارف کا نام", font=self.urdu_font, anchor="e").grid(row=0, column=1, padx=10, pady=10, sticky="e")
                ctk.CTkLabel(edit_window, text=customer_name, font=self.urdu_font, anchor="e", text_color="#1A2526").grid(row=0, column=0, padx=10, pady=10, sticky="e")

                ctk.CTkLabel(edit_window, text="ادا شدہ رقم", font=self.urdu_font, anchor="e").grid(row=1, column=1, padx=10, pady=10, sticky="e")
                paid_entry = ctk.CTkEntry(edit_window, font=self.urdu_font, width=200, justify="right")
                paid_entry.grid(row=1, column=0, padx=10, pady=10)
                paid_entry.insert(0, str(old_paid))

                def save_changes():
                    try:
                        new_paid = self.validate_amount(paid_entry.get(), "ادا شدہ رقم", allow_zero=False)
                        if new_paid is None:
                            return

                        with connect_db() as conn2:
                            if conn2 is None:
                                return
                            with conn2.cursor() as cursor2:
                                # Calculate total due for customer
                                cursor2.execute("SELECT SUM(due_amount) FROM sales WHERE customer_id = %s", (customer_id,))
                                total_due = cursor2.fetchone()[0] or 0
                                total_due += old_paid  # Add back the old payment

                                if new_paid > total_due:
                                    messagebox.showerror("خطا", f"ادائیگی کی رقم بقایا ({total_due:.2f}) سے زیادہ نہیں ہو سکتی!", parent=edit_window)
                                    return

                                # Revert old payment
                                remaining_old_paid = old_paid
                                cursor2.execute("SELECT id, due_amount, paid_amount FROM sales WHERE customer_id = %s AND paid_amount > 0 ORDER BY sale_date DESC", (customer_id,))
                                sales = cursor2.fetchall()
                                for sale_id, due_amount, current_paid in sales:
                                    if remaining_old_paid <= 0:
                                        break
                                    revert_amount = min(remaining_old_paid, current_paid)
                                    new_due = due_amount + revert_amount
                                    new_paid_sale = current_paid - revert_amount
                                    cursor2.execute("""
                                        UPDATE sales
                                        SET paid_amount = %s, due_amount = %s
                                        WHERE id = %s
                                    """, (new_paid_sale, new_due, sale_id))
                                    remaining_old_paid -= revert_amount

                                # Apply new payment
                                remaining_payment = new_paid
                                cursor2.execute("SELECT id, due_amount FROM sales WHERE customer_id = %s AND due_amount > 0 ORDER BY sale_date", (customer_id,))
                                sales = cursor2.fetchall()
                                for sale_id, due_amount in sales:
                                    if remaining_payment <= 0:
                                        break
                                    payment_for_sale = min(remaining_payment, due_amount)
                                    new_due = due_amount - payment_for_sale
                                    cursor2.execute("""
                                        UPDATE sales SET paid_amount = paid_amount + %s, due_amount = %s
                                        WHERE id = %s
                                    """, (payment_for_sale, new_due, sale_id))
                                    remaining_payment -= payment_for_sale

                                # Update payment record
                                remaining_due = max(0, total_due - new_paid)
                                cursor2.execute("""
                                    UPDATE payments
                                    SET paid_amount = %s, remaining_due = %s
                                    WHERE id = %s
                                """, (new_paid, remaining_due, payment_id))

                                conn2.commit()
                                logging.info(f"Payment edited: id={payment_id}, customer_id={customer_id}, amount={new_paid}")

                        messagebox.showinfo("کامیابی", "ادائیگی کامیابی سے ترمیم کی گئی!", parent=edit_window)
                        edit_window.destroy()
                        self.update_all_sections()
                    except mysql.connector.Error as e:
                        logging.error(f"Payment edit failed: {str(e)}")
                        messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=edit_window)
                        conn2.rollback()

                def delete_payment():
                    if messagebox.askyesno("تصدیق", "کیا آپ واقعی اس ادائیگی کو حذف کرنا چاہتے ہیں؟", parent=edit_window):
                        try:
                            with connect_db() as conn2:
                                if conn2 is None:
                                    return
                                with conn2.cursor() as cursor2:
                                    # Revert payment from sales
                                    remaining_old_paid = old_paid
                                    cursor2.execute("SELECT id, due_amount, paid_amount FROM sales WHERE customer_id = %s AND paid_amount > 0 ORDER BY sale_date DESC", (customer_id,))
                                    sales = cursor2.fetchall()
                                    for sale_id, due_amount, current_paid in sales:
                                        if remaining_old_paid <= 0:
                                            break
                                        revert_amount = min(remaining_old_paid, current_paid)
                                        new_due = due_amount + revert_amount
                                        new_paid_sale = current_paid - revert_amount
                                        cursor2.execute("""
                                            UPDATE sales
                                            SET paid_amount = %s, due_amount = %s
                                            WHERE id = %s
                                        """, (new_paid_sale, new_due, sale_id))
                                        remaining_old_paid -= revert_amount

                                    # Delete payment record
                                    cursor2.execute("DELETE FROM payments WHERE id = %s", (payment_id,))
                                    conn2.commit()
                                    logging.info(f"Payment deleted: id={payment_id}")

                            messagebox.showinfo("کامیابی", "ادائیگی کامیابی سے حذف کی گئی!", parent=edit_window)
                            edit_window.destroy()
                            self.update_all_sections()
                        except mysql.connector.Error as e:
                            logging.error(f"Payment deletion failed: {str(e)}")
                            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=edit_window)
                            conn2.rollback()

                ctk.CTkButton(
                    edit_window,
                    text="محفوظ کریں",
                    font=self.urdu_font,
                    command=save_changes,
                    corner_radius=8,
                    fg_color="#0078D7",
                    hover_color="#005BB5"
                ).grid(row=2, column=0, padx=5, pady=10)

                ctk.CTkButton(
                    edit_window,
                    text="حذف کریں",
                    font=self.urdu_font,
                    command=delete_payment,
                    corner_radius=8,
                    fg_color="#D32F2F",
                    hover_color="#B71C1C"
                ).grid(row=2, column=1, padx=5, pady=10)

        except mysql.connector.Error as e:
            logging.error(f"Payment edit/delete query failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def record_payment(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            name = self.due_customer_entry.get().strip()
            if not name:
                messagebox.showerror("خطا", "صارف کا نام درج کریں!", parent=self.root)
                return
            payment = self.validate_amount(self.payment_amount.get(), "ادائیگی کی رقم", allow_zero=False)
            if payment is None:
                return

            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM customers WHERE name = %s", (name,))
                customer = cursor.fetchone()
                if not customer:
                    messagebox.showerror("خطا", "صارف نہیں ملا!", parent=self.root)
                    return

                customer_id = customer[0]
                cursor.execute("SELECT SUM(due_amount) FROM sales WHERE customer_id = %s", (customer_id,))
                total_due = cursor.fetchone()[0] or 0
                if total_due <= 0:
                    messagebox.showerror("خطا", "اس صارف کے کوئی بقایا جات نہیں ہیں!", parent=self.root)
                    return
                if payment > total_due:
                    messagebox.showerror("خطا", f"ادائیگی کی رقم بقایا ({total_due:.2f}) سے زیادہ نہیں ہو سکتی!", parent=self.root)
                    return

                # Apply payment to sales in chronological order
                remaining_payment = payment
                cursor.execute("SELECT id, due_amount FROM sales WHERE customer_id = %s AND due_amount > 0 ORDER BY sale_date", (customer_id,))
                sales = cursor.fetchall()
                for sale_id, due_amount in sales:
                    if remaining_payment <= 0:
                        break
                    payment_for_sale = min(remaining_payment, due_amount)
                    new_due = due_amount - payment_for_sale
                    cursor.execute("""
                        UPDATE sales SET paid_amount = paid_amount + %s, due_amount = %s
                        WHERE id = %s
                    """, (payment_for_sale, new_due, sale_id))
                    remaining_payment -= payment_for_sale

                # Record payment
                remaining_due = max(0, total_due - payment)
                cursor.execute("""
                    INSERT INTO payments (customer_id, paid_amount, remaining_due, payment_date)
                    VALUES (%s, %s, %s, %s)
                """, (customer_id, payment, remaining_due, datetime.now()))

                conn.commit()
                logging.info(f"Payment recorded: customer_id={customer_id}, amount={payment}")

                messagebox.showinfo("کامیابی", "ادائیگی کامیابی سے ریکارڈ کی گئی!", parent=self.root)

                self.due_customer_entry.delete(0, ctk.END)
                self.payment_amount.delete(0, ctk.END)
                self.due_customer_entry.focus_set()
                self.update_all_sections()

        except mysql.connector.Error as e:
            logging.error(f"Payment recording failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def load_customer_from_dues(self, customer_id):
        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM customers WHERE id = %s", (customer_id,))
                customer_name = cursor.fetchone()[0]
                self.due_customer_entry.delete(0, ctk.END)
                self.due_customer_entry.insert(0, customer_name)
                self.payment_amount.focus_set()
        except mysql.connector.Error as e:
            logging.error(f"Load customer from dues failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_all_sections(self):
        if self.current_view == "dashboard":
            self.update_dashboard(None)
        elif self.current_view == "dues":
            self.update_dues(None)
        elif self.current_view == "payment_history":
            self.update_payment_history(None)
        else:
            self.update_dashboard(None)
            self.update_dues(None)
            self.update_payment_history(None)

    def update_dues(self, event):
        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT c.id, c.name, SUM(s.due_amount)
                    FROM customers c
                    JOIN sales s ON c.id = s.customer_id
                    WHERE s.due_amount > 0
                    GROUP BY c.id, c.name
                """
                params = []
                search_text = self.due_search_entry.get().strip().lower() if hasattr(self, 'due_search_entry') else ""
                if search_text:
                    query += " HAVING LOWER(c.name) LIKE %s"
                    params.append(f"%{search_text}%")
                query += " ORDER BY c.name LIMIT 100"

                cursor.execute(query, params)
                data = [(row[0], row[1], f"{row[2]:.2f}") for row in cursor.fetchall()]
                self.dues_grid.data = data
                self.dues_grid.update_data(data)
                logging.info(f"Dues updated with {len(data)} records")

        except mysql.connector.Error as e:
            logging.error(f"Dues update failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_payment_history(self, event):
        conn = connect_db()
        if conn is None:
            return
        try:
            with conn.cursor() as cursor:
                # Determine date range based on time period
                time_period = self.payment_time_period_button.get() if hasattr(self, 'payment_time_period_button') else "آج"
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if time_period == "آج":
                    start_date = today
                    end_date = today.replace(hour=23, minute=59, second=59)
                elif time_period == "اس ہفتے":
                    # Start from Monday of the current week
                    start_date = today - timedelta(days=today.weekday())
                    end_date = today.replace(hour=23, minute=59, second=59)
                else:  # "اس ماہ"
                    start_date = today.replace(day=1)
                    end_date = today.replace(hour=23, minute=59, second=59)

                # Build SQL query
                query = """
                    SELECT p.id, p.payment_date, c.name, p.paid_amount, p.remaining_due
                    FROM payments p
                    JOIN customers c ON p.customer_id = c.id
                    WHERE p.payment_date BETWEEN %s AND %s
                """
                params = [start_date, end_date]
                search_text = self.payment_search_entry.get().strip().lower() if hasattr(self, 'payment_search_entry') else ""
                if search_text:
                    query += " AND LOWER(c.name) LIKE %s"
                    params.append(f"%{search_text}%")
                query += " ORDER BY p.payment_date DESC LIMIT 100"

                cursor.execute(query, params)
                data = [(row[0], row[1].strftime("%Y-%m-%d %H:%M"), row[2], f"{row[3]:.2f}", f"{row[4]:.2f}")
                        for row in cursor.fetchall()]
                self.payment_grid.data = data
                self.payment_grid.update_data(data)
                logging.info(f"Payment history updated with {len(data)} records for period: {time_period}")

        except mysql.connector.Error as e:
            logging.error(f"Payment history update failed: {str(e)}")
            messagebox.showerror("خطا", f"ڈیٹابیس خطا: {str(e)}", parent=self.root)
            conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

if __name__ == "__main__":
    setup_database()
    root = ctk.CTk()
    app = SalesSystem(root)
    root.mainloop()