import tkinter as tk

# Function to handle button clicks
def click(btn_text):
    if btn_text == "=":
        try:
            result = str(eval(entry.get()))
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    elif btn_text == "C":
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, btn_text)

# Create main window
root = tk.Tk()
root.title("Mohamed Khaled")

# Entry widget
entry = tk.Entry(root, width=16, font=('Arial', 24), bd=4, relief='ridge')
entry.grid(row=0, column=0, columnspan=4, pady=5)

# Buttons
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+',
    'C'
]

# Arrange buttons
row = 1
col = 0
for b in buttons:
    tk.Button(root, text=b, width=5, height=2, font=('Arial', 18),
              command=lambda x=b: click(x)).grid(row=row, column=col, padx=2, pady=2)
    col += 1
    if col > 3:
        col = 0
        row += 1

# Add name under calculator
label = tk.Label(root, text="By Mohammed Khaled (BTEC)", font=('Arial', 12))
label.grid(row=row, column=0, columnspan=4, pady=5)

# Run program
root.mainloop()