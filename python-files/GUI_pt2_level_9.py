import tkinter as tk
import random

def generate_parameters():
    Root = ["C", "C#/Db", "D" , "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    Pattern9 = ["1", "b2", "2", "b3"]
    Movingin = ["b3", "3", "4", "#4", "5"]

    random.shuffle(Pattern9)
    root_var.set(random.choice(Root))
    position_var.set(str(random.randint(0, 15)))
    pattern_var.set(" ".join(Pattern9))
    movingin_var.set(random.choice(Movingin))

def quit_app():
    root.destroy()

root = tk.Tk()
root.title("Advanced Guitarist - Level: Fragments/Mosaics")

tk.Label(root, text="Advanced Guitar Practice", font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(root, text="Level 9: Weird Groupings", font=("Arial", 12)).pack(pady=2)

frame = tk.Frame(root)
frame.pack(pady=10)

root_var = tk.StringVar()
position_var = tk.StringVar()
pattern_var = tk.StringVar()
movingin_var = tk.StringVar()

tk.Label(frame, text="Root:").grid(row=0, column=0, sticky="e")
tk.Label(frame, textvariable=root_var).grid(row=0, column=1, sticky="w")

tk.Label(frame, text="Position:").grid(row=1, column=0, sticky="e")
tk.Label(frame, textvariable=position_var).grid(row=1, column=1, sticky="w")

tk.Label(frame, text="Pattern:").grid(row=2, column=0, sticky="e")
tk.Label(frame, textvariable=pattern_var).grid(row=2, column=1, sticky="w")

tk.Label(frame, text="Moving in:").grid(row=3, column=0, sticky="e")
tk.Label(frame, textvariable=movingin_var).grid(row=3, column=1, sticky="w")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="New Parameters", command=generate_parameters).pack(side="left", padx=5)
tk.Button(button_frame, text="Exit", command=quit_app).pack(side="left", padx=5)

generate_parameters()  # Initial parameters

root.mainloop()