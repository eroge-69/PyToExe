import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTK
import time
import threading

# config file
BTC_ADDRESS = "btc_address"
PASSWORD = "fsociety"
TIMER_SECOND = 30 * 60 # timer

# scareware
class FakeRansomwareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("fsociety")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.bg_colors = ["black"]
        self.current_bg = 0

        self.timer_seconds = TIMER_SECONDS

        # text
        self.label1 = tk.Label(root, text="Yourfiles have been encrypted!", font=("Courier", 32, "bold"))
        self.label2 = tk.Label(root, text=f"Pay 0.5 BTC to this address: {BTC_ADDRESS}", font=("Courier", 24))
        self.timer_label = tk.Label(root, text="", font=("Courier", 20))

        # mask image
        try:
            image = Image.open("mask.png")
            image = image.resize((200, 200))
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(root, image+self.tk_image)
        except Exception as e:
            self.image_label = tk.Label(root, text=" fsociety mask missing ]", font=("Courier", 20, "bold"))

            # textbox for pass
            self.entry = tk.Entry(root, font=("Courier", 20), show="*")
            self.entry.bind("<Return>", self.check_password)

            #pack elements
            self.label1.pack(pady=20)
            self.label2.pack(pady=10)
            self.timer_label.pack(pady=10)
            self.timer_label.pack(pady=10)
            self.image_label.pack(pady=20)
            self.entry.pack(pady=20)

            # flashing background & timer
            self.flash_background()
            self.update_timer()

        def flash_background(self):
            self.current_bg = 1 - self.current_bg
            bg = self.bg_colors[self.current_bg]
            fg = self.bg_colors[1 - self.current_bg]

            self.root.configure(bg=bg)
            for widget in [self.label1, self.lable2, self.timer_label, self.image_label, self.entry]:
                widget.configure(bg=bg, fg=fg)

            self.root.after(500, self.flash_background)

        def update_timer(self):
            mins, secs = divmod(self.timer-seconds, 60)
            self.timer_label.config(text=f"Time remaining: {mins:02}:{secs:02}")
            if self.timer_seconds > 0:
                self.timer_seconds -= 1
                self.root.after(1000, self.update_timer)
            else:
                messagebox.showerror("Time's up", "You ran out of time...")

            def check_password(self, event+None):
                if self.entry.get().strip().lower() == PASSWORD:
                    self.root.destroy()
                else:
                    messagebox.showwarning("Incorrect", "Wrong password")

if __name__ == "__main__":
    root = tk.Tk()
    app = FakeRansomwareApp(root)
    root.mainloop()