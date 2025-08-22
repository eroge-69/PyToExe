import sys
import os
import requests
from pathlib import Path
from PyQt6 import QtWidgets, QtCore, QtGui

# -----------------------------
API_KEY = "sk_362b229b87c12112f82d61ccf376d6cc346fa3528467ef57"

# Voice dictionary
VOICE_OPTIONS = {
    "Male Voices": {"Finn": "vBKc2FfBKJfcZNyEt1n6"},
    "Female Voices": {"Brittany": "lkVAP8k5tC0Wr1dYyQZH", "Brittney": "kPzsL2i3teMYv0FxEYQ6"}
}

# Model options
MODEL_OPTIONS = ["eleven_monolingual_v1", "eleven_multilingual_v1", "turbo_v2", "turbo_v2.5"]
# -----------------------------

def generate_vo(script_text, filename, voice_id, model):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    data = {"text": script_text, "voice": voice_id, "model": model, "format": "wav"}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    else:
        print("❌ Error generating VO:", response.text)
        return False

class VOAutoTakesApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VO Auto Takes")
        self.setFixedSize(700, 500)  # Fixed size like v14
        self.init_ui()

    def init_ui(self):
        # Dark theme palette
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#1e1e1e"))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#ffffff"))
        self.setPalette(palette)

        font_label = QtGui.QFont("Segoe UI", 10)

        # ----------------------------- Project Name
        lbl_project = QtWidgets.QLabel("Project Name:", self)
        lbl_project.setFont(font_label)
        lbl_project.setGeometry(20, 20, 120, 25)

        self.entry_project = QtWidgets.QLineEdit(self)
        self.entry_project.setGeometry(150, 20, 200, 30)

        # ----------------------------- Script
        lbl_script = QtWidgets.QLabel("Script Text:", self)
        lbl_script.setFont(font_label)
        lbl_script.setGeometry(20, 70, 120, 25)

        self.text_script = QtWidgets.QTextEdit(self)
        self.text_script.setGeometry(150, 70, 500, 100)

        # ----------------------------- Gender selection
        lbl_gender = QtWidgets.QLabel("Select Gender:", self)
        lbl_gender.setFont(font_label)
        lbl_gender.setGeometry(20, 190, 120, 25)

        self.combo_gender = QtWidgets.QComboBox(self)
        self.combo_gender.setGeometry(150, 190, 200, 30)
        self.combo_gender.addItems(VOICE_OPTIONS.keys())
        self.combo_gender.currentTextChanged.connect(self.update_voice_combo)

        # ----------------------------- Voice selection
        lbl_voice = QtWidgets.QLabel("Select Voice:", self)
        lbl_voice.setFont(font_label)
        lbl_voice.setGeometry(20, 240, 120, 25)

        self.combo_voice = QtWidgets.QComboBox(self)
        self.combo_voice.setGeometry(150, 240, 200, 30)
        self.update_voice_combo(self.combo_gender.currentText())

        # ----------------------------- Model selection
        lbl_model = QtWidgets.QLabel("Select Model:", self)
        lbl_model.setFont(font_label)
        lbl_model.setGeometry(20, 290, 120, 25)

        self.combo_model = QtWidgets.QComboBox(self)
        self.combo_model.setGeometry(150, 290, 200, 30)
        self.combo_model.addItems(MODEL_OPTIONS)

        # ----------------------------- Number of takes
        lbl_takes = QtWidgets.QLabel("Number of Takes:", self)
        lbl_takes.setFont(font_label)
        lbl_takes.setGeometry(20, 340, 120, 25)

        self.entry_takes = QtWidgets.QLineEdit(self)
        self.entry_takes.setGeometry(150, 340, 50, 30)
        self.entry_takes.setText("3")

        # ----------------------------- Save folder
        lbl_folder = QtWidgets.QLabel("Save Folder:", self)
        lbl_folder.setFont(font_label)
        lbl_folder.setGeometry(20, 390, 120, 25)

        self.entry_folder = QtWidgets.QLineEdit(self)
        self.entry_folder.setGeometry(150, 390, 300, 30)

        btn_browse = QtWidgets.QPushButton("Browse", self)
        btn_browse.setGeometry(460, 390, 80, 30)
        btn_browse.clicked.connect(self.browse_folder)

        # ----------------------------- Generate button
        self.btn_generate = QtWidgets.QPushButton("Generate VO", self)
        self.btn_generate.setGeometry(20, 440, 200, 40)
        self.btn_generate.clicked.connect(self.start_generation)

        # ----------------------------- Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(240, 450, 410, 25)
        self.progress_bar.setValue(0)

        # ----------------------------- Styles for inputs
        input_style = """
        QLineEdit, QTextEdit, QComboBox {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            border-radius: 5px;
            padding: 4px;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 1px solid #00aaff;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: #ffffff;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #00aaff;
        }
        QProgressBar {
            border: 1px solid #5a5a5a;
            border-radius: 5px;
            text-align: center;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #00aaff;
            width: 20px;
        }
        """
        self.setStyleSheet(input_style)

    def update_voice_combo(self, gender):
        self.combo_voice.clear()
        self.combo_voice.addItems(VOICE_OPTIONS[gender].keys())

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.entry_folder.setText(folder)

    def start_generation(self):
        thread = QtCore.QThread()
        worker = GenerationWorker(
            self.entry_project.text(),
            self.text_script.toPlainText(),
            self.combo_gender.currentText(),
            self.combo_voice.currentText(),
            self.combo_model.currentText(),
            self.entry_takes.text(),
            self.entry_folder.text(),
            self.progress_bar
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(self.open_output_folder)
        thread.start()

    def open_output_folder(self, folder_path):
        if folder_path and os.path.exists(folder_path):
            os.startfile(folder_path)

class GenerationWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)

    def __init__(self, project, script, gender, voice, model, takes, folder, progress_bar):
        super().__init__()
        self.project = project
        self.script = script
        self.gender = gender
        self.voice = VOICE_OPTIONS[gender][voice]
        self.model = model
        self.takes = int(takes) if takes.isdigit() else 1
        self.folder = folder or "VO_Output"
        self.progress_bar = progress_bar

    def run(self):
        output_folder = Path(self.folder) / self.project / self.gender
        output_folder.mkdir(parents=True, exist_ok=True)

        self.progress_bar.setMaximum(self.takes)
        for i in range(1, self.takes + 1):
            filename = output_folder / f"Take_{i}.wav"
            generate_vo(self.script, filename, self.voice, self.model)
            self.progress_bar.setValue(i)

        self.finished.emit(str(output_folder))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = VOAutoTakesApp()
    window.show()
    sys.exit(app.exec())
