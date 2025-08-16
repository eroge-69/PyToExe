import tkinter as tk
from tkinter import ttk, font
import pandas as pd
import os
from tkinter import messagebox

# Huawei color palette
HUAWEI_RED = "#CF0A2C"
HUAWEI_DARK_RED = "#A30822"
HUAWEI_LIGHT_GRAY = "#F5F5F5"
HUAWEI_DARK_GRAY = "#333333"
HUAWEI_WHITE = "#FFFFFF"

excel_file = 'ne_ips.xlsx'
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, excel_file)
except NameError:  # If running in interactive mode without __file__
    excel_path = excel_file

# Load the Excel data
try:
    df = pd.read_excel(excel_path)
    # Get unique NE Names for the dropdown
    ne_names = df['NE Name'].unique().tolist()
except Exception as e:
    # We'll handle the error later in the GUI
    ne_names = []
    error_message = str(e)

# Create the GUI
root = tk.Tk()
root.title("Huawei NodeB Transport Links MML Script Generator")
root.geometry("850x450")
root.configure(bg=HUAWEI_LIGHT_GRAY)

# Set custom icon (if available)
try:
    root.iconbitmap("huawei_logo_icon.ico")  # Place a Huawei icon in the same directory
except:
    pass

# Custom fonts
title_font = font.Font(family="Helvetica", size=16, weight="bold")
label_font = font.Font(family="Helvetica", size=10)
button_font = font.Font(family="Helvetica", size=10, weight="bold")
text_font = font.Font(family="Courier New", size=10)

# Header with Huawei styling
header = tk.Frame(root, bg=HUAWEI_RED, height=60)
header.pack(fill=tk.X, side=tk.TOP)
tk.Label(header, text="Huawei NodeB Transport Links MML Script Generator", 
         font=title_font, bg=HUAWEI_RED, fg=HUAWEI_WHITE).pack(pady=15)

# Main content frame
content = tk.Frame(root, bg=HUAWEI_LIGHT_GRAY, padx=20, pady=20)
content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Label and Combobox
label = tk.Label(content, text="Select NE Name:", 
                 font=label_font, bg=HUAWEI_LIGHT_GRAY, fg=HUAWEI_DARK_GRAY)
label.pack(pady=(0, 10), anchor="w")

combo = ttk.Combobox(content, values=ne_names, width=50)
combo.pack(fill=tk.X, pady=(0, 15))
if ne_names:
    combo.current(0)

# Text area for output (scrollable for multi-line)
text_frame = tk.LabelFrame(content, text="Generated MML Script", 
                           font=label_font, bg=HUAWEI_LIGHT_GRAY, fg=HUAWEI_DARK_GRAY)
text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

text = tk.Text(text_frame, height=10, wrap=tk.WORD, font=text_font,
               bg=HUAWEI_WHITE, fg=HUAWEI_DARK_GRAY, padx=10, pady=10)
text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

scrollbar = tk.Scrollbar(text_frame, command=text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text['yscrollcommand'] = scrollbar.set

# Function to clear text on Combobox selection change
def clear_text(event):
    text.delete(1.0, tk.END)

# Bind the clear_text function to Combobox selection change
combo.bind("<<ComboboxSelected>>", clear_text)

# Function to generate script
def generate_script():
    selected_ne = combo.get()
    if not selected_ne:
        messagebox.showwarning("Selection Required", "Please select an NE from the dropdown")
        return
    
    if not ne_names:  # Handle case where Excel didn't load
        messagebox.showerror("Data Error", "No NE data available. Check Excel file.")
        return
        
    try:
        # Find the row for the selected NE (assuming one record per NE)
        row = df[df['NE Name'] == selected_ne].iloc[0]
        first_ip = row['FIRSTPEERIP']
        second_ip = row['SECONDPEERIP']
        script_text = f"RMV IPPATH: PATHID=0;\n"
        script_text += f"ADD IPPATH: PATHID=0, FIRSTPEERIP={first_ip}, SECONDPEERIP={second_ip};\n"
        script_text += f"ADD IPPATH: PATHID=0, FIRSTPEERIP={second_ip}, SECONDPEERIP={first_ip};"
        text.delete(1.0, tk.END)
        text.insert(tk.END, script_text)
    except Exception as e:
        messagebox.showerror("Generation Error", f"Failed to generate script: {str(e)}")

# Function to copy to clipboard
def copy_to_clipboard():
    script = text.get(1.0, tk.END).strip()
    if not script:
        messagebox.showwarning("Empty Script", "No script to copy. Generate a script first.")
        return
        
    root.clipboard_clear()
    root.clipboard_append(script)
    messagebox.showinfo("Copied", "Script copied to clipboard!")

# Button frame with modern flat design
button_frame = tk.Frame(content, bg=HUAWEI_LIGHT_GRAY)
button_frame.pack(fill=tk.X, pady=(15, 5))

# Create modern flat buttons without rounded corners
generate_btn = tk.Button(button_frame, text="Generate MML", font=button_font,
                         bg=HUAWEI_RED, fg=HUAWEI_WHITE, activebackground=HUAWEI_DARK_RED,
                         relief=tk.FLAT, padx=15, pady=5, command=generate_script)
generate_btn.pack(side=tk.LEFT, padx=(0, 10))

copy_btn = tk.Button(button_frame, text="Copy to Clipboard", font=button_font,
                     bg=HUAWEI_RED, fg=HUAWEI_WHITE, activebackground=HUAWEI_DARK_RED,
                     relief=tk.FLAT, padx=15, pady=5, command=copy_to_clipboard)
copy_btn.pack(side=tk.LEFT)

# Add hover effects
def on_enter(e):
    e.widget['background'] = HUAWEI_DARK_RED

def on_leave(e):
    e.widget['background'] = HUAWEI_RED

generate_btn.bind("<Enter>", on_enter)
generate_btn.bind("<Leave>", on_leave)
copy_btn.bind("<Enter>", on_enter)
copy_btn.bind("<Leave>", on_leave)

# Status bar
if ne_names:
    status_text = f"Loaded {len(ne_names)} NEs from {excel_path}"
else:
    status_text = f"Error loading Excel file: {error_message}"

status_bar = tk.Label(root, text=status_text, 
                     bd=1, relief=tk.SUNKEN, anchor=tk.W,
                     bg=HUAWEI_DARK_GRAY, fg=HUAWEI_WHITE, font=("Arial", 9))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Make the window responsive
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
content.grid_columnconfigure(0, weight=1)

root.mainloop()