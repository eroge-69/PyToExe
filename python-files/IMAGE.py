"""
Picture Manager - Full Feature (Single-file) + Undo (Ctrl+Z) + Adjustments (Brightness/Contrast/Sharpness)
Features:
1. Manual select and crop (mouse drag)
2. Auto deskew for documents (Aadhaar/PAN) using minAreaRect on thresholded image
3. Rotate image by 1 degree (buttons for +1 / -1)
4. Convert background to white for clean B&W print
5. Enhance black for text/numbers only (adaptive threshold mask applied to image)
6. Save and replace edited picture
7. Join multiple pictures horizontal or vertical
8. Print picture (Windows os.startfile(...,'print'))
9. Reset to original
10. Next / Previous navigation for images in same folder
11. NEW: Undo button + Ctrl+Z shortcut
12. NEW: BRIGHTNESS / CONTRAST / SHARPNESS sliders (-100% to +100%) with live preview + Apply

Dependencies:
- Python 3.8+
- Pillow (PIL)
- OpenCV (cv2)
- numpy

Install:
    pip install pillow opencv-python numpy

Run:
    python picture_manager_full.py

Note: This is a pragmatic, single-file utility built with Tkinter. For heavy production usage, consider a PyQt/Electron app.
"""

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import cv2
import numpy as np
import os
import tempfile

# ---------------- Helper functions ----------------

def pil_to_cv(img_pil):
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def cv_to_pil(img_cv):
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

# Auto-deskew: find largest contour or minAreaRect on threshold
def auto_deskew(pil_img):
    cv = pil_to_cv(pil_img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    # blur and adaptive threshold to get document edges
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # invert if background dark
    if np.mean(th) < 127:
        th = 255 - th
    # find contours
    contours, _ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return pil_img
    # pick largest by area
    c = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(c)
    angle = rect[-1]
    # minAreaRect angle handling
    if angle < -45:
        angle = 90 + angle
    # rotate by negative angle to deskew
    (h,w) = cv.shape[:2]
    center = (w//2, h//2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(cv, M, (w,h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return cv_to_pil(rotated)

# Convert background gradually whiter by 5% each click
def whiten_background(pil_img, factor=0.05):
    cv = pil_to_cv(pil_img).astype(np.float32)
    # move pixel values slightly towards white (255)
    cv = cv + (255 - cv) * factor
    cv = np.clip(cv, 0, 255).astype(np.uint8)
    return cv_to_pil(cv)

# Enhance black text gradually darker by 5% each click
def enhance_black_text(pil_img, factor=0.05):
    cv = pil_to_cv(pil_img).astype(np.float32)
    gray = cv2.cvtColor(cv.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    # mask for text/dark areas
    th = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,10)
    mask = (th == 0)  # text pixels
    # darken only masked pixels toward 0 (black)
    cv[mask] = cv[mask] - cv[mask] * factor
    cv = np.clip(cv, 0, 255).astype(np.uint8)
    return cv_to_pil(cv)

# Manual crop utilities are handled in GUI mapping

# Join images horizontally or vertically
def join_images(img_list, mode='horizontal'):
    if not img_list:
        return None
    imgs = [im.convert('RGB') for im in img_list]
    if mode=='horizontal':
        heights = [im.height for im in imgs]
        target_h = min(heights)
        resized = [im.resize((int(im.width*target_h/im.height), target_h), Image.LANCZOS) if im.height!=target_h else im for im in imgs]
        total_w = sum(im.width for im in resized)
        out = Image.new('RGB', (total_w, target_h), (255,255,255))
        x=0
        for im in resized:
            out.paste(im, (x,0))
            x += im.width
        return out
    else:
        widths = [im.width for im in imgs]
        target_w = min(widths)
        resized = [im.resize((target_w, int(im.height*target_w/im.width)), Image.LANCZOS) if im.width!=target_w else im for im in imgs]
        total_h = sum(im.height for im in resized)
        out = Image.new('RGB', (target_w, total_h), (255,255,255))
        y=0
        for im in resized:
            out.paste(im, (0,y))
            y += im.height
        return out

# Print helper (Windows)
def print_pil_image(pil_img):
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    pil_img.save(path, dpi=(300,300))
    try:
        if os.name=='nt':
            os.startfile(path, 'print')
            return True
        else:
            pil_img.show()
            return False
    except Exception:
        pil_img.show()
        return False

# ---------------- GUI Application ----------------
class PictureManagerApp:
    def __init__(self, root):
        self.root = root
        root.title('')  # removed default title
        
        # --- Custom Title Bar ---
        title_frame = tk.Frame(root, bg="black")
        title_frame.pack(side="top", fill="x")

        title_label = tk.Label(
            title_frame,
            text="THIS APPLICATION WAS ENGINEERED BY MR. PRAKASH TIWARI",
            fg="red",
            bg="yellow",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="top", pady=3)
        self.root.geometry('1200x780')

        # State
        self.file_list = []      # list of image file paths in current folder
        self.index = -1          # current index in file_list
        self.orig = None         # original PIL image
        self.img = None          # working PIL image
        self.filename = None
        self.tkimg = None

        # --- NEW: Undo history ---
        self.history = []        # stack of previous states (PIL images)
        self.max_history = 30    # cap to avoid memory bloat

        # --- NEW: Live preview for adjustments ---
        self.preview_img = None  # None when not previewing

        # Left controls
        ctrl = tk.Frame(root, width=260)
        ctrl.pack(side='left', fill='y', padx=6, pady=6)

        btns = [
            ('Open File', self.open_file),
            ('Open Folder', self.open_folder),
            ('Prev Image', self.prev_image),
            ('Next Image', self.next_image),
            ('Manual Select & Crop', self.start_manual_crop),
            ('Auto Deskew (Doc)', self.do_auto_deskew),
            ('Rotate -1°', lambda: self.do_rotate(-1)),
            ('Rotate +1°', lambda: self.do_rotate(1)),
            ('Rotate 90°', lambda: self.do_rotate(90)),
            ('White Background', self.do_whiten_bg),
            ('Enhance Black Text', self.do_enhance_black),
            ('Join Images (Horizontal)', lambda: self.do_join('horizontal')),
            ('Join Images (Vertical)', lambda: self.do_join('vertical')),
            # --- NEW: Undo button (does not remove any existing option) ---
            ('Undo (Ctrl+Z)', self.undo),
            ('Save / Replace', self.save_image),
            ('Print', self.print_image),
            ('Reset', self.reset_image),
            ('Delete Image', self.delete_image),
            ('Rename Image', self.rename_image),  # Added Rename Button
            ('Exit', root.quit)
        ]

        for (t, cmd) in btns:
            b = tk.Button(ctrl, text=t, width=24, command=cmd)
            b.pack(pady=1)

        # --- NEW: Adjustment Sliders (moved to right panel under canvas) ---
        adj_frame = tk.LabelFrame(ctrl, text='')
        adj_frame.pack(fill='x', padx=2, pady=2)

        self.scale_b = tk.Scale(adj_frame, from_=-100, to=100, orient='horizontal', length=220,
                                label='BRIGHTNESS', command=self.on_adjust_change)
        self.scale_b.set(0)
        self.scale_b.pack(fill='x', padx=1, pady=0)

        self.scale_c = tk.Scale(adj_frame, from_=-100, to=100, orient='horizontal', length=220,
                                label='CONTRAST', command=self.on_adjust_change)
        self.scale_c.set(0)
        self.scale_c.pack(fill='x', padx=1, pady=0)

        self.scale_s = tk.Scale(adj_frame, from_=-100, to=100, orient='horizontal', length=220,
                                label='SHARPNESS', command=self.on_adjust_change)
        self.scale_s.set(0)
        self.scale_s.pack(fill='x', padx=1, pady=0)

        btn_row = tk.Frame(adj_frame)
        btn_row.pack(fill='x', padx=2, pady=0)
        tk.Button(btn_row, text='Apply Adjustments', command=self.apply_adjustments).pack(side='left', padx=2)
        tk.Button(btn_row, text='Reset Sliders', command=self.reset_adjustments).pack(side='right', padx=2)

        # Right: Canvas and status
        right = tk.Frame(root)
        right.pack(side='right', expand=True, fill='both')

        self.canvas = tk.Canvas(right, bg='grey')
        self.canvas.pack(expand=True, fill='both')
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.status = tk.Label(right, text='No image loaded', anchor='w')
        self.status.pack(fill='x')

        # Manual crop state
        self.manual_mode = False
        self.crop_rect_id = None
        self.start_x = self.start_y = 0

        # Keep GUI responsive to resize
        root.bind('<Configure>', lambda e: self.show_image())

        # --- NEW: Keyboard shortcut for Undo ---
        root.bind_all('<Control-z>', self._undo_event)

    # --- NEW: History helpers ---
    def push_history(self):
        """Save current image state before a destructive edit."""
        if self.img is None:
            return
        self.history.append(self.img.copy())
        # Cap size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def undo(self):
        """Revert to previous image state."""
        if not self.history:
            self.update_status()  # no change, just refresh label
            return
        self.img = self.history.pop()
        # clear any preview when undoing
        self.preview_img = None
        self.show_image()
        self.update_status()

    def _undo_event(self, event):
        self.undo()

    # --- File / Navigation ---
    def open_file(self):
        fn = filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if not fn: return
        self.load_file(fn)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        exts = ('.png','.jpg','.jpeg','.bmp','.tiff')
        files = [os.path.join(folder,f) for f in sorted(os.listdir(folder)) if f.lower().endswith(exts)]
        if not files:
            messagebox.showinfo('Info','No images found in folder')
            return
        self.file_list = files
        self.index = 0
        self.load_file(self.file_list[self.index])

    def load_file(self, path):
        try:
            im = Image.open(path).convert('RGB')
        except Exception as e:
            messagebox.showerror('Error', f'Unable to open: {path}\\n{e}')
            return
        self.filename = path
        self.orig = im.copy()
        self.img = im
        self.history = []  # NEW: clear undo stack on new file
        self.preview_img = None  # NEW: clear preview
        # If folder mode and file_list empty, create list with this file
        if not self.file_list:
            self.file_list = [path]
            self.index = 0
        else:
            try:
                self.index = self.file_list.index(path)
            except ValueError:
                # standalone file
                self.file_list = [path]
                self.index = 0
        self.update_status()
        self.show_image()

    def prev_image(self):
        if not self.file_list: return
        self.index = (self.index - 1) % len(self.file_list)
        self.load_file(self.file_list[self.index])

    def next_image(self):
        if not self.file_list: return
        self.index = (self.index + 1) % len(self.file_list)
        self.load_file(self.file_list[self.index])

    def update_status(self):
        nm = os.path.basename(self.filename) if self.filename else 'No file'
        hist = f" | Undo: {len(self.history)}" if self.img is not None else ""
        self.status.config(text=f'{nm}   ({self.index+1}/{len(self.file_list)}){hist}' if self.file_list else nm+hist)

    # --- Display ---
    def show_image(self):
        # Prefer preview image if available
        src_img = self.preview_img if self.preview_img is not None else self.img
        if src_img is None:
            self.canvas.delete('all')
            return
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        w,h = src_img.size
        scale = min(cw/w, ch/h, 1)
        disp = src_img.copy()
        if scale < 1:
            disp = disp.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(cw//2, ch//2, image=self.tkimg, anchor='c')

    # --- Manual crop handlers ---
    def start_manual_crop(self):
        if self.img is None:
            messagebox.showinfo('Info','Open an image first')
            return
        self.manual_mode = True
        # removed dialog

    def on_mouse_down(self, event):
        if not self.manual_mode: return
        self.start_x, self.start_y = event.x, event.y
        self.crop_rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        if not self.manual_mode or not self.crop_rect_id: return
        self.canvas.coords(self.crop_rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        if not self.manual_mode or not self.crop_rect_id: return
        x0,y0,x1,y1 = self.canvas.coords(self.crop_rect_id)
        # map to image coords
        imgw, imgh = self.img.size
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        scale = min(cw/imgw, ch/imgh, 1)
        disp_w, disp_h = int(imgw*scale), int(imgh*scale)
        offset_x = (cw - disp_w)/2
        offset_y = (ch - disp_h)/2
        cx0 = int(max(0,(x0 - offset_x)/scale))
        cy0 = int(max(0,(y0 - offset_y)/scale))
        cx1 = int(max(0,(x1 - offset_x)/scale))
        cy1 = int(max(0,(y1 - offset_y)/scale))
        if abs(cx1-cx0)<5 or abs(cy1-cy0)<5:
            self.canvas.delete(self.crop_rect_id)
            self.crop_rect_id = None
            self.manual_mode = False
            return
        # NEW: record state before applying crop
        self.push_history()
        self.img = self.img.crop((min(cx0,cx1), min(cy0,cy1), max(cx0,cx1), max(cy0,cy1)))
        self.canvas.delete(self.crop_rect_id)
        self.crop_rect_id = None
        self.manual_mode = False
        self.preview_img = None  # any preview invalid now
        self.show_image()
        self.update_status()

    
    # --- Added: Delete current image from disk ---
    def delete_image(self):
        if not self.filename:
            return
        path = self.filename
        try:
            # Determine next index before deletion
            next_index = None
            if self.file_list:
                if len(self.file_list) > 1:
                    next_index = (self.index + 1) % len(self.file_list)
            # Delete directly without confirmation dialog
            os.remove(path)
        except Exception as e:
            messagebox.showerror('Error', f'Could not delete file:\\n{e}')
            return
        # Update internal list
        try:
            if path in self.file_list:
                self.file_list.remove(path)
        except Exception:
            pass
        # Load next image or clear
        if self.file_list:
            if next_index is None or next_index >= len(self.file_list):
                next_index = 0
            self.index = next_index
            self.load_file(self.file_list[self.index])
        else:
            self.index = -1
            self.filename = None
            self.orig = None
            self.img = None
            self.history = []
            self.preview_img = None
            try:
                self.canvas.delete('all')
            except Exception:
                pass
            self.status.config(text='Deleted. No image loaded')
    def rename_image(self):
        if not self.filename:
            return
        folder = os.path.dirname(self.filename)
        old_name = os.path.basename(self.filename)
        new_name = simpledialog.askstring("Rename Image", f"Current name: {old_name}\nEnter new name (with extension):")
        if not new_name:
            return
        new_path = os.path.join(folder, new_name)
        try:
            os.rename(self.filename, new_path)
            if self.filename in self.file_list:
                idx = self.file_list.index(self.filename)
                self.file_list[idx] = new_path
                self.index = idx
            self.filename = new_path
            messagebox.showinfo("Success", f"File renamed to:\n{new_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename file:\n{e}")




    # --- Operations ---
    def do_auto_deskew(self):
        if self.img is None:
            messagebox.showinfo('Info','Open an image first')
            return
        self.push_history()
        self.img = auto_deskew(self.img)
        self.preview_img = None
        self.show_image()
        self.update_status()

    def do_rotate(self, deg):
        if self.img is None:
            return
        self.push_history()
        self.img = self.img.rotate(deg, expand=True, resample=Image.BICUBIC)
        self.preview_img = None
        self.show_image()
        self.update_status()

    def do_whiten_bg(self):
        if self.img is None:
            return
        self.push_history()
        self.img = whiten_background(self.img)
        self.preview_img = None
        self.show_image()
        self.update_status()

    def do_enhance_black(self):
        if self.img is None:
            return
        self.push_history()
        self.img = enhance_black_text(self.img)
        self.preview_img = None
        self.show_image()
        self.update_status()

    def do_join(self, mode="horizontal"):
        if self.img is None:
            self.update_status()
            return
        fn = filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.bmp")])
        if not fn:
            return
        try:
            im2 = Image.open(fn).convert("RGB")
            self.push_history()
            self.img = join_images([self.img, im2], mode)
            self.preview_img = None
            self.show_image()
            self.update_status()
            self.modified = True
        except Exception as e:
            self.update_status()

            # The following original snippet had extra code paths; kept intact but unreachable here.
            # (Retained to honor "keep as-is" requirement without removing features.)
            try:
                files = []  # placeholder to preserve original flow
                if not files: 
                    return
                imgs = [Image.open(f).convert('RGB') for f in files]
                out = join_images(imgs, mode=mode)
                if out:
                    self.img = out
                    self.filename = None
                    self.update_status()
                    self.show_image()
            except Exception:
                pass

    # --- Adjustments: Brightness/Contrast/Sharpness ---
    def _percent_to_factor(self, p):
        """Map slider percent [-100,100] to enhancer factor [0,2]. 0 disables, 1 original, 2 double."""
        try:
            p = float(p)
        except Exception:
            p = 0.0
        return max(0.0, 1.0 + p/100.0)

    def build_adjusted(self):
        """Create a preview image by applying B/C/S to the current image non-destructively."""
        if self.img is None:
            return None
        img = self.img.copy()
        # Apply in a stable order: Brightness -> Contrast -> Sharpness
        b = self._percent_to_factor(self.scale_b.get())
        c = self._percent_to_factor(self.scale_c.get())
        s = self._percent_to_factor(self.scale_s.get())

        if b != 1.0:
            img = ImageEnhance.Brightness(img).enhance(b)
        if c != 1.0:
            img = ImageEnhance.Contrast(img).enhance(c)
        if s != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(s)
        return img

    def on_adjust_change(self, _evt=None):
        """Live preview when sliders change; does NOT push to history until 'Apply'."""
        if self.img is None:
            return
        self.preview_img = self.build_adjusted()
        self.show_image()

    def apply_adjustments(self):
        if self.img is None:
            return
        # Build from base, then commit
        new_img = self.build_adjusted()
        if new_img is None:
            return
        self.push_history()
        self.img = new_img
        self.preview_img = None
        # Reset sliders to neutral after apply
        self.scale_b.set(0)
        self.scale_c.set(0)
        self.scale_s.set(0)
        self.show_image()
        self.update_status()

    def reset_adjustments(self):
        """Reset sliders and clear preview (no destructive change)."""
        self.scale_b.set(0)
        self.scale_c.set(0)
        self.scale_s.set(0)
        self.preview_img = None
        self.show_image()

    def save_image(self):
        if self.img is None:
            return
        if self.filename:
            try:
                self.img.save(self.filename)
                self.orig = self.img.copy()
                return
            except Exception as e:
                print("Save error:", e)
                return
        else:
            # If no filename, just skip (no dialog)
            return

    def print_image(self):
        if self.img is None:
            return
        ok = print_pil_image(self.img)
        if ok:
            messagebox.showinfo('Print','Print command sent (Windows).')
        else:
            messagebox.showinfo('Print','Image opened. On non-Windows OS save and print from viewer.')

    def reset_image(self):
        if self.orig is None:
            return
        # Reset should also be undoable
        self.push_history()
        self.img = self.orig.copy()
        self.preview_img = None
        self.show_image()
        self.update_status()


if __name__=='__main__':
    root = tk.Tk()
    root.state('zoomed')  # open in full screen (Windows)
    try:
        root.attributes('-fullscreen', True)  # for Linux/Mac
    except Exception:
        pass
    app = PictureManagerApp(root)

    # ---------------- Keyboard Shortcuts ----------------
    root.bind('o', lambda e: app.open_file())
    root.bind('f', lambda e: app.open_folder())
    root.bind('p', lambda e: app.prev_image())
    root.bind('<Left>', lambda e: app.prev_image())
    root.bind('<Right>', lambda e: app.next_image())
    root.bind('n', lambda e: app.next_image())
    root.bind('c', lambda e: app.start_manual_crop())
    root.bind('a', lambda e: app.do_auto_deskew())
    root.bind('-', lambda e: app.do_rotate(-1))
    root.bind('+', lambda e: app.do_rotate(1))
    root.bind('w', lambda e: app.do_whiten_bg())
    root.bind('b', lambda e: app.do_enhance_black())
    root.bind('h', lambda e: app.do_join('horizontal'))
    root.bind('v', lambda e: app.do_join('vertical'))
    root.bind('<Control-s>', lambda e: app.save_image())
    root.bind('<Control-p>', lambda e: app.print_image())
    root.bind('r', lambda e: app.rename_image())  # R Shortcut (changed from reset to rename)
    root.bind('<F2>', lambda e: app.rename_image())  # F2 Shortcut
    root.bind('d', lambda e: app.delete_image())
    root.bind('x', lambda e: root.quit())

    root.mainloop()
