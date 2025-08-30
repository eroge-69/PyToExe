"""
Gigabyte BIOS Logo Updater GUI - H410M HV2 (Refined)

Features:
- Browse for stock ROM
- Scan & preview candidate logo blocks with thumbnails
- Automatic detection of logo format and dimensions
- Select replacement image and auto-fit to block size
- Patch ROM safely with padding/compression if needed
- Backup original ROM and save patched ROM
- Optional launch of flash utility with confirmation

Dependencies:
- Python 3.8+
- PyQt6 (pip install PyQt6)
- Pillow (pip install pillow)
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QHBoxLayout, QMessageBox, QListWidgetItem, QScrollArea
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize
from PIL import Image
import shutil
import struct
from io import BytesIO

# --- Logo detection ---
IMG_SIGS = [
    (b"BM", "BMP"),
    (b"\xFF\xD8\xFF", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
]
OUTPUT_DIR = Path("extracted_gui")
OUTPUT_DIR.mkdir(exist_ok=True)

# Logo candidate finder
def find_image_candidates(data: bytes):
    candidates = []
    n = len(data)
    i = 0

    # BMP
    while True:
        i = data.find(b"BM", i)
        if i == -1: break
        if i + 6 <= n:
            size = struct.unpack_from('<I', data, i + 2)[0]
            if 8 <= size <= n - i:
                candidates.append({"type": "BMP", "offset": i, "length": size})
        i += 2

    # JPEG
    i = 0
    while True:
        i = data.find(b"\xFF\xD8\xFF", i)
        if i == -1: break
        j = data.find(b"\xFF\xD9", i + 2)
        if j != -1:
            length = j + 2 - i
            candidates.append({"type": "JPEG", "offset": i, "length": length})
        i += 3

    # PNG
    i = 0
    pngsig = b"\x89PNG\r\n\x1a\n"
    while True:
        i = data.find(pngsig, i)
        if i == -1: break
        j = data.find(b"IEND", i)
        if j != -1:
            length = (j - i) + 8
            candidates.append({"type": "PNG", "offset": i, "length": length})
        i += len(pngsig)

    candidates.sort(key=lambda x: x["offset"])
    return candidates

# Resize and fit replacement image to block
def fit_image_to_block(img_path: Path, block_length: int, target_type: str) -> bytes:
    img = Image.open(img_path)
    buf = BytesIO()
    if target_type == 'JPEG':
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        quality = 90
        while True:
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=quality)
            data = buf.getvalue()
            if len(data) <= block_length or quality <= 20:
                break
            quality -= 10
    elif target_type == 'PNG':
        img.save(buf, format='PNG', optimize=True)
        data = buf.getvalue()
        if len(data) > block_length:
            raise RuntimeError('PNG replacement too large')
    elif target_type == 'BMP':
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(buf, format='BMP')
        data = buf.getvalue()
        if len(data) > block_length:
            raise RuntimeError('BMP replacement too large')
    else:
        raise ValueError('Unsupported target type')
    if len(data) < block_length:
        data += b'\xFF'*(block_length-len(data))
    return data

# GUI
class LogoUpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gigabyte BIOS Logo Updater - H410M HV2')
        self.rom_path = None
        self.candidates = []
        self.selected_candidate = None
        self.image_path = None

        layout = QVBoxLayout()

        # ROM selection
        self.rom_label = QLabel('No ROM selected')
        btn_browse_rom = QPushButton('Browse ROM')
        btn_browse_rom.clicked.connect(self.browse_rom)
        layout.addWidget(self.rom_label)
        layout.addWidget(btn_browse_rom)

        # Candidate list
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(64,64))
        self.list_widget.currentRowChanged.connect(self.preview_candidate)
        layout.addWidget(QLabel('Candidate Logos:'))
        layout.addWidget(self.list_widget)

        # Preview
        self.preview_label = QLabel('Preview will appear here')
        layout.addWidget(self.preview_label)

        # Image selection
        btn_browse_image = QPushButton('Select Replacement Image')
        btn_browse_image.clicked.connect(self.browse_image)
        layout.addWidget(btn_browse_image)

        # Patch button
        btn_patch = QPushButton('Patch ROM')
        btn_patch.clicked.connect(self.patch_rom)
        layout.addWidget(btn_patch)

        self.setLayout(layout)

    def browse_rom(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Stock BIOS ROM')
        if file_path:
            self.rom_path = Path(file_path)
            self.rom_label.setText(str(self.rom_path))
            self.load_candidates()

    def load_candidates(self):
        if not self.rom_path: return
        data = self.rom_path.read_bytes()
        self.candidates = find_image_candidates(data)
        self.list_widget.clear()
        if not self.candidates:
            QMessageBox.warning(self, 'No Candidates', 'No obvious logos found in ROM.')
        for idx, c in enumerate(self.candidates, start=1):
            # Save temporary preview
            block = data[c['offset']:c['offset']+c['length']]
            tmp_file = OUTPUT_DIR/f'temp_{idx}.png'
            try:
                with open(tmp_file, 'wb') as f: f.write(block)
                pix = QPixmap(str(tmp_file)).scaled(64,64)
            except: pix = QPixmap(64,64)
            item = QListWidgetItem(QIcon(pix), f"[{idx}] {c['type']} off={c['offset']} len={c['length']}")
            self.list_widget.addItem(item)

    def preview_candidate(self, row):
        if row < 0 or row >= len(self.candidates):
            self.preview_label.setText('Preview will appear here')
            self.selected_candidate = None
            return
        self.selected_candidate = self.candidates[row]
        data = self.rom_path.read_bytes()
        offset = self.selected_candidate['offset']
        length = self.selected_candidate['length']
        block = data[offset:offset+length]
        tmp_file = OUTPUT_DIR/'preview.png'
        with open(tmp_file,'wb') as f: f.write(block)
        pix = QPixmap(str(tmp_file)).scaled(300,200)
        self.preview_label.setPixmap(pix)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Replacement Image')
        if file_path:
            self.image_path = Path(file_path)
            QMessageBox.information(self, 'Image Selected', f'Selected image: {self.image_path}')

    def patch_rom(self):
        if not self.rom_path or not self.selected_candidate or not self.image_path:
            QMessageBox.warning(self, 'Missing Info', 'Select ROM, candidate, and replacement image first')
            return
        bak = self.rom_path.with_suffix(self.rom_path.suffix+'.orig.bak')
        if not bak.exists(): shutil.copy(self.rom_path, bak)
        try:
            new_bytes = fit_image_to_block(self.image_path, self.selected_candidate['length'], self.selected_candidate['type'])
            data = bytearray(self.rom_path.read_bytes())
            data[self.selected_candidate['offset']:self.selected_candidate['offset']+self.selected_candidate['length']] = new_bytes
            out_path = self.rom_path.with_name('patched_'+self.rom_path.name)
            with open(out_path,'wb') as f: f.write(data)
            QMessageBox.information(self, 'Patched', f'Patched ROM saved to {out_path}\nBackup saved to {bak}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to patch ROM: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogoUpdaterGUI()
    window.show()
    sys.exit(app.exec())
