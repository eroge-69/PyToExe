import sys
import os
import fitz  # PyMuPDF
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class PDFToImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Image Converter")
        self.setMinimumSize(1000, 800)

        self.pdf_path = None
        self.images = []
        self.current_page = 0
        self.output_dir = None

        # Layout and UI elements
        self.layout = QVBoxLayout()
        self.label = QLabel("Upload a PDF to convert")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        self.label.setMinimumSize(600, 700)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Select PDF File")
        self.convert_button = QPushButton("Convert PDF")
        self.prev_button = QPushButton("Previous Page")
        self.next_button = QPushButton("Next Page")

        self.upload_button.clicked.connect(self.select_pdf)
        self.convert_button.clicked.connect(self.convert_to_png)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        # Add to layouts
        self.button_layout.addWidget(self.upload_button)
        self.button_layout.addWidget(self.convert_button)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.images = []

            # Create output directory under script path (not PDF path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = os.path.join(script_dir, base_name)
            os.makedirs(self.output_dir, exist_ok=True)

            # Preview pages (low-res)
            doc = fitz.open(self.pdf_path)
            self.images = []
            for page_num in range(min(3, doc.page_count)):  # preview first 3 pages
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # preview res
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.images.append(img)

            self.current_page = 0
            self.show_image(self.current_page)

            QMessageBox.information(self, "Upload Successful",
                                    f"PDF uploaded successfully!\nImages will be saved in: {self.output_dir}")

    def convert_to_png(self):
        """Converts PDF pages to high-quality images, saves them, and shows the first page."""
        if not self.pdf_path:
            QMessageBox.warning(self, "Error", "Please select a PDF file first!")
            return

        doc = fitz.open(self.pdf_path)
        self.images = []

        # Progress dialog
        progress = QProgressDialog("Converting PDF...", "Cancel", 0, doc.page_count, self)
        progress.setWindowTitle("Converting")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        for page_num in range(doc.page_count):
            if progress.wasCanceled():
                break

            page = doc[page_num]
            # High resolution (3.0 ≈ 300dpi)
            pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.images.append(img)

            # Save image to output folder
            output_path = os.path.join(self.output_dir, f"page_{page_num+1}.png")
            img.save(output_path, "PNG")

            progress.setValue(page_num + 1)

        self.current_page = 0
        if self.images:
            self.show_image(self.current_page)
            QMessageBox.information(self, "Conversion Complete",
                                    f"PDF successfully converted!\nImages saved in: {self.output_dir}")

    def show_image(self, index):
        """Displays the image on the QLabel."""
        if 0 <= index < len(self.images):
            pixmap = self.pil2pixmap(self.images[index])
            self.label.setPixmap(
                pixmap.scaled(
                    self.label.width(),
                    self.label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
            self.label.setAlignment(Qt.AlignCenter)

    def prev_page(self):
        if self.images and self.current_page > 0:
            self.current_page -= 1
            self.show_image(self.current_page)

    def next_page(self):
        if self.images and self.current_page < len(self.images) - 1:
            self.current_page += 1
            self.show_image(self.current_page)

    def pil2pixmap(self, image):
        """Converts PIL Image to QPixmap without ImageQt."""
        if image.mode != "RGB":
            image = image.convert("RGB")
        r, g, b = image.split()
        image = Image.merge("RGB", (b, g, r))
        data = image.tobytes("raw", "RGB")
        qimg = QImage(data, image.width, image.height, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFToImageApp()
    window.show()
    sys.exit(app.exec_())
