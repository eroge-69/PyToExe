import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import sys

# Get the folder where this script is located
base_path = os.path.dirname(os.path.abspath(__file__))

# Images in the same folder as this script
images = ["boyfriend.png", "giddy.png", "girlfriend.png"]

# Pick a random one
img_path = os.path.join(base_path, random.choice(images))

if not os.path.exists(img_path):
    sys.exit(f"Image not found: {img_path}")

# Load the image
img = Image.open(img_path)

# Resize to 75% of original
new_width = int(img.width * 0.75)
new_height = int(img.height * 0.75)
img = img.resize((new_width, new_height), Image.ANTIALIAS)

# Create the window
root = tk.Tk()
root.title("")

# Convert to Tkinter image
tk_img = ImageTk.PhotoImage(img)

# Display image
label = tk.Label(root, image=tk_img, borderwidth=0, highlightthickness=0)
label.pack()

# Resize window to match new image size
root.geometry(f"{new_width}x{new_height}")

# Disable resizing
root.resizable(False, False)

# Start event loop
root.mainloop()
