import tkinter as tk
from tkinter import messagebox
import random
import threading
import winsound

all_windows = []
spawning = True
time_limit = 15  # Total run time

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.withdraw()

flash_colors = ["red", "yellow", "orange", "white"]
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 180

def play_screech():
    def _play():
        try:
            winsound.PlaySound("screech.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass
    threading.Thread(target=_play, daemon=True).start()

def animate_window(win, flash_widget, dx, dy):
    def move():
        nonlocal dx, dy
        try:
            geo = win.geometry()
            _, pos = geo.split('+', 1)
            x, y = map(int, pos.split('+'))

            if x + dx < 0 or x + WINDOW_WIDTH + dx > screen_width:
                dx = -dx
            if y + dy < 0 or y + WINDOW_HEIGHT + dy > screen_height:
                dy = -dy

            x += dx
            y += dy

            win.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
            flash_widget.configure(bg=random.choice(flash_colors))

            win.after(50, move)
        except:
            pass
    move()

def make_fake_defender_window():
    x = random.randint(0, screen_width - WINDOW_WIDTH)
    y = random.randint(0, screen_height - WINDOW_HEIGHT)

    alert = tk.Toplevel()
    alert.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    alert.title("Windows Defender Alert")
    alert.resizable(False, False)
    alert.configure(bg="white")

    try:
        alert.iconbitmap("C:/Windows/System32/Shell32.dll")
    except:
        pass

    title = tk.Label(alert, text="Threats found", font=("Segoe UI", 16, "bold"), bg="white", fg="#c00000")
    title.pack(pady=(15, 5))

    subtitle = tk.Label(alert, text="Windows Defender has detected 1 potential threat.\nAction is recommended.",
                        font=("Segoe UI", 10), bg="white")
    subtitle.pack()

    divider = tk.Frame(alert, bg="#e5e5e5", height=2)
    divider.pack(fill="x", pady=10)

    button_frame = tk.Frame(alert, bg="white")
    button_frame.pack()

    def on_remove():
        messagebox.showinfo("Windows Defender", "Threat removed successfully.")
        alert.destroy()
        for _ in range(2):
            make_fake_defender_window()

    def on_ignore():
        messagebox.showwarning("Windows Defender", "Threat ignored. Your PC may be at risk.")
        alert.destroy()

    def on_more_info():
        messagebox.showinfo("Threat details", "Name: Trojan:Win32/CheeseFlood\nSeverity: High\nStatus: Active")

    tk.Button(button_frame, text="Remove threat", command=on_remove, bg="#d32f2f", fg="white", font=("Segoe UI", 10, "bold"), width=15).pack(side="left", padx=10)
    tk.Button(button_frame, text="Ignore", command=on_ignore, bg="#eeeeee", font=("Segoe UI", 10), width=10).pack(side="left", padx=10)
    tk.Button(button_frame, text="More info", command=on_more_info, bg="#eeeeee", font=("Segoe UI", 10), width=10).pack(side="left", padx=10)

    dx = random.choice([-5, 5])
    dy = random.choice([-4, 4])

    animate_window(alert, alert, dx, dy)
    all_windows.append(alert)

    play_screech()

    def on_close_attempt():
        for _ in range(2):
            make_fake_defender_window()

    alert.protocol("WM_DELETE_WINDOW", on_close_attempt)

def spawn_loop():
    if not spawning:
        return
    make_fake_defender_window()
    root.after(400, spawn_loop)

def close_all(event=None):
    global spawning
    spawning = False
    for win in all_windows:
        try:
            win.destroy()
        except:
            pass
    all_windows.clear()

def blackout_screen():
    # Main screen blackout
    blackout1 = tk.Toplevel()
    blackout1.attributes("-fullscreen", True)
    blackout1.configure(bg="black")
    blackout1.attributes("-topmost", True)
    blackout1.overrideredirect(True)
    blackout1.config(cursor="none")

    cheese1 = tk.Label(blackout1, text="🧀", font=("Segoe UI Emoji", 24), bg="black", fg="yellow", bd=0)
    cheese1.place(x=0, y=0)

    def follow_mouse1(event):
        cheese1.place(x=event.x, y=event.y)

    blackout1.bind('<Motion>', follow_mouse1)
    blackout1.bind_all("<n>", close_all)

    # Second monitor blackout (adjust resolution and position if needed)
    blackout2 = tk.Toplevel()
    blackout2.geometry("1920x1080+1920+0")  # Example: second monitor to right at 1920x1080
    blackout2.configure(bg="black")
    blackout2.attributes("-topmost", True)
    blackout2.overrideredirect(True)
    blackout2.config(cursor="none")

    cheese2 = tk.Label(blackout2, text="🧀", font=("Segoe UI Emoji", 24), bg="black", fg="yellow", bd=0)
    cheese2.place(x=0, y=0)

    def follow_mouse2(event):
        cheese2.place(x=event.x, y=event.y)

    blackout2.bind('<Motion>', follow_mouse2)
    blackout2.bind_all("<n>", close_all)

def countdown_timer(seconds):
    timer = tk.Toplevel()
    timer.title("Auto Stop")
    timer.geometry("250x100")
    label = tk.Label(timer, text="", font=("Segoe UI", 14))
    label.pack(expand=True)

    def update():
        nonlocal seconds
        if seconds <= 0:
            label.config(text="Stopping chaos...")
            close_all()
            timer.after(1500, timer.destroy)
        elif seconds == 3:
            blackout_screen()
            label.config(text="🧀 CHEESE FINALE...")
        else:
            label.config(text=f"Auto stopping in {seconds} sec")
        seconds -= 1
        timer.after(1000, update)

    update()

def create_cheese_background():
    cheese_bg = tk.Toplevel()
    cheese_bg.title("🧀 CHEESE SYSTEM 🧀")
    cheese_bg.geometry(f"{screen_width}x{screen_height}+0+0")
    cheese_bg.configure(bg="gold")
    cheese_bg.attributes("-fullscreen", True)
    cheese_bg.attributes("-topmost", False)

    label = tk.Label(cheese_bg, text="🧀 CHEESE OS ACTIVE 🧀", font=("Impact", 32), bg="gold", fg="brown")
    label.pack(expand=True)

    cheese_bg.protocol("WM_DELETE_WINDOW", lambda: None)

# START IT ALL
root.bind_all("<n>", close_all)
create_cheese_background()
countdown_timer(time_limit)
root.after(500, spawn_loop)
root.mainloop()
