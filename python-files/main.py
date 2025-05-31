import sys
import os
if hasattr(sys, 'frozen'):
        base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(__file__)

dll_path = os.path.join(base_dir, "llama_cpp", "lib")
if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
else:
    print("[ERROR] Missing llama_cpp/lib folder!")
import cv2
import numpy as np
import easyocr
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog, QSlider, QLineEdit, QGroupBox, QFrame, QMessageBox, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QTextCursor, QGuiApplication
from PyQt5.QtCore import QMimeData
from llm_handler import translate_with_llm, get_llm
from glossary_handler import load_glossary, extract_relevant_terms, parse_translation_output
from history_handler import save_translation_history
from data import add_to_json_file, add_xlsx_to_json

model = get_llm()

    
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        # Chỉ nhận plain text khi paste
        self.insertPlainText(source.text())

class TranslateWorker(QThread):
    finished = pyqtSignal(dict, list, str, list)
    def __init__(self, text, glossary):
        super().__init__()
        self.text = text
        self.glossary = glossary
    def run(self):
        relevant_glossary = extract_relevant_terms(self.text, self.glossary)
        result = translate_with_llm(self.text, relevant_glossary, model)
        # Tìm source
        matched_entry = next((entry for entry in self.glossary if entry['jp'] == self.text), None)
        last_source = matched_entry['src'] if matched_entry and 'src' in matched_entry else ''
        self.finished.emit(result, relevant_glossary, last_source, self.glossary)

class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Translation Desktop App')
        self.resize(1280, 800)
        self.setStyleSheet('QWidget { background: #f6f7fb; font-family: "Segoe UI", Arial, sans-serif; }')
        self.reader = easyocr.Reader(['ja', 'en'], gpu=False)
        self.last_input = ''
        self.last_output = ''
        self.last_alternatives = []
        self.last_source = ''
        self.last_relevant_glossary = []
        self.current_img = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(32)
        # Left panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(24)
        left_panel.setContentsMargins(0,0,0,0)
        left_panel_container = QGroupBox()
        left_panel_container.setTitle('')
        left_panel_container.setStyleSheet('QGroupBox { background: #fff; border-radius: 18px; border: 1.5px solid #e0e0e0; padding: 32px; }')
        left_panel_inner = QVBoxLayout()
        # Input text
        self.input_text = PlainTextEdit()
        self.input_text.setPlaceholderText('Enter text or paste image...')
        self.input_text.setStyleSheet('font-size: 24px; min-height: 120px; color: #222; background: transparent; border: none; font-family: "Segoe UI", Arial, "Meiryo", "MS PGothic", "Noto Sans JP", "Noto Sans", sans-serif; font-weight: 400; letter-spacing: 0.01em;')
        left_panel_inner.addWidget(self.input_text)
        # Button group
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        self.ocr_btn = QPushButton('OCR')
        self.ocr_btn.setStyleSheet('background: #e3eafc; color: #1967d2; font-size: 16px; border-radius: 8px; padding: 8px 24px; font-weight: bold; min-width: 120px;')
        self.ocr_btn.clicked.connect(self.ocr_image)
        self.translate_btn = QPushButton('Translate')
        self.translate_btn.setStyleSheet('background: #1967d2; color: #fff; font-size: 16px; border-radius: 8px; padding: 8px 24px; font-weight: bold; min-width: 120px;')
        self.translate_btn.clicked.connect(self.translate_text)
        self.glossary_btn = QPushButton('Add Glossary')
        self.glossary_btn.setStyleSheet('background: #fbbc04; color: #202124; font-size: 16px; border-radius: 8px; padding: 8px 24px; font-weight: bold; min-width: 120px;')
        self.glossary_btn.clicked.connect(self.add_glossary)
        btn_layout.addWidget(self.ocr_btn)
        btn_layout.addWidget(self.translate_btn)
        btn_layout.addWidget(self.glossary_btn)
        left_panel_inner.addLayout(btn_layout)
        # Auto-rotate panel
        auto_rotate_group = QGroupBox()
        auto_rotate_group.setTitle('')
        auto_rotate_group.setStyleSheet('QGroupBox { background:#f8fafc; border-radius:12px; padding:18px 12px; }')
        auto_rotate_layout = QVBoxLayout()
        self.upload_img_btn = QPushButton('Choose File')
        self.upload_img_btn.setStyleSheet('background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 6px 18px; font-size: 15px;')
        self.upload_img_btn.clicked.connect(self.upload_image)
        auto_rotate_layout.addWidget(self.upload_img_btn)
        self.img_label = QLabel()
        self.img_label.setFixedSize(220, 160)
        self.img_label.setStyleSheet('background:#fafbfc; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:24px;')
        auto_rotate_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(12)
        slider_layout.addWidget(QLabel('Angle:'))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 359)
        self.angle_slider.setFixedWidth(120)
        self.angle_slider.valueChanged.connect(self.update_angle)
        slider_layout.addWidget(self.angle_slider)
        self.angle_input = QLineEdit('0')
        self.angle_input.setFixedWidth(60)
        self.angle_input.editingFinished.connect(self.update_slider)
        slider_layout.addWidget(self.angle_input)
        auto_rotate_layout.addLayout(slider_layout)
        self.extract_btn = QPushButton('Extract')
        self.extract_btn.setStyleSheet('background: #1967d2; color: #fff; border-radius:8px; font-weight:bold; font-size:14px; padding:4px 18px; min-width:70px;')
        self.extract_btn.clicked.connect(self.extract_text_from_image)
        auto_rotate_layout.addWidget(self.extract_btn)
        self.ocr_result = QLabel()
        self.ocr_result.setStyleSheet('font-size:18px;')
        auto_rotate_layout.addWidget(self.ocr_result)
        auto_rotate_group.setLayout(auto_rotate_layout)
        left_panel_inner.addWidget(auto_rotate_group)
        left_panel_container.setLayout(left_panel_inner)
        left_panel.addWidget(left_panel_container)
        main_layout.addLayout(left_panel, 2)
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)
        right_panel.setContentsMargins(0,0,0,0)
        right_panel_container = QGroupBox()
        right_panel_container.setTitle('')
        right_panel_container.setStyleSheet('QGroupBox { background: #fff; border-radius: 18px; border: 1.5px solid #e0e0e0; padding: 32px; }')
        right_panel_inner = QVBoxLayout()
        # Output text
        self.output_text = QLabel()
        self.output_text.setStyleSheet('font-size:24px; font-weight:bold; color:#1a237e; min-height:40px; max-height:80px; text-transform:uppercase; background:transparent; letter-spacing:0.03em;')
        self.output_text.setAlignment(Qt.AlignCenter)
        self.output_text.setWordWrap(True)
        right_panel_inner.addWidget(self.output_text)
        # Edit translation
        edit_group = QGroupBox()
        edit_group.setTitle('')
        edit_group.setStyleSheet('QGroupBox { background: #f8fafc; border-radius: 10px; border: 1px solid #e0e0e0; }')
        edit_group.setFixedWidth(600)    
        edit_group.setFixedHeight(300)    
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(2)
        edit_label = QLabel('Edit translation:')
        edit_label.setStyleSheet('font-size:18px; font-weight:500;')
        edit_layout.addWidget(edit_label)
        self.edit_translation = QTextEdit()
        self.edit_translation.setFixedHeight(36)  
        self.edit_translation.setMaximumHeight(36)
        self.edit_translation.setMaximumWidth(420)  
        self.edit_translation.setStyleSheet('font-size:18px;')
        edit_layout.addWidget(self.edit_translation)
        self.source_label = QLabel('Source:')
        self.source_label.setStyleSheet('color: #888; font-size: 16px; margin-bottom: 8px;')
        edit_layout.addWidget(self.source_label)
        self.save_edit_btn = QPushButton('Save Edit')
        self.save_edit_btn.setStyleSheet('background: #43a047; color: #fff; border-radius:8px; font-weight:bold; font-size:14px; padding:4px 18px; min-width:70px;')
        self.save_edit_btn.clicked.connect(self.save_edit)
        edit_layout.addWidget(self.save_edit_btn)
        edit_group.setLayout(edit_layout)
        right_panel_inner.addWidget(edit_group)
        # Add pair to glossary and alternatives
        add_alt_layout = QHBoxLayout()
        self.add_pair_btn = QPushButton('Add this pair to Glossary')
        self.add_pair_btn.setStyleSheet('background: #e3eafc; color: #1967d2; font-size: 18px; border-radius: 10px; padding: 10px 32px; font-weight: bold; min-width: 180px;')
        self.add_pair_btn.clicked.connect(self.add_pair_to_glossary)
        add_alt_layout.addWidget(self.add_pair_btn)
        self.alt_label = QLabel('Alternatives:')
        self.alt_label.setStyleSheet('color: #757575; font-size: 20px; margin-top: 8px; margin-bottom: 4px; font-weight: bold;')
        add_alt_layout.addWidget(self.alt_label)
        right_panel_inner.addLayout(add_alt_layout)
        # Alternatives as scrollable horizontal buttons
        self.alt_scroll = QScrollArea()
        self.alt_scroll.setWidgetResizable(True)
        self.alt_scroll.setFixedWidth(600)
        self.alt_scroll.setMaximumWidth(800)
        self.alt_scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        self.alt_btns_widget = QWidget()
        self.alt_btns_layout = QVBoxLayout()
        self.alt_btns_layout.setSpacing(0)
        self.alt_btns_layout.setContentsMargins(0,0,0,0)
        self.alt_btns_widget.setLayout(self.alt_btns_layout)
        self.alt_scroll.setWidget(self.alt_btns_widget)
        right_panel_inner.addWidget(self.alt_scroll)
        right_panel_container.setLayout(right_panel_inner)
        right_panel.addWidget(right_panel_container)
        main_layout.addLayout(right_panel, 2) 
        self.setLayout(main_layout)

    def upload_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open image', '', 'Image files (*.png *.jpg *.jpeg *.bmp)')
        if fname:
            self.current_img = fname
            self.update_image_preview()

    def ocr_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open image for OCR', '', 'Image files (*.png *.jpg *.jpeg *.bmp)')
        if fname:
            img = cv2.imread(fname)
            result = self.reader.readtext(img, detail=0)
            self.input_text.setPlainText('\n'.join(result))

    def update_image_preview(self):
        if not self.current_img:
            self.img_label.clear()
            return
        angle = int(self.angle_input.text()) if self.angle_input.text().isdigit() else 0
        img = cv2.imread(self.current_img)
        if img is None:
            self.img_label.clear()
            return
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        if angle != 0:
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            M[0, 2] += (new_w / 2) - center[0]
            M[1, 2] += (new_h / 2) - center[1]
            img = cv2.warpAffine(img, M, (new_w, new_h), borderValue=(255,255,255))
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(self.img_label.width(), self.img_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setPixmap(pix)

    def extract_text_from_image(self):
        if not self.current_img:
            self.ocr_result.setText('No image loaded.')
            return
        angle = int(self.angle_input.text()) if self.angle_input.text().isdigit() else 0
        img = cv2.imread(self.current_img)
        if img is None:
            self.ocr_result.setText('Cannot load image.')
            return
        if angle != 0:
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            M[0, 2] += (new_w / 2) - center[0]
            M[1, 2] += (new_h / 2) - center[1]
            img = cv2.warpAffine(img, M, (new_w, new_h), borderValue=(255,255,255))
        result = self.reader.readtext(img, detail=0)
        self.ocr_result.setText('\n'.join(result))
        self.input_text.setPlainText('\n'.join(result))

    def update_angle(self):
        self.angle_input.setText(str(self.angle_slider.value()))
        self.update_image_preview()

    def update_slider(self):
        val = int(self.angle_input.text()) if self.angle_input.text().isdigit() else 0
        self.angle_slider.setValue(val)
        self.update_image_preview()

    def translate_text(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.output_text.setText('No input text.')
            return
        self.translate_btn.setEnabled(False)
        self.translate_btn.setText('Translating...')
        glossary = load_glossary()
        self.worker = TranslateWorker(text, glossary)
        self.worker.finished.connect(self.on_translate_finished)
        self.worker.start()

    def on_translate_finished(self, result, relevant_glossary, last_source, glossary):
        self.last_input = self.input_text.toPlainText().strip()
        self.last_output = result['result']['translation']
        self.last_alternatives = result['result'].get('alternatives', [])
        self.last_source = last_source
        self.last_relevant_glossary = relevant_glossary
        self.output_text.setText(self.last_output)
        self.edit_translation.setPlainText(self.last_output)
        self.source_label.setText(f"Source: {self.last_source}")
        for i in reversed(range(self.alt_btns_layout.count())):
            w = self.alt_btns_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        for alt in self.last_alternatives:
            btn = QPushButton(alt)
            btn.setStyleSheet('QPushButton { background: #fff; color: #222; border: 1.5px solid #e0e0e0; border-radius: 18px; margin: 4px 8px 4px 0; padding: 8px 24px; font-size: 18px; font-weight: 500; min-width: 120px; max-width: 320px; } QPushButton:hover { background: #e3eafc; color: #1967d2; border: 1.5px solid #1967d2; }')
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, alt=alt: self.select_alternative(alt))
            self.alt_btns_layout.addWidget(btn)
        self.alt_btns_layout.addStretch(1)
        save_translation_history(self.last_input, result, relevant_glossary)
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText('Translate')

    def select_alternative(self, alt):
        self.output_text.setText(alt)
        self.edit_translation.setPlainText(alt)

    def save_edit(self):
        self.output_text.setText(self.edit_translation.toPlainText())

    def add_pair_to_glossary(self):
        jp = self.last_input.strip()
        en = self.output_text.text().strip()
        source = self.last_source
        if jp and en:
            file_path = resource_path('data/glossary.json')
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                glossary = json.load(f)
            glossary.append({'jp': jp, 'en': en, 'src': source})
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(glossary, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, 'Success', 'Added to glossary!')

    def add_glossary(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Add Glossary', '', 'Text files (*.txt);;Excel files (*.xlsx)')
        if fname:
            if fname.endswith('.txt'):
                with open(fname, 'r', encoding='utf-8') as f:
                    data = f.read()
                add_to_json_file(resource_path('data/glossary.json'), data)
            elif fname.endswith('.xlsx'):
                add_xlsx_to_json(resource_path('data/glossary.json'), fname)
            QMessageBox.information(self, 'Success', 'Glossary updated!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DesktopApp()
    win.show()
    sys.exit(app.exec_())
