import tkinter as tk
from tkinter import messagebox

def show_about():
    messagebox.showinfo(
        "About",
        "Slot Decoder v1.0.0\nAuthor: Shane Williams & ChatGPT"
    )

root = tk.Tk()
root.title("Slot Decoder v1.0.0")
root.geometry("400x250")

about_btn = tk.Button(root, text="About", command=show_about)
about_btn.pack(pady=20)

label = tk.Label(root, text="Slot Decoder Running...", font=("Arial", 14))
label.pack(pady=10)

root.mainloop()
