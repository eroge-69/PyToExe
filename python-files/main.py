from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import ttk, colorchooser
import win32gui
import win32con
import pyautogui
import random
import os

# Set working directory for assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Load crosshair icon (ensure the path is valid or image exists)
def load_crosshair_icon():
    try:
        return ImageTk.PhotoImage(file=os.path.join(ASSETS_DIR, "crosshair_icon.png"))
    except:
        return None

def generate_dark_gradient(width, height):
    image = Image.new("RGB", (width, height), "#0a0a0a")
    draw = ImageDraw.Draw(image)
    for i in range(height):
        gradient = int(30 + 60 * (i / height))
        draw.line([(0, i), (width, i)], fill=(gradient, gradient, gradient))
    for _ in range(200):
        x, y = random.randint(0, width), random.randint(0, height)
        r = random.randint(1, 2)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=random.choice(["#333", "#444", "#555"]))
    return ImageTk.PhotoImage(image)

def enable_dragging(widget):
    def start_drag(event):
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
    def do_drag(event):
        x = widget.winfo_pointerx() - widget._drag_start_x
        y = widget.winfo_pointery() - widget._drag_start_y
        widget.geometry(f"+{x}+{y}")
    widget.bind("<Button-1>", start_drag)
    widget.bind("<B1-Motion>", do_drag)

class RoundedFrame(tk.Frame):
    def __init__(self, master, radius=20, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.radius = radius
        self.canvas = tk.Canvas(self, bg=kwargs.get("bg", "#000"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self.draw_rounded)

    def draw_rounded(self, event=None):
        self.canvas.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self.radius
        self.canvas.create_polygon(
            r, 0, w - r, 0,
            w, r, w, h - r,
            w - r, h, r, h,
            0, h - r, 0, r,
            smooth=True,
            fill="#121212"
        )

class CrosshairOverlay:
    def __init__(self):
        self.visible = False
        self.size = 10
        self.color = "red"
        self.offset_x = 0
        self.offset_y = 0
        self.style = "circle"
        self.filled = False
        self.overlay = tk.Toplevel()
        self.overlay.title("Crosshair")
        self.overlay.attributes("-topmost", True)
        self.overlay.overrideredirect(True)
        self.overlay.wm_attributes("-transparentcolor", "white")
        self.overlay.configure(bg='white')
        self.canvas_size = 200
        self.canvas = tk.Canvas(self.overlay, width=self.canvas_size, height=self.canvas_size,
                                bg="white", highlightthickness=0)
        self.canvas.pack()
        hwnd = win32gui.FindWindow(None, "Crosshair")
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        self.overlay.withdraw()
        self.update()

    def update(self):
        self.canvas.delete("all")
        cx, cy, r = self.canvas_size // 2, self.canvas_size // 2, self.size
        fill = self.color if self.filled else ""
        if self.style == "circle":
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=self.color, fill=fill, width=2)
        elif self.style == "cross":
            self.canvas.create_line(cx - r, cy, cx + r, cy, fill=self.color, width=2)
            self.canvas.create_line(cx, cy - r, cx, cy + r, fill=self.color, width=2)
        elif self.style == "dot":
            self.canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill=self.color, outline=self.color)
        sw, sh = pyautogui.size()
        wx = sw // 2 - self.canvas_size // 2 + self.offset_x
        wy = sh // 2 - self.canvas_size // 2 + self.offset_y
        self.overlay.geometry(f"{self.canvas_size}x{self.canvas_size}+{wx}+{wy}")

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.overlay.deiconify()
        else:
            self.overlay.withdraw()

    def move(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.update()

    def change_color(self):
        color = colorchooser.askcolor(title="Scegli il colore del mirino")[1]
        if color:
            self.color = color
            self.update()

    def change_size(self, val):
        self.size = int(float(val))
        self.update()

    def set_style(self, val):
        self.style = val
        self.update()

    def toggle_fill(self):
        self.filled = not self.filled
        self.update()

def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("880x360")
    enable_dragging(root)

    bg_img = generate_dark_gradient(880, 360)
    bg_label = tk.Label(root, image=bg_img)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", background="#1c1c1c", foreground="white", padding=10, relief="flat")
    style.configure("TLabel", background="#121212", foreground="white")
    style.configure("TFrame", background="#121212")
    style.configure("TCombobox", fieldbackground="#1c1c1c", background="#1c1c1c", foreground="white")

    overlay = CrosshairOverlay()

    rounded_frame = RoundedFrame(root, radius=25, bg="#000")
    rounded_frame.place(relx=0.5, rely=0.5, anchor="center", width=840, height=300)

    inner = ttk.Frame(rounded_frame.canvas)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    icon = load_crosshair_icon()
    if icon:
        tk.Label(inner, image=icon, bg="#121212").pack(pady=(5, 0))

    ttk.Label(inner, text="Crosshair Settings", font=("Segoe UI", 14, "bold")).pack(pady=8)

    controls = ttk.Frame(inner)
    controls.pack(pady=4)

    ttk.Button(controls, text="🎯 Toggle", command=overlay.toggle).grid(row=0, column=0, padx=10)
    ttk.Button(controls, text="🎨 Colore", command=overlay.change_color).grid(row=0, column=1, padx=10)
    ttk.Label(controls, text="Dimensione:").grid(row=0, column=2, padx=5)
    size_slider = ttk.Scale(controls, from_=5, to=50, orient="horizontal", command=overlay.change_size)
    size_slider.set(overlay.size)
    size_slider.grid(row=0, column=3, padx=5)

    config = ttk.Frame(inner)
    config.pack(pady=10)

    ttk.Label(config, text="Tipo: ").grid(row=0, column=0, padx=6)
    style_menu = ttk.Combobox(config, values=["circle", "cross", "dot"], state="readonly")
    style_menu.set("circle")
    style_menu.grid(row=0, column=1, padx=5)
    style_menu.bind("<<ComboboxSelected>>", lambda e: overlay.set_style(style_menu.get()))

    ttk.Checkbutton(config, text="Riempito", command=overlay.toggle_fill).grid(row=0, column=2, padx=10)

    arrows = ttk.Frame(inner)
    arrows.pack(pady=10)
    for (txt, dx, dy, col, row) in [("↑", 0, -1, 1, 0), ("←", -1, 0, 0, 1), ("→", 1, 0, 2, 1), ("↓", 0, 1, 1, 2)]:
        ttk.Button(arrows, text=txt, width=4, command=lambda dx=dx, dy=dy: overlay.move(dx, dy)).grid(row=row, column=col, padx=4, pady=2)

    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    main()
