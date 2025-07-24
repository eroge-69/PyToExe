import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys

class GifViewer(tk.Tk):
    def __init__(self, gif_path):
        super().__init__()
        self.title("GIF Viewer")
        self.gif_path = gif_path
        self.frames = []
        self.load_gif()
        self.label = tk.Label(self)
        self.label.pack()
        self.current_frame = 0
        self.animate()

    def load_gif(self):
        try:
            img = Image.open(self.gif_path)
            for frame in ImageSequence.Iterator(img):
                self.frames.append(ImageTk.PhotoImage(frame))
            self.delay = img.info["duration"]
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # Handle error, maybe display a placeholder image

    def animate(self):
        if self.frames:
            self.label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(self.delay, self.animate) # Use GIF\'s frame duration

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the absolute
        # path to the bundle temporary folder to _MEIPASS.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    gif_file = os.path.join(application_path, "camera_animation.gif")

    app = GifViewer(gif_file)
    app.mainloop()


