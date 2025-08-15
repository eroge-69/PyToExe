import tkinter as tk
import time
import random

def popup_spam():
    while True:
        root = tk.Tk()
        root.withdraw()
        
        popup = tk.Toplevel()
        popup.title("Warning")
        
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = random.randint(0, screen_width - 200)
        y = random.randint(0, screen_height - 100)
        popup.geometry(f"200x100+{x}+{y}")
        
        label = tk.Label(popup, text="Don't touch everything!", fg="red", font=("Arial", 10, "bold"))
        label.pack(expand=True)
        
        button = tk.Button(popup, text="OK", command=popup.destroy)
        button.pack()
        
        root.after(200, root.destroy)
        root.mainloop()
        time.sleep(0.1)

popup_spam()
