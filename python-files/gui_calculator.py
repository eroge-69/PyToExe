import tkinter as tk

# Button click handler
def click(button_text):
    current = entry.get()
    if button_text == "=":
        try:
            result = str(eval(current))
            entry.delete(0, tk.END)
            entry.insert(0, result)
        except:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    elif button_text == "C":
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, button_text)

# Set up the window
window = tk.Tk()
window.title("Basic Calculator")
window.geometry("300x400")
window.resizable(False, False)

# Entry field
entry = tk.Entry(window, font=("Arial", 24), borderwidth=2, relief="ridge", justify="right")
entry.pack(fill="both", padx=10, pady=10)

# Button layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", "C", "=", "+"]
]

for row in buttons:
    frame = tk.Frame(window)
    frame.pack(expand=True, fill="both")
    for btn in row:
        button = tk.Button(frame, text=btn, font=("Arial", 18), command=lambda b=btn: click(b))
        button.pack(side="left", expand=True, fill="both", padx=2, pady=2)

# Start the GUI loop
window.mainloop()