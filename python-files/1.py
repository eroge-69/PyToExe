import tkinter as tk
import time

# Create window
root = tk.Tk()
root.attributes('-fullscreen', True)   # Full screen
root.configure(bg="black")             # Background color

# Display text "1"
label = tk.Label(root, text="1", font=("Arial", 300), fg="white", bg="black")
label.pack(expand=True)

# Update window and wait 1 second
root.update()
time.sleep(1)

# Close window
root.destroy()
