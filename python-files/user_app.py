import tkinter as tk
from tkinter import ttk, messagebox

# Function to save user data to a text file
def save_user_data():
    first_name = entry_first_name.get().strip()
    last_name = entry_last_name.get().strip()
    employment_status = employment_var.get()

    if not first_name or not last_name:
        messagebox.showwarning("Missing Information", "Please fill in all fields.")
        return

    data_line = f"First Name: {first_name}, Last Name: {last_name}, Employment Status: {employment_status}\n"

    with open("user_data.txt", "a") as file:
        file.write(data_line)

    messagebox.showinfo("Success", "User information saved.")
    entry_first_name.delete(0, tk.END)
    entry_last_name.delete(0, tk.END)
    employment_var.set("Employed")

# Set up the GUI
root = tk.Tk()
root.title("User Information Entry")
root.geometry("300x200")

# Labels and Entries
tk.Label(root, text="First Name:").pack(pady=(10, 0))
entry_first_name = tk.Entry(root)
entry_first_name.pack()

tk.Label(root, text="Last Name:").pack(pady=(10, 0))
entry_last_name = tk.Entry(root)
entry_last_name.pack()

# Dropdown for Employment Status
tk.Label(root, text="Employment Status:").pack(pady=(10, 0))
employment_var = tk.StringVar(value="Employed")
employment_dropdown = ttk.Combobox(root, textvariable=employment_var, values=["Employed", "Unemployed"], state="readonly")
employment_dropdown.pack()

# Save Button
tk.Button(root, text="Save Information", command=save_user_data).pack(pady=20)

root.mainloop()