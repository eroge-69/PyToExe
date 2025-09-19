# crosshair_z_advanced_plus.py
"""
Crosshair Z — Advanced+
- Windows-only global hotkeys (keyboard)
- Cached GPU-friendly glow (pre-rendered pixmap on settings changes)
- Live preview + overlay
- Presets folder + cycling and quick-save
"""

import sys, os, json, ctypes, time, traceback, subprocess
from pathlib import Path
from copy import deepcopy

# ---------------- auto-install minimal deps ----------------
REQUIRED = ["pyqt5", "keyboard"]
def install_missing():
    for pkg in REQUIRED:
        name = pkg.split("==")[0]
        try:
            __import__(name)
        except ImportError:
            print(f"[installer] Installing {pkg} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
try:
    install_missing()
except Exception as e:
    print("Auto-install failed; please run: pip install pyqt5 keyboard")
    raise

# ---------------- admin elevation (Windows) ----------------
def ensure_admin_windows():
    if os.name != "nt":
        return
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        params = " ".join([f'"{p}"' for p in sys.argv])
        python_exe = sys.executable
        ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
        sys.exit(0)

# We try to get admin so hotkeys and click-through work reliably.
ensure_admin_windows()

# ---------------- imports ----------------
try:
    import keyboard
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
        QSlider, QComboBox, QCheckBox, QColorDialog, QFileDialog, QListWidget,
        QStackedWidget, QInputDialog
    )
    from PyQt5.QtCore import Qt, QTimer, QSize, QRect
    from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont
except Exception:
    traceback.print_exc()
    raise

# ---------------- paths & defaults ----------------
BASE_DIR = Path(__file__).parent
PRESETS_FILE = BASE_DIR / "crosshair_presets.json"
PRESETS_DIR = BASE_DIR / "presets"
PRESETS_DIR.mkdir(exist_ok=True)
PRESETS_FILE.touch(exist_ok=True)

DEFAULT_PRESETS = {
    "current": "Default",
    "presets": {
        "Default": {
            "shape": "X",
            "size": 20,
            "thickness": 2.0,
            "gap": 0,
            "color": [0, 200, 80],
            "opacity": 0.95,
            "outline": True,
            "outline_color": [0,0,0],
            "outline_thickness": 2.0,
            "outline_style": "Rounded",
            "glow": False,
            "glow_color": [0,200,80],
            "glow_radius": 8,
            "dot_alpha": 1.0,
            "offset_x": 0,
            "offset_y": 0
        }
    }
}

def load_presets_file():
    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "presets" not in data:
            raise Exception("invalid")
        return data
    except Exception:
        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PRESETS, f, indent=2)
        return deepcopy(DEFAULT_PRESETS)

def save_presets_file(data):
    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------------- crosshair rendering (cached pixmap) ----------------
def render_crosshair_pixmap(cfg, px_size=512):
    """
    Render the crosshair (with outline and glow) into an RGBA QPixmap of px_size x px_size,
    centered. Return QPixmap.
    This function is called only when settings change and its result is cached.
    """
    size = px_size
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)

    cx = size // 2
    cy = size // 2

    # configurable values
    shape = cfg.get("shape", "X")
    L = int(cfg.get("size", 20))
    gap = int(cfg.get("gap", 0))
    inner_thickness = max(0.5, float(cfg.get("thickness", 1.0)))
    r,g,b = (cfg.get("color", [0,200,80]) + [0,0,0])[:3]
    outline = bool(cfg.get("outline", False))
    or_, og, ob = (cfg.get("outline_color", [0,0,0]) + [0,0,0])[:3]
    outline_thickness = max(0.0, float(cfg.get("outline_thickness", 0.0)))
    outline_style = cfg.get("outline_style", "Rounded")
    glow = bool(cfg.get("glow", False))
    gr = int(cfg.get("glow_radius", 8))
    gr = max(0, min(gr, 80))
    gr_color = (cfg.get("glow_color", [r,g,b]) + [0,0,0])[:3]
    dot_alpha = float(cfg.get("dot_alpha", 1.0))
    # offset won't affect pixmap shape; applied at draw time (translation)

    # Helper to draw basic line to painter
    def draw_line_to(p, x1, y1, x2, y2, pen):
        p.setPen(pen)
        p.drawLine(x1, y1, x2, y2)

    # Create pens
    inner_pen = QPen(QColor(r,g,b))
    inner_pen.setWidthF(inner_thickness)
    inner_pen.setCapStyle(Qt.RoundCap)
    inner_pen.setJoinStyle(Qt.RoundJoin)

    # Outline pen width = inner + outline_thickness
    if outline and outline_thickness > 0:
        out_pen = QPen(QColor(or_,og,ob))
        out_pen.setWidthF(max(0.5, inner_thickness + outline_thickness))
        if outline_style == "Rounded":
            out_pen.setCapStyle(Qt.RoundCap)
            out_pen.setJoinStyle(Qt.RoundJoin)
        else:
            out_pen.setCapStyle(Qt.SquareCap)
            out_pen.setJoinStyle(Qt.MiterJoin)
    else:
        out_pen = None

    # Glow rendering: simulate blur by drawing multiple translucent outlines expanding outward.
    # We pre-render glow by drawing thicker translucent strokes.
    if glow and gr > 0:
        # draw multiple rings with decreasing alpha
        max_iter = max(4, min(40, gr // 1 + 2))
        for i in range(max_iter, 0, -1):
            # radius factor
            factor = i / max_iter
            alpha = int(40 * factor)  # small alpha per ring
            pen_width = inner_thickness + outline_thickness + (gr * factor)
            glow_pen = QPen(QColor(gr_color[0], gr_color[1], gr_color[2], alpha))
            glow_pen.setWidthF(pen_width)
            glow_pen.setCapStyle(Qt.RoundCap)
            glow_pen.setJoinStyle(Qt.RoundJoin)
            # draw shape with glow_pen
            if shape == "X":
                draw_line_to(painter, cx - L, cy - L, cx + L, cy + L, glow_pen)
                draw_line_to(painter, cx - L, cy + L, cx + L, cy - L, glow_pen)
            elif shape == "+":
                draw_line_to(painter, cx - L, cy, cx - gap, cy, glow_pen)
                draw_line_to(painter, cx + gap, cy, cx + L, cy, glow_pen)
                draw_line_to(painter, cx, cy - L, cx, cy - gap, glow_pen)
                draw_line_to(painter, cx, cy + gap, cx, cy + L, glow_pen)
            elif shape == "T":
                draw_line_to(painter, cx - L, cy, cx + L, cy, glow_pen)
                draw_line_to(painter, cx, cy, cx, cy + L, glow_pen)
            elif shape == "Dot":
                gp = QPen(QColor(gr_color[0], gr_color[1], gr_color[2], int(alpha)))
                gp.setWidthF(pen_width)
                painter.setPen(gp)
                painter.setBrush(QColor(gr_color[0], gr_color[1], gr_color[2], int(alpha)))
                # draw circle slightly larger
                painter.drawEllipse(cx - int(pen_width/2), cy - int(pen_width/2), int(pen_width), int(pen_width))
            elif shape == "Circle":
                gp = QPen(QColor(gr_color[0], gr_color[1], gr_color[2], int(alpha)))
                gp.setWidthF(pen_width)
                painter.setPen(gp)
                painter.drawEllipse(cx - L//2, cy - L//2, L, L)
            elif shape == "Hairline":
                gp = QPen(QColor(gr_color[0], gr_color[1], gr_color[2], int(alpha)))
                gp.setWidthF(max(1.0, pen_width))
                gp.setCapStyle(Qt.RoundCap)
                gp.setJoinStyle(Qt.RoundJoin)
                draw_line_to(painter, cx - L, cy, cx + L, cy, gp)
                draw_line_to(painter, cx, cy - L, cx, cy + L, gp)

    # Draw outline (if any)
    if out_pen:
        painter.setPen(out_pen)
        if shape == "X":
            painter.drawLine(cx - L, cy - L, cx + L, cy + L)
            painter.drawLine(cx - L, cy + L, cx + L, cy - L)
        elif shape == "+":
            painter.drawLine(cx - L, cy, cx - gap, cy)
            painter.drawLine(cx + gap, cy, cx + L, cy)
            painter.drawLine(cx, cy - L, cx, cy - gap)
            painter.drawLine(cx, cy + gap, cx, cy + L)
        elif shape == "T":
            painter.drawLine(cx - L, cy, cx + L, cy)
            painter.drawLine(cx, cy, cx, cy + L)
        elif shape == "Dot":
            painter.setBrush(QColor(or_,og,ob))
            painter.drawEllipse(cx - 3 - int(outline_thickness), cy - 3 - int(outline_thickness),
                                6 + int(outline_thickness*2), 6 + int(outline_thickness*2))
        elif shape == "Circle":
            painter.drawEllipse(cx - L//2, cy - L//2, L, L)
        elif shape == "Hairline":
            painter.drawLine(cx - L, cy, cx + L, cy)
            painter.drawLine(cx, cy - L, cx, cy + L)

    # Draw inner (foreground) lines/dot
    painter.setPen(inner_pen)
    painter.setBrush(QColor(r,g,b))
    if shape == "X":
        painter.drawLine(cx - L, cy - L, cx + L, cy + L)
        painter.drawLine(cx - L, cy + L, cx + L, cy - L)
    elif shape == "+":
        painter.drawLine(cx - L, cy, cx - gap, cy)
        painter.drawLine(cx + gap, cy, cx + L, cy)
        painter.drawLine(cx, cy - L, cx, cy - gap)
        painter.drawLine(cx, cy + gap, cx, cy + L)
    elif shape == "T":
        painter.drawLine(cx - L, cy, cx + L, cy)
        painter.drawLine(cx, cy, cx, cy + L)
    elif shape == "Dot":
        # dot alpha applied via brush
        dot_color = QColor(r,g,b)
        dot_color.setAlphaF(max(0.0, min(1.0, float(cfg.get("dot_alpha", 1.0)))))
        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 2, cy - 2, 4, 4)
    elif shape == "Circle":
        painter.drawEllipse(cx - L//2, cy - L//2, L, L)
    elif shape == "Hairline":
        thin_pen = QPen(QColor(r,g,b))
        thin_pen.setWidthF(0.5)
        thin_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(thin_pen)
        painter.drawLine(cx - L, cy, cx + L, cy)
        painter.drawLine(cx, cy - L, cx, cy + L)

    painter.end()
    return pm

# ---------------- overlay widget (uses cached pixmap) ----------------
class CachedOverlay(QWidget):
    def __init__(self, cfg):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.cfg = deepcopy(cfg)
        self.setWindowOpacity(self.cfg.get("opacity", 0.95))
        # cached pixmap and scale
        self.cached = None
        self.cached_cfg_hash = None
        self.cached_size = 512
        self._update_cache()

        # try click-through (Windows)
        if os.name == "nt":
            try:
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                WS_EX_TRANSPARENT = 0x20
                hwnd = self.winId().__int__()
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            except Exception:
                pass

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def _cfg_hash(self, cfg):
        # cheaply hash relevant visual settings so we can detect changes
        keys = ("shape","size","thickness","gap","color","outline","outline_color","outline_thickness","outline_style","glow","glow_color","glow_radius","dot_alpha")
        return tuple((k, str(cfg.get(k))) for k in keys)

    def _update_cache(self):
        h = self._cfg_hash(self.cfg)
        if h != self.cached_cfg_hash or self.cached is None:
            # pick px size relative to size value so glow has room
            base = max(256, min(2048, int(self.cfg.get("size",20) * 16 + 256)))
            self.cached_size = base
            self.cached = render_crosshair_pixmap(self.cfg, px_size=self.cached_size)
            self.cached_cfg_hash = h

    def update_settings(self, cfg):
        self.cfg = deepcopy(cfg)
        self.setWindowOpacity(self.cfg.get("opacity", 0.95))
        self._update_cache()

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        # use cached pixmap and draw it centered + offset
        if self.cached:
            cw = self.cached.width()
            ch = self.cached.height()
            # position center plus offsets
            offset_x = int(self.cfg.get("offset_x", 0))
            offset_y = int(self.cfg.get("offset_y", 0))
            sx = (self.width() - cw) // 2 + offset_x
            sy = (self.height() - ch) // 2 + offset_y
            painter.drawPixmap(sx, sy, self.cached)
        painter.end()

# ---------------- preview widget (uses same cache function) ----------------
class PreviewWidget(QWidget):
    def __init__(self, cfg, size=220):
        super().__init__()
        self.setFixedSize(QSize(size, size))
        self.cfg = deepcopy(cfg)
        self.cache = render_crosshair_pixmap(self.cfg, px_size=min(512, size*2))

    def set_config(self, cfg):
        self.cfg = deepcopy(cfg)
        self.cache = render_crosshair_pixmap(self.cfg, px_size=min(512, max(256, int(self.cfg.get("size",20)*8+128))))
        self.update()

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.cache:
            cw = self.cache.width()
            ch = self.cache.height()
            sx = (self.width() - cw)//2
            sy = (self.height() - ch)//2
            painter.drawPixmap(sx, sy, self.cache)
        painter.end()

# ---------------- UI ----------------
class CrosshairZApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crosshair Z")
        self.setGeometry(120, 120, 900, 580)
        self.setStyleSheet("""
            QWidget { background: #232323; color: #f0f0f0; font-family: Segoe UI, Roboto, Arial; }
            QPushButton { background: #323232; border-radius: 8px; padding: 8px; }
            QPushButton:hover { background: #3fae77; color: black; }
            QListWidget { background: #1b1b1b; border: none; }
            QLabel.title { font-size:18px; font-weight:700; }
        """)
        # load presets/global config (current)
        self.presets_data = load_presets_file()
        current_name = self.presets_data.get("current", "Default")
        self.config = deepcopy(self.presets_data["presets"].get(current_name, DEFAULT_PRESETS["presets"]["Default"]))

        # overlay (cached)
        self.overlay = CachedOverlay(self.config)
        self.overlay.show()

        # build UI
        self._build_ui()

        # register hotkeys (Windows)
        self._register_hotkeys()

    def _build_ui(self):
        root = QHBoxLayout(self)

        # sidebar
        sidebar = QListWidget()
        sidebar.setFixedWidth(160)
        sidebar.addItems(["Settings","Presets","About"])
        self.stack = QStackedWidget()  # Initialize stack here
        sidebar.currentRowChanged.connect(self._on_nav)
        sidebar.setCurrentRow(0)
        root.addWidget(sidebar)

        # pages stack
        root.addWidget(self.stack, 1)

        # --- Settings page ---
        pg = QWidget()
        layout = QVBoxLayout(pg)
        title = QLabel("Crosshair Z — Settings")
        title.setProperty("class","title")
        layout.addWidget(title)

        # preview
        self.preview = PreviewWidget(self.config, size=260)
        layout.addWidget(QLabel("Live Preview"))
        layout.addWidget(self.preview, alignment=Qt.AlignHCenter)

        # controls
        layout.addWidget(QLabel("Shape"))
        self.shape_combo = QComboBox(); self.shape_combo.addItems(["X","+","T","Dot","Circle","Hairline"])
        self.shape_combo.setCurrentText(self.config.get("shape","X")); self.shape_combo.currentTextChanged.connect(self._on_change)
        layout.addWidget(self.shape_combo)

        layout.addWidget(QLabel("Size"))
        self.size_slider = QSlider(Qt.Horizontal); self.size_slider.setRange(0,400); self.size_slider.setValue(int(self.config.get("size",20))); self.size_slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.size_slider)

        layout.addWidget(QLabel("Thickness (0.5 → 20.0 px)"))
        self.thick_slider = QSlider(Qt.Horizontal); self.thick_slider.setRange(5,200); self.thick_slider.setValue(int(float(self.config.get("thickness",2.0))*10)); self.thick_slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.thick_slider)

        layout.addWidget(QLabel("Gap (center offset)"))
        self.gap_slider = QSlider(Qt.Horizontal); self.gap_slider.setRange(0,100); self.gap_slider.setValue(int(self.config.get("gap",0))); self.gap_slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.gap_slider)

        layout.addWidget(QLabel("Dot Intensity (center dot alpha)"))
        self.dot_alpha_slider = QSlider(Qt.Horizontal); self.dot_alpha_slider.setRange(0,100); self.dot_alpha_slider.setValue(int(float(self.config.get("dot_alpha",1.0))*100)); self.dot_alpha_slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.dot_alpha_slider)

        layout.addWidget(QLabel("Offset X"))
        self.offset_x = QSlider(Qt.Horizontal); self.offset_x.setRange(-800,800); self.offset_x.setValue(int(self.config.get("offset_x",0))); self.offset_x.valueChanged.connect(self._on_change)
        layout.addWidget(self.offset_x)
        layout.addWidget(QLabel("Offset Y"))
        self.offset_y = QSlider(Qt.Horizontal); self.offset_y.setRange(-800,800); self.offset_y.setValue(int(self.config.get("offset_y",0))); self.offset_y.valueChanged.connect(self._on_change)
        layout.addWidget(self.offset_y)

        layout.addWidget(QLabel("Opacity"))
        self.opacity_slider = QSlider(Qt.Horizontal); self.opacity_slider.setRange(5,100); self.opacity_slider.setValue(int(float(self.config.get("opacity",0.95))*100)); self.opacity_slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.opacity_slider)

        # color + outline controls
        row = QHBoxLayout()
        self.color_btn = QPushButton("Pick Color"); self.color_btn.clicked.connect(self._pick_color); row.addWidget(self.color_btn)
        self.outline_btn = QPushButton("Pick Outline Color"); self.outline_btn.clicked.connect(self._pick_outline_color); row.addWidget(self.outline_btn)
        layout.addLayout(row)

        self.outline_check = QCheckBox("Enable Outline"); self.outline_check.setChecked(bool(self.config.get("outline",True))); self.outline_check.stateChanged.connect(self._on_change); layout.addWidget(self.outline_check)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Outline Style"))
        self.outline_style = QComboBox(); self.outline_style.addItems(["Rounded","Square"]); self.outline_style.setCurrentText(self.config.get("outline_style","Rounded")); self.outline_style.currentTextChanged.connect(self._on_change); row2.addWidget(self.outline_style)
        layout.addLayout(row2)

        layout.addWidget(QLabel("Outline Thickness (0.0 → 20.0 px)"))
        self.outline_thick = QSlider(Qt.Horizontal); self.outline_thick.setRange(0,200); self.outline_thick.setValue(int(float(self.config.get("outline_thickness",2.0))*10)); self.outline_thick.valueChanged.connect(self._on_change)
        layout.addWidget(self.outline_thick)

        # glow settings (own section)
        layout.addWidget(QLabel("Glow"))
        self.glow_check = QCheckBox("Enable Glow"); self.glow_check.setChecked(bool(self.config.get("glow", False))); self.glow_check.stateChanged.connect(self._on_change)
        layout.addWidget(self.glow_check)
        glow_row = QHBoxLayout()
        self.glow_color_btn = QPushButton("Pick Glow Color"); self.glow_color_btn.clicked.connect(self._pick_glow_color); glow_row.addWidget(self.glow_color_btn)
        glow_row.addWidget(QLabel("Glow Radius"))
        self.glow_radius = QSlider(Qt.Horizontal); self.glow_radius.setRange(0,80); self.glow_radius.setValue(int(self.config.get("glow_radius",8))); self.glow_radius.valueChanged.connect(self._on_change)
        glow_row.addWidget(self.glow_radius)
        layout.addLayout(glow_row)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Config"); save_btn.clicked.connect(self._save_config)
        btn_row.addWidget(save_btn)
        quick_save = QPushButton("Quick Save Preset"); quick_save.clicked.connect(self._quick_save_preset)
        btn_row.addWidget(quick_save)
        layout.addLayout(btn_row)

        layout.addStretch()
        self.stack.addWidget(pg)

        # --- Presets page ---
        pg2 = QWidget()
        pl = QVBoxLayout(pg2)
        self.presets_list = QListWidget()
        pl.addWidget(QLabel("Presets folder (quick cycle uses these)"))
        pl.addWidget(self.presets_list)
        btns = QHBoxLayout()
        import_btn = QPushButton("Import Preset"); import_btn.clicked.connect(self._import_preset); btns.addWidget(import_btn)
        export_btn = QPushButton("Export Current"); export_btn.clicked.connect(self._export_current); btns.addWidget(export_btn)
        pl.addLayout(btns)
        pl.addStretch()
        self.stack.addWidget(pg2)
        self._refresh_presets_list()

        # --- About page ---
        pg3 = QWidget(); al = QVBoxLayout(pg3)
        al.addWidget(QLabel("Crosshair Z — Advanced+\n\nFeatures:\n• Live cached glow (GPU-friendly)\n• Global hotkeys: F8 toggle, F9 cycle presets, Shift+F9 quick-save, F10 reset offsets\n• Center dot intensity, offsets, outline styles"))
        al.addStretch()
        self.stack.addWidget(pg3)

        # initial apply
        self._apply_all()

    # ---------------- UI helpers ----------------
    def _on_nav(self, idx):
        self.stack.setCurrentIndex(idx)

    def _on_change(self, *_):
        # update config from controls
        self.config["shape"] = self.shape_combo.currentText()
        self.config["size"] = int(self.size_slider.value())
        self.config["thickness"] = float(self.thick_slider.value())/10.0
        self.config["gap"] = int(self.gap_slider.value())
        self.config["dot_alpha"] = float(self.dot_alpha_slider.value())/100.0
        self.config["offset_x"] = int(self.offset_x.value())
        self.config["offset_y"] = int(self.offset_y.value())
        self.config["opacity"] = float(self.opacity_slider.value())/100.0
        self.config["outline"] = bool(self.outline_check.isChecked())
        self.config["outline_style"] = self.outline_style.currentText()
        self.config["outline_thickness"] = float(self.outline_thick.value())/10.0
        self.config["glow"] = bool(self.glow_check.isChecked())
        self.config["glow_radius"] = int(self.glow_radius.value())
        # preview & overlay update (re-cache happens inside overlay.update_settings)
        self.preview.set_config(self.config)
        self.overlay.update_settings(self.config)

    def _pick_color(self):
        start = QColor(*self.config.get("color",[0,200,80]))
        col = QColorDialog.getColor(start, self, "Pick Crosshair Color")
        if col.isValid():
            self.config["color"] = [col.red(), col.green(), col.blue()]
            self._on_change()

    def _pick_outline_color(self):
        start = QColor(*self.config.get("outline_color",[0,0,0]))
        col = QColorDialog.getColor(start, self, "Pick Outline Color")
        if col.isValid():
            self.config["outline_color"] = [col.red(), col.green(), col.blue()]
            self._on_change()

    def _pick_glow_color(self):
        start = QColor(*self.config.get("glow_color", self.config.get("color",[0,200,80])))
        col = QColorDialog.getColor(start, self, "Pick Glow Color")
        if col.isValid():
            self.config["glow_color"] = [col.red(), col.green(), col.blue()]
            self._on_change()

    def _save_config(self):
        # overwrite current preset in presets_file
        name = self.presets_data.get("current", "Default")
        self.presets_data["presets"][name] = deepcopy(self.config)
        save_presets_file(self.presets_data)
        # also write to disk
        with open(BASE_DIR / "crosshair_config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    # ---------------- presets helpers ----------------
    def _refresh_presets_list(self):
        self.presets_list.clear()
        for p in sorted(PRESETS_DIR.glob("*.json")):
            self.presets_list.addItem(p.name)

    def _import_preset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Preset (JSON)", str(PRESETS_DIR), "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            dest = PRESETS_DIR / Path(path).name
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self._refresh_presets_list()
        except Exception as e:
            print("Import failed:", e)

    def _export_current(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export current preset", str(PRESETS_DIR / "preset.json"), "JSON Files (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        self._refresh_presets_list()

    def _quick_save_preset(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        name = f"preset_{ts}.json"
        dest = PRESETS_DIR / name
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        self._refresh_presets_list()
        # also add to presets file as a new named preset
        pname = f"Quick_{ts}"
        self.presets_data["presets"][pname] = deepcopy(self.config)
        self.presets_data["current"] = pname
        save_presets_file(self.presets_data)
        # feedback
        print("Quick-saved preset:", name)

    # ---------------- hotkeys ----------------
    def _register_hotkeys(self):
        try:
            keyboard.add_hotkey("F8", lambda: self._hot_toggle_overlay())
            keyboard.add_hotkey("F9", lambda: self._hot_cycle_presets(next=True))
            keyboard.add_hotkey("shift+F9", lambda: self._quick_save_preset())
            keyboard.add_hotkey("F10", lambda: self._reset_offsets())
            print("Hotkeys registered: F8 toggle, F9 cycle, Shift+F9 quick-save, F10 reset offsets")
        except Exception as e:
            print("Failed to register hotkeys (run as admin on Windows?). Exception:", e)

    def _hot_toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

    def _hot_cycle_presets(self, next=True):
        # cycle files in presets dir
        files = sorted(PRESETS_DIR.glob("*.json"))
        if not files:
            return
        # find currently used file (if any) by matching exact content; else cycle sequentially
        cur = None
        try:
            # try to find file matching current config
            for i,f in enumerate(files):
                try:
                    with open(f,"r",encoding="utf-8") as fh:
                        data = json.load(fh)
                    if data == self.config:
                        cur = i
                        break
                except Exception:
                    continue
        except Exception:
            cur = None
        nxt = 0
        if cur is None:
            nxt = 0 if next else len(files)-1
        else:
            nxt = (cur + 1) % len(files) if next else (cur - 1) % len(files)
        # load
        try:
            with open(files[nxt],"r",encoding="utf-8") as fh:
                cfg = json.load(fh)
            self.config.update(cfg)
            # apply to UI controls & overlay
            self._apply_all_to_ui()
        except Exception as e:
            print("Failed to load preset", files[nxt], e)

    def _reset_offsets(self):
        self.config["offset_x"] = 0
        self.config["offset_y"] = 0
        # update sliders & apply
        self.offset_x.setValue(0)
        self.offset_y.setValue(0)
        self._on_change()

    # ---------------- apply states ----------------
    def _apply_all(self):
        # set UI controls to current config and apply
        self.shape_combo.setCurrentText(self.config.get("shape","X"))
        self.size_slider.setValue(int(self.config.get("size",20)))
        self.thick_slider.setValue(int(float(self.config.get("thickness",2.0))*10))
        self.gap_slider.setValue(int(self.config.get("gap",0)))
        self.dot_alpha_slider.setValue(int(float(self.config.get("dot_alpha",1.0))*100))
        self.offset_x.setValue(int(self.config.get("offset_x",0)))
        self.offset_y.setValue(int(self.config.get("offset_y",0)))
        self.opacity_slider.setValue(int(float(self.config.get("opacity",0.95))*100))
        self.outline_check.setChecked(bool(self.config.get("outline", True)))
        self.outline_style.setCurrentText(self.config.get("outline_style","Rounded"))
        self.outline_thick.setValue(int(float(self.config.get("outline_thickness",2.0))*10))
        self.glow_check.setChecked(bool(self.config.get("glow", False)))
        self.glow_radius.setValue(int(self.config.get("glow_radius",8)))

        self.preview.set_config(self.config)
        self.overlay.update_settings(self.config)

    def _apply_all_to_ui(self):
        # alias
        self._apply_all()

# ---------------- run ----------------
def main():
    app = QApplication(sys.argv)
    win = CrosshairZApp()
    win.show()
    try:
        sys.exit(app.exec_())
    finally:
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass

if __name__ == "__main__":
    main()