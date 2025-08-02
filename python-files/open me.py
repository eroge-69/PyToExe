import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

# List of popup messages
messages = [
    "You will be forked 👻", "Why are you clicking me?", "I see you 👀",
    "Something is coming...", "Too late to run!", "The Matrix is real!",
    "Hello... again.", "System overload imminent!", "Where is your firewall?",
    "Don't blink.", "Knock knock.", "Are you scared yet?",
    "Accept your fate.", "Resistance is futile.", "Error 404: Mercy not found.",
    "You started this.", "Hi from the void.", "BOO!", "You summoned me?",
    "This is just the beginning...", "nice loadout", "why did you trust me", "unlucky",
     "where am I?", "hmm, intriguing"
]

TOTAL_POPUPS = 100
BATCH_SIZE = 1

# Create a popup window at a random screen position
def create_popup(root, message):
    popup = tk.Toplevel(root)
    popup.title("Message")
    popup.geometry("200x100")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = random.randint(0, screen_width - 200)
    y = random.randint(0, screen_height - 100)
    popup.geometry(f"200x100+{x}+{y}")

    label = tk.Label(popup, text=message, wraplength=180, justify="center")
    label.pack(expand=True, fill="both")

    # Make the popup always stay on top
    popup.attributes("-topmost", True)
    popup.lift()
    popup.focus_force()

# Function to show popups in batches
def show_popups(root):
    for i in range(0, TOTAL_POPUPS, BATCH_SIZE):
        for _ in range(BATCH_SIZE):
            msg = random.choice(messages)
            create_popup(root, msg)
        root.update()
        time.sleep(1.5)

# Ask the user for permission before showing popups
def ask_permission():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("Permission", "Can I say some things?")
    root.destroy()
    return result

# Main logic
def main():
    if not ask_permission():
        print("Permission denied.")
        return

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Launch popup sequence in a background thread
    threading.Thread(target=show_popups, args=(root,), daemon=True).start()

    # Keep GUI running until user closes all popups manually
    root.mainloop()

if __name__ == "__main__":
    main()
