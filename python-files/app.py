import tkinter as tk
import random

# Quotes list
quotes = [
    "You're doing great!",
    "Keep going!",
    "Smile, you're awesome!",
    "Coffee first. Then world domination ☕",
    "Make today ridiculously amazing!",
    "Your seriously amazing! Don't worry about anyone else!",
    "bee awesome!",
    "life is like tesco! open 24/7... and always there for you!"
]

# Function to show a random quote
def show_quote():
    chosen = random.choice(quotes)
    label.config(text=chosen)

# Set up window
window = tk.Tk()
window.title("Mood Button")
window.geometry("300x200")

# Add button
button = tk.Button(window, text="Lift Me Up!", command=show_quote)
button.pack(pady=20)

# Add label for quotes
label = tk.Label(window, text="", wraplength=250, font=("Arial", 12))
label.pack(pady=10)

# Run the app
window.mainloop()