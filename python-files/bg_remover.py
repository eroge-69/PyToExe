import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Label, OptionMenu, StringVar
from PIL import Image, ImageTk

class BGRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover w/ Dark Mode")

        self.is_dark_mode = True
        self.set_theme()

        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.color_to_remove = StringVar(value="Choose a color")
        self.color_selected = False
        self.image_loaded = False

        self.root.configure(bg=self.bg_color)

        self.label = Label(root, text="Load an image to start", bg=self.bg_color, fg=self.fg_color)
        self.label.pack()

        self.load_btn = self.create_button("Load Image", self.load_image)

        self.color_menu = OptionMenu(root, self.color_to_remove, "white", "black", "red", "green", "blue")
        self.color_menu.pack()
        self._style_option_menu(self.color_menu)

        # THIS is the correct way to monitor dropdown changes
        self.color_to_remove.trace_add("write", self.color_chosen)

        self.remove_btn = self.create_button("Remove Background", self.remove_background)
        self.remove_btn.pack_forget()

        self.save_btn = self.create_button("Save Result", self.save_image)
        self.save_btn.pack_forget()

        self.toggle_btn = self.create_button("Toggle Light/Dark Mode", self.toggle_mode)

        self.canvas = Label(root, bg=self.bg_color)
        self.canvas.pack()

    def set_theme(self):
        self.bg_color = "#1e1e1e" if self.is_dark_mode else "#ffffff"
        self.fg_color = "#ffffff" if self.is_dark_mode else "#000000"
        self.button_bg = "#333333" if self.is_dark_mode else "#dddddd"
        self.button_fg = "#ffffff" if self.is_dark_mode else "#000000"

    def create_button(self, text, command):
        btn = Button(self.root, text=text, command=command, bg=self.button_bg, fg=self.button_fg,
                     activebackground="#555" if self.is_dark_mode else "#ccc", activeforeground=self.fg_color)
        btn.pack()
        return btn

    def _style_option_menu(self, option_menu):
        option_menu.configure(bg=self.button_bg, fg=self.button_fg, highlightthickness=0, relief="flat")
        menu = option_menu["menu"]
        menu.configure(bg=self.button_bg, fg=self.button_fg)

    def color_chosen(self, *args):
        color = self.color_to_remove.get()
        self.color_selected = color != "Choose a color"
        self.check_show_remove_btn()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.image_path = path
            self.original_image = cv2.imread(path)
            self.image_loaded = True
            self.processed_image = None
            self.show_image(self.original_image)
            self.label.config(text="Image loaded. Now choose a color to remove.")
            self.save_btn.pack_forget()
            self.check_show_remove_btn()

    def check_show_remove_btn(self):
        if self.image_loaded and self.color_selected:
            self.remove_btn.pack()

    def show_image(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        img_tk = ImageTk.PhotoImage(pil_img)
        self.canvas.imgtk = img_tk
        self.canvas.config(image=img_tk)

    def remove_background(self):
        color = self.color_to_remove.get()
        if not self.original_image.any():
            return

        lower, upper = self.get_color_range(color)
        if lower is None:
            return

        mask = cv2.inRange(self.original_image, lower, upper)
        result = self.apply_transparency(mask)
        self.processed_image = result
        self.show_image(result)
        self.label.config(text=f"Removed background: {color}")
        self.save_btn.pack()

    def apply_transparency(self, mask):
        b, g, r = cv2.split(self.original_image)
        alpha = cv2.bitwise_not(mask)
        result = cv2.merge((b, g, r, alpha))
        return result

    def get_color_range(self, color):
        ranges = {
            "white": ([200, 200, 200], [255, 255, 255]),
            "black": ([0, 0, 0], [60, 60, 60]),
            "red": ([0, 0, 100], [80, 80, 255]),
            "green": ([0, 100, 0], [80, 255, 80]),
            "blue": ([100, 0, 0], [255, 80, 80]),
        }
        if color in ranges:
            low, high = ranges[color]
            return np.array(low), np.array(high)
        return None, None

    def save_image(self):
        if self.processed_image is not None:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if path:
                b, g, r, a = cv2.split(self.processed_image)
                final = cv2.merge((r, g, b, a))
                Image.fromarray(final).save(path)
                self.label.config(text="Image saved!")

    def toggle_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.set_theme()
        self.root.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color, fg=self.fg_color)
        self.canvas.configure(bg=self.bg_color)

        for btn in [self.load_btn, self.remove_btn, self.save_btn, self.toggle_btn]:
            btn.configure(bg=self.button_bg, fg=self.button_fg,
                          activebackground="#555" if self.is_dark_mode else "#ccc",
                          activeforeground=self.fg_color)

        self._style_option_menu(self.color_menu)

if __name__ == "__main__":
    root = Tk()
    app = BGRemoverApp(root)
    root.mainloop()


