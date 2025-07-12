import sys
import random
import string
import subprocess
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPlainTextEdit,
    QPushButton, QMessageBox, QTextEdit
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPainter, QTextFormat,
    QSyntaxHighlighter, QTextCharFormat
)
from PyQt6.QtCore import Qt, QRect, QSize, QThread, pyqtSignal
from win10toast import ToastNotifier
from pygments import lex
from pygments.lexers import LuaLexer
from pygments.token import Token

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class LuaHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.lexer = LuaLexer()

        self.formats = {}

        def format(color, style=''):
            _format = QTextCharFormat()
            _format.setForeground(QColor(color))
            if 'bold' in style:
                _format.setFontWeight(QFont.Weight.Bold)
            if 'italic' in style:
                _format.setFontItalic(True)
            return _format

        self.formats[Token.Keyword] = format("#569CD6", 'bold')
        self.formats[Token.Name.Builtin] = format("#4EC9B0")
        self.formats[Token.Literal.String] = format("#CE9178")
        self.formats[Token.Comment] = format("#6A9955", 'italic')
        self.formats[Token.Literal.Number] = format("#B5CEA8")
        self.formats[Token.Operator] = format("#D4D4D4")
        self.formats[Token.Punctuation] = format("#D4D4D4")
        self.formats[Token.Name.Function] = format("#DCDCAA")
        self.formats[Token.Name] = format("#D4D4D4")
        self.formats[Token.Text] = format("#D4D4D4")

    def highlightBlock(self, text):
        for token, content in lex(text, self.lexer):
            length = len(content)
            fmt = self.formats.get(token, self.formats.get(token.parent, QTextCharFormat()))
            self.setFormat(text.find(content), length, fmt)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")

        self.highlighter = LuaHighlighter(self.document())

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount()))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#2d2d30"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#00ff00"))
                font_metrics = self.fontMetrics()
                painter.drawText(0, top, self.lineNumberArea.width() - 5, font_metrics.height(),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor("#2a2a2a")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

def random_title(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class InjectionThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)

    def run(self):
        logs = [
            "mapping driver",
            "allocating kernel memory",
            "hooking native functions",
            "0x00000000006c",
            "injection succes",
            "bypassing anti-cheat",
            "allocating executable memory",
            "initializing driver communication",
            "finalizing injection",
            "cleaning up",
        ]

        for i, log in enumerate(logs):
            self.log_signal.emit(f"[LOG] {log}")

            # İlk 4 hızlı (0.25 saniye)
            if i < 4:
                time.sleep(0.25)
            # Son sondan 2. hızlı (0.25 saniye)
            elif i == len(logs) - 2:
                time.sleep(0.25)
            # Son log yavaş (1 saniye)
            elif i == len(logs) - 1:
                time.sleep(1)
            # Diğerleri yarı hızda (0.125 saniye)
            else:
                time.sleep(0.125)

        self.finished_signal.emit()

class ExecutorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dxhook")
        self.resize(600, 400)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 255, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(70, 0, 130))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.scriptEdit = CodeEditor()
        layout.addWidget(self.scriptEdit)

        self.injectButton = QPushButton("Inject")
        self.injectButton.setStyleSheet("background-color: purple; color: white; height: 40px; font-weight: bold;")
        self.injectButton.clicked.connect(self.start_inject)
        layout.addWidget(self.injectButton)

        self.executeButton = QPushButton("Execute")
        self.executeButton.setStyleSheet("background-color: mediumorchid; color: white; height: 40px; font-weight: bold;")
        self.executeButton.clicked.connect(self.execute)
        layout.addWidget(self.executeButton)

        self.clearButton = QPushButton("Clear")
        self.clearButton.setStyleSheet("background-color: darkslateblue; color: white; height: 40px; font-weight: bold;")
        self.clearButton.clicked.connect(self.clear)
        layout.addWidget(self.clearButton)

        self.setLayout(layout)

        self.injectThread = None
        self.toaster = ToastNotifier()

    def start_inject(self):
        if self.injectThread is None or not self.injectThread.isRunning():
            self.injectButton.setEnabled(False)
            self.executeButton.setEnabled(False)
            self.clearButton.setEnabled(False)
            self.scriptEdit.clear()

            self.injectThread = InjectionThread()
            self.injectThread.log_signal.connect(self.update_log)
            self.injectThread.finished_signal.connect(self.injection_done)
            self.injectThread.start()

    def update_log(self, log):
        self.scriptEdit.appendPlainText(log)

    def injection_done(self):
        self.injectButton.setEnabled(True)
        self.executeButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.toaster.show_toast("dxhook", "Injected!", duration=5, threaded=True)

    def execute(self):
        script = self.scriptEdit.toPlainText()
        QMessageBox.information(self, "Execute", f"Script executed:\n\n{script}")

    def clear(self):
        self.scriptEdit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExecutorGUI()
    window.show()
    sys.exit(app.exec())