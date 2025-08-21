import tkinter as tk
from tkinter import messagebox

def on_ok():
    name = entry.get()
    messagebox.showinfo("Thank you", f"Hello {name}, we value you!")
    root.destroy()

root = tk.Tk()
root.title("Making sure it’s you")
root.geometry("400x200")

tk.Label(root, text="Thomas LLP", font=("Arial", 16)).pack(pady=10)
tk.Label(root, text="We value you", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text="Your Name").pack()

entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="OK", command=on_ok).pack(pady=10)

root.mainloop()
