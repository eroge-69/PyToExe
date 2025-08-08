import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Hello Window")
root.geometry("200x100")  # Set the size of the window (width x height)

# Create a label widget
label = tk.Label(root, text="Hello", font=("Arial", 20))
label.pack(pady=20)  # Add the label to the window with some vertical padding

# Run the application
root.mainloop()
