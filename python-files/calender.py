import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("AFAF Calculator")
window.geometry("340x500")
window.configure(bg="#000000")
window.resizable(False, False)

# Entry field for displaying input/output
entry = tk.Entry(window,
    font=("bold", 24),
    bd=0,
    bg="#000000",
    fg="#e8ff00",
    justify="left",
    relief="flat"
)
entry.pack(padx=0, pady=20, fill="both", ipady=20)

# Function to add characters
def press(key):
    entry.insert(tk.END, key)

# Function to clear screen
def clear():
    entry.delete(0, tk.END)

# Function to evaluate expression
def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

# Button layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "C", "+"],
    ["="]
]

# Button styling
btn_font = ("Helvetica", 18)
btn_bg = "#e8ff00"
btn_fg = "#000000"
btn_active_bg = "#16a085"

for row in buttons:
    frame = tk.Frame(window, bg="#000000")
    frame.pack(expand=True, fill="both", padx=1, pady=1)

    for btn in row:
        if btn == "=":
            tk.Button(
                frame,
                text=btn,
                font=btn_font,
                bg="#e67e22",
                fg="black",
                activebackground="#d35400",
                bd=0,
                command=calculate
            ).pack(side="left", expand=True, fill="both", padx=5, pady=5)

        elif btn == "C":
            tk.Button(
                frame,
                text=btn,
                font=btn_font,
                bg="white",
                fg="black",
                activebackground="#c0392b",
                bd=0,
                command=clear
            ).pack(side="left", expand=True, fill="both", padx=4, pady=5)

        else:
            tk.Button(
                frame,
                text=btn,
                font=btn_font,
                bg=btn_bg,
                fg=btn_fg,
                activebackground=btn_active_bg,
                bd=0,
                command=lambda b=btn: press(b)
            ).pack(side="left", expand=True, fill="both", padx=5, pady=5)

# Run the app
window.mainloop()
