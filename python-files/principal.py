import tkinter as tk
from tkinter import ttk # Import ttk in case it's needed for future styling, though not directly used for this label
import subprocess

# Create the main window with larger dimensions
root = tk.Tk()
root.title("Copyright Oldani Carlo Luigi")
root.geometry("400x300")  # Window dimensions

# Add a label above the buttons
# Use a larger and bold font to make it more visible
label_title = tk.Label(root, text="Composition rules of evidence", font=('Arial', 13, 'bold'))
label_title.pack(pady=10) # Add some padding to distance it

# Functions for the buttons
def button_2_Expert():
    # Open the table2experts.py file
    subprocess.Popen(["python", "table2experts.py"])

def button_3_Expert_empty():
    # Open the table3experts_openworld.py file
    subprocess.Popen(["python", "table3experts_openworld.py"])

def button_3_Expert():
    # Open the table3experts.py file
    subprocess.Popen(["python", "table3experts.py"])    

# Create a frame to contain the buttons
frame = tk.Frame(root)
frame.pack(expand=True)

# Create buttons with larger dimensions
pulsante_2_Expert = tk.Button(frame, text="2 Experts", command=button_2_Expert, width=20, height=2)
# Modified the text for the second button to be multi-line and removed the hyphen
pulsante_3_Expert_empty = tk.Button(frame, text="3 Experts\nopen world", command=button_3_Expert_empty, width=20, height=3) # Increased height to accommodate two lines
pulsante_3_Expert = tk.Button(frame, text="3 Experts", command=button_3_Expert, width=20, height=2)

# Position the buttons in the frame, horizontally centered
pulsante_2_Expert.pack(pady=5)
pulsante_3_Expert_empty.pack(pady=5)
pulsante_3_Expert.pack(pady=5)

# Main loop
root.mainloop()
