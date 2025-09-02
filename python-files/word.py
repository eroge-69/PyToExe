import tkinter as tk
from tkinter import messagebox
import subprocess

# Function to create a custom popup with custom buttons
def custom_popup_then_open():
    # Create a new top-level window for custom popup
    popup = tk.Toplevel(root)
    popup.title("Opening Scratch")
    
    # Label text for the popup
    label = tk.Label(popup, text="Do you want to open Scratch in Chrome?")
    label.pack(pady=10)
    
    # Custom buttons
    def on_yes():
        # Path to Chrome executable (adjust for your OS)
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        # URL to open
        url = "https://www.scratch.mit.edu"
        
        # Open Chrome tab
        subprocess.Popen([chrome_path, url])
        popup.destroy()  # Close the popup
    
    def on_no():
        print("User chose not to open Scratch.")
        popup.destroy()  # Close the popup

    # Buttons with custom text
    yes_button = tk.Button(popup, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=10, pady=10)
    
    no_button = tk.Button(popup, text="Not right now...", command=on_no)
    no_button.pack(side="right", padx=10, pady=10)

    # Wait until popup is closed
    popup.mainloop()

# Create a root window (hidden)
root = tk.Tk()
root.withdraw()  # Hide main window

# Call the custom popup function
custom_popup_then_open()
