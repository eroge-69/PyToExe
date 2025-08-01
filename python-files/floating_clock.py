
import tkinter as tk
from datetime import datetime
import time
import threading

def update_clock():
    while True:
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p\n%A, %B %d, %Y")
        label.config(text=time_str)
        time.sleep(1)

root = tk.Tk()
root.title("Floating Clock")
root.configure(bg="black")
root.geometry("320x120")
root.attributes("-topmost", True)
root.resizable(True, True)

label = tk.Label(root, font=("Arial", 16), fg="white", bg="black", justify="center")
label.pack(expand=True)

thread = threading.Thread(target=update_clock, daemon=True)
thread.start()

root.mainloop()
