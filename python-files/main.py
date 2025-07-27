# main.py

import tkinter as tk
import requests

def get_location():
    try:
        response = requests.get('https://ipinfo.io', timeout=5)
        data = response.json()
        info = (
            f"City: {data.get('city', 'Unknown')}\n"
            f"Region: {data.get('region', 'Unknown')}\n"
            f"Country: {data.get('country', 'Unknown')}\n"
            f"Coordinates: {data.get('loc', 'Unknown')}\n"
            f"IP: {data.get('ip', 'Unknown')}\n"
        )
        
        # Display info in the Text widget
        text_widget.config(state='normal')  # Enable editing to insert text
        text_widget.delete(1.0, tk.END)     # Clear current content
        text_widget.insert(tk.END, info)
        text_widget.config(state='disabled')  # Disable editing but keep selectable
        
        # Save info to file
        with open("location.txt", "w", encoding="utf-8") as f:
            f.write(info)
    except Exception as e:
        error_msg = f"Could not detect location:\n{e}"
        text_widget.config(state='normal')
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, error_msg)
        text_widget.config(state='disabled')

root = tk.Tk()
root.title("oneclick?")
root.geometry("360x220")
root.resizable(0, 0)

# Text widget (multi-line, selectable, copyable)
text_widget = tk.Text(root, wrap="word", font=("Arial", 12), bg="white", fg="black", bd=2, relief="sunken")
text_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Disable editing but allow selection
text_widget.config(state='disabled')

# Optional: Add vertical scrollbar
scrollbar = tk.Scrollbar(root, command=text_widget.yview)
scrollbar.grid(row=0, column=1, sticky='ns', pady=10)
text_widget.config(yscrollcommand=scrollbar.set)

# Automatically fetch location on startup
root.after(100, get_location)  # run get_location after 100 ms when app loads

# Configure grid weights for proper resizing (optional)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
