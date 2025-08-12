
"""
AutoFill PDF App - Ready for PyInstaller Build
Features:
- Bundles default 'aof.pdf' form in the exe
- Creates mappings.json and profiles.json if missing
- Automatically loads 'aof.pdf' on startup
- Larger font for printed form text
"""

import sys, os, json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure default files exist
default_pdf = os.path.join(DATA_DIR, "aof.pdf")
if not os.path.exists(default_pdf):
    try:
        import shutil
        shutil.copy(os.path.join(APP_DIR, "aof.pdf"), default_pdf)
    except Exception as e:
        print("Error copying default PDF:", e)

MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
if not os.path.exists(MAPPINGS_FILE):
    with open(MAPPINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)
if not os.path.exists(PROFILES_FILE):
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class AutoFillApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Autofill App")
        self.geometry("1000x700")
        self.mappings = load_json(MAPPINGS_FILE, {})
        self.profiles = load_json(PROFILES_FILE, {})
        self.template_pdf = default_pdf
        self.template_img = None
        self.img_tk = None
        self.scale = 1.0
        self.current_mapping_name = None

        self.create_ui()
        if os.path.exists(self.template_pdf):
            self.load_pdf(path=self.template_pdf)

    def create_ui(self):
        left = ttk.Frame(self, width=300)
        left.pack(side="left", fill="y", padx=8, pady=8)
        ttk.Button(left, text="Load Template PDF", command=self.load_pdf).pack(fill="x", pady=4)
        ttk.Button(left, text="Save Mappings", command=self.save_all).pack(fill="x", pady=4)
        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Label(left, text="Mappings").pack(anchor="w")
        self.map_listbox = tk.Listbox(left, height=8)
        self.map_listbox.pack(fill="x")
        self.map_listbox.bind("<<ListboxSelect>>", self.on_map_select)
        ttk.Button(left, text="Add Mapping", command=self.prompt_new_mapping).pack(fill="x", pady=4)
        ttk.Button(left, text="Delete Mapping", command=self.delete_mapping).pack(fill="x", pady=4)
        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Label(left, text="Profiles").pack(anchor="w")
        self.profile_cb = ttk.Combobox(left, values=list(self.profiles.keys()))
        self.profile_cb.pack(fill="x")
        ttk.Button(left, text="New Profile", command=self.new_profile).pack(fill="x", pady=4)
        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Button(left, text="Fill PDF with Selected Profile", command=self.fill_pdf).pack(fill="x", pady=4)

        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.canvas = tk.Canvas(right, bg="grey")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def load_pdf(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
        if not path:
            return
        self.template_pdf = path
        doc = fitz.open(path)
        page = doc.load_page(0)
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(DATA_DIR, "template_preview.png")
        pix.save(img_path)
        from PIL import Image
        self.template_img = Image.open(img_path)
        self.scale = zoom
        self.show_image()

    def show_image(self):
        if self.template_img is None:
            return
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        iw, ih = self.template_img.size
        ratio = min(cw/iw, ch/ih, 1.0)
        disp = self.template_img.resize((int(iw*ratio), int(ih*ratio)))
        self.img_tk = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        self.canvas.create_image(0,0,anchor="nw",image=self.img_tk)
        for name, info in self.mappings.items():
            if info.get("template")==os.path.basename(self.template_pdf):
                x = info["x"]/self.scale*ratio
                y = info["y"]/self.scale*ratio
                self.canvas.create_rectangle(x-3,y-3,x+3,y+3,fill="red")
                self.canvas.create_text(x+10,y,anchor="w",text=name,fill="red",font=("Arial",10))

    def on_canvas_click(self, event):
        if not self.template_img:
            return
        iw, ih = self.template_img.size
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        ratio = min(cw/iw, ch/ih, 1.0)
        img_x = event.x/ratio*self.scale
        img_y = event.y/ratio*self.scale
        name = simpledialog.askstring("Field name", "Enter the field name:")
        if name:
            self.mappings[name] = {
                "template": os.path.basename(self.template_pdf),
                "x": img_x, "y": img_y, "page": 0
            }
            self.show_image()

    def prompt_new_mapping(self):
        self.on_canvas_click

    def on_map_select(self, evt): pass

    def delete_mapping(self):
        sel = self.map_listbox.curselection()
        if not sel: return
        key = list(self.mappings.keys())[sel[0]]
        self.mappings.pop(key, None)
        self.show_image()

    def new_profile(self):
        name = simpledialog.askstring("Profile name", "Enter profile name:")
        if not name: return
        data = simpledialog.askstring("Profile data", "Enter JSON data for this profile:")
        try:
            self.profiles[name] = json.loads(data)
            self.profile_cb['values'] = list(self.profiles.keys())
        except:
            messagebox.showerror("Error", "Invalid JSON")

    def fill_pdf(self):
        profile_name = self.profile_cb.get()
        if not profile_name: return
        profile = self.profiles.get(profile_name)
        if not profile: return
        reader = PdfReader(self.template_pdf)
        page = reader.pages[0]
        pw = float(page.mediabox.width)
        ph = float(page.mediabox.height)
        overlay_path = os.path.join(DATA_DIR, "overlay.pdf")
        c = canvas.Canvas(overlay_path, pagesize=(pw, ph))
        for name, info in self.mappings.items():
            if info.get("template") != os.path.basename(self.template_pdf):
                continue
            x_pt = pw * (info["x"] / (self.scale * self.template_img.size[0]))
            y_pt = ph * (1 - (info["y"] / (self.scale * self.template_img.size[1])))
            text = str(profile.get(name, f"<{name}>"))
            c.setFont("Helvetica", 12)  # Larger font
            c.drawString(x_pt, y_pt, text)
        c.showPage()
        c.save()
        overlay_reader = PdfReader(overlay_path)
        merged_page = reader.pages[0]
        merged_page.merge_page(overlay_reader.pages[0])
        writer = PdfWriter()
        writer.add_page(merged_page)
        out_path = os.path.join(DATA_DIR, f"filled_{os.path.basename(self.template_pdf)}")
        with open(out_path, "wb") as f:
            writer.write(f)
        messagebox.showinfo("Done", f"Saved filled PDF:\n{out_path}")

    def save_all(self):
        save_json(MAPPINGS_FILE, self.mappings)
        save_json(PROFILES_FILE, self.profiles)
        messagebox.showinfo("Saved", "Data saved.")

if __name__ == "__main__":
    app = AutoFillApp()
    app.mainloop()
