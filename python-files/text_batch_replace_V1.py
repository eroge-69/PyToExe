#!/usr/bin/env python3
"""
Text Batch Search-and-Replace GUI

Requirements:
    pip install PyQt5

How it works (quick):
 - Choose a folder with "Browse". The app will scan recursively and list text/code files (skips common media/binary files).
 - Enter Search text and Replace text (Replace can be empty to delete).
 - Optionally check "Search filenames/foldernames" to also search/rename file and folder names.
 - Click "Start" to begin scanning. The first file with a match will be opened in the editor and the first occurrence highlighted.
 - For every occurrence the app will prompt (Replace / Skip / Replace All in this file / Skip File / Cancel).
 - You may also manually edit the file in the editor if "Allow manual edit" is checked. After you finish, click "Save & Next" to save changes and move to the next file.
 - Files that don't contain the search text are skipped automatically.

This is a single-file example intended to be a helpful starting point and is reasonably defensive but not production hardened.
"""

import sys
import os
import mimetypes
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

# --- Configuration ---
MEDIA_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.mp3', '.wav', '.ogg', '.mp4', '.mkv', '.avi', '.mov',
    '.exe', '.dll', '.so', '.bin', '.pdf', '.zip', '.tar', '.gz', '.7z'
}

# Helper: heuristic to detect text file
def is_text_file(path: Path) -> bool:
    try:
        ext = path.suffix.lower()
        if ext in MEDIA_EXTENSIONS:
            return False
        # check mimetype
        mtype, _ = mimetypes.guess_type(str(path))
        if mtype and not mtype.startswith('text') and 'json' not in str(ext) and 'xml' not in str(ext):
            # many code files are text but some unknown types are ok — we'll do a content check
            pass
        # quick null byte check
        with open(path, 'rb') as f:
            chunk = f.read(2048)
            if b"\x00" in chunk:
                return False
        return True
    except Exception:
        return False


class BatchReplaceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Batch Text Search & Replace')
        self.resize(1000, 700)

        self.files = []  # list of Path
        self.current_index = -1
        self.skip_non_matching = True
        self.replace_all_in_file = False

        self._build_ui()

    def _build_ui(self):
        mainw = QtWidgets.QWidget()
        self.setCentralWidget(mainw)
        layout = QtWidgets.QVBoxLayout(mainw)

        # Top controls
        top = QtWidgets.QHBoxLayout()
        self.folder_label = QtWidgets.QLabel('No folder selected')
        top.addWidget(self.folder_label)
        browse_btn = QtWidgets.QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_folder)
        top.addWidget(browse_btn)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText('Search text')
        top.addWidget(self.search_input)
        self.replace_input = QtWidgets.QLineEdit()
        self.replace_input.setPlaceholderText('Replace with')
        top.addWidget(self.replace_input)

        self.search_names_cb = QtWidgets.QCheckBox('Search filenames/foldernames')
        top.addWidget(self.search_names_cb)

        self.manual_edit_cb = QtWidgets.QCheckBox('Allow manual edit')
        top.addWidget(self.manual_edit_cb)

        start_btn = QtWidgets.QPushButton('Start')
        start_btn.clicked.connect(self.start_scan)
        top.addWidget(start_btn)

        layout.addLayout(top)

        # Middle split: file list and editor
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        left_layout.addWidget(self.file_list)
        splitter.addWidget(left_widget)

        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setReadOnly(True)
        font = QtGui.QFont('Courier', 10)
        self.editor.setFont(font)
        right_layout.addWidget(self.editor)

        btns = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton('Prev File')
        self.prev_btn.clicked.connect(self.prev_file)
        btns.addWidget(self.prev_btn)
        self.next_btn = QtWidgets.QPushButton('Next File')
        self.next_btn.clicked.connect(self.next_file)
        btns.addWidget(self.next_btn)

        self.process_btn = QtWidgets.QPushButton('Find Next Occurrence')
        self.process_btn.clicked.connect(self.find_next_occurrence)
        btns.addWidget(self.process_btn)

        self.save_btn = QtWidgets.QPushButton('Save & Next')
        self.save_btn.clicked.connect(self.save_and_next)
        btns.addWidget(self.save_btn)

        right_layout.addLayout(btns)

        splitter.addWidget(right_widget)
        layout.addWidget(splitter)

        # Status bar
        self.status = QtWidgets.QLabel('Ready')
        layout.addWidget(self.status)

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder')
        if folder:
            self.folder_label.setText(folder)
            self.root = Path(folder)

    def start_scan(self):
        if not hasattr(self, 'root'):
            QtWidgets.QMessageBox.warning(self, 'No folder', 'Please choose a folder first')
            return
        stext = self.search_input.text()
        if not stext:
            QtWidgets.QMessageBox.warning(self, 'No search text', 'Please enter search text')
            return
        self.files = self._gather_files(self.root)
        self.file_list.clear()
        for p in self.files:
            item = QtWidgets.QListWidgetItem(str(p))
            item.setCheckState(QtCore.Qt.Checked)
            self.file_list.addItem(item)
        if not self.files:
            self.status.setText('No candidate files found')
            return
        self.status.setText(f'Found {len(self.files)} files')
        # move to first matching file automatically
        self.current_index = -1
        self.next_file(auto=True)

    def _gather_files(self, root: Path):
        result = []
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                p = Path(dirpath) / fname
                if is_text_file(p):
                    result.append(p)
        return result

    def _load_file_into_editor(self, path: Path):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except Exception as e:
            text = f'Error reading file: {e}'
        self.editor.setPlainText(text)
        self.editor.setReadOnly(not self.manual_edit_cb.isChecked())
        self.status.setText(f'Opened {path}')

    def on_file_selected(self):
        items = self.file_list.selectedItems()
        if not items:
            return
        idx = self.file_list.row(items[0])
        self.current_index = idx
        path = self.files[idx]
        self._load_file_into_editor(path)

    def prev_file(self):
        if not self.files:
            return
        self.current_index = max(0, (self.current_index - 1) if self.current_index >= 0 else 0)
        self.file_list.setCurrentRow(self.current_index)

    def next_file(self, auto=False):
        # advance to next file that is checked. If auto=True, skip files with no matches automatically.
        if not self.files:
            return
        start = self.current_index + 1
        found = False
        for i in range(start, len(self.files)):
            item = self.file_list.item(i)
            if item.checkState() == QtCore.Qt.Unchecked:
                continue
            if auto:
                if self._file_has_match(self.files[i]):
                    self.current_index = i
                    found = True
                    break
            else:
                self.current_index = i
                found = True
                break
        if not found:
            QtWidgets.QMessageBox.information(self, 'Done', 'No more files')
            return
        self.file_list.setCurrentRow(self.current_index)

    def _file_has_match(self, path: Path) -> bool:
        s = self.search_input.text()
        if not s:
            return False
        # check contents
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            if s in text:
                return True
            # check filename/folder name if enabled
            if self.search_names_cb.isChecked():
                if s in path.name or s in str(path.parent):
                    return True
        except Exception:
            return False
        return False

    def find_next_occurrence(self):
        # find next occurrence in current editor text starting from cursor
        s = self.search_input.text()
        if not s:
            return
        text = self.editor.toPlainText()
        cursor = self.editor.textCursor()
        start_pos = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
        idx = text.find(s, start_pos)
        if idx == -1:
            # wrap around search
            idx = text.find(s, 0)
            if idx == -1:
                QtWidgets.QMessageBox.information(self, 'No match', 'No occurrences in this file')
                return
        # select match
        cursor.setPosition(idx)
        cursor.setPosition(idx + len(s), QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        # prompt user for replace
        self._prompt_replace_at_cursor(idx)

    def _prompt_replace_at_cursor(self, idx):
        s = self.search_input.text()
        r = self.replace_input.text()
        # dialog with many options
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle('Replace?')
        dlg.setText(f'Found occurrence at position {idx}.\nReplace this occurrence?')
        replace_btn = dlg.addButton('Replace', QtWidgets.QMessageBox.YesRole)
        skip_btn = dlg.addButton('Skip', QtWidgets.QMessageBox.NoRole)
        replace_all_btn = dlg.addButton('Replace All in File', QtWidgets.QMessageBox.AcceptRole)
        skip_file_btn = dlg.addButton('Skip File', QtWidgets.QMessageBox.RejectRole)
        cancel_btn = dlg.addButton('Cancel', QtWidgets.QMessageBox.DestructiveRole)
        dlg.exec_()
        btn = dlg.clickedButton()
        if btn == replace_btn:
            self._do_replace_at(idx)
        elif btn == skip_btn:
            # do nothing, leave selection and move on
            pass
        elif btn == replace_all_btn:
            self._do_replace_all_in_file()
        elif btn == skip_file_btn:
            # move to next file
            self.save_and_next(skip_save=True)
        else:
            # cancel
            return

    def _do_replace_at(self, idx):
        s = self.search_input.text()
        r = self.replace_input.text()
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(r)
        cursor.endEditBlock()
        self.status.setText('Replaced one occurrence')

    def _do_replace_all_in_file(self):
        s = self.search_input.text()
        r = self.replace_input.text()
        text = self.editor.toPlainText()
        new = text.replace(s, r)
        self.editor.setPlainText(new)
        self.status.setText('Replaced all occurrences in file')

    def save_and_next(self, skip_save=False):
        # Save current editor back to file, optionally renaming if filename contains search text
        if self.current_index < 0 or self.current_index >= len(self.files):
            return
        path = self.files[self.current_index]
        s = self.search_input.text()
        r = self.replace_input.text()
        # Save file
        if not skip_save:
            try:
                with open(path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(self.editor.toPlainText())
                self.status.setText(f'Saved {path.name}')
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Save error', f'Could not save: {e}')
                return
        # Rename file/folder if needed
        if self.search_names_cb.isChecked():
            # file rename
            if s in path.name:
                new_name = path.name.replace(s, r)
                new_path = path.with_name(new_name)
                try:
                    path.rename(new_path)
                    self.files[self.current_index] = new_path
                    self.status.setText(f'Renamed file to {new_name}')
                    path = new_path
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, 'Rename error', f'Could not rename file: {e}')
            # parent folder rename (single level)
            parent = path.parent
            if s in parent.name:
                new_parent_name = parent.name.replace(s, r)
                new_parent = parent.with_name(new_parent_name)
                try:
                    parent.rename(new_parent)
                    self.status.setText(f'Renamed folder to {new_parent_name}')
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, 'Rename error', f'Could not rename folder: {e}')
        # move to next file automatically: find next file with match, else plain next
        # update displayed file list item text (in case of rename)
        self.file_list.item(self.current_index).setText(str(self.files[self.current_index]))
        # advance
        old_index = self.current_index
        self.current_index += 1
        while self.current_index < len(self.files):
            item = self.file_list.item(self.current_index)
            if item.checkState() == QtCore.Qt.Unchecked:
                self.current_index += 1
                continue
            # if file contains search text move here; otherwise skip
            if self._file_has_match(self.files[self.current_index]):
                self.file_list.setCurrentRow(self.current_index)
                return
            else:
                # skip silently
                self.current_index += 1
        QtWidgets.QMessageBox.information(self, 'Done', 'Processed all files')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = BatchReplaceApp()
    w.show()
    sys.exit(app.exec_())
