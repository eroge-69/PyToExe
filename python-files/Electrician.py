import tkinter as tk
import time
def create_popup():
    root = tk.Tk()
    root.title("Beer man")
    label = tk.Label(root, text="Don't risk it, use a licensed electrician!", padx=20, pady=20)
    label.pack()
    close_button = tk.Button(root, text="Close", command=root.destroy)
    close_button.pack(pady=10)
    root.mainloop()
while True:
    create_popup()
    time.sleep(600)
