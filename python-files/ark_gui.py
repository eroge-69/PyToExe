import sys
import subprocess
import pyttsx3
import speech_recognition as sr
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextBrowser, QLabel, QFrame,
    QListWidget, QListWidgetItem, QStackedWidget, QFileDialog,
    QTextEdit, QSplitter,
        QMenu, QInputDialog, QMessageBox, QCheckBox, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QTextCursor, QIcon, QPixmap
import sqlite3, threading, subprocess

engine = pyttsx3.init()

class ChatThread(QThread):
    result = pyqtSignal(str)
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            text = self.prompt.lower()
            if text.startswith("create "):
                base, name = self.extract_path(text.replace("create ", "", 1).strip())
                filename = os.path.join(base, name)
                open(filename, "w").close()
                response = f"Created file: {filename}"
            elif text.startswith("delete "):
                base, name = self.extract_path(text.replace("delete ", "", 1).strip())
                filename = os.path.join(base, name)
                os.remove(filename)
                response = f"Deleted file: {filename}"
            else:
                proc = subprocess.run(
                    ["ollama", "run", "llama2", self.prompt],
                    capture_output=True, text=True
                )
                response = proc.stdout.strip() or proc.stderr.strip()
        except Exception as e:
            response = f"Error: {e}"
        self.result.emit(response)

class SpeakThread(QThread):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        try:
            engine.say(self.text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")

class ListenThread(QThread):
    result = pyqtSignal(str)

    def run(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio).lower()
            except Exception as e:
                text = f"Error during voice recognition: {str(e)}"
        self.result.emit(text)

class ArkGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ark | Local AI Assistant")
        # NEW: load logo.png from images folder as app icon
        logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png.png")
        self.setWindowIcon(QIcon(logo_path))

        # NEW: ensure plugins attribute exists before building UI
        try:
            from plugins import PluginManager
            self.plugins = PluginManager()
        except ImportError:
            # Create fallback plugin manager if import fails
            class PluginManager:
                def __init__(self):
                    self.plugins = {}
            self.plugins = PluginManager()

        # existing settings init
        # NEW: use QSettings for persistence
        self.settings = QSettings("ArkApp", "UserPrefs")
        # dropped Memory/NLP/Plugin managers—using built-in parsing only
        self.setWindowTitle("Ark | Local AI Assistant")
        self.setWindowIcon(QIcon("robot.png"))
        self.setStyleSheet("""
            QWidget {
                background-color: #0e0e0e;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 2px solid #444;
                padding: 8px;
                border-radius: 8px;
                color: #fff;
            }
            QPushButton {
                background-color: #00b894;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00cec9;
            }
            QTextBrowser, QListWidget {
                background-color: #1e1e1e;
                border: none;
                padding: 12px;
                border-radius: 8px;
            }
            QLabel#Title {
                font-size: 24px;
                font-weight: bold;
                color: #00b894;
                padding-bottom: 10px;
            }
        """)
        # prepare settings storage
        # self.settings = QSettings("ArkApp", "UserPrefs")
        # capture original dark & light styles
        self.dark_css = self.styleSheet()
        self.light_css = """
            QWidget { background: #f0f0f0; color: #202020; font-family: 'Segoe UI'; }
            QLineEdit, QTextBrowser, QListWidget { background: #ffffff; }
            QPushButton { background: #0078d4; color: #fff; }
            QPushButton:hover { background: #005a9e; }
            QLabel#Title { color: #0078d4; }
        """
        self.setup_ui()
        # after UI exists, load & apply last‐used prefs
        self.load_user_settings()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(140)
        self.sidebar.addItem("💬 Chat")
        self.sidebar.addItem("📁 Files")
        self.sidebar.addItem("⚙️ Settings")
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #121212;
                color: white;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #00b894;
            }
        """)

        self.chat_view = self.build_chat_view()
        self.files_view = self.build_files_view()
        self.settings_view = self.build_settings_view()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.chat_view)
        self.stack.addWidget(self.files_view)
        self.stack.addWidget(self.settings_view)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stack)
        splitter.setSizes([150, 650])

        main_layout.addWidget(splitter)

    def build_chat_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.title = QLabel("Ark: Your AI Assistant")
        self.title.setObjectName("Title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.output = QTextBrowser()
        self.output.setPlaceholderText("Ark is ready. Start typing or speak.")

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a command or question...")
        self.input.returnPressed.connect(self.handle_input)

        self.speak_btn = QPushButton("🎤")
        self.speak_btn.setFixedWidth(40)
        self.speak_btn.clicked.connect(self.handle_voice)

        # add clear and save buttons
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_chat)
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_chat)

        input_row.addWidget(self.input)
        input_row.addWidget(self.speak_btn)
        input_row.addWidget(self.clear_btn)
        input_row.addWidget(self.save_btn)

        self.status = QLabel("Status: Ready")
        self.status.setStyleSheet("color: #bbb; font-size: 12px;")

        layout.addWidget(self.title)
        layout.addWidget(self.output)
        layout.addLayout(input_row)
        layout.addWidget(self.status)

        return widget

    def build_files_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("📁 File Browser")
        label.setObjectName("Title")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.file_browser = QListWidget()
        self.load_files(Path.home() / "Documents")
        # enable context menu and double-click to open
        self.file_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_browser.customContextMenuRequested.connect(self.show_file_context_menu)
        self.file_browser.itemDoubleClicked.connect(self.open_file)
        self.file_browser.setAcceptDrops(True)
        self.file_browser.dragEnterEvent = self._on_drag_enter
        self.file_browser.dropEvent      = self._on_drop

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(lambda: self.load_files(self.current_folder))

        open_folder_btn = QPushButton("📂 Open Folder")
        open_folder_btn.clicked.connect(self.select_folder)

        btn_row = QHBoxLayout()
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(open_folder_btn)

        layout.addWidget(label)
        layout.addLayout(btn_row)
        layout.addWidget(self.file_browser)

        # NEW: preview area
        self.preview = QLabel("Drop a file here to preview")
        self.preview.setFixedHeight(200)
        layout.addWidget(self.preview)

        return widget

    # NEW:
    def _on_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _on_drop(self, event):
        url = event.mimeData().urls()[0].toLocalFile()
        ext = Path(url).suffix.lower()
        if ext in (".png",".jpg",".bmp"):
            pix = QPixmap(url).scaledToHeight(180, Qt.SmoothTransformation)
            self.preview.setPixmap(pix)
        elif ext == ".txt":
            self.preview.setText(Path(url).read_text(encoding="utf-8"))
        else:
            self.preview.setText(f"No preview for *{ext}*")

    def build_settings_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("⚙️ Settings")
        label.setObjectName("Title")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dark/Light Mode
        self.theme_checkbox = QCheckBox("Enable Dark Mode")
        self.theme_checkbox.stateChanged.connect(self.toggle_theme)

        # Voice feedback on/off
        self.voice_checkbox = QCheckBox("Enable Voice Responses")
        self.voice_checkbox.stateChanged.connect(
            lambda s: self.settings.setValue("voice_enabled", bool(s))
        )

        # Voice rate slider
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(50, 300)
        self.rate_slider.valueChanged.connect(self.change_voice_rate)
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Voice Rate"))
        rate_layout.addWidget(self.rate_slider)

        # Chat font size picker
        self.font_combo = QComboBox()
        for size in (12, 14, 16, 18, 20, 22):
            self.font_combo.addItem(f"{size}px", size)
        self.font_combo.currentIndexChanged.connect(self.change_font_size)

        # NEW: Custom Persona & Voice
        self.voice_chk = QCheckBox("Enable Voice Responses")
        # load a bool, default True
        enabled = self.settings.value("voice_on", True, type=bool)
        self.voice_chk.setChecked(enabled)
        self.voice_chk.stateChanged.connect(
            lambda s: self.settings.setValue("voice_on", bool(s))
        )

        self.voice_combo = QComboBox()
        for v in engine.getProperty("voices"):
            self.voice_combo.addItem(v.name, v.id)
        vid = self.settings.value("voice_id", None)
        if vid:
            idx = self.voice_combo.findData(vid)
            if idx >= 0:
                self.voice_combo.setCurrentIndex(idx)
        self.voice_combo.currentIndexChanged.connect(
            lambda i: (
                engine.setProperty("voice", self.voice_combo.itemData(i)),
                self.settings.setValue("voice_id", self.voice_combo.itemData(i))
            )
        )
        layout.addWidget(self.voice_chk)
        layout.addWidget(QLabel("Choose Voice"))
        layout.addWidget(self.voice_combo)

        # NEW: AI Personality
        layout.addWidget(QLabel("🤖 AI Personality"))
        self.personality_edit = QTextEdit()
        self.personality_edit.setPlaceholderText(
            "e.g. ‘You are a witty, encouraging coding tutor.’"
        )
        self.personality_edit.setFixedHeight(60)
        # load saved personality
        saved = self.settings.value("ai_personality", "")
        self.personality_edit.setPlainText(saved)
        # save on change
        self.personality_edit.textChanged.connect(
            lambda: self.settings.setValue(
                "ai_personality", self.personality_edit.toPlainText().strip()
            )
        )
        layout.addWidget(self.personality_edit)

        # NEW: Favorite folder
        fav_btn = QPushButton("★ Set Favorite Folder")
        fav_btn.clicked.connect(self._set_favorite_folder)
        layout.addWidget(fav_btn)

        # NEW: Registered Plugins
        layout.addWidget(QLabel("Plugins"))
        self.plugin_list = QListWidget()
        for name in self.plugins.plugins:
            self.plugin_list.addItem(name)
        layout.addWidget(self.plugin_list)
        return widget

    # NEW helper
    def _set_favorite_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Favorite")
        if folder:
            self.settings.setValue("fav_folder", folder)

    def load_user_settings(self):
        # Theme
        dark = self.settings.value("dark_mode", True, bool)
        self.theme_checkbox.setChecked(dark)
        self.apply_theme(dark)

        # Voice
        voice = self.settings.value("voice_enabled", True, bool)
        self.voice_checkbox.setChecked(voice)

        # Voice rate
        rate = self.settings.value("voice_rate", engine.getProperty("rate"), int)
        engine.setProperty("rate", rate)
        self.rate_slider.setValue(rate)

        # Chat font size
        size = self.settings.value("chat_font_size", self.output.font().pointSize(), int)
        idx = self.font_combo.findData(size)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        self.output.setStyleSheet(f"font-size: {size}px;")

    def toggle_theme(self, state):
        dark = bool(state)
        self.settings.setValue("dark_mode", dark)
        self.apply_theme(dark)

    def apply_theme(self, dark: bool):
        self.setStyleSheet(self.dark_css if dark else self.light_css)

    def speak(self, text):
        self.speak_thread = SpeakThread(text)
        self.speak_thread.start()

    def handle_input(self):
        raw = self.input.text().strip()
        if not raw:
            return
        self.input.clear()
        self.display_message("You", raw)
        self.status.setText("Status: Ark is thinking...")

        # NEW: build full prompt with personality
        persona = self.settings.value("ai_personality", "")
        prompt = f"{persona}\n{raw}" if persona else raw

        self.chat_thread = ChatThread(prompt)
        self.chat_thread.result.connect(self.handle_response)
        self.chat_thread.start()

    def handle_voice(self):
        self.display_message("System", "🎙️ Listening...")
        self.status.setText("Status: Listening for command...")
        self.listen_thread = ListenThread()
        self.listen_thread.result.connect(self.process_voice_command)
        self.listen_thread.start()

    def process_voice_command(self, command):
        self.display_message("You (Voice)", command)
        self.status.setText("Status: Ark is thinking...")
        self.chat_thread = ChatThread(command)
        self.chat_thread.result.connect(self.handle_response)
        self.chat_thread.start()

    def handle_response(self, response):
        self.display_message("Ark", response)
        if getattr(self, "voice_on", True):
            self.speak(response)
        self.status.setText("Status: Ready")

    def display_message(self, sender, message):
        self.output.append(f"<b>{sender}:</b> {message}")
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def load_files(self, path):
        self.file_browser.clear()
        try:
            files = os.listdir(path)
            for f in files:
                self.file_browser.addItem(QListWidgetItem(f))
            self.current_folder = path
        except Exception as e:
            self.file_browser.addItem(f"❌ Error: {e}")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            self.load_files(folder)

    # context menu handlers
    def show_file_context_menu(self, pos):
        menu = QMenu()
        rename_act = menu.addAction("Rename")
        delete_act = menu.addAction("Delete")
        action = menu.exec(self.file_browser.mapToGlobal(pos))
        item = self.file_browser.itemAt(pos)
        if not item:
            return
        name = item.text()
        if action == rename_act:
            self.rename_file(name)
        elif action == delete_act:
            self.delete_file(name)

    def open_file(self, item):
        try:
            path = os.path.join(self.current_folder, item.text())
            os.startfile(path)
        except Exception as e:
            self.display_message("System", f"Open failed: {e}")

    def rename_file(self, filename):
        new_name, ok = QInputDialog.getText(self, "Rename File", "New name:", text=filename)
        if ok and new_name:
            old = os.path.join(self.current_folder, filename)
            new = os.path.join(self.current_folder, new_name)
            os.rename(old, new)
            self.load_files(self.current_folder)

    def delete_file(self, filename):
        reply = QMessageBox.question(
            self, "Delete File", f"Delete {filename}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            os.remove(os.path.join(self.current_folder, filename))
            self.load_files(self.current_folder)

    # chat utilities
    def clear_chat(self):
        self.output.clear()

    def save_chat(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Chat History",
            str(Path.home() / "chat_history.txt"),
            "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output.toPlainText())
            self.status.setText(f"Status: Saved to {path}")

    def change_voice_rate(self, value):
        engine.setProperty("rate", value)
        self.settings.setValue("voice_rate", value)

    def change_font_size(self, index):
        size = self.font_combo.itemData(index)
        self.output.setStyleSheet(f"font-size: {size}px;")
        self.settings.setValue("chat_font_size", size)

    def edit_code_with_openai(self, original: str, task: str, lang: str) -> str:
        prompt = (
            f"You are a helpful coding assistant. Edit this {lang} code "
            f"as per the task, and return only the full updated code:\n\n"
            f"Task: {task}\n\nOriginal code:\n{original}"
        )
        try:
            proc = subprocess.run(
                ["ollama", "run", "llama2", prompt],
                capture_output=True, text=True, check=True
            )
            return proc.stdout.strip() or original
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Edit Error", f"Ollama failed: {e}")
            return original

    def run_chatbot_response(self):
        question = self.chat_entry.get()
        if not question.strip():
            return

        try:
            self.log(f"💬 You: {question}", level="CHAT")
            proc = subprocess.run(
                ["ollama", "run", "llama2", question],
                capture_output=True, text=True, check=True
            )
            answer = proc.stdout.strip()
            self.log(f"🤖 Bot: {answer}", level="CHAT")
        except Exception as e:
            self.log(f"Chatbot error: {e}", level="ERROR")

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    window = ArkGUI()
    window.resize(900,600)
    window.show()               # ← make sure you call show()
    sys.exit(app.exec())        # ← this starts the Qt event-loop