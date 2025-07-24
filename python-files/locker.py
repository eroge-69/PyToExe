import tkinter as tk
from tkinter import messagebox

CORRECT_PASSWORD = "letmein"

def try_unlock():
    if password_entry.get() == CORRECT_PASSWORD:
        root.destroy()
    else:
        messagebox.showerror("Fehler", "Falsches Passwort!")

root = tk.Tk()
root.title("Windows Locker")
root.attributes('-fullscreen', True)
root.configure(bg="black")

label = tk.Label(root, text="System gesperrt", fg="white", bg="black", font=("Arial", 32))
label.pack(pady=50)

password_entry = tk.Entry(root, show="*", font=("Arial", 24))
password_entry.pack()

unlock_button = tk.Button(root, text="Entsperren", command=try_unlock, font=("Arial", 18))
unlock_button.pack(pady=20)

def disable_event():
    pass
root.protocol("WM_DELETE_WINDOW", disable_event)
root.bind("<Alt-F4>", lambda e: "break")
root.bind("<Escape>", lambda e: "break")

root.config(cursor="none")

root.mainloop()


