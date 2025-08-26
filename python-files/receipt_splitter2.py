import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import os, time


class ReceiptSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Receipt Splitter - Photoshop Style")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        # ---- GLOBAL DARK THEME ----
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#e0e0e0")
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="#e0e0e0",
                        fieldbackground="#1e1e1e",
                        rowheight=70,
                        font=("Segoe UI", 10))
        style.map("Treeview",
                  background=[("selected", "#0078d7")],
                  foreground=[("selected", "#ffffff")])
        style.configure("TButton",
                        background="#3c3c3c",
                        foreground="#e0e0e0",
                        padding=5)
        style.map("TButton",
                  background=[("active", "#0078d7")],
                  foreground=[("active", "#ffffff")])

        # ---- Toolbar ----
        toolbar = ttk.Frame(root)
        toolbar.pack(side="top", fill="x")
        ttk.Button(toolbar, text="Open Image", command=self.load_image).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Process Selected", command=self.process_selected).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save All", command=self.save_all).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Zoom In (+)", command=lambda: self.zoom(1.25)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Zoom Out (-)", command=lambda: self.zoom(0.8)).pack(side="left", padx=2)

        # ---- Split main window ----
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Canvas
        self.canvas = tk.Canvas(main_frame, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Sidebar
        sidebar = ttk.Frame(main_frame, width=300)
        sidebar.pack(side="right", fill="y")
        ttk.Label(sidebar, text="Crops", font=("Segoe UI", 12, "bold")).pack(pady=5)

        self.tree = ttk.Treeview(sidebar,
                                 columns=("Name","Status"),
                                 show="tree headings",
                                 selectmode="extended")
        self.tree.heading("#0", text="Thumbnail")
        self.tree.heading("Name", text="Filename")
        self.tree.heading("Status", text="Status")
        self.tree.column("#0", width=70, anchor="center", stretch=False)
        self.tree.column("Name", width=160, anchor="w")
        self.tree.column("Status", width=60, anchor="center", stretch=False)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(sidebar, text="Delete Selected", command=self.delete_selected).pack(fill="x", padx=5, pady=5)

        # Status bar
        self.status = ttk.Label(root, text="Ready", anchor="w", relief="sunken")
        self.status.pack(side="bottom", fill="x")

        # State
        self.img = None
        self.display_img = None
        self.tk_img = None
        self.start_x = self.start_y = None
        self.rectangles = []
        self.crops = []  # list of dicts {id, box, img, name, thumb, editor}
        self.scale = 1.0
        self.dpi = (300, 300)

        # Events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.tree.bind("<<TreeviewSelect>>", self.update_highlights)
        self.tree.bind("<Double-1>", self.start_rename)
        self.rename_entry = None

    # ---------------- IMAGE HANDLING ----------------
    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.tif")])
        if not path:
            return
        self.img = Image.open(path)
        self.dpi = self.img.info.get("dpi", (300, 300))
        self.scale = 1.0
        self.rectangles.clear()
        self.crops.clear()
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.show_image()
        self.update_status("Loaded image", reset=True)

    def show_image(self):
        if not self.img:
            return
        w, h = self.img.size
        scaled = self.img.resize((int(w * self.scale), int(h * self.scale)), Image.LANCZOS)
        self.display_img = scaled
        self.tk_img = ImageTk.PhotoImage(scaled)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        selected = set(self.tree.selection())
        for crop in self.crops:
            x1, y1, x2, y2 = crop["box"]
            x1, y1, x2, y2 = [int(v * self.scale) for v in (x1, y1, x2, y2)]
            color = "#0078d7" if crop["id"] in selected else "#888888"
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

        self.update_status("Image refreshed")

    def zoom(self, factor):
        if not self.img:
            return
        self.scale *= factor
        self.show_image()

    def on_scroll(self, event):
        self.zoom(1.1 if event.delta > 0 else 0.9)

    # ---------------- CROP HANDLING ----------------
    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                            outline="#0078d7", width=2)
        self.rectangles.append(rect)

    def on_drag(self, event):
        rect = self.rectangles[-1]
        self.canvas.coords(rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        rect = self.rectangles[-1]
        x1, y1, x2, y2 = [int(v / self.scale) for v in self.canvas.coords(rect)]
        crop_box = (x1, y1, x2, y2)
        cropped_img = self.img.crop(crop_box)
        crop_id = f"crop{len(self.crops)}"
        name = f"receipt_{len(self.crops)+1}"
        thumb = cropped_img.copy()
        thumb.thumbnail((64, 64))
        tk_thumb = ImageTk.PhotoImage(thumb)
        crop_data = {"id": crop_id, "box": crop_box, "img": cropped_img, "name": name,
                     "thumb": tk_thumb, "editor": None, "original": cropped_img.copy()}
        self.crops.append(crop_data)
        self.tree.insert("", "end", iid=crop_id, text="", image=tk_thumb, values=(name, ""))
        self.show_image()
        self.update_status(f"Crop added ({name})")

    def update_highlights(self, event=None):
        self.show_image()

    def start_rename(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if column != "#1":
            return
        x, y, width, height = self.tree.bbox(item, "#1")
        if width == 0 or height == 0:
            return
        value = self.tree.set(item, "Name")
        self.rename_entry = tk.Entry(self.tree, bg="#333333", fg="white", insertbackground="white",
                                     relief="flat", font=("Segoe UI", 10))
        self.rename_entry.place(x=x, y=y, width=width, height=height)
        self.rename_entry.insert(0, value)
        self.rename_entry.focus()
        self.rename_entry.select_range(0, tk.END)

        def finish_rename(event=None):
            new_value = self.rename_entry.get().strip() or value
            self.tree.set(item, "Name", new_value)
            for crop in self.crops:
                if crop["id"] == item:
                    crop["name"] = new_value
            self.rename_entry.destroy()
            self.rename_entry = None

        self.rename_entry.bind("<Return>", finish_rename)
        self.rename_entry.bind("<Escape>", lambda e: self.rename_entry.destroy())
        self.rename_entry.bind("<FocusOut>", finish_rename)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            self.tree.delete(item)
            self.crops = [c for c in self.crops if c["id"] != item]
        self.show_image()
        self.update_status(f"Deleted {len(sel)} crops")

    # ---------------- PROCESSING ----------------
    def process_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            for crop in self.crops:
                if crop["id"] == item:
                    self.open_editor(crop)

    def timestamped_filename(self, base_name):
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return f"{base_name}_{timestamp}.jpg"

    def open_editor(self, crop):
        if crop["editor"] and tk.Toplevel.winfo_exists(crop["editor"]):
            crop["editor"].lift()
            return

        win = tk.Toplevel(self.root)
        win.title(f"Edit {crop['name']}")
        win.geometry("900x700")
        win.configure(bg="#1e1e1e")
        win.transient(self.root)
        crop["editor"] = win

        # Layout
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True)

        # Left preview
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(side="left", fill="both", expand=True)
        canvas = tk.Canvas(preview_frame, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True, side="left")
        v_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
        v_scroll.pack(side="right", fill="y")
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=canvas.xview)
        h_scroll.pack(side="bottom", fill="x")
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Right panel
        side_panel = ttk.Frame(main_frame, width=250)
        side_panel.pack(side="right", fill="y")
        side_panel.pack_propagate(False)

        # Variables
        brightness = tk.DoubleVar(value=1.0)
        contrast = tk.DoubleVar(value=1.0)
        shadows = tk.IntVar(value=0)
        fine_rotation = tk.DoubleVar(value=0.0)
        rotation_angle = [0]  # mutable container for fixed rotation
        zoom_factor = [1.0]

        def apply_adjustments():
            img = crop["original"].copy()
            img = ImageEnhance.Brightness(img).enhance(brightness.get())
            img = ImageEnhance.Contrast(img).enhance(contrast.get())
            if shadows.get() > 0:
                img = ImageOps.autocontrast(img, cutoff=shadows.get())
            angle = fine_rotation.get() + rotation_angle[0]
            if angle != 0:
                img = img.rotate(angle, expand=True, fillcolor="white")
            return img

        def update_preview(*args):
            mod = apply_adjustments()
            w, h = mod.size
            scaled = mod.resize((int(w * zoom_factor[0]), int(h * zoom_factor[0])), Image.LANCZOS)
            tk_mod = ImageTk.PhotoImage(scaled)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=tk_mod)
            canvas.image = tk_mod
            canvas.config(scrollregion=(0, 0, scaled.width, scaled.height))
            self.tree.set(crop["id"], "Status", "Edited")
            crop["adjusted"] = mod

        def on_scroll(event):
            zoom_factor[0] *= 1.1 if event.delta > 0 else 0.9
            update_preview()

        def rotate_fixed(deg):
            rotation_angle[0] += deg
            update_preview()

        def flip_horizontal():
            crop["original"] = crop["original"].transpose(Image.FLIP_LEFT_RIGHT)
            update_preview()

        def flip_vertical():
            crop["original"] = crop["original"].transpose(Image.FLIP_TOP_BOTTOM)
            update_preview()

        def reset_image():
            rotation_angle[0] = 0
            fine_rotation.set(0)
            brightness.set(1.0)
            contrast.set(1.0)
            shadows.set(0)
            crop["original"] = crop["img"].copy()
            update_preview()
            self.tree.set(crop["id"], "Status", "Edited")

        def save_image():
            out_dir = os.path.join(os.path.expanduser("~"), "Documents", "Extracted")
            os.makedirs(out_dir, exist_ok=True)
            final_img = crop.get("adjusted", crop["img"])
            for f in os.listdir(out_dir):
                if f.startswith(crop["name"] + "_") and f.endswith(".jpg"):
                    try: os.remove(os.path.join(out_dir, f))
                    except: pass
            new_name = self.timestamped_filename(crop["name"])
            final_img.save(os.path.join(out_dir, new_name), "JPEG", dpi=self.dpi)
            crop["img"] = final_img
            crop["original"] = final_img.copy()
            thumb = final_img.copy()
            thumb.thumbnail((64, 64))
            crop["thumb"] = ImageTk.PhotoImage(thumb)
            self.tree.item(crop["id"], image=crop["thumb"])
            self.tree.set(crop["id"], "Status", "✓")
            self.update_status(f"Saved {new_name}")

        # Sliders
        for label, var, rng in [
            ("Brightness", brightness, (0.5, 2.0, 0.1)),
            ("Contrast", contrast, (0.5, 2.0, 0.1)),
            ("Shadows/Highlights", shadows, (0, 10, 1)),
        ]:
            ttk.Label(side_panel, text=label).pack(anchor="w", pady=(10, 0))
            tk.Scale(side_panel, from_=rng[0], to=rng[1], resolution=rng[2],
                     orient="horizontal", variable=var,
                     command=update_preview,
                     bg="#2b2b2b", fg="#e0e0e0", highlightthickness=0).pack(fill="x")

        ttk.Label(side_panel, text="Fine Rotation (±15°)").pack(anchor="w", pady=(10, 0))
        tk.Scale(side_panel, from_=-15, to=15, resolution=0.5,
                 orient="horizontal", variable=fine_rotation,
                 command=update_preview,
                 bg="#2b2b2b", fg="#e0e0e0", highlightthickness=0).pack(fill="x")

        # Transform buttons
        btn_frame = ttk.Frame(side_panel)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="⟲ Left 90°", command=lambda: rotate_fixed(-90)).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="⟳ Right 90°", command=lambda: rotate_fixed(90)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="↔ Flip H", command=flip_horizontal).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="↕ Flip V", command=flip_vertical).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Save + Reset row
        bottom_frame = ttk.Frame(side_panel)
        bottom_frame.pack(side="bottom", pady=10, fill="x")
        save_btn = tk.Button(bottom_frame, text="💾 Save", command=save_image,
                             bg="#0078d7", fg="white", relief="flat")
        save_btn.grid(row=0, column=0, padx=5, sticky="ew")
        reset_btn = tk.Button(bottom_frame, text="⟲ Reset", command=reset_image,
                              bg="#555555", fg="white", relief="flat")
        reset_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Events
        canvas.bind("<MouseWheel>", on_scroll)
        update_preview()

    def save_all(self):
        out_dir = os.path.join(os.path.expanduser("~"), "Documents", "Extracted")
        os.makedirs(out_dir, exist_ok=True)
        if not self.crops:
            return
        for crop in self.crops:
            final_img = crop.get("adjusted", crop["img"])
            for f in os.listdir(out_dir):
                if f.startswith(crop["name"] + "_") and f.endswith(".jpg"):
                    try: os.remove(os.path.join(out_dir, f))
                    except: pass
            new_name = self.timestamped_filename(crop["name"])
            final_img.save(os.path.join(out_dir, new_name), "JPEG", dpi=self.dpi)
            thumb = final_img.copy()
            thumb.thumbnail((64, 64))
            crop["thumb"] = ImageTk.PhotoImage(thumb)
            self.tree.item(crop["id"], image=crop["thumb"])
            self.tree.set(crop["id"], "Status", "✓")   # ✅ mark saved
        self.update_status(f"Saved {len(self.crops)} receipts")

    # ---------------- STATUS ----------------
    def update_status(self, action, reset=False):
        zoom = f"Zoom: {int(self.scale*100)}%"
        dpi = f"DPI: {self.dpi[0]}x{self.dpi[1]}"
        crops = f"Crops: {len(self.crops)}"
        msg = f"{zoom} | {dpi} | {crops} | {action}"
        self.status.config(text=msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiptSplitter(root)
    root.mainloop()
