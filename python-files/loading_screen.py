
import tkinter as tk
import threading
import time

def animate_label(label):
    dots = ""
    while True:
        dots += "."
        if len(dots) > 3:
            dots = ""
        label.config(text="Loading" + dots)
        time.sleep(0.5)

root = tk.Tk()
root.title("Loading...")
root.attributes("-fullscreen", True)
root.configure(bg='black')

label = tk.Label(root, text="Loading", font=("Helvetica", 48), fg="white", bg="black")
label.pack(expand=True)

thread = threading.Thread(target=animate_label, args=(label,), daemon=True)
thread.start()

root.mainloop()
