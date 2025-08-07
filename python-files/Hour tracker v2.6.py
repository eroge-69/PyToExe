import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import json
import os

# File to store data (will now be month-specific)
DATA_FILE_PREFIX = "hour_tracker_data_"
TXT_FILE_PREFIX = "hour_tracker_export_"

class HourTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hour Tracker")
        self.root.geometry("800x600")

        # List to store entries
        self.entries = []

        # Track the current month
        self.current_month = datetime.now()

        # Load saved data for the current month
        self.load_data()

        # Create and place widgets
        self.create_widgets()

        # Start checking the date field every second
        self.check_date_field()

        # Bind Enter key to the root window
        self.root.bind('<Return>', self.handle_enter_key)

    def create_widgets(self):
        # [Previous create_widgets implementation remains exactly the same...]
        # Frame for input fields
        input_frame = ctk.CTkFrame(self.root)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Time input
        ctk.CTkLabel(input_frame, text="Hours:").grid(row=0, column=0, padx=5, pady=5)
        self.hours_entry = ctk.CTkEntry(input_frame, width=50)
        self.hours_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Minutes:").grid(row=0, column=2, padx=5, pady=5)
        self.minutes_entry = ctk.CTkEntry(input_frame, width=50)
        self.minutes_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Seconds:").grid(row=0, column=4, padx=5, pady=5)
        self.seconds_entry = ctk.CTkEntry(input_frame, width=50)
        self.seconds_entry.grid(row=0, column=5, padx=5, pady=5)

        # Date input (auto-populate with current date)
        ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ctk.CTkEntry(input_frame)
        self.date_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Weekday input (auto-populate with current day)
        ctk.CTkLabel(input_frame, text="Weekday:").grid(row=2, column=0, padx=5, pady=5)
        self.weekday_entry = ctk.CTkEntry(input_frame)
        self.weekday_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        self.weekday_entry.insert(0, datetime.now().strftime("%A"))

        # Description input
        ctk.CTkLabel(input_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = ctk.CTkEntry(input_frame)
        self.description_entry.grid(row=3, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Add entry button
        add_button = ctk.CTkButton(input_frame, text="Add Entry", command=self.add_entry)
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Month navigation buttons
        month_nav_frame = ctk.CTkFrame(input_frame)
        month_nav_frame.grid(row=4, column=2, columnspan=4, pady=5)

        self.prev_month_button = ctk.CTkButton(month_nav_frame, text="<", width=30, command=self.prev_month)
        self.prev_month_button.pack(side="left", padx=5)

        self.month_label = ctk.CTkLabel(month_nav_frame, text=self.current_month.strftime("%B %Y"))
        self.month_label.pack(side="left", padx=5)

        self.next_month_button = ctk.CTkButton(month_nav_frame, text=">", width=30, command=self.next_month)
        self.next_month_button.pack(side="left", padx=5)

        # Edit entry button
        edit_button = ctk.CTkButton(input_frame, text="Edit Entry", command=self.edit_entry)
        edit_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Delete entry button
        delete_button = ctk.CTkButton(input_frame, text="Delete Entry", command=self.delete_entry)
        delete_button.grid(row=5, column=2, columnspan=2, pady=10)

        # Frame for displaying entries
        display_frame = ctk.CTkFrame(self.root)
        display_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.entries_text = ctk.CTkTextbox(display_frame, wrap="none")
        self.entries_text.pack(pady=10, padx=10, fill="both", expand=True)

        # Export button
        export_button = ctk.CTkButton(self.root, text="Export to TXT", command=self.export_to_txt)
        export_button.pack(pady=10)

        # Frame for totals
        totals_frame = ctk.CTkFrame(self.root)
        totals_frame.place(relx=0.75, rely=0.05, anchor="n")

        # Total days worked
        ctk.CTkLabel(totals_frame, text="Total Days Worked:").grid(row=0, column=0, padx=5, pady=5)
        self.total_days_label = ctk.CTkLabel(totals_frame, text="0")
        self.total_days_label.grid(row=0, column=1, padx=5, pady=5)

        # Total hours worked
        ctk.CTkLabel(totals_frame, text="Total Hours Worked:").grid(row=1, column=0, padx=5, pady=5)
        self.total_hours_label = ctk.CTkLabel(totals_frame, text="0h 0m 0s")
        self.total_hours_label.grid(row=1, column=1, padx=5, pady=5)

        # Update the display with loaded data
        self.update_entries_display()

    def handle_enter_key(self, event):
        """Handle Enter key press to navigate between fields or submit."""
        current_focus = self.root.focus_get()
        
        # If coming from any time field, always go to date field
        if current_focus in [self.hours_entry, self.minutes_entry, self.seconds_entry]:
            self.date_entry.focus_set()
            self.date_entry.icursor("end")  # Move cursor to end
            return  # Stop further processing
        
        # If all fields are complete, submit the entry
        if all([
            self.hours_entry.get().strip(),
            self.minutes_entry.get().strip(),
            self.seconds_entry.get().strip(),
            self.date_entry.get().strip(),
            self.description_entry.get().strip()
        ]):
            self.add_entry()
            return
        
        # Otherwise, find next empty field in order
        for entry in [self.hours_entry, self.minutes_entry, self.seconds_entry, 
                     self.date_entry, self.description_entry]:
            if not entry.get().strip():
                entry.focus_set()
                entry.icursor("end")
                break

    def prev_month(self):
        """Cycle to the previous month."""
        self.current_month = (self.current_month.replace(day=1) - timedelta(days=1)).replace(day=1)
        self.update_month()

    def next_month(self):
        """Cycle to the next month."""
        self.current_month = (self.current_month.replace(day=1) + timedelta(days=32)).replace(day=1)
        self.update_month()

    def update_month(self):
        """Update the month label and load data for the new month."""
        self.month_label.configure(text=self.current_month.strftime("%B %Y"))
        self.load_data()
        self.update_entries_display()

    def check_date_field(self):
        """Check the date field every second and update the weekday."""
        try:
            date_str = self.date_entry.get()
            if date_str:
                # Parse the date string into a datetime object
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                # Get the weekday and update the weekday entry field
                self.weekday_entry.delete(0, "end")
                self.weekday_entry.insert(0, date_obj.strftime("%A"))
        except ValueError:
            # If the date format is invalid, do nothing
            pass

        # Schedule this function to run again after 1000 milliseconds (1 second)
        self.root.after(1000, self.check_date_field)

    def add_entry(self):
        try:
            hours = int(self.hours_entry.get())
            minutes = int(self.minutes_entry.get())
            seconds = int(self.seconds_entry.get())
            date = self.date_entry.get()
            weekday = self.weekday_entry.get()
            description = self.description_entry.get()

            # Validate time inputs
            if hours < 0 or minutes < 0 or seconds < 0:
                self.show_error("Time values cannot be negative.")
                return

            # Store the entry
            entry = {
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "date": date,
                "weekday": weekday,
                "description": description
            }
            self.entries.append(entry)

            # Sort entries by date
            self.sort_entries_by_date()

            # Update the display and save data
            self.update_entries_display()
            self.save_data()
            self.clear_inputs()
        except ValueError:
            self.show_error("Invalid input. Please enter numeric values for time.")

    def edit_entry(self):
        try:
            # Get the selected entry index
            selected_index = self.entries_text.index("insert").split(".")[0]
            if selected_index:
                selected_index = int(selected_index) - 1
                if 0 <= selected_index < len(self.entries):
                    # Load the selected entry into the input fields
                    entry = self.entries[selected_index]
                    self.hours_entry.delete(0, "end")
                    self.hours_entry.insert(0, entry["hours"])
                    self.minutes_entry.delete(0, "end")
                    self.minutes_entry.insert(0, entry["minutes"])
                    self.seconds_entry.delete(0, "end")
                    self.seconds_entry.insert(0, entry["seconds"])
                    self.date_entry.delete(0, "end")
                    self.date_entry.insert(0, entry["date"])
                    self.weekday_entry.delete(0, "end")
                    self.weekday_entry.insert(0, entry["weekday"])
                    self.description_entry.delete(0, "end")
                    self.description_entry.insert(0, entry["description"])

                    # Remove the old entry
                    self.entries.pop(selected_index)

                    # Sort entries by date
                    self.sort_entries_by_date()

                    # Update the display and save data
                    self.update_entries_display()
                    self.save_data()
                else:
                    self.show_error("Invalid selection.")
            else:
                self.show_error("Please select an entry to edit.")
        except Exception as e:
            self.show_error(f"Error editing entry: {e}")

    def delete_entry(self):
        try:
            # Get the selected entry index
            selected_index = self.entries_text.index("insert").split(".")[0]
            if selected_index:
                selected_index = int(selected_index) - 1
                if 0 <= selected_index < len(self.entries):
                    # Remove the entry
                    self.entries.pop(selected_index)
                    # Update the display and save data
                    self.update_entries_display()
                    self.save_data()
                else:
                    self.show_error("Invalid selection.")
            else:
                self.show_error("Please select an entry to delete.")
        except Exception as e:
            self.show_error(f"Error deleting entry: {e}")

    def sort_entries_by_date(self):
        """Sort entries by date in ascending order."""
        self.entries.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))

    def update_entries_display(self):
        self.entries_text.delete("1.0", "end")
        for i, entry in enumerate(self.entries, 1):
            # Display entry in a horizontal line format
            entry_line = (
                f"{i}. Date: {entry['date']} | "
                f"Weekday: {entry['weekday']} | "
                f"Time: {entry['hours']}h {entry['minutes']}m {entry['seconds']}s | "
                f"Worked on: {entry['description']}\n"
            )
            self.entries_text.insert("end", entry_line)

        # Update totals
        self.update_totals()

    def update_totals(self):
        """Update the total days worked and total hours worked."""
        # Calculate total days worked
        unique_dates = set(entry["date"] for entry in self.entries)
        total_days = len(unique_dates)
        self.total_days_label.configure(text=str(total_days))

        # Calculate total hours worked
        total_seconds = sum(
            entry["hours"] * 3600 + entry["minutes"] * 60 + entry["seconds"]
            for entry in self.entries
        )
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.total_hours_label.configure(text=f"{hours}h {minutes}m {seconds}s")

    def clear_inputs(self):
        self.hours_entry.delete(0, "end")
        self.minutes_entry.delete(0, "end")
        self.seconds_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Reset to current date
        self.weekday_entry.delete(0, "end")
        self.weekday_entry.insert(0, datetime.now().strftime("%A"))  # Reset to current weekday
        self.description_entry.delete(0, "end")

    def export_to_txt(self):
        if not self.entries:
            self.show_error("No entries to export.")
            return

        filename = f"{TXT_FILE_PREFIX}{self.current_month.strftime('%Y-%m')}.txt"
        total_time = self.calculate_total_time()
        unique_dates = set(entry["date"] for entry in self.entries)
        total_days = len(unique_dates)

        with open(filename, "w") as file:
            file.write("--- Hour Tracker Entries ---\n")
            for entry in self.entries:
                file.write(
                    f"Date: {entry['date']} | "
                    f"Weekday: {entry['weekday']} | "
                    f"Time: {entry['hours']}h {entry['minutes']}m {entry['seconds']}s | "
                    f"Worked on: {entry['description']}\n"
                )
            file.write(f"\n--- Total Time ---\n")
            file.write(f"{total_time[0]}h {total_time[1]}m {total_time[2]}s\n")
            file.write(f"Total Days Worked: {total_days}\n")

        self.show_info(f"Data exported to {filename}")

    def calculate_total_time(self):
        total_seconds = 0
        for entry in self.entries:
            total_seconds += entry["hours"] * 3600 + entry["minutes"] * 60 + entry["seconds"]
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return hours, minutes, seconds

    def save_data(self):
        """Save entries to a JSON file for the current month."""
        filename = f"{DATA_FILE_PREFIX}{self.current_month.strftime('%Y-%m')}.json"
        try:
            with open(filename, "w") as file:
                json.dump(self.entries, file, indent=4)
        except Exception as e:
            self.show_error(f"Error saving data: {e}")

    def load_data(self):
        """Load entries from a JSON file for the current month."""
        filename = f"{DATA_FILE_PREFIX}{self.current_month.strftime('%Y-%m')}.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r") as file:
                    self.entries = json.load(file)
                    # Sort entries by date when loading
                    self.sort_entries_by_date()
            except Exception as e:
                self.show_error(f"Error loading data: {e}")
        else:
            self.entries = []  # Reset entries if the file doesn't exist

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

# Run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = HourTrackerApp(root)
    root.mainloop()
