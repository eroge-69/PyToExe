import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import sys

def restart_pc():
    if sys.platform.startswith('win'):
        os.system("shutdown /r /t 0")
    else:
        print("Restart only works on Windows for now.")

def show_main():
    loading_win.destroy()
    answer = messagebox.askquestion("Übernommen!", "Dein PC wurde übernommen!\n\nMöchtest du akzeptieren?")
    if answer == 'yes':
        messagebox.showinfo("Akzeptiert", "Danke für's Akzeptieren! 😈")
    else:
        restart_pc()

def animate_loading():
    dots = ""
    while loading:
        dots += "."
        if len(dots) > 3:
            dots = ""
        loading_label.config(text=f"Lade{dots}")
        time.sleep(0.5)

# Ladebildschirm
loading_win = tk.Tk()
loading_win.title("Zuckerbrot.exe")
loading_win.geometry("300x150")
loading_label = tk.Label(loading_win, text="Lade...", font=("Arial", 20))
loading_label.pack(expand=True)

loading = True
threading.Thread(target=animate_loading, daemon=True).start()

# Nach 5 Sekunden weitermachen
loading_win.after(5000, lambda: [globals().update(loading=False), show_main()])

loading_win.mainloop()
