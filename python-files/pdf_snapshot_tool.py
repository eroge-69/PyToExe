
# app.py - PDF Snapshot Tool with Re-Cropping and Comment Feature

# This is a trimmed-down and clean version integrating:
# - PDF viewing
# - Snapshot selection
# - Re-cropping with rubber band tool
# - Adding text/answers to bottom before saving
#
# Required Libraries: PyQt6, fitz (PyMuPDF)

# Due to length, the complete updated code exceeds this message box size.
# However, here are the necessary parts to update:

# --- 1. Add RecropDialog class ---

class RecropDialog(QDialog):
    def __init__(self, original_pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Re-Crop and Annotate Snapshot")
        self.setMinimumSize(800, 700)

        self.original_pixmap = original_pixmap

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.pixmap_item = self.scene.addPixmap(original_pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())

        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Enter answer or comment (optional)...")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(self.comment_input)
        layout.addWidget(button_box)

    def get_cropped_pixmap_with_comment(self):
        rect = self.view.rubberBandRect()
        if rect.isNull():
            crop = self.original_pixmap
        else:
            scene_rect = self.view.mapToScene(rect).boundingRect().toRect()
            scene_rect = scene_rect.intersected(self.original_pixmap.rect())
            crop = self.original_pixmap.copy(scene_rect)

        comment = self.comment_input.text().strip()
        if not comment:
            return crop

        padding = 10
        font = QFont("Arial", 14)
        metrics = QFontMetrics(font)
        text_height = metrics.height() + padding * 2
        new_height = crop.height() + text_height

        annotated = QPixmap(crop.width(), new_height)
        annotated.fill(Qt.GlobalColor.white)

        painter = QPainter(annotated)
        painter.drawPixmap(0, 0, crop)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))

        text_rect = QRect(0, crop.height(), crop.width(), text_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, comment)
        painter.end()

        return annotated


# --- 2. Modify process_snapshot() to call RecropDialog ---

# Replace final line of your existing process_snapshot() function:
# self.save_snapshot(pixmap)
# With:
recrop_dialog = RecropDialog(pixmap, self)
if recrop_dialog.exec() == QDialog.DialogCode.Accepted:
    final_pixmap = recrop_dialog.get_cropped_pixmap_with_comment()
else:
    final_pixmap = pixmap

self.save_snapshot(final_pixmap)


# --- 3. (Optional) PyInstaller Command to Create Portable EXE ---
# After saving this as app.py and installing requirements:
# pip install PyQt6 pymupdf
# Then run:
# pyinstaller --onefile --windowed app.py

# The output EXE will be found inside the /dist directory.
