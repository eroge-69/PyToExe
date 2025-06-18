import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter
import numpy as np
from skimage.measure import label  # ← ersetzt scipy.ndimage

class ImageAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Binärbild Analyse")
        self.master.geometry("1000x700")
        self.master.minsize(900, 600)

        self.original_image = None
        self.processed_image = None
        self.tk_image = None
        self.loaded_filename = ""

        controls_frame = tk.Frame(master)
        controls_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        right_frame = tk.Frame(master)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(0, weight=1)

        row = 0
        self.btn_load = tk.Button(controls_frame, text="Bild laden", command=self.load_image)
        self.btn_load.grid(row=row, column=0, columnspan=3, pady=(0,10), sticky="ew")
        row += 1

        def create_slider(text, var, frm, row, from_, to_, resolution=1):
            label = tk.Label(frm, text=text)
            label.grid(row=row, column=0, sticky="w", pady=5)
            scale = tk.Scale(frm, from_=from_, to=to_, orient=tk.HORIZONTAL, variable=var,
                             resolution=resolution, showvalue=True, command=self.update_preview)
            scale.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

        self.threshold_var = tk.IntVar(value=128)
        create_slider("Threshold", self.threshold_var, controls_frame, row, 0, 255, 1)
        row += 1

        self.blur_radius_var = tk.DoubleVar(value=0.0)
        create_slider("Gauß-Filter (Radius zur Glättung)", self.blur_radius_var, controls_frame, row, 0.0, 5.0, 0.1)
        row += 1

        self.pos_factor_var = tk.DoubleVar(value=1.0)
        create_slider("Faktor zur Wichtung der Flächen", self.pos_factor_var, controls_frame, row, 0.1, 3.0, 0.1)
        row += 1

        self.frag_factor_var = tk.DoubleVar(value=1.0)
        create_slider("Faktor zur Wichtung der Fragmentierung", self.frag_factor_var, controls_frame, row, 0.0, 3.0, 0.1)
        row += 1

        tk.Label(controls_frame, text="Min. Pixelgröße").grid(row=row, column=0, sticky="w", pady=5)
        self.min_pixel_area_var = tk.IntVar(value=3)
        self.spin_min_area = tk.Spinbox(controls_frame, from_=1, to=50,
                                        textvariable=self.min_pixel_area_var,
                                        command=self.update_preview, width=7)
        self.spin_min_area.grid(row=row, column=1, sticky="w")
        row += 1

        self.invert_var = tk.BooleanVar()
        self.invert_check = tk.Checkbutton(controls_frame, text="Dunkle Flächen erkennen",
                                           variable=self.invert_var, command=self.update_preview)
        self.invert_check.grid(row=row, column=0, columnspan=2, pady=5, sticky="w")
        row += 1

        self.overlay_on_original_var = tk.BooleanVar()
        self.overlay_check = tk.Checkbutton(controls_frame, text="Markierung auf Originalbild",
                                            variable=self.overlay_on_original_var, command=self.update_preview)
        self.overlay_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        self.btn_save = tk.Button(controls_frame, text="Bild speichern", command=self.save_processed_image)
        self.btn_save.grid(row=row, column=0, columnspan=3, pady=(10,0), sticky="ew")
        row += 1

        controls_frame.grid_columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(right_frame, bg='black', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.results_frame = tk.Frame(right_frame)
        self.results_frame.grid(row=1, column=0, sticky="ew", pady=10)

        self.image_label = tk.Label(right_frame, text="")
        self.image_label.grid(row=2, column=0, sticky="w")

        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Bilddateien", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)
            self.original_image = img
            self.loaded_filename = path.split("/")[-1]
            self.image_label.config(text=f"Geladenes Bild: {self.loaded_filename}")
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def update_preview(self, _event=None):
        if self.original_image is None:
            return

        threshold = self.threshold_var.get()
        blur_radius = self.blur_radius_var.get()
        pos_factor = self.pos_factor_var.get()
        frag_factor = self.frag_factor_var.get()
        min_pixel_area = self.min_pixel_area_var.get()
        invert = self.invert_var.get()

        gray = self.original_image.convert("L")
        if blur_radius > 0:
            gray = gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        bin_img = gray.point(lambda p: 255 if (p > threshold) != invert else 0)
        bin_array = np.array(bin_img)
        binary = (bin_array == 255).astype(np.uint8)
        image_area = binary.shape[0] * binary.shape[1]
        min_large_area = max(10, int(image_area * 0.002))

        if np.sum(binary) in [0, image_area]:
            total_score = pos_score = frag_penalty = noise_penalty = 0.0
            filtered_num_features = large_regions_count = 0
            highlighted_img = bin_img.convert("RGB")
        else:
            labeled_array = label(binary, connectivity=1)  # angepasst
            sizes = np.bincount(labeled_array.ravel())[1:]
            sizes_filtered = sizes[sizes >= min_pixel_area]

            if sizes_filtered.size == 0:
                total_score = pos_score = frag_penalty = noise_penalty = 0.0
                filtered_num_features = large_regions_count = 0
                highlighted_img = bin_img.convert("RGB")
            else:
                component_sizes = np.bincount(labeled_array.ravel())
                large_region_labels = [i for i, size in enumerate(component_sizes) if size >= min_large_area and i != 0]

                large_regions = [component_sizes[i] for i in large_region_labels]
                small_regions = sizes_filtered[sizes_filtered < min_large_area]

                pos_score = (np.sum(large_regions) / image_area) * 100 * pos_factor
                frag_penalty = (len(small_regions) / max(1, len(sizes_filtered))) * frag_factor
                noise_regions = np.sum(sizes == 1)
                noise_penalty = (noise_regions / max(1, np.sum(sizes_filtered))) * 2.0

                total_score = pos_score - frag_penalty - noise_penalty
                filtered_num_features = len(sizes_filtered)
                large_regions_count = len(large_region_labels)

                if self.overlay_on_original_var.get():
                    base_img = self.original_image.convert("RGBA")
                else:
                    base_img = bin_img.convert("RGBA")

                overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
                overlay_data = np.array(overlay)

                for label_id in large_region_labels:
                    overlay_data[labeled_array == label_id] = [255, 0, 0, 100]

                overlay = Image.fromarray(overlay_data)
                highlighted_img = Image.alpha_composite(base_img, overlay)

        self.processed_image = highlighted_img
        self.display_image()

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        results = [
            ("Score (gesamt)", f"{total_score:.2f}"),
            ("Große Flächen (%) * Faktor (positiv)", f"{pos_score:.2f}"),
            ("Fragmentierung * Faktor (neagtiv)", f"{frag_penalty:.2f}"),
            ("Rauschen (1-Pixel-Flächen) (negativ)", f"{noise_penalty:.2f}"),
            ("Anzahl Flächen ≥ Min Pixelgröße", f"{filtered_num_features}"),
            ("Anzahl große Flächen", f"{large_regions_count}"),
        ]

        for i, (label_text, value_text) in enumerate(results):
            tk.Label(self.results_frame, text=label_text, anchor="w").grid(row=i, column=0, sticky="w")
            tk.Label(self.results_frame, text=value_text, anchor="e").grid(row=i, column=1, sticky="e")

    def display_image(self):
        if self.processed_image is None:
            return
        canvas_w = max(self.canvas.winfo_width(), 10)
        canvas_h = max(self.canvas.winfo_height(), 10)

        img_w, img_h = self.processed_image.size
        scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)
        disp_w, disp_h = int(img_w * scale), int(img_h * scale)

        display_img = self.processed_image.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(display_img)

        self.canvas.delete("all")
        x_center = (canvas_w - disp_w) // 2
        y_center = (canvas_h - disp_h) // 2
        self.canvas.create_image(x_center, y_center, anchor="nw", image=self.tk_image)

    def on_canvas_resize(self, event):
        self.display_image()

    def save_processed_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Nichts zu speichern", "Kein Bild verfügbar zum Speichern.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp"), ("Alle Dateien", "*.*")])
        if path:
            try:
                self.processed_image.convert("RGB").save(path)
                messagebox.showinfo("Gespeichert", f"Bild erfolgreich gespeichert:\n{path}")
            except Exception as e:
                messagebox.showerror("Fehler beim Speichern", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageAnalyzerApp(root)
    root.mainloop()
