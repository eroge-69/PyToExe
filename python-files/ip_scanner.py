import socket
import tkinter as tk
from urllib.request import urlopen

def get_internal_ip():
    """Retrieve the internal (local) IP address."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return f"Error: {str(e)}"

def get_external_ip():
    """Retrieve the external (public) IP address by querying a free API."""
    try:
        with urlopen('https://api.ipify.org', timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)} (Check internet connection)"

# Create the GUI
root = tk.Tk()
root.title("Corsair Solutions IP Scanner")
root.geometry("300x150")  # Set a basic window size

# Labels for IPs
internal_label = tk.Label(root, text=f"Internal IP: {get_internal_ip()}", font=("Arial", 12))
internal_label.pack(pady=10)

external_label = tk.Label(root, text=f"External IP: {get_external_ip()}", font=("Arial", 12))
external_label.pack(pady=10)

# Run the GUI loop
root.mainloop()