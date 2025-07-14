from tkinter import Tk, Label

# Create main overlay window
root = Tk()

# Remove window decorations and keep it always on top
root.overrideredirect(True)
root.attributes("-topmost", True)

# Make a specific color (white) fully transparent
root.attributes("-transparentcolor", "white")

# Get screen width and define overlay dimensions
screen_width = root.winfo_screenwidth()
overlay_height = 40  # ~1 cm in height
x_pos = 0
y_pos = 30  # A few pixels below the top edge

# Set window geometry and transparent background
root.geometry(f"{screen_width}x{overlay_height}+{x_pos}+{y_pos}")
root.configure(bg="white")  # This white becomes transparent

# Create a full-width black label with white text
label = Label(
    root,
    text="Hello World",
    font=("Helvetica", 20, "bold"),
    fg="white",
    bg="black",             # Black background strip behind text
    anchor="center",
)
label.pack(fill="both", expand=True)

# Run the application
root.mainloop()