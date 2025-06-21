import tkinter as tk
from tkinter import messagebox

# App window
app = tk.Tk()
app.title("PS XT LIVE - PS OPTIMIZATIONS")
app.geometry("600x700")
app.configure(bg='black')

# Heading
heading = tk.Label(app, text="PS OPTIMIZATIONS", fg='white', bg='black', font=("Arial", 20, "bold"))
heading.pack(pady=10)

# Option lists
essential_options = [
    "Create Restore Point", "Delete Temporary Files", "Disable ConsumerFeatures", "Disable Telemetry",
    "Disable Activity History", "Disable Explorer Automatic Folder Discovery", "Disable GameDVR",
    "Disable Hibernation", "Disable Homegroup", "Disable Location Tracking", "Disable Storage Sense",
    "Disable Wifi-Sense", "Enable End Task With Right Click", "Run Disk Cleanup",
    "Change Windows Terminal default: PowerShell 5 -> PowerShell 7", "Disable Powershell 7 Telemetry",
    "Disable Recall", "Set Hibernation as default (good for laptops)", "Set Services to Manual", "Debloat Edge"
]

advanced_options = [
    "Adobe Network Block", "Adobe Debloat", "Disable IPv6", "Prefer IPv4 over IPv6", "Disable Teredo",
    "Disable Background Apps", "Disable Fullscreen Optimizations", "Disable Microsoft Copilot",
    "Disable Intel IM (vPro LMS)", "Disable Notification Tray/Calendar", "Disable Windows Platform Binary Table (WPBT)",
    "Set Display for Performance", "Set Classic Right-Click Menu", "Set Time to UTC (Dual Boot)", 
    "Remove ALL MS Store Apps - NOT RECOMMENDED", "Remove Microsoft Edge", "Remove Home and Gallery from explorer",
    "Remove OneDrive", "Block Razer Software Installs"
]

# Store checkbox variables
option_vars = {}

# Function to create checkboxes
def create_checkboxes(options, parent):
    for option in options:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(parent, text=option, variable=var, fg='white', bg='black', selectcolor='gray', activebackground='black')
        cb.pack(anchor='w', padx=20)
        option_vars[option] = var

# Essential Tweaks
essential_label = tk.Label(app, text="Essential Tweaks", fg='white', bg='black', font=("Arial", 16, "bold"))
essential_label.pack(pady=5)
create_checkboxes(essential_options, app)

# Advanced Tweaks
advanced_label = tk.Label(app, text="Advanced Tweaks - CAUTION", fg='red', bg='black', font=("Arial", 16, "bold"))
advanced_label.pack(pady=5)
create_checkboxes(advanced_options, app)

# Ultimate Performance Profile Buttons
def apply_performance_profile():
    messagebox.showinfo("Action", "Ultimate Performance Profile Activated!")

def remove_performance_profile():
    messagebox.showinfo("Action", "Ultimate Performance Profile Removed!")

btn_activate = tk.Button(app, text="Add and Activate Ultimate Performance Profile", command=apply_performance_profile, bg='gray', fg='white')
btn_activate.pack(pady=5)

btn_remove = tk.Button(app, text="Remove Ultimate Performance Profile", command=remove_performance_profile, bg='gray', fg='white')
btn_remove.pack(pady=5)

# Run the app
app.mainloop()
