import tkinter as tk
import random
import sys
import os
import threading
import time
import winsound

# Close only with Ctrl+Shift+Q
def on_key(event):
    if (event.state & 0x4) and (event.state & 0x1) and event.keysym == 'q':  # Ctrl+Shift+Q
        root.destroy()
        sys.exit()

# Relaunch if closed in any other way
def on_close():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# High-pitched radar-like beeps
def beep_loop():
    while True:
        winsound.Beep(1200, 100)
        time.sleep(0.1)

# Matrix rain effect
def matrix_rain():
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    font_size = 15
    cols = width // font_size
    columns = [0 for _ in range(cols)]

    canvas.pack(fill=tk.BOTH, expand=True)
    label.place(relx=0.5, rely=0.5, anchor='center')

    while True:
        canvas.delete("all")
        for i in range(cols):
            text = random.choice(['0', '1'])
            x = i * font_size
            y = columns[i] * font_size
            canvas.create_text(x, y, text=text, fill='green', font=('Courier', font_size, 'bold'))
            if y > height and random.random() > 0.975:
                columns[i] = 0
            else:
                columns[i] += 1
        canvas.update()
        time.sleep(0.05)

root = tk.Tk()
root.attributes('-fullscreen', True)
root.overrideredirect(True)
root.configure(bg='black')

canvas = tk.Canvas(root, bg='black', highlightthickness=0)
label = tk.Label(root, text='YOU HAVE BEEN HACKED', fg='white', bg='black', font=('Courier', 50, 'bold'))

root.bind_all('<Key>', on_key)
root.protocol("WM_DELETE_WINDOW", on_close)

threading.Thread(target=beep_loop, daemon=True).start()
threading.Thread(target=matrix_rain, daemon=True).start()

root.mainloop()
