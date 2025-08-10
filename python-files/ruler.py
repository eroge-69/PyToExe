import math
import tkinter as tk
from tkinter import ttk

APP_TITLE = "Pixel Ruler — Click & drag to measure"

class PixelRuler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x520")
        self.minsize(500, 300)
        self.attributes("-topmost", True)

        self.mode = tk.StringVar(value="line")
        self.opacity = tk.DoubleVar(value=0.92)
        self.start = None
        self.end = None

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(bar, text="Mode:").pack(side=tk.LEFT, padx=(0,4))
        ttk.Radiobutton(bar, text="Line", variable=self.mode, value="line", command=self._redraw).pack(side=tk.LEFT)
        ttk.Radiobutton(bar, text="Rect", variable=self.mode, value="rect", command=self._redraw).pack(side=tk.LEFT, padx=(6,12))

        ttk.Label(bar, text="Opacity").pack(side=tk.LEFT)
        op = ttk.Scale(bar, from_=0.3, to=1.0, variable=self.opacity, command=self._set_opacity, length=130)
        op.pack(side=tk.LEFT, padx=(4,12))
        ttk.Button(bar, text="Reset", command=self._reset).pack(side=tk.LEFT)
        ttk.Button(bar, text="Copy", command=self._copy_readout).pack(side=tk.LEFT, padx=(6,0))
        ttk.Label(bar, text="Tip: Press M to toggle modes • ESC to clear").pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0, cursor="tcross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status = tk.StringVar(value="Ready. Click & drag to measure.")
        st = ttk.Label(self, textvariable=self.status, anchor="w")
        st.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)

        self.line_item = None
        self.rect_item = None
        self.cross1 = None
        self.cross2 = None
        self.text_bg = None
        self.text_item = None

        self._draw_grid()

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda e: self._reset())
        self.bind("<m>", self._toggle_mode)
        self.bind("<M>", self._toggle_mode)
        self.bind("<Configure>", lambda e: self._draw_grid())

    def _toggle_mode(self, *_):
        self.mode.set("rect" if self.mode.get() == "line" else "line")
        self._redraw()

    def _set_opacity(self, *_):
        try:
            self.wm_attributes("-alpha", float(self.opacity.get()))
        except Exception:
            pass

    def _draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        major = 100
        minor = 20
        for x in range(0, w, minor):
            self.canvas.create_line(x, 0, x, h, fill="#2b2b2b", tags="grid")
        for y in range(0, h, minor):
            self.canvas.create_line(0, y, w, y, fill="#2b2b2b", tags="grid")
        for x in range(0, w, major):
            self.canvas.create_line(x, 0, x, h, fill="#3f3f3f", width=2, tags="grid")
        for y in range(0, h, major):
            self.canvas.create_line(0, y, w, y, fill="#3f3f3f", width=2, tags="grid")
        for x in range(0, w, major):
            self.canvas.create_text(x+2, 12, text=str(x), fill="#9e9e9e", anchor="w", font=("Segoe UI", 9), tags="grid")
        for y in range(0, h, major):
            self.canvas.create_text(6, y+2, text=str(y), fill="#9e9e9e", anchor="w", font=("Segoe UI", 9), tags="grid")

    def _on_press(self, event):
        self.start = (event.x, event.y)
        self.end = (event.x, event.y)
        self._redraw()

    def _on_drag(self, event):
        if self.start is None:
            return
        self.end = (event.x, event.y)
        self._redraw()

    def _on_release(self, event):
        if self.start is None:
            return
        self.end = (event.x, event.y)
        self._redraw(final=True)

    def _reset(self):
        self.start = None
        self.end = None
        for item in (self.line_item, self.rect_item, self.cross1, self.cross2, self.text_bg, self.text_item):
            if item:
                self.canvas.delete(item)
        self.status.set("Cleared. Click & drag to measure.")

    def _copy_readout(self):
        text = self._build_readout()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status.set(f"Copied: {text}")

    def _build_readout(self):
        if not (self.start and self.end):
            return ""
        x0, y0 = self.start
        x1, y1 = self.end
        dx = x1 - x0
        dy = y1 - y0
        w = abs(dx)
        h = abs(dy)
        dist = math.hypot(dx, dy)
        if self.mode.get() == "line":
            return f"dx={dx}px, dy={dy}px, dist={dist:.1f}px"
        else:
            return f"width={w}px, height={h}px"

    def _redraw(self, final=False):
        for item in (self.line_item, self.rect_item, self.cross1, self.cross2, self.text_bg, self.text_item):
            if item:
                self.canvas.delete(item)
        self.line_item = self.rect_item = self.cross1 = self.cross2 = self.text_bg = self.text_item = None
        if not (self.start and self.end):
            return
        x0, y0 = self.start
        x1, y1 = self.end
        if self.mode.get() == "line":
            self.line_item = self.canvas.create_line(x0, y0, x1, y1, fill="#00d4ff", width=2)
            self.cross1 = self._cross(x0, y0, color="#00d4ff")
            self.cross2 = self._cross(x1, y1, color="#00d4ff")
        else:
            self.rect_item = self.canvas.create_rectangle(x0, y0, x1, y1, outline="#ffcc00", width=2)
            self.cross1 = self._cross(x0, y0, color="#ffcc00")
            self.cross2 = self._cross(x1, y1, color="#ffcc00")
        text = self._build_readout()
        cx, cy = x1 + 12, y1 + 12
        pad = 6
        bbox = self.canvas.create_rectangle(cx - pad, cy - pad, cx + 150, cy + 22, fill="#000", outline="")
        self.text_bg = bbox
        self.text_item = self.canvas.create_text(cx, cy, text=text, fill="#fff", anchor="nw", font=("Segoe UI", 10, "bold"))
        self.status.set(text)

    def _cross(self, x, y, color="#ffcc00", size=6):
        h1 = self.canvas.create_line(x - size, y, x + size, y, fill=color, width=2)
        h2 = self.canvas.create_line(x, y - size, x, y + size, fill=color, width=2)
        return h1, h2

if __name__ == "__main__":
    app = PixelRuler()
    app._set_opacity()
    app.mainloop()
