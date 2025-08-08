import customtkinter as ctk
import math

# Set appearance
ctk.set_appearance_mode("Dark")  # Options: "Dark", "Light", "System"
ctk.set_default_color_theme("blue")  # Optional: "blue", "green", "dark-blue"

# Main app window
app = ctk.CTk()
app.title("Modern Scientific Calculator")
app.geometry("400x600")
app.resizable(False, False)

# Entry field
entry = ctk.CTkEntry(app, width=360, height=60, font=("Arial", 24), justify='right')
entry.place(x=20, y=20)

# Insert character to entry
def insert(char):
    entry.insert("end", char)

# Clear entry field
def clear():
    entry.delete(0, "end")

# Evaluate the expression
def calculate():
    try:
        expression = entry.get()
        expression = expression.replace("^", "**").replace("π", str(math.pi)).replace("e", str(math.e))
        result = eval(expression, {"__builtins__": None}, math.__dict__)
        entry.delete(0, "end")
        entry.insert("end", str(result))
    except:
        entry.delete(0, "end")
        entry.insert("end", "Error")

# Buttons and their layout
buttons = [
    ['7', '8', '9', '/', 'C'],
    ['4', '5', '6', '*', '('],
    ['1', '2', '3', '-', ')'],
    ['0', '.', '^', '+', '='],
    ['sin(', 'cos(', 'tan(', 'log(', 'ln('],
    ['√(', 'π', 'e', 'exp(', 'abs(']
]

# Create buttons dynamically
start_y = 100
for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        def action(ch=char):
            if ch == '=':
                calculate()
            elif ch == 'C':
                clear()
            else:
                insert(ch)

        btn = ctk.CTkButton(
            master=app,
            text=char,
            width=60,
            height=50,
            font=("Arial", 18),
            command=action
        )
        btn.place(x=20 + c * 70, y=start_y + r * 60)

# Run the app
app.mainloop()
