import tkinter as tk
root = tk.Tk()
root.attributes('-fullscreen', True)
label = tk.Label(root, text="Верни ноут хозяину!", font=("Arial", 50))
label.pack(expand=True)
root.mainloop()