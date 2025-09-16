"""
Whisper GUI downloader + transcription app (single-file)
Requirements: Python 3.10+, PySide6, openai-whisper (or faster-whisper alternative), ffmpeg installed system-wide.
This file provides:
 - GUI to select model (large-v3, large-v3-turbo, etc.)
 - Download button (downloads model via whisper.load_model)
 - Options for device (cpu / cuda), fp16, task (transcribe/translate), language
 - Select audio file and transcribe; shows simple progress messages and saves .txt output
 - Uses QThread for background work so GUI stays responsive

Build to .exe: use pyinstaller --onefile --add-data for any required files. See README in chat for exact command examples.
"""

import sys
import os
import traceback
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QCheckBox, QLineEdit, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal

# NOTE: whisper import is delayed until worker thread to avoid heavy import time on GUI start

APP_NAME = "Whisper Downloader & GUI"


class DownloadWorker(QThread):
    status = Signal(str)
    finished_ok = Signal(object)  # emits loaded model
    error = Signal(str)

    def __init__(self, model_name: str, device: str, fp16: bool, cache_dir: str | None = None):
        super().__init__()
        self.model_name = model_name
        self.device = device
        self.fp16 = fp16
        self.cache_dir = cache_dir

    def run(self):
        try:
            self.status.emit(f"Importing whisper package...")
            # import inside thread
            import whisper
            self.status.emit(f"Loading model '{self.model_name}' (this can take several minutes)...")
            # whisper.load_model will download the model into cache automatically
            # You may control cache directory via environment var XDG_CACHE_HOME or whisper's options
            if self.cache_dir:
                os.environ.setdefault("XDG_CACHE_HOME", str(self.cache_dir))

            model = whisper.load_model(self.model_name, device=self.device, download_root=self.cache_dir)

            # optionally convert to fp16 on CPU is not supported; pass through
            self.status.emit("Model loaded successfully.")
            self.finished_ok.emit(model)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"Error loading model: {e}\n{tb}")


class TranscribeWorker(QThread):
    status = Signal(str)
    progress = Signal(int)
    finished_ok = Signal(str)  # emits path to saved transcription
    error = Signal(str)

    def __init__(self, model, audio_path: str, task: str, language: str, output_path: str, device: str, fp16: bool):
        super().__init__()
        self.model = model
        self.audio_path = audio_path
        self.task = task
        self.language = language
        self.output_path = output_path
        self.device = device
        self.fp16 = fp16

    def run(self):
        try:
            self.status.emit("Starting transcription...")
            # Whisper's model.transcribe already handles progress internally but doesn't provide a callback.
            # We'll perform a simple API call and then save result.
            result = self.model.transcribe(self.audio_path, task=self.task, language=(self.language or None))
            text = result.get("text", "")
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status.emit("Transcription finished and saved.")
            self.finished_ok.emit(self.output_path)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"Error during transcription: {e}\n{tb}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(760, 520)

        self.model = None  # loaded whisper model object

        v = QVBoxLayout()

        # Model selection row
        row = QHBoxLayout()
        row.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["large-v3", "large-v3-turbo", "large", "medium", "small"])  # common choices
        row.addWidget(self.model_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        row.addWidget(QLabel("Device:"))
        row.addWidget(self.device_combo)

        self.fp16_cb = QCheckBox("Use fp16 (if supported)")
        row.addWidget(self.fp16_cb)

        v.addLayout(row)

        # Cache / destination
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Model cache dir (optional):"))
        self.cache_edit = QLineEdit( str(Path.home() / ".cache" / "whisper_models") )
        row2.addWidget(self.cache_edit)
        self.cache_btn = QPushButton("Browse")
        self.cache_btn.clicked.connect(self.on_browse_cache)
        row2.addWidget(self.cache_btn)
        v.addLayout(row2)

        # Download / status
        row3 = QHBoxLayout()
        self.download_btn = QPushButton("Download / Load model")
        self.download_btn.clicked.connect(self.on_download)
        row3.addWidget(self.download_btn)

        self.remove_btn = QPushButton("Unload model")
        self.remove_btn.clicked.connect(self.on_unload)
        row3.addWidget(self.remove_btn)

        v.addLayout(row3)

        # Audio file selection and transcription options
        row4 = QHBoxLayout()
        self.audio_btn = QPushButton("Select audio file")
        self.audio_btn.clicked.connect(self.on_select_audio)
        row4.addWidget(self.audio_btn)
        self.audio_path_label = QLabel("No file selected")
        row4.addWidget(self.audio_path_label)
        v.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Task:"))
        self.task_combo = QComboBox()
        self.task_combo.addItems(["transcribe", "translate"])
        row5.addWidget(self.task_combo)
        row5.addWidget(QLabel("Language (optional ISO code):"))
        self.lang_edit = QLineEdit("")
        row5.addWidget(self.lang_edit)
        v.addLayout(row5)

        row6 = QHBoxLayout()
        self.transcribe_btn = QPushButton("Start transcription")
        self.transcribe_btn.clicked.connect(self.on_transcribe)
        row6.addWidget(self.transcribe_btn)
        self.open_out_btn = QPushButton("Open output folder")
        self.open_out_btn.clicked.connect(self.on_open_output)
        row6.addWidget(self.open_out_btn)
        v.addLayout(row6)

        # Status box
        v.addWidget(QLabel("Status:"))
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        v.addWidget(self.status_box)

        self.setLayout(v)

        self.download_worker = None
        self.transcribe_worker = None
        self.selected_audio = None
        self.last_output = None

    def append_status(self, txt: str):
        self.status_box.append(txt)

    def on_browse_cache(self):
        d = QFileDialog.getExistingDirectory(self, "Select cache directory", str(Path.home()))
        if d:
            self.cache_edit.setText(d)

    def on_download(self):
        if self.download_worker and self.download_worker.isRunning():
            self.append_status("Download already in progress.")
            return
        model_name = self.model_combo.currentText()
        device = self.device_combo.currentText()
        fp16 = self.fp16_cb.isChecked()
        cache_dir = self.cache_edit.text().strip() or None
        self.append_status(f"Starting background load for {model_name} on {device}...")
        self.download_worker = DownloadWorker(model_name=model_name, device=device, fp16=fp16, cache_dir=cache_dir)
        self.download_worker.status.connect(self.append_status)
        self.download_worker.error.connect(lambda e: self.append_status("ERROR: " + e))
        self.download_worker.finished_ok.connect(self.on_model_loaded)
        self.download_worker.start()

    def on_unload(self):
        if self.model is None:
            self.append_status("No model loaded.")
            return
        try:
            # delete references and let Python GC free memory
            del self.model
            self.model = None
            import gc
            gc.collect()
            self.append_status("Model unloaded.")
        except Exception as e:
            self.append_status(f"Error unloading model: {e}")

    def on_model_loaded(self, model_obj):
        self.model = model_obj
        self.append_status("Model is ready to use.")

    def on_select_audio(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select audio file", str(Path.home()), "Audio files (*.wav *.mp3 *.m4a *.flac *.ogg);;All files (*)")
        if f:
            self.selected_audio = f
            self.audio_path_label.setText(f)
            self.append_status(f"Selected audio: {f}")

    def on_transcribe(self):
        if self.model is None:
            self.append_status("Model not loaded. Please download/load a model first.")
            return
        if not self.selected_audio:
            self.append_status("No audio selected.")
            return
        if self.transcribe_worker and self.transcribe_worker.isRunning():
            self.append_status("Transcription in progress.")
            return
        task = self.task_combo.currentText()
        language = self.lang_edit.text().strip() or None
        out_dir = Path(self.cache_edit.text() or Path.home())
        out_dir.mkdir(parents=True, exist_ok=True)
        base = Path(self.selected_audio).stem
        out_path = out_dir / f"{base}_transcription.txt"
        self.append_status(f"Starting transcription -> {out_path}")
        self.transcribe_worker = TranscribeWorker(model=self.model, audio_path=self.selected_audio, task=task, language=language or None, output_path=str(out_path), device=self.device_combo.currentText(), fp16=self.fp16_cb.isChecked())
        self.transcribe_worker.status.connect(self.append_status)
        self.transcribe_worker.error.connect(lambda e: self.append_status("ERROR: " + e))
        self.transcribe_worker.finished_ok.connect(self.on_transcription_finished)
        self.transcribe_worker.start()

    def on_transcription_finished(self, out_path):
        self.last_output = out_path
        self.append_status(f"Saved transcription: {out_path}")

    def on_open_output(self):
        if not self.last_output:
            self.append_status("No output saved yet.")
            return
        import subprocess
        folder = str(Path(self.last_output).parent)
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(['explorer', folder])
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            self.append_status(f"Could not open folder: {e}")


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
