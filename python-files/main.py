#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Compressor & Resizer (.exe-ready)
- Rich PySide6 UI
- Batch compress to target sizes (e.g., 50 KB, 100 KB, under 500 KB)
- Optional max dimensions, format conversion (JPG/PNG/WebP), metadata stripping
- Drag & drop, progress bar, live log
- Multithreaded so the UI stays responsive
"""
import os
import sys
import io
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image, ImageOps
from PySide6.QtCore import (Qt, QAbstractTableModel, QModelIndex, QThreadPool,
                            QRunnable, Signal, QObject)
from PySide6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem, QGridLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QProgressBar, QTableView,
    QMessageBox, QHeaderView, QTextEdit, QGroupBox
)

APP_NAME = "Image Compressor & Resizer"
SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'}

def human_size(num_bytes: int) -> str:
    for unit in ['B','KB','MB','GB']:
        if num_bytes < 1024.0 or unit == 'GB':
            return f"{num_bytes:.0f} {unit}" if unit == 'B' else f"{num_bytes/1024.0:.1f} {unit}"
        num_bytes /= 1024.0

@dataclass
class JobItem:
    path: str
    size: int
    status: str = "Queued"

class JobTableModel(QAbstractTableModel):
    HEADERS = ["File", "Original Size", "Status"]
    def __init__(self, items: List[JobItem]):
        super().__init__()
        self.items = items

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.items)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole,):
            return None
        item = self.items[index.row()]
        col = index.column()
        if col == 0:
            return os.path.basename(item.path)
        elif col == 1:
            return human_size(item.size)
        elif col == 2:
            return item.status
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def set_status(self, row: int, status: str):
        self.items[row].status = status
        self.dataChanged.emit(self.index(row, 2), self.index(row, 2))

class WorkerSignals(QObject):
    progress = Signal(int)                 # overall percent
    row_status = Signal(int, str)          # row, status text
    log = Signal(str)                      # text log
    done = Signal()                        # finished all

class CompressWorker(QRunnable):
    def __init__(self, rows: List[int], model: JobTableModel, opts: dict, signals: WorkerSignals):
        super().__init__()
        self.rows = rows
        self.model = model
        self.opts = opts
        self.signals = signals

    def run(self):
        total = len(self.rows)
        processed = 0
        for i, row in enumerate(self.rows):
            try:
                item = self.model.items[row]
                self.signals.row_status.emit(row, "Processing...")
                out_path = self.process_one(item.path, self.opts)
                if out_path:
                    self.signals.row_status.emit(row, f"OK → {os.path.basename(out_path)}")
                else:
                    self.signals.row_status.emit(row, "Skipped/Failed")
            except Exception as e:
                self.signals.log.emit(f"[ERROR] {e}")
                self.signals.row_status.emit(row, "Error")
            processed += 1
            pct = int((processed/total)*100)
            self.signals.progress.emit(pct)
        self.signals.done.emit()

    # --- Core compression pipeline ---
    def process_one(self, path: str, opts: dict) -> Optional[str]:
        # Read options
        target_kb = opts.get("target_kb")  # can be None or float
        under_mode = opts.get("under_mode", True)  # keep <= target if True
        max_w = opts.get("max_w", 0)
        max_h = opts.get("max_h", 0)
        out_format = opts.get("out_format", "ORIGINAL")  # ORIGINAL/JPEG/PNG/WebP
        strip_meta = opts.get("strip_meta", True)
        grayscale = opts.get("grayscale", False)
        allow_webp_fallback = opts.get("allow_webp_fallback", True)
        rename_pattern = opts.get("rename_pattern", "{name}_compressed")
        out_dir = opts.get("out_dir") or os.path.dirname(path)
        overwrite = opts.get("overwrite", False)
        png_max_colors = opts.get("png_max_colors", 256)

        # Ensure output dir
        os.makedirs(out_dir, exist_ok=True)

        # Load image
        Image.MAX_IMAGE_PIXELS = None  # disable DecompressionBombError for huge files
        with Image.open(path) as im:
            im.load()

            # Convert mode for consistent saving
            if im.mode in ("P", "1"):
                im = im.convert("RGBA")
            if grayscale:
                im = ImageOps.grayscale(im)
            else:
                # ensure RGB(A) for JPEG/WebP
                if im.mode not in ("RGB", "RGBA", "L"):
                    im = im.convert("RGBA" if "A" in im.getbands() else "RGB")

            # Resize if requested
            if max_w > 0 or max_h > 0:
                w, h = im.size
                new_w, new_h = w, h
                if max_w > 0 and w > max_w:
                    scale = max_w / w
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    w, h = new_w, new_h
                if max_h > 0 and h > max_h:
                    scale = max_h / h
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                if (new_w, new_h) != im.size:
                    im = im.resize((max(1,new_w), max(1,new_h)), Image.LANCZOS)

            # Determine output format & extension
            orig_ext = os.path.splitext(path)[1].lower() or ".jpg"
            fmt = im.format or "JPEG"
            if out_format == "ORIGINAL":
                # normalize common extensions
                if orig_ext in (".jpg", ".jpeg"):
                    fmt = "JPEG"
                elif orig_ext == ".png":
                    fmt = "PNG"
                elif orig_ext == ".webp":
                    fmt = "WEBP"
                elif orig_ext in (".bmp", ".tif", ".tiff", ".gif"):
                    fmt = "PNG"  # safer default
                else:
                    fmt = "JPEG"
            else:
                fmt = out_format.upper()

            # Build output filename
            base_name = os.path.splitext(os.path.basename(path))[0]
            out_name = rename_pattern.format(name=base_name)
            ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
            out_ext = ext_map.get(fmt, ".jpg")
            out_path = os.path.join(out_dir, out_name + out_ext)

            if (not overwrite) and os.path.exists(out_path):
                # add numeric suffix
                k = 1
                while os.path.exists(out_path):
                    out_path = os.path.join(out_dir, f"{out_name}_{k}{out_ext}")
                    k += 1

            # Save with strategy
            if target_kb is None:
                # Quality-driven save without size target
                self.save_image(im, out_path, fmt, strip_meta=strip_meta, png_max_colors=png_max_colors)
                return out_path

            # Target size strategy:
            # JPEG/WEBP: binary search on quality
            # PNG: quantize/optimize, then if still too big and allowed → WEBP fallback
            target_bytes = int(target_kb * 1024)

            if fmt in ("JPEG", "WEBP"):
                ok = self.save_to_target_lossy(im, out_path, fmt, target_bytes, under_mode, strip_meta)
                if not ok and allow_webp_fallback and fmt != "WEBP":
                    # try WEBP fallback
                    fmt = "WEBP"
                    out_path = os.path.splitext(out_path)[0] + ".webp"
                    self.save_to_target_lossy(im, out_path, fmt, target_bytes, under_mode, strip_meta)
                return out_path

            if fmt == "PNG":
                # Try quantize & optimize, then check size
                self.save_png_quantized(im, out_path, strip_meta, png_max_colors)
                if os.path.exists(out_path) and os.path.getsize(out_path) <= target_bytes:
                    return out_path
                if allow_webp_fallback:
                    # Try WEBP lossy to hit target
                    fmt = "WEBP"
                    out_path = os.path.splitext(out_path)[0] + ".webp"
                    self.save_to_target_lossy(im.convert("RGB"), out_path, fmt, target_bytes, under_mode, strip_meta)
                return out_path

            # Fallback: try WEBP
            fmt = "WEBP"
            out_path = os.path.splitext(out_path)[0] + ".webp"
            self.save_to_target_lossy(im, out_path, fmt, target_bytes, under_mode, strip_meta)
            return out_path

    # --- Saving helpers ---
    def save_image(self, im: Image.Image, out_path: str, fmt: str, strip_meta: bool = True, png_max_colors: int = 256):
        save_kwargs = {}
        if fmt == "JPEG":
            if im.mode in ("RGBA", "LA"):
                im = im.convert("RGB")
            save_kwargs.update(dict(quality=85, optimize=True, progressive=True, subsampling="4:2:0"))
            if strip_meta:
                save_kwargs["exif"] = None
        elif fmt == "PNG":
            palette_im = None
            if im.mode not in ("P", "L", "RGB", "RGBA"):
                im = im.convert("RGBA")
            save_kwargs.update(dict(optimize=True, compress_level=9))
        elif fmt == "WEBP":
            if im.mode in ("RGBA", "LA"):
                save_kwargs.update(dict(lossless=False, quality=85, method=6))
            else:
                save_kwargs.update(dict(quality=85, method=6))
        else:
            # default JPEG
            fmt = "JPEG"
            if im.mode in ("RGBA", "LA"):
                im = im.convert("RGB")
            save_kwargs.update(dict(quality=85, optimize=True, progressive=True, subsampling="4:2:0"))
        im.save(out_path, fmt, **save_kwargs)

    def save_png_quantized(self, im: Image.Image, out_path: str, strip_meta: bool, max_colors: int):
        src = im
        if src.mode not in ("RGB", "RGBA", "L"):
            src = src.convert("RGBA")
        # try adaptive palette
        try:
            q = src.convert("P", palette=Image.ADAPTIVE, colors=max_colors)
            q.save(out_path, "PNG", optimize=True, compress_level=9)
        except Exception:
            src.save(out_path, "PNG", optimize=True, compress_level=9)

    def bytes_for_quality(self, im: Image.Image, fmt: str, q: int, strip_meta: bool) -> bytes:
        bio = io.BytesIO()
        kwargs = {}
        if fmt == "JPEG":
            tmp = im.convert("RGB") if im.mode not in ("RGB","L") else im
            kwargs = dict(quality=q, optimize=True, progressive=True, subsampling="4:2:0")
            if strip_meta:
                kwargs["exif"] = None
            tmp.save(bio, "JPEG", **kwargs)
        elif fmt == "WEBP":
            tmp = im.convert("RGB") if im.mode not in ("RGB","L") else im
            kwargs = dict(quality=q, method=6)
            tmp.save(bio, "WEBP", **kwargs)
        else:
            raise ValueError("bytes_for_quality only for JPEG/WEBP")
        return bio.getvalue()

    def save_to_target_lossy(self, im: Image.Image, out_path: str, fmt: str, target_bytes: int, under_mode: bool, strip_meta: bool) -> bool:
        # Binary search quality between 95..10
        lo, hi = 10, 95
        best = None
        best_q = None
        for _ in range(12):  # ~12 iterations
            mid = (lo + hi) // 2
            data = self.bytes_for_quality(im, fmt, mid, strip_meta)
            size = len(data)
            if under_mode:
                # prefer <= target, maximize quality
                if size <= target_bytes:
                    best = data; best_q = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            else:
                # prefer as close as possible to target (above/below)
                if size < target_bytes:
                    best = data; best_q = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
        final = best if best is not None else self.bytes_for_quality(im, fmt, max(10, min(95, hi)), strip_meta)
        with open(out_path, "wb") as f:
            f.write(final)
        return len(final) <= target_bytes if under_mode else True

class DropTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(self.DropOnly)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(self.SelectRows)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if not self.model():
            return
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                p = url.toLocalFile()
                if os.path.isdir(p):
                    for root, _, files in os.walk(p):
                        for fn in files:
                            if os.path.splitext(fn)[1].lower() in SUPPORTED_EXT:
                                paths.append(os.path.join(root, fn))
                else:
                    if os.path.splitext(p)[1].lower() in SUPPORTED_EXT:
                        paths.append(p)
        self.parent().add_files(paths)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 680)
        self.items: List[JobItem] = []
        self.model = JobTableModel(self.items)
        self.thread_pool = QThreadPool.globalInstance()
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.on_progress)
        self.signals.row_status.connect(self.on_row_status)
        self.signals.log.connect(self.on_log)
        self.signals.done.connect(self.on_done)

        # --- UI ---
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top controls (file ops)
        file_bar = QHBoxLayout()
        btn_add_files = QPushButton("Add Files")
        btn_add_folder = QPushButton("Add Folder")
        btn_clear = QPushButton("Clear")
        btn_output = QPushButton("Choose Output Folder")
        self.out_dir_label = QLabel("Output: (same as source)")
        btn_add_files.clicked.connect(self.on_add_files)
        btn_add_folder.clicked.connect(self.on_add_folder)
        btn_clear.clicked.connect(self.on_clear)
        btn_output.clicked.connect(self.on_choose_output)
        file_bar.addWidget(btn_add_files)
        file_bar.addWidget(btn_add_folder)
        file_bar.addWidget(btn_clear)
        file_bar.addWidget(btn_output)
        file_bar.addWidget(self.out_dir_label, 1)

        layout.addLayout(file_bar)

        # Options panel
        opt_grid = QGridLayout()
        gb = QGroupBox("Compression Options")
        gb.setLayout(opt_grid)

        # Presets + custom target
        opt_grid.addWidget(QLabel("Preset target:"), 0, 0)
        self.preset = QComboBox()
        self.preset.addItems(["None", "50 KB", "100 KB", "Under 100 KB", "Under 500 KB", "Under 1 MB"])
        self.preset.currentIndexChanged.connect(self.on_preset_change)
        opt_grid.addWidget(self.preset, 0, 1)

        opt_grid.addWidget(QLabel("Custom target (KB):"), 0, 2)
        self.target_kb = QDoubleSpinBox()
        self.target_kb.setRange(0, 999999)
        self.target_kb.setDecimals(1)
        self.target_kb.setValue(0.0)
        opt_grid.addWidget(self.target_kb, 0, 3)

        self.under_mode = QCheckBox("Keep file <= target (Under mode)")
        self.under_mode.setChecked(True)
        opt_grid.addWidget(self.under_mode, 0, 4, 1, 2)

        # Dimensions
        opt_grid.addWidget(QLabel("Max width:"), 1, 0)
        self.max_w = QSpinBox(); self.max_w.setRange(0, 100000); self.max_w.setValue(0)
        opt_grid.addWidget(self.max_w, 1, 1)
        opt_grid.addWidget(QLabel("Max height:"), 1, 2)
        self.max_h = QSpinBox(); self.max_h.setRange(0, 100000); self.max_h.setValue(0)
        opt_grid.addWidget(self.max_h, 1, 3)

        # Format, metadata, grayscale
        opt_grid.addWidget(QLabel("Output format:"), 2, 0)
        self.out_fmt = QComboBox()
        self.out_fmt.addItems(["ORIGINAL", "JPEG", "PNG", "WEBP"])
        opt_grid.addWidget(self.out_fmt, 2, 1)

        self.strip_meta = QCheckBox("Strip metadata/EXIF")
        self.strip_meta.setChecked(True)
        opt_grid.addWidget(self.strip_meta, 2, 2)

        self.grayscale = QCheckBox("Convert to Grayscale")
        opt_grid.addWidget(self.grayscale, 2, 3)

        self.webp_fallback = QCheckBox("Allow WEBP fallback for PNG")
        self.webp_fallback.setChecked(True)
        opt_grid.addWidget(self.webp_fallback, 2, 4, 1, 2)

        # PNG quantization
        opt_grid.addWidget(QLabel("PNG max colors:"), 3, 0)
        self.png_colors = QSpinBox(); self.png_colors.setRange(2, 256); self.png_colors.setValue(256)
        opt_grid.addWidget(self.png_colors, 3, 1)

        # Renaming / overwrite
        opt_grid.addWidget(QLabel("Rename pattern:"), 3, 2)
        self.rename_pattern = QLineEdit("{name}_compressed")
        opt_grid.addWidget(self.rename_pattern, 3, 3)

        self.overwrite = QCheckBox("Overwrite if file exists")
        opt_grid.addWidget(self.overwrite, 3, 4, 1, 2)

        layout.addWidget(gb)

        # Table
        self.table = DropTable(self)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        # Progress + action
        bottom = QHBoxLayout()
        self.progress = QProgressBar(); self.progress.setValue(0)
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.on_start)
        bottom.addWidget(self.progress, 1)
        bottom.addWidget(self.btn_start)
        layout.addLayout(bottom)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        layout.addWidget(self.log)

        # State
        self.output_dir = None

        # Menu (optional)
        help_act = QAction("About", self)
        help_act.triggered.connect(self.on_about)
        self.menuBar().addAction(help_act)

    # --- Event handlers ---
    def on_about(self):
        QMessageBox.information(self, "About", f"{APP_NAME}\nBatch compress & resize images to a target size.\nBuilt with PySide6 + Pillow.")

    def on_add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select images", "", "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif *.gif)")
        self.add_files(paths)

    def on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            paths = []
            for root, _, files in os.walk(folder):
                for fn in files:
                    if os.path.splitext(fn)[1].lower() in SUPPORTED_EXT:
                        paths.append(os.path.join(root, fn))
            self.add_files(paths)

    def on_clear(self):
        self.items.clear()
        self.model.layoutChanged.emit()
        self.progress.setValue(0)
        self.log.clear()

    def on_choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if folder:
            self.output_dir = folder
            self.out_dir_label.setText(f"Output: {folder}")

    def on_start(self):
        if not self.items:
            QMessageBox.warning(self, "No files", "Add some images first.")
            return
        rows = list(range(len(self.items)))
        for r in rows:
            self.model.set_status(r, "Queued")

        opts = dict(
            target_kb = (self.target_kb.value() if self.target_kb.value() > 0 else None),
            under_mode = self.under_mode.isChecked(),
            max_w = self.max_w.value(),
            max_h = self.max_h.value(),
            out_format = self.out_fmt.currentText(),
            strip_meta = self.strip_meta.isChecked(),
            grayscale = self.grayscale.isChecked(),
            allow_webp_fallback = self.webp_fallback.isChecked(),
            rename_pattern = self.rename_pattern.text().strip() or "{name}_compressed",
            out_dir = self.output_dir,
            overwrite = self.overwrite.isChecked(),
            png_max_colors = self.png_colors.value(),
        )

        worker = CompressWorker(rows, self.model, opts, self.signals)
        self.btn_start.setEnabled(False)
        self.thread_pool.start(worker)

    def on_progress(self, pct: int):
        self.progress.setValue(pct)

    def on_row_status(self, row: int, status: str):
        self.model.set_status(row, status)

    def on_log(self, msg: str):
        self.log.append(msg)

    def on_done(self):
        self.btn_start.setEnabled(True)
        QMessageBox.information(self, "Done", "All tasks finished.")

    # utility to add files (used by drag&drop and buttons)
    def add_files(self, paths: List[str]):
        added = 0
        for p in paths:
            if not os.path.isfile(p):
                continue
            ext = os.path.splitext(p)[1].lower()
            if ext not in SUPPORTED_EXT:
                continue
            try:
                size = os.path.getsize(p)
                self.items.append(JobItem(p, size))
                added += 1
            except Exception:
                pass
        if added:
            self.model.layoutChanged.emit()

def main():
    # HiDPI friendly
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "Round"
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
