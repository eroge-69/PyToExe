import tkinter as tk
import random

# Set window dimensions before using them in move_window
window_width = 300
window_height = 200

root = tk.Tk()
root.title("Fenêtre mobile")


def move_window():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = random.randint(0, screen_width - window_width)
    y = random.randint(0, screen_height - window_height)
    current_x = int(root.winfo_x())
    current_y = int(root.winfo_y())

    # Calculer les nouvelles positions avec une transition douce
    new_x = (x + current_x) // 2
    new_y = (y + current_y) // 2

    root.geometry(f"{window_width}x{window_height}+{new_x}+{new_y}")
    root.after(100, move_window)

move_window()
root.mainloop()