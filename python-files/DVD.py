import tkinter as tk
import random

# Create main window
root = tk.Tk()
root.title("Warning")
root.overrideredirect(True)  # Remove window borders

# Set message label
label = tk.Label(root, text="Hello", bg="yellow", fg="black", font=("Arial", 16), padx=20, pady=10)
label.pack()

# Set initial position and size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 200
window_height = 100
x = random.randint(0, screen_width - window_width)
y = random.randint(0, screen_height - window_height)
dx, dy = 4, 4  # Speed

def move():
    global x, y, dx, dy
    x += dx
    y += dy

    if x <= 0 or x + window_width >= screen_width:
        dx *= -1
    if y <= 0 or y + window_height >= screen_height:
        dy *= -1

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.after(10, move)

# Close on ESC key press
def close_on_esc(event):
    root.destroy()

root.bind("<Escape>", close_on_esc)

root.geometry(f"{window_width}x{window_height}+{x}+{y}")
move()
root.mainloop()
