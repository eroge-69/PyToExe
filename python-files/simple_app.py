import tkinter as tk
from tkinter import messagebox

def show_message():
    messagebox.showinfo("Hello!", "This is a simple EXE application.")

root = tk.Tk()
root.withdraw()  # Hide the main window
show_message()
