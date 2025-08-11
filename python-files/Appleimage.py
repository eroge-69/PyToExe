import tkinter as tk
from PIL import Image, ImageTk  # Pillow for better image handling

# Create the main window
root = tk.Tk()
root.title("Sandwich Display - Yasss")

# Load and resize the image
image = Image.open("apple.png")
width, height = image.size
resized_image = image.resize((int(width * 0.2), int(height * 0.2)))
photo = ImageTk.PhotoImage(resized_image)

# Create a label to hold the image
label = tk.Label(root, image=photo)
label.pack(padx=20, pady=20)
# Ivechangedalot
# Run the app
root.mainloop()
