import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pyperclip
from tkcalendar import DateEntry
from collections import deque

# Default values
FILE_NAME = None  # User will select a file
COLUMNS = ["area_name", "census_block", "governorate", "ownership_type", "parcel_area_sqf",
           "parcel_area_sqm", "parcel_number", "price_per_sqf", "price_per_sqm", "property_type",
           "property_value", "transaction_type", "transfer_year", "transfer_date"]

# Columns that should be saved as numbers
NUMERIC_COLUMNS = ["parcel_area_sqf", "parcel_area_sqm", "parcel_number", 
                   "price_per_sqf", "price_per_sqm", "property_value", "transfer_year"]

# Global variables
selected_transfer_date = None
undo_stack = deque(maxlen=10)  # Stores the last 10 states for undo
redo_stack = deque(maxlen=10)  # Stores the last 10 states for redo


# Function to convert values to numbers where possible
def convert_to_numeric(value):
    try:
        # Remove commas from numbers
        cleaned_value = str(value).replace(',', '')
        # Convert to float first to handle decimals
        num_value = float(cleaned_value)
        # Convert to int if it's a whole number
        return int(num_value) if num_value.is_integer() else num_value
    except (ValueError, TypeError):
        return value


# Function to select an Excel file
def select_file():
    global FILE_NAME
    FILE_NAME = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if FILE_NAME:
        messagebox.showinfo("File Selected", f"Data will be saved in:\n{FILE_NAME}")
        update_last_entries()  # Update the preview after selecting a file


# Load existing data or create a new DataFrame
def load_data():
    if FILE_NAME and FILE_NAME.endswith(".xlsx"):
        try:
            df = pd.read_excel(FILE_NAME)
            # Ensure transfer_date is in datetime format
            if "transfer_date" in df.columns:
                df["transfer_date"] = pd.to_datetime(df["transfer_date"], format="%Y-%m-%d")
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    if FILE_NAME:
        # Convert numeric columns to appropriate types before saving
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(convert_to_numeric)
        df.to_excel(FILE_NAME, index=False)
    else:
        messagebox.showerror("Error", "Please select an Excel file first!")


# Paste data from clipboard
def paste_clipboard():
    raw_data = pyperclip.paste()
    lines = raw_data.strip().split("\n")
    data_dict = {}
    for line in lines:
        key_value = line.split("\t", 1)
        if len(key_value) == 2:
            key, value = key_value
            data_dict[key.strip()] = value.strip()

    for i, col in enumerate(COLUMNS):
        if col != "transfer_date":  # Do not overwrite transfer_date
            entries[i].delete(0, tk.END)
            entries[i].insert(0, data_dict.get(col, ""))


# Save new entry
def save_entry():
    global selected_transfer_date

    if not FILE_NAME:
        messagebox.showerror("Error", "No file selected! Choose an Excel file first.")
        return

    new_data = {col: entries[i].get() for i, col in enumerate(COLUMNS)}

    # Use stored transfer_date
    if selected_transfer_date:
        new_data["transfer_date"] = selected_transfer_date.get()

    # Validate transfer_date format
    try:
        pd.to_datetime(new_data["transfer_date"], format="%Y-%m-%d")
    except:
        messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
        return

    # Save current state for undo
    df = load_data()
    undo_stack.append(df.copy())

    # Add new entry
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    save_data(df)
    update_last_entries()
    messagebox.showinfo("Success", "Data saved successfully!")


# Update last 5 entries
def update_last_entries():
    df = load_data()
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.tail(5).iterrows():
        tree.insert("", tk.END, values=list(row))


# Undo last entry
def undo_last_entry():
    if not undo_stack:
        messagebox.showwarning("Warning", "Nothing to undo!")
        return
    # Save current state for redo
    df = load_data()
    redo_stack.append(df.copy())
    # Restore previous state
    previous_state = undo_stack.pop()
    save_data(previous_state)
    update_last_entries()
    messagebox.showinfo("Undo", "Last action undone!")


# Redo last undone entry
def redo_last_entry():
    if not redo_stack:
        messagebox.showwarning("Warning", "Nothing to redo!")
        return
    # Save current state for undo
    df = load_data()
    undo_stack.append(df.copy())
    # Restore next state
    next_state = redo_stack.pop()
    save_data(next_state)
    update_last_entries()
    messagebox.showinfo("Redo", "Last action redone!")


# Set transfer date
def set_transfer_date():
    global selected_transfer_date
    selected_transfer_date.set(date_picker.get())


# Clear all fields
def clear_all_fields():
    for entry in entries:
        entry.delete(0, tk.END)
    selected_transfer_date.set("")  # Clear the date picker


# Search functionality
def search_entries():
    search_term = simpledialog.askstring("Search", "Enter search term:")
    if search_term:
        df = load_data()
        # Search in all columns
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        for row in tree.get_children():
            tree.delete(row)
        for _, row in filtered_df.iterrows():
            tree.insert("", tk.END, values=list(row))


# Sort Treeview by column
def sort_treeview(col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children("")]
    data.sort(reverse=reverse)
    for index, (_, child) in enumerate(data):
        tree.move(child, "", index)
    tree.heading(col, command=lambda: sort_treeview(col, not reverse))


# Count entries for selected date
def count_entries_for_date():
    selected_date = single_date_picker.get_date()
    if not selected_date:
        messagebox.showwarning("Warning", "Please select a date first!")
        return

    df = load_data()
    if "transfer_date" not in df.columns:
        messagebox.showwarning("Warning", "No transfer_date column found!")
        return

    count = df[df["transfer_date"].astype(str) == str(selected_date)].shape[0]
    messagebox.showinfo("Count", f"Number of entries for {selected_date}: {count}")


# Count entries for date range
def count_entries_for_range():
    start_date = range_start_picker.get_date()
    end_date = range_end_picker.get_date()

    if not start_date or not end_date:
        messagebox.showwarning("Warning", "Please provide both start and end dates!")
        return

    df = load_data()
    if "transfer_date" not in df.columns:
        messagebox.showwarning("Warning", "No transfer_date column found!")
        return

    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        count = df[(df["transfer_date"] >= start_date) & (df["transfer_date"] <= end_date)].shape[0]
        messagebox.showinfo("Count", f"Number of entries between {start_date.date()} and {end_date.date()}: {count}")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")


# Refresh data from Excel
def refresh_data():
    update_last_entries()
    messagebox.showinfo("Refresh", "Data reloaded from Excel file!")


# Remove duplicates from the data
def remove_duplicates():
    if not FILE_NAME:
        messagebox.showerror("Error", "No file selected! Choose an Excel file first.")
        return

    # Load the data
    df = load_data()

    # Check if the DataFrame is empty
    if df.empty:
        messagebox.showwarning("Warning", "No data found in the file!")
        return

    # Save current state for undo
    undo_stack.append(df.copy())

    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    final_count = len(df)

    # Save the updated DataFrame
    save_data(df)

    # Update the Treeview
    update_last_entries()

    # Show a message with the number of duplicates removed
    duplicates_removed = initial_count - final_count
    messagebox.showinfo(
        "Duplicates Removed", 
        f"Removed {duplicates_removed} duplicate(s).\nTotal entries: {final_count}"
    )


# Keyboard shortcuts
def setup_keyboard_shortcuts():
    root.bind("<Control-s>", lambda event: save_entry())
    root.bind("<Control-z>", lambda event: undo_last_entry())
    root.bind("<Control-y>", lambda event: redo_last_entry())
    root.bind("<Control-f>", lambda event: search_entries())
    root.bind("<Control-l>", lambda event: clear_all_fields())


# GUI Setup
root = tk.Tk()
root.title("Aqari Data Collection Portal")
root.geometry("1200x750")  # Increased width to accommodate the dashboard
root.configure(bg="#f0f0f0")  # Light gray background
# Dashboard Frame
contact_frame = tk.Frame(root, bg="#e8f4f8", bd=2, relief=tk.GROOVE)
contact_frame.place(relx=0.01, rely=0.01, relwidth=0.28, relheight=0.18)  # Increased size

# Contact Information Text
contact_text = "For any inquiries or assistance regarding this app, please contact: pankaj.chaudhary@estater.com"
tk.Label(contact_frame, 
         text=contact_text,
         bg="#e8f4f8",
         fg="#2c3e50",
         font=("Arial", 10, "italic"),  # Increased font size
         justify=tk.LEFT,
         wraplength=250,  # Increased wrap length
         padx=10,  # Added horizontal padding
         pady=10).pack(anchor=tk.NW, fill=tk.BOTH, expand=True)  # Added fill and expand
# User Guide Frame
user_guide_frame = tk.Frame(root, bg="#e8f4f8", bd=2, relief=tk.GROOVE)
user_guide_frame.place(relx=0.01, rely=0.20, relwidth=0.28, relheight=0.30)

# User Guide Text
user_guide_text = """📌 User Guide:
 *Select File* - Choose an Excel file to save data.
 *Paste Data* - Copy & paste Transaction Details.
 *Save Entry* - Add a new record to the file.
 *Undo/Redo* - Use Ctrl+Z (Undo), Ctrl+Y (Redo).
 *Search* - Find records by keyword (Ctrl+F).
 *Clear Fields* - Reset input fields (Ctrl+L).
 *Count Entries* - Count records for a specific date/range.
 *Remove Duplicates* - Delete duplicate records.
 *Refresh Data* - Reload the latest Excel data.


 NOTE - Before counting the transactions please click Refresh button.
"""

# Add Text Widget for User Guide
user_guide_text_widget = tk.Text(user_guide_frame, bg="#e8f4f8", fg="#2c3e50", font=("Arial", 10), wrap=tk.WORD)
user_guide_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
user_guide_text_widget.insert(tk.END, user_guide_text)
user_guide_text_widget.config(state=tk.DISABLED) # Make it read-only

# Add Scrollbar
scrollbar = tk.Scrollbar(user_guide_frame, command=user_guide_text_widget.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
user_guide_text_widget.config(yscrollcommand=scrollbar.set)

dashboard_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief=tk.RIDGE)
dashboard_frame.place(relx=0.75, rely=0.05, relwidth=0.23, relheight=0.35)

# Dashboard Title
tk.Label(dashboard_frame, text="Dashboard", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)

# Single Date Picker
single_date_frame = tk.Frame(dashboard_frame, bg="#f0f0f0")
single_date_frame.pack(pady=5)

tk.Label(single_date_frame, text="Select Date:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
single_date_picker = DateEntry(single_date_frame, width=12, background="blue", foreground="white", borderwidth=2, date_pattern="yyyy-MM-dd")
single_date_picker.grid(row=0, column=1, padx=5)

# Button to count entries for selected date
btn_count_date = tk.Button(dashboard_frame, text="Count Entries for Date", command=count_entries_for_date,
                           bg="#0078D7", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, width=20)
btn_count_date.pack(pady=5)

# Range Date Pickers
range_date_frame = tk.Frame(dashboard_frame, bg="#f0f0f0")
range_date_frame.pack(pady=5)

tk.Label(range_date_frame, text="Start Date:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
range_start_picker = DateEntry(range_date_frame, width=12, background="blue", foreground="white", borderwidth=2, date_pattern="yyyy-MM-dd")
range_start_picker.grid(row=0, column=1, padx=5)

tk.Label(range_date_frame, text="End Date:", font=("Arial", 10), bg="#f0f0f0").grid(row=1, column=0, padx=5)
range_end_picker = DateEntry(range_date_frame, width=12, background="blue", foreground="white", borderwidth=2, date_pattern="yyyy-MM-dd")
range_end_picker.grid(row=1, column=1, padx=5)

# Button to count entries for date range
btn_count_range = tk.Button(dashboard_frame, text="Count Entries for Range", command=count_entries_for_range,
                            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, width=20)
btn_count_range.pack(pady=5)

# Refresh Button
btn_refresh = tk.Button(dashboard_frame, text="Refresh Data", command=refresh_data,
                        bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, width=20)
btn_refresh.pack(pady=5)

# Main Frame
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=10)

# Create input fields
entries = []
for i, col in enumerate(COLUMNS):
    tk.Label(frame, text=col, font=("Arial", 10), bg="#f0f0f0").grid(row=i, column=0, sticky="w")
    entry = tk.Entry(frame, width=40)
    entry.grid(row=i, column=1)
    entries.append(entry)

# Transfer Date Picker
selected_transfer_date = tk.StringVar()
date_frame = tk.Frame(root, bg="#f0f0f0")
date_frame.pack(pady=5)

tk.Label(date_frame, text="Select Transfer Date:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
date_picker = DateEntry(date_frame, textvariable=selected_transfer_date, width=12, background="blue",
                        foreground="white", borderwidth=2, date_pattern="yyyy-MM-dd")
date_picker.grid(row=0, column=1, padx=5)
tk.Button(date_frame, text="Set Date", command=set_transfer_date, bg="#0078D7", fg="white", font=("Arial", 10, "bold"),
          padx=10, pady=5).grid(row=0, column=2, padx=5)

# Buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

btn_style = {"font": ("Arial", 10, "bold"), "padx": 10, "pady": 5, "width": 18, "borderwidth": 2}

btn_select = tk.Button(button_frame, text="Select File", command=select_file, bg="#0078D7", fg="white", **btn_style)
btn_select.grid(row=0, column=0, padx=5, pady=5)

btn_paste = tk.Button(button_frame, text="Paste from Clipboard", command=paste_clipboard, bg="#4CAF50", fg="white",
                       **btn_style)
btn_paste.grid(row=0, column=1, padx=5, pady=5)

btn_save = tk.Button(button_frame, text="Save Entry", command=save_entry, bg="#FF9800", fg="white", **btn_style)
btn_save.grid(row=0, column=2, padx=5, pady=5)

btn_undo = tk.Button(button_frame, text="Undo", command=undo_last_entry, bg="#F44336", fg="white", **btn_style)
btn_undo.grid(row=0, column=3, padx=5, pady=5)

btn_redo = tk.Button(button_frame, text="Redo", command=redo_last_entry, bg="#9C27B0", fg="white", **btn_style)
btn_redo.grid(row=1, column=3, padx=5, pady=5)

btn_clear = tk.Button(button_frame, text="Clear All", command=clear_all_fields, bg="#FF5722", fg="white", **btn_style)
btn_clear.grid(row=1, column=0, padx=5, pady=5)

btn_search = tk.Button(button_frame, text="Search", command=search_entries, bg="#673AB7", fg="white", **btn_style)
btn_search.grid(row=1, column=1, padx=5, pady=5)

# Remove Duplicates Button
btn_remove_duplicates = tk.Button(
    button_frame, 
    text="Remove Duplicates", 
    command=remove_duplicates, 
    bg="#E91E63",  # Pink color for distinction
    fg="white", 
    font=("Arial", 10, "bold"), 
    padx=10, 
    pady=5, 
    width=18
)
btn_remove_duplicates.grid(row=1, column=2, padx=5, pady=5)

# Treeview with Horizontal Scrollbar
tree_frame = tk.Frame(root, bg="#f0f0f0")
tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Add a horizontal scrollbar
x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Add a vertical scrollbar
y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create the Treeview
tree = ttk.Treeview(tree_frame, columns=COLUMNS, show="headings", height=5,
                    xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
for col in COLUMNS:
    tree.heading(col, text=col, command=lambda c=col: sort_treeview(c, False))
    tree.column(col, width=100)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure scrollbars
x_scrollbar.config(command=tree.xview)
y_scrollbar.config(command=tree.yview)

# Tooltips
tooltips = {
    btn_select: "Select an Excel file to save data",
    btn_paste: "Paste data from clipboard",
    btn_save: "Save the current entry",
    btn_undo: "Undo the last action",
    btn_redo: "Redo the last undone action",
}
for widget, text in tooltips.items():
    tk.Label(button_frame, text=text, bg="#f0f0f0", fg="#333333", font=("Arial", 8)).grid(row=2, column=0, columnspan=4, pady=5)

# Keyboard shortcuts
setup_keyboard_shortcuts()

update_last_entries()
root.mainloop()