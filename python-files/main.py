
import tkinter as tk
from tkinter import messagebox

def submit():
    # Get the values from the form
    name = name_var.get()
    date = date_var.get()

    # Clear previous canvas texts
    canvas.delete("all")
    canvas.create_rectangle(0, 0, 800, 600, fill="white", outline="")

    # Place the text on predetermined coordinates
    # (Adjust x, y as per your real intended “print” position)
    canvas.create_text(100, 100, text=name, anchor="nw", font=("Arial", 12))
    canvas.create_text(100, 140, text=date, anchor="nw", font=("Arial", 12))

def print_page():
    # Export canvas to PostScript (works on Windows & Linux)
    file_name = "output.ps"
    canvas.postscript(file=file_name)
    messagebox.showinfo("Saved", f"Canvas saved as {file_name}.\n"
                                 "Open it and print from any viewer.")

# Main window
root = tk.Tk()
root.title("Form Fill & Print Demo")

# Input frame
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
name_var = tk.StringVar()
tk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1)

tk.Label(frame, text="Date").grid(row=1, column=0, sticky="w")
date_var = tk.StringVar()
tk.Entry(frame, textvariable=date_var, width=30).grid(row=1, column=1)

tk.Button(frame, text="Submit", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Print", command=print_page).grid(row=3, column=0, columnspan=2, pady=10)

# Canvas for output (white area)
canvas = tk.Canvas(root, width=800, height=600, bg="white")
canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
