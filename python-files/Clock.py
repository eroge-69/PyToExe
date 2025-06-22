import tkinter as tk
import time

# Function to update the time displayed on the clock
def update_time():
    # Get the current local time
    current_time = time.strftime("%H:%M:%S") # Format: Hour:Minute:Second (24-hour format)
    # Update the text of the clock label
    clock_label.config(text=current_time)
    # Schedule the update_time function to run again after 1000ms (1 second)
    clock_label.after(1000, update_time)

# Create the main application window
app = tk.Tk()
app.title("Digital Clock") # Set the window title

# Make the window non-resizable
app.resizable(False, False)

# Create a label to display the time
# 'font' sets the font family, size, and style
# 'bg' sets the background color
# 'fg' sets the foreground (text) color
clock_label = tk.Label(app, font=("Arial", 80, "bold"), bg="black", fg="cyan")
clock_label.pack(padx=50, pady=20) # Add padding around the label

# Call the update_time function for the first time to display the clock immediately
update_time()

# Start the Tkinter event loop
# This keeps the window open and responsive to events
app.mainloop()
