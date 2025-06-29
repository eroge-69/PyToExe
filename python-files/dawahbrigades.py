import tkinter as tk

# Create the main application window
root = tk.Tk()
root.title("Dawah Brigades")
root.geometry("300x150")  # Width x Height
root.resizable(False, False)

# Add a label with the app name
label = tk.Label(root, text="Dawah Brigades", font=("Helvetica", 18, "bold"))
label.pack(expand=True)

# Start the application
root.mainloop()
