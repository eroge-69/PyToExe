
import tkinter as tk
from PIL import Image, ImageTk

# قائمة مسارات الصور
image_paths = ["image_1.jpg", "image_2.jpg", "image_3.jpg"]

class FullscreenApp:
    def __init__(self, root, images):
        self.root = root
        self.images = images
        self.index = 0

        self.root.attributes('-fullscreen', True)
        self.root.bind("<Button-1>", self.next_image)
        self.label = tk.Label(self.root, image=self.images[self.index])
        self.label.pack(expand=True)

    def next_image(self, event=None):
        self.index += 1
        if self.index < len(self.images):
            self.label.configure(image=self.images[self.index])
        else:
            self.show_exit_screen()

    def show_exit_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = tk.Frame(self.root, bg="white")
        frame.pack(expand=True)
        exit_btn = tk.Button(frame, text="Exit", font=("Arial", 30), command=self.root.destroy)
        again_btn = tk.Button(frame, text="Again", font=("Arial", 30), command=self.restart)
        exit_btn.pack(pady=20)
        again_btn.pack(pady=20)

    def restart(self):
        self.index = 0
        for widget in self.root.winfo_children():
            widget.destroy()
        self.label = tk.Label(self.root, image=self.images[self.index])
        self.label.pack(expand=True)

def main():
    root = tk.Tk()
    images = [ImageTk.PhotoImage(Image.open(path)) for path in image_paths]
    app = FullscreenApp(root, images)
    root.mainloop()

if __name__ == "__main__":
    main()
