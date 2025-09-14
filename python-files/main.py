import tkinter as tk
import keyboard

# Starting value
mana = 0

# Update the label when mana changes
def update_label():
    label.config(text=f"LIVE MANA COUNTER : {mana}")

# Increase mana when hotkey pressed
def increase_mana(e=None):
    global mana
    mana += 1
    update_label()

# Decrease mana when hotkey pressed
def decrease_mana(e=None):
    global mana
    mana -= 1
    update_label()

# Reset mana (optional, press 'r')
def reset_mana(e=None):
    global mana
    mana = 0
    update_label()

# Tkinter setup
root = tk.Tk()
root.title("Mana Counter")

# Remove window border & make always on top
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")  # Makes black transparent

# Position at top-left
root.geometry("+10+10")

# Label setup
label = tk.Label(root, text=f"LIVE MANA COUNTER : {mana}", font=("Arial", 30, "bold"), fg="red", bg="black")
label.pack()

update_label()

# Keyboard listeners
keyboard.add_hotkey("f1", increase_mana)  # Press F1 to add +1 mana
keyboard.add_hotkey("f2", decrease_mana)  # Press F2 to subtract -1 mana
keyboard.add_hotkey("f3", reset_mana)      # Press "r" to reset

# Run Tkinter loop
root.mainloop()
