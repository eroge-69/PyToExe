
import tkinter as tk

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.seconds = 60
        self.label = tk.Label(root, text="", font=("Courier", 60), fg="white", bg="black")
        self.label.pack(expand=True, fill="both")
        root.overrideredirect(True)  # Remove window borders
        root.wm_attributes("-topmost", 1)  # Always on top
        root.geometry("200x100+10+10")  # Small size, top-left corner
        self.update_timer()

    def update_timer(self):
        self.label.config(text=f"{self.seconds:02}")
        self.seconds -= 1
        if self.seconds < 0:
            self.seconds = 59
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
