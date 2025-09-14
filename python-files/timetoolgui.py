import tkinter as tk
from datetime import datetime
import time
import threading

def update_time(label):
    def refresh():
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            label.config(text=current_time)
            time.sleep(1)
    thread = threading.Thread(target=refresh, daemon=True)
    thread.start()

# Create the main window
root = tk.Tk()
root.title("Date and Time")
root.geometry("250x60")
root.attributes("-topmost", True)  # Always on top
root.resizable(True, True)

# Create and pack the label
time_label = tk.Label(root, font=("Helvetica", 16), fg="black")
time_label.pack(expand=True)

# Start updating the time
update_time(time_label)

# Run the application
root.mainloop()
