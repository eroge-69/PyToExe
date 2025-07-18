import tkinter as tk
from tkinter import messagebox

while True:
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Warning!", "System Erorr!")
    root.destroy()