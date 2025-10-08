# main.py
import tkinter as tk
from tkinter import messagebox

def create_download_window():
    root = tk.Tk()
    root.title("Download")
    root.geometry("300x200")
    
    # Create a label with "download" text
    label = tk.Label(root, text="download", font=("Arial", 24, "bold"))
    label.pack(expand=True)
    
    # Add a button to close the window
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_download_window()
