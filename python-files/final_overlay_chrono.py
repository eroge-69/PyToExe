
import tkinter as tk

seconds = 0
running = False

def update_timer():
    global seconds
    if running:
        seconds += 1
        label.config(text=f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}")
    root.after(1000, update_timer)

def start_timer():
    global running
    running = True

def stop_timer():
    global running
    running = False

def reset_timer():
    global seconds
    seconds = 0
    label.config(text="00:00:00")

root = tk.Tk()
root.title("Overlay Kronometre")
root.geometry("200x70+50+50")
root.attributes('-topmost', True)
root.attributes('-alpha', 0.8)
root.overrideredirect(True)

def start_move(event):
    global x_offset, y_offset
    x_offset = event.x
    y_offset = event.y

def stop_move(event):
    global x_offset, y_offset
    x_offset = None
    y_offset = None

def do_move(event):
    x = root.winfo_pointerx() - x_offset
    y = root.winfo_pointery() - y_offset
    root.geometry(f"+{x}+{y}")

root.bind("<Button-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)

label = tk.Label(root, text="00:00:00", font=("Arial", 18), bg="black", fg="white")
label.pack(fill="both", expand=True)

frame = tk.Frame(root, bg="black")
frame.pack()

tk.Button(frame, text="▶ Başlat", command=start_timer, width=7).pack(side="left")
tk.Button(frame, text="⏸ Durdur", command=stop_timer, width=7).pack(side="left")
tk.Button(frame, text="⏹ Sıfırla", command=reset_timer, width=7).pack(side="left")

update_timer()
root.mainloop()
