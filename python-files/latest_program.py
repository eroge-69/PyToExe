"""
image_viewer_tk.py
- Single-window image viewer + slideshow (Tkinter + Pillow)
- 3-dots menu on the right (large, visible)
- Image uses COVER behavior (fills whole client area without white bars)
- Always-on-top toggle, Minimize/Restore, Start/Stop Slideshow
- No PyQt5 dependency (safe for auto-py-to-exe)
Requires: pip install pillow
"""

import os
import glob
import itertools
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

SLIDESHOW_DELAY_MS = 2000  # 2 seconds between slides


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("360x300")
        self.root.minsize(220, 160)
        self.root.attributes("-alpha", 0.98)

        # Variables
        self.orig_image = None
        self.tk_image = None
        self.image_paths = []
        self.image_cycle = None
        self.slideshow_running = False
        self.slideshow_after_id = None

        self.always_on_top = tk.BooleanVar(value=False)

        # --- Top bar (only spacer + 3 dots) ---
        self.ribbon = tk.Frame(self.root, bg="#222222", height=36)
        self.ribbon.pack(side="top", fill="x")

        # Spacer
        self.ribbon_spacer = tk.Frame(self.ribbon, bg="#222222")
        self.ribbon_spacer.pack(side="left", expand=True, fill="x")

        # 3-dots button
        self.menubtn = tk.Button(
            self.ribbon, text="⋮", bg="#222222", fg="white",
            font=("Segoe UI", 14), bd=0, activebackground="#333333",
            command=self.open_menu
        )
        self.menubtn.pack(side="right", padx=(0, 6), pady=2)

        # Popup menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Open Image...", command=self.open_image)
        self.menu.add_command(label="Open Folder (Slideshow)...", command=self.open_folder_slideshow)
        self.menu.add_separator()
        self.menu.add_command(label="Start Slideshow", command=self.start_slideshow)
        self.menu.add_command(label="Stop Slideshow", command=self.stop_slideshow)
        self.menu.add_separator()
        self.menu.add_command(label="Minimize", command=self.minimize_window)
        self.menu.add_command(label="Restore", command=self.restore_window)
        self.menu.add_separator()
        self.menu.add_checkbutton(label="Always on Top", variable=self.always_on_top,
                                  command=self.toggle_always_on_top)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.quit)

        # Image area
        self.image_frame = tk.Frame(self.root, bg="black")
        self.image_frame.pack(side="top", fill="both", expand=True)
        self.image_label = tk.Label(self.image_frame, bg="black")
        self.image_label.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.on_configure)
        self.show_placeholder()

    def open_menu(self):
        x = self.menubtn.winfo_rootx()
        y = self.menubtn.winfo_rooty() + self.menubtn.winfo_height()
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                       ("All files", "*.*")]
        )
        if path:
            self.stop_slideshow()
            self.image_paths = [path]
            self.load_image(path)

    def open_folder_slideshow(self):
        folder = filedialog.askdirectory(title="Select folder for slideshow")
        if folder:
            files = []
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"):
                files.extend(glob.glob(os.path.join(folder, ext)))
            files = sorted(files)
            if not files:
                messagebox.showinfo("No images", "No images found in the selected folder.")
                return
            self.image_paths = files
            self.start_slideshow()

    def load_image(self, path_or_pil):
        if isinstance(path_or_pil, str):
            try:
                img = Image.open(path_or_pil).convert("RGBA")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open image:\n{e}")
                return
        else:
            img = path_or_pil
        self.orig_image = img
        self.update_displayed_image()

    def show_placeholder(self):
        placeholder = Image.new("RGBA", (800, 600), (40, 40, 40, 255))
        self.load_image(placeholder)

    def update_displayed_image(self):
        if not self.orig_image:
            return
        w = max(1, self.image_frame.winfo_width())
        h = max(1, self.image_frame.winfo_height())
        iw, ih = self.orig_image.size

        scale = max(w / iw, h / ih)
        new_w = int(iw * scale + 0.5)
        new_h = int(ih * scale + 0.5)
        img_resized = self.orig_image.resize((new_w, new_h), Image.LANCZOS)

        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img_cropped = img_resized.crop((left, top, left + w, top + h))

        self.tk_image = ImageTk.PhotoImage(img_cropped)
        self.image_label.config(image=self.tk_image)

    def on_configure(self, event):
        if event.widget == self.root:
            if hasattr(self, "_after_update_id") and self._after_update_id:
                self.root.after_cancel(self._after_update_id)
            self._after_update_id = self.root.after(80, self.update_displayed_image)

    def start_slideshow(self):
        if not self.image_paths:
            messagebox.showinfo("No images", "Open an image or choose a folder first.")
            return
        self.slideshow_running = True
        self.image_cycle = itertools.cycle(self.image_paths)
        self._slideshow_step()

    def _slideshow_step(self):
        if not self.slideshow_running:
            return
        try:
            next_path = next(self.image_cycle)
            self.load_image(next_path)
        except StopIteration:
            return
        self.slideshow_after_id = self.root.after(SLIDESHOW_DELAY_MS, self._slideshow_step)

    def stop_slideshow(self):
        self.slideshow_running = False
        if self.slideshow_after_id:
            self.root.after_cancel(self.slideshow_after_id)
            self.slideshow_after_id = None

    def minimize_window(self):
        self.root.iconify()

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top.get())


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
