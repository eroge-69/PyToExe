import tkinter as tk
from tkinter import simpledialog, messagebox, Menu, Toplevel, scrolledtext, filedialog
import json
import os
import re
import math
import datetime

SAVE_FILE = "kerekpartarolo_canvas_state.json"
LOG_FILE = None
MAX_PER_RACK = 10
BASE_CANVAS_W = 1200
BASE_CANVAS_H = 800
BASE_RACK_W = 120
BASE_RACK_MIN_H = 200
BASE_FONT = 28
BASE_LABEL_FONT = 16
MIN_FONT = 11

def rotate_point(x, y, cx, cy, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    x -= cx
    y -= cy
    xr = x * cos_a - y * sin_a
    yr = x * sin_a + y * cos_a
    return xr + cx, yr + cy

def nowstr():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(text):
    if LOG_FILE:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{nowstr()} - {text}\n")

class RackBox:
    def __init__(self, app, idx, x, y, angle=0, bikes=None, name=None):
        self.app = app
        self.canvas = app.canvas
        self.idx = idx
        self.x = x
        self.y = y
        self.angle = angle
        self.bikes = bikes if bikes else []
        self.name = name or chr(65 + self.idx)
        self.items_all = []
        self.dragging = False
        self.label_id = None
        self.last_draw_size = (BASE_RACK_W, BASE_RACK_MIN_H)
        self.draw()

    def draw(self):
        for item in getattr(self, "items_all", []):
            self.canvas.delete(item)
        self.items_all = []
        scale = self.app.scale
        min_w, min_h = self.app.rack_w, self.app.rack_min_h
        w, h = min_w, min_h

        max_w = self.app.canvas.winfo_width() * 0.9
        max_h = self.app.canvas.winfo_height() * 0.9

        label_font_size = int(BASE_LABEL_FONT * scale)
        fit_font = label_font_size   # <-- A számok mindig a tároló nevének betűméretét kapják

        n = len(self.bikes)
        vertical = (self.angle % 180 == 0)
        need_w, need_h = w, h
        maxlen = max([len(str(b)) for b in self.bikes]) if self.bikes else 1

        if n > 0:
            char_w = maxlen * fit_font * 0.6 + fit_font * 0.8
            if vertical:
                need_h = max(h, n * (fit_font + 12) + 60)
            else:
                need_w = max(w, n * (char_w + 12) + 40)

        w, h = min(need_w, max_w), min(need_h, max_h)
        self.last_draw_size = (w, h)

        cx = self.x * scale + w/2
        cy = self.y * scale + h/2

        left, right = self.x * scale, self.x * scale + w
        top, bottom = self.y * scale, self.y * scale + h
        canvas_w = self.app.canvas.winfo_width()
        canvas_h = self.app.canvas.winfo_height()
        dx, dy = 0, 0
        if left < 0:
            dx = -left/scale
        elif right > canvas_w:
            dx = (canvas_w - right)/scale
        if top < 0:
            dy = -top/scale
        elif bottom > canvas_h:
            dy = (canvas_h - bottom)/scale
        if dx or dy:
            self.x += dx
            self.y += dy
            cx = self.x * scale + w/2
            cy = self.y * scale + h/2

        corners = [
            (self.x*scale, self.y*scale),
            (self.x*scale + w, self.y*scale),
            (self.x*scale + w, self.y*scale + h),
            (self.x*scale, self.y*scale + h),
        ]
        rcorners = [rotate_point(x, y, cx, cy, self.angle) for x, y in corners]
        rect = self.canvas.create_polygon(
            *sum(rcorners, ()),
            fill="#ececec", outline="#aaa", width=3*scale,
            tags=(f"rackbox_{self.idx}", "rackbox", f"movablezone_{self.idx}")
        )
        self.items_all.append(rect)
        if not self.app.move_mode:
            self.canvas.tag_bind(rect, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(rect, "<B1-Motion>", self.on_move)
            self.canvas.tag_bind(rect, "<ButtonRelease-1>", self.on_release)

        label_x, label_y = rotate_point(self.x*scale + w/2, self.y*scale + 28*scale, cx, cy, self.angle)
        self.label_id = self.canvas.create_text(
            label_x, label_y, text=self.name,
            angle=0, font=("Arial", label_font_size, "bold"),
            tags=(f"rackbox_{self.idx}", "rackbox", f"label_{self.idx}")
        )
        self.items_all.append(self.label_id)
        self.canvas.tag_bind(self.label_id, "<Double-1>", self.on_label_rename)

        self.bike_item_ids = []
        if n > 0:
            if vertical:
                total_height = n * (fit_font + 10)
                base_y = self.y*scale + 60*scale + (h - total_height)/2
                for i, bike in enumerate(self.bikes):
                    bx = self.x*scale + w/2
                    by = base_y + i*(fit_font+10)
                    rect_id = self.canvas.create_rectangle(
                        bx - w*0.35, by - fit_font/2-5, bx + w*0.35, by + fit_font/2+5,
                        fill="#e8f4ff", outline="#55aaff", width=2, tags=(f"bike_tile_{self.idx}_{i}","bike_rect"))
                    t = self.canvas.create_text(
                        bx, by, text=str(bike), angle=0,
                        font=("Arial", fit_font, "bold"),
                        tags=(f"rackbox_{self.idx}", "rackbox", f"bike_num_{bike}", "bike", f"bike_idx_{i}")
                    )
                    self.items_all.append(rect_id)
                    self.items_all.append(t)
                    self.bike_item_ids.append((t, bike))
                    self.canvas.tag_bind(rect_id, "<ButtonPress-1>", lambda e, idx=i: self.on_bike_drag_start(e, idx))
                    self.canvas.tag_bind(rect_id, "<B1-Motion>", lambda e, idx=i: self.on_bike_drag_motion(e, idx))
                    self.canvas.tag_bind(rect_id, "<ButtonRelease-1>", lambda e, idx=i: self.on_bike_drag_release(e, idx))
                    self.canvas.tag_bind(rect_id, "<ButtonPress-3>", lambda e, idx=i: self.on_bike_right_click(idx))
            else:
                total_width = n * (fit_font*maxlen*0.62 + fit_font*0.7 + 12)
                base_x = self.x*scale + (w - total_width)/2 + fit_font
                by = self.y*scale + h/2
                for i, bike in enumerate(self.bikes):
                    bx = base_x + i*(fit_font*maxlen*0.62 + fit_font*0.7 + 12)
                    bx, by2 = rotate_point(bx, by, cx, cy, self.angle)
                    rect_id = self.canvas.create_rectangle(
                        bx - fit_font*maxlen*0.36-7, by2 - fit_font/2-5, bx + fit_font*maxlen*0.36+7, by2 + fit_font/2+5,
                        fill="#e8f4ff", outline="#55aaff", width=2, tags=(f"bike_tile_{self.idx}_{i}","bike_rect"))
                    t = self.canvas.create_text(
                        bx, by2, text=str(bike), angle=0,
                        font=("Arial", fit_font, "bold"),
                        tags=(f"rackbox_{self.idx}", "rackbox", f"bike_num_{bike}", "bike", f"bike_idx_{i}")
                    )
                    self.items_all.append(rect_id)
                    self.items_all.append(t)
                    self.bike_item_ids.append((t, bike))
                    self.canvas.tag_bind(rect_id, "<ButtonPress-1>", lambda e, idx=i: self.on_bike_drag_start(e, idx))
                    self.canvas.tag_bind(rect_id, "<B1-Motion>", lambda e, idx=i: self.on_bike_drag_motion(e, idx))
                    self.canvas.tag_bind(rect_id, "<ButtonRelease-1>", lambda e, idx=i: self.on_bike_drag_release(e, idx))
                    self.canvas.tag_bind(rect_id, "<ButtonPress-3>", lambda e, idx=i: self.on_bike_right_click(idx))

        rot_bx, rot_by = rotate_point(self.x*scale + w - 18*scale, self.y*scale + 18*scale, cx, cy, self.angle)
        rot_btn = self.canvas.create_oval(
            rot_bx-12*scale, rot_by-12*scale, rot_bx+12*scale, rot_by+12*scale,
            fill="#6cf", outline="#339", width=2*scale, tags=(f"rotate_{self.idx}",))
        rot_icon = self.canvas.create_text(rot_bx, rot_by, text="⟳",
                                               font=("Arial", int(label_font_size*0.9), "bold"), tags=(f"rotate_{self.idx}",))
        self.items_all += [rot_btn, rot_icon]
        self.canvas.tag_bind(f"rotate_{self.idx}", "<ButtonPress-1>", self.on_rotate)

        del_bx, del_by = rotate_point(self.x*scale + 18*scale, self.y*scale + h - 18*scale, cx, cy, self.angle)
        del_btn = self.canvas.create_text(del_bx, del_by, text="🗑", font=("Arial", int(label_font_size*1.1)), fill="#d22",
                                          tags=(f"del_{self.idx}",))
        self.items_all.append(del_btn)
        self.canvas.tag_bind(del_btn, "<ButtonPress-1>", self.on_delete)

    def on_press(self, event):
        if self.app.move_mode:
            return
        self.dragging = True
        self.mouse_offset = (event.x_root, event.y_root, self.x, self.y)
        self.app.active_drag_rack = self

    def on_move(self, event):
        if not self.dragging or self.app.move_mode:
            return
        x0, y0, old_x, old_y = self.mouse_offset
        dx = (event.x_root - x0) / self.app.scale
        dy = (event.y_root - y0) / self.app.scale
        self.x = old_x + dx
        self.y = old_y + dy
        self.app.redraw_all()

    def on_release(self, event):
        if self.app.move_mode:
            return
        self.dragging = False
        self.app.active_drag_rack = None
        self.app.save_state()

    def on_rotate(self, event):
        self.angle = (self.angle + 90) % 360
        self.app.redraw_all()
        self.app.save_state()

    def on_delete(self, event):
        if messagebox.askyesno("Törlés", f"Biztos törlöd a(z) '{self.name}' tárolót?"):
            self.app.racks.remove(self)
            self.app.redraw_all()
            self.app.save_state()
            log_event(f"Tároló törölve: {self.name}")

    def on_bike_drag_start(self, event, idx):
        if self.app.move_mode:
            return
        self.app.bike_drag_mode = True
        self.dragged_bike = self.bikes[idx]
        self.dragged_idx = idx
        self.app.dragged_bike_from_rack = self
        self.app.dragged_bike_number = self.dragged_bike
        self.app.show_dragged_bike(event.x_root, event.y_root, str(self.dragged_bike))

    def on_bike_drag_motion(self, event, idx):
        if not self.app.bike_drag_mode or self.app.move_mode:
            return
        self.app.show_dragged_bike(event.x_root, event.y_root, str(self.dragged_bike))

    def on_bike_drag_release(self, event, idx):
        if not self.app.bike_drag_mode or self.app.move_mode:
            return
        drop_rack, drop_idx = self.app.get_bike_drop_target(event)
        from_rack = self.app.dragged_bike_from_rack
        bike = self.dragged_bike

        if drop_rack:
            if drop_rack is from_rack:
                if drop_idx is not None and drop_idx != self.dragged_idx:
                    from_rack.bikes.pop(self.dragged_idx)
                    from_rack.bikes.insert(drop_idx, bike)
            else:
                if bike in drop_rack.bikes or any(bike in r.bikes for r in self.app.racks if r is not from_rack):
                    self.app.msg("Ez a szám már máshol szerepel!")
                else:
                    from_rack.bikes.remove(bike)
                    drop_rack.bikes.insert(drop_idx if drop_idx is not None else len(drop_rack.bikes), bike)
                    log_event(f"Bicikli {bike} áthelyezve: {from_rack.name} -> {drop_rack.name}")
        self.dragged_bike = None
        self.app.bike_drag_mode = False
        self.app.dragged_bike_from_rack = None
        self.app.dragged_bike_number = None
        self.app.drop_target = None
        self.app.hide_dragged_bike()
        self.app.redraw_all()
        self.app.save_state()

    def on_bike_right_click(self, idx):
        num = self.bikes[idx]
        self.bikes.remove(num)
        self.app.msg(f"{num} törölve.")
        log_event(f"Bicikli {num} törölve: {self.name}")
        self.app.redraw_all()
        self.app.save_state()

    def on_label_rename(self, event):
        name = simpledialog.askstring("Tároló átnevezése", "Új név (1 karakter!):", initialvalue=self.name, parent=self.app.root)
        if name and len(name) == 1:
            old = self.name
            self.name = name.upper()
            log_event(f"Tároló átnevezve: {old} -> {self.name}")
            self.app.redraw_all()
            self.app.save_state()

    def get_state(self):
        return {"x": self.x, "y": self.y, "angle": self.angle, "bikes": self.bikes, "name": self.name}

class BikeRackCanvasApp:
    def __init__(self, root):
        self.root = root
        global LOG_FILE
        LOG_FILE = filedialog.asksaveasfilename(
            title="Válaszd ki a napló fájlt!",
            defaultextension=".txt",
            filetypes=[("Szövegfájl", "*.txt")]
        )
        if not LOG_FILE:
            root.destroy()
            return

        self.root.title("Kerékpártároló - naplóval")
        self.menu = Menu(root)
        self.root.config(menu=self.menu)
        file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Fájl", menu=file_menu)
        file_menu.add_command(label="Új tárolás (üresen)", command=self.reset_all)
        file_menu.add_command(label="Tárolás betöltése...", command=self.load_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Tároló mozgatása", command=self.start_rack_move_mode)
        file_menu.add_command(label="Mozgatás vége", command=self.stop_rack_move_mode)
        file_menu.add_separator()
        file_menu.add_command(label="Kilépés", command=self.on_close)
        naplo_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Napló", menu=naplo_menu)
        naplo_menu.add_command(label="Napló megtekintése", command=self.show_log)
        naplo_menu.add_command(label="Szám keresése naplóban", command=self.search_log)

        self.num_racks = simpledialog.askinteger("Tárolók száma", "Hány tároló legyen?", minvalue=1, maxvalue=20)
        if not self.num_racks:
            root.destroy()
            return

        self.canvas = tk.Canvas(root, width=BASE_CANVAS_W, height=BASE_CANVAS_H, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        control_frame = tk.Frame(root)
        control_frame.pack(fill="x", pady=5)
        tk.Label(control_frame, text="Szám(ok) feltöltése (pl. 12, B15, 33):", font=("Arial", 18, "bold")).pack(side=tk.LEFT, padx=10)
        self.entry = tk.Entry(control_frame, width=28, font=("Arial", 24, "bold"))
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", self.handle_entry)
        tk.Button(control_frame, text="Új tároló", command=self.add_rack, font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=8)
        self.msg_label = tk.Label(control_frame, text="", fg="red", font=("Arial", 16, "bold"))
        self.msg_label.pack(side=tk.LEFT, padx=10)
        tk.Label(control_frame, text="Keresés:", font=("Arial", 18, "bold")).pack(side=tk.LEFT, padx=15)
        self.search_entry = tk.Entry(control_frame, width=8, font=("Arial", 24, "bold"))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.handle_search)

        self.scale = 1.0
        self.rack_w = BASE_RACK_W
        self.rack_min_h = BASE_RACK_MIN_H

        self.dragged_bike = None
        self.dragged_bike_number = None
        self.dragged_bike_from_rack = None
        self.drag_label = None
        self.drag_label_bg = None
        self.bike_drag_mode = False
        self.drop_target = None

        self.active_drag_rack = None

        self.move_mode = False
        self.selected_rack = None
        self.arrow_ids = []

        self.racks = []
        self.add_racks()
        self.load_state()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_racks(self):
        self.racks = []
        COLS = 6
        for i in range(self.num_racks):
            col = i % COLS
            row = i // COLS
            x = 90 + col * (BASE_RACK_W + 60)
            y = 40 + row * (BASE_RACK_MIN_H + 50)
            name = chr(65 + i)
            rack = RackBox(self, i, x, y, name=name)
            self.racks.append(rack)

    def add_rack(self):
        name = simpledialog.askstring("Új tároló", "Név (1 karakter):")
        if name is None or len(name) != 1:
            return
        n = len(self.racks)
        COLS = 6
        col = n % COLS
        row = n // COLS
        x = 90 + col * (BASE_RACK_W + 60)
        y = 40 + row * (BASE_RACK_MIN_H + 50)
        rack = RackBox(self, n, x, y, name=name.upper())
        self.racks.append(rack)
        self.redraw_all()
        self.save_state()
        log_event(f"Új tároló hozzáadva: {name.upper()}")

    def reset_all(self):
        self.canvas.delete("all")
        self.add_racks()
        self.save_state()
        log_event("Új üres tárolás indítva")
        self.msg("Minden törölve.")

    def handle_entry(self, event):
        values = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not values:
            return
        entries = re.split(r'[,\s]+', values)
        name_map = {rack.name.upper(): rack for rack in self.racks}
        added, removed, rejected, full, dupl = [], [], [], [], []
        all_nums = {bike for rack in self.racks for bike in rack.bikes}
        for entry in entries:
            m = re.match(r"^([A-Za-z])?(\d+)$", entry)
            if not m:
                rejected.append(entry)
                continue
            rackname, bikeno = m.group(1), int(m.group(2))
            was = False
            for rack in self.racks:
                if bikeno in rack.bikes:
                    rack.bikes.remove(bikeno)
                    removed.append(f"{rack.name}{bikeno}")
                    log_event(f"Bicikli {bikeno} törölve: {rack.name}")
                    was = True
            if was:
                continue
            if bikeno in all_nums:
                dupl.append(bikeno)
                continue
            if rackname:
                rack = name_map.get(rackname.upper())
            else:
                rack = next((r for r in self.racks if len(r.bikes) < MAX_PER_RACK), None)
            if not rack:
                rejected.append(entry)
                continue
            if len(rack.bikes) >= MAX_PER_RACK:
                full.append(rack.name)
                continue
            rack.bikes.append(bikeno)
            added.append(f"{rack.name}{bikeno}")
            log_event(f"Bicikli {bikeno} hozzáadva: {rack.name}")
        self.redraw_all()
        self.save_state()
        msg = ""
        if added:
            msg += f"Feltöltve: {', '.join(added)}  "
        if removed:
            msg += f"Törölve: {', '.join(removed)}  "
        if full:
            msg += f"Teltház: {', '.join(set(full))}  "
        if rejected:
            msg += f"Hibás/Ismeretlen: {', '.join(rejected)}"
        if dupl:
            msg += f"Duplikált: {', '.join(str(x) for x in dupl)}"
        self.msg(msg)

    def load_menu(self):
        if not os.path.exists(SAVE_FILE):
            messagebox.showinfo("Nincs mentett állapot", "Nincs elérhető mentett tárolás!")
            return
        resp = messagebox.askquestion("Betöltés", "Tárolókat tartalommal együtt töltsük vissza? (Igen = tartalommal, Nem = csak üres tárolók)")
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.racks = []
        self.canvas.delete("all")
        if resp == "yes":
            for i, rack in enumerate(saved):
                rb = RackBox(self, i, rack["x"], rack["y"], rack.get("angle", 0), rack.get("bikes"), rack.get("name"))
                self.racks.append(rb)
            log_event("Tárolás visszatöltve tartalommal")
        else:
            for i, rack in enumerate(saved):
                rb = RackBox(self, i, rack["x"], rack["y"], rack.get("angle", 0), [], rack.get("name"))
                self.racks.append(rb)
            log_event("Tárolás váz (üresen) visszatöltve")
        self.redraw_all()
        self.save_state()
        self.msg("Betöltve.")

    def all_bike_numbers(self):
        return [bike for rack in self.racks for bike in rack.bikes]

    def msg(self, text):
        self.msg_label.config(text=text)
        self.root.after(4000, lambda: self.msg_label.config(text=""))

    def get_state(self):
        return [rack.get_state() for rack in self.racks]

    def save_state(self):
        state = self.get_state()
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.racks = []
            self.canvas.delete("all")
            for i, rack in enumerate(saved):
                rb = RackBox(self, i, rack["x"], rack["y"], rack.get("angle", 0), rack.get("bikes"), rack.get("name"))
                self.racks.append(rb)
        else:
            self.add_racks()

    def on_resize(self, event):
        scale_w = event.width / BASE_CANVAS_W
        scale_h = event.height / BASE_CANVAS_H
        self.scale = min(scale_w, scale_h)
        self.rack_w = BASE_RACK_W * self.scale
        self.rack_min_h = BASE_RACK_MIN_H * self.scale
        self.redraw_all()

    def redraw_all(self):
        self.canvas.delete("all")
        for rack in self.racks:
            rack.draw()
        if self.move_mode and self.selected_rack:
            self.show_rack_arrows()

    def show_dragged_bike(self, x, y, num):
        if self.drag_label:
            self.canvas.delete(self.drag_label)
        if self.drag_label_bg:
            self.canvas.delete(self.drag_label_bg)
        font_size = int(BASE_FONT * self.scale * 1.4)
        self.drag_label_bg = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="#ff8", outline="#bbb", width=2)
        self.drag_label = self.canvas.create_text(x, y, text=num, fill="#222", font=("Arial", font_size, "bold"))

    def hide_dragged_bike(self):
        if self.drag_label:
            self.canvas.delete(self.drag_label)
            self.drag_label = None
        if self.drag_label_bg:
            self.canvas.delete(self.drag_label_bg)
            self.drag_label_bg = None

    def set_drop_target(self, rack, idx):
        self.drop_target = rack

    def get_drop_target(self, event=None):
        if event:
            x, y = event.x_root, event.y_root
            min_dist = 999999
            target_rack = None
            for rack in self.racks:
                scale = self.scale
                w, h = rack.last_draw_size
                cx = rack.x*scale + w/2
                cy = rack.y*scale + h/2
                c_win = self.canvas.winfo_rootx(), self.canvas.winfo_rooty()
                cabs_x, cabs_y = c_win[0] + cx, c_win[1] + cy
                dist = (cabs_x - x)**2 + (cabs_y - y)**2
                if dist < min_dist:
                    min_dist = dist
                    target_rack = rack
            return target_rack
        else:
            return self.drop_target

    def get_bike_drop_target(self, event):
        x, y = event.x_root, event.y_root
        min_dist = 999999
        target_rack = None
        target_idx = None
        for rack in self.racks:
            for i, (item_id, _) in enumerate(rack.bike_item_ids):
                bbox = self.canvas.bbox(item_id)
                if bbox:
                    bx = (bbox[0] + bbox[2]) / 2 + self.canvas.winfo_rootx()
                    by = (bbox[1] + bbox[3]) / 2 + self.canvas.winfo_rooty()
                    dist = (bx - x) ** 2 + (by - y) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        target_rack = rack
                        target_idx = i
        if min_dist > 100**2:
            target_rack = self.get_drop_target(event)
            target_idx = None
        return target_rack, target_idx

    def handle_search(self, event):
        value = self.search_entry.get().strip()
        if not value.isdigit():
            self.msg("Csak szám lehet!")
            return
        num = int(value)
        found = False
        for rack in self.racks:
            if num in rack.bikes:
                self.flash_bike(rack, num)
                found = True
                break
        if not found:
            self.msg("Nincs ilyen kerékpár!")

    def flash_bike(self, rack, num):
        bike_id = None
        for item_id, bike in rack.bike_item_ids:
            if bike == num:
                bike_id = item_id
                break
        if not bike_id:
            return
        def flash(times=6):
            if times == 0:
                self.canvas.itemconfig(bike_id, fill="#222")
                return
            color = "#f00" if times % 2 == 1 else "#222"
            self.canvas.itemconfig(bike_id, fill=color)
            self.root.after(250, lambda: flash(times-1))
        flash()

    def show_log(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("Napló", "Nincs napló!")
            return
        win = Toplevel(self.root)
        win.title("Napló")
        win.geometry("800x500")
        txt = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        txt.pack(fill="both", expand=True)
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            txt.insert("end", f.read())
        txt.config(state="disabled")

    def search_log(self):
        num = simpledialog.askstring("Szám keresése naplóban", "Add meg a keresett bicikliszámot:")
        if not num or not num.isdigit():
            return
        result = []
        patt = re.compile(rf"\b{num}\b")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if patt.search(line):
                        result.append(line.strip())
        win = Toplevel(self.root)
        win.title(f"{num} naplóbejegyzései")
        win.geometry("800x400")
        txt = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        txt.pack(fill="both", expand=True)
        if result:
            txt.insert("end", "\n".join(result))
        else:
            txt.insert("end", f"Nincs bejegyzés {num} számra.")
        txt.config(state="disabled")

    def on_close(self):
        self.save_state()
        self.root.destroy()

    # -- Mozgatás mód START
    def start_rack_move_mode(self):
        self.move_mode = True
        self.selected_rack = None
        self.msg("Kattints egy tárolóra, amit mozgatni szeretnél!")
        self.canvas.bind("<Button-1>", self.pick_rack_for_move)
        self.redraw_all()

    def stop_rack_move_mode(self):
        self.move_mode = False
        self.selected_rack = None
        self.clear_rack_arrows()
        self.canvas.unbind("<Button-1>")
        self.msg("Mozgatás mód kikapcsolva.")
        self.redraw_all()

    def pick_rack_for_move(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for rack in self.racks:
            scale = self.scale
            w, h = rack.last_draw_size
            rx, ry = rack.x*scale, rack.y*scale
            if rx <= x <= rx+w and ry <= y <= ry+h:
                self.selected_rack = rack
                self.msg(f"Tároló kijelölve: {rack.name}. Használd a nyilakat!")
                self.redraw_all()
                break
        self.canvas.unbind("<Button-1>")

    def show_rack_arrows(self):
        self.clear_rack_arrows()
        rack = self.selected_rack
        if not rack:
            return
        scale = self.scale
        w, h = rack.last_draw_size
        cx = rack.x * scale + w/2
        cy = rack.y * scale + h/2
        arrow_size = 28 * scale
        self.arrow_ids = []
        for dx, dy, symbol, callback in [
            (0, -arrow_size, "▲", self.move_rack_up),
            (0, arrow_size, "▼", self.move_rack_down),
            (-arrow_size, 0, "◀", self.move_rack_left),
            (arrow_size, 0, "▶", self.move_rack_right),
        ]:
            btn = self.canvas.create_text(cx+dx, cy+dy, text=symbol, font=("Arial", int(arrow_size)), fill="red", tags="arrow_btn")
            self.arrow_ids.append(btn)
            self.canvas.tag_bind(btn, "<Button-1>", lambda e, f=callback: f())

    def clear_rack_arrows(self):
        for arrow in getattr(self, "arrow_ids", []):
            self.canvas.delete(arrow)
        self.arrow_ids = []

    def move_rack_up(self):
        if self.selected_rack:
            self.selected_rack.y -= 20
            self.redraw_all()
            self.save_state()

    def move_rack_down(self):
        if self.selected_rack:
            self.selected_rack.y += 20
            self.redraw_all()
            self.save_state()

    def move_rack_left(self):
        if self.selected_rack:
            self.selected_rack.x -= 20
            self.redraw_all()
            self.save_state()

    def move_rack_right(self):
        if self.selected_rack:
            self.selected_rack.x += 20
            self.redraw_all()
            self.save_state()
    # -- Mozgatás mód END

if __name__ == "__main__":
    root = tk.Tk()
    app = BikeRackCanvasApp(root)
    root.mainloop()
