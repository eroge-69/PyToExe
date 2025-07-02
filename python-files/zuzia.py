import tkinter as tk

def pokaz_napis():
    label.config(text="Kocham Cię Zuzia 💕", font=("Arial", 30))

root = tk.Tk()
root.title("Dla Zuzi")
root.geometry("400x300")
root.configure(bg="white")

label = tk.Label(root, text="❤️", font=("Arial", 100), bg="white", cursor="hand2")
label.pack(expand=True)
label.bind("<Button-1>", lambda e: pokaz_napis())

root.mainloop()