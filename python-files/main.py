import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, 
    QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout, QColorDialog, QFileDialog,
    QDialog, QSlider, QScrollArea, QFontDialog, QMessageBox, QSpinBox, QFormLayout,
    QGroupBox, QDialogButtonBox
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPixmap, QColor, QFont, QImage, QPainter, QPainterPath, QBrush, QPen, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QRectF
import json
from PIL import Image, ImageQt, ImageFont, ImageDraw, ImageOps, ImageEnhance

class PhotoCorrectionDialog(QDialog):
    image_corrected = pyqtSignal(Image.Image)

    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photo Correction")
        self.original_image = image
        self.current_image = image.copy()

        layout = QVBoxLayout(self)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 250)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_preview()

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.apply_corrections)

        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.apply_corrections)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept_changes)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        controls_layout = QGridLayout()
        controls_layout.addWidget(self.preview_label, 0, 0, 1, 2)
        controls_layout.addWidget(QLabel("Brightness"), 1, 0)
        controls_layout.addWidget(self.brightness_slider, 1, 1)
        controls_layout.addWidget(QLabel("Contrast"), 2, 0)
        controls_layout.addWidget(self.contrast_slider, 2, 1)
        layout.addLayout(controls_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def apply_corrections(self):
        temp_image = self.original_image.copy()
        brightness = self.brightness_slider.value() / 100.0
        enhancer = ImageEnhance.Brightness(temp_image)
        temp_image = enhancer.enhance(brightness)
        contrast = self.contrast_slider.value() / 100.0
        enhancer = ImageEnhance.Contrast(temp_image)
        self.current_image = enhancer.enhance(contrast)
        self.update_preview()

    def update_preview(self):
        qimage = ImageQt.ImageQt(self.current_image)
        pixmap = QPixmap.fromImage(qimage)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def accept_changes(self):
        self.image_corrected.emit(self.current_image)
        self.accept()


class CroppableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_rect = QRect()
        self.origin = QPoint()
        self.is_selecting = False
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap():
            self.is_selecting = True
            self.origin = event.pos()
            self.selection_rect = QRect(self.origin, QSize())
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_rect = QRect(self.origin, event.pos()).normalized()
            self.update() # Trigger a repaint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Keep selection visible after mouse release
            self.is_selecting = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.selection_rect.isNull():
            painter = QPainter(self)
            overlay_color = QColor(0, 0, 0, 120)
            path = QPainterPath()
            path.addRect(QRectF(self.rect()))
            path.addRect(QRectF(self.selection_rect))
            path.setFillRule(Qt.FillRule.OddEvenFill)
            painter.fillPath(path, QBrush(overlay_color))

            pen = QPen(QColor("#FFFFFF"), 1, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)

    def get_selection(self):
        return self.selection_rect if not self.selection_rect.isNull() else None

    def clear_selection(self):
        self.selection_rect = QRect()
        self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path:
                self.parent().open_image(file_path)
            event.acceptProposedAction()


class PhotoSoft(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoSoft - The Best Photo Print Software")
        self.setGeometry(100, 100, 1200, 800)
        self.pil_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.font1 = QFont("Arial", 24)
        self.font2 = QFont("Arial", 24)

        self.custom_layout_settings = None
        self.border_settings = {'color': QColor('#000000'), 'thickness': 0}

        self.page_settings = {
            'paper_size': 'A4',
            'margin_top': 50,
            'margin_right': 50,
            'margin_bottom': 50,
            'margin_left': 50,
            'alignment': 'center'
        }
        self.grid_settings = {
            'spacing_x': 20,
            'spacing_y': 20
        }

        self._create_menu_bar()
        self._create_ui()
        self.load_settings()
        self.setAcceptDrops(True)

    def _create_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left side: Image Preview
        self.image_preview = CroppableLabel("Drag & drop an image, or click 'Open Image'")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumSize(600, 600)
        main_layout.addWidget(self.image_preview, 2)

        # Right side: Controls Area
        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        main_layout.addWidget(controls_scroll, 1)

        controls_widget = QWidget()
        controls_scroll.setWidget(controls_widget)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Image Editing Group ---
        editing_group = QGroupBox("Image Editing")
        editing_layout = QVBoxLayout(editing_group)
        controls_layout.addWidget(editing_group)

        self.open_btn = QPushButton("Open Image")
        self.open_btn.clicked.connect(self.open_image)
        editing_layout.addWidget(self.open_btn)

        self.crop_btn = QPushButton("Crop Selection")
        self.crop_btn.clicked.connect(self.crop_image)
        editing_layout.addWidget(self.crop_btn)

        self.correction_btn = QPushButton("Brightness/Contrast")
        self.correction_btn.clicked.connect(self.open_photo_correction)
        editing_layout.addWidget(self.correction_btn)

        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        editing_layout.addWidget(filter_group)

        self.grayscale_btn = QPushButton("Grayscale")
        self.grayscale_btn.clicked.connect(lambda: self.apply_filter('grayscale'))
        filter_layout.addWidget(self.grayscale_btn)

        self.sepia_btn = QPushButton("Sepia")
        self.sepia_btn.clicked.connect(lambda: self.apply_filter('sepia'))
        filter_layout.addWidget(self.sepia_btn)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_last_action)
        self.undo_btn.setEnabled(False)
        editing_layout.addWidget(self.undo_btn)

        # --- Text Overlay Group ---
        text_group = QGroupBox("Text Overlay")
        text_layout = QFormLayout(text_group)
        controls_layout.addWidget(text_group)

        self.text1_input = QLineEdit()
        self.font1_btn = QPushButton("Font...")
        self.font1_btn.clicked.connect(lambda: self.open_font_dialog(1))
        text1_row = QHBoxLayout()
        text1_row.addWidget(self.text1_input)
        text1_row.addWidget(self.font1_btn)
        text_layout.addRow("Text 1:", text1_row)

        self.text2_input = QLineEdit()
        self.font2_btn = QPushButton("Font...")
        self.font2_btn.clicked.connect(lambda: self.open_font_dialog(2))
        text2_row = QHBoxLayout()
        text2_row.addWidget(self.text2_input)
        text2_row.addWidget(self.font2_btn)
        text_layout.addRow("Text 2:", text2_row)

        self.apply_text_btn = QPushButton("Apply Text")
        self.apply_text_btn.clicked.connect(self.apply_text_overlay)
        text_layout.addRow(self.apply_text_btn)

        # --- Print Layout Group ---
        layout_group = QGroupBox("Print Layout")
        layout_form = QFormLayout(layout_group)
        controls_layout.addWidget(layout_group)

        self.photo_layout_combo = QComboBox()
        self.photo_layout_combo.addItems(["8 Passport Photo", "16 Passport Photo", "Stamp Size", "1x2 Custom", "Custom Layout..."])
        self.photo_layout_combo.currentIndexChanged.connect(self.on_layout_change)
        layout_form.addRow("Layout Preset:", self.photo_layout_combo)

        self.border_btn = QPushButton("Set Border...")
        self.border_btn.clicked.connect(self.open_border_settings)
        layout_form.addRow("Photo Border:", self.border_btn)



        # --- Grid Preview and Actions ---
        self.grid_preview = QLabel("Photo grid will appear here.")
        self.grid_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_preview.setStyleSheet("border: 1px solid #ccc;")
        controls_layout.addWidget(self.grid_preview, 1) # Give it stretch factor

        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self.print_grid)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_grid)
        bottom_btn_layout.addWidget(self.print_btn)
        bottom_btn_layout.addWidget(self.save_btn)
        controls_layout.addLayout(bottom_btn_layout)

        controls_layout.addStretch()

    def open_image(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        
        if file_path:
            try:
                new_image = Image.open(file_path).convert("RGBA")
                self.pil_image = new_image
                self.add_to_undo_stack(is_initial=True)
                self.update_ui_from_image(self.pil_image)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open image file: {e}")

    def add_to_undo_stack(self, is_initial=False):
        if self.pil_image:
            if is_initial:
                self.undo_stack.clear()
                self.redo_stack.clear()
            else:
                self.undo_stack.append(self.pil_image.copy())
                self.redo_stack.clear()
            self.undo_btn.setEnabled(bool(self.undo_stack))

    def undo_last_action(self):
        if self.undo_stack:
            self.redo_stack.append(self.pil_image.copy())
            self.pil_image = self.undo_stack.pop()
            self.update_ui_from_image(self.pil_image)
            self.undo_btn.setEnabled(bool(self.undo_stack))

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.generate_grid_preview()

    def open_photo_correction(self):
        if not self.pil_image: return
        dialog = PhotoCorrectionDialog(self.pil_image, self)
        dialog.image_corrected.connect(self.handle_image_correction)
        dialog.exec()

    def handle_image_correction(self, corrected_image):
        self.add_to_undo_stack()
        self.update_ui_from_image(corrected_image)

    def apply_text_overlay(self):
        if not self.pil_image: return
        text1 = self.text1_input.text()
        text2 = self.text2_input.text()

        if not text1 and not text2: return

        self.add_to_undo_stack()
        image_with_text = self.pil_image.copy()
        draw = ImageDraw.Draw(image_with_text)

        if text1:
            try:
                # This assumes a standard Windows font path. May need adjustment for other OS.
                pil_font1 = ImageFont.truetype(f"C:/Windows/Fonts/{self.font1.family()}.ttf", self.font1.pointSize())
                draw.text((10, 10), text1, font=pil_font1, fill=(0, 0, 0, 255))
            except IOError:
                print(f"Font {self.font1.family()} not found. Using default.")
                draw.text((10, 10), text1, fill=(0, 0, 0, 255))
        
        if text2:
            try:
                pil_font2 = ImageFont.truetype(f"C:/Windows/Fonts/{self.font2.family()}.ttf", self.font2.pointSize())
                # Position at bottom left
                text_width, text_height = pil_font2.getbbox(text2)[2:]
                x = 10
                y = image_with_text.height - text_height - 10
                draw.text((x, y), text2, font=pil_font2, fill=(0, 0, 0, 255))
            except IOError:
                print(f"Font {self.font2.family()} not found. Using default.")
                text_width, text_height = draw.textbbox((0,0), text2)[2:]
                x = 10
                y = image_with_text.height - text_height - 10
                draw.text((x, y), text2, fill=(0, 0, 0, 255))

        self.update_ui_from_image(image_with_text)

    def apply_filter(self, filter_type):
        if not self.pil_image: return

        self.add_to_undo_stack()
        original_image = self.pil_image.copy()
        filtered_image = None

        if filter_type == 'grayscale':
            # Convert to grayscale and then back to RGBA to keep alpha channel
            filtered_image = original_image.convert("L").convert("RGBA")
        
        elif filter_type == 'sepia':
            # Create a sepia-toned image
            sepia_image = original_image.copy()
            if sepia_image.mode != 'RGB':
                 sepia_image = sepia_image.convert('RGB')
            
            width, height = sepia_image.size
            pixels = sepia_image.load()

            for py in range(height):
                for px in range(width):
                    r, g, b = sepia_image.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
            
            # If original had alpha, re-apply it
            if 'A' in original_image.mode:
                alpha = original_image.split()[3]
                sepia_image.putalpha(alpha)
            filtered_image = sepia_image

        if filtered_image:
            self.update_ui_from_image(filtered_image)

    def update_ui_from_image(self, pil_img):
        self.pil_image = pil_img
        qimage = ImageQt.ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qimage)
        self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.generate_grid_preview()

    def crop_image(self):
        if not self.pil_image: return

        selection = self.image_preview.get_selection()
        if not selection or selection.width() <= 0 or selection.height() <= 0:
            self.image_preview.clear_selection()
            return

        label_size = self.image_preview.size()
        img_size = self.pil_image.size
        pixmap = self.image_preview.pixmap()
        if not pixmap: return

        scaled_pixmap_size = pixmap.size()
        scaled_pixmap_size.scale(label_size, Qt.AspectRatioMode.KeepAspectRatio)

        if scaled_pixmap_size.width() <= 0 or scaled_pixmap_size.height() <= 0: return

        offset_x = (label_size.width() - scaled_pixmap_size.width()) / 2
        offset_y = (label_size.height() - scaled_pixmap_size.height()) / 2

        pixmap_x1 = max(0, selection.left() - offset_x)
        pixmap_y1 = max(0, selection.top() - offset_y)

        x_scale = img_size[0] / scaled_pixmap_size.width()
        y_scale = img_size[1] / scaled_pixmap_size.height()

        img_crop_x1 = int(pixmap_x1 * x_scale)
        img_crop_y1 = int(pixmap_y1 * y_scale)
        img_crop_x2 = int((selection.width() + pixmap_x1) * x_scale)
        img_crop_y2 = int((selection.height() + pixmap_y1) * y_scale)

        img_crop_x1 = max(0, img_crop_x1)
        img_crop_y1 = max(0, img_crop_y1)
        img_crop_x2 = min(img_size[0], img_crop_x2)
        img_crop_y2 = min(img_size[1], img_crop_y2)

        if img_crop_x1 >= img_crop_x2 or img_crop_y1 >= img_crop_y2:
            self.image_preview.clear_selection()
            return

        crop_box = (img_crop_x1, img_crop_y1, img_crop_x2, img_crop_y2)
        self.add_to_undo_stack()
        cropped_image = self.pil_image.crop(crop_box)
        self.image_preview.clear_selection()
        self.update_ui_from_image(cropped_image)

    def generate_grid_preview(self):
        if not self.pil_image: return
        layout_text = self.photo_layout_combo.currentText()
        if not layout_text: return

        photo_count = 0
        paper_sizes = {
            'A4': (2480, 3508),
            'Letter': (2550, 3300),
            'Legal': (2550, 4200)
        }
        paper_width_px, paper_height_px = paper_sizes.get(self.page_settings['paper_size'], (2480, 3508))
        # Create a new blank image for the grid with a white background
        self.final_grid_image = Image.new('RGBA', (paper_width_px, paper_height_px), (255, 255, 255, 255))

        margin_top = self.page_settings['margin_top']
        margin_bottom = self.page_settings['margin_bottom']
        margin_left = self.page_settings['margin_left']
        margin_right = self.page_settings['margin_right']
        drawable_width = paper_width_px - (margin_left + margin_right)
        drawable_height = paper_height_px - (margin_top + margin_bottom)

        photo_size_map = {
            "8 Passport Photo": (350, 450, 2, 4),
            "16 Passport Photo": (350, 450, 4, 4),
            "Stamp Size": (200, 250, 5, 5),
            "1x2 Custom": (350, 450, 1, 2)
        }

        if layout_text == "Custom Layout...":
            if not self.custom_layout_settings: return
            rows = self.custom_layout_settings['rows']
            cols = self.custom_layout_settings['cols']
            photo_count = self.custom_layout_settings.get('count', rows * cols)
            spacing_x = self.grid_settings['spacing_x']
            spacing_y = self.grid_settings['spacing_y']

            # Calculate best fit photo size
            if cols <= 0 or rows <= 0: return
            photo_aspect_ratio = self.pil_image.width / self.pil_image.height
            
            cell_width = (drawable_width - (cols - 1) * spacing_x) / cols
            cell_height = (drawable_height - (rows - 1) * spacing_y) / rows

            if cell_width <= 0 or cell_height <= 0: return

            cell_aspect_ratio = cell_width / cell_height

            if photo_aspect_ratio > cell_aspect_ratio:
                p_w = int(cell_width)
                p_h = int(p_w / photo_aspect_ratio)
            else:
                p_h = int(cell_height)
                p_w = int(p_h * photo_aspect_ratio)

            if p_w <= 0 or p_h <= 0: return
            photo = self.pil_image.resize((p_w, p_h))

        elif layout_text in photo_size_map:
            p_w, p_h, cols, rows = photo_size_map[layout_text]
            photo_count = rows * cols
            photo = self.pil_image.resize((p_w, p_h))
        else:
            return

        # Apply border if specified
        border_thickness = self.border_settings['thickness']
        if border_thickness > 0:
            border_color = self.border_settings['color'].name()
            # Use ImageOps.expand for a reliable border
            photo = ImageOps.expand(photo, border=border_thickness, fill=border_color)
            p_w, p_h = photo.size

        total_photos_width = cols * p_w
        total_photos_height = rows * p_h
        
        spacing_x = self.grid_settings['spacing_x']
        spacing_y = self.grid_settings['spacing_y']

        block_width = (cols * p_w) + (max(0, cols - 1) * spacing_x)
        block_height = (rows * p_h) + (max(0, rows - 1) * spacing_y)

        if self.page_settings.get('alignment', 'center') == 'top_left':
            x_offset = margin_left
            y_offset = margin_top
        else: # Default to center
            x_offset = margin_left + (drawable_width - block_width) // 2
            y_offset = margin_top + (drawable_height - block_height) // 2

        photo_index = 0
        for r in range(rows):
            for c in range(cols):
                if photo_index >= photo_count:
                    break
                x = x_offset + c * (p_w + spacing_x)
                y = y_offset + r * (p_h + spacing_y)
                self.final_grid_image.paste(photo, (x, y))
                photo_index += 1
            if photo_index >= photo_count:
                break

        qimage = ImageQt.ImageQt(self.final_grid_image)
        pixmap = QPixmap.fromImage(qimage)
        self.grid_preview.setPixmap(pixmap.scaled(self.grid_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def save_grid(self):
        if not self.final_grid_image: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png);;JPEG Image (*.jpg)")
        if file_path:
            try:
                self.final_grid_image.save(file_path)
            except Exception as e:
                print(f"Error saving file: {e}")

    def print_grid(self):
        if not self.final_grid_image: return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter()
            painter.begin(printer)
            
            qimage = ImageQt.ImageQt(self.final_grid_image)
            pixmap = QPixmap.fromImage(qimage)
            
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
            
            painter.end()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        self.open_action = QAction("&Open Image...", self)
        self.open_action.triggered.connect(self.open_image)
        file_menu.addAction(self.open_action)

        save_action = QAction("&Save Grid As...", self)
        save_action.triggered.connect(self.save_grid)
        file_menu.addAction(save_action)

        print_action = QAction("&Print Grid...", self)
        print_action.triggered.connect(self.print_grid)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("&Settings")
        page_settings_action = QAction("Page Settings...", self)
        page_settings_action.triggered.connect(self.open_page_settings)
        settings_menu.addAction(page_settings_action)

        grid_settings_action = QAction("Grid Settings...", self)
        grid_settings_action.triggered.connect(self.open_grid_settings)
        settings_menu.addAction(grid_settings_action)

        save_settings_action = QAction("Save Settings...", self)
        save_settings_action.triggered.connect(self.save_settings)
        settings_menu.addAction(save_settings_action)

        load_settings_action = QAction("Load Settings...", self)
        load_settings_action.triggered.connect(self.load_settings)
        settings_menu.addAction(load_settings_action)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        QMessageBox.about(self, "About PhotoSoft",
                          "<b>Photo Soft</b><br>"
                          "Version 1.0<br><br>"
                          "A powerful tool for photo editing and printing.<br>"
                          "Developed with Cascade AI.")

    def save_settings(self):
        settings = {
            'page_settings': self.page_settings,
            'grid_settings': self.grid_settings,
            'border_color': self.border_settings['color'].name(),
            'border_thickness': self.border_settings['thickness'],
            'layout_index': self.photo_layout_combo.currentIndex(),
            'custom_layout': self.custom_layout_settings
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.page_settings = settings.get('page_settings', self.page_settings)
                self.grid_settings = settings.get('grid_settings', self.grid_settings)
                border_color_hex = settings.get('border_color', '#000000')
                self.border_settings['color'] = QColor(border_color_hex)
                self.border_settings['thickness'] = settings.get('border_thickness', 0)
                self.custom_layout_settings = settings.get('custom_layout', None)
                layout_index = settings.get('layout_index', 0)

                # Block signals to prevent dialog from opening on load
                self.photo_layout_combo.blockSignals(True)
                if self.photo_layout_combo.count() > layout_index:
                    self.photo_layout_combo.setCurrentIndex(layout_index)
                self.photo_layout_combo.blockSignals(False)

                # Manually trigger a grid refresh with loaded settings
                self.generate_grid_preview()
        except FileNotFoundError:
            pass # No settings file yet, use defaults
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load settings: {e}")

    def open_page_settings(self):
        dialog = PageSettingsDialog(self.page_settings, self)
        dialog.settings_saved.connect(self.save_settings)
        if dialog.exec():
            self.page_settings = dialog.get_settings()
            self.generate_grid_preview()

    def on_layout_change(self, index):
        layout_text = self.photo_layout_combo.itemText(index)
        if layout_text == "Custom Layout...":
            dialog = CustomLayoutDialog(self)
            if dialog.exec():
                self.custom_layout_settings = dialog.get_settings()
                self.generate_grid_preview()
            else:
                # If user cancels, revert to previous selection if possible
                # This part is tricky, might need a more robust state management
                pass
        else:
            self.generate_grid_preview()

    def open_border_settings(self):
        dialog = BorderSettingsDialog(self.border_settings, self)
        if dialog.exec():
            self.border_settings = dialog.get_settings()
            self.generate_grid_preview()

    def open_grid_settings(self):
        dialog = GridSettingsDialog(self.grid_settings, self)
        if dialog.exec():
            self.grid_settings = dialog.get_settings()
            self.generate_grid_preview()

class PageSettingsDialog(QDialog):
    settings_saved = pyqtSignal()
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Page Settings")
        self.layout = QFormLayout(self)

        self.paper_size_combo = QComboBox()
        self.paper_size_combo.addItems(["A4", "Letter", "A5", "A6"])
        self.paper_size_combo.setCurrentText(current_settings.get('paper_size', 'A4'))
        self.layout.addRow("Paper Size:", self.paper_size_combo)

        self.margin_top = QSpinBox()
        self.margin_top.setRange(0, 500)
        self.margin_top.setValue(current_settings.get('margin_top', 50))
        self.layout.addRow("Top Margin (px):", self.margin_top)

        self.margin_right = QSpinBox()
        self.margin_right.setRange(0, 500)
        self.margin_right.setValue(current_settings.get('margin_right', 50))
        self.layout.addRow("Right Margin (px):", self.margin_right)

        self.margin_bottom = QSpinBox()
        self.margin_bottom.setRange(0, 500)
        self.margin_bottom.setValue(current_settings.get('margin_bottom', 50))
        self.layout.addRow("Bottom Margin (px):", self.margin_bottom)

        self.margin_left = QSpinBox()
        self.margin_left.setRange(0, 500)
        self.margin_left.setValue(current_settings.get('margin_left', 50))
        self.layout.addRow("Left Margin (px):", self.margin_left)

        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["Center", "Top Left"])
        self.alignment_combo.setCurrentText(current_settings.get('alignment', 'center').title())
        self.layout.addRow("Grid Alignment:", self.alignment_combo)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.save_button = self.button_box.addButton("Save Settings", QDialogButtonBox.ButtonRole.AcceptRole)
        self.save_button.clicked.connect(self.save_and_accept)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def save_and_accept(self):
        self.settings_saved.emit()
        self.accept()

    def get_settings(self):
        return {
            'paper_size': self.paper_size_combo.currentText(),
            'margin_top': self.margin_top.value(),
            'margin_right': self.margin_right.value(),
            'margin_bottom': self.margin_bottom.value(),
            'margin_left': self.margin_left.value(),
            'alignment': self.alignment_combo.currentText().lower().replace(" ", "_")
        }

class GridSettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Settings")
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.spacing_x_spin = QSpinBox()
        self.spacing_x_spin.setRange(0, 200)
        self.spacing_x_spin.setValue(current_settings.get('spacing_x', 20))
        form_layout.addRow("Horizontal Spacing (px):", self.spacing_x_spin)

        self.spacing_y_spin = QSpinBox()
        self.spacing_y_spin.setRange(0, 200)
        self.spacing_y_spin.setValue(current_settings.get('spacing_y', 20))
        form_layout.addRow("Vertical Spacing (px):", self.spacing_y_spin)

        self.layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        self.layout.addLayout(button_box)

    def get_settings(self):
        return {
            'spacing_x': self.spacing_x_spin.value(),
            'spacing_y': self.spacing_y_spin.value(),
        }

class CustomLayoutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Layout")
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 100)
        self.cols_spin.setValue(2)
        form_layout.addRow("Columns (Horizontal):", self.cols_spin)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 100)
        self.rows_spin.setValue(4)
        form_layout.addRow("Rows (Vertical):", self.rows_spin)

        self.photo_count_spin = QSpinBox()
        self.photo_count_spin.setRange(1, 500)
        self.photo_count_spin.setValue(1) # Default to 1
        form_layout.addRow("Photo Count:", self.photo_count_spin)

        self.layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        self.layout.addLayout(button_box)

    def get_settings(self):
        return {
            'rows': self.rows_spin.value(),
            'cols': self.cols_spin.value(),
            'count': self.photo_count_spin.value()
        }

class BorderSettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photo Border Settings")
        self.layout = QVBoxLayout(self)
        self.current_color = current_settings.get('color', QColor('#000000'))

        form_layout = QFormLayout()
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(0, 50)
        self.thickness_spin.setValue(current_settings.get('thickness', 0))
        form_layout.addRow("Border Thickness (px):", self.thickness_spin)

        self.color_btn = QPushButton("Choose Color...")
        self.color_btn.clicked.connect(self.choose_color)
        self.update_color_button_style()
        form_layout.addRow(self.color_btn)

        self.layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        self.layout.addLayout(button_box)

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Choose Border Color")
        if color.isValid():
            self.current_color = color
            self.update_color_button_style()

    def update_color_button_style(self):
        self.color_btn.setStyleSheet(f"background-color: {self.current_color.name()};")

    def get_settings(self):
        return {
            'thickness': self.thickness_spin.value(),
            'color': self.current_color
        }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = PhotoSoft()
    main_win.show()
    sys.exit(app.exec())
