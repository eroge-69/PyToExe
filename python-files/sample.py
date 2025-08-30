
import tkinter as tk
from tkinter import messagebox
import time

def show_popups(message="You have been hacked", count=100, interval=0.15):
    root = tk.Tk()
    root.withdraw()  

    for i in range(count):
        messagebox.showinfo(f"H4ck3r ;) {i+1}/{count}", message)
        time.sleep(interval)

    root.destroy()

if __name__ == "__main__":
    show_popups(message=" Y0u H4v3 B33N H4cK3D", count=20, interval=0.1)
