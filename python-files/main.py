import os
import re
from PySide6.QtGui import (
    QFont, QColor, QTextCursor, QTextCharFormat, QIcon, QKeySequence, QShortcut,
    QSyntaxHighlighter, QTextFormat
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QInputDialog, QLineEdit, QCompleter,
    QLabel, QListWidget, QTabWidget, QColorDialog, QFormLayout
)
from PySide6.QtCore import QStringListModel, Qt, QTimer, QRegularExpression


# --- Syntax Highlighter for COBOL ---
class CobolHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.formats = {}

        def _format(color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            return fmt

        # Keyword groups and colors
        self.formats['identification'] = _format("#ff7f50", True)  # coral
        self.formats['division'] = _format("#1e90ff", True)  # dodger blue
        self.formats['section'] = _format("#32cd32", True)  # lime green
        self.formats['data'] = _format("#8a2be2", True)  # blue violet
        self.formats['procedure'] = _format("#ffa500", True)  # orange
        self.formats['operator'] = _format("#ff4500", True)  # orange red
        self.formats['number'] = _format("#00ced1")  # dark turquoise
        self.formats['comment'] = _format("#708090")  # slate gray

        self.rules = []

        id_keywords = ["IDENTIFICATION", "PROGRAM-ID", "AUTHOR", "INSTALLATION", "DATE-WRITTEN", "DATE-COMPILED"]
        for kw in id_keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption), self.formats['identification']))

        division_keywords = ["DIVISION"]
        for kw in division_keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption), self.formats['division']))

        section_keywords = ["SECTION", "WORKING-STORAGE", "LOCAL-STORAGE", "LINKAGE", "FILE"]
        for kw in section_keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption), self.formats['section']))

        data_keywords = ["DATA", "PIC", "VALUE", "IS", "TYPE", "LEVEL"]
        for kw in data_keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption), self.formats['data']))

        procedure_keywords = [
            "PROCEDURE", "DIVISION", "PERFORM", "DISPLAY", "STOP", "RUN", "MOVE", "ADD", "SUBTRACT",
            "MULTIPLY", "DIVIDE", "IF", "ELSE", "END-IF", "GO", "TO", "EXIT"
        ]
        for kw in procedure_keywords:
            self.rules.append((QRegularExpression(r"\b" + kw + r"\b", QRegularExpression.CaseInsensitiveOption), self.formats['procedure']))

        operator_keywords = ["+", "-", "*", "/", "=", "<", ">", "<=", ">=", "=="]
        for kw in operator_keywords:
            self.rules.append((QRegularExpression(re.escape(kw)), self.formats['operator']))

        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), self.formats['number']))

        # Comments start with * or *>
        self.rules.append((QRegularExpression(r"\*.*$"), self.formats['comment']))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)


class CodeEditor(QTextEdit):
    def __init__(self, error_list):
        super().__init__()
        self.error_list = error_list

        self.highlighter = CobolHighlighter(self.document())

        self.completer = QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

        self.model = QStringListModel()
        self.completer.setModel(self.model)
        self.last_completed_prefix = ""

        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_words)

        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self._check_for_errors)

    def insert_completion(self, completion):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#add8e6"))  # Light blue
        cursor.insertText(completion, fmt)
        self.setTextCursor(cursor)
        self.completer.popup().hide()
        self.last_completed_prefix = ""

        QTimer.singleShot(1000, self.clear_previous_highlights)

    def textUnderCursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def keyPressEvent(self, event):
        PAIRS = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        char = event.text()

        if self.last_completed_prefix and not self.completer.popup().isVisible():
            self.clear_previous_highlights()

        if char in PAIRS:
            closing = PAIRS[char]
            cursor = self.textCursor()
            cursor.insertText(char + closing)
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return

        key = event.key()

        if key in {Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter}:
            self.clear_previous_highlights()
            self.completer.popup().hide()
            super().keyPressEvent(event)
            return

        if key == Qt.Key_Tab and self.completer.popup().isVisible():
            completion = self.completer.currentCompletion()
            if completion:
                self.insert_completion(completion)
            event.accept()
            return

        super().keyPressEvent(event)

        prefix = self.textUnderCursor()
        if not prefix or " " in prefix:
            self.completer.popup().hide()
            return

        if prefix == self.last_completed_prefix:
            self.completer.popup().hide()
            return

        self.last_completed_prefix = prefix
        self.update_timer.start(100)

        self.completer.setCompletionPrefix(prefix)
        self.completer.popup().setCurrentIndex(
            self.completer.completionModel().index(0, 0)
        )
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                    self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

        self.error_timer.start(300)

    def _update_words(self):
        text = self.toPlainText()
        words = set(re.findall(r'\b\w+\b', text))
        prefix = self.textUnderCursor()
        words.discard(prefix)
        self.model.setStringList(sorted(list(words))[:500])

    def clear_previous_highlights(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        clear_fmt = QTextCharFormat()
        clear_fmt.setBackground(QColor("transparent"))
        cursor.setCharFormat(clear_fmt)

    def _check_for_errors(self):
        code = self.toPlainText()
        self.error_list.clear()

        if "IDENTIFICATION DIVISION." not in code:
            self.error_list.addItem("Missing IDENTIFICATION DIVISION.")
        if "PROGRAM-ID." not in code:
            self.error_list.addItem("Missing PROGRAM-ID.")
        if "END PROGRAM" not in code and "END-PROGRAM" not in code:
            self.error_list.addItem("Missing END PROGRAM.")


class ThemeCustomizer(QWidget):
    PRESET_THEMES = {
        "Light": {
            "bg": "#FFFFFF",
            "text": "#000000",
            "highlight": "#ADD8E6",
            "button_bg": "#E0E0E0",
            "button_text": "#000000",
        },
        "Dark": {
            "bg": "#121212",
            "text": "#E0E0E0",
            "highlight": "#3399FF",
            "button_bg": "#333333",
            "button_text": "#FFFFFF",
        },
        "High Contrast": {
            "bg": "#000000",
            "text": "#FFFFFF",
            "highlight": "#FFFF00",
            "button_bg": "#000000",
            "button_text": "#FFFF00",
        }
    }

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Customize Theme")

        layout = QVBoxLayout()

        # Theme preset buttons
        self.preset_layout = QHBoxLayout()
        for name in self.PRESET_THEMES:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.apply_preset(n))
            self.preset_layout.addWidget(btn)
        layout.addLayout(self.preset_layout)

        # Custom colors inputs
        form = QFormLayout()

        self.bg_color_input = QLineEdit()
        self.bg_color_input.setPlaceholderText("#FFFFFF")
        form.addRow("Background Color:", self.bg_color_input)

        self.text_color_input = QLineEdit()
        self.text_color_input.setPlaceholderText("#000000")
        form.addRow("Text Color:", self.text_color_input)

        self.highlight_color_input = QLineEdit()
        self.highlight_color_input.setPlaceholderText("#ADD8E6")
        form.addRow("Highlight Color:", self.highlight_color_input)

        self.button_bg_color_input = QLineEdit()
        self.button_bg_color_input.setPlaceholderText("#E0E0E0")
        form.addRow("Button Background:", self.button_bg_color_input)

        self.button_text_color_input = QLineEdit()
        self.button_text_color_input.setPlaceholderText("#000000")
        form.addRow("Button Text Color:", self.button_text_color_input)

        # Pickers buttons
        self.color_pickers = {}
        for line_edit in [
            self.bg_color_input, self.text_color_input, self.highlight_color_input,
            self.button_bg_color_input, self.button_text_color_input,
        ]:
            btn = QPushButton("Pick...")
            btn.clicked.connect(lambda _, le=line_edit: self.pick_color(le))
            form.addRow("", btn)
            self.color_pickers[line_edit] = btn

        layout.addLayout(form)

        self.apply_btn = QPushButton("Apply Theme")
        self.apply_btn.clicked.connect(self.apply_theme)
        layout.addWidget(self.apply_btn)

        self.setLayout(layout)

        self.load_current_theme()

    def apply_preset(self, name):
        theme = self.PRESET_THEMES.get(name)
        if theme:
            self.bg_color_input.setText(theme["bg"])
            self.text_color_input.setText(theme["text"])
            self.highlight_color_input.setText(theme["highlight"])
            self.button_bg_color_input.setText(theme["button_bg"])
            self.button_text_color_input.setText(theme["button_text"])
            self.apply_theme()

    def pick_color(self, line_edit):
        color = QColorDialog.getColor()
        if color.isValid():
            line_edit.setText(color.name())

    def load_current_theme(self):
        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                css = f.read()
                colors = {
                    "bg": re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', css),
                    "text": re.search(r'color:\s*(#[0-9a-fA-F]{6})', css),
                    "highlight": re.search(r'QPushButton\s*{[^}]*background-color:\s*(#[0-9a-fA-F]{6})', css),
                    "button_text": re.search(r'QPushButton\s*{[^}]*color:\s*(#[0-9a-fA-F]{6})', css),
                    "button_bg": re.search(r'QPushButton:hover\s*{[^}]*background-color:\s*(#[0-9a-fA-F]{6})', css),
                }
                if colors["bg"]:
                    self.bg_color_input.setText(colors["bg"].group(1))
                if colors["text"]:
                    self.text_color_input.setText(colors["text"].group(1))
                if colors["highlight"]:
                    self.highlight_color_input.setText(colors["highlight"].group(1))
                if colors["button_text"]:
                    self.button_text_color_input.setText(colors["button_text"].group(1))
                if colors["button_bg"]:
                    self.button_bg_color_input.setText(colors["button_bg"].group(1))

    def apply_theme(self):
        bg = self.bg_color_input.text() or "#FFFFFF"
        text = self.text_color_input.text() or "#000000"
        highlight = self.highlight_color_input.text() or "#ADD8E6"
        button_bg = self.button_bg_color_input.text() or "#E0E0E0"
        button_text = self.button_text_color_input.text() or "#000000"

        css = f"""
        QWidget {{
            background-color: {bg};
            color: {text};
        }}
        QTextEdit {{
            background-color: {bg};
            color: {text};
        }}
        QListWidget {{
            background-color: {bg};
            color: {text};
        }}
        QLineEdit {{
            background-color: {bg};
            color: {text};
        }}
        QPushButton {{
            background-color: {button_bg};
            color: {button_text};
            border-radius: 5px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {highlight};
            color: {bg};
        }}
        """

        with open("styles.css", "w", encoding="utf-8") as f:
            f.write(css)

        self.main_window.load_stylesheet()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spinfex COBOL IDE v1.0")

        # Sidebar UI components
        sidebar_layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.perform_search)

        search_icon = QLabel()
        search_icon.setPixmap(QIcon("assets/search.png").pixmap(16, 16))

        search_row = QHBoxLayout()
        search_row.addWidget(search_icon)
        search_row.addWidget(self.search_bar)
        sidebar_layout.addLayout(search_row)

        self.save_button = QPushButton("Save")
        self.save_button.setIcon(QIcon("assets/save.png"))
        self.save_button.clicked.connect(self.save_code)
        sidebar_layout.addWidget(self.save_button)

        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(self.add_new_tab)
        sidebar_layout.addWidget(self.new_tab_button)

        self.new_cobol_button = QPushButton("New COBOL Doc")
        self.new_cobol_button.clicked.connect(self.add_new_cobol_doc)
        sidebar_layout.addWidget(self.new_cobol_button)

        self.run_button = QPushButton("Run")
        self.run_button.setIcon(QIcon("assets/run.png"))
        self.run_button.clicked.connect(self.run_code)
        sidebar_layout.addWidget(self.run_button)

        self.error_list = QListWidget()
        sidebar_layout.addWidget(QLabel("Errors:"))
        sidebar_layout.addWidget(self.error_list)
        sidebar_layout.addStretch()

        sidebar = QWidget()
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(200)

        # Tabs widget for editors + theme
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)

        self.editors = {}

        # Add initial editor tab
        self.add_new_tab()

        # Add Theme tab at the end (non-closable)
        self.theme_tab = ThemeCustomizer(self)
        self.tabs.addTab(self.theme_tab, "Customize Theme")

        # Output console
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setFixedHeight(120)

        # Run shortcut F5
        run_shortcut = QShortcut(QKeySequence("F5"), self)
        run_shortcut.activated.connect(self.run_code)

        # Main layout
        main_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(sidebar)
        h_layout.addWidget(self.tabs)

        main_layout.addLayout(h_layout)
        main_layout.addWidget(QLabel("Output:"))
        main_layout.addWidget(self.output_console)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_stylesheet()

    def on_tab_close_requested(self, index):
        # Prevent closing the theme tab (last tab)
        if index == self.tabs.count() - 1:
            # Optionally show a message box warning here
            return
        # Remove editor tab normally
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget in self.editors:
            del self.editors[widget]

    def add_new_tab(self, filename=None, content=""):
        editor = CodeEditor(self.error_list)
        if content:
            editor.setPlainText(content)
        # Insert before Theme tab (which is last)
        index = self.tabs.count() - 1
        self.tabs.insertTab(index, editor, filename or "Untitled")
        self.tabs.setCurrentIndex(index)
        self.editors[editor] = filename or "Untitled"

    def add_new_cobol_doc(self):
        cobol_template = """IDENTIFICATION DIVISION.
PROGRAM-ID. MyProgram.

ENVIRONMENT DIVISION.

DATA DIVISION.
WORKING-STORAGE SECTION.

PROCEDURE DIVISION.
    DISPLAY "Hello, COBOL World!".
    STOP RUN.
"""
        self.add_new_tab(filename="NewCOBOL.cbl", content=cobol_template)

    def current_editor(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def save_code(self):
        editor = self.current_editor()
        if not editor:
            return
        text, ok = QInputDialog.getText(self, "Save File", "Enter filename:")
        if ok and text:
            if not text.endswith(".txt") and not text.endswith(".cbl"):
                text += ".cbl"
            with open(text, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            index = self.tabs.currentIndex()
            self.tabs.setTabText(index, os.path.basename(text))
            self.editors[editor] = text

    def run_code(self):
        editor = self.current_editor()
        if not editor:
            self.output_console.setText("No editor tab selected to run.")
            return
        code = editor.toPlainText()
        with open("temp.cbl", "w", encoding="utf-8") as f:
            f.write(code)
        try:
            # Run COBOL compile & execute (assuming environment setup)
            result = os.popen("cobc -x temp.cbl && ./temp").read()
        except Exception as e:
            result = f"Error running COBOL code: {e}"
        self.output_console.setText(result)

    def perform_search(self, text):
        editor = self.current_editor()
        if not editor:
            return

        # Clear previous highlights
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        clear_fmt = QTextCharFormat()
        clear_fmt.setBackground(QColor("transparent"))
        cursor.setCharFormat(clear_fmt)
        cursor.endEditBlock()

        if not text:
            return

        fmt = QTextCharFormat()
        fmt.setBackground(self.palette().highlight())
        doc = editor.document()
        pos = 0
        while True:
            cursor = doc.find(text, pos, QTextDocument.FindCaseSensitively)
            if cursor.isNull():
                break
            cursor.mergeCharFormat(fmt)
            pos = cursor.position()

    def load_stylesheet(self):
        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
