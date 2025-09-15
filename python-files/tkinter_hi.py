import tkinter as tk

window = tk.Tk()
window.minsize(width=500, height=500)
window.title("Simple TK")
window.config(bg="black", padx=20, pady=20)

hi_label = tk.Label(text="HI", bg="black", fg="white")
hi_label.pack()

window.mainloop()
