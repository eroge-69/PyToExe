import pyautogui
import keyboard
import threading
import tkinter as tk
from tkinter import ttk

# Initialize the main window
root = tk.Tk()
root.title("Auto Clicker")
root.geometry("300x200")

# Global variable to control the clicking state
clicking = False

def click_mouse():
    """Function to click the mouse at the current position."""
    while True:
        if clicking:
            pyautogui.click()
            time.sleep(float(delay_entry.get()))

def toggle_clicking():
    """Function to toggle the clicking state when F1 is pressed."""
    global clicking
    while True:
        if keyboard.is_pressed('F1'):
            clicking = not clicking
            status_label.config(text="Status: Clicking" if clicking else "Status: Stopped")
            time.sleep(0.5)  # Prevent multiple toggles from a single press

# Create GUI components
delay_label = ttk.Label(root, text="Delay (seconds):")
delay_label.pack(pady=5)

delay_entry = ttk.Entry(root)
delay_entry.insert(0, "0.1")  # Default delay
delay_entry.pack(pady=5)

status_label = ttk.Label(root, text="Status: Stopped")
status_label.pack(pady=5)

# Start the clicking thread
click_thread = threading.Thread(target=click_mouse, daemon=True)
click_thread.start()

# Start the toggle thread
toggle_thread = threading.Thread(target=toggle_clicking, daemon=True)
toggle_thread.start()

# Run the Tkinter event loop
root.mainloop()
