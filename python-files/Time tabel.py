import tkinter as tk
import random
x = random.randint(100,400)
y = random.randint(100,400)
root = tk.Tk()
label = tk.Label(root, text="Absolute Position")
root.geometry(f"300x200+{x}+{y}")
root.mainloop()