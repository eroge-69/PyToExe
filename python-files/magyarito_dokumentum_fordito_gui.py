import sys
import os
import traceback
import threading
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressBar, QLabel, QPushButton
import pyttsx3
from transformers import MarianMTModel, MarianTokenizer
from docx import Document
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

APP_NAME = "Magyarító Dokumentum Fordító"

# --- Hibák naplózása ---
def log_exceptions(exc_type, exc_value, exc_traceback):
    with open("exe_log.txt", "w", encoding="utf-8") as f:
        f.write("Hiba történt a programban:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

sys.excepthook = log_exceptions

# --- Modell útvonal (relatív a projekt mappához) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "opus-mt-en-hu")

# Ellenőrizzük a szükséges fájlokat
required_files = [
    "config.json",
    "generation_config.json",
    "pytorch_model.bin",
    "source.spm",
    "target.spm",
    "tokenizer_config.json",
    "vocab.json"
]

missing = [f for f in required_files if not os.path.exists(os.path.join(MODEL_DIR, f))]
if missing:
    QMessageBox.critical(None, APP_NAME, f"A következő fájlok hiányoznak a modell mappából:\n{', '.join(missing)}")
    sys.exit()

# --- Fordító modell betöltése ---
try:
    tokenizer = MarianTokenizer.from_pretrained(MODEL_DIR)
    model = MarianMTModel.from_pretrained(MODEL_DIR)
except Exception as e:
    QMessageBox.critical(None, APP_NAME, f"A Marian modell betöltése sikertelen: {e}")
    sys.exit()

# --- Szöveg fordítása ---
def translate_text(text):
    lines = text.split("\n")
    translated_lines = []
    for line in lines:
        if not line.strip():
            continue
        try:
            batch = tokenizer([line], return_tensors="pt", truncation=True, max_length=512)
            gen = model.generate(**batch, max_length=512)
            translated_lines.append(tokenizer.decode(gen[0], skip_special_tokens=True))
        except Exception as e:
            translated_lines.append(f"[FORDÍTÁSI HIBA: {e}]")
    return "\n".join(translated_lines)

# --- Szöveg kinyerése ---
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext in [".doc", ".docx"]:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext == ".epub":
            book = epub.read_epub(file_path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    text += soup.get_text() + "\n"
        else:
            QMessageBox.critical(None, APP_NAME, "Támogatott formátumok: txt, doc, docx, pdf, epub")
    except Exception as e:
        QMessageBox.critical(None, APP_NAME, f"Szövegkinyerési hiba: {e}")
    return text

# --- TTS külön szálon ---
class TTSThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self, text, output_path):
        super().__init__()
        self.text = text
        self.output_path = output_path

    def run(self):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            for v in voices:
                if "male" in v.name.lower() or "férfi" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.save_to_file(self.text, self.output_path)
            engine.runAndWait()
            self.progress_signal.emit(100)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, APP_NAME, f"TTS hiba: {e}")

# --- GUI ---
class TranslatorGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 700, 350)

        # Fájl kiválasztás
        self.label_file = QLabel("Fájl kiválasztása:")
        self.entry_file = QtWidgets.QLineEdit()
        self.btn_browse = QPushButton("Tallózás")
        self.btn_browse.clicked.connect(self.select_file)

        # Fordítás + MP3
        self.btn_translate = QPushButton("Fordítás + MP3 létrehozása")
        self.btn_translate.clicked.connect(self.translate_file)

        # Progress bar
        self.progressbar = QProgressBar()
        self.progressbar.setValue(0)
        self.progressbar.setFormat("%p%")  # százalékos formátum

        # Státusz
        self.status_label = QLabel("")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_file)
        layout.addWidget(self.entry_file)
        layout.addWidget(self.btn_browse)
        layout.addWidget(self.btn_translate)
        layout.addWidget(self.progressbar)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, APP_NAME, "", "Dokumentumok (*.txt *.doc *.docx *.pdf *.epub)")
        if file_path:
            self.entry_file.setText(file_path)

    def translate_file(self):
        file_path = self.entry_file.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.critical(self, APP_NAME, "Érvénytelen fájl!")
            return

        text = extract_text(file_path)
        if not text.strip():
            QMessageBox.critical(self, APP_NAME, "Nem sikerült szöveget kinyerni!")
            return

        self.progressbar.setValue(0)
        self.status_label.setText("Fordítás folyamatban...")
        QtWidgets.QApplication.processEvents()

        try:
            translated = translate_text(text)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Fordítási hiba: {e}")
            return

        output_dir = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        translated_path = os.path.join(output_dir, f"{base_name}_HU.txt")
        mp3_path = os.path.join(output_dir, f"{base_name}_HU.mp3")

        # Mentés szöveg
        try:
            with open(translated_path, "w", encoding="utf-8") as f:
                f.write(translated)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"A fájl mentése nem sikerült: {e}")
            return

        self.progressbar.setValue(50)
        self.status_label.setText("Fordítás kész! MP3 generálás folyamatban...")
        QtWidgets.QApplication.processEvents()

        # TTS
        self.tts_thread = TTSThread(translated, mp3_path)
        self.tts_thread.progress_signal.connect(self.update_progress)
        self.tts_thread.start()

    def update_progress(self, value):
        self.progressbar.setValue(value)
        if value >= 100:
            self.status_label.setText("Kész!")
            QMessageBox.information(self, APP_NAME, "MP3 létrehozva!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TranslatorGUI()
    window.show()
    sys.exit(app.exec())



