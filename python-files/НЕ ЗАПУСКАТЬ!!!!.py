import tkinter as tk

def fake_bsod():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='blue')

    label = tk.Label(
        root, text="Your PC ran into a problem and needs to restart.\n\n"
                   "We're just collecting some error info, and then we'll restart for you.",
        fg='white', bg='blue', font=("Consolas", 20), justify='left'
    )
    label.pack(padx=100, pady=100, anchor='nw')

    root.bind("<Escape>", lambda e: root.destroy())  # Нажми Esc чтобы выйти
    root.mainloop()

fake_bsod()