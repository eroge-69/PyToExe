import tkinter as tk
from datetime import date

# Define the start date of the "Dictatorship"
start_date = date(2025, 1, 20)
today = date.today()
days_in_office = (today - start_date).days

# Create the message
message = f"Day {days_in_office} of Rump's Dictatorship"

# Create the Tkinter window
root = tk.Tk()
root.title("Daily Message")
root.geometry("300x100")
root.resizable(False, False)

# Center the message in the window
label = tk.Label(root, text=message, font=("Arial", 14), wraplength=280, justify="center")
label.pack(expand=True)

# Run the application
root.mainloop()
