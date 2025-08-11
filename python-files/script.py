import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime, timedelta
import pandas as pd
import os
import openpyxl
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import uuid
import re

# Excel import functionality

def import_excel_data(excel_path, employee_name, date_range):
    """Import hours data from Excel file"""
    imported_data = []
    try:
        df = pd.read_excel(excel_path)
        
        # Parse the timesheet format
        imported_data = parse_timesheet_format(df, employee_name, date_range)
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import Excel data: {e}")
    
    return imported_data

def import_excel_data(excel_path, employee_name, date_range):
    """Import hours data from Excel file"""
    imported_data = []
    try:
        # Use openpyxl to read with formula evaluation
        wb = openpyxl.load_workbook(excel_path, data_only=True)  # data_only=True evaluates formulas
        
        # Get the sheet for this employee
        if employee_name in wb.sheetnames:
            ws = wb[employee_name]
            
            # Convert worksheet to DataFrame with evaluated formulas
            data = []
            for row in ws.iter_rows(values_only=True):
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Check if the Excel file has the expected CSV format
            if len(df.columns) >= 5 and any('Employee Name' in str(cell) for cell in df.iloc[0] if pd.notna(cell)):
                # Excel file has CSV-like format
                for _, row in df.iterrows():
                    # Validate required fields
                    if pd.isna(row['Date']) or pd.isna(row['Job Number']) or pd.isna(row['Hour Code']) or pd.isna(row['Hours']):
                        continue
                    
                    # Validate date is in range
                    date = str(row['Date']).split()[0]  # Get just the date part
                    if date not in date_range:
                        continue
                    
                    # Validate hour code
                    if row['Hour Code'] not in hour_codes:
                        continue
                    
                    # Validate hours
                    try:
                        hours = float(row['Hours'])
                        if hours <= 0:
                            continue
                    except:
                        continue
                    
                    # Determine night shift
                    night_shift = False
                    if 'Night Shift' in df.columns:
                        night_shift = str(row.get('Night Shift', 'False')).lower() in ['true', '1', 'yes']
                    
                    imported_data.append({
                        'Employee Name': employee_name,
                        'Date': date,
                        'Job Number': str(row['Job Number']),
                        'Hour Code': row['Hour Code'],
                        'Hours': hours,
                        'Night Shift': night_shift
                    })
            else:
                # Try to parse the timesheet format
                imported_data = parse_timesheet_format(df, employee_name, date_range)
        else:
            print(f"Sheet '{employee_name}' not found in workbook")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import Excel data: {e}")
    
    return imported_data

def parse_timesheet_format(df, employee_name, date_range):
    """Parse the timesheet format from Excel file"""
    imported_data = []
    
    try:
        # Find the date row - check multiple possible locations for updated template
        dates = []
        date_row_candidates = [7, 8, 9]  # Row 8 (index 7) for updated multi-employee template, Row 9 (index 8), Row 10 (index 9) for legacy templates
        
        for date_row_idx in date_row_candidates:
            if date_row_idx < len(df):
                for j in range(len(df.columns)):
                    date_value = df.iloc[date_row_idx, j]
                    if pd.notna(date_value):
                        # Handle both direct date strings and Excel formulas
                        date_str = str(date_value)
                        # If it's a formula, try to extract the date part
                        if date_str.startswith('='):
                            # For Excel formulas like =TEXT('Data Selection'!$B$3 + 0, "yyyy-mm-dd")
                            # We need to look for actual date values in the data
                            # For now, let's try to parse the date from the formula or look for actual dates
                            try:
                                # Try to extract date from formula or use the cell value
                                if 'yyyy-mm-dd' in date_str:
                                    # This is a formula, we need to look for the actual calculated value
                                    # Let's check if there are any date-like strings in the row
                                    continue
                            except:
                                pass
                        else:
                            # Direct date string
                            date_str = date_str.split()[0]
                            if date_str in date_range:
                                dates.append((j, date_str))
                
                if dates:  # Found dates, use this row
                    print(f"Found dates in row {date_row_idx + 1}: {[d[1] for d in dates]}")
                    break
        
        if not dates:
            # Try to find dates by looking for date-like patterns in the expected date row
            print("No dates found in expected rows, trying alternative approach...")
            for date_row_idx in date_row_candidates:
                if date_row_idx < len(df):
                    # Look for date columns (E-T, columns 4-19) in the expected date row
                    for j in range(4, 20):  # Columns E-T (indices 4-19)
                        if j < len(df.columns):
                            cell_value = df.iloc[date_row_idx, j]
                            if pd.notna(cell_value):
                                cell_str = str(cell_value)
                                # Check if this looks like a date (contains dashes)
                                if '-' in cell_str and len(cell_str) >= 8:
                                    # Extract the date part
                                    date_part = cell_str.split()[0]
                                    if date_part in date_range:
                                        dates.append((j, date_part))
                    
                    if dates:
                        print(f"Found dates in row {date_row_idx + 1}: {[d[1] for d in dates]}")
                        break
            
            if not dates:
                print("Still no dates found in expected rows")
                print(f"Available date range: {date_range}")
                print(f"DataFrame shape: {df.shape}")
                print(f"First few rows:")
                for i in range(min(10, len(df))):
                    print(f"Row {i}: {list(df.iloc[i, :5])}")
                    # Also show the date columns (E-T, columns 4-19)
                    if i >= 6:  # Only show for rows that might have dates
                        date_cols = list(df.iloc[i, 4:20])  # Columns E-T (indices 4-19)
                        print(f"  Date cols: {date_cols}")
                return imported_data
        
        # Determine the starting row for job data based on where dates were found
        if date_row_idx == 7:  # Updated multi-employee template format (row 8)
            job_start_offset = 1  # Jobs start at row 9 (index 8)
        elif date_row_idx == 8:  # Legacy multi-employee template format (row 9)
            job_start_offset = 1  # Jobs start at row 10 (index 9)
        else:  # Single template format (row 10)
            job_start_offset = 1  # Jobs start at row 11 (index 10)
        
        # Process jobs in 5-row increments
        # Each job has exactly 5 rows:
        # Row 1: Job name (e.g., M3446, M4100)
        # Row 2: 6100 hours
        # Row 3: 6220 hours
        # Row 4: 1210 hours
        # Row 5: Travel hours
        
        for job_start_row in range(date_row_idx + job_start_offset, len(df), 5):
            if job_start_row + 4 >= len(df):  # Need 5 rows total
                break
                
            # Get job name from column 1 (B column) in the first row of this job
            job_name_value = df.iloc[job_start_row, 1]  # Row job_start_row, Column 1 (B)
            if pd.notna(job_name_value):
                current_job = str(job_name_value)
                
                # Skip summary rows that contain "Subtotal", "Project #", or other non-job entries
                if ("Subtotal" in current_job or not current_job.strip() or 
                    current_job == "Task/Project Detail" or current_job == "Project #"):
                    continue
                    
                print(f"Found job: {current_job}")
                
                # Process the 4 hour code rows that follow this job
                hour_codes = ['6100', '6220', '1210', 'Travel']
                for i, hour_code in enumerate(hour_codes):
                    hour_row = job_start_row + 1 + i  # +1 because first row is job name
                    if hour_row >= len(df):
                        break
                        
                    print(f"Processing hour code: {hour_code} for job: {current_job}")
                    
                    # Look for hours in the date columns (now E-T, 16 columns)
                    for col_idx, date_str in dates:
                        value = df.iloc[hour_row, col_idx]
                        if pd.notna(value) and value != 0:
                            try:
                                hours = float(value)
                                if hours > 0:
                                    # Check for night shift indicator in column D
                                    night_shift = False
                                    night_shift_value = df.iloc[hour_row, 3]  # Column D (index 3)
                                    if pd.notna(night_shift_value):
                                        night_shift_str = str(night_shift_value).strip()
                                        if night_shift_str in ['X', 'x', '1', 'true', 'True', 'yes', 'Yes']:
                                            night_shift = True
                                    # Also check if there's an "x" in the Project # row for this job (updated template structure)
                                    elif hour_code != 'Travel':  # Only check for non-Travel codes
                                        # Look for "x" in the Project # row (job_start_row) for this job
                                        project_row_night_shift = df.iloc[job_start_row, 3]  # Column D in Project # row
                                        if pd.notna(project_row_night_shift):
                                            project_night_str = str(project_row_night_shift).strip()
                                            if project_night_str in ['X', 'x', '1', 'true', 'True', 'yes', 'Yes']:
                                                night_shift = True
                                    
                                    imported_data.append({
                                        'Employee Name': employee_name,
                                        'Date': date_str,
                                        'Job Number': current_job,
                                        'Hour Code': hour_code,
                                        'Hours': hours,
                                        'Night Shift': night_shift
                                    })
                                    print(f"Imported: {date_str}, {current_job}, {hour_code}, {hours}, Night: {night_shift}")
                            except ValueError:
                                # Skip non-numeric values
                                pass
    
    except Exception as e:
        print(f"Error parsing timesheet format: {e}")
    
    return imported_data

def populate_employee_data(emp, imported_data):
    """Populate the GUI with imported data"""
    data = employee_data[emp]
    
    # Group data by job number
    job_data = {}
    for entry in imported_data:
        job_num = entry['Job Number']
        if job_num not in job_data:
            job_data[job_num] = {}
        
        date = entry['Date']
        code = entry['Hour Code']
        hours = entry['Hours']
        night_shift = entry['Night Shift']
        
        if date not in job_data[job_num]:
            job_data[job_num][date] = {}
        
        job_data[job_num][date][code] = {
            'hours': hours,
            'night_shift': night_shift
        }
    
    # Clear existing data
    reset_employee_data(emp)
    
    # Add job sections as needed
    num_jobs_needed = len(job_data)
    while len(data['job_entries']) < num_jobs_needed:
        add_job(emp)
    
    # Populate data for each job
    for i, (job_num, job_info) in enumerate(job_data.items()):
        if i < len(data['job_entries']):
            # Set job number
            job_entry = data['job_entries'][i]
            job_entry.delete(0, tk.END)
            job_entry.insert(0, job_num)
            update_job_name(emp, i)
            
            # Populate hours for this job
            for date, date_info in job_info.items():
                for code, code_info in date_info.items():
                    entry_key = (f"job{i+1}", date, code)
                    if entry_key in data['entries']:
                        entry = data['entries'][entry_key]
                        entry.delete(0, tk.END)
                        entry.insert(0, str(code_info['hours']))
                        
                        # Set night shift checkbox
                        if code != 'Travel':
                            night_var = data['night_shift_vars'].get((f"job{i+1}", code))
                            if night_var:
                                night_var.set(code_info['night_shift'])
    
    # Recalculate totals
    calculate(emp)



def import_multi_employee_excel():
    """Import data from multi-employee Excel template"""
    # Create import dialog
    import_window = tk.Toplevel()
    import_window.title("Import Multi-Employee Excel")
    import_window.geometry("600x500")
    import_window.minsize(550, 450)  # Minimum size to ensure buttons are visible
    import_window.transient(root)
    import_window.grab_set()
    
    # Variables
    file_path = tk.StringVar()
    
    # GUI elements
    tk.Label(import_window, text="Import Multi-Employee Excel File", font=('Arial', 12, 'bold')).pack(pady=10)
    
    tk.Label(import_window, text="Select the multi-employee template file:", font=('Arial', 10)).pack(pady=5)
    
    file_frame = tk.Frame(import_window)
    file_frame.pack(fill="x", padx=20, pady=10)
    
    file_entry = tk.Entry(file_frame, textvariable=file_path, width=50)
    file_entry.pack(side="left", fill="x", expand=True)
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select Multi-Employee Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            file_path.set(filename)
    
    browse_btn = tk.Button(file_frame, text="Browse", command=browse_file)
    browse_btn.pack(side="right", padx=(5, 0))
    
    # Status text
    status_text = tk.Text(import_window, height=15, width=60, font=('Arial', 9))
    status_text.pack(pady=10, padx=20, fill="both", expand=True)
    
    def log_message(message):
        status_text.insert(tk.END, message + "\n")
        status_text.see(tk.END)
        import_window.update()
    
    def do_import():
        if not file_path.get():
            messagebox.showerror("Error", "Please select a file")
            return
        
        if not os.path.exists(file_path.get()):
            messagebox.showerror("Error", "File does not exist")
            return
        
        try:
            log_message("Starting import process...")
            
            # Load the workbook
            wb = openpyxl.load_workbook(file_path.get())
            log_message(f"Found {len(wb.sheetnames)} sheets in file")
            
            imported_count = 0
            total_entries = 0
            
            # Process each sheet (employee)
            for sheet_name in wb.sheetnames:
                if sheet_name in employees:
                    emp = sheet_name
                    log_message(f"\nProcessing employee: {emp}")
                    
                    try:
                        # Read the sheet with openpyxl to evaluate formulas
                        wb = openpyxl.load_workbook(file_path.get(), data_only=True)
                        
                        if emp in wb.sheetnames:
                            ws = wb[emp]
                            
                            # Convert worksheet to DataFrame with evaluated formulas
                            data = []
                            for row in ws.iter_rows(values_only=True):
                                data.append(row)
                            
                            df = pd.DataFrame(data)
                            
                            # Get date range for this employee
                            data = employee_data[emp]
                            date_range = data['dates']
                            
                            if not date_range:
                                log_message(f"  Warning: No date range set for {emp}")
                                continue
                            
                            # Import data for this employee
                            log_message(f"  Date range for {emp}: {list(date_range)[:5]}...")  # Show first 5 dates
                            imported_data = parse_timesheet_format(df, emp, date_range)
                        else:
                            log_message(f"  Sheet '{emp}' not found in workbook")
                            continue
                        
                        if imported_data:
                            # Populate the GUI with imported data
                            populate_employee_data(emp, imported_data)
                            log_message(f"  Successfully imported {len(imported_data)} entries")
                            imported_count += 1
                            total_entries += len(imported_data)
                        else:
                            log_message(f"  No data found for {emp}")
                            log_message(f"  Available columns: {list(df.columns)}")
                            log_message(f"  DataFrame shape: {df.shape}")
                    
                    except Exception as e:
                        log_message(f"  Error processing {emp}: {e}")
                
                else:
                    log_message(f"Skipping sheet '{sheet_name}' (not a recognized employee)")
            
            log_message(f"\nImport completed!")
            log_message(f"Processed {imported_count} employees")
            log_message(f"Total entries imported: {total_entries}")
            
            if imported_count > 0:
                messagebox.showinfo("Success", f"Import completed!\nProcessed {imported_count} employees\nTotal entries: {total_entries}")
            else:
                messagebox.showwarning("Warning", "No data was imported. Check the file format and employee names.")
            
            import_window.destroy()
        
        except Exception as e:
            log_message(f"Error during import: {e}")
            messagebox.showerror("Error", f"Import failed: {e}")
    
    # Bottom button frame with grid layout for better control
    bottom_frame = tk.Frame(import_window, height=80)
    bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)
    bottom_frame.pack_propagate(False)  # Maintain frame height
    
    # Center the buttons horizontally
    button_container = tk.Frame(bottom_frame)
    button_container.pack(expand=True)
    
    # Style configuration for buttons
    button_style = {
        'font': ('Arial', 12, 'bold'),
        'width': 12,
        'height': 2,
        'relief': 'raised',
        'bd': 2,
        'cursor': 'hand2'
    }
    
    # Import button with styling
    import_btn = tk.Button(button_container, text="Import", command=do_import, 
                          bg="#4CAF50", fg="white", activebackground="#45a049", **button_style)
    import_btn.pack(side="left", padx=20)
    
    # Cancel button with styling  
    cancel_btn = tk.Button(button_container, text="Cancel", command=import_window.destroy,
                          bg="#f44336", fg="white", activebackground="#da190b", **button_style)
    cancel_btn.pack(side="left", padx=20)

# Define global variables
# Load employee names and rates from CSV file
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'rates.csv')
    rates_df = pd.read_csv(csv_path)
    employees = rates_df['Employee Name'].tolist()
    rates = dict(zip(rates_df['Employee Name'], rates_df['Hourly Rate']))
except FileNotFoundError:
    messagebox.showerror("Error", "rates.csv file not found in the script directory")
    employees = []
    rates = {}
except Exception as e:
    messagebox.showerror("Error", f"Failed to load rates.csv: {e}")
    employees = []
    rates = {}

# Load job numbers and names from CSV file
try:
    csv_path = os.path.join(script_dir, 'jobs.csv')
    job_df = pd.read_csv(csv_path)
    job_name_map = dict(zip(job_df['JOB NUMBER'], job_df['JOB NAME']))
except FileNotFoundError:
    messagebox.showerror("Error", "jobs.csv file not found in the script directory")
    job_name_map = {}
except Exception as e:
    messagebox.showerror("Error", f"Failed to load jobs.csv: {e}")
    job_name_map = {}

hour_codes = ['6100', '6220', '1210', 'Travel']
employee_data = {emp: {
    'dates': [], 'job_rows': {}, 'entries': {}, 'col_total_labels': {}, 'code_total_labels': {}, 'grand_total_label': None,
    'totals_row': 0, 'job_entries': [], 'job_name_labels': [], 'table_frame': None, 'totals_frame': None,
    'rt_day_hours_label': None, 'ot_day_hours_label': None, 'dt_day_hours_label': None, 'rt_night_hours_label': None,
    'ot_night_hours_label': None, 'dt_night_hours_label': None, 'rt_amount_label': None, 'ot_amount_label': None,
    'gross_label': None, 'job_count': 0, 'daily_totals_label': None, 'add_button': None, 'night_shift_vars': {},
    'hour_entries_grid': [], 'rate_label': None, 'row_total_labels': [], 'vacation_pay_entry': None, 'vacation_pay_label': None,
    'vacation_pay': 0.0, 'travel_hours_label': None, 'travel_amount_label': None
} for emp in employees}

# Create main root window and hide it
root = tk.Tk()
root.withdraw()

# Create date range prompt window
prompt_root = tk.Tk()
prompt_root.title("Select Pay Period")
prompt_root.geometry("300x100")
prompt_root.grid_rowconfigure(0, weight=1)
prompt_root.grid_columnconfigure(0, weight=1)

# Semi-monthly date ranges for 2024-2025
semi_monthly_ranges = [
    ('2024-12-26', '2025-01-10'), ('2025-01-11', '2025-01-25'), ('2025-01-26', '2025-02-10'), ('2025-02-11', '2025-02-25'),
    ('2025-02-26', '2025-03-10'), ('2025-03-11', '2025-03-25'), ('2025-03-26', '2025-04-10'), ('2025-04-11', '2025-04-25'),
    ('2025-04-26', '2025-05-10'), ('2025-05-11', '2025-05-25'), ('2025-05-26', '2025-06-10'), ('2025-06-11', '2025-06-25'),
    ('2025-06-26', '2025-07-10'), ('2025-07-11', '2025-07-25'), ('2025-07-26', '2025-08-10'), ('2025-08-11', '2025-08-25'),
    ('2025-08-26', '2025-09-10'), ('2025-09-11', '2025-09-25'), ('2025-09-26', '2025-10-10'), ('2025-10-11', '2025-10-25'),
    ('2025-10-26', '2025-11-10'), ('2025-11-11', '2025-11-25'), ('2025-11-26', '2025-12-10'), ('2025-12-16', '2025-12-25'),
    ('2025-12-26', '2026-01-10')
]

# Set up date range selection
period_var = tk.StringVar(value="")
tk.Label(prompt_root, text="Select Pay Period:", font=('Arial', 8)).grid(row=0, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
period_dropdown = ttk.Combobox(prompt_root, textvariable=period_var, values=[f"{start} to {end}" for start, end in semi_monthly_ranges], state="readonly", font=('Arial', 8))
period_dropdown.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)

# Bind Combobox selection to ensure period_var updates
def on_select(event):
    period_var.set(period_dropdown.get())

period_dropdown.bind('<<ComboboxSelected>>', on_select)

def confirm_period():
    selected_period = period_var.get()
    if not selected_period or selected_period not in [f"{start} to {end}" for start, end in semi_monthly_ranges]:
        messagebox.showerror("Error", "Please select a valid pay period")
        return
    try:
        start_date, end_date = selected_period.split(" to ")
        dates = [(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(n)).strftime('%Y-%m-%d') for n in range((datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1)]
        for emp in employees:
            employee_data[emp]['dates'] = dates
            employee_data[emp]['job_count'] = 3
        prompt_root.destroy()
        root.deiconify()
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date range: {e}")

tk.Button(prompt_root, text="Confirm", font=('Arial', 8), command=confirm_period).grid(row=2, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
prompt_root.wait_window()

# Main GUI setup
root.title("Timesheet GUI")
root.geometry("1200x800")
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create menubar
menubar = tk.Menu(root)
root.config(menu=menubar)
edit_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Reset All", command=lambda: [reset_employee_data(emp) for emp in employees])
edit_menu.add_command(label="Import Multi-Employee Excel", command=lambda: import_multi_employee_excel())
edit_menu.add_command(label="Print to PDF", command=lambda: print_to_pdf())

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")

# Configure tab style for larger, uniform tabs
style = ttk.Style()
style.configure("TNotebook.Tab", font=('Arial', 10), padding=[10, 5])

def get_weeks(dates):
    weeks = {}
    for date_str in dates:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        sunday = (date - timedelta(days=(date.weekday() + 1) % 7)).strftime('%Y-%m-%d')
        weeks.setdefault(sunday, []).append(date_str)
    return weeks

def update_job_name(emp, row_idx):
    data = employee_data[emp]
    data['job_name_labels'][row_idx].config(text=job_name_map.get(data['job_entries'][row_idx].get().strip(), ""))

def reset_employee_data(emp):
    data = employee_data[emp]
    for entry in data['job_entries'] + list(data['entries'].values()):
        entry.delete(0, tk.END)
        entry.insert(0, "")
    if data['vacation_pay_entry']:
        data['vacation_pay_entry'].delete(0, tk.END)
        data['vacation_pay_entry'].insert(0, "")
    for var in data['night_shift_vars'].values():
        var.set(False)
    for label in list(data['code_total_labels'].values()) + list(data['col_total_labels'].values()) + [
        data['rt_day_hours_label'], data['ot_day_hours_label'], data['dt_day_hours_label'],
        data['rt_night_hours_label'], data['ot_night_hours_label'], data['dt_night_hours_label'],
        data['rt_amount_label'], data['ot_amount_label'], data['gross_label'], data['vacation_pay_label'], data['travel_hours_label'], data['travel_amount_label']
    ] + data['row_total_labels']:
        if label:
            label.config(text="0" if label not in [data['rt_amount_label'], data['ot_amount_label'], data['gross_label'], data['vacation_pay_label'], data['travel_amount_label']] else "$0")
    data['vacation_pay'] = 0.0
    set_date_range(emp)
    setup_job_navigation(emp)
    update_layout(emp)

def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

def add_vacation_pay(emp, silent=False):
    data = employee_data[emp]
    try:
        vacation_pay = safe_float(data['vacation_pay_entry'].get())
        data['vacation_pay'] = round(vacation_pay, 2)
        data['vacation_pay_label'].config(text=f"${data['vacation_pay']:.2f}")
    except ValueError:
        if not silent:
            messagebox.showerror("Error", "Please enter a valid number for vacation pay")
        data['vacation_pay'] = 0.0
        data['vacation_pay_label'].config(text="$0.00")
    calculate(emp)

def add_totals_row(emp):
    data = employee_data[emp]
    if data['daily_totals_label']:
        data['daily_totals_label'].destroy()
    for l in data['col_total_labels'].values():
        l.destroy()
    if data['grand_total_label']:
        data['grand_total_label'].destroy()

    totals_row = max(data['job_rows'].values(), default=1) + 5
    data['daily_totals_label'] = tk.Label(data['table_frame'], text="Daily Totals", font=('Arial', 8), anchor="center")
    data['daily_totals_label'].grid(row=totals_row, column=0, columnspan=4 + len(data['dates']), sticky="nsew", padx=3, pady=3)

    data['col_total_labels'] = {}
    for i, d in enumerate(data['dates']):
        l = tk.Label(data['table_frame'], text="0", font=('Arial', 8), anchor="center")
        l.grid(row=totals_row, column=4 + i, sticky="nsew", padx=3, pady=3)
        data['col_total_labels'][d] = l

    data['grand_total_label'] = tk.Label(data['table_frame'], text="0", font=('Arial', 8), anchor="center")
    data['grand_total_label'].grid(row=totals_row, column=4 + len(data['dates']), sticky="nsew", padx=3, pady=3)

def add_job(emp):
    data = employee_data[emp]
    data['job_count'] += 1
    job_num = f"job{data['job_count']}"
    base_row = max(data['job_rows'].values(), default=1) + 5

    job_frame = tk.Frame(data['table_frame'], borderwidth=1, relief="solid")
    job_frame.grid(row=base_row, column=0, columnspan=4 + len(data['dates']), rowspan=5, sticky="nsew", padx=3, pady=3)
    for j in range(4 + len(data['dates'])):
        job_frame.grid_columnconfigure(j, weight=1, uniform="cols", minsize=80)

    for col, text in enumerate(["Job Number", "Hour Code", "Night Shift", "Job Name"]):
        tk.Label(job_frame, text=text, font=('Arial', 8), anchor="center").grid(row=0, column=col, sticky="nsew", padx=3, pady=3)

    job_entry = tk.Entry(job_frame, width=5, font=('Arial', 8), justify='center')
    job_entry.grid(row=2, column=0, sticky="nsew", padx=3, pady=3)
    job_entry.bind("<KeyRelease>", lambda event, e=emp, r=data['job_count'] - 1: update_job_name(e, r))
    data['job_entries'].append(job_entry)

    job_name_label = tk.Label(job_frame, text="", font=('Arial', 8), anchor="center", wraplength=80, justify="center")
    job_name_label.grid(row=1, column=3, rowspan=4, sticky="nsew", padx=3, pady=3)
    data['job_name_labels'].append(job_name_label)

    for j, code in enumerate(hour_codes):
        row = j + 1
        tk.Label(job_frame, text=code, font=('Arial', 8), anchor="center").grid(row=row, column=1, sticky="nsew", padx=3, pady=3)
        if code != 'Travel':
            var = tk.BooleanVar()
            tk.Checkbutton(job_frame, variable=var).grid(row=row, column=2, sticky="nsew", padx=3, pady=3)
            data['night_shift_vars'][(job_num, code)] = var
            var.trace("w", lambda *args, e=emp: calculate(e))
        else:
            tk.Label(job_frame, text="", font=('Arial', 8), anchor="center").grid(row=row, column=2, sticky="nsew", padx=3, pady=3)
        date_entries = []
        for k, d in enumerate(data['dates']):
            hour_entry = tk.Entry(job_frame, width=5, font=('Arial', 8), justify='center')
            hour_entry.grid(row=row, column=4 + k, sticky="nsew", padx=3, pady=3)
            hour_entry.bind("<KeyRelease>", lambda event, e=emp: calculate(e))
            data['entries'][(job_num, d, code)] = hour_entry
            date_entries.append(hour_entry)
        data['hour_entries_grid'].append(date_entries)
        total_label = tk.Label(data['table_frame'], text="0", font=('Arial', 8), anchor="center")
        total_label.grid(row=base_row + row, column=4 + len(data['dates']), sticky="nsew", padx=3, pady=3)
        data['row_total_labels'].append(total_label)
    data['job_rows'][job_num] = base_row
    add_totals_row(emp)
    setup_job_navigation(emp)
    update_layout(emp)

def update_layout(emp):
    data = employee_data[emp]
    data['table_frame'].master.configure(scrollregion=data['table_frame'].master.bbox("all"))
    setup_navigation(emp)

def setup_navigation(emp):
    data = employee_data[emp]
    grid = data['hour_entries_grid']
    if not grid:
        return
    num_rows, num_cols = len(grid), len(grid[0])
    entry_to_pos = {grid[r][c]: (r, c) for r in range(num_rows) for c in range(num_cols)}

    def navigate(event):
        widget = event.widget
        if widget not in entry_to_pos:
            return
        r, c = entry_to_pos[widget]
        if event.keysym == 'Up' and r > 0:
            grid[r-1][c].focus()
        elif (event.keysym == 'Down' or event.keysym == 'Return') and r < num_rows - 1:
            grid[r+1][c].focus()
        elif event.keysym == 'Left' and c > 0:
            grid[r][c-1].focus()
        elif event.keysym == 'Right' and c < num_cols - 1:
            grid[r][c+1].focus()

    for row in grid:
        for entry in row:
            for key in ('<Up>', '<Down>', '<Left>', '<Right>', '<Return>'):
                entry.bind(key, navigate)

def setup_job_navigation(emp):
    data = employee_data[emp]
    entries = data['job_entries']
    if not entries:
        return

    def navigate(event):
        widget = event.widget
        try:
            idx = entries.index(widget)
            if idx < len(entries) - 1:
                entries[idx + 1].focus()
        except ValueError:
            pass

    for entry in entries:
        entry.bind('<Return>', navigate)

def allocate_hours_to_jobs(job_hours, job_rt_hours, job_ot_hours, job_dt_hours, date, rt_day, rt_night, ot_day, ot_night, dt_day, dt_night, night_shift_vars, job_num_to_id):
    """Allocate hours to jobs for a specific day based on their actual hours worked, separating day and night"""
    # Get jobs that worked on this date, separating day and night hours
    jobs_with_day_hours = []
    jobs_with_night_hours = []
    
    for job_num, job_data in job_hours.items():
        day_hours = 0.0
        night_hours = 0.0
        
        for code in hour_codes:
            if code != 'Travel':
                code_hours = job_data[code][date]
                if code_hours > 0:
                    # Check if this job/code combination is night shift
                    is_night = False
                    job_id = job_num_to_id.get(job_num)
                    if job_id:
                        night_var = night_shift_vars.get((job_id, code))
                        if night_var and night_var.get():
                            is_night = True
                    
                    if is_night:
                        night_hours += code_hours
                    else:
                        day_hours += code_hours
        
        if day_hours > 0:
            jobs_with_day_hours.append((job_num, day_hours))
        if night_hours > 0:
            jobs_with_night_hours.append((job_num, night_hours))
    
    # Allocate day hours separately
    if jobs_with_day_hours and (rt_day > 0 or ot_day > 0 or dt_day > 0):
        # Allocate regular time for day hours
        remaining_rt_day = rt_day
        for job_num, day_hours_worked in jobs_with_day_hours:
            if remaining_rt_day <= 0:
                break
            rt_for_job = min(day_hours_worked, remaining_rt_day)
            remaining_rt_day -= rt_for_job
            
            # Distribute RT across hour codes for this job (day only)
            for code in hour_codes:
                if code != 'Travel' and rt_for_job > 0:
                    code_hours = job_hours[job_num][code][date]
                    if code_hours > 0:
                        rt_for_code = min(code_hours, rt_for_job)
                        job_rt_hours[job_num][code] += rt_for_code
                        rt_for_job -= rt_for_code
                        if rt_for_job <= 0:
                            break
        
        # Allocate overtime for day hours - only to jobs with remaining unallocated hours
        if ot_day > 0:
            if len(jobs_with_day_hours) > 1:
                # Calculate remaining unallocated hours for each job
                jobs_with_remaining_hours = []
                remaining_rt_check = rt_day
                
                # First pass: calculate how much RT each job got
                for job_num, day_hours_worked in jobs_with_day_hours:
                    rt_allocated = min(day_hours_worked, remaining_rt_check)
                    remaining_rt_check -= rt_allocated
                    remaining_hours = day_hours_worked - rt_allocated
                    if remaining_hours > 0:
                        jobs_with_remaining_hours.append((job_num, remaining_hours))
                
                # Sort by remaining hours (descending) for priority
                jobs_with_remaining_hours.sort(key=lambda x: x[1], reverse=True)
                remaining_ot_day = ot_day
                
                for job_num, remaining_hours in jobs_with_remaining_hours:
                    if remaining_ot_day <= 0:
                        break
                    ot_for_job = min(remaining_ot_day, remaining_hours)
                    remaining_ot_day -= ot_for_job
                    
                    # Distribute OT across hour codes for this job (day only)
                    for code in hour_codes:
                        if code != 'Travel' and ot_for_job > 0:
                            code_hours = job_hours[job_num][code][date]
                            if code_hours > 0:
                                ot_for_code = min(code_hours, ot_for_job)
                                job_ot_hours[job_num][code] += ot_for_code
                                ot_for_job -= ot_for_code
                                if ot_for_job <= 0:
                                    break
            else:
                # Single job days - allocate all overtime to the single job
                job_num = jobs_with_day_hours[0][0]
                job_ot_hours[job_num]['6220'] += ot_day
        
        # Allocate double time for day hours - only to jobs with remaining unallocated hours
        if dt_day > 0:
            if len(jobs_with_day_hours) > 1:
                # Calculate remaining unallocated hours for each job (after RT and OT)
                jobs_with_remaining_hours = []
                remaining_rt_check = rt_day
                remaining_ot_check = ot_day
                
                # Calculate remaining hours after RT and OT allocation
                for job_num, day_hours_worked in jobs_with_day_hours:
                    rt_allocated = min(day_hours_worked, remaining_rt_check)
                    remaining_rt_check -= rt_allocated
                    hours_after_rt = day_hours_worked - rt_allocated
                    
                    ot_allocated = min(hours_after_rt, remaining_ot_check) if hours_after_rt > 0 else 0
                    remaining_ot_check -= ot_allocated
                    
                    remaining_hours = hours_after_rt - ot_allocated
                    if remaining_hours > 0:
                        jobs_with_remaining_hours.append((job_num, remaining_hours))
                
                # Sort by remaining hours (descending) for priority
                jobs_with_remaining_hours.sort(key=lambda x: x[1], reverse=True)
                remaining_dt_day = dt_day
                
                for job_num, remaining_hours in jobs_with_remaining_hours:
                    if remaining_dt_day <= 0:
                        break
                    dt_for_job = min(remaining_dt_day, remaining_hours)
                    remaining_dt_day -= dt_for_job
                    
                    # Distribute DT across hour codes for this job (day only)
                    for code in hour_codes:
                        if code != 'Travel' and dt_for_job > 0:
                            code_hours = job_hours[job_num][code][date]
                            if code_hours > 0:
                                dt_for_code = min(code_hours, dt_for_job)
                                job_dt_hours[job_num][code] += dt_for_code
                                dt_for_job -= dt_for_code
                                if dt_for_job <= 0:
                                    break
            else:
                job_num = jobs_with_day_hours[0][0]
                job_dt_hours[job_num]['6220'] += dt_day
    
    # Allocate night hours separately
    if jobs_with_night_hours and (rt_night > 0 or ot_night > 0 or dt_night > 0):
        # Allocate regular time for night hours
        remaining_rt_night = rt_night
        for job_num, night_hours_worked in jobs_with_night_hours:
            if remaining_rt_night <= 0:
                break
            rt_for_job = min(night_hours_worked, remaining_rt_night)
            remaining_rt_night -= rt_for_job
            
            # Distribute RT across hour codes for this job (night only)
            for code in hour_codes:
                if code != 'Travel' and rt_for_job > 0:
                    code_hours = job_hours[job_num][code][date]
                    if code_hours > 0:
                        rt_for_code = min(code_hours, rt_for_job)
                        job_rt_hours[job_num][code] += rt_for_code
                        rt_for_job -= rt_for_code
                        if rt_for_job <= 0:
                            break
        
        # Allocate overtime for night hours
        if ot_night > 0:
            if len(jobs_with_night_hours) > 1:
                nightly_job_hours = sorted(jobs_with_night_hours, key=lambda x: x[1], reverse=True)
                remaining_ot_night = ot_night
                
                for job_num, night_hours_today in nightly_job_hours:
                    if remaining_ot_night <= 0:
                        break
                    ot_for_job = min(remaining_ot_night, night_hours_today)
                    remaining_ot_night -= ot_for_job
                    
                    # Distribute OT across hour codes for this job (night only)
                    for code in hour_codes:
                        if code != 'Travel' and ot_for_job > 0:
                            code_hours = job_hours[job_num][code][date]
                            if code_hours > 0:
                                ot_for_code = min(code_hours, ot_for_job)
                                job_ot_hours[job_num][code] += ot_for_code
                                ot_for_job -= ot_for_code
                                if ot_for_job <= 0:
                                    break
            else:
                job_num = jobs_with_night_hours[0][0]
                job_ot_hours[job_num]['6220'] += ot_night
        
        # Allocate double time for night hours
        if dt_night > 0:
            if len(jobs_with_night_hours) > 1:
                nightly_job_hours = sorted(jobs_with_night_hours, key=lambda x: x[1], reverse=True)
                remaining_dt_night = dt_night
                
                for job_num, night_hours_today in nightly_job_hours:
                    if remaining_dt_night <= 0:
                        break
                    dt_for_job = min(remaining_dt_night, night_hours_today)
                    remaining_dt_night -= dt_for_job
                    
                    # Distribute DT across hour codes for this job (night only)
                    for code in hour_codes:
                        if code != 'Travel' and dt_for_job > 0:
                            code_hours = job_hours[job_num][code][date]
                            if code_hours > 0:
                                dt_for_code = min(code_hours, dt_for_job)
                                job_dt_hours[job_num][code] += dt_for_code
                                dt_for_job -= dt_for_code
                                if dt_for_job <= 0:
                                    break
            else:
                job_num = jobs_with_night_hours[0][0]
                job_dt_hours[job_num]['6220'] += dt_night
    


def reallocate_weekly_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, date, adjust_amount, shift_type):
    """Reallocate weekly overtime to jobs for a specific date"""
    # Get jobs that worked on this date, sorted by most hours first
    jobs_with_hours = []
    for job_num, job_data in job_hours.items():
        total_job_hours = sum(job_data[code][date] for code in hour_codes if code != 'Travel')
        if total_job_hours > 0:
            jobs_with_hours.append((job_num, total_job_hours))
    
    if not jobs_with_hours:
        return
    
    # Sort by hours worked (descending) to prioritize jobs with more hours
    jobs_with_hours.sort(key=lambda x: x[1], reverse=True)
    
    # Allocate weekly OT to jobs with most hours first
    remaining_adjust = adjust_amount
    for job_num, job_total in jobs_with_hours:
        if remaining_adjust <= 0:
            break
            
        # Allocate overtime to this job based on hours worked
        ot_to_allocate = min(remaining_adjust, job_total)
        remaining_adjust -= ot_to_allocate
        
        # Distribute weekly OT across hour codes for this job
        for code in hour_codes:
            if code != 'Travel' and ot_to_allocate > 0:
                code_hours = job_hours[job_num][code][date]
                if code_hours > 0:
                    # Convert from regular time to overtime for this code
                    hours_to_convert = min(code_hours, ot_to_allocate)
                    job_rt_hours[job_num][code] -= hours_to_convert
                    job_ot_hours[job_num][code] += hours_to_convert
                    ot_to_allocate -= hours_to_convert
                    if ot_to_allocate <= 0:
                        break

def reallocate_period_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, adjust_amount, shift_type):
    """Reallocate period overtime to jobs"""
    # Get all jobs with hours, sorted by most hours first
    jobs_with_hours = []
    for job_num, job_data in job_hours.items():
        total_job_hours = sum(sum(job_data[code].values()) for code in hour_codes if code != 'Travel')
        if total_job_hours > 0:
            jobs_with_hours.append((job_num, total_job_hours))
    
    if not jobs_with_hours:
        return
    
    # Sort by hours worked (descending) to prioritize jobs with most hours
    jobs_with_hours.sort(key=lambda x: x[1], reverse=True)
    
    # Allocate period OT to jobs with most hours first
    remaining_adjust = adjust_amount
    for job_num, job_total in jobs_with_hours:
        if remaining_adjust <= 0:
            break
            
        # Get remaining hours for this job across all dates
        job_remaining_hours = 0
        for code in hour_codes:
            if code != 'Travel':
                for date in job_hours[job_num][code]:
                    code_hours = job_hours[job_num][code][date]
                    # For period OT, we need to check total allocated hours across all dates
                    rt_allocated = job_rt_hours[job_num][code]
                    ot_allocated = job_ot_hours[job_num][code]
                    job_remaining_hours += max(0, code_hours - rt_allocated - ot_allocated)
        
        if job_remaining_hours > 0:
            ot_to_allocate = min(remaining_adjust, job_remaining_hours)
            remaining_adjust -= ot_to_allocate
            
            # Distribute period OT across hour codes for this job
            for code in hour_codes:
                if code != 'Travel' and remaining_adjust < adjust_amount:
                    for date in job_hours[job_num][code]:
                        code_hours = job_hours[job_num][code][date]
                        rt_allocated = job_rt_hours[job_num][code]
                        ot_allocated = job_ot_hours[job_num][code]
                        available_hours = max(0, code_hours - rt_allocated - ot_allocated)
                        if available_hours > 0:
                            ot_allocated = min(available_hours, ot_to_allocate)
                            job_ot_hours[job_num][code] += ot_allocated
                            ot_to_allocate -= ot_allocated
                            if ot_to_allocate <= 0:
                                break
                    if ot_to_allocate <= 0:
                        break

def is_night_shift(job_num, code):
    """Check if a job/code combination is night shift"""
    # This would need to access the night shift variables from the employee data
    # For now, return False as a placeholder
    return False

def create_tab(emp):
    data = employee_data[emp]
    frame = tk.Frame(notebook)
    notebook.add(frame, text=emp)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=0)
    frame.grid_rowconfigure(3, weight=0)
    for i in range(5):
        frame.grid_columnconfigure(i, weight=1)
    frame.grid_columnconfigure(5, weight=0)

    rate_frame = tk.Frame(frame)
    rate_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=3, pady=3)
    tk.Label(rate_frame, text="Hourly Rate:", font=('Arial', 8)).pack(side="left", padx=3)
    rate_label = tk.Label(rate_frame, text=f"${rates.get(emp, 0.0):.2f}", font=('Arial', 8))
    rate_label.pack(side="left", padx=3)
    data['rate_label'] = rate_label

    canvas = tk.Canvas(frame, height=500)
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta/120), "units"))
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=3, pady=3)
    scrollbar.grid(row=1, column=5, sticky="ns", padx=(0, 3), pady=3)

    table_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor="nw")
    num_cols = 4 + len(data['dates']) + 1
    for i in range(num_cols):
        table_frame.grid_columnconfigure(i, weight=1, uniform="cols", minsize=80)
    for i in range(50):
        table_frame.grid_rowconfigure(i, weight=1, minsize=20)
    data['table_frame'] = table_frame
    table_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    button_frame = tk.Frame(frame)
    button_frame.grid(row=2, column=0, columnspan=6, sticky="ew", padx=3, pady=3)
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=0)
    button_frame.grid_columnconfigure(2, weight=0)
    button_frame.grid_columnconfigure(3, weight=0)
    button_frame.grid_columnconfigure(4, weight=0)
    button_frame.grid_columnconfigure(5, weight=0)
    button_frame.grid_columnconfigure(6, weight=0)
    button_frame.grid_columnconfigure(7, weight=1)

    tk.Label(button_frame, text="Vacation Pay:", font=('Arial', 8)).grid(row=0, column=0, sticky="e", padx=3, pady=3)
    data['vacation_pay_entry'] = tk.Entry(button_frame, width=10, font=('Arial', 8), justify='center')
    data['vacation_pay_entry'].grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
    data['vacation_pay_entry'].bind("<KeyRelease>", lambda event, e=emp: add_vacation_pay(e, silent=True))
    data['add_button'] = tk.Button(button_frame, text="Add Job", font=('Arial', 8), width=8, command=lambda e=emp: add_job(e))
    data['add_button'].grid(row=0, column=2, padx=5, pady=3)
    tk.Button(button_frame, text="Reset", font=('Arial', 8), width=8, command=lambda e=emp: reset_employee_data(e)).grid(row=0, column=3, padx=5, pady=3)

    totals_frame = tk.Frame(frame)
    totals_frame.grid(row=3, column=0, columnspan=6, sticky="nsew", padx=3, pady=3)
    for i in range(len(hour_codes) + 11):
        totals_frame.grid_columnconfigure(i, weight=1, uniform="totals", minsize=80)
    data['totals_frame'] = totals_frame

    set_date_range(emp)
    setup_job_navigation(emp)
    update_layout(emp)

def set_date_range(emp):
    data = employee_data[emp]
    for widget in data['table_frame'].winfo_children():
        widget.destroy()
    for widget in data['totals_frame'].winfo_children():
        widget.destroy()

    data['job_rows'].clear()
    data['entries'].clear()
    data['col_total_labels'].clear()
    data['code_total_labels'].clear()
    data['job_entries'] = []
    data['job_name_labels'] = []
    data['daily_totals_label'] = None
    data['grand_total_label'] = None
    data['add_button'] = None
    data['night_shift_vars'] = {}
    data['hour_entries_grid'] = []
    data['row_total_labels'] = []
    data['vacation_pay_label'] = None
    data['vacation_pay'] = 0.0

    for i, d in enumerate(data['dates']):
        date_obj = datetime.strptime(d, '%Y-%m-%d')
        tk.Label(data['table_frame'], text=date_obj.strftime('%a'), font=('Arial', 8), anchor="center").grid(row=0, column=4 + i, sticky="nsew", padx=3, pady=3)
        tk.Label(data['table_frame'], text=d, font=('Arial', 8), anchor="center").grid(row=1, column=4 + i, sticky="nsew", padx=3, pady=3)
    tk.Label(data['table_frame'], text="Total", font=('Arial', 8), anchor="center").grid(row=0, column=4 + len(data['dates']), sticky="nsew", padx=3, pady=3)

    for i in range(data['job_count']):
        job_num = f"job{i+1}"
        base_row = i * 5 + 2

        job_frame = tk.Frame(data['table_frame'], borderwidth=1, relief="solid")
        job_frame.grid(row=base_row, column=0, columnspan=4 + len(data['dates']), rowspan=5, sticky="nsew", padx=3, pady=3)
        for j in range(4 + len(data['dates'])):
            job_frame.grid_columnconfigure(j, weight=1, uniform="cols", minsize=80)

        for col, text in enumerate(["Job Number", "Hour Code", "Night Shift", "Job Name"]):
            tk.Label(job_frame, text=text, font=('Arial', 8), anchor="center").grid(row=0, column=col, sticky="nsew", padx=3, pady=3)

        job_entry = tk.Entry(job_frame, width=5, font=('Arial', 8), justify='center')
        job_entry.grid(row=2, column=0, sticky="nsew", padx=3, pady=3)
        job_entry.bind("<KeyRelease>", lambda event, e=emp, r=i: update_job_name(e, r))
        data['job_entries'].append(job_entry)

        job_name_label = tk.Label(job_frame, text="", font=('Arial', 8), anchor="center", wraplength=80, justify="center")
        job_name_label.grid(row=1, column=3, rowspan=4, sticky="nsew", padx=3, pady=3)
        data['job_name_labels'].append(job_name_label)

        for j, code in enumerate(hour_codes):
            row = j + 1
            tk.Label(job_frame, text=code, font=('Arial', 8), anchor="center").grid(row=row, column=1, sticky="nsew", padx=3, pady=3)
            if code != 'Travel':
                var = tk.BooleanVar()
                tk.Checkbutton(job_frame, variable=var).grid(row=row, column=2, sticky="nsew", padx=3, pady=3)
                data['night_shift_vars'][(job_num, code)] = var
                var.trace("w", lambda *args, e=emp: calculate(e))
            else:
                tk.Label(job_frame, text="", font=('Arial', 8), anchor="center").grid(row=row, column=2, sticky="nsew", padx=3, pady=3)
            date_entries = []
            for k, d in enumerate(data['dates']):
                hour_entry = tk.Entry(job_frame, width=5, font=('Arial', 8), justify='center')
                hour_entry.grid(row=row, column=4 + k, sticky="nsew", padx=3, pady=3)
                hour_entry.bind("<KeyRelease>", lambda event, e=emp: calculate(e))
                data['entries'][(job_num, d, code)] = hour_entry
                date_entries.append(hour_entry)
            data['hour_entries_grid'].append(date_entries)
            total_label = tk.Label(data['table_frame'], text="0", font=('Arial', 8), anchor="center")
            total_label.grid(row=base_row + row, column=4 + len(data['dates']), sticky="nsew", padx=3, pady=3)
            data['row_total_labels'].append(total_label)
        data['job_rows'][job_num] = base_row

    add_totals_row(emp)

    col = 0
    data['code_total_labels'] = {}
    for code in hour_codes:
        tk.Label(data['totals_frame'], text=f"Total Hours ({code})", font=('Arial', 7), anchor="center").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
        l = tk.Label(data['totals_frame'], text="0", font=('Arial', 7), anchor="center")
        l.grid(row=1, column=col, sticky="nsew", padx=2, pady=2)
        data['code_total_labels'][code] = l
        col += 1
    for label, text in [
        ('rt_day_hours_label', "Regular Day Hours"), ('ot_day_hours_label', "OT Day Hours"), ('dt_day_hours_label', "2xDay Hours"),
        ('rt_night_hours_label', "Regular Night Hours"), ('ot_night_hours_label', "OT Night Hours"), ('dt_night_hours_label', "2xNight Hours"),
        ('travel_hours_label', "Travel Hours"), ('travel_amount_label', "Travel Amount"),
        ('vacation_pay_label', "Vacation Pay"), ('rt_amount_label', "Regular Amount"), ('ot_amount_label', "Overtime Amount"), ('gross_label', "Total Gross Pay")
    ]:
        tk.Label(data['totals_frame'], text=text, font=('Arial', 7), anchor="center").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
        l = tk.Label(data['totals_frame'], text="$0" if "amount" in label or "gross" in label or "vacation" in label else "0", font=('Arial', 7), anchor="center")
        l.grid(row=1, column=col, sticky="nsew", padx=2, pady=2)
        data[label] = l
        col += 1

def calculate(emp):
    data = employee_data[emp]
    rate = rates.get(emp, 0.0)
    night_premium = 5.0
    code_hours = {code: 0.0 for code in hour_codes}
    daily_normal = {d: 0.0 for d in data['dates']}
    daily_night = {d: 0.0 for d in data['dates']}
    daily_travel = {d: 0.0 for d in data['dates']}
    
    # Store job-specific data for breakdown
    job_hours = {}
    job_rt_hours = {}
    job_ot_hours = {}
    job_dt_hours = {}

    # Collect hours from entries
    for job_num in data['job_rows']:
        job_entry = data['job_entries'][list(data['job_rows'].keys()).index(job_num)].get().strip()
        if job_entry:
            job_hours[job_entry] = {code: {d: 0.0 for d in data['dates']} for code in hour_codes}
            job_rt_hours[job_entry] = {code: 0.0 for code in hour_codes}
            job_ot_hours[job_entry] = {code: 0.0 for code in hour_codes}
            job_dt_hours[job_entry] = {code: 0.0 for code in hour_codes}
            
        for code in hour_codes:
            is_night = data['night_shift_vars'].get((job_num, code), tk.BooleanVar(value=False)).get() if code != 'Travel' else False
            for d in data['dates']:
                entry = data['entries'].get((job_num, d, code))
                if entry:
                    h = safe_float(entry.get())
                    code_hours[code] += h
                    if job_entry:
                        job_hours[job_entry][code][d] = h
                    if code == 'Travel':
                        daily_travel[d] += h
                    elif is_night:
                        daily_night[d] += h
                    else:
                        daily_normal[d] += h

    # Apply daily overtime rules (excluding Travel) - allocate by day first
    rt_day_hours = ot_day_hours = dt_day_hours = rt_night_hours = ot_night_hours = dt_night_hours = 0.0
    daily_rt_day = {d: 0.0 for d in data['dates']}
    daily_rt_night = {d: 0.0 for d in data['dates']}
    daily_ot_day = {d: 0.0 for d in data['dates']}
    daily_ot_night = {d: 0.0 for d in data['dates']}
    daily_dt_day = {d: 0.0 for d in data['dates']}
    daily_dt_night = {d: 0.0 for d in data['dates']}
    rt_travel = round(sum(daily_travel.values()), 2)
    
    # Process each day and allocate overtime to jobs
    for d in data['dates']:
        day_h = daily_normal[d]
        night_h = daily_night[d]
        total_h = day_h + night_h
        
        if total_h > 0:
            # Daily overtime allocation (day first, then week, then period)
            # Regular time (up to 8 hours)
            rt = min(total_h, 8.0)
            rt_night = min(night_h, rt)
            rt_day = rt - rt_night
            
            # Overtime (8-12 hours)
            ot = max(0.0, min(total_h - 8.0, 4.0))
            ot_day = min(ot, day_h - rt_day)
            ot_night = ot - ot_day
            if ot_day < 0:
                ot_night += ot_day
                ot_day = 0
            
            # Double time (>12 hours)
            dt = max(0.0, total_h - 12.0)
            dt_day = min(dt, day_h - rt_day - ot_day)
            dt_night = dt - dt_day
            
            # Create job number to job identifier mapping for night shift vars
            job_num_to_id = {}
            for job_idx, job_num in enumerate(data['job_rows']):
                job_entry = data['job_entries'][job_idx].get().strip()
                if job_entry:
                    job_num_to_id[job_entry] = job_num
            
            # Allocate these hours to jobs for this day
            allocate_hours_to_jobs(job_hours, job_rt_hours, job_ot_hours, job_dt_hours, d, rt_day, rt_night, ot_day, ot_night, dt_day, dt_night, data['night_shift_vars'], job_num_to_id)
            
            # Daily allocation is complete - no need for redistribution
            
            daily_rt_day[d] = rt_day
            daily_rt_night[d] = rt_night
            daily_ot_day[d] = ot_day
            daily_ot_night[d] = ot_night
            daily_dt_day[d] = dt_day
            daily_dt_night[d] = dt_night
            rt_day_hours += rt_day
            ot_day_hours += ot_day
            dt_day_hours += dt_day
            rt_night_hours += rt_night
            ot_night_hours += ot_night
            dt_night_hours += dt_night

    # Apply weekly and period overtime rules
    weeks = get_weeks(data['dates'])
    working_days = len([d for d in data['dates'] if datetime.strptime(d, '%Y-%m-%d').weekday() < 5])  # Mon-Fri
    period_ot_threshold = working_days * 8.0
    
    # Track total period hours for period OT calculation
    total_period_hours = rt_day_hours + ot_day_hours + dt_day_hours + rt_night_hours + ot_night_hours + dt_night_hours
    
    # Calculate weekly overtime (>40 hours per week, Sunday to Saturday)
    for week_start, week_dates in weeks.items():
        week_rt_total = sum(daily_rt_day.get(d, 0) + daily_rt_night.get(d, 0) for d in week_dates)
        week_ot_total = sum(daily_ot_day.get(d, 0) + daily_ot_night.get(d, 0) for d in week_dates)
        week_total = week_rt_total + week_ot_total
        
        if week_total > 40.0:
            weekly_ot_needed = week_total - 40.0
            # Reallocate from regular time to overtime for this week
            weekly_rt_to_convert = min(weekly_ot_needed, week_rt_total - 40.0) if week_rt_total > 40.0 else 0.0
            
            if weekly_rt_to_convert > 0:
                # Convert regular time to overtime for this week
                remaining_to_convert = weekly_rt_to_convert
                for d in week_dates:
                    if remaining_to_convert <= 0:
                        break
                    
                    day_rt_total = daily_rt_day.get(d, 0) + daily_rt_night.get(d, 0)
                    if day_rt_total > 0:
                        # Convert proportionally from day and night
                        day_convert = min(remaining_to_convert, daily_rt_day.get(d, 0))
                        night_convert = min(remaining_to_convert - day_convert, daily_rt_night.get(d, 0))
                        
                        # Update daily totals
                        daily_rt_day[d] -= day_convert
                        daily_rt_night[d] -= night_convert
                        daily_ot_day[d] += day_convert
                        daily_ot_night[d] += night_convert
                        
                        # Update summary totals
                        rt_day_hours -= day_convert
                        rt_night_hours -= night_convert
                        ot_day_hours += day_convert
                        ot_night_hours += night_convert
                        
                        remaining_to_convert -= (day_convert + night_convert)
                        
                        # Reallocate to jobs for this date
                        if day_convert > 0:
                            reallocate_weekly_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, d, day_convert, 'day')
                        if night_convert > 0:
                            reallocate_weekly_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, d, night_convert, 'night')
    
    # Calculate period overtime (>working_days * 8 hours for the period)
    if total_period_hours > period_ot_threshold:
        period_ot_needed = total_period_hours - period_ot_threshold
        period_rt_total = rt_day_hours + rt_night_hours
        period_rt_to_convert = min(period_ot_needed, period_rt_total - period_ot_threshold) if period_rt_total > period_ot_threshold else 0.0
        
        if period_rt_to_convert > 0:
            # Convert regular time to overtime across the entire period
            remaining_to_convert = period_rt_to_convert
            for d in data['dates']:
                if remaining_to_convert <= 0:
                    break
                
                day_rt_total = daily_rt_day.get(d, 0) + daily_rt_night.get(d, 0)
                if day_rt_total > 0:
                    # Convert proportionally from day and night
                    day_convert = min(remaining_to_convert, daily_rt_day.get(d, 0))
                    night_convert = min(remaining_to_convert - day_convert, daily_rt_night.get(d, 0))
                    
                    # Update daily totals
                    daily_rt_day[d] -= day_convert
                    daily_rt_night[d] -= night_convert
                    daily_ot_day[d] += day_convert
                    daily_ot_night[d] += night_convert
                    
                    # Update summary totals
                    rt_day_hours -= day_convert
                    rt_night_hours -= night_convert
                    ot_day_hours += day_convert
                    ot_night_hours += night_convert
                    
                    remaining_to_convert -= (day_convert + night_convert)
                    
                    # Reallocate to jobs for this date
                    if day_convert > 0:
                        reallocate_weekly_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, d, day_convert, 'day')
                    if night_convert > 0:
                        reallocate_weekly_ot_to_jobs(job_hours, job_rt_hours, job_ot_hours, d, night_convert, 'night')
    
    # Store job breakdown data for PDF with day/night separation
    data['job_breakdown'] = {
        'job_hours': job_hours,
        'job_rt_hours': job_rt_hours,
        'job_ot_hours': job_ot_hours,
        'job_dt_hours': job_dt_hours,
        'job_rt_day_hours': {},
        'job_rt_night_hours': {},
        'job_ot_day_hours': {},
        'job_ot_night_hours': {},
        'job_dt_day_hours': {},
        'job_dt_night_hours': {}
    }

    # Create job number to job identifier mapping for night shift vars
    job_num_to_id = {}
    for job_idx, job_id in enumerate(data['job_rows']):
        job_entry = data['job_entries'][job_idx].get().strip()
        if job_entry:
            job_num_to_id[job_entry] = job_id

    # Populate day and night breakdown using allocated hours
    for job_num in job_hours:
        data['job_breakdown']['job_rt_day_hours'][job_num] = {code: 0.0 for code in hour_codes}
        data['job_breakdown']['job_rt_night_hours'][job_num] = {code: 0.0 for code in hour_codes}
        data['job_breakdown']['job_ot_day_hours'][job_num] = {code: 0.0 for code in hour_codes}
        data['job_breakdown']['job_ot_night_hours'][job_num] = {code: 0.0 for code in hour_codes}
        data['job_breakdown']['job_dt_day_hours'][job_num] = {code: 0.0 for code in hour_codes}
        data['job_breakdown']['job_dt_night_hours'][job_num] = {code: 0.0 for code in hour_codes}

        for code in hour_codes:
            if code != 'Travel':
                # Check if this job/code combination is night shift
                is_night = False
                job_id = job_num_to_id.get(job_num)
                if job_id:
                    night_var = data['night_shift_vars'].get((job_id, code))
                    if night_var and night_var.get():
                        is_night = True

                # Assign allocated hours to day or night based on night shift status
                rt_hours = job_rt_hours[job_num][code]
                ot_hours = job_ot_hours[job_num][code]
                dt_hours = job_dt_hours[job_num][code]

                if is_night:
                    data['job_breakdown']['job_rt_night_hours'][job_num][code] = rt_hours
                    data['job_breakdown']['job_ot_night_hours'][job_num][code] = ot_hours
                    data['job_breakdown']['job_dt_night_hours'][job_num][code] = dt_hours
                else:
                    data['job_breakdown']['job_rt_day_hours'][job_num][code] = rt_hours
                    data['job_breakdown']['job_ot_day_hours'][job_num][code] = ot_hours
                    data['job_breakdown']['job_dt_day_hours'][job_num][code] = dt_hours
            else:
                # Travel hours are neither day nor night, store in job_hours directly
                data['job_breakdown']['job_rt_day_hours'][job_num][code] = sum(job_hours[job_num][code].values())

    # Verify totals match
    total_from_breakdown = 0.0
    for job_num in job_hours:
        for code in hour_codes:
            if code == 'Travel':
                total_from_breakdown += sum(job_hours[job_num][code].values())
            else:
                rt_day = data['job_breakdown']['job_rt_day_hours'][job_num][code]
                rt_night = data['job_breakdown']['job_rt_night_hours'][job_num][code]
                ot_day = data['job_breakdown']['job_ot_day_hours'][job_num][code]
                ot_night = data['job_breakdown']['job_ot_night_hours'][job_num][code]
                dt_day = data['job_breakdown']['job_dt_day_hours'][job_num][code]
                dt_night = data['job_breakdown']['job_dt_night_hours'][job_num][code]
                total_from_breakdown += (rt_day + rt_night + ot_day + ot_night + dt_day + dt_night)

    # Round hours to 2 decimal places
    rt_day_hours = round(rt_day_hours, 2)
    ot_day_hours = round(ot_day_hours, 2)
    dt_day_hours = round(dt_day_hours, 2)
    rt_night_hours = round(rt_night_hours, 2)
    ot_night_hours = round(ot_night_hours, 2)
    dt_night_hours = round(dt_night_hours, 2)
    rt_travel = round(rt_travel, 2)
    total_hours = round(rt_day_hours + ot_day_hours + dt_day_hours + rt_night_hours + ot_night_hours + dt_night_hours + rt_travel, 2)

    # Calculate amounts
    base_rate = rate
    night_rate = rate + night_premium
    rt_amount = round((rt_day_hours * base_rate) + (rt_night_hours * night_rate), 2)
    ot_amount = round(
        (ot_day_hours * base_rate * 1.5) +
        (ot_night_hours * night_rate * 1.5) +
        (dt_day_hours * base_rate * 2.0) +
        (dt_night_hours * night_rate * 2.0), 2)
    travel_amount = round(rt_travel * base_rate, 2)
    gross = round(rt_amount + ot_amount + travel_amount + data['vacation_pay'], 2)

    # Update GUI labels
    for code in hour_codes:
        value = round(code_hours[code], 2)
        data['code_total_labels'][code].config(text=f"{value:g}")
    for d in data['dates']:
        value = round(daily_normal[d] + daily_night[d] + daily_travel[d], 2)
        data['col_total_labels'][d].config(text=f"{value:g}")
    data['rt_day_hours_label'].config(text=f"{rt_day_hours:g}")
    data['ot_day_hours_label'].config(text=f"{ot_day_hours:g}")
    data['dt_day_hours_label'].config(text=f"{dt_day_hours:g}")
    data['rt_night_hours_label'].config(text=f"{rt_night_hours:g}")
    data['ot_night_hours_label'].config(text=f"{ot_night_hours:g}")
    data['dt_night_hours_label'].config(text=f"{dt_night_hours:g}")
    data['travel_hours_label'].config(text=f"{rt_travel:g}")
    data['travel_amount_label'].config(text=f"${travel_amount:.2f}")
    data['vacation_pay_label'].config(text=f"${data['vacation_pay']:.2f}")
    data['rt_amount_label'].config(text=f"${rt_amount:.2f}")
    data['ot_amount_label'].config(text=f"${ot_amount:.2f}")
    data['gross_label'].config(text=f"${gross:.2f}")
    data['grand_total_label'].config(text=f"{total_hours:g}")

    for idx, date_entries in enumerate(data['hour_entries_grid']):
        row_total = sum(safe_float(e.get()) for e in date_entries)
        value = round(row_total, 2)
        data['row_total_labels'][idx].config(text=f"{value:g}")

def print_to_pdf():
    try:
        selected_period = period_var.get()
        start_date, end_date = selected_period.split(" to ")
        pdf_filename = f"Timesheet_{start_date}_to_{end_date}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(A3), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']

        for emp in employees:
            data = employee_data[emp]
            # Calculate job breakdown before generating PDF
            calculate(emp)
            # Employee header
            elements.append(Paragraph(f"Timesheet for {emp}", title_style))
            base_rate = rates.get(emp, 0.0)
            night_rate = base_rate + 5.0  # Night premium
            ot_night_rate = night_rate * 1.5  # OT night rate
            elements.append(Paragraph(f"Hourly Rate: ${base_rate:.2f} | Night Rate: ${night_rate:.2f} | OT Night Rate: ${ot_night_rate:.2f}", normal_style))
            elements.append(Paragraph(f"Pay Period: {start_date} to {end_date}", normal_style))
            elements.append(Spacer(1, 12))

            # Prepare job columns with job number and hour code, adding (Night) if checked, filtering out empty ones
            job_columns = []
            job_indices = []
            job_legend = {}  # Dictionary to store job number and name for legend
            for i, job_num in enumerate(data['job_rows']):
                job_entry = data['job_entries'][i].get().strip()
                for code in hour_codes:
                    total = sum(safe_float(data['entries'].get((job_num, d, code), tk.Entry()).get()) for d in data['dates'])
                    if total > 0:
                        night_text = " (Night)" if code != 'Travel' and data['night_shift_vars'].get((job_num, code), tk.BooleanVar(value=False)).get() else ""
                        job_columns.append(f"{job_entry}\n{code}{night_text}")
                        job_indices.append((i, job_num, code))
                        # Add to legend only if job has hours
                        if job_entry and job_entry not in job_legend:
                            job_name = job_name_map.get(job_entry, "")
                            job_legend[job_entry] = job_name

            if not job_columns:
                elements.append(Paragraph("No non-zero hours recorded", normal_style))
                # Don't continue here - we still want to show summary if there's vacation pay

            # Only create main table if there are job columns
            if job_columns:
                # Prepare table header
                table_data = [['Date'] + job_columns + ['Total']]

                # Collect hours by date, filtering out empty rows
                for d in data['dates']:
                    row = [datetime.strptime(d, '%Y-%m-%d').strftime('%a %Y-%m-%d')]
                    total_hours = 0.0
                    row_data = []
                    for i, job_num, code in job_indices:
                        hours = safe_float(data['entries'].get((job_num, d, code), tk.Entry()).get())
                        row_data.append(f"{hours:.2f}" if hours > 0 else '')
                        total_hours += hours
                    if total_hours > 0:
                        row.extend(row_data)
                        row.append(f"{total_hours:.2f}")
                        table_data.append(row)

                # Add column totals, only for non-zero columns
                col_totals = ['Totals']
                grand_total = 0.0
                for i, job_num, code in job_indices:
                    total = sum(safe_float(data['entries'].get((job_num, d, code), tk.Entry()).get()) for d in data['dates'])
                    col_totals.append(f"{total:.2f}" if total > 0 else '')
                    grand_total += total
                if grand_total > 0:
                    col_totals.append(f"{grand_total:.2f}")
                    table_data.append(col_totals)

                # Calculate column widths to fit content
                num_cols = len(job_columns) + 2  # Date + Total
                available_width = 1190 - 60 - 120 - 80  # A3 landscape width minus margins and wider Date/Total columns
                col_width = available_width / max(len(job_columns), 1)  # Avoid division by zero
                colWidths = [120] + [max(80, col_width)] * len(job_columns) + [80]  # Wider Date (120) and Total (80) columns

                # Create main table with adjusted font sizes and row heights
                table = Table(table_data, colWidths=colWidths, rowHeights=[30] * len(table_data))
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))

                # Add job breakdown section
                if 'job_breakdown' in data and data['job_breakdown']['job_hours']:
                    elements.append(Paragraph("Job Breakdown by Hour Codes", normal_style))
                    
                    # Create job breakdown table
                    breakdown_data = []
                    
                    # First row: Job Numbers
                    job_numbers_row = ["Job Number"]
                    job_names_row = ["Job Name"]
                    
                    # Collect all jobs and their data
                    for job_num in data['job_breakdown']['job_hours']:
                        job_name = job_name_map.get(job_num, "")
                        # Keep full job names - they will wrap in the table
                        job_numbers_row.append(job_num)
                        job_names_row.append(job_name)
                    
                    breakdown_data.append(job_numbers_row)
                    breakdown_data.append(job_names_row)
                    
                    # Create Regular Time row
                    regular_time_row = ["Regular Time"]
                    for job_num in data['job_breakdown']['job_hours']:
                        regular_hours_list = []
                        
                        # Collect all regular time hours for this job
                        for code in ['6100', '1210', '6220']:
                            # Day hours
                            rt_day_hours = data['job_breakdown']['job_rt_day_hours'][job_num][code]
                            if rt_day_hours > 0:
                                regular_hours_list.append(f"{rt_day_hours:.1f}(RT{code})")
                            
                            # Night hours
                            rt_night_hours = data['job_breakdown']['job_rt_night_hours'][job_num][code]
                            if rt_night_hours > 0:
                                regular_hours_list.append(f"{rt_night_hours:.1f}(RTN{code})")
                        
                        # Travel hours
                        travel_hours = sum(data['job_breakdown']['job_hours'][job_num]['Travel'].values())
                        if travel_hours > 0:
                            regular_hours_list.append(f"{travel_hours:.1f}(Travel)")
                        
                        # Join all regular hours for this job
                        regular_time_row.append(" ".join(regular_hours_list) if regular_hours_list else "")
                    
                    # Create Overtime row
                    overtime_row = ["Overtime"]
                    for job_num in data['job_breakdown']['job_hours']:
                        overtime_hours_list = []
                        
                        # Collect all overtime hours for this job
                        for code in ['6100', '1210', '6220']:
                            # Day overtime
                            ot_day_hours = data['job_breakdown']['job_ot_day_hours'][job_num][code]
                            if ot_day_hours > 0:
                                overtime_hours_list.append(f"{ot_day_hours:.1f}(OT{code})")
                            
                            # Night overtime
                            ot_night_hours = data['job_breakdown']['job_ot_night_hours'][job_num][code]
                            if ot_night_hours > 0:
                                overtime_hours_list.append(f"{ot_night_hours:.1f}(OTN{code})")
                            
                            # Day double time
                            dt_day_hours = data['job_breakdown']['job_dt_day_hours'][job_num][code]
                            if dt_day_hours > 0:
                                overtime_hours_list.append(f"{dt_day_hours:.1f}(2xOT{code})")
                            
                            # Night double time
                            dt_night_hours = data['job_breakdown']['job_dt_night_hours'][job_num][code]
                            if dt_night_hours > 0:
                                overtime_hours_list.append(f"{dt_night_hours:.1f}(2xOTN{code})")
                        
                        # Join all overtime hours for this job
                        overtime_row.append(" ".join(overtime_hours_list) if overtime_hours_list else "")
                    
                    # Add the rows to breakdown data
                    breakdown_data.append(regular_time_row)
                    breakdown_data.append(overtime_row)
                    
                    if len(breakdown_data) > 2:  # More than just headers
                        # Calculate column widths - make them wider
                        num_cols = len(job_numbers_row)
                        available_width = 1190 - 60  # A3 landscape width minus margins
                        first_col_width = 150  # Wider first column for labels
                        remaining_width = available_width - first_col_width
                        other_col_width = max(120, remaining_width / (num_cols - 1))  # Minimum 120px per column
                        col_widths = [first_col_width] + [other_col_width] * (num_cols - 1)
                        
                        # Calculate row heights for the 4 rows: Job Number, Job Name, Regular Time, Overtime
                        # Give more height to job names, regular time, and overtime rows for text wrapping
                        row_heights = [25, 35, 40, 40]
                        breakdown_table = Table(breakdown_data, colWidths=col_widths, rowHeights=row_heights)
                        breakdown_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.grey),  # First column header
                            ('BACKGROUND', (0, 0), (-1, 1), colors.grey),  # Top two rows
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 1), 9),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 2), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 1), 8),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('LEFTPADDING', (0, 0), (-1, -1), 4),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                            ('BACKGROUND', (1, 2), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                            ('WORDWRAP', (0, 0), (-1, -1), True),
                        ]))
                        elements.append(breakdown_table)
                        elements.append(Spacer(1, 12))
            # Summary table as a row, only include specified non-zero entries
            summary_labels = []
            summary_values = []
            for key, display_text in [
                ('rt_day_hours_label', "Regular Day Hours"),
                ('ot_day_hours_label', "OT Day Hours"),
                ('dt_day_hours_label', "2 Day Hours"),
                ('rt_night_hours_label', "Regular Night Hours"),
                ('ot_night_hours_label', "OT Night Hours"),
                ('dt_night_hours_label', "2 Night Hours"),
                ('travel_hours_label', "Travel Hours"),
                ('travel_amount_label', "Travel Amount"),
                ('vacation_pay_label', "Vacation Pay"),
                ('rt_amount_label', "Regular Amount"),
                ('ot_amount_label', "Overtime Amount"),
                ('gross_label', "Total Gross Pay")
            ]:
                value_text = data[key].cget('text')
                # For vacation pay, show if greater than 0 (regardless of other amounts)
                if key == 'vacation_pay_label':
                    if float(value_text.strip('$')) > 0:
                        summary_labels.append(display_text)
                        summary_values.append(value_text)
                # For other fields, show if greater than 0
                elif float(value_text.strip('$')) > 0:
                    summary_labels.append(display_text)
                    summary_values.append(value_text)
            
            # If there's vacation pay but no other amounts, still show the summary
            if not summary_labels and data['vacation_pay'] > 0:
                summary_labels.append("Vacation Pay")
                summary_values.append(f"${data['vacation_pay']:.2f}")
            
            # Always show summary if there are any labels or vacation pay
            if summary_labels or data['vacation_pay'] > 0:
                summary_data = [summary_labels, summary_values]
                num_summary_cols = len(summary_labels)
                available_summary_width = 1190 - 60  # A3 landscape width minus margins
                col_width = max(100, available_summary_width / max(num_summary_cols, 1))
                summary_table = Table(summary_data, colWidths=[col_width] * num_summary_cols, rowHeights=[30, 30])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, 1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ]))
                elements.append(Paragraph("Summary", normal_style))
                elements.append(summary_table)

            elements.append(PageBreak())

        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Success", f"PDF generated: {pdf_filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")

for emp in employees:
    create_tab(emp)

root.mainloop()