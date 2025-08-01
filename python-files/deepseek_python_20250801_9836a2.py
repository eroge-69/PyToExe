import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime, date, timedelta
import os
import sys
from tkcalendar import Calendar
from dateutil.relativedelta import relativedelta
import calendar

class LibraryTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Tracker System")
        self.root.geometry("1200x700")
        
        # Set current date by default
        self.current_date = date.today()
        
        # Create database file if it doesn't exist
        self.db_file = "library_records.csv"
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
        
        # Create name-roll mapping dictionary
        self.name_roll_mapping = {}
        self.load_name_roll_mapping()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load records
        self.load_records()
    
    def load_name_roll_mapping(self):
        """Load existing roll no and name pairs from database"""
        try:
            with open(self.db_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:  # Ensure row has roll no and name
                        self.name_roll_mapping[row[0]] = row[1]
        except FileNotFoundError:
            pass
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (Input form)
        left_panel = ttk.Frame(main_frame, padding="10", width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Calendar
        ttk.Label(left_panel, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.calendar = Calendar(left_panel, selectmode='day', year=self.current_date.year, 
                               month=self.current_date.month, day=self.current_date.day)
        self.calendar.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Roll No
        ttk.Label(left_panel, text="Roll No:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.roll_no_entry = ttk.Entry(left_panel)
        self.roll_no_entry.grid(row=2, column=1, pady=5, padx=5)
        self.roll_no_entry.bind("<FocusOut>", self.auto_fill_name)
        self.roll_no_entry.bind("<Return>", self.auto_fill_name)
        
        # Name
        ttk.Label(left_panel, text="Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(left_panel)
        self.name_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Book Title
        ttk.Label(left_panel, text="Book Title:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.book_entry = ttk.Entry(left_panel)
        self.book_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Status
        ttk.Label(left_panel, text="Status:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar()
        self.status_combobox = ttk.Combobox(left_panel, textvariable=self.status_var, 
                                          values=["Checked Out", "Returned"])
        self.status_combobox.grid(row=5, column=1, pady=5, padx=5)
        self.status_combobox.current(0)
        
        # Time In/Out
        ttk.Label(left_panel, text="Time In:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.time_in_entry = ttk.Entry(left_panel)
        self.time_in_entry.grid(row=6, column=1, pady=5, padx=5)
        
        ttk.Label(left_panel, text="Time Out:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.time_out_entry = ttk.Entry(left_panel)
        self.time_out_entry.grid(row=7, column=1, pady=5, padx=5)
        self.time_out_entry.insert(0, "")
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Record", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Record", command=self.update_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Record", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        # Right panel (Records display)
        right_panel = ttk.Frame(main_frame, padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Treeview for records
        self.tree = ttk.Treeview(right_panel, columns=("Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"), 
                                show="headings", height=25)
        
        # Define columns
        self.tree.heading("Roll No", text="Roll No")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time In", text="Time In")
        self.tree.heading("Time Out", text="Time Out")
        self.tree.heading("Book Title", text="Book Title")
        self.tree.heading("Status", text="Status")
        
        # Set column widths
        self.tree.column("Roll No", width=80)
        self.tree.column("Name", width=120)
        self.tree.column("Date", width=100)
        self.tree.column("Time In", width=80)
        self.tree.column("Time Out", width=80)
        self.tree.column("Book Title", width=150)
        self.tree.column("Status", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind treeview selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Search frame
        search_frame = ttk.Frame(right_panel)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_records)
        
        # Export buttons frame
        export_frame = ttk.Frame(right_panel)
        export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(export_frame, text="Export All to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export Date-wise", command=self.export_date_wise).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export Month-wise", command=self.export_month_wise).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export Year-wise", command=self.export_year_wise).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
    
    def auto_fill_name(self, event=None):
        """Automatically fill name and time-in when roll number is entered"""
        roll_no = self.roll_no_entry.get()
        
        # Set current time in Time In field
        current_time = datetime.now().strftime("%H:%M")
        self.time_in_entry.delete(0, tk.END)
        self.time_in_entry.insert(0, current_time)
        
        # If roll no exists in mapping, fill the name
        if roll_no in self.name_roll_mapping:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.name_roll_mapping[roll_no])
    
    def load_records(self):
        # Clear existing records
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load records from CSV
        try:
            with open(self.db_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 7:  # Ensure row has all required fields
                        self.tree.insert("", tk.END, values=row)
        except FileNotFoundError:
            messagebox.showerror("Error", "Database file not found!")
    
    def add_record(self):
        # Get values from form
        roll_no = self.roll_no_entry.get()
        name = self.name_entry.get()
        selected_date = self.calendar.get_date()
        time_in = self.time_in_entry.get()
        time_out = self.time_out_entry.get()
        book_title = self.book_entry.get()
        status = self.status_var.get()
        
        # Validate inputs
        if not roll_no or not name or not book_title:
            messagebox.showerror("Error", "Please fill in all required fields!")
            return
        
        # Add to name-roll mapping if not exists
        if roll_no not in self.name_roll_mapping:
            self.name_roll_mapping[roll_no] = name
        
        # Add to treeview
        self.tree.insert("", tk.END, values=(roll_no, name, selected_date, time_in, time_out, book_title, status))
        
        # Save to CSV
        self.save_to_csv()
        
        # Clear fields
        self.clear_fields()
        
        messagebox.showinfo("Success", "Record added successfully!")
    
    def update_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to update!")
            return
        
        # Get values from form
        roll_no = self.roll_no_entry.get()
        name = self.name_entry.get()
        selected_date = self.calendar.get_date()
        time_in = self.time_in_entry.get()
        time_out = self.time_out_entry.get()
        book_title = self.book_entry.get()
        status = self.status_var.get()
        
        # Validate inputs
        if not roll_no or not name or not book_title:
            messagebox.showerror("Error", "Please fill in all required fields!")
            return
        
        # Update name-roll mapping
        self.name_roll_mapping[roll_no] = name
        
        # Update treeview
        self.tree.item(selected_item, values=(roll_no, name, selected_date, time_in, time_out, book_title, status))
        
        # Save to CSV
        self.save_to_csv()
        
        messagebox.showinfo("Success", "Record updated successfully!")
    
    def delete_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to delete!")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            self.tree.delete(selected_item)
            
            # Save to CSV
            self.save_to_csv()
            
            # Clear fields
            self.clear_fields()
    
    def clear_fields(self):
        self.roll_no_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.book_entry.delete(0, tk.END)
        self.time_in_entry.delete(0, tk.END)
        self.time_out_entry.delete(0, tk.END)
        self.status_combobox.current(0)
    
    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            if values:
                self.roll_no_entry.delete(0, tk.END)
                self.roll_no_entry.insert(0, values[0])
                
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, values[1])
                
                # Parse and set calendar date
                try:
                    date_obj = datetime.strptime(values[2], "%m/%d/%y").date()
                    self.calendar.selection_set(date_obj)
                except:
                    pass
                
                self.time_in_entry.delete(0, tk.END)
                self.time_in_entry.insert(0, values[3])
                
                self.time_out_entry.delete(0, tk.END)
                if len(values) > 4:
                    self.time_out_entry.insert(0, values[4])
                
                self.book_entry.delete(0, tk.END)
                if len(values) > 5:
                    self.book_entry.insert(0, values[5])
                
                if len(values) > 6:
                    self.status_var.set(values[6])
    
    def save_to_csv(self):
        try:
            with open(self.db_file, 'w', newline='') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
                
                # Write all records from treeview
                for child in self.tree.get_children():
                    writer.writerow(self.tree.item(child)['values'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save records: {str(e)}")
    
    def search_records(self, event=None):
        search_term = self.search_var.get().lower()
        
        for child in self.tree.get_children():
            values = [str(v).lower() for v in self.tree.item(child)['values']]
            if any(search_term in value for value in values):
                self.tree.selection_add(child)
                self.tree.see(child)
            else:
                self.tree.selection_remove(child)
    
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                               filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    # Write header
                    writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
                    
                    # Get all records sorted by Date, Roll No, Name, Time In, Time Out
                    records = []
                    for child in self.tree.get_children():
                        records.append(self.tree.item(child)['values'])
                    
                    # Sort records
                    records.sort(key=lambda x: (
                        datetime.strptime(x[2], "%m/%d/%y").date(),  # Date
                        x[0],  # Roll No
                        x[1],  # Name
                        x[3],  # Time In
                        x[4] if x[4] else ""  # Time Out
                    ))
                    
                    # Write sorted records
                    for record in records:
                        writer.writerow(record)
                
                messagebox.showinfo("Success", f"All records exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export records: {str(e)}")
    
    def export_date_wise(self):
        # Create date selection dialog
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("Select Date Range")
        date_dialog.geometry("400x300")
        
        ttk.Label(date_dialog, text="Start Date:").pack(pady=5)
        start_cal = Calendar(date_dialog, selectmode='day', 
                            year=self.current_date.year, 
                            month=self.current_date.month, 
                            day=self.current_date.day)
        start_cal.pack(pady=5)
        
        ttk.Label(date_dialog, text="End Date:").pack(pady=5)
        end_cal = Calendar(date_dialog, selectmode='day', 
                          year=self.current_date.year, 
                          month=self.current_date.month, 
                          day=self.current_date.day)
        end_cal.pack(pady=5)
        
        def perform_export():
            start_date = datetime.strptime(start_cal.get_date(), "%m/%d/%y").date()
            end_date = datetime.strptime(end_cal.get_date(), "%m/%d/%y").date()
            
            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date!")
                return
            
            # Calculate 10 years ago from today
            ten_years_ago = self.current_date - relativedelta(years=10)
            if start_date < ten_years_ago:
                messagebox.showerror("Error", "Records only available for the past 10 years!")
                return
            
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                   filetypes=[("CSV Files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        # Write header
                        writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
                        
                        # Get matching records
                        records = []
                        for child in self.tree.get_children():
                            record = self.tree.item(child)['values']
                            record_date = datetime.strptime(record[2], "%m/%d/%y").date()
                            if start_date <= record_date <= end_date:
                                records.append(record)
                        
                        # Sort records
                        records.sort(key=lambda x: (
                            datetime.strptime(x[2], "%m/%d/%y").date(),  # Date
                            x[0],  # Roll No
                            x[1],  # Name
                            x[3],  # Time In
                            x[4] if x[4] else ""  # Time Out
                        ))
                        
                        # Write sorted records
                        for record in records:
                            writer.writerow(record)
                    
                    messagebox.showinfo("Success", f"Date-wise records exported to {file_path}")
                    date_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export records: {str(e)}")
        
        ttk.Button(date_dialog, text="Export", command=perform_export).pack(pady=10)
    
    def export_month_wise(self):
        # Create month selection dialog
        month_dialog = tk.Toplevel(self.root)
        month_dialog.title("Select Month")
        month_dialog.geometry("300x200")
        
        ttk.Label(month_dialog, text="Select Month:").pack(pady=5)
        
        # Month selection
        month_var = tk.StringVar()
        month_combobox = ttk.Combobox(month_dialog, textvariable=month_var, 
                                     values=[calendar.month_name[i] for i in range(1, 13)])
        month_combobox.pack(pady=5)
        month_combobox.current(self.current_date.month - 1)
        
        # Year selection
        year_var = tk.StringVar()
        year_combobox = ttk.Combobox(month_dialog, textvariable=year_var, 
                                    values=[str(self.current_date.year - i) for i in range(10)])
        year_combobox.pack(pady=5)
        year_combobox.current(0)
        
        def perform_export():
            month_name = month_var.get()
            year = int(year_var.get())
            
            try:
                month_num = list(calendar.month_name).index(month_name)
            except ValueError:
                messagebox.showerror("Error", "Invalid month selected!")
                return
            
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                   filetypes=[("CSV Files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        # Write header
                        writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
                        
                        # Get matching records
                        records = []
                        for child in self.tree.get_children():
                            record = self.tree.item(child)['values']
                            record_date = datetime.strptime(record[2], "%m/%d/%y").date()
                            if record_date.year == year and record_date.month == month_num:
                                records.append(record)
                        
                        # Sort records
                        records.sort(key=lambda x: (
                            datetime.strptime(x[2], "%m/%d/%y").date(),  # Date
                            x[0],  # Roll No
                            x[1],  # Name
                            x[3],  # Time In
                            x[4] if x[4] else ""  # Time Out
                        ))
                        
                        # Write sorted records
                        for record in records:
                            writer.writerow(record)
                    
                    messagebox.showinfo("Success", f"Month-wise records exported to {file_path}")
                    month_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export records: {str(e)}")
        
        ttk.Button(month_dialog, text="Export", command=perform_export).pack(pady=10)
    
    def export_year_wise(self):
        # Create year selection dialog
        year_dialog = tk.Toplevel(self.root)
        year_dialog.title("Select Year")
        year_dialog.geometry("300x150")
        
        ttk.Label(year_dialog, text="Select Year:").pack(pady=5)
        
        # Year selection
        year_var = tk.StringVar()
        year_combobox = ttk.Combobox(year_dialog, textvariable=year_var, 
                                    values=[str(self.current_date.year - i) for i in range(10)])
        year_combobox.pack(pady=5)
        year_combobox.current(0)
        
        def perform_export():
            year = int(year_var.get())
            
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                   filetypes=[("CSV Files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        # Write header
                        writer.writerow(["Roll No", "Name", "Date", "Time In", "Time Out", "Book Title", "Status"])
                        
                        # Get matching records
                        records = []
                        for child in self.tree.get_children():
                            record = self.tree.item(child)['values']
                            record_date = datetime.strptime(record[2], "%m/%d/%y").date()
                            if record_date.year == year:
                                records.append(record)
                        
                        # Sort records
                        records.sort(key=lambda x: (
                            datetime.strptime(x[2], "%m/%d/%y").date(),  # Date
                            x[0],  # Roll No
                            x[1],  # Name
                            x[3],  # Time In
                            x[4] if x[4] else ""  # Time Out
                        ))
                        
                        # Write sorted records
                        for record in records:
                            writer.writerow(record)
                    
                    messagebox.showinfo("Success", f"Year-wise records exported to {file_path}")
                    year_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export records: {str(e)}")
        
        ttk.Button(year_dialog, text="Export", command=perform_export).pack(pady=10)
    
    def generate_report(self):
        # Count checked out vs returned books
        checked_out = 0
        returned = 0
        
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            if len(values) > 6 and values[6] == "Returned":
                returned += 1
            else:
                checked_out += 1
        
        # Create report content
        report_content = f"""Library Usage Report
========================
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Total Records: {len(self.tree.get_children())}
Books Checked Out: {checked_out}
Books Returned: {returned}

Recent Activities:
"""
        # Add last 5 records
        children = self.tree.get_children()
        for child in children[-5:][::-1]:  # Show last 5 in reverse order (newest first)
            values = self.tree.item(child)['values']
            report_content += f"- {values[1]} ({values[0]}) - {values[5]} ({values[6]}) on {values[2]}\n"
        
        # Ask where to save the report
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                               filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(report_content)
                messagebox.showinfo("Success", f"Report generated at {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryTrackerApp(root)
    root.mainloop()