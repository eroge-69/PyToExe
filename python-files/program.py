import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
import pandas as pd
from datetime import date

class CalibrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibration Schedule")
        self.root.geometry("600x600") # Increased height for better text area view

        self.today = date.today()

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.load_button = ttk.Button(
            self.main_frame,
            text="Load Excel File",
            command=self.load_file
        )
        self.load_button.pack(pady=(0, 15), fill='x')

        self.cal = Calendar(
            self.main_frame,
            selectmode='day',
            date_pattern='dd/mm/yyyy',
            weekendbackground='white',
            weekendforeground='black',
            year=self.today.year,
            month=self.today.month,
            day=self.today.day
        )
        self.cal.pack(pady=10, fill="x")

        self.cal.calevent_create(self.today, 'Today', 'today_tag')
        self.cal.tag_config('today_tag', background='lightblue')

        # --- NEW: Frame for Text Area and Scrollbar ---
        details_frame = ttk.Frame(self.main_frame)
        details_frame.pack(pady=10, fill='both', expand=True)

        # --- NEW: Scrollbar ---
        scrollbar = ttk.Scrollbar(details_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- NEW: Text widget instead of Label ---
        self.details_area = tk.Text(
            details_frame,
            wrap='word', # Wraps long lines at word boundaries
            font=("Helvetica", 10),
            yscrollcommand=scrollbar.set, # Link scrollbar to text area
            borderwidth=0,
            highlightthickness=0
        )
        self.details_area.pack(expand=True, fill='both')
        
        # Link text area to scrollbar
        scrollbar.config(command=self.details_area.yview)
        
        self.update_details_text("Please load an Excel file to begin.")

        self.events = {}
        self.cal.bind("<<CalendarSelected>>", self.show_details)

    def update_details_text(self, text_content):
        """Helper function to update the read-only Text widget."""
        self.details_area.config(state='normal')  # Enable writing
        self.details_area.delete('1.0', tk.END)    # Clear existing text
        self.details_area.insert(tk.END, text_content) # Insert new text
        self.details_area.config(state='disabled') # Disable writing (makes it read-only)

    def load_file(self):
        """Opens a file dialog to select an Excel file and loads the data."""
        filepath = filedialog.askopenfilename(
            title="Select a Calibration File",
            filetypes=(("Excel Files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if not filepath:
            return

        self.cal.calevent_remove('cal_due')
        self.events = self.process_data(filepath)

        if self.events is not None:
            self.highlight_events()
            messagebox.showinfo("Success", f"Successfully loaded {len(self.events)} unique event dates.")
            
            self.cal.selection_set(self.today)
            self.show_details(None)

    def process_data(self, filepath):
        """Loads data from the given Excel file path."""
        try:
            df = pd.read_excel(filepath)
            
            required_cols = ['Chamber', 'SN', 'Next Calib']
            if not all(col in df.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df.columns]
                messagebox.showerror("Error", f"Excel is missing columns: {', '.join(missing_cols)}")
                return None

            df['Next Calib'] = pd.to_datetime(df['Next Calib'], dayfirst=True)
            events = {}
            for index, row in df.iterrows():
                cal_date = row['Next Calib'].date()
                if cal_date not in events:
                    events[cal_date] = []
                
                details = f"Chamber: {row['Chamber']} (SN: {row['SN']})"
                events[cal_date].append(details)
            return events

        except Exception as e:
            messagebox.showerror("Error Reading File", f"An error occurred: \n\n{e}")
            return None

    def highlight_events(self):
        """Adds a visual marker to dates with a scheduled calibration."""
        for event_date in self.events.keys():
            self.cal.calevent_create(event_date, 'Calibration Due', 'cal_due')
        self.cal.tag_config('cal_due', background='red', foreground='white')

    def show_due_soon_details(self):
        """Calculates and displays all items due in the next 30 days."""
        due_soon_items = []
        for event_date, details_list in sorted(self.events.items()):
            delta = event_date - self.today
            if 0 <= delta.days <= 30:
                for item_detail in details_list:
                    remaining = delta.days
                    day_str = "day" if remaining == 1 else "days"
                    due_soon_items.append(f"{item_detail} - {remaining} {day_str} remaining")
        
        if due_soon_items:
            details_text = f"Items due in the next 30 days (from {self.today.strftime('%d-%b-%Y')}):\n\n"
            details_text += "\n".join(due_soon_items)
        else:
            details_text = "No items are due for calibration in the next 30 days."
        
        self.update_details_text(details_text)

    def show_details(self, event):
        """Router function to show details based on the selected date."""
        if not self.events:
            return

        selected_date = self.cal.selection_get()

        if selected_date == self.today:
            self.show_due_soon_details()
        else:
            if selected_date in self.events:
                details_text = f"Items due on {selected_date.strftime('%d-%b-%Y')}:\n\n"
                details_text += "\n".join(self.events[selected_date])
                self.update_details_text(details_text)
            else:
                self.update_details_text("No calibrations scheduled for this date.")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = CalibrationApp(app_root)
    app_root.mainloop()