import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()  # Hide the main window
messagebox.showwarning("The Dud", "A simple message with an information icon", parent=root)
root.destroy()  # Clean up
import pymsgbox
pymsgbox.alert('This is an alert!', 'Title')   