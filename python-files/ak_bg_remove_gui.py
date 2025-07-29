import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from rembg import new_session, remove

session = new_session("isnet-general-use")

class BGRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AK BG Remove - Professional Tool")
        self.root.geometry("1100x600")
        self.root.configure(bg="white")

        self.original_images = []
        self.processed_images = []
        self.current_index = 0

        self.setup_ui()

    def setup_ui(self):
        self.left_label = tk.Label(self.root, bg="white", bd=1, relief="solid")
        self.left_label.place(x=10, y=10, width=520, height=520)

        self.right_label = tk.Label(self.root, bg="white", bd=1, relief="solid")
        self.right_label.place(x=570, y=10, width=520, height=520)

        self.open_btn = tk.Button(self.root, text="📁 Open Images", bg="#4CAF50", fg="white", command=self.load_images)
        self.open_btn.place(x=30, y=550, width=120, height=30)

        self.remove_btn = tk.Button(self.root, text="✂ Remove BG", bg="#2196F3", fg="white", command=self.remove_bg)
        self.remove_btn.place(x=170, y=550, width=120, height=30)

        self.save_btn = tk.Button(self.root, text="💾 Save", bg="#FF9800", fg="white", command=self.save_images)
        self.save_btn.place(x=310, y=550, width=100, height=30)

        self.save_as_btn = tk.Button(self.root, text="💾 Save As", bg="#9C27B0", fg="white", command=self.save_as_image)
        self.save_as_btn.place(x=430, y=550, width=100, height=30)

        self.reset_btn = tk.Button(self.root, text="❌ Reset", bg="#F44336", fg="white", command=self.reset_all)
        self.reset_btn.place(x=550, y=550, width=100, height=30)

        self.prev_btn = tk.Button(self.root, text="◀", command=self.prev_image)
        self.prev_btn.place(x=680, y=550, width=30, height=30)

        self.index_label = tk.Label(self.root, text="Image 0 of 0")
        self.index_label.place(x=720, y=550, width=80, height=30)

        self.next_btn = tk.Button(self.root, text="▶", command=self.next_image)
        self.next_btn.place(x=810, y=550, width=30, height=30)

        tk.Label(self.root, text="Save Quality").place(x=880, y=550)
        self.quality = ttk.Combobox(self.root, values=["Full", "80", "60"])
        self.quality.set("Full")
        self.quality.place(x=950, y=550, width=100, height=30)

    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not file_paths:
            return
        self.original_images = [Image.open(p).convert("RGBA") for p in file_paths]
        self.image_paths = file_paths
        self.processed_images = [None] * len(self.original_images)
        self.current_index = 0
        self.update_preview()

    def update_preview(self):
        if not self.original_images:
            return
        orig = self.original_images[self.current_index]
        self.display_image(orig, self.left_label)

        proc = self.processed_images[self.current_index]
        if proc:
            self.display_image(proc, self.right_label)
        else:
            self.right_label.config(image="")

        self.index_label.config(text=f"Image {self.current_index+1} of {len(self.original_images)}")

    def display_image(self, pil_image, label):
        w, h = label.winfo_width(), label.winfo_height()
        img = pil_image.copy()
        img.thumbnail((w, h), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        label.image = tk_img
        label.config(image=tk_img)

    def remove_bg(self):
        if not self.original_images:
            return
        for i, img in enumerate(self.original_images):
            np_img = np.array(img)
            result = remove(np_img, session=session)
            self.processed_images[i] = Image.fromarray(result).convert("RGBA")
        self.update_preview()
        messagebox.showinfo("Done", "Background removed successfully!")

    def save_images(self):
        output_folder = os.path.join(os.path.expanduser("~"), "Downloads", "output")
        os.makedirs(output_folder, exist_ok=True)

        for i, img in enumerate(self.processed_images):
            if img:
                quality = self.quality.get()
                file_name = os.path.splitext(os.path.basename(self.image_paths[i]))[0] + "_no_bg.png"
                path = os.path.join(output_folder, file_name)
                img.save(path, format="PNG", optimize=True)

        messagebox.showinfo("Saved", f"Images saved to:\n{output_folder}")

    def save_as_image(self):
        if not self.processed_images[self.current_index]:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not file_path:
            return

        img = self.processed_images[self.current_index]
        img.save(file_path, format="PNG", optimize=True)
        messagebox.showinfo("Saved", f"Saved as:\n{file_path}")

    def reset_all(self):
        self.original_images = []
        self.processed_images = []
        self.current_index = 0
        self.left_label.config(image="")
        self.right_label.config(image="")
        self.index_label.config(text="Image 0 of 0")

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_preview()

    def next_image(self):
        if self.current_index < len(self.original_images) - 1:
            self.current_index += 1
            self.update_preview()

if __name__ == "__main__":
    root = tk.Tk()
    app = BGRemoverApp(root)
    root.mainloop()
