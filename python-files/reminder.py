import tkinter as tk
import pyautogui

def follow_mouse():
    x, y = pyautogui.position()
    root.geometry(f"+{x+10}+{y+10}")
    root.after(100, follow_mouse)

root = tk.Tk()
root.title("Reminder")
root.overrideredirect(True)
root.attributes("-topmost", True)

label = tk.Label(root, text="Are you working yet?", bg="yellow", fg="black", font=("Arial", 12, "bold"))
label.pack(padx=10, pady=5)

follow_mouse()
root.mainloop()
