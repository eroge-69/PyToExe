#!/usr/bin/env python3
import os
import sys
import tempfile
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Barcode generation via reportlab
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPM

# Image display via Pillow
try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit("This program requires Pillow. Install it with: pip install pillow")

APP_TITLE = "Code128 Timestamp Generator"
BAR_HEIGHT = 60    # pixels (visual height of bars)
BAR_WIDTH  = 1.2   # module width (affects overall width)
MARGIN_PX  = 20    # padding around barcode image when rendering

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("600x400")
        self.resizable(True, True)

        self.content = ttk.Frame(self, padding=10)
        self.content.pack(fill="both", expand=True)

        # Display field for the encoded data (YYYYMMDDHHMMSS)
        self.var_string = tk.StringVar(value="(no barcode yet)")
        self.lbl_text = ttk.Label(self.content, textvariable=self.var_string, font=("Consolas", 12))
        self.lbl_text.pack(pady=(0,10))

        # Button
        self.btn = ttk.Button(self.content, text="Generate Code128 from current date/time", command=self.generate)
        self.btn.pack(pady=(0,10))

        # Canvas / image label to show the barcode
        self.img_label = ttk.Label(self.content)
        self.img_label.pack(fill="both", expand=True)

        # Keep a reference to the PhotoImage so it doesn't get garbage collected
        self._photo = None

        # Temp folder for images in this session
        self.tempdir = tempfile.mkdtemp(prefix="code128_")

    def _build_barcode_png(self, data: str) -> str:
        """
        Build a Code128 barcode PNG for the given data and return its file path.
        Uses reportlab's graphics+renderPM pipeline.
        """
        # Create the Code128 barcode object
        bc = code128.Code128(data, barHeight=BAR_HEIGHT, barWidth=BAR_WIDTH)
        # Compute drawing bounds
        bw = bc.width + MARGIN_PX * 2
        bh = bc.height + MARGIN_PX * 2

        # Build a drawing and add the barcode
        drawing = Drawing(bw, bh)
        # Position barcode at (MARGIN_PX, MARGIN_PX)
        bc.x = MARGIN_PX
        bc.y = MARGIN_PX
        drawing.add(bc)

        out_path = os.path.join(self.tempdir, f"{data}.png")
        # Render to PNG
        renderPM.drawToFile(drawing, out_path, fmt="PNG")
        return out_path

    def generate(self):
        try:
            # 1) Make timestamp string YYYYMMDDHHMMSS
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            self.var_string.set(ts)

            # 2) Build barcode PNG
            png_path = self._build_barcode_png(ts)

            # 3) Load with PIL and display
            img = Image.open(png_path)
            # Optional: scale down if very large to fit window
            max_w, max_h = 1000, 300
            img.thumbnail((max_w, max_h))
            self._photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self._photo)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate barcode:\n{e}")

if __name__ == "__main__":
    try:
        App().mainloop()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
