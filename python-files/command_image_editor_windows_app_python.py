"""
CommandImageEditor - single-file Python app for Windows 11 (Tkinter)
==================================================================

Why this rewrite
----------------
You ran the earlier PyQt6-based file and encountered:

    ModuleNotFoundError: No module named 'PyQt6'

PyQt6 is not guaranteed to be available in every environment. This version uses **Tkinter** (bundled with CPython on Windows) so the GUI will run without installing PyQt6. Image processing still uses Pillow (PIL).

What this file provides
-----------------------
- A simple GUI image editor that accepts textual commands (same language as before):
    rotate <deg>
    resize <width>x<height>
    grayscale
    blur <radius>
    sharpen
    contrast <factor>
    brightness <factor>
    crop x,y,w,h
    flip horizontal|vertical
    overlay_text "your text" at x,y size N
    posterize <bits>
    invert
    strip_exif
- Commands may be separated by `;` or newline and are applied in order.
- An automated test-suite is included. Run `python app.py test` to run tests (these do not open the GUI).

Notes
-----
- Rotation uses `expand=True` (output canvas grows to contain the rotated image). If you'd rather keep the original canvas size (cropping rotated parts), tell me and I'll change the implementation and tests.
- If Tkinter (or Pillow's ImageTk) is missing, the program still supports test mode.

Dependencies
------------
- Python 3.8+ (3.11 recommended)
- Pillow (`pip install Pillow`)
- Tkinter (bundled with CPython on Windows; if missing, install the official Windows distribution which includes it)

Run
---
- Test mode (no GUI):
    python app.py test

- GUI mode:
    python app.py

Packaging to EXE (PyInstaller)
-----------------------------
PyInstaller usually bundles Tkinter automatically. Example:

    pip install pyinstaller
    pyinstaller --onefile --windowed app.py

If the generated EXE misses TCL/TK files, build in folder mode (no `--onefile`) to inspect bundled files and include tcl/tk data if needed.

License
-------
MIT

"""

import sys
import re
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageFont, ImageDraw

# Import Tkinter and ImageTk if available; GUI is optional for test mode
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from PIL import ImageTk
except Exception:
    tk = None
    ImageTk = None


SUPPORTED_EXTS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']


# -----------------------
# Command parsing / apply
# -----------------------

def parse_crop_args(arg: str) -> Tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in arg.split(',') if p.strip()]
    if len(parts) != 4:
        raise ValueError('crop requires 4 integers: x,y,w,h')
    return tuple(parts)


def parse_size(arg: str) -> Tuple[int, int]:
    m = re.match(r"(\d+)\s*[xX]\s*(\d+)", arg)
    if not m:
        raise ValueError('resize requires WIDTHxHEIGHT')
    return int(m.group(1)), int(m.group(2))


def apply_command(img: Image.Image, cmd: str) -> Image.Image:
    """Apply a single textual command to a PIL Image and return a new image.

    The function is case-insensitive for command keywords and is defensive about types.
    It returns a (usually) new Image object so callers may keep the original image intact.
    """
    cmd = cmd.strip()
    if not cmd:
        return img

    # helper for case-insensitive regex matching
    def imatch(pattern, s=cmd):
        return re.match(pattern, s, flags=re.IGNORECASE)

    # rotate
    m = imatch(r'rotate\s+(-?\d+)')
    if m:
        deg = int(m.group(1))
        # expand=True so output canvas contains full rotated image (no cropping)
        return img.rotate(-deg, expand=True)

    # resize
    m = imatch(r'resize\s+(\d+\s*[xX]\s*\d+)')
    if m:
        w, h = parse_size(m.group(1))
        return img.resize((w, h), Image.LANCZOS)

    # grayscale / grey
    if re.fullmatch(r'grayscale|grey|gray', cmd, flags=re.IGNORECASE):
        return img.convert('L').convert('RGBA')

    # blur (allow float radius)
    m = imatch(r'blur\s+(\d+(?:\.\d+)?)')
    if m:
        r = float(m.group(1))
        return img.filter(ImageFilter.GaussianBlur(radius=r))

    # sharpen
    if re.fullmatch(r'sharpen', cmd, flags=re.IGNORECASE):
        return img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    # contrast
    m = imatch(r'contrast\s+([0-9]*\.?[0-9]+)')
    if m:
        f = float(m.group(1))
        return ImageEnhance.Contrast(img).enhance(f)

    # brightness
    m = imatch(r'brightness\s+([0-9]*\.?[0-9]+)')
    if m:
        f = float(m.group(1))
        return ImageEnhance.Brightness(img).enhance(f)

    # crop
    m = imatch(r'crop\s+([0-9\s,]+)')
    if m:
        x, y, w, h = parse_crop_args(m.group(1))
        return img.crop((x, y, x + w, y + h))

    # flip
    if re.fullmatch(r'flip\s+horizontal|flip_horizontal|flip-h', cmd, flags=re.IGNORECASE):
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    if re.fullmatch(r'flip\s+vertical|flip_vertical|flip-v', cmd, flags=re.IGNORECASE):
        return img.transpose(Image.FLIP_TOP_BOTTOM)

    # overlay text: overlay_text "text" at X,Y size N
    m = imatch(r'overlay_text\s+"([^\"]+)"\s+at\s+(\d+)\s*,\s*(\d+)\s+size\s+(\d+)')
    if m:
        text = m.group(1)
        x = int(m.group(2)); y = int(m.group(3)); size = int(m.group(4))
        dst = img.convert('RGBA').copy()
        drawable = ImageDraw.Draw(dst)
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except Exception:
            font = ImageFont.load_default()
        drawable.text((x, y), text, fill=(255,255,255,255), font=font)
        return dst

    # posterize
    m = imatch(r'posterize\s+(\d+)')
    if m:
        bits = int(m.group(1))
        return ImageOps.posterize(img.convert('RGB'), bits).convert('RGBA')

    # invert
    if re.fullmatch(r'invert', cmd, flags=re.IGNORECASE):
        return ImageOps.invert(img.convert('RGB')).convert('RGBA')

    # strip exif
    if re.fullmatch(r'strip_exif', cmd, flags=re.IGNORECASE):
        data = list(img.getdata())
        new = Image.new(img.mode, img.size)
        new.putdata(data)
        return new

    raise ValueError(f'Unknown or malformed command: "{cmd}"')


# -----------------------
# GUI using Tkinter
# -----------------------

class MainWindow:
    def __init__(self, root):
        if tk is None or ImageTk is None:
            raise RuntimeError('Tkinter or PIL.ImageTk not available in this Python environment')

        self.root = root
        root.title('Command Image Editor')
        root.geometry('1000x700')

        # Main frames
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        right_frame = tk.Frame(root, width=360)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=6)

        # Preview label
        self.preview_label = tk.Label(left_frame, text='Open an image to begin', bd=1, relief=tk.SOLID)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        self.preview_label.bind('<Configure>', lambda e: self._update_preview_image())

        # Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(6,0))
        open_btn = tk.Button(btn_frame, text='Open', command=self.open_image)
        open_btn.pack(side=tk.LEFT, padx=4)
        save_btn = tk.Button(btn_frame, text='Save As', command=self.save_image)
        save_btn.pack(side=tk.LEFT, padx=4)

        # Commands text
        tk.Label(right_frame, text='Commands (separate with ; or newline):').pack(anchor='w')
        self.cmd_text = tk.Text(right_frame, height=8)
        self.cmd_text.insert('1.0', 'resize 800x600; brightness 1.2; overlay_text "Hello" at 10,10 size 24')
        self.cmd_text.pack(fill=tk.X, pady=(0,6))

        run_btn = tk.Button(right_frame, text='Run Commands', command=self.run_commands)
        run_btn.pack(fill=tk.X)

        tk.Label(right_frame, text='Log / Output:').pack(anchor='w', pady=(6,0))
        self.log_text = tk.Text(right_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # state
        self.pil_image = None
        self.tk_image_ref = None  # keep reference to PhotoImage
        self.image_path = None

    def _log(self, text: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + '\n')
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def open_image(self):
        fname = filedialog.askopenfilename(title='Open image', initialdir=str(Path.home()), filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp *.tiff')])
        if not fname:
            return
        try:
            img = Image.open(fname).convert('RGBA')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open image: {e}')
            return
        self.pil_image = img
        self.image_path = fname
        self._update_preview_image()
        self._log(f'Loaded: {fname}')

    def save_image(self):
        if self.pil_image is None:
            messagebox.showwarning('No image', 'No image loaded')
            return
        fname = filedialog.asksaveasfilename(title='Save image as', initialfile='edited.png', defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg;*.jpeg'), ('BMP', '*.bmp')])
        if not fname:
            return
        try:
            ext = Path(fname).suffix.lower()
            if ext in ('.jpg', '.jpeg'):
                self.pil_image.convert('RGB').save(fname, quality=95)
            else:
                self.pil_image.save(fname)
            self._log(f'Saved to: {fname}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save image: {e}')

    def run_commands(self):
        if self.pil_image is None:
            messagebox.showwarning('No image', 'Load an image first')
            return
        raw = self.cmd_text.get('1.0', tk.END).strip()
        if not raw:
            messagebox.showwarning('No commands', 'Enter commands to run')
            return
        parts = re.split(r'[;\n]+', raw)
        img = self.pil_image.copy()
        self._log('Running commands...')
        for i, p in enumerate(parts, 1):
            p = p.strip()
            if not p:
                continue
            try:
                img = apply_command(img, p)
                self._log(f'[{i}] OK: {p}')
            except Exception as e:
                self._log(f'[{i}] ERROR for "{p}": {e}')
                break
        else:
            self.pil_image = img
            self._update_preview_image()
            self._log('All commands applied successfully')

    def _update_preview_image(self):
        if self.pil_image is None:
            self.preview_label.config(image='', text='Open an image to begin')
            return
        # compute size to fit label
        w = max(1, self.preview_label.winfo_width())
        h = max(1, self.preview_label.winfo_height())
        disp = self.pil_image.copy()
        disp.thumbnail((w, h), Image.LANCZOS)
        try:
            tk_img = ImageTk.PhotoImage(disp)
        except Exception:
            tk_img = None
        if tk_img is not None:
            self.tk_image_ref = tk_img
            self.preview_label.config(image=tk_img, text='')
        else:
            self.preview_label.config(text='Preview not available', image='')


# -----------------------
# Tests (automated)
# -----------------------

def run_tests():
    print('Running tests for apply_command()...')
    failures = []

    def expect(cond, msg):
        if not cond:
            failures.append(msg)

    # base image: 200x100 blue
    base = Image.new('RGBA', (200, 100), (0, 0, 255, 255))

    # resize
    try:
        r = apply_command(base.copy(), 'resize 100x50')
        expect(r.size == (100, 50), f'resize expected (100,50) got {r.size}')
    except Exception as e:
        failures.append(f'resize raised {e}')

    # rotate 90 (expand -> size swaps)
    try:
        r = apply_command(base.copy(), 'rotate 90')
        expect(r.size[0] == 100 and r.size[1] == 200, f'rotate 90 expected dims swapped got {r.size}')
    except Exception as e:
        failures.append(f'rotate raised {e}')

    # grayscale
    try:
        r = apply_command(base.copy(), 'grayscale')
        expect(r.mode in ('RGBA', 'RGB', 'L'), f'grayscale unexpected mode {r.mode}')
        px = r.convert('RGB').getpixel((10, 10))
        expect(px[0] == px[1] == px[2], f'grayscale pixel channels not equal {px}')
    except Exception as e:
        failures.append(f'grayscale raised {e}')

    # invert
    try:
        r = apply_command(base.copy(), 'invert')
        px = r.convert('RGB').getpixel((0, 0))
        expect(px == (255, 255, 0), f'invert of blue expected (255,255,0) got {px}')
    except Exception as e:
        failures.append(f'invert raised {e}')

    # crop
    try:
        r = apply_command(base.copy(), 'crop 10,5,50,40')
        expect(r.size == (50, 40), f'crop expected (50,40) got {r.size}')
    except Exception as e:
        failures.append(f'crop raised {e}')

    # flip horizontal (make a 2x1 image with different left/right)
    try:
        im = Image.new('RGBA', (2, 1))
        im.putpixel((0, 0), (255, 0, 0, 255))
        im.putpixel((1, 0), (0, 255, 0, 255))
        r = apply_command(im, 'flip horizontal')
        expect(r.getpixel((0, 0)) == (0, 255, 0, 255) and r.getpixel((1, 0)) == (255, 0, 0, 255), 'flip horizontal did not swap pixels')
    except Exception as e:
        failures.append(f'flip raised {e}')

    # posterize smoke test
    try:
        r = apply_command(base.copy(), 'posterize 2')
        expect(isinstance(r, Image.Image), 'posterize did not return an Image')
    except Exception as e:
        failures.append(f'posterize raised {e}')

    # overlay_text smoke test (should not crash)
    try:
        r = apply_command(base.copy(), 'overlay_text "Hi" at 5,5 size 12')
        expect(isinstance(r, Image.Image), 'overlay_text did not return Image')
    except Exception as e:
        failures.append(f'overlay_text raised {e}')

    # brightness & contrast should not change size and not crash
    try:
        r1 = apply_command(base.copy(), 'brightness 1.5')
        r2 = apply_command(base.copy(), 'contrast 0.8')
        expect(r1.size == base.size and r2.size == base.size, 'brightness/contrast changed image size')
    except Exception as e:
        failures.append(f'brightness/contrast raised {e}')

    # blur should not change size
    try:
        r = apply_command(base.copy(), 'blur 2')
        expect(r.size == base.size, 'blur changed image size')
    except Exception as e:
        failures.append(f'blur raised {e}')

    # strip_exif keeps size
    try:
        r = apply_command(base.copy(), 'strip_exif')
        expect(r.size == base.size, 'strip_exif changed size')
    except Exception as e:
        failures.append(f'strip_exif raised {e}')

    # multiple commands in sequence
    try:
        r = base.copy()
        r = apply_command(r, 'resize 50x25')
        r = apply_command(r, 'invert')
        expect(r.size == (50, 25), f'multiple commands final size expected (50,25) got {r.size}')
    except Exception as e:
        failures.append(f'multiple commands raised {e}')

    # unknown command should raise
    try:
        try:
            apply_command(base.copy(), 'thiscommanddoesnotexist')
            failures.append('unknown command did not raise')
        except ValueError:
            pass
    except Exception as e:
        failures.append(f'unknown command test raised {e}')

    if failures:
        print('TESTS FAILED:')
        for f in failures:
            print(' -', f)
        return 1
    else:
        print('All tests passed ✅')
        return 0


# -----------------------
# Entry point
# -----------------------

def main():
    # Support a test mode which runs without GUI (useful if Tkinter isn't present or for CI)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('test', '--test'):
        rc = run_tests()
        sys.exit(rc)

    if tk is None or ImageTk is None:
        print('Tkinter or ImageTk is not available in this Python environment. GUI cannot run.')
        print('You can still run the automated tests: python app.py test')
        sys.exit(1)

    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
