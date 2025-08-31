import tkinter as tk
from tkinter import messagebox
import requests

def main():
    # Create a hidden root window for tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Show a message box
    messagebox.showinfo("Message", "Connecting to Google...")

    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Connected to Google successfully!")
        else:
            messagebox.showwarning("Warning", f"Connection failed. Status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    main()
