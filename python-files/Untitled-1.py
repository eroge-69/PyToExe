import tkinter as tk
import threading
import time
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
on = "i don't have the time to add a indecator for if its on or off idc"
class AutoClicker:
    def __init__(self):
        self.clicking = False
        self.mouse = mouse.Controller()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        if key == keyboard.Key.f5:
            self.clicking = not self.clicking

    def start_clicking(self):
        while getattr(self, 'active', True):
            if self.clicking:
                self.mouse.click(mouse.Button.left)
            time.sleep(0.0000001)
def close_window():
    autoclicker.active = False
    root.destroy()
# Create main window
root = tk.Tk()
root.title("AutoClicker")
root.geometry("500x500")
root.configure(bg="black")
def ha():
    print("ha")
label = tk.Label(
    root,
    text="Press F5 to start/stop autoclicking",
    bg="black",
    fg="white",
    font=("Arial", 12)
)
label.pack(pady=5)
onoroff = tk.Label(
    root,
    text= str(on),
    bg="black",
    fg="white",
    font=("arial",12)
)
onoroff.pack(pady=20)
# Add button
btn = tk.Button(
    root,
    text="quit",
    bg="white",
    fg="black",
    command=close_window
)
btn.pack(pady=10)
img = tk.PhotoImage(file="Downloads\gamedevTeun.png")  # Replace with your PNG file path

# Make the image half as big (divide both width and height by 2)
small_img = img.subsample(3, 3)

png = tk.Label(root, image=small_img)
png.pack()

# Initialize autoclicker
autoclicker = AutoClicker()
autoclicker.active = True
click_thread = threading.Thread(target=autoclicker.start_clicking, daemon=True)
click_thread.start()
root.protocol("WM_DELETE_WINDOW", close_window)
root.mainloop()