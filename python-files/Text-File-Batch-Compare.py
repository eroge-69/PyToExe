#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Text-File-Batch-Compare.py:
Compares text files across two directories (and sub-directories)
and determines whether they are identical or not.

---------------------------------------------
                CHANGELOG
---------------------------------------------
Version: 1.00

Notes:
- Standard 'Text-File-Batch-Compare.py:' file
---------------------------------------------

"""

import sys
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QDialog, QListWidget, QTextEdit, QListWidgetItem
)

from PyQt5.QtCore import Qt
class FileCompareDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recursive File Comparator")
        self.setMinimumSize(1000, 700)
        self.dir_a = ""
        self.dir_b = ""
        self.files_a = {}
        self.files_b = {}
        self.theme = "Normal"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Folder A
        folder_a_layout = QHBoxLayout()
        self.txt_folder_a = QLineEdit()
        #self.txt_folder_a.setReadOnly(True)
        btn_browse_a = QPushButton("Open Folder A")
        btn_browse_a.clicked.connect(self.browse_folder_a)
        folder_a_layout.addWidget(QLabel("Folder A:"))
        folder_a_layout.addWidget(self.txt_folder_a)
        folder_a_layout.addWidget(btn_browse_a)

        # Folder B
        folder_b_layout = QHBoxLayout()
        self.txt_folder_b = QLineEdit()
        #self.txt_folder_b.setReadOnly(True)
        btn_browse_b = QPushButton("Open Folder B")
        btn_browse_b.clicked.connect(self.browse_folder_b)
        folder_b_layout.addWidget(QLabel("Folder B:"))
        folder_b_layout.addWidget(self.txt_folder_b)
        folder_b_layout.addWidget(btn_browse_b)

        # Compare button
        self.btn_compare = QPushButton("Compare Files")
        self.btn_compare.clicked.connect(self.compare_files)

        # Results list
        self.result_list = QListWidget()
        self.result_list.clicked.connect(lambda index: self.load_file_diff(self.result_list.item(index.row())))
        self.result_list.itemDoubleClicked.connect(self.launch_text_compare)

        # Side-by-side viewer + copy buttons
        viewer_layout = QHBoxLayout()

        # Left side (Folder A)
        left_layout = QVBoxLayout()
        self.viewer_a = QTextEdit()
        self.viewer_a.setReadOnly(True)
        btn_copy_a = QPushButton("Copy Left")
        btn_copy_a.clicked.connect(lambda: self.copy_to_clipboard(self.viewer_a))
        left_layout.addWidget(self.viewer_a)
        left_layout.addWidget(btn_copy_a)

        # Right side (Folder B)
        right_layout = QVBoxLayout()
        self.viewer_b = QTextEdit()
        self.viewer_b.setReadOnly(True)
        btn_copy_b = QPushButton("Copy Right")
        btn_copy_b.clicked.connect(lambda: self.copy_to_clipboard(self.viewer_b))
        right_layout.addWidget(self.viewer_b)
        right_layout.addWidget(btn_copy_b)

        viewer_layout.addLayout(left_layout)
        viewer_layout.addLayout(right_layout)

        layout.addLayout(folder_a_layout)
        layout.addLayout(folder_b_layout)
        layout.addWidget(self.btn_compare)
        layout.addWidget(QLabel("Double-click a differing file to view:"))
        layout.addWidget(self.result_list)
        layout.addLayout(viewer_layout)

        btn_text_compare = QPushButton("Text Compare")
        btn_text_compare.clicked.connect(self.launch_text_compare)
        layout.addWidget(btn_text_compare)

        self.theme_dropdown = QtWidgets.QComboBox()
        self.theme_dropdown.addItems(["Normal", "Dark", "Futuristic"])
        self.theme_dropdown.setCurrentText(self.theme)
        self.theme_dropdown.setFixedSize(100, 20)
        self.theme_dropdown.currentTextChanged.connect(self.apply_theme)

        theme_layout = QtWidgets.QHBoxLayout()
        theme_label = QtWidgets.QLabel("Theme:")
        theme_label.setFixedHeight(20)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_dropdown)
        theme_layout.addStretch()

        layout.addLayout(theme_layout)

        self.setLayout(layout)

    def apply_theme(self, selected_theme):
        self.theme = selected_theme
        app = QtWidgets.QApplication.instance()
        app.setStyleSheet(self.get_stylesheet())


    def get_stylesheet(self):
        if self.theme == "Futuristic":
            return """
            QWidget {
                background-color: #1e1e1e;
                color: #00ffcc;
                font-family: "JetBrains Mono", "Hack", "Share Tech Mono", "Consolas", monospace;
                font-size: 8pt;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #121212;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                selection-background-color: #004d4d;
                selection-color: #00ffff;
            }
            QPushButton {
                background-color: #121212;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #004040;
            }
            QPushButton:pressed {
                background-color: #002222;
            }
            QLabel {
                color: #00ffaa;
                font-weight: bold;
            }
            QListWidget::item:selected {
                background-color: #003333;
                color: #00ffff;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #1e1e1e;
                border: none;
                width: 8px;
            }
            QScrollBar::handle {
                background-color: #00ffcc;
                border-radius: 4px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                height: 0px;
            }
            """
        elif self.theme == "Dark":
            return """
            QWidget {
                background-color: #0e0e0e;
                color: #bbbbbb;
                font-family: Consolas, monospace;
                font-size: 8pt;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #101010;
                color: #dddddd;
                border: 1px solid #444444;
                selection-background-color: #222222;
                selection-color: #ffffff;
            }
            QPushButton {
                background-color: #101010;
                color: #bbbbbb;
                border: 1px solid #444444;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
            QLabel {
                color: #bbbbbb;
            }
            QListWidget::item:selected {
                background-color: #303030;
                color: #ffffff;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #0e0e0e;
                border: none;
                width: 8px;
            }
            QScrollBar::handle {
                background-color: #666666;
                border-radius: 4px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                height: 0px;
            }
            """
        else:  # Normal
            return """
            QWidget {
                background-color: #f0f0f0;
                color: #000000;
                font-family: Consolas, monospace;
                font-size: 8pt;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #aaaaaa;
                selection-background-color: #cceeff;
                selection-color: #000000;
            }
            QPushButton {
                background-color: #eeeeee;
                color: #000000;
                border: 1px solid #999999;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
            QLabel {
                color: #000000;
            }
            QListWidget::item:selected {
                background-color: #cceeff;
                color: #000000;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #f0f0f0;
                border: none;
                width: 8px;
            }
            QScrollBar::handle {
                background-color: #999999;
                border-radius: 4px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                height: 0px;
            }
            """
        
    def get_diff_colors(self):
        if self.theme == "Futuristic":
            return "#665500", "#444400"  # Amber, olive
        elif self.theme == "Dark":
            return "#553311", "#224422"  # Deeper amber, dark green
        else:  # Normal
            return "#ffee99", "#ccffcc"  # Yellow highlight, light green


    def launch_text_compare(self):
        if not hasattr(self, 'last_diff_key'):
            return

        rel_path = self.last_diff_key
        path_a = self.files_a.get(rel_path)
        path_b = self.files_b.get(rel_path)

        text_a = self.read_text_file(path_a)
        text_b = self.read_text_file(path_b)

        highlight_replace, highlight_insert = self.get_diff_colors()
        dlg = DiffDialog(text_a, text_b, title=f"Compare: {rel_path}",
                        replace_color=highlight_replace,
                        insert_color=highlight_insert)
        dlg.exec_()


    def copy_to_clipboard(self, text_edit):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text_edit.toPlainText())


    def browse_folder_a(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder A")
        if path:
            self.dir_a = path
            self.txt_folder_a.setText(path)

    def browse_folder_b(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder B")
        if path:
            self.dir_b = path
            self.txt_folder_b.setText(path)

    def compare_files(self):
        self.dir_a = self.txt_folder_a.text().strip()
        self.dir_b = self.txt_folder_b.text().strip()

        if not os.path.isdir(self.dir_a) or not os.path.isdir(self.dir_b):
            self.result_list.clear()
            self.result_list.addItem("Please select both *valid* folders before comparing.")
            return

        self.files_a = self.get_all_files(self.dir_a)
        self.files_b = self.get_all_files(self.dir_b)
        all_keys = sorted(set(self.files_a.keys()) | set(self.files_b.keys()))

        self.result_list.clear()

        for rel_path in all_keys:
            path_a = self.files_a.get(rel_path)
            path_b = self.files_b.get(rel_path)

            if path_a and path_b:
                if self.files_equal(path_a, path_b):
                    item = QListWidgetItem(f"[=] {rel_path}")
                    item.setData(1000, rel_path)
                    self.result_list.addItem(item)

                else:
                    item = QListWidgetItem(f"[≠] {rel_path}")
                    item.setData(1000, rel_path)  # Store the key for lookup
                    self.result_list.addItem(item)
            elif path_a:
                self.result_list.addItem(f"[A] {rel_path} (only in Folder A)")
            elif path_b:
                self.result_list.addItem(f"[B] {rel_path} (only in Folder B)")

    def get_all_files(self, base_dir):
        file_map = {}
        for root, _, files in os.walk(base_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, base_dir).replace("\\", "/")
                file_map[rel_path] = abs_path
        return file_map

    def files_equal(self, path1, path2):
        try:
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                return f1.read() == f2.read()
        except Exception:
            return False

    def load_file_diff(self, item):
        text = item.text()
        if text.startswith("[=]") or text.startswith("[≠]"):
            rel_path = item.data(1000) or text[4:].strip()
            self.last_diff_key = rel_path  # Set regardless of tag

            path_a = self.files_a.get(rel_path)
            path_b = self.files_b.get(rel_path)

            text_a = self.read_text_file(path_a)
            text_b = self.read_text_file(path_b)

            self.viewer_a.setPlainText(text_a)
            self.viewer_b.setPlainText(text_b)



    def read_text_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            return f"Could not read file: {e}"

class DiffDialog(QDialog):
    def __init__(self, text1, text2, title="Text Comparison",
                 replace_color="#665500", insert_color="#444400"):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(1200, 700)

        self.highlight_replace = replace_color
        self.highlight_insert = insert_color
        self.line_numbers_enabled = True  # New toggle state

        layout = QHBoxLayout()

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        font = self.status_label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.status_label.setFont(font)


        self.left_edit = QTextEdit()
        self.left_edit.setReadOnly(True)
        self.left_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.left_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.right_edit = QTextEdit()
        self.right_edit.setReadOnly(True)
        self.right_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.right_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        layout.addWidget(self.left_edit)
        layout.addWidget(self.right_edit)

        # Bottom button layout
        bottom_buttons = QHBoxLayout()

        self.wrap_button = QPushButton("Toggle Word Wrap")
        self.wrap_button.setCheckable(True)
        self.wrap_button.setChecked(False)
        self.wrap_button.setFixedSize(150, 25)
        self.wrap_button.toggled.connect(self.toggle_word_wrap)

        self.line_button = QPushButton("Toggle Line Numbers")
        self.line_button.setFixedSize(150, 25)
        self.line_button.clicked.connect(self.toggle_line_numbers)

        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.wrap_button)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.line_button)
        bottom_buttons.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)  # Add label at top
        main_layout.addLayout(layout)
        main_layout.addLayout(bottom_buttons)
        self.setLayout(main_layout)

        # Scroll synchronization (vertical only)
        self.left_edit.verticalScrollBar().valueChanged.connect(
            self.right_edit.verticalScrollBar().setValue
        )
        self.right_edit.verticalScrollBar().valueChanged.connect(
            self.left_edit.verticalScrollBar().setValue
        )

        self.show_diff(text1, text2)

    def toggle_word_wrap(self, enabled):
        mode = QTextEdit.WidgetWidth if enabled else QTextEdit.NoWrap
        self.left_edit.setLineWrapMode(mode)
        self.right_edit.setLineWrapMode(mode)

    def toggle_line_numbers(self):
        # Save current scroll positions
        left_scroll = self.left_edit.verticalScrollBar().value()
        right_scroll = self.right_edit.verticalScrollBar().value()

        self.line_numbers_enabled = not self.line_numbers_enabled
        self.show_diff(self._text1, self._text2)

        # Restore scroll positions
        QtCore.QTimer.singleShot(0, lambda: self.left_edit.verticalScrollBar().setValue(left_scroll))
        QtCore.QTimer.singleShot(0, lambda: self.right_edit.verticalScrollBar().setValue(right_scroll))


    def escape(self, s):
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace(" ", "&nbsp;")       # preserve spaces
            .replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")  # preserve tabs (4 spaces)
        )


    def show_diff(self, text1, text2):
        import difflib
        import re

        self._text1 = text1  # Store for refresh
        self._text2 = text2

        lines1 = text1.split('\n')
        lines2 = text2.split('\n')

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        left_result = []
        right_result = []

        highlight_replace = self.highlight_replace
        highlight_insert = self.highlight_insert

        def add_line_numbers(result_lines, source_lines):
            numbered_lines = []
            source_index = 0
            line_count = len(source_lines)
            pad_width = len(str(line_count))

            def strip_tags(html):
                return re.sub(r'<[^>]+>', '', html).strip()

            for line in result_lines:
                if self.line_numbers_enabled:
                    if source_index < len(source_lines):
                        expected_line = source_lines[source_index].strip()
                        actual_line = strip_tags(line)
                        if actual_line == expected_line:
                            line_number = f"<span style='color:#888888;'>[{source_index + 1:0{pad_width}d}]</span> "
                            numbered_lines.append(line_number + line)
                            source_index += 1
                        elif actual_line == "":
                            numbered_lines.append(line)
                        else:
                            line_number = f"<span style='color:#888888;'>[{source_index + 1:0{pad_width}d}]</span> "
                            numbered_lines.append(line_number + line)
                            source_index += 1
                    else:
                        numbered_lines.append(line)
                else:
                    numbered_lines.append(line)
                    if source_index < len(source_lines):
                        source_index += 1

            return numbered_lines

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            left_chunk = lines1[i1:i2]
            right_chunk = lines2[j1:j2]

            if tag == 'equal':
                for l, r in zip(left_chunk, right_chunk):
                    left_result.append(self.escape(l))
                    right_result.append(self.escape(r))

            elif tag == 'replace':
                maxlen = max(len(left_chunk), len(right_chunk))
                for i in range(maxlen):
                    left_line = left_chunk[i] if i < len(left_chunk) else ""
                    right_line = right_chunk[i] if i < len(right_chunk) else ""
                    left_result.append(
                        f"<span style='background-color:{highlight_replace}'>{self.escape(left_line)}</span>"
                    )
                    right_result.append(
                        f"<span style='background-color:{highlight_replace}'>{self.escape(right_line)}</span>"
                    )

            elif tag == 'delete':
                for l in left_chunk:
                    left_result.append(
                        f"<span style='background-color:{highlight_replace}'>{self.escape(l)}</span>"
                    )
                    right_result.append("")

            elif tag == 'insert':
                for r in right_chunk:
                    left_result.append("")
                    right_result.append(
                        f"<span style='background-color:{highlight_insert}'>{self.escape(r)}</span>"
                    )

        # Preserve scroll position
        scroll_left = self.left_edit.verticalScrollBar().value()
        scroll_right = self.right_edit.verticalScrollBar().value()

        self.left_edit.setHtml("<br>".join(add_line_numbers(left_result, lines1)))
        self.right_edit.setHtml("<br>".join(add_line_numbers(right_result, lines2)))

        # Restore scroll position
        self.left_edit.verticalScrollBar().setValue(scroll_left)
        self.right_edit.verticalScrollBar().setValue(scroll_right)
        
        if text1 == text2:
            self.status_label.setText("Identical Files")
            self.status_label.setStyleSheet("""
                background-color: green;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;
                border-radius: 4px;
            """)
        else:
            self.status_label.setText("Differing Files")
            self.status_label.setStyleSheet("""
                background-color: red;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;
                border-radius: 4px;
            """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = FileCompareDialog()
    app.setStyleSheet(window.get_stylesheet())
    window.show()

    sys.exit(app.exec_())


