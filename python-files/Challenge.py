"""
90-Day Progress Tracker Application
A desktop application for tracking 90-day progress milestones with persistent data storage
Author: Claude
Date: September 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time
from pathlib import Path
import calendar


class DateTimeSelector:
    def __init__(self, parent, title="Select Start Date & Time", initial_datetime=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300 // 2)
        self.dialog.geometry(f"400x400+{x}+{y}")

        if initial_datetime is None:
            initial_datetime = datetime.now()

        self.create_widgets(initial_datetime)

    def create_widgets(self, initial_dt):
        """Create date and time selection widgets"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Select Start Date & Time",
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))

        # Date selection frame
        date_frame = tk.LabelFrame(main_frame, text="Date", font=('Arial', 10, 'bold'))
        date_frame.pack(fill=tk.X, pady=(0, 10))

        date_inner = tk.Frame(date_frame)
        date_inner.pack(padx=10, pady=10)

        # Month
        tk.Label(date_inner, text="Month:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.month_var = tk.StringVar(value=str(initial_dt.month))
        month_combo = ttk.Combobox(date_inner, textvariable=self.month_var, width=12, state='readonly')
        month_combo['values'] = [f"{i} - {calendar.month_name[i]}" for i in range(1, 13)]
        month_combo.set(f"{initial_dt.month} - {calendar.month_name[initial_dt.month]}")
        month_combo.grid(row=0, column=1, padx=5)
        month_combo.bind('<<ComboboxSelected>>', self.on_date_change)

        # Day
        tk.Label(date_inner, text="Day:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.day_var = tk.StringVar(value=str(initial_dt.day))
        self.day_combo = ttk.Combobox(date_inner, textvariable=self.day_var, width=12, state='readonly')
        self.day_combo.grid(row=1, column=1, padx=5, pady=(5, 0))

        # Year
        tk.Label(date_inner, text="Year:").grid(row=2, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.year_var = tk.StringVar(value=str(initial_dt.year))
        year_combo = ttk.Combobox(date_inner, textvariable=self.year_var, width=12, state='readonly')
        current_year = datetime.now().year
        year_combo['values'] = [str(year) for year in range(current_year - 5, current_year + 6)]
        year_combo.set(str(initial_dt.year))
        year_combo.grid(row=2, column=1, padx=5, pady=(5, 0))
        year_combo.bind('<<ComboboxSelected>>', self.on_date_change)

        # Time selection frame
        time_frame = tk.LabelFrame(main_frame, text="Time", font=('Arial', 10, 'bold'))
        time_frame.pack(fill=tk.X, pady=(0, 10))

        time_inner = tk.Frame(time_frame)
        time_inner.pack(padx=10, pady=10)

        # Hour
        tk.Label(time_inner, text="Hour:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.hour_var = tk.StringVar(value=f"{initial_dt.hour:02d}")
        hour_combo = ttk.Combobox(time_inner, textvariable=self.hour_var, width=8, state='readonly')
        hour_combo['values'] = [f"{i:02d}" for i in range(24)]
        hour_combo.set(f"{initial_dt.hour:02d}")
        hour_combo.grid(row=0, column=1, padx=5)

        # Minute
        tk.Label(time_inner, text="Minute:").grid(row=0, column=2, sticky='w', padx=(15, 5))
        self.minute_var = tk.StringVar(value=f"{initial_dt.minute:02d}")
        minute_combo = ttk.Combobox(time_inner, textvariable=self.minute_var, width=8, state='readonly')
        minute_combo['values'] = [f"{i:02d}" for i in range(60)]
        minute_combo.set(f"{initial_dt.minute:02d}")
        minute_combo.grid(row=0, column=3, padx=5)

        # Second
        tk.Label(time_inner, text="Second:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.second_var = tk.StringVar(value=f"{initial_dt.second:02d}")
        second_combo = ttk.Combobox(time_inner, textvariable=self.second_var, width=8, state='readonly')
        second_combo['values'] = [f"{i:02d}" for i in range(60)]
        second_combo.set(f"{initial_dt.second:02d}")
        second_combo.grid(row=1, column=1, padx=5, pady=(5, 0))

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        # Now button
        now_btn = tk.Button(button_frame, text="Use Current Time",
                           command=self.set_current_time, bg='#17a2b8', fg='white',
                           font=('Arial', 10), padx=15, pady=5)
        now_btn.pack(side=tk.LEFT, padx=5)

        # OK button
        ok_btn = tk.Button(button_frame, text="OK", command=self.on_ok,
                          bg='#28a745', fg='white', font=('Arial', 10), padx=20, pady=5)
        ok_btn.pack(side=tk.LEFT, padx=5)

        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.on_cancel,
                              bg='#6c757d', fg='white', font=('Arial', 10), padx=15, pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        self.dialog.resizable(True, True)
        # Initialize day combo
        self.on_date_change(None)

        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_date_change(self, event):
        """Update day combo when month or year changes"""
        try:
            month = int(self.month_var.get().split(' - ')[0])
            year = int(self.year_var.get())

            # Get number of days in the selected month
            _, days_in_month = calendar.monthrange(year, month)

            # Update day combo values
            self.day_combo['values'] = [str(i) for i in range(1, days_in_month + 1)]

            # Ensure current day is valid
            current_day = int(self.day_var.get()) if self.day_var.get().isdigit() else 1
            if current_day > days_in_month:
                current_day = days_in_month

            self.day_var.set(str(current_day))

        except (ValueError, IndexError):
            pass

    def set_current_time(self):
        """Set all fields to current date and time"""
        now = datetime.now()

        # Set date
        self.month_var.set(f"{now.month} - {calendar.month_name[now.month]}")
        self.year_var.set(str(now.year))
        self.on_date_change(None)  # Update days
        self.day_var.set(str(now.day))

        # Set time
        self.hour_var.set(f"{now.hour:02d}")
        self.minute_var.set(f"{now.minute:02d}")
        self.second_var.set(f"{now.second:02d}")

    def on_ok(self):
        """Handle OK button"""
        try:
            month = int(self.month_var.get().split(' - ')[0])
            day = int(self.day_var.get())
            year = int(self.year_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())

            self.result = datetime(year, month, day, hour, minute, second)
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Date/Time",
                               "Please check your date and time values.\n\n" + str(e))

    def on_cancel(self):
        """Handle Cancel button"""
        self.result = None
        self.dialog.destroy()


class ProgressTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("90 Day Without Fap")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Configure colors
        self.colors = {
            'bg': '#ffffff',
            'completed': '#90EE90',
            'uncompleted': '#f0f0f0',
            'text': '#333333',
            'header': '#2c3e50',
            'progress_bg': '#e0e0e0',
            'progress_fill': '#dc3545',
            'border': '#cccccc'
        }

        self.root.configure(bg=self.colors['bg'])

        # Data file path
        self.data_file = Path.home() / '.90day_tracker_data.json'

        # Initialize data
        self.completed_days = set()
        self.start_date = datetime(2025, 9, 12, 5, 0, 0)  # Default start date

        # Load saved data
        self.load_data()

        # Create UI
        self.create_widgets()

        # Start progress update thread
        self.update_progress_thread()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Create all UI elements"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="90 DAY WITHOUT FAP",
            font=('Arial', 20, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['header']
        )
        title_label.pack(pady=(0, 20))

        # Calendar frame with border
        calendar_container = tk.Frame(
            main_frame,
            bg=self.colors['border'],
            relief=tk.SOLID,
            borderwidth=2
        )
        calendar_container.pack(fill=tk.BOTH, expand=True)

        # Calendar grid
        self.calendar_frame = tk.Frame(calendar_container, bg=self.colors['bg'])
        self.calendar_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)

        self.day_buttons = {}
        self.create_calendar_grid()

        # Progress section
        progress_container = tk.Frame(main_frame, bg=self.colors['bg'])
        progress_container.pack(fill=tk.X, pady=(20, 0))

        # Progress label
        self.progress_label = tk.Label(
            progress_container,
            text="CHALLENGE PROGRESS: 0.00%",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['header']
        )
        self.progress_label.pack(pady=(0, 10))

        # Progress bar frame
        progress_bar_frame = tk.Frame(
            progress_container,
            bg=self.colors['border'],
            relief=tk.SOLID,
            borderwidth=2,
            height=40
        )
        progress_bar_frame.pack(fill=tk.X, padx=20)
        progress_bar_frame.pack_propagate(False)

        # Progress bar background
        self.progress_bg = tk.Frame(
            progress_bar_frame,
            bg=self.colors['progress_bg'],
            height=36
        )
        self.progress_bg.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Progress bar fill
        self.progress_fill = tk.Frame(
            self.progress_bg,
            bg=self.colors['progress_fill'],
            height=32
        )
        self.progress_fill.place(x=0, y=0, relheight=1, width=0)

        # Control buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=(20, 0))

        # Set Start Date button
        set_date_btn = tk.Button(
            button_frame,
            text="Set Start Date/Time",
            command=self.set_start_date,
            font=('Arial', 10),
            padx=15,
            pady=8,
            bg='#28a745',
            fg='white',
            relief=tk.RAISED,
            cursor='hand2'
        )
        set_date_btn.pack(side=tk.LEFT, padx=5)

        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text="Reset Challenge",
            command=self.reset_challenge,
            font=('Arial', 10),
            padx=20,
            pady=8,
            bg='#6c757d',
            fg='white',
            relief=tk.RAISED,
            cursor='hand2'
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Info button
        info_btn = tk.Button(
            button_frame,
            text="Info",
            command=self.show_info,
            font=('Arial', 10),
            padx=20,
            pady=8,
            bg='#17a2b8',
            fg='white',
            relief=tk.RAISED,
            cursor='hand2'
        )
        info_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(
            main_frame,
            text=f"Started: {self.start_date.strftime('%B %d, %Y at %I:%M:%S %p')}",
            font=('Arial', 9),
            bg=self.colors['bg'],
            fg='#666666'
        )
        self.status_label.pack(pady=(10, 0))

    def create_calendar_grid(self):
        """Create the 90-day calendar grid"""
        # Clear existing buttons
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        day_number = 1
        for row in range(9):  # 9 rows
            for col in range(10):  # 10 columns
                if day_number <= 90:
                    # Create day button
                    is_completed = day_number in self.completed_days

                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day_number),
                        width=5,
                        height=2,
                        font=('Arial', 10),
                        bg=self.colors['completed'] if is_completed else self.colors['uncompleted'],
                        relief=tk.SOLID,
                        borderwidth=1,
                        cursor='hand2',
                        command=lambda d=day_number: self.toggle_day(d)
                    )
                    btn.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
                    self.day_buttons[day_number] = btn

                    # Configure grid weights
                    self.calendar_frame.grid_columnconfigure(col, weight=1)

                    day_number += 1

            self.calendar_frame.grid_rowconfigure(row, weight=1)

    def toggle_day(self, day):
        """Toggle the completion status of a day"""
        if day in self.completed_days:
            self.completed_days.remove(day)
            self.day_buttons[day].configure(bg=self.colors['uncompleted'])
        else:
            self.completed_days.add(day)
            self.day_buttons[day].configure(bg=self.colors['completed'])

        self.save_data()

    def calculate_progress(self):
        """Calculate current progress based on elapsed time"""
        now = datetime.now()
        elapsed = now - self.start_date

        # Total hours in 90 days
        total_hours = 90 * 24  # 2160 hours

        # Elapsed hours
        elapsed_hours = elapsed.total_seconds() / 3600

        # Calculate percentage
        if elapsed_hours >= total_hours:
            progress = 100.0
        elif elapsed_hours < 0:
            progress = 0.0
        else:
            progress = (elapsed_hours / total_hours) * 100

        return min(100.0, max(0.0, progress))

    def update_progress(self):
        """Update progress display"""
        progress = self.calculate_progress()

        # Update progress label
        self.progress_label.config(text=f"CHALLENGE PROGRESS: {progress:.2f}%")

        # Update progress bar
        self.progress_bg.update_idletasks()
        bar_width = int(self.progress_bg.winfo_width() * (progress / 100))
        self.progress_fill.place(width=bar_width)

    def update_progress_thread(self):
        """Continuously update progress in background"""

        def update():
            while True:
                try:
                    self.root.after(0, self.update_progress)
                    time.sleep(60)  # Update every minute
                except:
                    break

        thread = threading.Thread(target=update, daemon=True)
        thread.start()

    def set_start_date(self):
        """Open date/time selector to set custom start date"""
        selector = DateTimeSelector(self.root, "Set Challenge Start Date & Time", self.start_date)
        self.root.wait_window(selector.dialog)

        if selector.result:
            # Ask for confirmation if this will clear existing progress
            if self.completed_days:
                confirm = messagebox.askyesno(
                    "Change Start Date",
                    "Changing the start date will clear all current progress.\n\n"
                    "Do you want to continue?"
                )
                if not confirm:
                    return

            # Clear completed days since we're changing the start date
            self.completed_days.clear()

            # Set new start date
            self.start_date = selector.result
            self.save_data()

            # Recreate calendar grid
            self.create_calendar_grid()

            # Update status label
            self.status_label.config(
                text=f"Started: {self.start_date.strftime('%B %d, %Y at %I:%M:%S %p')}"
            )

            # Update progress
            self.update_progress()

            messagebox.showinfo(
                "Start Date Updated",
                f"Challenge start date set to:\n{self.start_date.strftime('%B %d, %Y at %I:%M:%S %p')}"
            )

    def reset_challenge(self):
        """Reset the challenge with new start date"""
        result = messagebox.askyesno(
            "Reset Challenge",
            "Are you sure you want to reset the 90-day challenge?\n\n"
            "This will clear all progress and start a new 90-day period from now."
        )

        if result:
            self.completed_days.clear()
            self.start_date = datetime.now()
            self.save_data()

            # Recreate calendar grid
            self.create_calendar_grid()

            # Update status label
            self.status_label.config(
                text=f"Started: {self.start_date.strftime('%B %d, %Y at %I:%M:%S %p')}"
            )

            # Update progress
            self.update_progress()

            messagebox.showinfo(
                "Challenge Reset",
                "Your 90-day challenge has been reset!\n\n"
                "Good luck on your journey!"
            )

    def show_info(self):
        """Show application information"""
        end_date = self.start_date + timedelta(days=90)
        days_elapsed = (datetime.now() - self.start_date).days
        days_remaining = max(0, 90 - days_elapsed)

        info_text = (
            "90-Day Progress Tracker\n\n"
            f"Start Date: {self.start_date.strftime('%B %d, %Y at %I:%M:%S %p')}\n"
            f"End Date: {end_date.strftime('%B %d, %Y at %I:%M:%S %p')}\n\n"
            f"Days Elapsed: {min(90, days_elapsed)}\n"
            f"Days Remaining: {days_remaining}\n"
            f"Days Completed: {len(self.completed_days)}\n\n"
            "Click on any day to mark it as completed.\n"
            "Use 'Set Start Date/Time' to customize when your challenge began.\n"
            "Your progress is automatically saved."
        )

        messagebox.showinfo("Challenge Information", info_text)

    def save_data(self):
        """Save data to local file"""
        data = {
            'completed_days': list(self.completed_days),
            'start_date': self.start_date.isoformat()
        }

        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Load data from local file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.completed_days = set(data.get('completed_days', []))
                    self.start_date = datetime.fromisoformat(data.get('start_date', self.start_date.isoformat()))
            except Exception as e:
                print(f"Error loading data: {e}")
                # Use defaults if loading fails
                self.completed_days = set()
                self.start_date = datetime(2025, 9, 12, 5, 0, 0)

    def on_closing(self):
        """Handle window closing"""
        self.save_data()
        self.root.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ProgressTracker(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()

"""
SETUP INSTRUCTIONS FOR CREATING EXECUTABLE:

1. Install required packages:
   pip install pyinstaller

2. Create the executable:
   pyinstaller --onefile --windowed --name "90DayTracker" --icon=icon.ico progress_tracker.py

   (Note: --windowed prevents console window, --icon is optional if you have an icon file)

3. The executable will be created in the 'dist' folder

4. Data is stored in the user's home directory as '.90day_tracker_data.json'

NEW FEATURES ADDED:
- Custom date/time selector dialog with intuitive controls
- "Set Start Date/Time" button to manually choose challenge start
- Dropdown menus for month (with names), day, year, hour, minute, and second
- "Use Current Time" button for quick current datetime selection
- Automatic day validation based on selected month and year
- Enhanced status display showing seconds in start time
- Confirmation dialog when changing start date (clears existing progress)
- Smart day range updates when month or year changes (handles leap years)

EXISTING FEATURES:
- 90-day calendar grid with clickable days
- Real-time progress calculation based on elapsed time
- Persistent data storage that survives app restarts
- Reset functionality to start a new 90-day period
- Visual progress bar with percentage display
- Clean, minimalist interface matching the design requirements
- Automatic progress updates every minute
- Thread-safe operation for continuous updates

USAGE:
- Click "Set Start Date/Time" to manually choose when your challenge begins
- Click any day to mark it as completed (turns green)
- Click again to unmark (returns to gray)
- Progress percentage is calculated based on time elapsed since start date
- Use "Reset Challenge" to start a new 90-day period from current time
- Use "Info" to see detailed challenge information
- All data is automatically saved
"""