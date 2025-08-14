import tkinter as tk

def update_hex_value():
    """Recalculate the 32-bit hex value from selected checkboxes."""
    value = 0
    for i in range(32):
        if var_list[i].get():  # if checkbox is selected
            value |= (1 << i)
    hex_value.set(f"0x{value:08X}")

# Create main window
root = tk.Tk()
root.title("32-bit Hex Value from Checkboxes")

# Store the state of each checkbox
var_list = [tk.IntVar() for _ in range(32)]

# Create checkboxes in a grid (two rows of 16 for compactness)
for i in range(32):
    cb = tk.Checkbutton(root, text=str(i), variable=var_list[i], command=update_hex_value)
    cb.grid(row=i // 16, column=i % 16, sticky="w")

# StringVar to hold the hex display
hex_value = tk.StringVar(value="0x00000000")

# Label to display hex value
hex_label = tk.Label(root, textvariable=hex_value, font=("Courier", 14))
hex_label.grid(row=2, column=0, columnspan=16, pady=10)

root.mainloop()
