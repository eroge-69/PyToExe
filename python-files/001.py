import tkinter as tk

print("starting...")
# Function to evaluate the expression
def evaluate_expression(expression):
    try:
        result = eval(expression)
        entry_var.set(result)
    except Exception as e:
        entry_var.set("Error")

# Function to update the expression in the entry field
def update_expression(value):
    current_text = entry_var.get()
    entry_var.set(current_text + str(value))

# Function to clear the entry field
def clear_entry():
    entry_var.set("")

# Create the main window
root = tk.Tk()
root.title("calculator")

# Variable to hold the expression
entry_var = tk.StringVar()

# Entry widget to display the expression
entry = tk.Entry(root, textvariable=entry_var, font=('Arial', 16), bd=10, insertwidth=2, width=14, borderwidth=4)
entry.grid(row=0, column=0, columnspan=4)

# Buttons for the calculator
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    'C', '0', '=', '+'
]

row_val = 1
col_val = 0

for button in buttons:
    if button == 'C':
        tk.Button(root, text=button, padx=20, pady=20, command=clear_entry).grid(row=row_val, column=col_val)
    elif button == '=':
        tk.Button(root, text=button, padx=20, pady=20, command=lambda: evaluate_expression(entry_var.get())).grid(row=row_val, column=col_val)
    else:
        tk.Button(root, text=button, padx=20, pady=20, command=lambda value=button: update_expression(value)).grid(row=row_val, column=col_val)
    
    col_val += 1
    if col_val > 3:
        col_val = 0
        row_val += 1

# Start the main loop
root.mainloop()
