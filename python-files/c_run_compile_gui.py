#!/usr/bin/env python3
"""
C Run & Compile GUI
Single-file PyQt5 application with three-pane layout:
- Left: Code editor (QPlainTextEdit)
- Right: Live Preview / Compiler messages (QPlainTextEdit)
- Bottom: Program output (QPlainTextEdit)

Features:
- Open / Save .c files
- Compile (uses system `gcc`) — compiler messages appear in the Preview pane
- Run (executes compiled binary) — stdout/stderr shown in Output pane
- Compile+Run
- Simple C syntax highlighter (keywords, types, numbers, strings, comments)
- Splitter-based resizable panes

Requirements:
- Python 3.8+
- PyQt5 (`pip install pyqt5`)
- gcc available in PATH (on Windows, use MinGW or WSL; on macOS install Xcode command line tools)

To create an EXE (Windows):
- pip install pyinstaller
- pyinstaller --onefile --noconsole C_Run_Compile_GUI.py

"""

import sys
import os
import tempfile
import subprocess
import shlex
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QFileDialog, QMessageBox, QSplitter, QLabel, QToolBar,
    QAction, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QRegularExpression

# --- Simple C Syntax Highlighter ---
class CSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Prepare formats
        def make_format(color: QColor, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            if bold:
                fmt.setFontWeight(QFont.Bold)
            return fmt

        self.keywordFormat = make_format(QColor("#0000FF"), True)
        self.typeFormat = make_format(QColor("#005500"), True)
        self.numberFormat = make_format(QColor("#AA00AA"))
        self.stringFormat = make_format(QColor("#AA0000"))
        self.commentFormat = make_format(QColor("#888888"))

        keywords = [
            'if','else','while','for','return','break','continue','switch','case','default',
            'sizeof','typedef','struct','union','enum','goto'
        ]
        types = [
            'int','float','double','char','void','long','short','signed','unsigned','bool'
        ]

        self.rules = []
        for kw in keywords:
            pattern = QRegularExpression(r"\b" + kw + r"\b")
            self.rules.append((pattern, self.keywordFormat))
        for t in types:
            pattern = QRegularExpression(r"\b" + t + r"\b")
            self.rules.append((pattern, self.typeFormat))

        # numbers
        self.rules.append((QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"), self.numberFormat))
        # strings
        self.rules.append((QRegularExpression(r'".*?"'), self.stringFormat))
        self.rules.append((QRegularExpression(r"'.'"), self.stringFormat))
        # comments
        self.comment_pattern = QRegularExpression(r"//[^
]*")
        self.block_comment_start = QRegularExpression(r"/\*")
        self.block_comment_end = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # single-line comments
        it = self.comment_pattern.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.commentFormat)

        # multi-line comments
        startIndex = 0
        if self.previousBlockState() != 1:
            match = self.block_comment_start.match(text)
            startIndex = match.capturedStart() if match.hasMatch() else -1
        else:
            startIndex = 0

        while startIndex >= 0:
            match = self.block_comment_end.match(text, startIndex)
            if match.hasMatch():
                end = match.capturedEnd()
                length = end - startIndex
                self.setFormat(startIndex, length, self.commentFormat)
                startIndex = self.block_comment_start.match(text, end).capturedStart() if self.block_comment_start.match(text, end).hasMatch() else -1
                self.setCurrentBlockState(0)
            else:
                # rest of block is comment
                self.setFormat(startIndex, len(text) - startIndex, self.commentFormat)
                self.setCurrentBlockState(1)
                break


# --- Worker thread to run processes without blocking UI ---
class ProcessRunner(QThread):
    outputReady = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, cmd, cwd=None, timeout=None):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.timeout = timeout

    def run(self):
        try:
            # Use subprocess to capture output
            proc = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
            out, _ = proc.communicate(timeout=self.timeout)
            text = out.decode(errors='ignore') if out else ''
            self.outputReady.emit(text)
            self.finished.emit(proc.returncode)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.outputReady.emit('\n[Process timed out]')
            self.finished.emit(-1)
        except Exception as e:
            self.outputReady.emit(f'\n[Error running process]\n{e}')
            self.finished.emit(-1)


# --- Main Application Window ---
class CRunnerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('C Run & Compile - ICT360')
        self.setMinimumSize(900, 600)
        self.current_file = None
        self.binary_path = None

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Toolbar
        toolbar = QToolBar()
        btn_open = QAction('Open', self)
        btn_save = QAction('Save', self)
        btn_save_as = QAction('Save As', self)
        btn_compile = QAction('Compile', self)
        btn_run = QAction('Run', self)
        btn_compile_run = QAction('Compile+Run', self)

        toolbar.addAction(btn_open)
        toolbar.addAction(btn_save)
        toolbar.addAction(btn_save_as)
        toolbar.addSeparator()
        toolbar.addAction(btn_compile)
        toolbar.addAction(btn_run)
        toolbar.addAction(btn_compile_run)

        main_layout.addWidget(toolbar)

        # Splitter: horizontal between left and right; bottom for output
        horizontal_splitter = QSplitter(Qt.Horizontal)

        # Left: Code editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont('Courier', 11))
        self.editor.setPlainText(self.sample_c_program())
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel('Editor'))
        left_layout.addWidget(self.editor)
        left_widget.setLayout(left_layout)

        # Right: Preview / Compiler messages
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont('Courier', 10))
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel('Compiler / Preview'))
        right_layout.addWidget(self.preview)
        right_widget.setLayout(right_layout)

        horizontal_splitter.addWidget(left_widget)
        horizontal_splitter.addWidget(right_widget)
        horizontal_splitter.setStretchFactor(0, 3)
        horizontal_splitter.setStretchFactor(1, 2)

        # Bottom: Output pane
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont('Courier', 10))

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(QLabel('Program Output'))
        bottom_layout.addWidget(self.output)
        bottom_widget.setLayout(bottom_layout)

        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(bottom_widget)
        vertical_splitter.setStretchFactor(0, 8)
        vertical_splitter.setStretchFactor(1, 3)

        main_layout.addWidget(vertical_splitter)

        # Status / gcc path
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('GCC path:'))
        self.gcc_path_edit = QLineEdit('gcc')
        status_layout.addWidget(self.gcc_path_edit)
        self.gcc_check_btn = QPushButton('Check GCC')
        status_layout.addWidget(self.gcc_check_btn)
        main_layout.addLayout(status_layout)

        # Highlighter
        self.highlighter = CSyntaxHighlighter(self.editor.document())

        # Signals
        btn_open.triggered.connect(self.open_file)
        btn_save.triggered.connect(self.save_file)
        btn_save_as.triggered.connect(self.save_file_as)
        btn_compile.triggered.connect(self.compile_code)
        btn_run.triggered.connect(self.run_binary)
        btn_compile_run.triggered.connect(self.compile_and_run)
        self.gcc_check_btn.clicked.connect(self.check_gcc)

        # Auto-compile preview on edits (debounced)
        self.debounce_timer = QTimer()
        self.debounce_timer.setInterval(700)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.update_preview_compile)
        self.editor.textChanged.connect(self.debounce_timer.start)

    def sample_c_program(self):
        return ('#include <stdio.h>\n\n'
                'int main() {\n'
                '    printf("Hello, world!\\n");\n'
                '    return 0;\n'
                '}\n')

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open C file', '', 'C files (*.c);;All files (*)')
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.editor.setPlainText(text)
                self.current_file = path
                self.setWindowTitle(f'C Run & Compile - {os.path.basename(path)}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not open file:\n{e}')

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, 'Saved', f'Saved to {self.current_file}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not save file:\n{e}')

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save C file', 'program.c', 'C files (*.c);;All files (*)')
        if path:
            self.current_file = path
            self.save_file()
            self.setWindowTitle(f'C Run & Compile - {os.path.basename(path)}')

    def check_gcc(self):
        gcc = self.gcc_path_edit.text().strip() or 'gcc'
        try:
            proc = subprocess.Popen([gcc, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate(timeout=3)
            if proc.returncode == 0:
                ver = out.decode().splitlines()[0]
                QMessageBox.information(self, 'GCC Found', ver)
            else:
                QMessageBox.warning(self, 'GCC Not Found', 'GCC returned non-zero exit code')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error checking GCC:\n{e}')

    def write_temp_c(self):
        text = self.editor.toPlainText()
        fd, path = tempfile.mkstemp(suffix='.c', text=True)
        os.close(fd)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return path

    def compile_code(self):
        cpath = self.write_temp_c()
        gcc = self.gcc_path_edit.text().strip() or 'gcc'
        # generate binary in temp dir
        out_bin = tempfile.NamedTemporaryFile(delete=False)
        out_bin.close()
        bin_path = out_bin.name
        cmd = [gcc, cpath, '-o', bin_path]
        self.preview.setPlainText('[Compiling...]')
        self.compile_thread = ProcessRunner(cmd)
        self.compile_thread.outputReady.connect(self.on_compile_output)
        self.compile_thread.finished.connect(lambda rc: setattr(self, 'binary_path', bin_path if rc == 0 else None))
        self.compile_thread.start()

    def on_compile_output(self, text):
        if not text.strip():
            text = '[Compiled successfully — no output]'
        self.preview.setPlainText(text)

    def run_binary(self):
        if not self.binary_path:
            # try compiling the current code first
            self.compile_and_run()
            return
        cmd = [self.binary_path]
        # Ensure executable permission on Unix
        try:
            os.chmod(self.binary_path, 0o755)
        except Exception:
            pass
        self.output.setPlainText('[Running program...]')
        self.run_thread = ProcessRunner(cmd, timeout=10)
        self.run_thread.outputReady.connect(self.on_run_output)
        self.run_thread.finished.connect(lambda rc: None)
        self.run_thread.start()

    def on_run_output(self, text):
        if not text:
            text = '[Program produced no output]'
        self.output.setPlainText(text)

    def compile_and_run(self):
        # compile first, then run on success
        cpath = self.write_temp_c()
        gcc = self.gcc_path_edit.text().strip() or 'gcc'
        out_bin = tempfile.NamedTemporaryFile(delete=False)
        out_bin.close()
        bin_path = out_bin.name
        cmd = [gcc, cpath, '-o', bin_path]
        self.preview.setPlainText('[Compiling (Compile+Run)...]')

        def after_compile(text):
            self.on_compile_output(text)
            # if "error" in text lower -> don't run
            low = text.lower()
            if 'error' in low or 'undefined' in low:
                self.output.setPlainText('[Compilation failed — not running]')
                return
            # run
            self.binary_path = bin_path
            self.run_binary()

        self.compile_thread = ProcessRunner(cmd)
        self.compile_thread.outputReady.connect(after_compile)
        self.compile_thread.start()

    def update_preview_compile(self):
        # lightweight preview: try to run "gcc -fsyntax-only" to show syntax warnings quickly
        cpath = self.write_temp_c()
        gcc = self.gcc_path_edit.text().strip() or 'gcc'
        cmd = [gcc, '-fsyntax-only', cpath]
        self.preview.setPlainText('[Checking syntax...]')
        self.syntax_thread = ProcessRunner(cmd)
        self.syntax_thread.outputReady.connect(self.on_compile_output)
        self.syntax_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CRunnerApp()
    window.show()
    sys.exit(app.exec_())
