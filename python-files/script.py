import tkinter as tk

# Starting mana value
mana = 0

# Update the label
def update_label():
    label.config(text=f"LIVE MANA COUNTER : {mana}")

# Increase / Decrease / Reset functions
def increase_mana(event=None):
    global mana
    mana += 1
    update_label()

def decrease_mana(event=None):
    global mana
    mana -= 1
    update_label()

def reset_mana(event=None):
    global mana
    mana = 0
    update_label()

# Dragging functions
def start_move(event):
    global x_offset, y_offset
    x_offset = event.x
    y_offset = event.y

def do_move(event):
    x = event.x_root - x_offset
    y = event.y_root - y_offset
    root.geometry(f"+{x}+{y}")

# Tkinter setup
root = tk.Tk()
root.title("LIVE MANA COUNTER")
root.overrideredirect(True)           # Remove window borders
root.attributes("-topmost", True)     # Always on top
root.attributes("-transparentcolor", "black")  # Transparent background
root.geometry("+10+10")               # Start top-left

# Label setup
label = tk.Label(root, text=f"LIVE MANA COUNTER : {mana}", font=("Arial", 30, "bold"), fg="red", bg="black")
label.pack()

# Bind keys (window must be focused)
root.bind("<F1>", increase_mana)
root.bind("<F2>", decrease_mana)
root.bind("<F3>", reset_mana)
root.bind("<Escape>", lambda e: root.destroy())  # Esc closes cleanly

# Enable dragging
label.bind("<Button-1>", start_move)
label.bind("<B1-Motion>", do_move)

# Run Tkinter mainloop
try:
    root.mainloop()
except:
    pass  # Prevent red traceback in terminal on exit