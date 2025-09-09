# bestand: flits.py
import tkinter as tk

# Instellingen
FPS = 20  # hoger = sneller knipperen

root = tk.Tk()
root.attributes("-fullscreen", True)  # fullscreen
root.configure(bg="white")

color_is_white = True

def toggle():
    global color_is_white
    color_is_white = not color_is_white
    root.configure(bg=("white" if color_is_white else "black"))
    root.after(int(1000 / FPS), toggle)

def stop(_event=None):
    root.destroy()

# Stoppen op '3' of ESC
root.bind("<Escape>", stop)
root.bind("3", stop)

# Starten
toggle()
root.mainloop()
