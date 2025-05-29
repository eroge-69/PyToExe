import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import time
from datetime import datetime
import io
import os
import ctypes
import sys
import mss
import copy

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def get_bounds_from_layers_sketches_texts(layers, sketch_items, text_layers):
    """Zwraca minimalny prostokąt obejmujący wszystkie warstwy, szkice i teksty."""
    xs, ys, xe, ye = [], [], [], []
    for layer in layers:
        xs.append(layer["x"])
        ys.append(layer["y"])
        xe.append(layer["x"] + layer["image"].width)
        ye.append(layer["y"] + layer["image"].height)
    for item in sketch_items:
        typ, extra, *_ = item
        if typ in ("rectangle", "line"):
            x1, y1, x2, y2 = extra
            xs.extend([x1, x2])
            ys.extend([y1, y2])
            xe.extend([x1, x2])
            ye.extend([y1, y2])
        elif typ in ("pencil", "eraser"):
            for x, y in extra:
                xs.append(x)
                ys.append(y)
                xe.append(x)
                ye.append(y)
    for text_layer in text_layers:
        x, y = text_layer["x"], text_layer["y"]
        w, h = text_layer["w"], text_layer["h"]
        xs.append(x)
        ys.append(y)
        xe.append(x + w)
        ye.append(y + h)
    if xs and ys and xe and ye:
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xe)
        max_y = max(ye)
    else:
        min_x = min_y = 0
        max_x = max_y = 1
    return min_x, min_y, max_x, max_y

class SnippingTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snipping Tool")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.screenshot = None
        self.canvas = None
        self.draw_color = "red"
        self.draw_width = 3
        self.delay_time = 0

        self.layers = []
        self.active_layer = None
        self.layer_drag_data = {"id": None, "x": 0, "y": 0, "offset_x": 0, "offset_y": 0, "dragging": False}

        self.draw_mode = "cursor"
        self.is_drawing = False
        self.last_x = None
        self.last_y = None
        self.temp_shape = None
        self.sketch_points = []

        self.sketch_items = []  # (typ, extra, color, width, tag, [text])
        self.sketch_color = self.draw_color
        self.sketch_width = self.draw_width
        self.sketch_counter = 0

        self.text_entry = None
        self.text_layers = []  # lista tekstów
        self.text_active_idx = None  # indeks aktywnego tekstu

        self.undo_stack = []
        self.redo_stack = []

        self.current_zoom = 1.0

        # For moving rectangles and lines
        self.selected_sketch = None
        self.sketch_drag_offset = (0, 0)

        # For line handles
        self.line_handle_radius = 6
        self.line_handle_drag = None  # (sketch_idx, handle_idx)

        # For resize handles
        self.handle_radius = 7
        self.handle_drag = None  # (typ, idx, handle_idx)

        # For eraser path preview
        self.eraser_path = []
        self.eraser_preview = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.layer_panel = ttk.Frame(main_frame)
        self.layer_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        self.layer_panel.pack_forget()
        self.layer_listbox = tk.Listbox(self.layer_panel, height=20)
        self.layer_listbox.pack(fill=tk.Y, expand=True, padx=5, pady=5)
        btn_up = ttk.Button(self.layer_panel, text="↑", command=self.move_layer_up)
        btn_down = ttk.Button(self.layer_panel, text="↓", command=self.move_layer_down)
        btn_del = ttk.Button(self.layer_panel, text="Usuń", command=self.delete_layer)
        btn_up.pack(fill=tk.X, padx=5, pady=2)
        btn_down.pack(fill=tk.X, padx=5, pady=2)
        btn_del.pack(fill=tk.X, padx=5, pady=2)
        self.layer_listbox.bind("<<ListboxSelect>>", self.select_layer_from_list)

        ttk.Label(self.layer_panel, text="Przezroczystość").pack()
        self.opacity_var = tk.DoubleVar(value=1.0)
        self.opacity_scale = ttk.Scale(self.layer_panel, from_=0, to=1, orient=tk.HORIZONTAL, variable=self.opacity_var, command=self.on_opacity_change)
        self.opacity_scale.pack(fill=tk.X, padx=5, pady=5)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame1 = ttk.Frame(left_frame)
        button_frame1.pack(fill=tk.X, pady=(0, 2))

        ttk.Button(button_frame1, text="Nowy", command=self.new_screenshot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Dodaj warstwę", command=self.add_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Kursor", command=lambda: self.set_draw_mode("cursor")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Ołówek", command=lambda: self.set_draw_mode("pencil")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Prostokąt", command=lambda: self.set_draw_mode("rectangle")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Linia", command=lambda: self.set_draw_mode("line")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Tekst", command=lambda: self.set_draw_mode("text")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Gumka", command=lambda: self.set_draw_mode("eraser")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Kolor", command=self.choose_color).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Kopiuj", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame1, text="Zapisz jako...", command=self.save_image).pack(side=tk.LEFT, padx=(0, 5))

        delay_frame = ttk.Frame(button_frame1)
        delay_frame.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(delay_frame, text="Czas:").pack(side=tk.LEFT)
        self.time_var = tk.StringVar(value="0s")
        time_combo = ttk.Combobox(delay_frame, textvariable=self.time_var, values=["0s", "1s", "3s", "5s"],
                                 state="readonly", width=5)
        time_combo.pack(side=tk.LEFT, padx=(2, 5))
        time_combo.bind("<<ComboboxSelected>>", self.update_delay_time)

        button_frame2 = ttk.Frame(left_frame)
        button_frame2.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(button_frame2, text="Oddal/przybliż widok: Ctrl + Scroll").pack(side=tk.LEFT, padx=(0, 5))

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        canvas_frame = ttk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)

        self.canvas = tk.Canvas(canvas_frame, bg='white',
                               yscrollcommand=v_scrollbar.set,
                               xscrollcommand=h_scrollbar.set)

        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel_zoom)
        self.canvas.bind("<Button-4>", self.on_mousewheel_zoom)
        self.canvas.bind("<Button-5>", self.on_mousewheel_zoom)
        self.canvas.bind("<ButtonPress-2>", self.pan_start)
        self.canvas.bind("<B2-Motion>", self.pan_move)

        self.canvas.tag_bind("sketch", "<Button-3>", self.on_sketch_right_click)
        self.canvas.tag_bind("sketch_text", "<Button-3>", self.on_sketch_right_click)
        self.canvas.tag_bind("text_layer", "<Button-1>", self.on_text_layer_click)

        self.root.bind("<Delete>", lambda e: self.delete_layer())
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

        self.status_var = tk.StringVar()
        self.status_var.set("Gotowy - kliknij 'Nowy' aby zrobić zrzut ekranu")
        status_bar = ttk.Label(left_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))

        self.update_delay_time()
        self.set_draw_mode("cursor")

    def on_opacity_change(self, val):
        idx = self.layer_listbox.curselection()
        if idx:
            i = idx[0]
            self.layers[i]["opacity"] = float(val)
            self.redraw_layers()

    def set_zoom(self, zoom):
        if zoom <= 0:
            return
        scale = zoom / self.current_zoom
        self.current_zoom = zoom

        # Rescale all layers using the original image
        for layer in self.layers:
            orig = layer.get("original")
            if orig:
                w, h = orig.size
                new_size = (int(w * self.current_zoom), int(h * self.current_zoom))
                layer["image"] = orig.resize(new_size, resample=Image.LANCZOS)
                layer["tk"] = ImageTk.PhotoImage(layer["image"])
                layer["x"] = int(layer["x"] * scale)
                layer["y"] = int(layer["y"] * scale)

        # Rescale sketch items
        new_sketch_items = []
        for item in self.sketch_items:
            typ, extra, color, width, tag, *text = item
            if typ in ("pencil", "eraser"):
                scaled_points = [(x * scale, y * scale) for x, y in extra]
                new_sketch_items.append((typ, scaled_points, color, width, tag))
            elif typ in ("rectangle", "line"):
                scaled_coords = [coord * scale for coord in extra]
                new_sketch_items.append((typ, scaled_coords, color, width, tag))
        self.sketch_items = new_sketch_items

        # Rescale text layers
        for text_layer in self.text_layers:
            text_layer["x"] = int(text_layer["x"] * scale)
            text_layer["y"] = int(text_layer["y"] * scale)
            text_layer["w"] = int(text_layer["w"] * scale)
            text_layer["h"] = int(text_layer["h"] * scale)
            text_layer["size"] = int(text_layer["size"] * scale)

        self.redraw_layers()
        self.status_var.set(f"Zoom: {int(zoom * 100)}%")

    def on_mousewheel_zoom(self, event):
        if (event.state & 0x0004) != 0:
            if hasattr(event, 'delta'):
                scale = 1.1 if event.delta > 0 else 0.9
            elif event.num == 4:
                scale = 1.1
            elif event.num == 5:
                scale = 0.9
            else:
                scale = 1.0
            self.set_zoom(self.current_zoom * scale)
        else:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        return "break"

    def update_delay_time(self, event=None):
        time_str = self.time_var.get()
        try:
            self.delay_time = int(time_str.replace('s', ''))
        except:
            self.delay_time = 0

    def new_screenshot(self):
        self.layers.clear()
        self.sketch_items.clear()
        self.text_layers.clear()
        self.text_active_idx = None
        self.canvas.delete("all")
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._screenshot_to_layer(clear_layers=True)

    def add_layer(self):
        self._screenshot_to_layer(clear_layers=False)

    def _screenshot_to_layer(self, clear_layers=False):
        def do_capture():
            if self.delay_time > 0:
                for i in range(self.delay_time, 0, -1):
                    self.status_var.set(f"Zrzut ekranu za {i} s...")
                    self.root.update()
                    time.sleep(1)
            self.status_var.set("Robię zrzut...")
            self.root.update()
            self.root.withdraw()
            time.sleep(0.3)
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            bbox = (monitor["left"], monitor["top"], monitor["left"] + monitor["width"], monitor["top"] + monitor["height"])
            self.root.after(100, lambda: self.show_selection_window_layer(img, bbox, clear_layers))
        threading.Thread(target=do_capture, daemon=True).start()

    def show_selection_window_layer(self, screenshot, bbox, clear_layers):
        width, height = screenshot.width, screenshot.height
        left, top, _, _ = bbox

        selection_window = tk.Toplevel()
        selection_window.geometry(f"{width}x{height}+{left}+{top}")
        selection_window.overrideredirect(True)
        selection_window.lift()
        selection_window.attributes('-topmost', True)
        selection_window.focus_force()
        selection_window.configure(cursor='cross')

        selection_canvas = tk.Canvas(
            selection_window,
            highlightthickness=0,
            width=width,
            height=height
        )
        selection_canvas.pack(fill=tk.BOTH, expand=True)
        bg_image = ImageTk.PhotoImage(screenshot)
        selection_canvas.create_image(0, 0, image=bg_image, anchor=tk.NW)
        selection_canvas.image = bg_image

        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.current_screenshot = screenshot

        def start_selection(event):
            self.start_x = event.x
            self.start_y = event.y
            selection_canvas.delete("instruction")

        def update_selection(event):
            if self.start_x is not None and self.start_y is not None:
                if self.rect_id:
                    selection_canvas.delete(self.rect_id)
                self.rect_id = selection_canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline="red", width=2, fill="", tags="selection"
                )

        def end_selection(event):
            try:
                if self.start_x is not None and self.start_y is not None:
                    x1 = min(self.start_x, event.x)
                    y1 = min(self.start_y, event.y)
                    x2 = max(self.start_x, event.x)
                    y2 = max(self.start_y, event.y)
                    if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                        selection_window.destroy()
                        cropped = self.current_screenshot.crop((x1, y1, x2, y2))
                        if clear_layers:
                            self.layers.clear()
                            self.canvas.delete("all")
                        self.add_image_layer(cropped)
                        self.root.deiconify()
                        self.root.state('normal')
                        self.status_var.set(f"Zrzut {cropped.width}x{cropped.height} - dodano warstwę!")
                        if len(self.layers) > 1:
                            self.show_layer_panel()
                    else:
                        cancel_selection(None)
                else:
                    cancel_selection(None)
            except Exception as e:
                print(f"Błąd podczas kończenia zaznaczania: {e}")
                cancel_selection(None)

        def cancel_selection(event):
            try:
                if selection_window.winfo_exists():
                    selection_window.destroy()
            except:
                pass
            finally:
                self.root.deiconify()
                self.root.state('normal')
                self.status_var.set("Anulowano")

        selection_canvas.bind("<Button-1>", start_selection)
        selection_canvas.bind("<B1-Motion>", update_selection)
        selection_canvas.bind("<ButtonRelease-1>", end_selection)
        selection_window.bind("<Escape>", cancel_selection)
        selection_window.bind("<Return>", cancel_selection)

        selection_canvas.create_text(
            width // 2, 50,
            text="Przeciągnij myszą aby zaznaczyć obszar • ESC/Enter - anuluj",
            fill="yellow",
            font=("Arial", 16, "bold"),
            tags="instruction"
        )

        selection_window.focus_set()
        selection_window.grab_set()

    def add_image_layer(self, pil_image):
        tk_img = ImageTk.PhotoImage(pil_image)
        x, y = 40, 40
        canvas_id = self.canvas.create_image(x, y, anchor=tk.NW, image=tk_img, tags="layer")
        rect_id = self.canvas.create_rectangle(x, y, x+pil_image.width, y+pil_image.height, outline="blue", width=2, tags="frame")
        name = f"Warstwa {len(self.layers)+1}"
        layer = {"image": pil_image.convert("RGBA"), "original": pil_image.copy(), "tk": tk_img, "id": canvas_id, "frame_id": rect_id, "x": x, "y": y, "name": name, "opacity": 1.0}
        self.layers.append(layer)
        self.canvas.tag_raise(canvas_id)
        self.canvas.tag_raise(rect_id)
        self.update_layer_listbox()
        self.set_active_layer(len(self.layers)-1)
        self.show_layer_panel()
        self.update_canvas_scrollregion()
        self.push_undo()

    def update_canvas_scrollregion(self):
        min_x, min_y, max_x, max_y = self._get_full_bounds()
        self.canvas.configure(scrollregion=(min_x, min_y, max_x, max_y))

    def show_layer_panel(self):
        self.layer_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))

    def update_layer_listbox(self):
        self.layer_listbox.delete(0, tk.END)
        for layer in self.layers:
            self.layer_listbox.insert(tk.END, layer["name"])
        idx = self.layer_listbox.curselection()
        if idx:
            self.opacity_var.set(self.layers[idx[0]].get("opacity", 1.0))
        elif self.layers:
            active_idx = self.layers.index(self.active_layer) if self.active_layer in self.layers else len(self.layers)-1
            self.layer_listbox.select_set(active_idx)
            self.opacity_var.set(self.layers[active_idx].get("opacity", 1.0))

    def select_layer_from_list(self, event=None):
        idx = self.layer_listbox.curselection()
        if idx:
            idx = idx[0]
            self.set_active_layer(idx)
            self.opacity_var.set(self.layers[idx].get("opacity", 1.0))

    def set_active_layer(self, idx):
        if 0 <= idx < len(self.layers):
            self.active_layer = self.layers[idx]
            for i, layer in enumerate(self.layers):
                color = "red" if i == idx else "blue"
                self.canvas.coords(layer["frame_id"], layer["x"], layer["y"], layer["x"]+layer["image"].width, layer["y"]+layer["image"].height)
                self.canvas.itemconfig(layer["frame_id"], outline=color)

    def move_layer_up(self):
        idx = self.layer_listbox.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self.layers[i-1], self.layers[i] = self.layers[i], self.layers[i-1]
            self.redraw_layers()
            self.update_layer_listbox()
            self.layer_listbox.select_set(i-1)
            self.set_active_layer(i-1)
            self.push_undo()

    def move_layer_down(self):
        idx = self.layer_listbox.curselection()
        if idx and idx[0] < len(self.layers)-1:
            i = idx[0]
            self.layers[i], self.layers[i+1] = self.layers[i+1], self.layers[i]
            self.redraw_layers()
            self.update_layer_listbox()
            self.layer_listbox.select_set(i+1)
            self.set_active_layer(i+1)
            self.push_undo()

    def delete_layer(self):
        idx = self.layer_listbox.curselection()
        if idx:
            i = idx[0]
            layer = self.layers.pop(i)
            self.canvas.delete(layer["id"])
            self.canvas.delete(layer["frame_id"])
            self.update_layer_listbox()
            if not self.layers:
                self.layer_panel.pack_forget()
                self.active_layer = None
            else:
                self.layer_listbox.select_set(min(i, len(self.layers)-1))
                self.set_active_layer(min(i, len(self.layers)-1))
            self.update_canvas_scrollregion()
            self.push_undo()

    def draw_resize_handles(self, x1, y1, x2, y2, tag_prefix):
        r = self.handle_radius
        handles = [
            (x1, y1), (x2, y1), (x2, y2), (x1, y2)
        ]
        for idx, (hx, hy) in enumerate(handles):
            self.canvas.create_oval(hx-r, hy-r, hx+r, hy+r, fill="orange", outline="black", tags=(f"{tag_prefix}_handle_{idx}", "resize_handle"))

    def redraw_layers(self):
        self.canvas.delete("all")
        # Warstwy
        for idx, layer in enumerate(self.layers):
            x, y = layer["x"], layer["y"]
            img = layer["image"].copy()
            if layer.get("opacity", 1.0) < 1.0:
                alpha = img.split()[-1].point(lambda p: int(p * layer["opacity"]))
                img.putalpha(alpha)
            layer["tk"] = ImageTk.PhotoImage(img)
            layer["id"] = self.canvas.create_image(x, y, anchor=tk.NW, image=layer["tk"], tags="layer")
            color = "red" if self.active_layer == layer else "blue"
            layer["frame_id"] = self.canvas.create_rectangle(
                x, y, x+layer["image"].width, y+layer["image"].height,
                outline=color, width=2, tags=("frame")
            )
            if self.active_layer == layer and self.selected_sketch is None and self.text_active_idx is None:
                self.draw_resize_handles(x, y, x+layer["image"].width, y+layer["image"].height, f"layer_{idx}")

        # Sketch items
        for idx, (typ, extra, color, width, tag, *text) in enumerate(self.sketch_items):
            is_active = (self.selected_sketch == idx)
            if typ == "pencil":
                self.canvas.create_line(*extra, fill=color, width=width, capstyle=tk.ROUND, smooth=tk.TRUE, tags=("sketch", tag))
            elif typ == "eraser":
                self.canvas.create_line(*extra, fill="white", width=width, capstyle=tk.ROUND, smooth=tk.TRUE, tags=("sketch", tag))
            elif typ == "rectangle":
                self.canvas.create_rectangle(*extra, outline=color, width=width, tags=("sketch", tag))
                x1, y1, x2, y2 = extra
                if is_active:
                    self.draw_resize_handles(x1, y1, x2, y2, f"rect_{idx}")
            elif typ == "line":
                self.canvas.create_line(*extra, fill=color, width=width, tags=("sketch", tag))
                x1, y1, x2, y2 = extra
                if is_active:
                    r = self.line_handle_radius
                    self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, fill="orange", outline="black", tags=(f"line_handle_{idx}_0", "line_handle"))
                    self.canvas.create_oval(x2-r, y2-r, x2+r, y2+r, fill="orange", outline="black", tags=(f"line_handle_{idx}_1", "line_handle"))
        # Teksty
        for idx, text_layer in enumerate(self.text_layers):
            text_layer["id"] = self.canvas.create_text(
                text_layer["x"], text_layer["y"],
                text=text_layer["text"], fill=text_layer["color"],
                font=("Arial", text_layer["size"]), anchor="nw", tags=("text_layer", f"text_{idx}")
            )
            text_layer["frame_id"] = self.canvas.create_rectangle(
                text_layer["x"], text_layer["y"],
                text_layer["x"]+text_layer["w"], text_layer["y"]+text_layer["h"],
                outline="green", width=1, tags=("text_layer", f"text_{idx}")
            )
            if self.text_active_idx == idx:
                x1, y1 = text_layer["x"], text_layer["y"]
                x2, y2 = x1 + text_layer["w"], y1 + text_layer["h"]
                self.draw_resize_handles(x1, y1, x2, y2, f"text_{idx}")
        # Eraser preview
        if self.eraser_preview:
            self.canvas.delete(self.eraser_preview)
            self.eraser_preview = None
        if self.draw_mode == "eraser" and len(self.eraser_path) > 1:
            self.eraser_preview = self.canvas.create_line(
                *sum(self.eraser_path, ()), fill="orange", width=2, dash=(2, 2), tags="eraser_preview"
            )
        self.update_layer_listbox()
        self.update_canvas_scrollregion()

    def on_left_click(self, event):
        handle = self.canvas.find_withtag("current")
        tags = self.canvas.gettags(handle)
        for t in tags:
            if t.startswith("line_handle_"):
                parts = t.split("_")
                idx = int(parts[2])
                handle_idx = int(parts[3])
                self.line_handle_drag = (idx, handle_idx)
                self.selected_sketch = idx
                self.redraw_layers()
                return
            if t.startswith("rect_") and "resize_handle" in tags:
                idx = int(t.split("_")[1])
                handle_idx = int(t.split("_")[-1])
                self.handle_drag = ("rectangle", idx, handle_idx)
                self.selected_sketch = idx
                self.redraw_layers()
                return
            if t.startswith("layer_") and "resize_handle" in tags:
                idx = int(t.split("_")[1])
                handle_idx = int(t.split("_")[-1])
                self.handle_drag = ("layer", idx, handle_idx)
                self.selected_sketch = None
                self.redraw_layers()
                return
            if t.startswith("text") and "resize_handle" in tags:
                idx = int(t.split("_")[1])
                self.handle_drag = ("text", idx, int(t.split("_")[-1]))
                self.text_active_idx = idx
                self.selected_sketch = None
                self.redraw_layers()
                return
        if self.draw_mode == "cursor":
            clicked = self.canvas.find_withtag("current")
            for idx, text_layer in enumerate(self.text_layers):
                if text_layer["id"] in clicked:
                    text_layer["dragging"] = True
                    text_layer["offset_x"] = event.x - text_layer["x"]
                    text_layer["offset_y"] = event.y - text_layer["y"]
                    self.text_active_idx = idx
                    self.selected_sketch = None
                    self.redraw_layers()
                    return
            for idx, layer in enumerate(self.layers):
                if layer["frame_id"] in clicked or layer["id"] in clicked:
                    self.active_layer = layer
                    self.set_active_layer(idx)
                    self.layer_drag_data["id"] = layer["id"]
                    self.layer_drag_data["frame_id"] = layer["frame_id"]
                    self.layer_drag_data["x"] = event.x
                    self.layer_drag_data["y"] = event.y
                    bbox = self.canvas.bbox(layer["id"])
                    self.layer_drag_data["offset_x"] = event.x - bbox[0]
                    self.layer_drag_data["offset_y"] = event.y - bbox[1]
                    self.layer_drag_data["dragging"] = True
                    self.text_active_idx = None
                    self.selected_sketch = None
                    self.redraw_layers()
                    break
            for idx, item in enumerate(self.sketch_items):
                typ, extra, color, width, tag, *text = item
                if typ in ("rectangle", "line"):
                    if tag in self.canvas.gettags("current"):
                        self.selected_sketch = idx
                        self.text_active_idx = None
                        x1, y1, x2, y2 = extra
                        self.sketch_drag_offset = (event.x - x1, event.y - y1, x2 - x1, y2 - y1)
                        self.redraw_layers()
                        return
        elif self.draw_mode in ("pencil", "rectangle", "line"):
            self.start_drawing(event)
        elif self.draw_mode == "text":
            if self.text_entry:
                self.text_entry.destroy()
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.text_entry = tk.Entry(self.canvas, font=("Arial", self.sketch_width*3), fg=self.sketch_color)
            self.text_entry.place(x=x, y=y)
            self.text_entry.focus_set()
            self.text_entry.bind("<Return>", lambda e: self.finish_text_entry(x, y))
            self.text_entry.bind("<Escape>", lambda e: self.cancel_text_entry())
            self.text_entry.bind("<FocusOut>", lambda e: self.finish_text_entry(x, y))
        elif self.draw_mode == "eraser":
            self.eraser_path = [(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))]
            self.eraser_preview = None
            self.is_drawing = True
            self.redraw_layers()
            return

    def finish_text_entry(self, x, y):
        if not self.text_entry:
            return
        text = self.text_entry.get()
        self.text_entry.destroy()
        self.text_entry = None
        if text:
            font_size = self.sketch_width*3
            text_id = self.canvas.create_text(x, y, text=text, fill=self.sketch_color, font=("Arial", font_size), anchor="nw", tags="text_layer")
            bbox = self.canvas.bbox(text_id)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            frame_id = self.canvas.create_rectangle(x, y, x+w, y+h, outline="green", width=1, tags="text_layer")
            self.text_layers.append({
                "text": text, "x": x, "y": y, "color": self.sketch_color, "size": font_size,
                "id": text_id, "frame_id": frame_id, "w": w, "h": h, "dragging": False
            })
            self.text_active_idx = len(self.text_layers) - 1
            self.push_undo()
            self.set_draw_mode("cursor")

    def cancel_text_entry(self):
        if self.text_entry:
            self.text_entry.destroy()
            self.text_entry = None

    def on_left_drag(self, event):
        if self.line_handle_drag:
            idx, handle_idx = self.line_handle_drag
            typ, extra, color, width, tag, *text = self.sketch_items[idx]
            x1, y1, x2, y2 = extra
            if handle_idx == 0:
                new_extra = (event.x, event.y, x2, y2)
            else:
                new_extra = (x1, y1, event.x, event.y)
            self.sketch_items[idx] = (typ, new_extra, color, width, tag)
            self.redraw_layers()
            return
        if self.handle_drag:
            typ, idx, handle_idx = self.handle_drag
            shift = (event.state & 0x0001) != 0  # Shift wciśnięty
            if typ == "rectangle":
                item = self.sketch_items[idx]
                _, extra, color, width, tag, *text = item
                x1, y1, x2, y2 = extra
                coords = [x1, y1, x2, y2]
                if shift:
                    opp = [(x2, y2), (x1, y2), (x1, y1), (x2, y1)][handle_idx]
                    dx = event.x - opp[0]
                    dy = event.y - opp[1]
                    d = max(abs(dx), abs(dy))
                    sign_x = 1 if dx >= 0 else -1
                    sign_y = 1 if dy >= 0 else -1
                    coords[handle_idx*2%4] = opp[0] + sign_x * d
                    coords[(handle_idx*2+1)%4] = opp[1] + sign_y * d
                else:
                    if handle_idx == 0:
                        coords[0], coords[1] = event.x, event.y
                    elif handle_idx == 1:
                        coords[2], coords[1] = event.x, event.y
                    elif handle_idx == 2:
                        coords[2], coords[3] = event.x, event.y
                    elif handle_idx == 3:
                        coords[0], coords[3] = event.x, event.y
                self.sketch_items[idx] = ("rectangle", tuple(coords), color, width, tag)
                self.redraw_layers()
                return
            elif typ == "layer":
                layer = self.layers[idx]
                x1, y1 = layer["x"], layer["y"]
                x2, y2 = x1 + layer["image"].width, y1 + layer["image"].height
                coords = [x1, y1, x2, y2]
                if shift:
                    opp = [(x2, y2), (x1, y2), (x1, y1), (x2, y1)][handle_idx]
                    dx = event.x - opp[0]
                    dy = event.y - opp[1]
                    d = max(abs(dx), abs(dy))
                    sign_x = 1 if dx >= 0 else -1
                    sign_y = 1 if dy >= 0 else -1
                    coords[handle_idx*2%4] = opp[0] + sign_x * d
                    coords[(handle_idx*2+1)%4] = opp[1] + sign_y * d
                else:
                    if handle_idx == 0:
                        coords[0], coords[1] = event.x, event.y
                    elif handle_idx == 1:
                        coords[2], coords[1] = event.x, event.y
                    elif handle_idx == 2:
                        coords[2], coords[3] = event.x, event.y
                    elif handle_idx == 3:
                        coords[0], coords[3] = event.x, event.y
                new_x1, new_y1, new_x2, new_y2 = coords
                new_w = max(10, new_x2 - new_x1)
                new_h = max(10, new_y2 - new_y1)
                layer["x"], layer["y"] = new_x1, new_y1
                layer["image"] = layer["original"].resize((new_w, new_h), resample=Image.LANCZOS)
                layer["tk"] = ImageTk.PhotoImage(layer["image"])
                self.redraw_layers()
                return
            elif typ == "text":
                if 0 <= idx < len(self.text_layers):
                    text_layer = self.text_layers[idx]
                    x1, y1 = text_layer["x"], text_layer["y"]
                    x2, y2 = x1 + text_layer["w"], y1 + text_layer["h"]
                    coords = [x1, y1, x2, y2]
                    if shift:
                        opp = [(x2, y2), (x1, y2), (x1, y1), (x2, y1)][handle_idx]
                        dx = event.x - opp[0]
                        dy = event.y - opp[1]
                        d = max(abs(dx), abs(dy))
                        sign_x = 1 if dx >= 0 else -1
                        sign_y = 1 if dy >= 0 else -1
                        coords[handle_idx*2%4] = opp[0] + sign_x * d
                        coords[(handle_idx*2+1)%4] = opp[1] + sign_y * d
                    else:
                        if handle_idx == 0:
                            coords[0], coords[1] = event.x, event.y
                        elif handle_idx == 1:
                            coords[2], coords[1] = event.x, event.y
                        elif handle_idx == 2:
                            coords[2], coords[3] = event.x, event.y
                        elif handle_idx == 3:
                            coords[0], coords[3] = event.x, event.y
                    new_x1, new_y1, new_x2, new_y2 = coords
                    new_h = max(10, new_y2 - new_y1)
                    new_size = max(8, int(new_h * 0.8))
                    text_layer["x"], text_layer["y"] = new_x1, new_y1
                    text_layer["w"], text_layer["h"] = max(10, new_x2 - new_x1), new_h
                    text_layer["size"] = new_size
                    self.redraw_layers()
                return
        if self.draw_mode == "cursor":
            if self.text_active_idx is not None:
                text_layer = self.text_layers[self.text_active_idx]
                if text_layer.get("dragging"):
                    new_x = event.x - text_layer["offset_x"]
                    new_y = event.y - text_layer["offset_y"]
                    text_layer["x"] = new_x
                    text_layer["y"] = new_y
                    self.canvas.coords(text_layer["id"], new_x, new_y)
                    self.canvas.coords(text_layer["frame_id"], new_x, new_y, new_x+text_layer["w"], new_y+text_layer["h"])
                    return
            if self.layer_drag_data["dragging"] and self.active_layer:
                new_x = event.x - self.layer_drag_data["offset_x"]
                new_y = event.y - self.layer_drag_data["offset_y"]
                self.canvas.coords(self.active_layer["id"], new_x, new_y)
                self.canvas.coords(self.active_layer["frame_id"], new_x, new_y, new_x+self.active_layer["image"].width, new_y+self.active_layer["image"].height)
                self.active_layer["x"] = new_x
                self.active_layer["y"] = new_y
                self.update_canvas_scrollregion()
            if self.selected_sketch is not None:
                typ, extra, color, width, tag, *text = self.sketch_items[self.selected_sketch]
                dx = event.x - self.sketch_drag_offset[0]
                dy = event.y - self.sketch_drag_offset[1]
                w = self.sketch_drag_offset[2]
                h = self.sketch_drag_offset[3]
                if typ == "rectangle":
                    new_extra = (dx, dy, dx + w, dy + h)
                elif typ == "line":
                    new_extra = (dx, dy, dx + w, dy + h)
                else:
                    new_extra = extra
                self.sketch_items[self.selected_sketch] = (typ, new_extra, color, width, tag)
                self.redraw_layers()
                return
        elif self.draw_mode in ("pencil", "rectangle", "line"):
            self.draw(event)
        elif self.draw_mode == "eraser" and self.is_drawing:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.eraser_path.append((x, y))
            if self.eraser_preview:
                self.canvas.delete(self.eraser_preview)
            if len(self.eraser_path) > 1:
                self.eraser_preview = self.canvas.create_line(
                    *sum(self.eraser_path, ()), fill="orange", width=2, dash=(2, 2), tags="eraser_preview"
                )

    def on_left_release(self, event):
        if self.line_handle_drag:
            self.line_handle_drag = None
            self.push_undo()
            return
        if self.handle_drag:
            self.handle_drag = None
            self.push_undo()
            return
        if self.draw_mode == "cursor":
            for text_layer in self.text_layers:
                text_layer["dragging"] = False
            self.layer_drag_data["dragging"] = False
            self.selected_sketch = None
            self.sketch_drag_offset = (0, 0)
        elif self.draw_mode in ("pencil", "rectangle", "line"):
            self.stop_drawing(event)
        elif self.draw_mode == "eraser" and self.is_drawing:
            # Usuń podgląd gumki natychmiast po puszczeniu myszy
            if self.eraser_preview:
                self.canvas.delete(self.eraser_preview)
                self.eraser_preview = None
            # Sprawdź, które szkice przecina ścieżka gumki
            to_delete = []
            for idx, item in enumerate(self.sketch_items):
                typ, extra, color, width, tag, *text = item
                if typ in ("pencil", "eraser"):
                    points = extra
                    if self._eraser_path_intersects_polyline(self.eraser_path, points):
                        to_delete.append(idx)
                elif typ in ("rectangle", "line"):
                    rect_points = [extra[:2], extra[2:]]
                    if self._eraser_path_intersects_polyline(self.eraser_path, rect_points):
                        to_delete.append(idx)
            for idx in reversed(to_delete):
                del self.sketch_items[idx]
            self.is_drawing = False
            self.eraser_path = []
            # Po gumkowaniu wróć do kursora i odśwież warstwy (to usunie ślad gumki)
            self.set_draw_mode("cursor")
            self.redraw_layers()
            if to_delete:
                self.push_undo()
        elif self.draw_mode == "eraser":
            self.is_drawing = False
            self.last_x = None
            self.last_y = None
            self.sketch_points = []

    def _eraser_path_intersects_polyline(self, path, polyline):
        # Sprawdza czy jakikolwiek odcinek z path przecina jakikolwiek odcinek z polyline
        def ccw(A, B, C):
            return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
        def intersect(A,B,C,D):
            return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
        for i in range(len(path)-1):
            A, B = path[i], path[i+1]
            for j in range(len(polyline)-1):
                C, D = polyline[j], polyline[j+1]
                if intersect(A,B,C,D):
                    return True
        return False

    def on_text_layer_click(self, event):
        clicked = self.canvas.find_withtag("current")
        for idx, text_layer in enumerate(self.text_layers):
            if text_layer["id"] in clicked:
                text_layer["dragging"] = True
                text_layer["offset_x"] = event.x - text_layer["x"]
                text_layer["offset_y"] = event.y - text_layer["y"]
                self.text_active_idx = idx

    def pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_sketch_right_click(self, event):
        item = self.canvas.find_withtag("current")
        tags = self.canvas.gettags(item)
        for tag in tags:
            if tag.startswith("sketch_"):
                self.canvas.delete(tag)
                self.sketch_items = [s for s in self.sketch_items if s[4] != tag]
                self.push_undo()
                break

    def erase_sketch_paint(self, x, y, r):
        changed = False
        new_sketch_items = []
        for item in self.sketch_items:
            typ, extra, color, width, tag, *text = item
            if typ == "pencil":
                new_points = []
                for px, py in extra:
                    if (px - x) ** 2 + (py - y) ** 2 > r ** 2:
                        new_points.append((px, py))
                if len(new_points) > 1:
                    new_sketch_items.append(("pencil", new_points, color, width, tag))
                else:
                    changed = True
            elif typ in ("rectangle", "line", "eraser"):
                new_sketch_items.append(item)
            else:
                new_sketch_items.append(item)
        if changed:
            self.sketch_items = new_sketch_items
            self.redraw_layers()

    def copy_image_to_clipboard(self, image):
        try:
            output = io.BytesIO()
            image.convert("RGB").save(output, format='BMP')
            data = output.getvalue()[14:]
            output.close()
            if os.name == 'nt':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                except ImportError:
                    messagebox.showwarning("Brak biblioteki", "Aby kopiować obraz do schowka na Windows potrzebujesz pakietu pywin32.\nZainstaluj go poleceniem:\npip install pywin32")
            else:
                messagebox.showwarning("Kopiowanie obrazów", "Kopiowanie do schowka działa tylko na Windows.")
        except Exception as e:
            print(f"Nie można skopiować do schowka: {e}")
            messagebox.showwarning("Kopiowanie obrazów", f"Nie udało się skopiować obrazu do schowka.\n{e}")

    def copy_to_clipboard(self):
        if not self.layers:
            messagebox.showwarning("Ostrzeżenie", "Brak warstw do skopiowania!")
            return
        min_x, min_y, max_x, max_y = self._get_full_bounds()
        width = int(max_x - min_x)
        height = int(max_y - min_y)
        result = Image.new("RGBA", (width, height), (255,255,255,255))
        for layer in self.layers:
            img = layer["image"].convert("RGBA")
            if layer.get("opacity", 1.0) < 1.0:
                alpha = img.split()[-1].point(lambda p: int(p * layer["opacity"]))
                img.putalpha(alpha)
            if img.size != (layer["image"].width, layer["image"].height):
                img = img.resize((layer["image"].width, layer["image"].height))
            result.alpha_composite(img, (int(layer["x"]-min_x), int(layer["y"]-min_y)))
        draw = ImageDraw.Draw(result)
        for typ, extra, color, width, tag, *text in self.sketch_items:
            if typ == "pencil":
                shifted = [(px-min_x, py-min_y) for px, py in extra]
                draw.line(shifted, fill=color, width=width)
            elif typ == "eraser":
                shifted = [(px-min_x, py-min_y) for px, py in extra]
                draw.line(shifted, fill="white", width=width)
            elif typ == "rectangle":
                x1, y1, x2, y2 = extra
                draw.rectangle((x1-min_x, y1-min_y, x2-min_x, y2-min_y), outline=color, width=width)
            elif typ == "line":
                x1, y1, x2, y2 = extra
                draw.line((x1-min_x, y1-min_y, x2-min_x, y2-min_y), fill=color, width=width)
        for text_layer in self.text_layers:
            try:
                font = ImageFont.truetype("arial.ttf", text_layer["size"])
            except Exception:
                font = None
            draw.text((text_layer["x"]-min_x, text_layer["y"]-min_y), text_layer["text"], fill=text_layer["color"], font=font)
        self.copy_image_to_clipboard(result.convert("RGB"))
        self.status_var.set("Skopiowano do schowka!")

    def set_draw_mode(self, mode):
        self.draw_mode = mode
        if mode == "cursor":
            self.status_var.set("Tryb: przesuwanie warstw")
        elif mode == "pencil":
            self.status_var.set("Tryb: szkic ołówkiem")
        elif mode == "rectangle":
            self.status_var.set("Tryb: rysowanie prostokąta")
        elif mode == "line":
            self.status_var.set("Tryb: rysowanie linii")
        elif mode == "text":
            self.status_var.set("Tryb: wstawianie tekstu")
        elif mode == "eraser":
            self.status_var.set("Tryb: gumka (miecz świetlny)")

    def choose_color(self):
        color = colorchooser.askcolor(color=self.draw_color)[1]
        if color:
            self.draw_color = color
            self.sketch_color = color
            self.status_var.set(f"Wybrano kolor: {color}")

    def start_drawing(self, event):
        if self.draw_mode in ("pencil", "rectangle", "line"):
            self.is_drawing = True
            self.last_x = self.canvas.canvasx(event.x)
            self.last_y = self.canvas.canvasy(event.y)
            self.temp_shape = None
            self.sketch_points = [(self.last_x, self.last_y)]

    def draw(self, event):
        if not self.is_drawing:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        tag = f"sketch_{self.sketch_counter}"
        if self.draw_mode == "pencil":
            self.sketch_points.append((x, y))
            self.canvas.create_line(
                self.sketch_points[-2][0], self.sketch_points[-2][1], x, y,
                fill=self.sketch_color, width=self.sketch_width, capstyle=tk.ROUND, smooth=tk.TRUE, tags=("sketch", tag)
            )
        elif self.draw_mode == "rectangle":
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            self.temp_shape = self.canvas.create_rectangle(self.last_x, self.last_y, x, y, outline=self.sketch_color, width=self.sketch_width, tags=("sketch_temp", tag))
        elif self.draw_mode == "line":
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            self.temp_shape = self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.sketch_color, width=self.sketch_width, tags=("sketch_temp", tag))

    def stop_drawing(self, event):
        if not self.is_drawing:
            return
        color = self.sketch_color
        width = self.sketch_width
        tag = f"sketch_{self.sketch_counter}"
        if self.draw_mode == "pencil" and len(self.sketch_points) > 1:
            self.sketch_items.append(("pencil", list(self.sketch_points), color, width, tag))
            self.sketch_counter += 1
            self.push_undo()
        elif self.draw_mode == "rectangle":
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            rect = (self.last_x, self.last_y, x, y)
            self.sketch_items.append(("rectangle", rect, color, width, tag))
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            self.canvas.create_rectangle(*rect, outline=color, width=width, tags=("sketch", tag))
            self.sketch_counter += 1
            self.push_undo()
            self.set_draw_mode("cursor")
        elif self.draw_mode == "line":
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            line = (self.last_x, self.last_y, x, y)
            self.sketch_items.append(("line", line, color, width, tag))
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            self.canvas.create_line(*line, fill=color, width=width, tags=("sketch", tag))
            self.sketch_counter += 1
            self.push_undo()
            self.set_draw_mode("cursor")
        self.is_drawing = False
        self.last_x = None
        self.last_y = None
        self.sketch_points = []
        self.temp_shape = None

    def erase_sketch(self):
        self.canvas.delete("sketch")
        self.canvas.delete("sketch_temp")
        self.canvas.delete("sketch_text")
        self.sketch_items.clear()
        self.status_var.set("Wyczyszczono szkice.")
        self.push_undo()

    def save_image(self):
        if not self.layers:
            messagebox.showwarning("Ostrzeżenie", "Brak warstw do zapisania!")
            return
        min_x, min_y, max_x, max_y = self._get_full_bounds()
        width = int(max_x - min_x)
        height = int(max_y - min_y)
        result = Image.new("RGBA", (width, height), (255,255,255,255))
        for layer in self.layers:
            img = layer["image"].convert("RGBA")
            if layer.get("opacity", 1.0) < 1.0:
                alpha = img.split()[-1].point(lambda p: int(p * layer["opacity"]))
                img.putalpha(alpha)
            if img.size != (layer["image"].width, layer["image"].height):
                img = img.resize((layer["image"].width, layer["image"].height))
            result.alpha_composite(img, (int(layer["x"]-min_x), int(layer["y"]-min_y)))
        draw = ImageDraw.Draw(result)
        for typ, extra, color, width, tag, *text in self.sketch_items:
            if typ == "pencil":
                shifted = [(px-min_x, py-min_y) for px, py in extra]
                draw.line(shifted, fill=color, width=width)
            elif typ == "eraser":
                shifted = [(px-min_x, py-min_y) for px, py in extra]
                draw.line(shifted, fill="white", width=width)
            elif typ == "rectangle":
                x1, y1, x2, y2 = extra
                draw.rectangle((x1-min_x, y1-min_y, x2-min_x, y2-min_y), outline=color, width=width)
            elif typ == "line":
                x1, y1, x2, y2 = extra
                draw.line((x1-min_x, y1-min_y, x2-min_x, y2-min_y), fill=color, width=width)
        for text_layer in self.text_layers:
            try:
                font = ImageFont.truetype("arial.ttf", text_layer["size"])
            except Exception:
                font = None
            draw.text((text_layer["x"]-min_x, text_layer["y"]-min_y), text_layer["text"], fill=text_layer["color"], font=font)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"zrzut_ekranu_{timestamp}.png"
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            try:
                result.convert("RGB").save(filename)
                self.status_var.set(f"Zapisano: {os.path.basename(filename)}")
                messagebox.showinfo("Sukces", f"Obraz został zapisany jako:\n{filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać pliku:\n{str(e)}")

    # Undo/redo system
    def push_undo(self):
        state = (
            [layer.copy() for layer in self.layers],
            [item for item in self.sketch_items],
            copy.deepcopy(self.text_layers),
            self.text_active_idx
        )
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        if len(self.undo_stack) == 1:
            return
        self.redo_stack.append(self.undo_stack.pop())
        state = self.undo_stack[-1]
        self.restore_state(state)

    def redo(self):
        if not self.redo_stack:
            return
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        self.restore_state(state)

    def restore_state(self, state):
        layers, sketches, text_layers, text_active_idx = state
        self.layers = [layer.copy() for layer in layers]
        self.sketch_items = [item for item in sketches]
        self.text_layers = copy.deepcopy(text_layers)
        self.text_active_idx = text_active_idx
        self.redraw_layers()

    def run(self):
        self.root.mainloop()

    def _get_full_bounds(self):
        # Refaktoryzacja: korzystamy z funkcji pomocniczej
        return get_bounds_from_layers_sketches_texts(self.layers, self.sketch_items, self.text_layers)

    # --- Nowa funkcja: wyśrodkowanie aktywnej warstwy ---
    def center_active_layer(self):
        """Wyśrodkuj aktywną warstwę względem wszystkich elementów."""
        if self.active_layer:
            min_x, min_y, max_x, max_y = self._get_full_bounds()
            canvas_w = max_x - min_x
            canvas_h = max_y - min_y
            layer = self.active_layer
            layer_w = layer["image"].width
            layer_h = layer["image"].height
            layer["x"] = min_x + (canvas_w - layer_w) // 2
            layer["y"] = min_y + (canvas_h - layer_h) // 2
            self.redraw_layers()
            self.status_var.set("Wyśrodkowano aktywną warstwę.")

    # Możesz dodać przycisk do UI, np. w setup_ui:
    # ttk.Button(button_frame1, text="Wyśrodkuj warstwę", command=self.center_active_layer).pack(side=tk.LEFT, padx=(0, 5))

if __name__ == "__main__":
    app = SnippingTool()
    app.run()