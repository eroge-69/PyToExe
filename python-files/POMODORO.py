import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime, date
import time
import calendar
try:
    import winsound
    WINDOWS = True
except ImportError:
    WINDOWS = False

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer 🍅")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fa")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Custom fonts
        self.large_font = font.Font(family="Helvetica", size=48, weight="bold")
        self.medium_font = font.Font(family="Helvetica", size=14)
        self.small_font = font.Font(family="Helvetica", size=12)

        # Color scheme
        self.colors = {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#e74c3c",
            "work": "#e74c3c",
            "break": "#2ecc71",
            "long_break": "#3498db",
            "background": "#f5f7fa",
            "text": "#2c3e50",
            "highlight": "#f1c40f"
        }

        # Database setup
        self.conn = sqlite3.connect('pomodoro.db', check_same_thread=False)
        self.create_db()

        # Timer settings
        self.timer_configs = {
            "Standard": {"work": 25, "break": 5, "long_break": 15, "cycles": 4},
            "Short": {"work": 15, "break": 3, "long_break": 10, "cycles": 3},
            "Long": {"work": 50, "break": 10, "long_break": 20, "cycles": 2}
        }
        self.current_config = "Standard"
        self.work_time = self.timer_configs[self.current_config]["work"] * 60
        self.break_time = self.timer_configs[self.current_config]["break"] * 60
        self.long_break_time = self.timer_configs[self.current_config]["long_break"] * 60
        self.cycles = self.timer_configs[self.current_config]["cycles"]
        self.target_hours = 4  # Default target hours per day

        self.is_running = False
        self.is_paused = False
        self.is_work = True
        self.current_time = self.work_time
        self.cycle_count = 0
        self.session_count = 0
        self.total_work_time = 0
        self.start_timestamp = None

        # Floating timer window
        self.floating_window = None
        self.floating_timer_label = None
        self.floating_status_indicator = None
        self.floating_start_button = None
        self.floating_pause_button = None

        # GUI setup
        self.setup_gui()

    def create_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS sessions
                            (date TEXT, sessions INTEGER, work_time INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                            (id INTEGER PRIMARY KEY, target_hours REAL)''')
            
            # Initialize settings if not exists
            cursor.execute("INSERT OR IGNORE INTO settings (id, target_hours) VALUES (1, 4.0)")
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create database: {e}")

    def setup_gui(self):
        # Configure styles
        self.configure_styles()

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Timer
        self.timer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer_tab, text="Timer ⏰")
        self.setup_timer_tab()

        # Tab 2: Progress
        self.progress_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_tab, text="Progress 📊")
        self.setup_progress_tab()

        # Tab 3: Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings ⚙️")
        self.setup_settings_tab()

        # Create floating timer window
        self.create_floating_window()

        self.update_stats()
        self.update_progress()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure("TFrame", background=self.colors["background"])
        style.configure("TNotebook", background=self.colors["background"])
        style.configure("TNotebook.Tab", 
                      font=self.medium_font, 
                      padding=[10, 5],
                      background=self.colors["background"],
                      foreground=self.colors["text"])
        style.map("TNotebook.Tab", 
                 background=[("selected", self.colors["primary"])],
                 foreground=[("selected", "white")])

        # Button styles
        style.configure("Start.TButton", 
                       font=self.medium_font, 
                       padding=10, 
                       background="#27ae60", 
                       foreground="white")
        style.configure("Stop.TButton", 
                       font=self.medium_font, 
                       padding=10, 
                       background="#e74c3c", 
                       foreground="white")
        style.configure("Reset.TButton", 
                       font=self.medium_font, 
                       padding=10, 
                       background="#f39c12", 
                       foreground="white")
        style.configure("Settings.TButton", 
                       font=self.medium_font, 
                       padding=10, 
                       background="#3498db", 
                       foreground="white")

        # Label styles
        style.configure("TLabel", 
                      font=self.small_font, 
                      background=self.colors["background"], 
                      foreground=self.colors["text"])
        style.configure("Large.TLabel", 
                       font=self.large_font, 
                       background=self.colors["background"])

    def create_floating_window(self):
        if self.floating_window:
            self.floating_window.destroy()
        
        # Taskbar-style dimensions
        taskbar_height = 40
        window_width = 200
        
        self.floating_window = tk.Toplevel(self.root)
        self.floating_window.title("Pomodoro Timer")
        self.floating_window.geometry(f"{window_width}x{taskbar_height}")
        self.floating_window.attributes('-topmost', True)
        self.floating_window.resizable(False, False)
        self.floating_window.configure(bg=self.colors["secondary"])
        self.floating_window.overrideredirect(True)  # Remove window decorations
        
        # Make the floating window always stay on top of other windows
        self.floating_window.wm_attributes("-topmost", 1)
        
        # Add mouse drag functionality
        def move_window(event):
            self.floating_window.geometry(f"+{event.x_root}+{event.y_root}")
        
        self.floating_window.bind('<B1-Motion>', move_window)
        
        # Main frame for the floating window
        frame = tk.Frame(self.floating_window, bg=self.colors["secondary"])
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Timer label (compact version)
        self.floating_timer_label = tk.Label(
            frame, 
            text="25:00", 
            font=("Helvetica", 12, "bold"), 
            bg=self.colors["secondary"], 
            fg="white",
            width=7
        )
        self.floating_timer_label.pack(side=tk.LEFT, padx=2)
        
        # Status indicator (small circle)
        self.floating_status_indicator = tk.Canvas(
            frame, 
            width=16, 
            height=16, 
            bg=self.colors["secondary"], 
            highlightthickness=0
        )
        self.floating_status_indicator.pack(side=tk.LEFT, padx=2)
        self.update_status_indicator()
        
        # Button frame
        btn_frame = tk.Frame(frame, bg=self.colors["secondary"])
        btn_frame.pack(side=tk.RIGHT, padx=2)
        
        # Start/Stop button
        self.floating_start_button = tk.Button(
            btn_frame, 
            text="▶", 
            font=("Helvetica", 10), 
            bg="#27ae60", 
            fg="white",
            relief="flat",
            bd=0,
            width=3,
            command=self.start_timer
        )
        self.floating_start_button.pack(side=tk.LEFT, padx=1)
        
        # Pause/Resume button
        self.floating_pause_button = tk.Button(
            btn_frame, 
            text="⏸", 
            font=("Helvetica", 10), 
            bg="#3498db", 
            fg="white",
            relief="flat",
            bd=0,
            width=3,
            command=self.toggle_pause
        )
        self.floating_pause_button.pack(side=tk.LEFT, padx=1)
        
        # Close button
        tk.Button(
            btn_frame, 
            text="✕", 
            font=("Helvetica", 10), 
            bg="#e74c3c", 
            fg="white",
            relief="flat",
            bd=0,
            width=3,
            command=self.toggle_floating_window
        ).pack(side=tk.LEFT, padx=1)

    def update_status_indicator(self):
        """Update the small status indicator circle"""
        self.floating_status_indicator.delete("all")
        color = self.colors["work"] if self.is_work else (
            self.colors["long_break"] if self.cycle_count >= self.cycles - 1 else self.colors["break"]
        )
        self.floating_status_indicator.create_oval(
            2, 2, 14, 14, 
            fill=color, 
            outline=color
        )

    def toggle_floating_window(self):
        if self.floating_window.winfo_viewable():
            self.floating_window.withdraw()
        else:
            self.floating_window.deiconify()

    def setup_timer_tab(self):
        frame = ttk.Frame(self.timer_tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Timer display
        self.main_timer_label = ttk.Label(
            frame, 
            text="25:00", 
            font=self.large_font, 
            foreground=self.colors["work"],
            style="Large.TLabel"
        )
        self.main_timer_label.pack(pady=(10, 5))

        self.main_status_label = ttk.Label(
            frame, 
            text="Work Time", 
            foreground=self.colors["text"],
            font=("Helvetica", 14, "bold")
        )
        self.main_status_label.pack()

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            frame, 
            orient="horizontal", 
            length=300, 
            mode="determinate"
        )
        self.progress_bar.pack(pady=10)
        self.update_progress_bar()

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=15)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Start ▶️", 
            style="Start.TButton", 
            command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.main_stop_button = ttk.Button(
            button_frame, 
            text="Stop ⏹️", 
            style="Stop.TButton", 
            command=self.stop_timer, 
            state="disabled"
        )
        self.main_stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Reset 🔄", 
            style="Reset.TButton", 
            command=self.reset_timer
        ).grid(row=0, column=2, padx=5)

        # Configuration dropdown
        config_frame = ttk.Frame(frame)
        config_frame.pack(pady=10)
        
        ttk.Label(config_frame, text="Timer Preset:").pack(side=tk.LEFT, padx=5)
        self.config_var = tk.StringVar(value="Standard")
        config_menu = ttk.OptionMenu(
            config_frame, 
            self.config_var, 
            "Standard", 
            *self.timer_configs.keys(), 
            command=self.change_config
        )
        config_menu.pack(side=tk.LEFT)

        # Stats display
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(pady=20)
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text="Today's Sessions: 0\nToday's Work: 0 hr", 
            foreground=self.colors["text"],
            font=self.small_font
        )
        self.stats_label.pack()

    def setup_progress_tab(self):
        frame = ttk.Frame(self.progress_tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Calendar selection
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        selection_frame = ttk.Frame(frame)
        selection_frame.pack(pady=10)
        
        ttk.Label(selection_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar(value=str(current_month))
        ttk.OptionMenu(
            selection_frame, 
            self.month_var, 
            str(current_month), 
            *[str(i) for i in range(1, 13)], 
            command=self.update_progress
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(selection_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar(value=str(current_year))
        ttk.OptionMenu(
            selection_frame, 
            self.year_var, 
            str(current_year), 
            *[str(i) for i in range(current_year-5, current_year+1)], 
            command=self.update_progress
        ).pack(side=tk.LEFT, padx=5)

        # Calendar canvas
        self.calendar_canvas = tk.Canvas(
            frame, 
            bg=self.colors["background"], 
            height=300,
            highlightthickness=0
        )
        self.calendar_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Weekly summary
        summary_frame = ttk.Frame(frame)
        summary_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            summary_frame, 
            text="Weekly Summary:", 
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w")
        
        self.weekly_summary = ttk.Label(
            summary_frame, 
            text="Loading...",
            wraplength=400
        )
        self.weekly_summary.pack(anchor="w")

        self.update_progress()

    def setup_settings_tab(self):
        frame = ttk.Frame(self.settings_tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ttk.Label(
            frame, 
            text="Custom Timer Settings", 
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        # Create a scrollable frame for settings
        canvas = tk.Canvas(frame, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

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

        # Timer settings
        settings_frame = ttk.Frame(scrollable_frame)
        settings_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(settings_frame, text="Work Time (min):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.work_entry = ttk.Entry(settings_frame)
        self.work_entry.insert(0, str(self.timer_configs[self.current_config]["work"]))
        self.work_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(settings_frame, text="Break Time (min):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.break_entry = ttk.Entry(settings_frame)
        self.break_entry.insert(0, str(self.timer_configs[self.current_config]["break"]))
        self.break_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(settings_frame, text="Long Break Time (min):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.long_break_entry = ttk.Entry(settings_frame)
        self.long_break_entry.insert(0, str(self.timer_configs[self.current_config]["long_break"]))
        self.long_break_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(settings_frame, text="Cycles before long break:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.cycles_entry = ttk.Entry(settings_frame)
        self.cycles_entry.insert(0, str(self.timer_configs[self.current_config]["cycles"]))
        self.cycles_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(settings_frame, text="Daily Target Hours:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.target_entry = ttk.Entry(settings_frame)
        self.target_entry.insert(0, str(self.target_hours))
        self.target_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Save button
        ttk.Button(
            scrollable_frame, 
            text="Save Settings 💾", 
            style="Settings.TButton", 
            command=self.save_settings
        ).pack(pady=20)

    def update_progress(self, *args):
        self.calendar_canvas.delete("all")
        month = int(self.month_var.get())
        year = int(self.year_var.get())
        cal = calendar.monthcalendar(year, month)
        target_minutes = self.target_hours * 60
        today = date.today()
        today_str = today.isoformat()

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT date, work_time FROM sessions WHERE strftime('%Y-%m', date) = ?", 
                         (f"{year}-{month:02d}",))
            sessions = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Update weekly summary
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            cursor.execute("SELECT SUM(work_time) FROM sessions WHERE date BETWEEN ? AND ?", 
                         (start_date.isoformat(), end_date.isoformat()))
            total_work = cursor.fetchone()[0] or 0
            total_hours = total_work / 60
            target_hours = self.target_hours * end_date.day
            completion = (total_hours / target_hours * 100) if target_hours > 0 else 0
            
            self.weekly_summary.config(
                text=f"Month: {calendar.month_name[month]} {year}\n"
                     f"Total Work: {total_hours:.1f} hours\n"
                     f"Target: {target_hours:.1f} hours\n"
                     f"Completion: {completion:.1f}%"
            )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch sessions: {e}")
            return

        # Draw month header
        self.calendar_canvas.create_text(
            150, 20, 
            text=f"{calendar.month_name[month]} {year}", 
            font=("Helvetica", 14, "bold"), 
            fill=self.colors["primary"]
        )

        # Draw day names
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            self.calendar_canvas.create_text(
                50 + i * 50, 50, 
                text=day, 
                font=("Helvetica", 10, "bold"), 
                fill=self.colors["text"]
            )

        # Draw calendar days
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                date_str = f"{year}-{month:02d}-{day:02d}"
                work_time = sessions.get(date_str, 0)
                progress = min(work_time / target_minutes, 1.0) if target_minutes > 0 else 0
                x = 30 + day_idx * 50
                y = 70 + week_idx * 50
                
                # Highlight today's date
                if date_str == today_str:
                    self.calendar_canvas.create_rectangle(
                        x - 20, y - 15, 
                        x + 20, y + 25, 
                        fill=self.colors["highlight"], 
                        outline=""
                    )
                
                # Draw day number
                self.calendar_canvas.create_text(
                    x, y, 
                    text=str(day), 
                    font=("Helvetica", 10), 
                    fill=self.colors["text"]
                )
                
                # Draw progress bar
                if progress > 0:
                    bar_height = 20 * progress
                    self.calendar_canvas.create_rectangle(
                        x - 15, y + 10, 
                        x + 15, y + 10 + bar_height, 
                        fill=self.colors["accent"], 
                        outline=""
                    )

    def change_config(self, config):
        self.current_config = config
        self.work_time = self.timer_configs[config]["work"] * 60
        self.break_time = self.timer_configs[config]["break"] * 60
        self.long_break_time = self.timer_configs[config]["long_break"] * 60
        self.cycles = self.timer_configs[config]["cycles"]
        self.current_time = self.work_time
        self.update_timer_display()
        self.reset_timer()

    def save_settings(self):
        try:
            work = int(self.work_entry.get())
            break_time = int(self.break_entry.get())
            long_break = int(self.long_break_entry.get())
            cycles = int(self.cycles_entry.get())
            target_hours = float(self.target_entry.get())
            
            if all(0 < x <= 120 for x in [work, break_time, long_break]) and 0 < cycles <= 10 and 0 < target_hours <= 24:
                self.timer_configs["Custom"] = {
                    "work": work,
                    "break": break_time,
                    "long_break": long_break,
                    "cycles": cycles
                }
                self.target_hours = target_hours
                self.config_var.set("Custom")
                self.change_config("Custom")
                
                # Save target hours to database
                cursor = self.conn.cursor()
                cursor.execute("UPDATE settings SET target_hours = ? WHERE id = 1", (target_hours,))
                self.conn.commit()
                
                self.update_progress()
                messagebox.showinfo("Success", "Settings saved! 🎉")
            else:
                messagebox.showerror("Error", "Timers: 1-120 min\nCycles: 1-10\nTarget: 1-24 hr")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_button.config(state="disabled")
            self.floating_start_button.config(state="disabled")
            self.main_stop_button.config(state="normal")
            self.floating_pause_button.config(text="⏸")
            self.start_timestamp = time.time()
            self.update_status_indicator()
            
            # Update status label color based on timer type
            if self.is_work:
                self.main_status_label.config(foreground=self.colors["work"])
            else:
                if self.cycle_count < self.cycles - 1:
                    self.main_status_label.config(foreground=self.colors["break"])
                else:
                    self.main_status_label.config(foreground=self.colors["long_break"])
            
            self.update_timer()

    def stop_timer(self):
        self.is_running = False
        self.is_paused = False
        self.start_button.config(state="normal")
        self.floating_start_button.config(state="normal")
        self.main_stop_button.config(state="disabled")
        self.floating_pause_button.config(text="⏸")
        self.start_timestamp = None
        self.update_status_indicator()

    def toggle_pause(self):
        if not self.is_running:
            return
            
        if not self.is_paused:
            self.is_paused = True
            self.floating_pause_button.config(text="▶")
            self.start_timestamp = None
        else:
            self.is_paused = False
            self.floating_pause_button.config(text="⏸")
            self.start_timestamp = time.time()
            self.update_timer()
        self.update_status_indicator()

    def reset_timer(self):
        self.stop_timer()
        self.is_work = True
        self.current_time = self.work_time
        self.cycle_count = 0
        self.main_status_label.config(text="Work Time", foreground=self.colors["work"])
        self.update_timer_display()
        self.update_progress_bar()
        self.update_status_indicator()

    def update_timer(self):
        if self.is_running and not self.is_paused:
            elapsed = time.time() - self.start_timestamp
            self.current_time = max(0, self.current_time - int(elapsed))
            self.start_timestamp = time.time()
            
            if self.current_time > 0:
                self.update_timer_display()
                self.update_progress_bar()
                self.root.after(1000, self.update_timer)
            else:
                self.play_sound()
                if self.is_work:
                    self.session_count += 1
                    self.total_work_time += self.timer_configs[self.current_config]["work"]
                    self.save_session()
                    self.cycle_count += 1
                    
                    if self.cycle_count < self.cycles:
                        self.is_work = False
                        self.current_time = self.break_time
                        self.main_status_label.config(text="Break Time", foreground=self.colors["break"])
                    else:
                        self.is_work = False
                        self.current_time = self.long_break_time
                        self.main_status_label.config(text="Long Break", foreground=self.colors["long_break"])
                        self.cycle_count = 0
                else:
                    self.is_work = True
                    self.current_time = self.work_time
                    self.main_status_label.config(text="Work Time", foreground=self.colors["work"])
                
                self.start_timestamp = time.time()
                self.update_timer_display()
                self.update_progress_bar()
                self.update_stats()
                self.update_progress()
                self.update_status_indicator()
                self.root.after(1000, self.update_timer)

    def update_timer_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.main_timer_label.config(text=time_str)
        self.floating_timer_label.config(text=time_str)

    def update_progress_bar(self):
        if self.is_work:
            total_time = self.timer_configs[self.current_config]["work"] * 60
        else:
            if self.cycle_count < self.cycles - 1:
                total_time = self.timer_configs[self.current_config]["break"] * 60
            else:
                total_time = self.timer_configs[self.current_config]["long_break"] * 60
        
        progress = ((total_time - self.current_time) / total_time) * 100
        self.progress_bar["value"] = progress

    def play_sound(self):
        if WINDOWS:
            winsound.Beep(1000, 500)
        else:
            print("\a")

    def save_session(self):
        today = date.today().isoformat()
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sessions, work_time FROM sessions WHERE date = ?", (today,))
            result = cursor.fetchone()
            
            if result:
                sessions, work_time = result
                cursor.execute("UPDATE sessions SET sessions = ?, work_time = ? WHERE date = ?",
                             (sessions + 1, work_time + self.timer_configs[self.current_config]["work"], today))
            else:
                cursor.execute("INSERT INTO sessions (date, sessions, work_time) VALUES (?, ?, ?)",
                             (today, 1, self.timer_configs[self.current_config]["work"]))
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save session: {e}")

    def update_stats(self):
        today = date.today().isoformat()
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sessions, work_time FROM sessions WHERE date = ?", (today,))
            result = cursor.fetchone()
            
            sessions = result[0] if result else 0
            work_time = result[1] / 60 if result else 0
            target_percentage = (work_time / self.target_hours * 100) if self.target_hours > 0 else 0
            
            self.stats_label.config(
                text=f"Today's Sessions: {sessions} 🍅\n"
                     f"Today's Work: {work_time:.1f} hr\n"
                     f"Target: {self.target_hours} hr ({target_percentage:.1f}%)"
            )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update stats: {e}")

    def on_closing(self):
        try:
            self.conn.close()
        except:
            pass
            
        if self.floating_window:
            self.floating_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
