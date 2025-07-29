import tkinter as tk
import time
import threading
import random
import sys

# Duck ASCII Art
DUCK = """
   __
<(o )___
 (  ._>  )
  `----'
"""

# Self-destruct timer (in seconds)
TIMER_SECONDS = 300  # 5 minutes

def walk_duck(canvas, duck_text, width):
    x = 0
    y = 100
    direction = 1
    while True:
        canvas.delete("all")
        canvas.create_text(x, y, text=duck_text, font=("Courier", 16), anchor="nw")
        x += 5 * direction
        if x > width - 150 or x < 0:
            direction *= -1
        time.sleep(0.1)
        canvas.update()

def countdown_to_self_destruct(root):
    time.sleep(TIMER_SECONDS)
    print("💥 Self-destructing now!")
    root.destroy()
    sys.exit()

def main():
    root = tk.Tk()
    root.title("Ducky.exe")
    root.attributes('-topmost', True)
    root.geometry("600x200")
    root.configure(bg='black')

    canvas = tk.Canvas(root, width=600, height=200, bg="black", highlightthickness=0)
    canvas.pack()

    duck_text = DUCK

    # Start duck walking in a separate thread
    duck_thread = threading.Thread(target=walk_duck, args=(canvas, duck_text, 600))
    duck_thread.daemon = True
    duck_thread.start()

    # Start self-destruct countdown
    timer_thread = threading.Thread(target=countdown_to_self_destruct, args=(root,))
    timer_thread.daemon = True
    timer_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()
