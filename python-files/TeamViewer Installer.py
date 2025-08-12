import tkinter as tk
import random
import winsound  # Windows sound module

# Play an evil beep
def evil_beep():
    winsound.Beep(random.randint(400, 800), 100)

# Random movement
def move_window(win):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = random.randint(0, screen_width - 250)
    y = random.randint(0, screen_height - 100)
    win.geometry(f"250x100+{x}+{y}")
    win.after(300, lambda: move_window(win))

# Jump away from mouse
def dodge_mouse(event, win):
    evil_beep()
    flash_red(win)
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    new_x = random.randint(0, screen_width - 250)
    new_y = random.randint(0, screen_height - 100)
    win.geometry(f"250x100+{new_x}+{new_y}")

# Flash the window red
def flash_red(win):
    original_color = win.cget("bg")
    win.configure(bg="red")
    win.after(150, lambda: win.configure(bg=original_color))

# Spawn more evil windows
def spawn_window(depth=1):
    win = tk.Toplevel()
    win.title("🔥 SYSTEM ALERT 🔥")
    win.configure(bg="black")

    label = tk.Label(
        win, 
        text=f"INTRUDER DETECTED\nLevel {depth}", 
        font=("Arial", 12, "bold"),
        fg="white", 
        bg="black"
    )
    label.pack(padx=20, pady=20)

    win.bind("<Enter>", lambda e: dodge_mouse(e, win))

    def try_close():
        # Spawn 2 more evil windows
        spawn_window(depth + 1)
        spawn_window(depth + 1)
        evil_beep()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", try_close)
    move_window(win)

root = tk.Tk()
root.withdraw()
spawn_window()

root.mainloop()
