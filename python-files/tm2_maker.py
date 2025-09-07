"""
TM2 Maker - Batch Converter + Viewer GUI for Windows (PyQt5)
Made by Iconic Modder

This tool supports:
 - Open .tm2 TIM2 info (width, height, bits, palette)
 - Convert TM2 -> PNG (supports paletted 4/8-bit and 16/24/32-bit simple decoding)
 - Convert PNG -> TM2 (supports 4-bit, 8-bit, 16-bit(RGB5551), 24-bit, 32-bit)
 - Save format dropdown: PNG, TIM2, TM2
 - Simple GUI (PyQt5)

Notes:
 - TIM2/TM2 format varies across games. This writer/reader uses a simple container ('TIM2' + 'IMGH') format.
 - For paletted images, palettes are stored as 16-bit RGB5551 entries (common for PS2 workflow).
 - Swizzle support: not automatically applied on TM2->PNG; tool writes linear or swizzled depending on option (advanced users can toggle in code).
"""

import os, sys, struct
from PIL import Image
from PyQt5 import QtWidgets, QtCore
import numpy as np

# ----------------- Utilities -----------------

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def pack_rgb5551(r, g, b, a=255):
    r5 = (r * 31) // 255
    g5 = (g * 31) // 255
    b5 = (b * 31) // 255
    a1 = 1 if a >= 128 else 0
    return (a1 << 15) | (r5 << 10) | (g5 << 5) | b5

def unpack_rgb5551(val):
    a = 255 if (val >> 15) & 1 else 0
    r = ((val >> 10) & 31) * 255 // 31
    g = ((val >> 5) & 31) * 255 // 31
    b = (val & 31) * 255 // 31
    return (r, g, b, a)

# simple swizzle (block-based) - optional
def simple_swizzle_bytes(data: bytes, w: int, h: int, bytes_per_pixel: int) -> bytes:
    out = bytearray(len(data))
    block_w = 16
    block_h = 8
    idx = 0
    for by in range(0, h, block_h):
        for bx in range(0, w, block_w):
            for y in range(block_h):
                for x in range(block_w):
                    sx = bx + x
                    sy = by + y
                    if sx >= w or sy >= h:
                        idx += bytes_per_pixel
                        continue
                    src_pos = (sy * w + sx) * bytes_per_pixel
                    out[idx:idx+bytes_per_pixel] = data[src_pos:src_pos+bytes_per_pixel]
                    idx += bytes_per_pixel
    return bytes(out)

# ----------------- TIM2 Writer/Reader -----------------

def write_tim2_file(out_path, width, height, bits, pixel_bytes, palette=None):
    # simple TIM2 writer using 'TIM2' + 'IMGH' chunk we defined earlier
    with open(out_path, 'wb') as f:
        f.write(b'TIM2')
        f.write(struct.pack('<I', 0))  # placeholder filesize
        img_chunk = bytearray()
        img_chunk += struct.pack('<I', width)
        img_chunk += struct.pack('<I', height)
        img_chunk += struct.pack('<I', bits)
        has_palette = 1 if palette else 0
        img_chunk += struct.pack('<I', has_palette)
        img_chunk += struct.pack('<I', len(pixel_bytes))
        if palette:
            img_chunk += struct.pack('<I', len(palette))
            img_chunk += palette
        img_chunk += pixel_bytes

        f.write(b'IMGH')
        f.write(struct.pack('<I', len(img_chunk)))
        f.write(img_chunk)

        filesize = f.tell()
        f.seek(4)
        f.write(struct.pack('<I', filesize))

def read_tim2_info(path):
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != b'TIM2':
            raise ValueError('Not a TIM2 file')
        fsize = struct.unpack('<I', f.read(4))[0]
        cid = f.read(4)
        if cid != b'IMGH':
            raise ValueError('Unsupported TIM2 variant')
        size = struct.unpack('<I', f.read(4))[0]
        width = struct.unpack('<I', f.read(4))[0]
        height = struct.unpack('<I', f.read(4))[0]
        bits = struct.unpack('<I', f.read(4))[0]
        has_pal = struct.unpack('<I', f.read(4))[0]
        pix_len = struct.unpack('<I', f.read(4))[0]
        pal_len = 0
        if has_pal:
            pal_len = struct.unpack('<I', f.read(4))[0]
        return {
            'width': width,
            'height': height,
            'bits': bits,
            'palette': bool(has_pal),
            'pixel_bytes': pix_len,
            'palette_bytes': pal_len
        }

def tim2_to_png(path, out_png):
    info = read_tim2_info(path)
    with open(path, 'rb') as f:
        # skip header up to pixel data
        # header size = 4(magic)+4(filesize)+4('IMGH')+4(chunk_size)+ (width+height+bits+has_pal+pixlen) = 4+4+4+4+20 = 36
        # if palette exists, an extra 4 + pal_len bytes present before pixel data
        f.seek(4+4+4+4+20)
        if info['palette']:
            pal_len = info['palette_bytes']
            pal_raw = f.read(pal_len)
            # palette expected as series of uint16 RGB5551
            pal = []
            for i in range(0, pal_len, 2):
                if i+2 <= pal_len:
                    val = struct.unpack('<H', pal_raw[i:i+2])[0]
                    pal.append(unpack_rgb5551(val)[:3])
            # now pixel indices follow
            pix_data = f.read(info['pixel_bytes'])
            # handle 4-bit (nibbles) or 8-bit indices
            if info['bits'] == 4:
                # expand nibbles
                indices = []
                for b in pix_data:
                    lo = b & 0x0F
                    hi = (b >> 4) & 0x0F
                    indices.append(lo)
                    indices.append(hi)
                indices = indices[:info['width'] * info['height']]
                img = Image.new('P', (info['width'], info['height']))
                # build palette flat list (R,G,B,...)
                flat = []
                for rgb in pal:
                    flat.extend(rgb)
                # pad palette to 256*3
                while len(flat) < 256*3:
                    flat.extend([0,0,0])
                img.putpalette(flat)
                img.putdata(indices)
                img.save(out_png)
                return
            elif info['bits'] == 8:
                # direct indices
                indices = list(pix_data[:info['width'] * info['height']])
                img = Image.new('P', (info['width'], info['height']))
                flat = []
                for rgb in pal:
                    flat.extend(rgb)
                while len(flat) < 256*3:
                    flat.extend([0,0,0])
                img.putpalette(flat)
                img.putdata(indices)
                img.save(out_png)
                return
            else:
                raise ValueError('Unsupported paletted bit depth: {}'.format(info['bits']))
        else:
            # non-paletted: read raw pixels
            pix_data = f.read(info['pixel_bytes'])
            if info['bits'] == 16:
                # each pixel is 2 bytes (RGB5551)
                pixels = []
                for i in range(0, len(pix_data), 2):
                    val = struct.unpack('<H', pix_data[i:i+2])[0]
                    pixels.append(unpack_rgb5551(val))
                img = Image.new('RGBA', (info['width'], info['height']))
                img.putdata(pixels)
                img.save(out_png)
                return
            elif info['bits'] == 24:
                pixels = []
                for i in range(0, len(pix_data), 3):
                    r = pix_data[i]
                    g = pix_data[i+1] if i+1 < len(pix_data) else 0
                    b = pix_data[i+2] if i+2 < len(pix_data) else 0
                    pixels.append((r,g,b,255))
                img = Image.new('RGBA', (info['width'], info['height']))
                img.putdata(pixels)
                img.save(out_png)
                return
            elif info['bits'] == 32:
                pixels = []
                for i in range(0, len(pix_data), 4):
                    r = pix_data[i]
                    g = pix_data[i+1] if i+1 < len(pix_data) else 0
                    b = pix_data[i+2] if i+2 < len(pix_data) else 0
                    a = pix_data[i+3] if i+3 < len(pix_data) else 255
                    pixels.append((r,g,b,a))
                img = Image.new('RGBA', (info['width'], info['height']))
                img.putdata(pixels)
                img.save(out_png)
                return
            else:
                raise ValueError('Unsupported non-paletted bit depth: {}'.format(info['bits']))

# PNG -> TIM2 conversion: supports 4/8 paletted (PIL quantize), 16, 24, 32
def png_to_tim2(png_path, out_path, bits=16, swizzle=False):
    img = Image.open(png_path).convert('RGBA')
    width, height = img.size

    palette_bytes = None
    pixel_bytes = b''

    if bits == 4:
        p = img.convert('RGBA').convert('P', palette=Image.ADAPTIVE, colors=16)
        # build palette as RGB5551 list
        pal = p.getpalette()[:16*3]  # list of RGB values for 16 colours
        pals = bytearray()
        for i in range(0, len(pal), 3):
            r = pal[i]; g = pal[i+1]; b = pal[i+2]
            pals += struct.pack('<H', pack_rgb5551(r,g,b,255))
        palette_bytes = bytes(pals)
        # pixel indices packed 2 per byte (low nibble first)
        inds = list(p.tobytes())
        # pack nibbles
        out = bytearray()
        for i in range(0, len(inds), 2):
            a = inds[i] & 0x0F
            b2 = inds[i+1] & 0x0F if i+1 < len(inds) else 0
            out.append((b2 << 4) | a)
        pixel_bytes = bytes(out)
    elif bits == 8:
        p = img.convert('RGBA').convert('P', palette=Image.ADAPTIVE, colors=256)
        pal = p.getpalette()[:256*3]
        pals = bytearray()
        for i in range(0, len(pal), 3):
            r = pal[i]; g = pal[i+1]; b = pal[i+2]
            pals += struct.pack('<H', pack_rgb5551(r,g,b,255))
        palette_bytes = bytes(pals)
        pixel_bytes = p.tobytes()
    elif bits == 16:
        # pack RGB5551 per pixel
        arr = list(img.getdata())
        out = bytearray()
        for (r,g,b,a) in arr:
            out += struct.pack('<H', pack_rgb5551(r,g,b,a))
        pixel_bytes = bytes(out)
    elif bits == 24:
        arr = list(img.getdata())
        out = bytearray()
        for (r,g,b,a) in arr:
            out += bytes([r,g,b])
        pixel_bytes = bytes(out)
    elif bits == 32:
        arr = list(img.getdata())
        out = bytearray()
        for (r,g,b,a) in arr:
            out += bytes([r,g,b,a])
        pixel_bytes = bytes(out)
    else:
        raise ValueError('Unsupported target bit depth')

    # optional swizzle
    if swizzle and bits in (16,24,32):
        bpp = 2 if bits==16 else (3 if bits==24 else 4)
        pixel_bytes = simple_swizzle_bytes(pixel_bytes, width, height, bpp)

    write_tim2_file(out_path, width, height, bits, pixel_bytes, palette=palette_bytes)

# ----------------- GUI -----------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TM2 Maker - Made by Iconic Modder')
        self.resize(820, 520)
        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel('<b>TM2 Maker - Made by Iconic Modder</b>')
        layout.addWidget(title)

        # TM2 info
        hbox = QtWidgets.QHBoxLayout()
        self.info_btn = QtWidgets.QPushButton('Open TM2 Info')
        self.info_btn.clicked.connect(self.open_tm2_info)
        hbox.addWidget(self.info_btn)

        self.format_dropdown = QtWidgets.QComboBox()
        self.format_dropdown.addItems(['PNG','TIM2','TM2'])
        hbox.addWidget(self.format_dropdown)

        self.swizzle_cb = QtWidgets.QCheckBox('Apply PS2-like swizzle for PNG->TM2 (optional)')
        hbox.addWidget(self.swizzle_cb)

        layout.addLayout(hbox)

        # Convert area
        conv_box = QtWidgets.QGroupBox('Convert / Save')
        v2 = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()

        self.open_tm2_path = QtWidgets.QLineEdit()
        btn_browse_tm2 = QtWidgets.QPushButton('Browse TM2')
        btn_browse_tm2.clicked.connect(self.browse_tm2)
        row_tm2 = QtWidgets.QHBoxLayout(); row_tm2.addWidget(self.open_tm2_path); row_tm2.addWidget(btn_browse_tm2)
        form.addRow('TM2 File:', row_tm2)

        self.open_png_path = QtWidgets.QLineEdit()
        btn_browse_png = QtWidgets.QPushButton('Browse PNG')
        btn_browse_png.clicked.connect(self.browse_png)
        row_png = QtWidgets.QHBoxLayout(); row_png.addWidget(self.open_png_path); row_png.addWidget(btn_browse_png)
        form.addRow('PNG File:', row_png)

        self.bits_combo = QtWidgets.QComboBox()
        self.bits_combo.addItems(['4-bit (16)','8-bit (256)','16-bit','24-bit','32-bit'])
        form.addRow('Target Bit Depth (for PNG->TM2):', self.bits_combo)

        v2.addLayout(form)
        btn_save = QtWidgets.QPushButton('Convert & Save')
        btn_save.clicked.connect(self.convert_and_save)
        v2.addWidget(btn_save)
        conv_box.setLayout(v2)
        layout.addWidget(conv_box)

        # Info box
        self.info_box = QtWidgets.QTextEdit(); self.info_box.setReadOnly(True)
        layout.addWidget(self.info_box)

        self.setLayout(layout)

    def browse_tm2(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open TM2', filter='TM2 files (*.tm2)')
        if path:
            self.open_tm2_path.setText(path)

    def browse_png(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open PNG', filter='PNG files (*.png)')
        if path:
            self.open_png_path.setText(path)

    def open_tm2_info(self):
        path = self.open_tm2_path.text().strip()
        if not path:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open TM2', filter='TM2 files (*.tm2)')
        if not path:
            return
        try:
            info = read_tim2_info(path)
            text = f\"File: {os.path.basename(path)}\\nSize: {info['width']}x{info['height']}\\nBits: {info['bits']}\\nPalette: {info['palette']}\\nPixel bytes: {info['pixel_bytes']}\\nPalette bytes: {info['palette_bytes']}\"
            self.info_box.setPlainText(text)
        except Exception as e:
            self.info_box.setPlainText('Error: ' + str(e))

    def convert_and_save(self):
        fmt = self.format_dropdown.currentText()
        if fmt == 'PNG':
            # TM2 -> PNG
            path = self.open_tm2_path.text().strip()
            if not path:
                path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open TM2', filter='TM2 files (*.tm2)')
            if not path:
                return
            save, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save PNG', filter='PNG files (*.png)')
            if not save:
                return
            try:
                tim2_to_png(path, save)
                self.info_box.append(f'Converted {os.path.basename(path)} -> {os.path.basename(save)}')
            except Exception as e:
                self.info_box.append('Error: ' + str(e))
        else:
            # PNG -> TIM2/TM2
            path = self.open_png_path.text().strip()
            if not path:
                path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open PNG', filter='PNG files (*.png)')
            if not path:
                return
            save, _ = QtWidgets.QFileDialog.getSaveFileName(self, f'Save {fmt}', filter=f'{fmt} (*.{fmt.lower()})')
            if not save:
                return
            bits_map = {0:4,1:8,2:16,3:24,4:32}
            bits = bits_map[self.bits_combo.currentIndex()]
            try:
                png_to_tim2(path, save, bits=bits, swizzle=self.swizzle_cb.isChecked())
                self.info_box.append(f'Converted {os.path.basename(path)} -> {os.path.basename(save)} [{bits}-bit]')
            except Exception as e:
                self.info_box.append('Error: ' + str(e))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
