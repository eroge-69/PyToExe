"""
Improved PDF Annotator with more accurate AI ballooning and nicer UI.

Requirements:
    pip install pymupdf pillow numpy opencv-python openpyxl
"""

import tkinter as tk
from tkinter import filedialog, ttk, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import fitz  # PyMuPDF
import io
import math
import json
import cv2
import numpy as np
import os
import sys
import openpyxl  # For Excel support

# -------------------------
# Helper geometry functions
# -------------------------
def polygon_centered(x, y, radius, sides, rotation=0):
    pts = []
    for i in range(sides):
        ang = rotation + 2 * math.pi * i / sides
        px = x + radius * math.cos(ang)
        py = y + radius * math.sin(ang)
        pts.append((px, py))
    return pts

def star_points(x, y, outer_r, inner_r, points=5, rotation=0):
    pts = []
    angle = rotation
    delta = math.pi / points
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        angle += delta
    return pts

# -------------------------
# Tooltip utility
# -------------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, _=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text, justify=tk.LEFT, bg="#ffffe0", relief=tk.SOLID, borderwidth=1,
                       font=("Segoe UI", 9))
        lbl.pack(ipadx=6, ipady=3)
    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# -------------------------
# Main application
# -------------------------
class PDFAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional PDF Annotator — AI Ballooning")
        self.root.geometry("1220x820")
        # Core state
        self.pdf_doc = None
        self.current_page = 0
        self.annotations = {}  # page_index -> list of anns
        self.scale = 1.5  # render scale for display / annotation coordinates
        self.annotation_count = 0
        self.selected_color = "#FF6B6B"
        self.shape_var = tk.StringVar(value="circle")
        self.tk_img = None
        self.display_image_size = (0, 0)
        self.balloon_size_var = tk.IntVar(value=40)  # Advanced: User-adjustable balloon size
        # UI setup
        self.setup_ui()

    def setup_ui(self):
        # Style
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6, background="#e0e0e0", foreground="#333333")
        style.configure("TLabel", font=("Segoe UI", 10), foreground="#333333")
        self.root.configure(bg="#f4f6f9")

        # Toolbar
        toolbar = tk.Frame(self.root, bd=0, relief=tk.FLAT, padx=6, pady=6, bg="#ffffff")
        toolbar.pack(fill=tk.X, side=tk.TOP)

        btn_upload = ttk.Button(toolbar, text="📁 Upload PDF", command=self.load_pdf)
        btn_upload.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_upload, "Load a PDF file for annotation")

        self.auto_annotate_btn = ttk.Button(toolbar, text="🤖 AI Auto-Balloon", command=self.auto_annotate, state=tk.DISABLED)
        self.auto_annotate_btn.pack(side=tk.LEFT, padx=6)
        ToolTip(self.auto_annotate_btn, "Automatically add balloons to text & large areas")

        btn_zoom_in = ttk.Button(toolbar, text="🔍 Zoom +", command=lambda: self.set_scale(self.scale * 1.2))
        btn_zoom_in.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_zoom_in, "Zoom in (or Ctrl + MouseWheel)")

        btn_zoom_out = ttk.Button(toolbar, text="🔎 Zoom -", command=lambda: self.set_scale(self.scale / 1.2))
        btn_zoom_out.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_zoom_out, "Zoom out")

        btn_clear_page = ttk.Button(toolbar, text="🧽 Clear Page", command=self.clear_page)
        btn_clear_page.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_clear_page, "Remove all annotations on current page")

        btn_clear_all = ttk.Button(toolbar, text="🧼 Clear All", command=self.clear_all)
        btn_clear_all.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_clear_all, "Remove all annotations on all pages")

        btn_export_json = ttk.Button(toolbar, text="💾 Export JSON", command=self.export_json)
        btn_export_json.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_export_json, "Export annotations to JSON")

        btn_save_pdf = ttk.Button(toolbar, text="📦 Download Annotated PDF", command=self.download_pdf)
        btn_save_pdf.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_save_pdf, "Save a new PDF with the annotations")

        btn_export_excel = ttk.Button(toolbar, text="📊 Export to Excel", command=self.export_excel)
        btn_export_excel.pack(side=tk.LEFT, padx=6)
        ToolTip(btn_export_excel, "Export annotations to an Excel file")

        # Right control panel
        right_controls = tk.Frame(self.root, bg="#f4f6f9", relief=tk.GROOVE, bd=2, padx=10, pady=10)
        right_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)

        ttk.Label(right_controls, text="Select Page:").pack(anchor="w", pady=(6,2))
        self.page_combo = ttk.Combobox(right_controls, state="readonly", width=20)
        self.page_combo.bind("<<ComboboxSelected>>", self.change_page)
        self.page_combo.pack(anchor="w", pady=(0,8))

        ttk.Label(right_controls, text="Shape:").pack(anchor="w")
        shapes = ['circle', 'rectangle', 'speech-bubble', 'diamond', 'hexagon', 'star', 'triangle', 'pentagon']
        for s in shapes:
            rb = ttk.Radiobutton(right_controls, text=s.capitalize(), variable=self.shape_var, value=s)
            rb.pack(anchor="w")

        ttk.Label(right_controls, text="Color:").pack(anchor="w", pady=(8,0))
        self.color_btn = ttk.Button(right_controls, text="Choose Color", command=self.choose_color)
        self.color_btn.pack(anchor="w", pady=(0,8))
        ToolTip(self.color_btn, "Select balloon color")

        ttk.Label(right_controls, text="Balloon Size:").pack(anchor="w", pady=(8,0))
        ttk.Scale(right_controls, from_=20, to=80, orient=tk.HORIZONTAL, variable=self.balloon_size_var, length=150).pack(anchor="w")
        ttk.Label(right_controls, textvariable=self.balloon_size_var).pack(anchor="w")

        # Canvas area with scrollbars
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=6, pady=6)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        self.hbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Bind events
        self.canvas.bind("<Button-1>", self.add_annotation_click)          # left-click add
        self.canvas.bind("<Button-3>", self.remove_annotation_nearest)    # right-click delete nearest
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        # mousewheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)    # Linux scroll down

        # status bar
        self.status = ttk.Label(self.root, text="No PDF loaded", relief=tk.SUNKEN, anchor="w")
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    # -------------------------
    # UI helpers
    # -------------------------
    def set_scale(self, new_scale):
        if new_scale < 0.25:
            new_scale = 0.25
        if new_scale > 4.0:
            new_scale = 4.0
        if self.pdf_doc:
            ratio = new_scale / self.scale
            for page_anns in self.annotations.values():
                for ann in page_anns:
                    ann['balloonX'] *= ratio
                    ann['balloonY'] *= ratio
                    ann['arrowX'] *= ratio
                    ann['arrowY'] *= ratio
        self.scale = new_scale
        if self.pdf_doc:
            self.display_page(self.current_page)

    def on_canvas_configure(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        # Zoom with Ctrl + wheel
        try:
            ctrl_pressed = (event.state & 0x4) != 0
        except Exception:
            ctrl_pressed = False
        if ctrl_pressed:
            if hasattr(event, "delta"):
                if event.delta > 0:
                    self.set_scale(self.scale * 1.08)
                else:
                    self.set_scale(self.scale / 1.08)
            else:
                # Linux wheel events
                if event.num == 4:
                    self.set_scale(self.scale * 1.08)
                elif event.num == 5:
                    self.set_scale(self.scale / 1.08)
        else:
            # scroll
            if hasattr(event, "delta"):
                self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")

    def choose_color(self):
        color = colorchooser.askcolor(color=self.selected_color)[1]
        if color:
            self.selected_color = color

    # -------------------------
    # PDF loading & display
    # -------------------------
    def load_pdf(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file:
            return
        try:
            self.pdf_doc = fitz.open(file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{e}")
            return
        num_pages = len(self.pdf_doc)
        self.annotations = {i: [] for i in range(num_pages)}
        self.page_combo['values'] = [f"Page {i+1}" for i in range(num_pages)]
        self.page_combo.current(0)
        self.current_page = 0
        self.annotation_count = 0
        self.display_page(0)
        self.auto_annotate_btn.config(state=tk.NORMAL)
        self.status.config(text=f"Loaded: {os.path.basename(file)} — {num_pages} pages")

    def change_page(self, event=None):
        if not self.pdf_doc:
            return
        page_num = self.page_combo.current()
        if page_num >= 0:
            self.display_page(page_num)

    def display_page(self, page_num):
        """Render page at current scale and display on canvas, then render annotations."""
        if self.pdf_doc is None:
            return
        page = self.pdf_doc[page_num]
        matrix = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.display_image_size = (pix.width, pix.height)

        # keep reference to avoid GC
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img, tags=("pdf_image",))
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.current_page = page_num
        self.page_combo.current(page_num)
        self.render_annotations()

    # -------------------------
    # Annotations
    # -------------------------
    def add_annotation(self, x, y, arrow_offset=(0,0)):
        """Add annotation. x,y are image coords at current scale (pixels)."""
        max_num = max((a['number'] for anns in self.annotations.values() for a in anns), default=0)
        new_num = max_num + 1
        balloon_w = self.balloon_size_var.get()
        balloon_h = balloon_w * 0.75
        # default balloon above the point (with small offset)
        bx = float(x - balloon_w / 2 + arrow_offset[0])
        by = float(y - balloon_h - 8 + arrow_offset[1])
        ann = {
            'id': self.annotation_count,
            'balloonX': bx,
            'balloonY': by,
            'arrowX': float(x),
            'arrowY': float(y),
            'number': int(new_num),
            'shape': self.shape_var.get(),
            'color': self.selected_color
        }
        self.annotations.setdefault(self.current_page, []).append(ann)
        self.annotation_count += 1
        self.render_annotations()

    def add_annotation_click(self, event):
        if not self.pdf_doc:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        w, h = self.display_image_size
        if 0 <= x <= w and 0 <= y <= h:
            self.add_annotation(x, y)

    def render_annotations(self):
        """Draw annotations on top of canvas image using canvas primitives."""
        self.canvas.delete("annotation")
        anns = self.annotations.get(self.current_page, [])
        for ann in anns:
            x = ann['balloonX']
            y = ann['balloonY']
            color = ann['color']
            shape = ann['shape']
            num = ann['number']
            darker = self.get_darker_color(color)
            balloon_w = self.balloon_size_var.get()
            balloon_h = balloon_w * 0.75
            cx = x + balloon_w / 2
            cy = y + balloon_h / 2
            radius = balloon_w / 2 - 5
            # draw shape
            if shape == 'circle':
                self.canvas.create_oval(x, y, x+balloon_w, y+balloon_h, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'rectangle':
                self.canvas.create_rectangle(x, y, x+balloon_w, y+balloon_h, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'speech-bubble':
                # rounded rectangle + tail
                self.canvas.create_rectangle(x, y, x+balloon_w, y+balloon_h-8, fill=color, outline=darker, width=3, tags="annotation")
                tail = [x+balloon_w/2-6, y+balloon_h-8, x+balloon_w/2, y+balloon_h-8, ann['arrowX'], ann['arrowY']]
                self.canvas.create_polygon(tail, fill=color, outline=darker, tags="annotation")
            elif shape == 'diamond':
                pts = [x+balloon_w/2, y, x+balloon_w, y+balloon_h/2, x+balloon_w/2, y+balloon_h, x, y+balloon_h/2]
                self.canvas.create_polygon(pts, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'hexagon':
                pts = polygon_centered(cx, cy, radius, 6, rotation=math.pi/6)
                flat = [coord for p in pts for coord in p]
                self.canvas.create_polygon(flat, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'triangle':
                pts = [x+balloon_w/2, y, x+balloon_w, y+balloon_h, x, y+balloon_h]
                self.canvas.create_polygon(pts, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'pentagon':
                pts = polygon_centered(cx, cy, radius, 5, rotation=-math.pi/2)
                flat = [coord for p in pts for coord in p]
                self.canvas.create_polygon(flat, fill=color, outline=darker, width=3, tags="annotation")
            elif shape == 'star':
                pts = star_points(cx, cy, radius, radius/2, points=5)
                flat = [coord for p in pts for coord in p]
                self.canvas.create_polygon(flat, fill=color, outline=darker, width=3, tags="annotation")
            else:
                self.canvas.create_rectangle(x, y, x+balloon_w, y+balloon_h, fill=color, outline=darker, width=3, tags="annotation")

            # number text centered
            font_size = int(balloon_w / 3)
            self.canvas.create_text(cx, cy, text=str(num), font=("Helvetica", font_size, "bold"), tags="annotation")

            # arrow: line + arrowhead
            bx = cx
            by = cy
            ax = ann['arrowX']
            ay = ann['arrowY']
            self.canvas.create_line(bx, by, ax, ay, fill=darker, width=3, tags="annotation")
            angle = math.atan2(ay - by, ax - bx)
            size = 10
            px1 = ax - size * math.cos(angle - math.pi/6)
            py1 = ay - size * math.sin(angle - math.pi/6)
            px2 = ax - size * math.cos(angle + math.pi/6)
            py2 = ay - size * math.sin(angle + math.pi/6)
            self.canvas.create_polygon(ax, ay, px1, py1, px2, py2, fill=darker, tags="annotation")

    def get_darker_color(self, color):
        """Return a slightly darker hex color for outlines."""
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        except Exception:
            return "#000000"
        r = max(0, r - 50)
        g = max(0, g - 50)
        b = max(0, b - 50)
        return f'#{r:02x}{g:02x}{b:02x}'

    # -------------------------
    # Deletion & Clearing
    # -------------------------
    def remove_annotation_nearest(self, event):
        """Right-click: remove the nearest annotation within a threshold."""
        if not self.pdf_doc:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        anns = self.annotations.get(self.current_page, [])
        if not anns:
            return
        nearest = None
        min_d = 1e9
        for a in anns:
            d = (a['arrowX'] - x) ** 2 + (a['arrowY'] - y) ** 2
            if d < min_d:
                min_d = d
                nearest = a
        if nearest and min_d < (45 ** 2):  # threshold ~45px
            anns.remove(nearest)
            self.render_annotations()

    def clear_page(self):
        if not self.pdf_doc:
            return
        self.annotations[self.current_page] = []
        self.render_annotations()

    def clear_all(self):
        if not self.pdf_doc:
            return
        for k in list(self.annotations.keys()):
            self.annotations[k] = []
        self.render_annotations()

    # -------------------------
    # Export JSON & PDF & Excel
    # -------------------------
    def export_json(self):
        if not self.pdf_doc:
            messagebox.showinfo("No PDF", "Load a PDF first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not file:
            return
        data = {"scale": self.scale, "pages": {}}
        for p, anns in self.annotations.items():
            data["pages"][str(p)] = anns
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Annotations exported to JSON.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save JSON:\n{e}")

    def download_pdf(self):
        """Render each page at the same scale used for display, draw annotations using PIL,
           and save a new PDF with annotated images."""
        if not self.pdf_doc:
            return
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not file:
            return
        try:
            new_pdf = fitz.open()
            # Try to pick a reasonable truetype font for PIL text
            pil_font = None
            for candidate in ["arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
                try:
                    pil_font = ImageFont.truetype(candidate, 14)
                    break
                except Exception:
                    pil_font = None
            if pil_font is None:
                pil_font = ImageFont.load_default()

            for i in range(len(self.pdf_doc)):
                page = self.pdf_doc[i]
                matrix = fitz.Matrix(self.scale, self.scale)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                draw = ImageDraw.Draw(img)

                for ann in self.annotations.get(i, []):
                    x = ann['balloonX']
                    y = ann['balloonY']
                    color = ann['color']
                    darker_color = self.get_darker_color(color)

                    def hex_to_rgb(h):
                        try:
                            return tuple(int(h[l:l+2], 16) for l in (1, 3, 5))
                        except Exception:
                            return (0, 0, 0)
                    rgb = hex_to_rgb(color)
                    rgb_d = hex_to_rgb(darker_color)
                    balloon_w = self.balloon_size_var.get()
                    balloon_h = balloon_w * 0.75
                    cx = x + balloon_w / 2
                    cy = y + balloon_h / 2
                    radius = balloon_w / 2 - 5
                    # draw balloon shapes (PIL)
                    if ann['shape'] == 'circle':
                        bbox = [x, y, x + balloon_w, y + balloon_h]
                        draw.ellipse(bbox, fill=rgb, outline=rgb_d, width=4)
                    elif ann['shape'] == 'rectangle':
                        bbox = [x, y, x + balloon_w, y + balloon_h]
                        draw.rectangle(bbox, fill=rgb, outline=rgb_d, width=4)
                    elif ann['shape'] == 'speech-bubble':
                        bbox = [x, y, x + balloon_w, y + balloon_h - 8]
                        try:
                            draw.rounded_rectangle(bbox, radius=6, fill=rgb, outline=rgb_d, width=4)
                        except Exception:
                            draw.rectangle(bbox, fill=rgb, outline=rgb_d, width=4)
                        tail = [(x + balloon_w/2 - 6, y + balloon_h - 8), (x + balloon_w/2, y + balloon_h - 8), (ann['arrowX'], ann['arrowY'])]
                        draw.polygon(tail, fill=rgb, outline=rgb_d)
                    elif ann['shape'] == 'diamond':
                        pts = [(x+balloon_w/2, y), (x+balloon_w, y+balloon_h/2), (x+balloon_w/2, y+balloon_h), (x, y+balloon_h/2)]
                        draw.polygon(pts, fill=rgb, outline=rgb_d)
                    elif ann['shape'] == 'hexagon':
                        pts = polygon_centered(cx, cy, radius, 6, rotation=math.pi/6)
                        draw.polygon(pts, fill=rgb, outline=rgb_d)
                    elif ann['shape'] == 'triangle':
                        pts = [(x+balloon_w/2, y), (x+balloon_w, y+balloon_h), (x, y+balloon_h)]
                        draw.polygon(pts, fill=rgb, outline=rgb_d)
                    elif ann['shape'] == 'pentagon':
                        pts = polygon_centered(cx, cy, radius, 5, rotation=-math.pi/2)
                        draw.polygon(pts, fill=rgb, outline=rgb_d)
                    elif ann['shape'] == 'star':
                        pts = star_points(cx, cy, radius, radius/2, points=5)
                        draw.polygon(pts, fill=rgb, outline=rgb_d)
                    else:
                        draw.rectangle([x, y, x+balloon_w, y+balloon_h], fill=rgb, outline=rgb_d, width=4)

                    # number text centered
                    txt = str(ann['number'])
                    font_size = int(balloon_w / 3)
                    fnt = ImageFont.truetype("arial.ttf", font_size) if "arial.ttf" in ImageFont.truetype else pil_font
                    bbox = draw.textbbox((0, 0), txt, font=fnt)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text((cx - tw/2, cy - th/2), txt, fill=(0, 0, 0), font=fnt)

                    # arrow line + arrowhead
                    draw.line((cx, cy, ann['arrowX'], ann['arrowY']), fill=rgb_d, width=4)
                    ax = ann['arrowX']; ay = ann['arrowY']
                    angle = math.atan2(ay - cy, ax - cx)
                    size = 12
                    px1 = ax - size * math.cos(angle - math.pi/6)
                    py1 = ay - size * math.sin(angle - math.pi/6)
                    px2 = ax - size * math.cos(angle + math.pi/6)
                    py2 = ay - size * math.sin(angle + math.pi/6)
                    draw.polygon([(ax, ay), (px1, py1), (px2, py2)], fill=rgb_d)

                # convert to bytes and add as a page image
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                new_page = new_pdf.new_page(width=pix.width, height=pix.height)
                new_page.insert_image(new_page.rect, stream=img_bytes.getvalue())

            new_pdf.save(file)
            messagebox.showinfo("Success", f"Annotated PDF saved to:\n{file}")
        except Exception as e:
            messagebox.showerror("Error saving PDF", str(e))

    def export_excel(self):
        if not self.pdf_doc:
            messagebox.showinfo("No PDF", "Load a PDF first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not file:
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Annotations"
        ws.append(["Page", "Annotation ID", "Number", "Shape", "Color", "Arrow X", "Arrow Y", "Balloon X", "Balloon Y"])
        for page, anns in self.annotations.items():
            for ann in anns:
                ws.append([page + 1, ann['id'], ann['number'], ann['shape'], ann['color'], ann['arrowX'], ann['arrowY'], ann['balloonX'], ann['balloonY']])
        try:
            wb.save(file)
            messagebox.showinfo("Success", "Annotations exported to Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save Excel:\n{e}")

    # -------------------------
    # AI Auto-annotation
    # -------------------------
    def auto_annotate(self):
        """First use exact PyMuPDF text blocks for high accuracy, then fallback to OpenCV to detect large image/figure regions."""
        if not self.pdf_doc:
            return
        page = self.pdf_doc[self.current_page]
        added = 0

        # ---------- 1) Use PyMuPDF text blocks (high accuracy for text regions) ----------
        try:
            # page.get_text("blocks") returns list of (x0,y0,x1,y1,"text", block_no)
            blocks = page.get_text("blocks")
            used_centers = []
            for blk in blocks:
                if len(blk) >= 5:
                    x0, y0, x1, y1, text = blk[0], blk[1], blk[2], blk[3], blk[4]
                else:
                    continue
                if not text or not text.strip():
                    continue
                # scale block center into image coords
                cx = int(((x0 + x1) / 2) * self.scale)
                cy = int(((y0 + y1) / 2) * self.scale)
                # avoid duplicates: check distance from existing ann points
                too_close = False
                for a in self.annotations.get(self.current_page, []):
                    if (a['arrowX'] - cx)**2 + (a['arrowY'] - cy)**2 < (40**2):
                        too_close = True
                        break
                if too_close:
                    continue
                # add annotation pointing to center of block
                self.add_annotation(cx, cy)
                used_centers.append((cx, cy))
                added += 1
        except Exception:
            # If text extraction fails, just continue to OpenCV fallback
            pass

        # ---------- 2) OpenCV fallback for large graphical regions (images/diagrams) ----------
        try:
            matrix = fitz.Matrix(self.scale, self.scale)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                arr = arr[:, :, :3]
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

            # Adaptive threshold tuned to highlight blocks/figures
            th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 21, 9)
            # Morphology to join text lines into blocks and remove small noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
            # Find contours
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Collect bounding boxes and merge overlapping ones to reduce duplicates
            rects = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                area = w * h
                if area < 1500:  # skip small noise
                    continue
                # skip extremely skinny / long shapes (likely lines)
                aspect = w / float(h) if h > 0 else 0
                if aspect > 20 or aspect < 0.02:
                    continue
                rects.append((x, y, x + w, y + h))

            # Merge rectangles (simple greedy)
            rects_merged = self.merge_rects(rects, iou_threshold=0.2)

            for (x0, y0, x1, y1) in rects_merged:
                cx = int((x0 + x1) / 2)
                cy = int((y0 + y1) / 2)
                too_close = False
                for a in self.annotations.get(self.current_page, []):
                    if (a['arrowX'] - cx)**2 + (a['arrowY'] - cy)**2 < (45**2):
                        too_close = True
                        break
                if not too_close:
                    self.add_annotation(cx, cy)
                    added += 1
        except Exception:
            # OpenCV fallback failed — ignore
            pass

        self.render_annotations()
        messagebox.showinfo("AI Ballooning", f"Automatically added {added} balloon(s).")

    def merge_rects(self, rects, iou_threshold=0.15):
        """Merge overlapping rectangles. rects: list of (x0,y0,x1,y1). Returns merged list."""
        if not rects:
            return []
        rects = [list(r) for r in rects]
        merged = []
        used = [False] * len(rects)
        for i, r in enumerate(rects):
            if used[i]:
                continue
            x0, y0, x1, y1 = r
            box = [x0, y0, x1, y1]
            used[i] = True
            changed = True
            while changed:
                changed = False
                for j, s in enumerate(rects):
                    if used[j]:
                        continue
                    iou = self.iou_box(box, s)
                    if iou > iou_threshold:
                        # merge
                        box = [min(box[0], s[0]), min(box[1], s[1]), max(box[2], s[2]), max(box[3], s[3])]
                        used[j] = True
                        changed = True
            merged.append(tuple(box))
        return merged

    def iou_box(self, a, b):
        """Compute IoU (intersection over union) between two boxes a and b."""
        ax0, ay0, ax1, ay1 = a
        bx0, by0, bx1, by1 = b
        ix0 = max(ax0, bx0)
        iy0 = max(ay0, by0)
        ix1 = min(ax1, bx1)
        iy1 = min(ay1, by1)
        iw = max(0, ix1 - ix0)
        ih = max(0, iy1 - iy0)
        inter = iw * ih
        area_a = max(0, ax1 - ax0) * max(0, ay1 - ay0)
        area_b = max(0, bx1 - bx0) * max(0, by1 - by0)
        union = area_a + area_b - inter
        if union <= 0:
            return 0.0
        return inter / float(union)

# -------------------------
# Run application
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFAnnotator(root)
    root.mainloop()
