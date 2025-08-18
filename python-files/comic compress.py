import sys
import os
import zipfile
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QComboBox, QSpinBox, QCheckBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PIL import Image, UnidentifiedImageError

# -------- Worker Thread pour compression --------
class CompressorThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, files, max_length, quality, keep_color, engine):
        super().__init__()
        self.files = files
        self.max_length = max_length
        self.quality = quality
        self.keep_color = keep_color
        self.engine = engine

    def run(self):
        # Compter toutes les images pour barre précise
        total_images = 0
        archives_images = []

        # 1️⃣ Extraire une fois et collecter images valides
        temp_dirs = []
        for file_path in self.files:
            tmpdir = tempfile.TemporaryDirectory()
            temp_dirs.append(tmpdir)  # garder la référence pour ne pas supprimer
            tmpdir_path = Path(tmpdir.name)
            ext = file_path.suffix.lower()
            if ext in ['.cbz', '.zip']:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir_path)
                images = [p for p in tmpdir_path.rglob("*")
                          if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
                          and "__MACOSX" not in str(p)
                          and not p.name.startswith("._")]
                total_images += len(images)
                archives_images.append((file_path, images, tmpdir_path))
            else:
                self.log.emit(f"Unsupported format: {file_path.name}")

        if total_images == 0:
            self.log.emit("No images found!")
            return

        processed_images = 0

        # 2️⃣ Traiter chaque image
        for file_idx, (file_path, images, tmpdir_path) in enumerate(archives_images, 1):
            if not images:
                continue
            for img_idx, img_path in enumerate(images, 1):
                self.log.emit(f"File {file_idx}/{len(self.files)}: {file_path.name} - Page {img_idx}/{len(images)}")
                try:
                    img = Image.open(img_path)
                except UnidentifiedImageError:
                    continue
                if not self.keep_color:
                    img = img.convert("L")
                img.thumbnail((self.max_length, self.max_length))
                if self.engine == "MozJPEG":
                    tmp_file = img_path.with_suffix(".jpg")
                    img.save(tmp_file)
                    os.system(f"cjpeg -quality {self.quality} -outfile {img_path} {tmp_file}")
                    tmp_file.unlink()
                else:
                    img.save(img_path, quality=self.quality)

                processed_images += 1
                percent = int(processed_images / total_images * 100)
                self.progress.emit(percent)

            # 3️⃣ Recréer archive compressée
            compressed_name = file_path.with_name(file_path.stem + "_compressed" + file_path.suffix)
            with zipfile.ZipFile(compressed_name, 'w') as zip_out:
                for file in tmpdir_path.rglob("*"):
                    if file.is_file():
                        zip_out.write(file, file.relative_to(tmpdir_path))

        self.log.emit("All done!")

# -------- GUI --------
class CompressorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comic Archive Compressor")
        self.resize(600, 500)
        layout = QVBoxLayout()

        self.label = QLabel("Select one or more comic archives (CBZ/CB7/CBR/ZIP):")
        layout.addWidget(self.label)

        self.select_btn = QPushButton("Select Files")
        self.select_btn.clicked.connect(self.select_files)
        layout.addWidget(self.select_btn)

        self.engine_label = QLabel("Compression Engine:")
        layout.addWidget(self.engine_label)
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["ImageMagick", "MozJPEG"])
        layout.addWidget(self.engine_combo)

        self.max_length_label = QLabel("Max Side Length (px):")
        layout.addWidget(self.max_length_label)
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(100, 10000)
        self.max_length_spin.setValue(1920)
        layout.addWidget(self.max_length_spin)

        self.quality_label = QLabel("JPEG Quality (%):")
        layout.addWidget(self.quality_label)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(10, 100)
        self.quality_spin.setValue(85)
        layout.addWidget(self.quality_spin)

        self.color_checkbox = QCheckBox("Keep Color")
        self.color_checkbox.setChecked(True)
        layout.addWidget(self.color_checkbox)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.log_label = QTextEdit()
        self.log_label.setReadOnly(True)
        layout.addWidget(self.log_label)

        self.start_btn = QPushButton("Start Compression")
        self.start_btn.clicked.connect(self.start_compression)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
        self.files = []

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Comic Archives", "", "Comics (*.cbz *.cb7 *.cbr *.zip)")
        self.files = [Path(f) for f in files]
        self.label.setText(f"Selected {len(self.files)} files")

    def start_compression(self):
        if not self.files:
            self.log_label.append("No files selected!")
            return
        self.thread = CompressorThread(
            self.files,
            self.max_length_spin.value(),
            self.quality_spin.value(),
            self.color_checkbox.isChecked(),
            self.engine_combo.currentText()
        )
        self.thread.progress.connect(self.progress.setValue)
        self.thread.log.connect(lambda msg: self.log_label.append(msg))
        self.thread.start()

# -------- Run App --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompressorGUI()
    window.show()
    sys.exit(app.exec())
