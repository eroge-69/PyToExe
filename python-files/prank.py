import tkinter as tk

def exit_app(event):
    root.destroy()

root = tk.Tk()
root.title("Mystery Screen")
root.attributes('-fullscreen', True)
root.configure(bg='black')

label = tk.Label(
    root,
    text="System Override Engaged...\nPress Esc to abort mission.",
    fg="white",
    bg="black",
    font=("Consolas", 24, "bold"),
    justify="center"
)
label.pack(expand=True)

# Bind Esc key to exit
root.bind("<Escape>", exit_app)

# Keep window on top
root.attributes('-topmost', True)

root.mainloop()