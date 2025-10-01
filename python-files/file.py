import os
import shutil
from PyQt5 import QtWidgets

class FileCopyApp(QtWidgets.QWidget):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Smart File Copier")
        self.setGeometry(300, 300, 600, 350)

        # UI elements
        self.source_path = QtWidgets.QLineEdit(self)
        self.dest_path = QtWidgets.QLineEdit(self)
        self.selected_files_folder = QtWidgets.QLineEdit(self)

        self.source_btn = QtWidgets.QPushButton("Browse Source Folder", self)
        self.dest_btn = QtWidgets.QPushButton("Browse Destination Folder", self)
        self.selected_btn = QtWidgets.QPushButton("Browse Selected Files Folder", self)
        self.run_btn = QtWidgets.QPushButton("Run Copy", self)
        self.log = QtWidgets.QTextEdit(self)
        self.log.setReadOnly(True)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.source_path)
        layout.addWidget(self.source_btn)
        layout.addWidget(self.dest_path)
        layout.addWidget(self.dest_btn)
        layout.addWidget(self.selected_files_folder)
        layout.addWidget(self.selected_btn)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.log)
        self.setLayout(layout)

        # Connections
        self.source_btn.clicked.connect(self.browse_source)
        self.dest_btn.clicked.connect(self.browse_dest)
        self.selected_btn.clicked.connect(self.browse_selected)
        self.run_btn.clicked.connect(self.run_copy)

    def browse_source(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.source_path.setText(folder)

    def browse_dest(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.dest_path.setText(folder)

    def browse_selected(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Selected Files Folder")
        if folder:
            self.selected_files_folder.setText(folder)

    def run_copy(self):
        src = self.source_path.text()
        dest = self.dest_path.text()
        sel_folder = self.selected_files_folder.text()

        if not all([src, dest, sel_folder]):
            self.log.append("Please select all three paths!")
            return

        # Collect all filenames from text files in selected folder
        file_names = []
        for txt_file in os.listdir(sel_folder):
            txt_path = os.path.join(sel_folder, txt_file)
            if os.path.isfile(txt_path) and txt_file.lower().endswith(".txt"):
                with open(txt_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line:
                            file_names.append(clean_line)

        if not file_names:
            self.log.append("No filenames found in selected files folder!")
            return

        # Copy matching files
        copied = 0
        for fname in file_names:
            src_file = os.path.join(src, fname)
            if os.path.exists(src_file):
                shutil.copy(src_file, dest)
                self.log.append(f"Copied: {fname}")
                copied += 1
            else:
                self.log.append(f"File not found in source: {fname}")

        self.log.append(f"Done! Total files copied: {copied}")

# Run the app
if _name_ == "_main_":
    app = QtWidgets.QApplication([])
    window = FileCopyApp()
    window.show()
    app.exec_()