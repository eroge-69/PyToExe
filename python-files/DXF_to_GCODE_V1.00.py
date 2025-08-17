import ezdxf
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import math
import numpy as np
from scipy.spatial import distance_matrix
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Circle

class DXFProcessor:
    def __init__(self, round_prec=4):
        self.circles = []  # list of (x, y, r)
        self.round_prec = round_prec  # precision for rounding generated points

    def load_dxf(self, file_path):
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        self.circles = [(e.dxf.center.x, e.dxf.center.y, e.dxf.radius) for e in msp.query("CIRCLE")]
        return self.circles

    def generate_points(self, center, num_points, spacing, direction):
        """Return list of points in a line along X or Y, rounding coords to reduce FP noise."""
        cx, cy = center
        pts = []
        for i in range(-num_points, num_points + 1):
            if direction == 'X':
                x = cx + i * spacing
                y = cy
            else:
                x = cx
                y = cy + i * spacing
            # round coordinates to avoid tiny FP differences
            x = round(x, self.round_prec)
            y = round(y, self.round_prec)
            pts.append((x, y))
        return pts

    def distance(self, p1, p2):
        if p1 is None or p2 is None:
            return float('inf')
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def optimize_tsp_greedy(self, points):
        """Greedy nearest neighbor like original (returns ordered points)."""
        if not points:
            return []
        pts = list(points)
        dist_mat = distance_matrix(pts, pts)
        n = len(pts)
        visited = [False] * n
        path = [0]
        visited[0] = True
        for _ in range(1, n):
            last = path[-1]
            cand = np.argmin([dist_mat[last][j] if not visited[j] else np.inf for j in range(n)])
            visited[cand] = True
            path.append(cand)
        return [pts[i] for i in path]

    def group_by_rounded(self, points, axis='y', round_prec=None):
        """Group points by rounded axis coordinate. axis='y' groups by y, 'x' by x."""
        if round_prec is None:
            round_prec = self.round_prec
        groups = {}
        if axis == 'y':
            for p in points:
                key = round(p[1], round_prec)
                groups.setdefault(key, []).append(p)
        else:
            for p in points:
                key = round(p[0], round_prec)
                groups.setdefault(key, []).append(p)
        return groups

    def optimize_zigzag_rows(self, points):
        groups = self.group_by_rounded(points, axis='y')
        ys = sorted(groups.keys(), reverse=True)  # top to bottom
        path = []
        reverse = False
        for y in ys:
            row = sorted(groups[y], key=lambda p: p[0])
            if reverse:
                row.reverse()
            path.extend(row)
            reverse = not reverse
        return path

    def optimize_zigzag_columns(self, points):
        groups = self.group_by_rounded(points, axis='x')
        xs = sorted(groups.keys())
        path = []
        reverse = False
        for x in xs:
            col = sorted(groups[x], key=lambda p: p[1])
            if reverse:
                col.reverse()
            path.extend(col)
            reverse = not reverse
        return path

    def optimize_raster_rows(self, points):
        groups = self.group_by_rounded(points, axis='y')
        ys = sorted(groups.keys(), reverse=True)
        path = []
        for y in ys:
            row = sorted(groups[y], key=lambda p: p[0])
            path.extend(row)
        return path

    def optimize_raster_columns(self, points):
        groups = self.group_by_rounded(points, axis='x')
        xs = sorted(groups.keys())
        path = []
        for x in xs:
            col = sorted(groups[x], key=lambda p: p[1])
            path.extend(col)
        return path

    def optimize_path(self, points, mode='tsp'):
        """Master optimizer: mode in ['none','tsp','zigzag_rows','zigzag_cols','raster_rows','raster_cols']"""
        if not points:
            return []
        if mode == 'none':
            return list(points)
        elif mode == 'tsp':
            return self.optimize_tsp_greedy(points)
        elif mode == 'zigzag_rows':
            return self.optimize_zigzag_rows(points)
        elif mode == 'zigzag_cols':
            return self.optimize_zigzag_columns(points)
        elif mode == 'raster_rows':
            return self.optimize_raster_rows(points)
        elif mode == 'raster_cols':
            return self.optimize_raster_columns(points)
        else:
            return list(points)

    def generate_gcode(self, all_points, z_safe_near, z_safe_far, spacing, z_final, xy_feed, z_feed, z_safe_home, optimize_mode='tsp'):
        """Generate G-code. Uses eps tolerance to avoid FP comparison issues with decimal spacing."""
        gcode = []
        gcode.append("T1M6")
        gcode.append(f"G0Z{z_safe_home:.3f}")
        gcode.append("G0X0.000Y0.000")

        ordered = self.optimize_path(all_points, mode=optimize_mode)

        prev = None
        eps = max(1e-6, abs(spacing) * 1e-6)

        for p in ordered:
            if p[0] == 0 and p[1] == 0:
                continue

            dist = self.distance(prev, p) if prev else float('inf')

            if dist <= spacing + eps:
                z_safe = z_safe_near
            else:
                z_safe = z_safe_far

            gcode.append(f"G0Z{z_safe:.3f}")
            gcode.append(f"G0X{p[0]:.3f}Y{p[1]:.3f}F{xy_feed:.1f}")
            gcode.append(f"G1Z{-abs(z_final):.3f}F{z_feed:.1f}")

            prev = p

        gcode.append(f"G0Z{z_safe_home:.3f}")
        gcode.append("G0X0.000Y0.000")
        gcode.append("M30")
        return gcode


class App:
    def __init__(self, root):
        self.processor = DXFProcessor()
        self.file_path = ""
        self.all_points = []
        self.ordered_points = []
        self.gcode_lines = []
        self.selected_circles = []  # indices of selected circles
        self.shift_pressed = False  # track if Shift is held

        root.title("DXF to G-Code Generator")
        root.geometry("1200x760")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

        # left control frame (uses grid)
        self.ctrl = ttk.Frame(root, padding=8)
        self.ctrl.grid(row=0, column=0, sticky="ns")

        ttk.Button(self.ctrl, text="بارگذاری فایل DXF", command=self.load_file).grid(row=0, column=0, columnspan=2, pady=(0,8), sticky="ew")

        # entries (left)
        self.entries = {}
        labels_left = [
            ("تعداد نقطه جوش x 2", "num_points"),
            ("فاصله بین نقاط جوش (mm)", "spacing"),
            ("Z-safe نقاط نزدیک (mm)", "z_safe_near"),
            ("Z-safe نقاط دور (mm)", "z_safe_far"),
            ("مقدار حرکت عمودی الکترود (mm)", "z_final"),
        ]
        for i, (lab, key) in enumerate(labels_left, start=1):
            ttk.Label(self.ctrl, text=lab).grid(row=i, column=0, sticky='w', pady=2)
            e = ttk.Entry(self.ctrl, width=12)
            e.grid(row=i, column=1, pady=2)
            self.entries[key] = e

        labels_right = [
            ("X/Y Feed Rate(mm/min)", "xy_feed"),
            ("Z Feed Rate(mm/min)", "z_feed"),
            ("Z-Safe Home(mm)", "z_safe_home"),
        ]
        for i, (lab, key) in enumerate(labels_right, start=1):
            ttk.Label(self.ctrl, text=lab).grid(row=i, column=2, sticky='w', padx=(10,0), pady=2)
            e = ttk.Entry(self.ctrl, width=12)
            e.grid(row=i, column=3, pady=2)
            self.entries[key] = e

        defaults = {
            'num_points': '2',
            'spacing': '1',
            'z_safe_near': '5',
            'z_safe_far': '10',
            'z_final': '1',
            'xy_feed': '800',
            'z_feed': '200',
            'z_safe_home': '15'
        }
        for k, v in defaults.items():
            if k in self.entries:
                self.entries[k].insert(0, v)

        self.direction = tk.StringVar(value='X')
        ttk.Label(self.ctrl, text="جهت ایجاد نقاط:").grid(row=6, column=0, sticky='w', pady=(6,0))
        ttk.Radiobutton(self.ctrl, text="X", variable=self.direction, value='X').grid(row=6, column=1, sticky='w')
        ttk.Radiobutton(self.ctrl, text="Y", variable=self.direction, value='Y').grid(row=7, column=1, sticky='w')

        ttk.Label(self.ctrl, text="حالت بهینه‌سازی مسیر حرکت الکترود:").grid(row=8, column=0, columnspan=2, sticky='w', pady=(8,0))
        self.optimize_mode = tk.StringVar(value='tsp')
        opt_modes = [
            ("بدون بهینه‌سازی", 'none'),
            ("TSP کل نقاط (گرِیدی)", 'tsp'),
            ("زیگزاگ ردیفی (گروه‌بندی بر اساس Y)", 'zigzag_rows'),
            ("زیگزاگ ستونی (گروه‌بندی بر اساس X)", 'zigzag_cols'),
            ("ردیفی (rows left->right)", 'raster_rows'),
            ("ستونی (columns bottom->top)", 'raster_cols'),
        ]
        for i, (txt, val) in enumerate(opt_modes, start=9):
            ttk.Radiobutton(self.ctrl, text=txt, variable=self.optimize_mode, value=val).grid(row=i, column=0, columnspan=4, sticky='w')

        ttk.Button(self.ctrl, text="تولید نقاط از فایل", command=self.create_points).grid(row=15, column=0, columnspan=2, pady=(8,4), sticky="ew")
        ttk.Button(self.ctrl, text="تولید G-code", command=self.process).grid(row=15, column=2, columnspan=2, pady=(8,4), sticky="ew")
        ttk.Button(self.ctrl, text="تولید نقاط از دایره‌های انتخاب شده", command=self.create_points_from_selected_circles).grid(row=16, column=0, columnspan=4, pady=(8,4), sticky="ew")
        ttk.Button(self.ctrl, text="ذخیره G-code (.tap)", command=self.save_gcode).grid(row=17, column=0, columnspan=4, pady=(4,0), sticky="ew")

        ttk.Label(self.ctrl, text="اطلاعات آماری:").grid(row=18, column=0, columnspan=4, sticky='w', pady=(8,0))
        self.info_box = tk.Text(self.ctrl, width=40, height=6, state='disabled', bg="#f7f7f7")
        self.info_box.grid(row=19, column=0, columnspan=4, pady=(2,6))

        ttk.Label(self.ctrl, text="پیش‌نمایش G-code:").grid(row=20, column=0, columnspan=4, sticky='w')
        self.output_frame = ttk.Frame(self.ctrl)
        self.output_frame.grid(row=21, column=0, columnspan=4, sticky="nsew", pady=(2,6))
        self.ctrl.grid_rowconfigure(21, weight=1)
        self.output_scroll = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL)
        self.output_box = tk.Text(self.output_frame, width=60, height=18, yscrollcommand=self.output_scroll.set)
        self.output_scroll.config(command=self.output_box.yview)
        self.output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.plot_frame = ttk.Frame(root)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(7,7))
        self.ax.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self._dragging = False
        self._last_event = None

        self.refresh_info()

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
        if not path:
            return
        try:
            circles = self.processor.load_dxf(path)
            self.file_path = path
            messagebox.showinfo("موفق", f"{len(circles)} دایره شناسایی شد.")
            self.all_points = []
            self.ordered_points = []
            self.gcode_lines = []
            self.selected_circles = []
            self.output_box.delete("1.0", tk.END)
            self.info_box.config(state='normal')
            self.info_box.delete("1.0", tk.END)
            self.info_box.insert(tk.END, f"فایل: {path}\nتعداد دایره‌ها: {len(circles)}\nتعداد نقاط تولید شده: 0\nتعداد نقاط بهینه: 0\n")
            self.info_box.config(state='disabled')
            self.plot_points([], self.processor.circles)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری DXF:\n{e}")

    def create_points_from_selected_circles(self):
        if not self.selected_circles:
            messagebox.showwarning("هشدار", "هیچ دایره‌ای انتخاب نشده است.")
            return

        try:
            num_points = int(self.entries['num_points'].get().strip())
            spacing = float(self.entries['spacing'].get().strip())
        except Exception:
            messagebox.showerror("خطا", "لطفاً تعداد نقاط و فاصله را درست وارد کنید.")
            return

        pts = []
        for idx in self.selected_circles:
            c = self.processor.circles[idx]
            center = (c[0], c[1])
            new_pts = self.processor.generate_points(center, num_points, spacing, self.direction.get())
            pts.extend(new_pts)

        self.all_points = pts
        self.ordered_points = []
        self.gcode_lines = []
        self.output_box.delete("1.0", tk.END)
        self.refresh_info()
        self.plot_points(self.all_points, self.processor.circles)
        messagebox.showinfo("موفق", f"{len(self.all_points)} نقطه تولید شد.")

    def create_points(self):
        try:
            num_points = int(self.entries['num_points'].get().strip())
            spacing = float(self.entries['spacing'].get().strip())
        except Exception:
            messagebox.showerror("خطا", "لطفاً تعداد نقاط و فاصله را درست وارد کنید.")
            return
        if not self.processor.circles:
            messagebox.showwarning("هشدار", "ابتدا فایل DXF بارگذاری شود.")
            return
        pts = []
        for c in self.processor.circles:
            center = (c[0], c[1])
            new_pts = self.processor.generate_points(center, num_points, spacing, self.direction.get())
            pts.extend(new_pts)
        self.all_points = pts
        self.ordered_points = []
        self.gcode_lines = []
        self.output_box.delete("1.0", tk.END)
        self.refresh_info()
        self.plot_points(self.all_points, self.processor.circles)
        messagebox.showinfo("موفق", f"{len(self.all_points)} نقطه تولید شد.")

    def process(self):
        """Generate G-code using current parameters and selected optimizer."""
        try:
            num_points = int(self.entries['num_points'].get().strip())
            spacing = float(self.entries['spacing'].get().strip())
            z_safe_near = float(self.entries['z_safe_near'].get().strip())
            z_safe_far = float(self.entries['z_safe_far'].get().strip())
            z_final = float(self.entries['z_final'].get().strip())
            xy_feed = float(self.entries['xy_feed'].get().strip())
            z_feed = float(self.entries['z_feed'].get().strip())
            z_safe_home = float(self.entries['z_safe_home'].get().strip())
        except Exception:
            messagebox.showerror("خطا", "لطفاً همهٔ پارامترها را چک کنید.")
            return
        if not self.all_points:
            messagebox.showwarning("هشدار", "ابتدا نقاط را تولید کنید.")
            return

        mode = self.optimize_mode.get()
        self.gcode_lines = self.processor.generate_gcode(self.all_points, z_safe_near, z_safe_far, spacing, z_final, xy_feed, z_feed, z_safe_home, optimize_mode=mode)
        self.ordered_points = self.processor.optimize_path(self.all_points, mode=mode)

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "\n".join(self.gcode_lines))

        self.refresh_info()
        self.plot_points(self.all_points, self.processor.circles, path=self.ordered_points)
        messagebox.showinfo("انجام شد", "G-code تولید شد و در پنجره پیش‌نمایش قرار گرفت.")

    def save_gcode(self):
        if not self.gcode_lines:
            messagebox.showwarning("هشدار", "ابتدا G-code تولید شود.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".tap", filetypes=[("TAP Files", "*.tap"), ("All Files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.gcode_lines))
            messagebox.showinfo("ذخیره شد", f"G-code ذخیره شد:\n{path}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل:\n{e}")

    def refresh_info(self):
        circles_count = len(self.processor.circles)
        pts_count = len(self.all_points)
        ordered_count = len(self.ordered_points) if self.ordered_points else 0
        self.info_box.config(state='normal')
        self.info_box.delete("1.0", tk.END)
        file_label = self.file_path if self.file_path else "هیچ فایلی انتخاب نشده"
        self.info_box.insert(tk.END, f"فایل: {file_label}\n")
        self.info_box.insert(tk.END, f"تعداد دایره‌ها: {circles_count}\n")
        self.info_box.insert(tk.END, f"تعداد نقاط تولید شده: {pts_count}\n")
        self.info_box.insert(tk.END, f"تعداد نقاط در مسیر بهینه: {ordered_count}\n")
        self.info_box.config(state='disabled')

    def plot_points(self, points, centers, path=None):
        self.ax.clear()
        if centers:
            for idx, (x, y, r) in enumerate(centers):
                if idx in self.selected_circles:
                    c = Circle((x, y), r, fill=False, edgecolor='yellow', linewidth=2)
                else:
                    c = Circle((x, y), r, fill=False, edgecolor='green', linewidth=1)
                self.ax.add_patch(c)
            cx = [c[0] for c in centers]
            cy = [c[1] for c in centers]
            self.ax.scatter(cx, cy, c='red', s=10, label='centers')
        if points:
            px = [p[0] for p in points]
            py = [p[1] for p in points]
            self.ax.scatter(px, py, c='blue', s=8, label='generated points', alpha=0.7)
        if path:
            px = [p[0] for p in path]
            py = [p[1] for p in path]
            self.ax.plot(px, py, '-r', linewidth=1, label='ordered path')
            self.ax.scatter(px, py, c='red', s=20)
        self.ax.legend(loc='upper right')
        self.ax.set_aspect('equal', 'box')
        self.ax.set_title("Display weld points and path")
        self.ax.grid(True)
        self.canvas.draw_idle()

    def on_scroll(self, event):
        if event.inaxes is None:
            return
        base_scale = 1.1
        ax = event.inaxes
        xdata = event.xdata
        ydata = event.ydata
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes is None:
            return

        if event.button == 1:
            clicked_circle = None
            for idx, (x, y, r) in enumerate(self.processor.circles):
                dist = math.hypot(event.xdata - x, event.ydata - y)
                if dist <= r:
                    clicked_circle = idx
                    break

            if clicked_circle is not None:
                try:
                    self.shift_pressed = (event.key == 'shift') if event.key else False
                except Exception:
                    self.shift_pressed = False

                if self.shift_pressed:
                    if clicked_circle not in self.selected_circles:
                        self.selected_circles.append(clicked_circle)
                else:
                    if clicked_circle in self.selected_circles:
                        self.selected_circles.remove(clicked_circle)
                    else:
                        self.selected_circles = [clicked_circle]

                return
            else:
                self._dragging = True
                self._last_event = event

    def on_release(self, event):
        if self.shift_pressed:
            self.plot_points(self.all_points, self.processor.circles, path=self.ordered_points)
            self.shift_pressed = False
        self._dragging = False
        self._last_event = None

    def on_motion(self, event):
        if not self._dragging or event.inaxes is None or self._last_event is None:
            return
        dx = event.xdata - self._last_event.xdata
        dy = event.ydata - self._last_event.ydata
        ax = event.inaxes
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
        ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)
        self.canvas.draw_idle()
        self._last_event = event


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
