import tkinter as tk
from threading import Timer

# --- SETTINGS ---
MESSAGE = "⏰ Time to take a break!"  # notification text
INTERVAL = 60  # seconds between notifications

# --- FUNCTION TO SHOW THE NOTIFICATION WINDOW ---
def show_notification():
    global window

    # if a window is already open, do nothing
    if 'window' in globals() and window.winfo_exists():
        return

    # create the main window
    window = tk.Tk()
    window.title("Reminder")
    window.geometry("300x100+1000+600")  # width x height + x + y
    window.configure(bg="black")  # background color

    # make sure window stays on top
    window.attributes("-topmost", True)

    # create the label with message
    label = tk.Label(window, text=MESSAGE, fg="white", bg="black", font=("Arial", 14))
    label.pack(pady=10)

    # create the close button
    btn = tk.Button(window, text="Close", command=lambda: window.destroy(), bg="#444", fg="white")
    btn.pack()

    # start the tkinter main loop in a non-blocking way
    window.mainloop()

    # schedule the next notification
    Timer(INTERVAL, show_notification).start()

# --- START FIRST NOTIFICATION IMMEDIATELY ---
show_notification()
