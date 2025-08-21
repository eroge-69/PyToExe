import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
from tkinter import filedialog
import os
import threading
import time

# Install required packages: pip install tkcalendar sqlalchemy pyodbc pandas openpyxl
try:
    from tkcalendar import DateEntry
except ImportError:
    print("Please install tkcalendar: pip install tkcalendar")
    exit()

try:
    from sqlalchemy import create_engine
except ImportError:
    print("Please install sqlalchemy: pip install sqlalchemy")
    exit()

class TestRunExporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Run Summary Exporter")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self.export_thread = None
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Test Run Summary Exporter", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Date picker frame
        date_frame = ttk.LabelFrame(main_frame, text="Select Date", padding="10")
        date_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Date entry (using DateEntry widget)
        ttk.Label(date_frame, text="Choose Date:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Calendar widget
        self.calendar = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.calendar.grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        # Bind date selection event
        self.calendar.bind('<<DateSelected>>', self.on_date_selected)
        
        # Export button
        self.export_button = ttk.Button(main_frame, text="Export to Excel", 
                                       command=self.start_export_thread, state=tk.DISABLED)
        self.export_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", font=('Arial', 9))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        self.progress.grid_remove()  # Hide initially
        
        # Update button state initially
        self.update_button_state()
        
    def on_date_selected(self, event=None):
        """Update button state when date is selected"""
        self.update_button_state()
        
    def update_button_state(self):
        """Enable/disable export button based on date selection"""
        if self.calendar.get_date():
            self.export_button.config(state=tk.NORMAL)
            self.status_label.config(text="")
        else:
            self.export_button.config(state=tk.DISABLED)
            self.status_label.config(text="Please select a date")
            
    def start_export_thread(self):
        """Start export operation in a separate thread"""
        self.export_button.config(state=tk.DISABLED)
        self.calendar.config(state=tk.DISABLED)
        self.status_label.config(text="Starting export...")
        self.progress.grid()  # Show progress bar
        self.progress.start()
        
        # Start export in separate thread
        self.export_thread = threading.Thread(target=self.export_to_excel)
        self.export_thread.daemon = True  # Dies when main thread dies
        self.export_thread.start()
        
        # Check thread periodically
        self.check_export_thread()
        
    def check_export_thread(self):
        """Check if export thread is still running"""
        if self.export_thread.is_alive():
            self.root.after(100, self.check_export_thread)  # Check again in 100ms
        else:
            # Thread finished
            self.progress.stop()
            self.progress.grid_remove()  # Hide progress bar
            self.export_button.config(state=tk.NORMAL)
            self.calendar.config(state=tk.NORMAL)
            
    def export_to_excel(self):
        """Export data to Excel file (runs in separate thread)"""
        try:
            # Get selected date
            selected_date = self.calendar.get_date()
            date_str = selected_date.strftime('%Y-%m-%d')
            
            # Show save file dialog (must be in main thread)
            self.root.after(0, lambda: self.status_label.config(text="Selecting file..."))
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel File",
                initialfile=f"TestRunSummary_{date_str}.xlsx"
            )
            
            if not filename:  # User cancelled
                self.root.after(0, lambda: self.status_label.config(text="Export cancelled"))
                return
                
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Connecting to database..."))
            time.sleep(0.1)  # Small delay to allow UI update
            
            # Create SQLAlchemy engine
            connection_string = (
                "mssql+pyodbc://sa:sa@SERVER_HP/DONA_DATA"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )
            engine = create_engine(connection_string)
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Executing stored procedure..."))
            time.sleep(0.1)  # Small delay to allow UI update
            
            # Execute stored procedure
            query = f"EXEC GetTestRunSummaryByDate '{date_str}'"
            df = pd.read_sql(query, engine)
            
            # Close connection
            engine.dispose()
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Saving to Excel..."))
            time.sleep(0.1)  # Small delay to allow UI update
            
            # Export to Excel with borders
            from openpyxl.styles import Border, Side, Alignment
            from openpyxl.utils import get_column_letter
            
            # Define border style
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Define alignment for centering
            center_alignment = Alignment(horizontal='center', vertical='center')
            
            # Export to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='TestRunSummary', index=False)
                
                # Get worksheet
                worksheet = writer.sheets['TestRunSummary']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column_letter].width = min(adjusted_width, 50)
                
                # Add borders to all cells and center alignment
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = center_alignment
                        
                # Make header row bold
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    
                # Make total row bold
                if len(df) > 0:
                    total_row = len(df) + 1
                    for cell in worksheet[total_row]:
                        cell.font = cell.font.copy(bold=True)
                        cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Success message
            self.root.after(0, lambda: self.status_label.config(text="Export completed successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Data exported successfully to:\n{filename}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Export failed"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))

def main():
    root = tk.Tk()
    app = TestRunExporter(root)
    root.mainloop()

if __name__ == "__main__":
    main()