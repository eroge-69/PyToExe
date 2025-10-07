import tkinter as tk
from tkinter import ttk, messagebox

def calculate():
    try:
        value = float(entry_value.get())
        material = material_var.get()
        conversion = conversion_var.get()

        if material == "Copper":
            if conversion == "Meters ➗ X = Lengths":
                result = value / 3
            elif conversion == "Lengths ✖️ X = Meters":
                result = value * 3
            else:
                messagebox.showwarning("Selection Error", "Please choose a conversion type.")
                return

        elif material == "Lagging":
            if conversion == "Meters ➗ X = Lengths":
                result = value / 2
            elif conversion == "Lengths ✖️ X = Meters":
                result = value * 2
            else:
                messagebox.showwarning("Selection Error", "Please choose a conversion type.")
                return
        else:
            messagebox.showwarning("Selection Error", "Please choose a material.")
            return

        result_label.config(text=f"Result: {result:.2f}")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number.")

def reset_fields():
    material_var.set("")
    conversion_var.set("")
    entry_value.delete(0, tk.END)
    result_label.config(text="Result:")

root = tk.Tk()
root.title("Length Calculator")
root.geometry("350x300")
root.resizable(False, False)

tk.Label(root, text="Select Material:").pack(pady=5)
material_var = tk.StringVar()
material_menu = ttk.Combobox(root, textvariable=material_var, state="readonly")
material_menu["values"] = ["Copper", "Lagging"]
material_menu.pack()

tk.Label(root, text="Select Conversion:").pack(pady=5)
conversion_var = tk.StringVar()
conversion_menu = ttk.Combobox(root, textvariable=conversion_var, state="readonly")
conversion_menu["values"] = ["Meters ➗ X = Lengths", "Lengths ✖️ X = Meters"]
conversion_menu.pack()

tk.Label(root, text="Enter Value:").pack(pady=5)
entry_value = tk.Entry(root)
entry_value.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Calculate", width=12, command=calculate).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Reset", width=12, command=reset_fields).grid(row=0, column=1, padx=5)

result_label = tk.Label(root, text="Result:", font=("Arial", 12, "bold"))
result_label.pack(pady=10)

root.mainloop()
