import tkinter as tk
from instalocker_helpers import select_category, update_hero_buttons_gui

root = tk.Tk()
root.title("Rivals Locker")

frame_categories = tk.Frame(root)
frame_categories.pack(pady=20)

frame_heroes = tk.Frame(root)
frame_heroes.pack(pady=20)

button_duelist = tk.Button(
    frame_categories,
    text="Duelist",
    command=lambda: select_category("duelist", frame_heroes, root),
)
button_strat = tk.Button(
    frame_categories,
    text="Strat",
    command=lambda: select_category("strat", frame_heroes, root),
)
button_vanguard = tk.Button(
    frame_categories,
    text="Vanguard",
    command=lambda: select_category("vanguard", frame_heroes, root),
)

button_duelist.pack(side=tk.LEFT, padx=10)
button_strat.pack(side=tk.LEFT, padx=10)
button_vanguard.pack(side=tk.LEFT, padx=10)

root.mainloop()
