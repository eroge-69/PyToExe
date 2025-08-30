"""
lut_generator_pyqt.py — Light Pro PyQt5 LUT Generator

Install dependencies:
    pip install numpy opencv-python scikit-learn pillow pyqt5

Run:
    python lut_generator_pyqt.py

Create single-file Windows EXE later:
    pip install pyinstaller
    pyinstaller --onefile --noconsole lut_generator_pyqt.py
"""

import os
import numpy as np
import cv2
from sklearn.cluster import KMeans
from PIL import Image, ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets

# ---------- Config ----------
MAX_SAMPLE_PIXELS = 120_000
PREVIEW_MAX_WIDTH = 900
# ----------------------------

def sample_pixels(img_rgb):
    """Return sampled pixels (N,3) normalized 0..1"""
    h, w, _ = img_rgb.shape
    pixels = img_rgb.reshape(-1, 3).astype(np.float32) / 255.0
    total = pixels.shape[0]
    if total > MAX_SAMPLE_PIXELS:
        idx = np.random.choice(total, MAX_SAMPLE_PIXELS, replace=False)
        pixels = pixels[idx]
    return pixels

def extract_colors(image_path, num_colors=8):
    """Return centers (num_colors,3 in 0..1), full image RGB uint8, labels for full pixels"""
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError("Can't read image. Check file path/format.")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    sampled = sample_pixels(img_rgb)
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(sampled)
    centers = kmeans.cluster_centers_.astype(np.float32)  # 0..1
    # compute labels for full image pixels
    full = img_rgb.reshape(-1, 3).astype(np.float32) / 255.0
    dists = np.linalg.norm(full[:, None, :] - centers[None, :, :], axis=2)
    labels = np.argmin(dists, axis=1)
    return centers, img_rgb, labels

def rgb_to_hex(col):
    r, g, b = (np.clip(col, 0, 1) * 255).astype(int)
    return f"#{r:02x}{g:02x}{b:02x}"

def apply_preset(colors, mode):
    colors = colors.copy().astype(np.float32)
    if mode == "Original":
        pass
    elif mode == "Warm":
        colors[:,0] = np.clip(colors[:,0] * 1.08 + 0.02, 0, 1)
        colors[:,2] = np.clip(colors[:,2] * 0.9, 0, 1)
    elif mode == "Cool":
        colors[:,2] = np.clip(colors[:,2] * 1.08 + 0.02, 0, 1)
        colors[:,0] = np.clip(colors[:,0] * 0.92, 0, 1)
    elif mode == "Cinematic":
        colors = np.clip(np.power(colors, 0.95), 0, 1)
        colors[:,2] = np.clip(colors[:,2] * 1.06, 0, 1)
        colors[:,0] = np.clip(colors[:,0] * 1.03, 0, 1)
    elif mode == "Muted":
        means = colors.mean(axis=1, keepdims=True)
        colors = np.clip((colors + means) / 2.0, 0, 1)
    return colors

def generate_cube_lut_file(output_path, dominant_colors, size=17, title="Generated LUT"):
    dom = np.array(dominant_colors, dtype=np.float32)
    if dom.size == 0:
        raise ValueError("No colors to write to LUT.")
    with open(output_path, "w") as f:
        f.write("# Generated LUT\n")
        f.write(f"TITLE \"{title}\"\n")
        f.write(f"LUT_3D_SIZE {size}\n")
        # iterate b,g,r and write r g b per line
        for b in range(size):
            for g in range(size):
                for r in range(size):
                    rgb = np.array([r, g, b], dtype=np.float32) / (size - 1)
                    dists = np.linalg.norm(dom - rgb, axis=1)
                    nearest = dom[np.argmin(dists)]
                    f.write(f"{nearest[0]:.6f} {nearest[1]:.6f} {nearest[2]:.6f}\n")

def map_image_to_palette(img_rgb, palette_colors):
    h, w, _ = img_rgb.shape
    full = img_rgb.reshape(-1, 3).astype(np.float32) / 255.0
    dom = np.array(palette_colors, dtype=np.float32)
    if dom.size == 0:
        return img_rgb.copy()
    dists = np.linalg.norm(full[:, None, :] - dom[None, :, :], axis=2)
    nearest_idx = np.argmin(dists, axis=1)
    mapped = dom[nearest_idx]
    mapped_img = (mapped.reshape(h, w, 3) * 255.0).astype(np.uint8)
    return mapped_img

def numpy_to_qpixmap(img_rgb):
    """Convert HxWx3 uint8 numpy RGB to QPixmap"""
    pil = Image.fromarray(img_rgb)
    qim = ImageQt.ImageQt(pil)
    return QtGui.QPixmap.fromImage(qim)

# ---------- PyQt5 GUI App ----------

class LutApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LUT Generator — Light Pro (PyQt5)")
        self.resize(1200, 720)

        # state
        self.file_path = None
        self.centers = None
        self.img_rgb = None
        self.labels = None
        self.swatch_checkboxes = []  # list of (QCheckBox, center array)

        # main layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)

        # left controls
        ctrl = QtWidgets.QFrame()
        ctrl.setMaximumWidth(320)
        ctrl_layout = QtWidgets.QVBoxLayout(ctrl)
        main_layout.addWidget(ctrl)

        btn_load = QtWidgets.QPushButton("Load Image")
        btn_load.clicked.connect(self.load_image)
        ctrl_layout.addWidget(btn_load)

        ctrl_layout.addSpacing(6)
        ctrl_layout.addWidget(QtWidgets.QLabel("Extract colors (2–50):"))
        self.spin_colors = QtWidgets.QSpinBox()
        self.spin_colors.setRange(2, 50)
        self.spin_colors.setValue(8)
        ctrl_layout.addWidget(self.spin_colors)

        ctrl_layout.addSpacing(6)
        ctrl_layout.addWidget(QtWidgets.QLabel("Preset mode:"))
        self.combo_preset = QtWidgets.QComboBox()
        self.combo_preset.addItems(["Original", "Warm", "Cool", "Cinematic", "Muted"])
        ctrl_layout.addWidget(self.combo_preset)

        ctrl_layout.addSpacing(6)
        ctrl_layout.addWidget(QtWidgets.QLabel("LUT size:"))
        self.combo_lut_size = QtWidgets.QComboBox()
        self.combo_lut_size.addItems(["17", "33"])
        self.combo_lut_size.setCurrentIndex(0)
        ctrl_layout.addWidget(self.combo_lut_size)

        ctrl_layout.addSpacing(10)
        btn_extract = QtWidgets.QPushButton("Extract & Show Swatches")
        btn_extract.clicked.connect(self.extract_and_show)
        ctrl_layout.addWidget(btn_extract)

        btn_preview = QtWidgets.QPushButton("Preview Selected LUT")
        btn_preview.clicked.connect(self.preview_lut)
        ctrl_layout.addWidget(btn_preview)

        btn_save = QtWidgets.QPushButton("Save .cube LUT")
        btn_save.clicked.connect(self.save_lut)
        ctrl_layout.addWidget(btn_save)

        ctrl_layout.addStretch(1)

        # right: swatches (top) + preview (bottom)
        right_frame = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout(right_frame)
        main_layout.addWidget(right_frame, 1)

        swatch_label = QtWidgets.QLabel("Extracted colors (check to include):")
        swatch_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(swatch_label)

        self.swatches_area = QtWidgets.QScrollArea()
        self.swatches_area.setWidgetResizable(True)
        self.swatches_container = QtWidgets.QWidget()
        self.swatches_layout = QtWidgets.QGridLayout(self.swatches_container)
        self.swatches_area.setWidget(self.swatches_container)
        right_layout.addWidget(self.swatches_area, 0)

        preview_label = QtWidgets.QLabel("Preview (Original vs LUT-applied):")
        preview_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(preview_label)

        self.preview_holder = QtWidgets.QFrame()
        self.preview_layout = QtWidgets.QHBoxLayout(self.preview_holder)
        right_layout.addWidget(self.preview_holder, 1)

        # two QLabel for images
        self.lbl_orig = QtWidgets.QLabel()
        self.lbl_orig.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_mapped = QtWidgets.QLabel()
        self.lbl_mapped.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_layout.addWidget(self.lbl_orig, 1)
        self.preview_layout.addWidget(self.lbl_mapped, 1)

        # status bar
        self.status = QtWidgets.QLabel("Ready")
        self.status.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.status.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        right_layout.addWidget(self.status)

    def set_status(self, txt):
        self.status.setText(txt)
        QtWidgets.QApplication.processEvents()

    def load_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.jpg *.jpeg *.png *.bmp *.tiff)")
        if not path:
            return
        self.file_path = path
        self.set_status(f"Loaded: {os.path.basename(path)}")
        # reset state
        self.centers = None
        self.img_rgb = None
        self.labels = None
        self.clear_swatches()
        self.lbl_orig.clear()
        self.lbl_mapped.clear()

    def extract_and_show(self):
        if not self.file_path:
            QtWidgets.QMessageBox.warning(self, "No image", "Please load an image first.")
            return
        n = int(self.spin_colors.value())
        self.set_status("Extracting colors (KMeans)...")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            centers, img_rgb, labels = extract_colors(self.file_path, num_colors=n)
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self.set_status("Error")
            return
        QtWidgets.QApplication.restoreOverrideCursor()
        self.centers = centers
        self.img_rgb = img_rgb
        self.labels = labels
        self.show_swatches()
        self.set_status(f"Extracted {len(centers)} colors.")

    def clear_swatches(self):
        for i in reversed(range(self.swatches_layout.count())):
            widget = self.swatches_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.swatch_checkboxes.clear()

    def show_swatches(self):
        self.clear_swatches()
        cols = 6
        for idx, c in enumerate(self.centers):
            row = idx // cols
            col = idx % cols
            # color box
            color_hex = rgb_to_hex(c)
            box = QtWidgets.QFrame()
            box.setFixedSize(64, 64)
            box.setStyleSheet(f"background: {color_hex}; border: 1px solid #333;")
            # checkbox + label
            chk = QtWidgets.QCheckBox(f"{idx+1}")
            chk.setChecked(True)
            hex_lbl = QtWidgets.QLabel(color_hex)
            hex_lbl.setAlignment(QtCore.Qt.AlignCenter)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(box, alignment=QtCore.Qt.AlignCenter)
            vbox.addWidget(chk, alignment=QtCore.Qt.AlignCenter)
            vbox.addWidget(hex_lbl, alignment=QtCore.Qt.AlignCenter)
            container = QtWidgets.QWidget()
            container.setLayout(vbox)
            self.swatches_layout.addWidget(container, row, col)
            self.swatch_checkboxes.append((chk, c))

    def get_selected_colors(self):
        selected = [c for chk, c in self.swatch_checkboxes if chk.isChecked()]
        if not selected:
            selected = [c for chk, c in self.swatch_checkboxes]
        return np.array(selected, dtype=np.float32)

    def preview_lut(self):
        if self.img_rgb is None:
            QtWidgets.QMessageBox.warning(self, "No data", "Extract colors first.")
            return
        self.set_status("Generating preview...")
        selected = self.get_selected_colors()
        preset = self.combo_preset.currentText()
        transformed = apply_preset(selected, preset)
        mapped = map_image_to_palette(self.img_rgb, transformed)
        # resize for preview
        h, w, _ = self.img_rgb.shape
        scale = 1.0
        if w > PREVIEW_MAX_WIDTH:
            scale = PREVIEW_MAX_WIDTH / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        orig_resized = cv2.resize(self.img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        mapped_resized = cv2.resize(mapped, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        # convert to pixmaps
        pix_orig = numpy_to_qpixmap(orig_resized)
        pix_map = numpy_to_qpixmap(mapped_resized)
        self.lbl_orig.setPixmap(pix_orig.scaled(self.lbl_orig.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.lbl_mapped.setPixmap(pix_map.scaled(self.lbl_mapped.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.set_status(f"Preview ready — {len(selected)} colors, preset: {preset}")

    def resizeEvent(self, event):
        # ensure preview pixmaps scale with resizing
        if self.lbl_orig.pixmap():
            self.lbl_orig.setPixmap(self.lbl_orig.pixmap().scaled(self.lbl_orig.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        if self.lbl_mapped.pixmap():
            self.lbl_mapped.setPixmap(self.lbl_mapped.pixmap().scaled(self.lbl_mapped.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        super().resizeEvent(event)

    def save_lut(self):
        if self.centers is None or self.img_rgb is None:
            QtWidgets.QMessageBox.warning(self, "No data", "Please extract colors and preview first.")
            return
        selected = self.get_selected_colors()
        preset = self.combo_preset.currentText()
        final_palette = apply_preset(selected, preset)
        default_name = os.path.splitext(os.path.basename(self.file_path))[0]
        suggested = f"{default_name}_lut_{len(final_palette)}colors.cube"
        outpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save .cube LUT", suggested, "CUBE LUT (*.cube)")
        if not outpath:
            return
        try:
            size = int(self.combo_lut_size.currentText())
            generate_cube_lut_file(outpath, final_palette, size=size, title=f"{default_name} LUT")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error saving", str(e))
            self.set_status("Error saving")
            return
        QtWidgets.QMessageBox.information(self, "Saved", f"LUT saved: {outpath}")
        self.set_status(f"Saved: {os.path.basename(outpath)}")

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = LutApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()