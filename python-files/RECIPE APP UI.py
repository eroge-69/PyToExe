import tkinter as tk
from tkinter import messagebox

# --- Function to calculate ingredients ---
def calculate():
    try:
        x = float(entry_weight.get())

        a = x * 18 / 100
        b = x * 13 / 100
        c = (x * 25 / 100) / 60
        d = x * 18 / 100
        e = x * 26 / 100

        result_text = (
            f"🍞 Flour: {a:.2f} g\n"
            f"🍬 Sugar: {b:.2f} g\n"
            f"🥚 Eggs: {c:.2f}\n"
            f"🧈 Butter: {d:.2f} g\n"
            f"🥛 Condensed Milk: {e:.2f} g"
        )
        label_result.config(text=result_text, fg="#2b2b2b")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number!")

# --- Window Setup ---
root = tk.Tk()
root.title("🎂 Cake Ingredient Calculator")
root.geometry("420x400")
root.resizable(False, False)
root.configure(bg="#fdf6ec")  # Soft cream background

# --- Header ---
title = tk.Label(
    root,
    text="🎂 Cake Ingredient Calculator 🎂",
    font=("Segoe UI", 16, "bold"),
    bg="#fdf6ec",
    fg="#e07a5f",
)
title.pack(pady=15)

# --- Input Section ---
frame_input = tk.Frame(root, bg="#fdf6ec")
frame_input.pack(pady=10)

tk.Label(
    frame_input,
    text="Enter cake weight (grams):",
    font=("Segoe UI", 11),
    bg="#fdf6ec",
    fg="#3d405b"
).pack(side=tk.LEFT, padx=5)

entry_weight = tk.Entry(frame_input, width=10, font=("Segoe UI", 11), justify="center", bg="#fff")
entry_weight.pack(side=tk.LEFT)

# --- Calculate Button ---
btn_calc = tk.Button(
    root,
    text="Calculate",
    font=("Segoe UI", 12, "bold"),
    bg="#81b29a",
    fg="white",
    activebackground="#6a9c89",
    activeforeground="white",
    padx=20,
    pady=5,
    command=calculate
)
btn_calc.pack(pady=15)

# --- Results Display ---
label_result = tk.Label(
    root,
    text="",
    font=("Consolas", 12),
    bg="#fdf6ec",
    justify="left",
)
label_result.pack(pady=20)

# --- Footer ---
footer = tk.Label(
    root,
    text="Made with 💖 in Python",
    font=("Segoe UI", 9, "italic"),
    bg="#fdf6ec",
    fg="#a5a5a5"
)
footer.pack(side="bottom", pady=10)

root.mainloop()
