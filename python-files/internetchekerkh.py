import tkinter as tk
import subprocess
import sys

def ping(host):
    """
    Pings a host to check for network connectivity.
    Returns True if successful, False otherwise.
    """
    # Use -n 1 for Windows, -c 1 for macOS/Linux
    param = '-n' if sys.platform.startswith('win') else '-c'
    # Build the command. Add -w to specify timeout (e.g., 1 second).
    # Timeout is in milliseconds for Windows (-w), seconds for Linux/macOS (-W)
    command = ['ping', param, '1', host]
    timeout_param = '-w' if sys.platform.startswith('win') else '-W'
    timeout_value = '1000' if sys.platform.startswith('win') else '1' # 1000 ms or 1 second
    command.extend([timeout_param, timeout_value])

    try:
        # Use subprocess.run for better control and error handling
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        # On Windows, a return code of 0 usually means success.
        # On Linux/macOS, a return code of 0 also means success.
        return result.returncode == 0
    except FileNotFoundError:
        # Ping command not found
        print(f"Error: 'ping' command not found. Make sure it's in your system's PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during ping: {e}")
        return False

def update_status():
    """
    Checks the internet status and updates the label accordingly.
    """
    host_to_ping = "4.2.2.4"  # A reliable DNS server often used for connectivity checks
    if ping(host_to_ping):
        status_label.config(text="وضعیت: آنلاین ✅", fg="green", bg="lightgrey")
    else:
        status_label.config(text="وضعیت: آفلاین ❌", fg="red", bg="lightgrey")
    # Schedule the next check after 1000 milliseconds (1 second)
    root.after(1000, update_status)

# --- Main application setup ---
root = tk.Tk()
root.title("وضعیت اتصال اینترنت")
root.geometry("300x100")
root.resizable(False, False) # Make the window not resizable

# Label to display the status
status_label = tk.Label(root, text="در حال بررسی...", font=("Arial", 14), fg="black", bg="lightgrey", width=20, height=2)
status_label.pack(pady=20) # Add some padding

# Initial call to update status
update_status()

# Start the Tkinter event loop
root.mainloop()
