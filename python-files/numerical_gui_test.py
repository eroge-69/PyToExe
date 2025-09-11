import tkinter as tk
from tkinter import scrolledtext, font

# ---------------- Functions ----------------
def clear_all():
    """Clear all input fields and the log/solution box."""
    for i in range(3):
        for j in range(3):
            entries[i][j].delete(0, tk.END)
        const_entries[i].delete(0, tk.END)
    text_area.config(state='normal')
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, "Step-by-step results will appear here...\n")
    text_area.config(state='disabled')
    solution_label.config(text="Final Solution: x = ?, y = ?, z = ?")
    
def validate_number(P):
    """Allow only numbers, decimal point, and minus sign."""
    if P == "" or P == "-" or P == ".":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False

# ---------------- GUI ----------------
root = tk.Tk()
root.title("LU Decomposition (3x3) - GUI Prototype")
root.geometry("1280x720")

vcmd = (root.register(validate_number), "%P")

# Make root window resizable with proportions
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0, minsize=80)


# --- Coefficient Entries (Centered) ---
entries = [[None]*3 for _ in range(3)]
const_entries = [None]*3

label_frame = tk.Frame(root)
label_frame.grid(row=0, column=0, pady=20, sticky="n")

tk.Label(label_frame, text="Enter 3x3 system:", font=("Arial", 14, "bold")).grid(
    row=0, column=0, columnspan=8, pady=(0,10)
)

for i in range(3):
    for j in range(3):
        entries[i][j] = tk.Entry(label_frame, width=10, justify='center',
                                 font=("Consolas", 14), validate="key", validatecommand=vcmd)
        entries[i][j].grid(row=1+i, column=2*j, padx=6, pady=6)
    tk.Label(label_frame, text=" = ", font=("Arial", 14, "bold")).grid(row=1+i, column=6, padx=10)
    const_entries[i] = tk.Entry(label_frame, width=10, justify='center',
                                font=("Consolas", 14), validate="key", validatecommand=vcmd)
    const_entries[i].grid(row=1+i, column=7, pady=6)

# --- Buttons (Centered) ---
btn_frame = tk.Frame(root)
btn_frame.grid(row=1, column=0, pady=10)

btn_font = ("Arial", 14, "bold")

tk.Button(btn_frame, text="Calculate", font=btn_font, width=12, height=2).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Clear", font=btn_font, width=12, height=2, command=clear_all).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="Exit", font=btn_font, width=12, height=2, command=root.quit).grid(row=0, column=2, padx=10)

# --- Result Log Area (fills available space) ---
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 12))
text_area.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
text_area.insert(tk.END, "Step-by-step results will appear here...\n")
text_area.config(state='disabled')

# Make text area expand with window resize
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# --- Final Solution Placeholder (bottom, centered) ---
solution_frame = tk.Frame(root, bg="white", relief="sunken", bd=2)
solution_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

solution_font = font.Font(family="Consolas", size=20, weight="bold")
solution_label = tk.Label(
    solution_frame,
    text="Final Solution: x = ?, y = ?, z = ?",
    font=solution_font,
    fg="darkblue",
    bg="white",
    pady=12
)
solution_label.pack(expand=True)

root.mainloop()
