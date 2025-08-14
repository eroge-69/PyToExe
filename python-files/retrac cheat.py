import tkinter as tk
import random
import time
import threading

# List of funny and confusing messages
messages = [
    "Error: NIGGER DETECTED. 🤖",
    "Warning: NIGGER DETECTED. 🌟",
    "System Alert: NIGGER DETECTED! 🐱",
    "Oops! KEON IS A KING. 🎹",
    "ERROR: This message will self-destruct in 5 seconds... just kidding. 💥",
    "Whoops! MANNY IS A NONCE? 😂",
    "Alert: DOM IS A PAKI. 🌌"
]

# Function to create the pop-up message
def pop_up_message():
    root = tk.Tk()
    root.title("SYSTEM ALERT ⚠️")
    root.geometry("400x200")
    
    # Choose a random message
    message = random.choice(messages)
    label = tk.Label(root, text=message, font=("Arial", 14), padx=20, pady=40)
    label.pack()

    # Auto close after 5 seconds
    root.after(5000, root.destroy)
    root.mainloop()

# Function to repeatedly open pop-ups
def open_pop_ups():
    for _ in range(10):  # Number of pop-ups
        threading.Thread(target=pop_up_message).start()
        time.sleep(1)  # Wait 1 second between pop-ups

# Start the prank
if __name__ == "__main__":
    open_pop_ups()
