import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QFrame, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit
from PIL import Image, ImageQt, ImageEnhance, ExifTags
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

class ImageEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bildeditor Pro")
        self.resize(1400, 900)

        self.images = []
        self.current_index = -1
        self.processed_image = None
        self.original_image = None
        self.zoom_factor = 1.0
        self.exif_data = {}

        self.initUI()
        self.apply_dark_mode()

    def initUI(self):
        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        toolbar_layout = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("💾 Speichern")
        self.btn_compare = QtWidgets.QPushButton("🆚 Vorher/Nachher")
        self.btn_prev = QtWidgets.QPushButton("⬅️ Zurück")
        self.btn_next = QtWidgets.QPushButton("➡️ Vor")
        self.btn_reset = QtWidgets.QPushButton("🔄 Zurücksetzen")

        toolbar_layout.addWidget(self.btn_save)
        toolbar_layout.addWidget(self.btn_compare)
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addWidget(self.btn_reset)
        toolbar_layout.addStretch()

        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setFixedWidth(100)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setStyleSheet(
            "color: white; background-color: #444;"
            "padding: 3px; border-radius: 4px; font-weight: bold;"
        )
        toolbar_layout.addWidget(self.zoom_label)

        self.btn_info = QtWidgets.QPushButton("ℹ️ Info")
        self.btn_edit = QtWidgets.QPushButton("✏️ Bearbeiten")
        toolbar_layout.addWidget(self.btn_info)
        toolbar_layout.addWidget(self.btn_edit)

        main_layout.addLayout(toolbar_layout)

        content_layout = QtWidgets.QHBoxLayout()

        gallery_layout = QtWidgets.QVBoxLayout()
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setIconSize(QtCore.QSize(100, 100))
        self.list_widget.setFixedWidth(180)
        self.btn_add = QtWidgets.QPushButton("+ Bilder hinzufügen")
        gallery_layout.addWidget(self.list_widget)
        gallery_layout.addWidget(self.btn_add)
        content_layout.addLayout(gallery_layout)

        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        content_layout.addWidget(self.view, 1)

        controls_layout = QtWidgets.QVBoxLayout()

        self.histogram_frame = QFrame()
        self.histogram_frame.setFixedSize(220, 140)
        self.histogram_frame.setStyleSheet("""
            QFrame {
                border: 1.5px solid #666;
                background-color: #222;
                border-radius: 5px;
            }
        """)
        controls_layout.addWidget(self.histogram_frame)

        self.histogram_label = QLabel(self.histogram_frame)
        self.histogram_label.setGeometry(5, 5, 210, 130)
        self.histogram_label.setStyleSheet("background-color: transparent;")

        self.sliders_widget = QtWidgets.QWidget()
        sliders_layout = QVBoxLayout(self.sliders_widget)
        sliders_layout.setContentsMargins(0, 0, 0, 0)

        self.brightness_slider = self.create_slider("🌞 Helligkeit", sliders_layout)
        self.contrast_slider = self.create_slider("🌓 Kontrast", sliders_layout)
        self.saturation_slider = self.create_slider("🎨 Sättigung", sliders_layout)
        self.sharpness_slider = self.create_slider("🔎 Schärfe", sliders_layout)
        self.temperature_slider = self.create_slider("🌡️ Farbtemperatur", sliders_layout)
        self.tint_slider = self.create_slider("🎨 Farbton", sliders_layout)
        self.shadows_slider = self.create_slider("🌑 Tiefen", sliders_layout)
        self.highlights_slider = self.create_slider("🌟 Lichter", sliders_layout)
        self.blackpoint_slider = self.create_slider("⚫ Schwarzpunkt", sliders_layout)
        self.whitepoint_slider = self.create_slider("⚪ Weißpunkt", sliders_layout)
        self.noise_reduction_slider = self.create_slider("🔇 Rauschreduzierung", sliders_layout)

        controls_layout.addWidget(self.sliders_widget)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            background-color: #222;
            color: white;
            border: 1.5px solid #666;
            border-radius: 5px;
            font-size: 14px;
            font-family: Consolas, monospace;
        """)
        self.info_text.setFixedHeight(260)
        self.info_text.setVisible(False)
        controls_layout.addWidget(self.info_text)

        controls_layout.addStretch()
        content_layout.addLayout(controls_layout)

        main_layout.addLayout(content_layout)
        self.setCentralWidget(central_widget)

        self.connect_signals()

        self.view.viewport().installEventFilter(self)

        self.sliders_widget.setVisible(True)
        self.info_text.setVisible(False)

    def create_slider(self, label_text, layout):
        label = QtWidgets.QLabel(f"{label_text}: 0%")
        slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setFixedHeight(30)
        layout.addWidget(label)
        layout.addWidget(slider)

        if "Helligkeit" in label_text:
            self.brightness_label = label
        elif "Kontrast" in label_text:
            self.contrast_label = label
        elif "Sättigung" in label_text:
            self.saturation_label = label
        elif "Schärfe" in label_text:
            self.sharpness_label = label
        elif "Farbtemperatur" in label_text:
            self.temperature_label = label
        elif "Farbton" in label_text:
            self.tint_label = label
        elif "Tiefen" in label_text:
            self.shadows_label = label
        elif "Lichter" in label_text:
            self.highlights_label = label
        elif "Schwarzpunkt" in label_text:
            self.blackpoint_label = label
        elif "Weißpunkt" in label_text:
            self.whitepoint_label = label
        elif "Rauschreduzierung" in label_text:
            self.noise_reduction_label = label

        return slider

    def apply_dark_mode(self):
        dark_style = """
            QWidget {
                background-color: #2e2e2e;
                color: #ddd;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #444;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #bbb;
                border: 1px solid #666;
                width: 18px;
                margin: -2px 0;
                border-radius: 8px;
            }
            QListWidget {
                background-color: #333;
                border: 1px solid #555;
            }
        """
        self.setStyleSheet(dark_style)

    def connect_signals(self):
        self.btn_add.clicked.connect(self.open_images)
        self.list_widget.currentRowChanged.connect(self.set_current_image)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_reset.clicked.connect(self.reset_image)
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_next.clicked.connect(self.next_image)
        self.btn_compare.pressed.connect(self.show_original)
        self.btn_compare.released.connect(self.show_processed)

        self.brightness_slider.valueChanged.connect(self.update_image)
        self.contrast_slider.valueChanged.connect(self.update_image)
        self.saturation_slider.valueChanged.connect(self.update_image)
        self.sharpness_slider.valueChanged.connect(self.update_image)
        self.temperature_slider.valueChanged.connect(self.update_image)
        self.tint_slider.valueChanged.connect(self.update_image)
        self.shadows_slider.valueChanged.connect(self.update_image)
        self.highlights_slider.valueChanged.connect(self.update_image)
        self.blackpoint_slider.valueChanged.connect(self.update_image)
        self.whitepoint_slider.valueChanged.connect(self.update_image)
        self.noise_reduction_slider.valueChanged.connect(self.update_image)

        self.btn_info.clicked.connect(self.show_info)
        self.btn_edit.clicked.connect(self.toggle_editing)

    def eventFilter(self, source, event):
        if source is self.view.viewport():
            if event.type() == QtCore.QEvent.Type.Wheel:
                modifiers = QtWidgets.QApplication.keyboardModifiers()
                if modifiers == Qt.KeyboardModifier.ControlModifier:
                    delta = event.angleDelta().y()
                    if delta > 0:
                        self.zoom_factor *= 1.1
                    else:
                        self.zoom_factor /= 1.1
                    self.zoom_factor = max(0.1, min(self.zoom_factor, 10))
                    self.update_view_zoom()
                    return True
        return super().eventFilter(source, event)

    def update_view_zoom(self):
        if not hasattr(self, "pixmap_item") or self.pixmap_item is None:
            return
        t = QtGui.QTransform()
        t.scale(self.zoom_factor, self.zoom_factor)
        self.view.setTransform(t)
        self.update_zoom_label()

    def update_zoom_label(self):
        self.zoom_label.setText(f"Zoom: {self.zoom_factor*100:.0f}%")

    def open_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Bilder öffnen", "", "Bilder (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return
        for file in files:
            try:
                img = Image.open(file).convert("RGBA")
                self.images.append((img, file))
                icon = QtGui.QIcon(QtGui.QPixmap(file).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                item = QListWidgetItem(icon, os.path.basename(file))
                self.list_widget.addItem(item)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Fehler", f"Konnte Bild nicht laden:\n{file}\n{e}")

        if self.current_index == -1 and self.images:
            self.list_widget.setCurrentRow(0)

    def set_current_image(self, index):
        if index < 0 or index >= len(self.images):
            return
        self.current_index = index
        img, file = self.images[index]
        self.original_image = img.copy()
        self.processed_image = self.original_image.copy()
        self.reset_sliders()
        self.update_image()
        self.extract_exif()
        self.update_info_text()
        self.fit_image_to_view()

    def reset_sliders(self):
        self.brightness_slider.blockSignals(True)
        self.contrast_slider.blockSignals(True)
        self.saturation_slider.blockSignals(True)
        self.sharpness_slider.blockSignals(True)
        self.temperature_slider.blockSignals(True)
        self.tint_slider.blockSignals(True)
        self.shadows_slider.blockSignals(True)
        self.highlights_slider.blockSignals(True)
        self.blackpoint_slider.blockSignals(True)
        self.whitepoint_slider.blockSignals(True)
        self.noise_reduction_slider.blockSignals(True)

        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.sharpness_slider.setValue(0)
        self.temperature_slider.setValue(0)
        self.tint_slider.setValue(0)
        self.shadows_slider.setValue(0)
        self.highlights_slider.setValue(0)
        self.blackpoint_slider.setValue(0)
        self.whitepoint_slider.setValue(0)
        self.noise_reduction_slider.setValue(0)

        self.brightness_slider.blockSignals(False)
        self.contrast_slider.blockSignals(False)
        self.saturation_slider.blockSignals(False)
        self.sharpness_slider.blockSignals(False)
        self.temperature_slider.blockSignals(False)
        self.tint_slider.blockSignals(False)
        self.shadows_slider.blockSignals(False)
        self.highlights_slider.blockSignals(False)
        self.blackpoint_slider.blockSignals(False)
        self.whitepoint_slider.blockSignals(False)
        self.noise_reduction_slider.blockSignals(False)

        self.update_slider_labels()

    def update_slider_labels(self):
        self.brightness_label.setText(f"🌞 Helligkeit: {self.brightness_slider.value()}%")
        self.contrast_label.setText(f"🌓 Kontrast: {self.contrast_slider.value()}%")
        self.saturation_label.setText(f"🎨 Sättigung: {self.saturation_slider.value()}%")
        self.sharpness_label.setText(f"🔎 Schärfe: {self.sharpness_slider.value()}%")
        self.temperature_label.setText(f"🌡️ Farbtemperatur: {self.temperature_slider.value()}%")
        self.tint_label.setText(f"🎨 Farbton: {self.tint_slider.value()}%")
        self.shadows_label.setText(f"🌑 Tiefen: {self.shadows_slider.value()}%")
        self.highlights_label.setText(f"🌟 Lichter: {self.highlights_slider.value()}%")
        self.blackpoint_label.setText(f"⚫ Schwarzpunkt: {self.blackpoint_slider.value()}%")
        self.whitepoint_label.setText(f"⚪ Weißpunkt: {self.whitepoint_slider.value()}%")
        self.noise_reduction_label.setText(f"🔇 Rauschreduzierung: {self.noise_reduction_slider.value()}%")

    def update_image(self):
        if self.original_image is None:
            return
        self.update_slider_labels()

        img = self.original_image.copy()

        brightness_factor = 1 + self.brightness_slider.value() / 100
        contrast_factor = 1 + self.contrast_slider.value() / 100
        saturation_factor = 1 + self.saturation_slider.value() / 100
        sharpness_factor = 1 + self.sharpness_slider.value() / 100

        # Farbtemperatur und Farbton
        temperature_adjustment = self.temperature_slider.value() / 100
        tint_adjustment = self.tint_slider.value() / 100

        # Tiefen und Lichter
        shadows_adjustment = self.shadows_slider.value() / 100
        highlights_adjustment = self.highlights_slider.value() / 100

        # Schwarzpunkt und Weißpunkt
        blackpoint_adjustment = self.blackpoint_slider.value() / 100
        whitepoint_adjustment = self.whitepoint_slider.value() / 100

        # Rauschreduzierung
        noise_reduction_factor = self.noise_reduction_slider.value() / 100

        # Helligkeit, Kontrast, Sättigung und Schärfe
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(saturation_factor)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness_factor)

        # Hier können die Anpassungen für Farbtemperatur, Farbton, Tiefen, Lichter, Schwarzpunkt, Weißpunkt und Rauschreduzierung implementiert werden
        # Diese Anpassungen sind nicht trivial und erfordern möglicherweise zusätzliche Bibliotheken oder Algorithmen

        self.processed_image = img
        self.show_image(img)
        self.update_histogram(img)

    def show_image(self, pil_img):
        qim = ImageQt.ImageQt(pil_img)
        pix = QtGui.QPixmap.fromImage(qim)
        self.scene.clear()
        self.pixmap_item = self.scene.addPixmap(pix)
        self.fit_image_to_view()  # Bild an View anpassen

    def fit_image_to_view(self):
        if not hasattr(self, "pixmap_item") or self.pixmap_item is None:
            return
        view_rect = self.view.viewport().rect()
        pixmap_rect = self.pixmap_item.pixmap().rect()

        if pixmap_rect.isNull() or view_rect.isNull():
            return

        scale_x = view_rect.width() / pixmap_rect.width()
        scale_y = view_rect.height() / pixmap_rect.height()
        self.zoom_factor = min(scale_x, scale_y)
        self.update_view_zoom()

    def save_image(self):
        if self.processed_image is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Bild speichern", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if not file_path:
            return
        try:
            self.processed_image.save(file_path)
            QtWidgets.QMessageBox.information(self, "Erfolg", "Bild wurde gespeichert.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def reset_image(self):
        if self.original_image is None:
            return
        self.processed_image = self.original_image.copy()
        self.reset_sliders()
        self.show_image(self.processed_image)
        self.update_histogram(self.processed_image)

    def prev_image(self):
        if not self.images:
            return
        idx = self.current_index - 1
        if idx < 0:
            idx = len(self.images) - 1
        self.list_widget.setCurrentRow(idx)

    def next_image(self):
        if not self.images:
            return
        idx = (self.current_index + 1) % len(self.images)
        self.list_widget.setCurrentRow(idx)

    def show_original(self):
        if self.original_image is not None:
            self.show_image(self.original_image)
    
    def show_processed(self):
        if self.processed_image is not None:
            self.show_image(self.processed_image)

    def update_histogram(self, pil_img):
        data = np.array(pil_img.convert("RGB"))
        r = data[:, :, 0].flatten()
        g = data[:, :, 1].flatten()
        b = data[:, :, 2].flatten()

        plt.figure(figsize=(2.2, 1.3), dpi=100)
        plt.clf()
        plt.axis('off')
        plt.hist(r, bins=256, color='red', alpha=0.5, range=(0,255))
        plt.hist(g, bins=256, color='green', alpha=0.5, range=(0,255))
        plt.hist(b, bins=256, color='blue', alpha=0.5, range=(0,255))

        buf = BytesIO()
        plt.savefig(buf, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()
        buf.seek(0)
        hist_img = Image.open(buf)
        qim = ImageQt.ImageQt(hist_img)
        pix = QtGui.QPixmap.fromImage(qim)
        self.histogram_label.setPixmap(pix)
        buf.close()

    def extract_exif(self):
        self.exif_data = {}
        if self.current_index < 0 or self.current_index >= len(self.images):
            return
        img, _ = self.images[self.current_index]
        try:
            raw_exif = img._getexif()
            if not raw_exif:
                self.exif_data = {}
                return

            exif = {}
            for tag, val in raw_exif.items():
                tagname = ExifTags.TAGS.get(tag, tag)
                exif[tagname] = val

            lens = exif.get("LensModel")
            self.exif_data = exif
        except Exception as e:
            print(f"EXIF Fehler: {e}")
            self.exif_data = {}

    def update_info_text(self):
        if not self.exif_data:
            self.info_text.setText("Keine EXIF-Daten vorhanden.")
            return

        def format_ratio(val):
            if isinstance(val, tuple) and len(val) == 2 and val[1] != 0:
                return f"{val[0]/val[1]:.4g}"
            return str(val)

        info_lines = []
        if "Make" in self.exif_data or "Model" in self.exif_data:
            info_lines.append(f"Kamera: {self.exif_data.get('Make', '')} {self.exif_data.get('Model', '')}".strip())

        if "LensModel" in self.exif_data:
            info_lines.append(f"Objektiv: {self.exif_data['LensModel']}")

        if "FocalLength" in self.exif_data:
            info_lines.append(f"Brennweite: {format_ratio(self.exif_data['FocalLength'])} mm")

        if "ExposureTime" in self.exif_data:
            info_lines.append(f"Verschlusszeit: {format_ratio(self.exif_data['ExposureTime'])} s")

        if "FNumber" in self.exif_data:
            info_lines.append(f"Blende: f/{format_ratio(self.exif_data['FNumber'])}")

        if "ISOSpeedRatings" in self.exif_data:
            iso = self.exif_data["ISOSpeedRatings"]
            info_lines.append(f"ISO: {iso if not isinstance(iso, (list, tuple)) else iso[0]}")

        white_balance_map = {
            0: "Automatisch",
            1: "Manuell",
            2: "Tageslicht",
            3: "Bewölkt",
            4: "Kunstlicht",
            5: "Fluoreszierend"
        }
        if "WhiteBalance" in self.exif_data:
            wb = self.exif_data["WhiteBalance"]
            info_lines.append(f"Weißabgleich: {white_balance_map.get(wb, f'Unbekannt ({wb})')}")

        if "Artist" in self.exif_data:
            info_lines.append(f"Urheber: {self.exif_data['Artist']}")

        if "Copyright" in self.exif_data:
            info_lines.append(f"Copyright: {self.exif_data['Copyright']}")

        self.info_text.setText("\n".join(info_lines) if info_lines else "Keine relevanten EXIF-Daten gefunden.")

    def show_info(self):
        self.sliders_widget.setVisible(False)
        self.info_text.setVisible(True)
        self.update_info_text()

    def toggle_editing(self):
        if self.sliders_widget.isVisible():
            self.sliders_widget.setVisible(False)
            self.info_text.setVisible(True)
        else:
            self.sliders_widget.setVisible(True)
            self.info_text.setVisible(False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

       