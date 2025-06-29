import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QLabel, QSpacerItem, QSizePolicy, QInputDialog, QLineEdit
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import subprocess

# Optional imports with error handling
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

class PDFTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 PDF Toolkit - By Divyansh")
        self.setGeometry(100, 100, 500, 600)

        # Set icon if available
        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header
        header = QLabel("🛠️ PDF Toolkit by Divyansh")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Buttons and functions
        actions = {
            "📚 Merge PDFs": self.merge_pdfs,
            "✂️ Split PDF": self.split_pdf,
            "📦 Compress PDF": self.compress_pdf,
            "🖼️ PDF to Images": self.pdf_to_images,
            "🗂️ Images to PDF": self.images_to_pdf,
            "📝 Extract Text": self.extract_text,
            "🔐 Add Password": self.add_password,
            "🔓 Remove Password": self.remove_password,
            "🔄 Rotate PDF": self.rotate_pdf
        }

        for label, func in actions.items():
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("font-size: 14px;")
            btn.clicked.connect(func)
            layout.addWidget(btn)

        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def show_msg(self, msg):
        QMessageBox.information(self, "Info", msg)

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def merge_pdfs(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs to Merge", "", "PDF Files (*.pdf)")
            if files:
                merger = PdfMerger()
                for f in files:
                    merger.append(f)
                out, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
                if out:
                    merger.write(out)
                    merger.close()
                    self.show_msg(f"Merged PDF saved to:\n{out}")
        except Exception as e:
            self.show_error(f"Error merging PDFs: {str(e)}")

    def split_pdf(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select PDF to Split", "", "PDF Files (*.pdf)")
            if f:
                # Get output directory
                output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
                if not output_dir:
                    return
                
                reader = PdfReader(f)
                base_name = os.path.splitext(os.path.basename(f))[0]
                
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    out_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                    with open(out_path, "wb") as out_f:
                        writer.write(out_f)
                
                self.show_msg(f"Split completed. {len(reader.pages)} files saved in:\n{output_dir}")
        except Exception as e:
            self.show_error(f"Error splitting PDF: {str(e)}")

    def compress_pdf(self):
        try:
            input_pdf, _ = QFileDialog.getOpenFileName(self, "Select PDF to Compress", "", "PDF Files (*.pdf)")
            if input_pdf:
                output_pdf, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
                if output_pdf:
                    # Check if Ghostscript is available
                    try:
                        cmd = [
                            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                            "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
                            f"-sOutputFile={output_pdf}", input_pdf
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            self.show_msg(f"Compressed PDF saved to:\n{output_pdf}")
                        else:
                            self.show_error("Ghostscript failed. Make sure it's installed and in PATH.")
                    except FileNotFoundError:
                        self.show_error("Ghostscript not found. Please install Ghostscript to use PDF compression.")
        except Exception as e:
            self.show_error(f"Error compressing PDF: {str(e)}")

    def pdf_to_images(self):
        if not PDF2IMAGE_AVAILABLE:
            self.show_error("pdf2image library not installed. Install with: pip install pdf2image")
            return
        
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
            if f:
                # Get output directory
                output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
                if not output_dir:
                    return
                
                images = convert_from_path(f)
                base = os.path.splitext(os.path.basename(f))[0]
                
                for i, img in enumerate(images):
                    img_path = os.path.join(output_dir, f"{base}_page{i+1}.png")
                    img.save(img_path, "PNG")
                
                self.show_msg(f"Images saved in:\n{output_dir}")
        except Exception as e:
            self.show_error(f"Error converting PDF to images: {str(e)}")

    def images_to_pdf(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Images", "", 
                "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp);;All Files (*)"
            )
            if not files:
                return
                
            output, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if not output:
                return
                
            # Ensure output has .pdf extension
            if not output.lower().endswith('.pdf'):
                output += '.pdf'
            
            # Sort files by name to maintain order
            files.sort()
            imgs = []
            
            # Supported image extensions
            supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
            
            for file_path in files:
                try:
                    # Check file extension
                    _, ext = os.path.splitext(file_path.lower())
                    if ext not in supported_extensions:
                        self.show_error(f"Unsupported file format: {ext}\nSupported formats: JPG, PNG, BMP, TIFF, GIF, WEBP")
                        return
                    
                    # Open and process image
                    img = Image.open(file_path)
                    
                    # Handle different image modes
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    imgs.append(img)
                    
                except Exception as img_error:
                    self.show_error(f"Error processing image {os.path.basename(file_path)}: {str(img_error)}")
                    return
            
            if imgs:
                # Save as PDF
                imgs[0].save(
                    output, 
                    format='PDF',
                    save_all=True, 
                    append_images=imgs[1:] if len(imgs) > 1 else []
                )
                self.show_msg(f"PDF created successfully with {len(imgs)} images:\n{output}")
            else:
                self.show_error("No valid images found to convert.")
                
        except Exception as e:
            self.show_error(f"Error creating PDF from images: {str(e)}")

    def extract_text(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
            if f:
                reader = PdfReader(f)
                text_parts = []
                
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}\n\n")
                
                if text_parts:
                    text = "".join(text_parts)
                    output, _ = QFileDialog.getSaveFileName(self, "Save Text File", "", "Text Files (*.txt)")
                    if output:
                        with open(output, "w", encoding="utf-8") as out:
                            out.write(text)
                        self.show_msg(f"Text saved to:\n{output}")
                else:
                    self.show_msg("No text found in the PDF.")
        except Exception as e:
            self.show_error(f"Error extracting text: {str(e)}")

    def add_password(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
            if f:
                # Get password from user
                from PyQt5.QtWidgets import QLineEdit
                password, ok = QInputDialog.getText(
                    self, "Set Password", "Enter password for PDF:", 
                    QLineEdit.Password
                )
                if ok and password:
                    reader = PdfReader(f)
                    writer = PdfWriter()
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    writer.encrypt(password)
                    
                    output, _ = QFileDialog.getSaveFileName(self, "Save Encrypted PDF", "", "PDF Files (*.pdf)")
                    if output:
                        with open(output, "wb") as out:
                            writer.write(out)
                        self.show_msg(f"Encrypted PDF saved to:\n{output}")
        except Exception as e:
            self.show_error(f"Error adding password: {str(e)}")

    def remove_password(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select Encrypted PDF", "", "PDF Files (*.pdf)")
            if f:
                # Get password from user
                from PyQt5.QtWidgets import QLineEdit
                password, ok = QInputDialog.getText(
                    self, "Enter Password", "Enter PDF password:", 
                    QLineEdit.Password
                )
                if ok and password:
                    try:
                        reader = PdfReader(f)
                        if reader.is_encrypted:
                            reader.decrypt(password)
                        
                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        
                        output, _ = QFileDialog.getSaveFileName(self, "Save Decrypted PDF", "", "PDF Files (*.pdf)")
                        if output:
                            with open(output, "wb") as out:
                                writer.write(out)
                            self.show_msg(f"Decrypted PDF saved to:\n{output}")
                    except Exception:
                        self.show_error("Incorrect password or file is not encrypted.")
        except Exception as e:
            self.show_error(f"Error removing password: {str(e)}")

    def rotate_pdf(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Select PDF to Rotate", "", "PDF Files (*.pdf)")
            if f:
                # Get rotation angle
                angles = ["90", "180", "270"]
                angle, ok = QInputDialog.getItem(
                    self, "Select Rotation", "Choose rotation angle (clockwise):", 
                    angles, 0, False
                )
                if ok:
                    reader = PdfReader(f)
                    writer = PdfWriter()
                    
                    for page in reader.pages:
                        page.rotate(int(angle))
                        writer.add_page(page)
                    
                    output, _ = QFileDialog.getSaveFileName(self, "Save Rotated PDF", "", "PDF Files (*.pdf)")
                    if output:
                        with open(output, "wb") as out:
                            writer.write(out)
                        self.show_msg(f"Rotated PDF saved to:\n{output}")
        except Exception as e:
            self.show_error(f"Error rotating PDF: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTool()
    window.show()
    sys.exit(app.exec_())