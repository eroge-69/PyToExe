import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Create main app window
app = tk.Tk()
app.title("PS XT LIVE - PS OPTIMIZATIONS")
app.geometry("800x700")

# Load background image
bg_image = Image.open("84d3782a-56a2-4a8d-9fbf-c06a74ac2a95.png")  # Use your image filename
bg_image = bg_image.resize((800, 700), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a background label
bg_label = tk.Label(app, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Create canvas for scrolling
canvas = tk.Canvas(app, bg='black', highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add scrollbar to canvas
scrollbar = tk.Scrollbar(app, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

# Create frame inside canvas
frame = tk.Frame(canvas, bg='black')
canvas.create_window((0, 0), window=frame, anchor='nw')

# Scroll region update
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", update_scrollregion)

# Heading
heading = tk.Label(frame, text="PS OPTIMIZATIONS", fg='white', bg='black', font=("Arial", 20, "bold"))
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

option_vars = {}

# Create checkboxes
def create_checkboxes(options):
    for option in options:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(frame, text=option, variable=var, fg='white', bg='black', selectcolor='gray', activebackground='black')
        cb.pack(anchor='w', padx=20)
        option_vars[option] = var

# Sections
essential_label = tk.Label(frame, text="Essential Tweaks", fg='white', bg='black', font=("Arial", 16, "bold"))
essential_label.pack(pady=5)
create_checkboxes(essential_options)

advanced_label = tk.Label(frame, text="Advanced Tweaks - CAUTION", fg='red', bg='black', font=("Arial", 16, "bold"))
advanced_label.pack(pady=5)
create_checkboxes(advanced_options)

# Buttons
def apply_performance_profile():
    messagebox.showinfo("Action", "Ultimate Performance Profile Activated!")

def remove_performance_profile():
    messagebox.showinfo("Action", "Ultimate Performance Profile Removed!")

btn_activate = tk.Button(frame, text="Add and Activate Ultimate Performance Profile", command=apply_performance_profile, bg='gray', fg='white')
btn_activate.pack(pady=5)

btn_remove = tk.Button(frame, text="Remove Ultimate Performance Profile", command=remove_performance_profile, bg='gray', fg='white')
btn_remove.pack(pady=5)

# Run app
app.mainloop()
