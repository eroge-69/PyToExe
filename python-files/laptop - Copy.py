import tkinter as tk
from tkinter import ttk, messagebox

# Sample list of available laptop models
laptop_models = ["Dell XPS 13", "MacBook Air", "Lenovo ThinkPad", "HP Spectre", "Asus ZenBook"]

# Booking records (in-memory list)
bookings = []

def book_laptop():
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    model = selected_model.get()

    if not name or not email or model == "Select Model":
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    booking = f"{name} ({email}) - {model}"
    bookings.append(booking)
    listbox_bookings.insert(tk.END, booking)

    # Clear fields
    entry_name.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    selected_model.set("Select Model")
    messagebox.showinfo("Success", "Laptop booked successfully!")

# GUI Setup
root = tk.Tk()
root.title("Laptop Booking Application")
root.geometry("400x450")
root.resizable(False, False)

# Title
title_label = ttk.Label(root, text="Laptop Booking", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

# Name
ttk.Label(root, text="Full Name:").pack(pady=5)
entry_name = ttk.Entry(root, width=40)
entry_name.pack()

# Email
ttk.Label(root, text="Email:").pack(pady=5)
entry_email = ttk.Entry(root, width=40)
entry_email.pack()

# Laptop model selection
ttk.Label(root, text="Laptop Model:").pack(pady=5)
selected_model = tk.StringVar(value="Select Model")
model_menu = ttk.OptionMenu(root, selected_model, "Select Model", *laptop_models)
model_menu.pack()

# Book Button
book_button = ttk.Button(root, text="Book Laptop", command=book_laptop)
book_button.pack(pady=15)

# Booking List
ttk.Label(root, text="Bookings:").pack(pady=5)
listbox_bookings = tk.Listbox(root, width=50, height=10)
listbox_bookings.pack()

# Run the application
root.mainloop()
