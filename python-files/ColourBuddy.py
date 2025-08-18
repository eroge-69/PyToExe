import sys
import ctypes
from PyQt6 import QtCore, QtGui, QtWidgets
import win32gui, win32api, win32con

# ------- CSS Color List (name -> hex) -------
CSS4_COLORS = {
    # (short list of common names first for better readability; full list follows)
    "black": "#000000", "white": "#ffffff", "gray": "#808080", "grey": "#808080",
    "silver": "#c0c0c0", "red": "#ff0000", "maroon": "#800000", "yellow": "#ffff00",
    "olive": "#808000", "lime": "#00ff00", "green": "#008000", "aqua": "#00ffff",
    "teal": "#008080", "blue": "#0000ff", "navy": "#000080", "fuchsia": "#ff00ff",
    "purple": "#800080", "orange": "#ffa500", "brown": "#a52a2a", "gold": "#ffd700",
    "pink": "#ffc0cb", "indigo": "#4b0082", "violet": "#ee82ee", "tan": "#d2b48c",
    # full CSS4 set (abbreviated here for space—add more if you like):
    "aliceblue":"#f0f8ff","antiquewhite":"#faebd7","aquamarine":"#7fffd4",
    "azure":"#f0ffff","beige":"#f5f5dc","bisque":"#ffe4c4","blanchedalmond":"#ffebcd",
    "blueviolet":"#8a2be2","burlywood":"#deb887","cadetblue":"#5f9ea0","chartreuse":"#7fff00",
    "chocolate":"#d2691e","coral":"#ff7f50","cornflowerblue":"#6495ed","cornsilk":"#fff8dc",
    "crimson":"#dc143c","darkblue":"#00008b","darkcyan":"#008b8b","darkgoldenrod":"#b8860b",
    "darkgray":"#a9a9a9","darkgreen":"#006400","darkgrey":"#a9a9a9","darkkhaki":"#bdb76b",
    "darkmagenta":"#8b008b","darkolivegreen":"#556b2f","darkorange":"#ff8c00",
    "darkorchid":"#9932cc","darkred":"#8b0000","darksalmon":"#e9967a","darkseagreen":"#8fbc8f",
    "darkslateblue":"#483d8b","darkslategray":"#2f4f4f","darkslategrey":"#2f4f4f",
    "darkturquoise":"#00ced1","darkviolet":"#9400d3","deeppink":"#ff1493","deepskyblue":"#00bfff",
    "dimgray":"#696969","dimgrey":"#696969","dodgerblue":"#1e90ff","firebrick":"#b22222",
    "floralwhite":"#fffaf0","forestgreen":"#228b22","gainsboro":"#dcdcdc","ghostwhite":"#f8f8ff",
    "goldenrod":"#daa520","greenyellow":"#adff2f","honeydew":"#f0fff0","hotpink":"#ff69b4",
    "indianred":"#cd5c5c","ivory":"#fffff0","khaki":"#f0e68c","lavender":"#e6e6fa",
    "lavenderblush":"#fff0f5","lawngreen":"#7cfc00","lemonchiffon":"#fffacd",
    "lightblue":"#add8e6","lightcoral":"#f08080","lightcyan":"#e0ffff","lightgoldenrodyellow":"#fafad2",
    "lightgray":"#d3d3d3","lightgreen":"#90ee90","lightgrey":"#d3d3d3","lightpink":"#ffb6c1",
    "lightsalmon":"#ffa07a","lightseagreen":"#20b2aa","lightskyblue":"#87cefa",
    "lightslategray":"#778899","lightslategrey":"#778899","lightsteelblue":"#b0c4de",
    "lightyellow":"#ffffe0","limegreen":"#32cd32","linen":"#faf0e6","mediumaquamarine":"#66cdaa",
    "mediumblue":"#0000cd","mediumorchid":"#ba55d3","mediumpurple":"#9370db",
    "mediumseagreen":"#3cb371","mediumslateblue":"#7b68ee","mediumspringgreen":"#00fa9a",
    "mediumturquoise":"#48d1cc","mediumvioletred":"#c71585","midnightblue":"#191970",
    "mintcream":"#f5fffa","mistyrose":"#ffe4e1","moccasin":"#ffe4b5","navajowhite":"#ffdead",
    "oldlace":"#fdf5e6","olivedrab":"#6b8e23","orangered":"#ff4500","orchid":"#da70d6",
    "palegoldenrod":"#eee8aa","palegreen":"#98fb98","paleturquoise":"#afeeee",
    "palevioletred":"#db7093","papayawhip":"#ffefd5","peachpuff":"#ffdab9","peru":"#cd853f",
    "plum":"#dda0dd","powderblue":"#b0e0e6","rosybrown":"#bc8f8f","royalblue":"#4169e1",
    "saddlebrown":"#8b4513","salmon":"#fa8072","sandybrown":"#f4a460","seagreen":"#2e8b57",
    "seashell":"#fff5ee","sienna":"#a0522d","skyblue":"#87ceeb","slateblue":"#6a5acd",
    "slategray":"#708090","slategrey":"#708090","snow":"#fffafa","springgreen":"#00ff7f",
    "steelblue":"#4682b4","thistle":"#d8bfd8","tomato":"#ff6347","turquoise":"#40e0d0",
    "wheat":"#f5deb3","whitesmoke":"#f5f5f5","yellowgreen":"#9acd32"
}

def hex_to_rgb(hx: str):
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))

# Build color table (name, (R,G,B))
COLOR_TABLE = [(name, hex_to_rgb(hx)) for name, hx in CSS4_COLORS.items()]

# ----- sRGB -> Lab conversion (D65) for perceptual matching -----
def _pivot_rgb(c):
    # sRGB to linear
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _f(t):
    eps = 216/24389
    kappa = 24389/27
    return t ** (1/3) if t > eps else (kappa * t + 16) / 116

def rgb_to_lab(rgb):
    r, g, b = [_pivot_rgb(x) for x in rgb]
    # sRGB to XYZ (D65)
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    # Normalize by D65 reference white
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    fx, fy, fz = _f(X / Xn), _f(Y / Yn), _f(Z / Zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return (L, a, b)

def deltaE_lab(lab1, lab2):
    # Simple CIE76 distance
    return ((lab1[0]-lab2[0])**2 + (lab1[1]-lab2[1])**2 + (lab1[2]-lab2[2])**2) ** 0.5

# Precompute LAB for table
COLOR_TABLE_LAB = [(name, rgb, rgb_to_lab(rgb)) for name, rgb in COLOR_TABLE]

def nearest_color_name(rgb):
    target = rgb_to_lab(rgb)
    best = None
    best_d = 1e9
    for name, _, lab in COLOR_TABLE_LAB:
        d = deltaE_lab(target, lab)
        if d < best_d:
            best_d = d
            best = name
    return best

# ----- Screen color sampling -----
def get_color_under_cursor():
    # Avoid DPI scaling issues
    ctypes.windll.user32.SetProcessDPIAware()
    pt = win32gui.GetCursorPos()
    hdc = win32gui.GetDC(0)
    pixel = win32gui.GetPixel(hdc, pt[0], pt[1])
    win32gui.ReleaseDC(0, hdc)
    r = pixel & 0xff
    g = (pixel >> 8) & 0xff
    b = (pixel >> 16) & 0xff
    return (r, g, b)

# ----- UI -----
class ColorBuddy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Buddy – Color-Blind Helper")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
        self.setFixedSize(420, 250)

        # Fonts
        big = QtGui.QFont("Segoe UI", 16, QtGui.QFont.Weight.Bold)
        med = QtGui.QFont("Segoe UI", 12)

        # Swatch
        self.swatch = QtWidgets.QLabel()
        self.swatch.setFixedSize(120, 120)
        self.swatch.setStyleSheet("border: 2px solid #333; border-radius: 6px;")

        # Labels
        self.name_lbl = QtWidgets.QLabel("—")
        self.name_lbl.setFont(big)
        self.name_lbl.setWordWrap(True)

        self.hex_lbl = QtWidgets.QLabel("HEX: —")
        self.hex_lbl.setFont(med)

        self.rgb_lbl = QtWidgets.QLabel("RGB: —")
        self.rgb_lbl.setFont(med)

        # Buttons
        self.lock_btn = QtWidgets.QPushButton("Lock / Pick (Space)")
        self.copy_hex = QtWidgets.QPushButton("Copy HEX")
        self.copy_rgb = QtWidgets.QPushButton("Copy RGB")

        self.lock_btn.clicked.connect(self.toggle_lock)
        self.copy_hex.clicked.connect(self.copy_hex_to_clip)
        self.copy_rgb.clicked.connect(self.copy_rgb_to_clip)

        # Layout
        right = QtWidgets.QVBoxLayout()
        right.addWidget(self.name_lbl)
        right.addWidget(self.hex_lbl)
        right.addWidget(self.rgb_lbl)
        right.addStretch()
        right.addWidget(self.lock_btn)
        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(self.copy_hex)
        btns.addWidget(self.copy_rgb)
        right.addLayout(btns)

        main = QtWidgets.QHBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.addWidget(self.swatch)
        main.addLayout(right)

        # Timer for live preview
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_color_live)
        self.timer.start(60)  # ~16 fps would be 60 ms; smooth but not heavy

        self.locked = False
        self.current_rgb = (0,0,0)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key.Key_Space:
            self.toggle_lock()

    def toggle_lock(self):
        self.locked = not self.locked
        self.lock_btn.setText("Unlock (Space)" if self.locked else "Lock / Pick (Space)")

    def copy_hex_to_clip(self):
        QtWidgets.QApplication.clipboard().setText(self.hex_lbl.text().replace("HEX: ", ""))

    def copy_rgb_to_clip(self):
        QtWidgets.QApplication.clipboard().setText(self.rgb_lbl.text().replace("RGB: ", ""))

    def update_color_live(self):
        if self.locked:
            return
        rgb = get_color_under_cursor()
        if rgb != self.current_rgb:
            self.current_rgb = rgb
            name = nearest_color_name(rgb)
            hx = "#{:02X}{:02X}{:02X}".format(*rgb)
            self.name_lbl.setText(name.replace("-", " ").title())
            self.hex_lbl.setText(f"HEX: {hx}")
            self.rgb_lbl.setText(f"RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}")
            self.swatch.setStyleSheet(
                f"background-color: {hx}; border: 2px solid #333; border-radius: 6px;"
            )

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = ColorBuddy()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
