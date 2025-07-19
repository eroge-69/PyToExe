import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from scipy.ndimage import generic_filter, gaussian_filter, distance_transform_edt

class PadAlphaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alpha Padder")
        icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico')
        self.root.iconbitmap(icon_path)
        self.root.configure(bg="#f0f0f0")

        self.img_path = None
        self.orig_img = None
        self.padded_img = None
        self.mask_img = None

        self.radius_var = tk.IntVar(value=3)
        self.blur_sigma_var = tk.DoubleVar(value=3.0)
        self.use_uv_mask = tk.BooleanVar(value=False)

        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True)

        self.load_btn = tk.Button(main_frame, text="Load Image", command=self.load_image, bg="#dfefff")
        self.load_btn.pack(pady=5, fill="x", padx=10)

        canvas_frame = tk.Frame(main_frame, bg="#f0f0f0")
        canvas_frame.pack(fill="both", expand=True)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.columnconfigure(1, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        left_panel = tk.Frame(canvas_frame, bg="#f0f0f0")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        right_panel = tk.Frame(canvas_frame, bg="#f0f0f0")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        self.orig_label = tk.Label(left_panel, text="Original Image", bg="#f0f0f0")
        self.orig_label.pack()
        self.orig_canvas = tk.Canvas(left_panel, bg="gray")
        self.orig_canvas.pack(fill="both", expand=True)

        self.padded_label = tk.Label(right_panel, text="Padded Image (RGB only)", bg="#f0f0f0")
        self.padded_label.pack()
        self.padded_canvas = tk.Canvas(right_panel, bg="gray")
        self.padded_canvas.pack(fill="both", expand=True)

        param_frame = tk.LabelFrame(main_frame, text="Padding Parameters", bg="#f0f0f0")
        param_frame.pack(pady=5, fill="x", padx=10)

        tk.Label(param_frame, text="RGB Averaging Radius:", bg="#f0f0f0", width=22, anchor="w").grid(row=0, column=0, sticky="w")
        self.radius_spin = tk.Spinbox(param_frame, from_=1, to=20, textvariable=self.radius_var, width=5)
        self.radius_spin.grid(row=0, column=1, sticky="w")
        self.radius_spin.bind("<Enter>", lambda e: self.show_tooltip("Neighborhood radius for RGB smoothing"))

        tk.Label(param_frame, text="Alpha Blur Sigma:", bg="#f0f0f0", width=22, anchor="w").grid(row=1, column=0, sticky="w")
        self.sigma_spin = tk.Spinbox(param_frame, from_=0, to=10, increment=0.5, textvariable=self.blur_sigma_var, width=5)
        self.sigma_spin.grid(row=1, column=1, sticky="w")
        self.sigma_spin.bind("<Enter>", lambda e: self.show_tooltip("Smooth transition on alpha edges"))

        self.uv_mask_check = tk.Checkbutton(param_frame, text="Source is UV Texture (use island mask)", variable=self.use_uv_mask, bg="#f0f0f0", command=self.toggle_uv_options)
        self.uv_mask_check.grid(row=2, column=0, columnspan=2, sticky="w")

        self.load_mask_btn = tk.Button(param_frame, text="Load UV Island Mask", command=self.load_mask, state="disabled", bg="#ffe8cc")
        self.load_mask_btn.grid(row=3, column=0, columnspan=2, sticky="w")

        btn_frame = tk.Frame(param_frame, bg="#f0f0f0")
        btn_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)

        preset_btn = tk.Button(btn_frame, text="Auto Set by Resolution", command=self.auto_set_params, bg="#e8ffe8", anchor="w")
        preset_btn.pack(side="left")

        self.tooltip_label = tk.Label(param_frame, text="", fg="gray", bg="#f0f0f0", anchor="w")
        self.tooltip_label.grid(row=5, column=0, columnspan=3, sticky="w")

        self.pad_btn = tk.Button(main_frame, text="Pad Transparent Pixels", command=self.pad_image, state=tk.DISABLED, bg="#ccf0cc")
        self.pad_btn.pack(pady=5, fill="x", padx=10)

        self.orig_canvas.bind("<Configure>", lambda e: self.redraw_canvas_image(self.orig_img.convert("RGB") if self.orig_img else None, self.orig_canvas))
        self.padded_canvas.bind("<Configure>", lambda e: self.redraw_canvas_image(self.padded_img, self.padded_canvas))

    def toggle_uv_options(self):
        if self.use_uv_mask.get():
            self.load_mask_btn.config(state="normal")
        else:
            self.load_mask_btn.config(state="disabled")

    def show_tooltip(self, text):
        self.tooltip_label.config(text=text)

    def auto_set_params(self):
        if self.orig_img:
            w, h = self.orig_img.size
            max_dim = max(w, h)
            radius = max(2, int(max_dim / 512 * 3))
            sigma = round(min(10.0, max(1.0, max_dim / 1024 * 3)), 1)
            self.radius_var.set(radius)
            self.blur_sigma_var.set(sigma)
            self.tooltip_label.config(text=f"Auto-set radius={radius}, sigma={sigma}")

    def load_image(self):
        filetypes = [("Image files", "*.png *.tga *.tiff *.bmp"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select image", filetypes=filetypes)
        if not path:
            return

        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")
            return

        self.img_path = path
        self.orig_img = img
        self.padded_img = None
        self.redraw_canvas_image(img.convert("RGB"), self.orig_canvas)
        self.padded_canvas.delete("all")

        self.pad_btn.config(state=tk.NORMAL)
        self.auto_set_params()

    def load_mask(self):
        filetypes = [("Mask image", "*.png *.tga *.tiff *.bmp"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select island mask", filetypes=filetypes)
        if not path:
            return
        try:
            img = Image.open(path).convert("L")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open mask image:\n{e}")
            return
        self.mask_img = np.array(img) > 128

    def redraw_canvas_image(self, pil_img, canvas):
        if pil_img is None:
            return
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return

        img_width, img_height = pil_img.size
        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        resized_img = pil_img.resize(new_size, Image.NEAREST)

        tk_img = ImageTk.PhotoImage(resized_img)
        canvas.delete("all")
        x = (canvas_width - new_size[0]) // 2
        y = (canvas_height - new_size[1]) // 2
        canvas.create_image(x, y, anchor="nw", image=tk_img)
        canvas.image = tk_img

    def smooth_pad(self, data, mask, radius=3):
        weight_mask = mask.astype(np.float32)
        output = data.copy()
        for c in range(3):
            channel = data[:, :, c].astype(np.float32)
            sum_c = generic_filter(channel * weight_mask, np.sum, size=2*radius+1, mode='constant', cval=0.0)
            sum_w = generic_filter(weight_mask, np.sum, size=2*radius+1, mode='constant', cval=0.0)
            avg_c = np.divide(sum_c, sum_w, out=np.zeros_like(sum_c), where=sum_w > 0)
            output[:, :, c][~mask] = avg_c[~mask]
        return output.astype(np.uint8)

    def flood_fill_pad(self, data, mask):
        inverse_mask = ~mask
        if not np.any(inverse_mask):
            return data
        h, w = inverse_mask.shape
        result = data.copy()
        indices = np.indices((h, w))
        dist, (i_idx, j_idx) = distance_transform_edt(inverse_mask, return_indices=True)
        for c in range(3):
            result[:, :, c][inverse_mask] = data[i_idx, j_idx, c][inverse_mask]
        return result

    def pad_image(self):
        if self.orig_img is None or self.img_path is None:
            messagebox.showwarning("Warning", "Load an image first.")
            return

        data = np.array(self.orig_img)
        h, w = data.shape[:2]

        if self.use_uv_mask.get():
            if self.mask_img is None or self.mask_img.shape != (h, w):
                messagebox.showerror("Error", "Invalid or missing UV island mask.")
                return
            mask = self.mask_img
        else:
            alpha = data[:, :, 3]
            if np.all(alpha == 255):
                messagebox.showinfo("Info", "Image has no transparency. Nothing to pad.")
                return
            mask = alpha == 255
            data[alpha < 255, :3] = 0

        radius = self.radius_var.get()
        padded_data = self.smooth_pad(data, mask, radius=radius)
        padded_data = self.flood_fill_pad(padded_data, mask)

        if not self.use_uv_mask.get():
            sigma = self.blur_sigma_var.get()
            alpha = data[:, :, 3].astype(np.float32)
            fade_mask = (alpha < 255).astype(np.float32)
            distance = gaussian_filter(1 - fade_mask, sigma=sigma)
            normalized = np.clip((distance - distance.min()) / (distance.max() - distance.min()), 0, 1)
            faded_alpha = np.maximum(alpha, normalized * 255).astype(np.uint8)
            padded_data[:, :, 3] = faded_alpha
        else:
            padded_data = np.concatenate([padded_data[:, :, :3], np.full((h, w, 1), 255, dtype=np.uint8)], axis=2)

        self.padded_img = Image.fromarray(padded_data[:, :, :3], mode="RGB")
        self.redraw_canvas_image(self.padded_img, self.padded_canvas)
        full_rgba_img = Image.fromarray(padded_data, mode="RGBA")
        base, ext = os.path.splitext(self.img_path)
        save_path = base + "_padded.tga"
        try:
            full_rgba_img.save(save_path)
            messagebox.showinfo("Success", f"Padded image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save padded image:\n{e}")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = PadAlphaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
