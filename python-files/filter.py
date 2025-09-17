import sys
import pandas as pd
import numpy as np
import os
import glob
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar,
    QGroupBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import warnings
warnings.filterwarnings('ignore')


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_folder, given_name_file, ignored_websites_file, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.given_name_file = given_name_file
        self.ignored_websites_file = ignored_websites_file
        self.output_folder = output_folder

    def read_data_file(self, file_path):
        """Read Excel or CSV file with robust error handling"""
        try:
            path_lower = file_path.lower()
            if path_lower.endswith('.xlsx'):
                # .xlsx → openpyxl
                return pd.read_excel(file_path, dtype=str, engine='openpyxl')
            elif path_lower.endswith('.xls'):
                # .xls → xlrd (if available); otherwise let pandas pick default
                try:
                    return pd.read_excel(file_path, dtype=str, engine='xlrd')
                except Exception:
                    return pd.read_excel(file_path, dtype=str)
            elif path_lower.endswith('.csv'):
                # Try different encodings for CSV
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        return pd.read_csv(file_path, dtype=str, encoding=encoding)
                    except Exception:
                        continue
                # If all encodings fail, try without specifying encoding
                return pd.read_csv(file_path, dtype=str)
            else:
                self.message.emit(f"Unsupported file type: {os.path.basename(file_path)}")
                return None
        except Exception as e:
            self.message.emit(f"Failed to read {os.path.basename(file_path)}: {str(e)}")
            return None

    def run(self):
        try:
            # Step 1: Merge all Excel and CSV files
            self.message.emit("Finding data files...")
            data_files = (
                glob.glob(os.path.join(self.input_folder, "*.xlsx")) +
                glob.glob(os.path.join(self.input_folder, "*.xls")) +
                glob.glob(os.path.join(self.input_folder, "*.csv"))
            )

            if not data_files:
                self.finished.emit(False, "No data files (Excel or CSV) found in the selected folder")
                return

            self.message.emit(f"Found {len(data_files)} data files")

            # Read and merge files
            dfs = []
            for i, file_path in enumerate(data_files):
                self.message.emit(f"Reading {os.path.basename(file_path)}...")
                df = self.read_data_file(file_path)
                if df is not None and not df.empty:
                    dfs.append(df)
                    self.message.emit(f"Successfully read {len(df)} rows from {os.path.basename(file_path)}")
                else:
                    self.message.emit(f"Failed to read or empty data in {os.path.basename(file_path)}")

                self.progress.emit(int((i + 1) * 30 / len(data_files)))

            if not dfs:
                self.finished.emit(False, "No valid data found in any files")
                return

            self.message.emit("Merging files...")
            merged_df = pd.concat(dfs, ignore_index=True, sort=False)
            merged_df = merged_df.drop_duplicates()

            self.progress.emit(40)

            # Step 2: Process Given Name file
            self.message.emit("Processing Given Name file...")
            given_names_df = self.read_data_file(self.given_name_file)
            if given_names_df is None or given_names_df.empty:
                self.finished.emit(False, "Failed to read Given Name file or file is empty")
                return

            # Find the Given Name column (case-insensitive)
            given_name_col = None
            for col in given_names_df.columns:
                cl = str(col).lower()
                if 'given' in cl and 'name' in cl:
                    given_name_col = col
                    break

            if given_name_col is None:
                for col in given_names_df.columns:
                    cl = str(col).lower()
                    if 'given' in cl or 'name' in cl:
                        given_name_col = col
                        break

            if given_name_col is None:
                self.finished.emit(False, "'Given Name' column not found in the selected file")
                return

            given_names = (
                given_names_df[given_name_col]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )
            self.message.emit(f"Found {len(given_names)} unique values in '{given_name_col}' column")

            # Lookup Given Names in merged data
            self.message.emit("Performing lookup for Given Names...")
            # Find 'input' column case-insensitively if needed
            input_col = None
            for col in merged_df.columns:
                if str(col).lower() == 'input':
                    input_col = col
                    break
            if input_col is None:
                self.finished.emit(False, "'input' column not found in merged data")
                return

            merged_df[input_col] = merged_df[input_col].astype(str).str.strip()
            mask = merged_df[input_col].isin(given_names)
            matched_rows = merged_df[mask].copy()

            self.progress.emit(60)

            # Step 3: Process Ignored Websites file
            self.message.emit("Processing Ignored Websites file...")
            ignored_websites_df = self.read_data_file(self.ignored_websites_file)
            if ignored_websites_df is None or ignored_websites_df.empty:
                self.finished.emit(False, "Failed to read Ignored Websites file or file is empty")
                return

            # Find the Ignored Website column (case-insensitive)
            ignored_website_col = None
            for col in ignored_websites_df.columns:
                cl = str(col).lower()
                if 'ignored' in cl and 'website' in cl:
                    ignored_website_col = col
                    break

            if ignored_website_col is None:
                for col in ignored_websites_df.columns:
                    cl = str(col).lower()
                    if 'ignored' in cl or 'website' in cl:
                        ignored_website_col = col
                        break

            if ignored_website_col is None:
                self.finished.emit(False, "'Ignored Website' column not found in the selected file")
                return

            ignored_websites = (
                ignored_websites_df[ignored_website_col]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )
            self.message.emit(f"Found {len(ignored_websites)} ignored websites")

            # Filter out rows with ignored websites
            self.message.emit("Filtering out ignored websites...")

            # Locate link column (prefer exact 'link', else case-insensitive)
            link_col = None
            if 'link' in matched_rows.columns:
                link_col = 'link'
            else:
                for col in matched_rows.columns:
                    if str(col).lower() == 'link':
                        link_col = col
                        break

            if link_col is None:
                # No link column → cannot filter by websites; just pass matched as filtered
                self.message.emit("Warning: 'link' column not found in matched data; skipping website filtering")
                filtered_rows = matched_rows.copy()
                ignored_rows = pd.DataFrame()
            else:
                matched_rows[link_col] = matched_rows[link_col].astype(str)

                def contains_ignored_website(link, ignored_list):
                    link_lower = str(link).lower()
                    return any(str(ignored).lower() in link_lower for ignored in ignored_list)

                contains_ignored_mask = matched_rows[link_col].apply(
                    lambda x: contains_ignored_website(x, ignored_websites)
                )

                filtered_rows = matched_rows[~contains_ignored_mask].copy()
                ignored_rows = matched_rows[contains_ignored_mask].copy()

            self.progress.emit(80)

            # Save results
            self.message.emit("Saving output files...")

            # Function to save large files with splitting
            def save_large_file(df, base_name, max_rows=1_000_000):
                if len(df) == 0:
                    self.message.emit(f"No data to save for {base_name}")
                    return

                if len(df) <= max_rows:
                    output_path = os.path.join(self.output_folder, f"{base_name}.xlsx")
                    df.to_excel(output_path, index=False, engine='openpyxl')
                    self.message.emit(f"Saved {len(df)} rows to {base_name}.xlsx")
                else:
                    num_files = (len(df) // max_rows) + (1 if len(df) % max_rows else 0)
                    for i in range(num_files):
                        start_idx = i * max_rows
                        end_idx = min((i + 1) * max_rows, len(df))
                        chunk_df = df.iloc[start_idx:end_idx]
                        output_path = os.path.join(self.output_folder, f"{base_name}_part_{i+1}.xlsx")
                        chunk_df.to_excel(output_path, index=False, engine='openpyxl')
                        self.message.emit(f"Saved {len(chunk_df)} rows to {base_name}_part_{i+1}.xlsx")

            # Save all output files
            save_large_file(merged_df, "merged_all_files")
            save_large_file(matched_rows, "all_matched_rows")
            save_large_file(filtered_rows, "filtered_final_output")
            save_large_file(ignored_rows, "removed_ignored_websites")

            self.progress.emit(100)
            self.finished.emit(
                True,
                (
                    "Processing completed successfully!\n"
                    f"Merged files: {len(merged_df):,} rows\n"
                    f"Matched rows: {len(matched_rows):,} rows\n"
                    f"Final output: {len(filtered_rows):,} rows\n"
                    f"Removed rows: {len(ignored_rows):,} rows"
                )
            )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.finished.emit(False, f"Error occurred: {str(e)}\n\nDetails:\n{error_details}")


class ExcelProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize variables
        self.input_folder = None
        self.given_name_file = None
        self.ignored_websites_file = None
        self.output_folder = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Data File Processor')
        self.setGeometry(100, 100, 900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel('Data File Processor (Excel & CSV)')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel('This tool processes multiple Excel/CSV files with millions of rows, merges them, and performs lookups and filtering.')
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Input section
        input_group = QGroupBox("Input Files Selection")
        input_layout = QVBoxLayout()

        # Input folder selection
        self.input_folder_btn = QPushButton('Select Input Folder (Excel/CSV files)')
        self.input_folder_btn.clicked.connect(self.select_input_folder)
        self.input_folder_label = QLabel('No folder selected')
        input_layout.addWidget(self.input_folder_btn)
        input_layout.addWidget(self.input_folder_label)

        # Given Name file selection
        self.given_name_btn = QPushButton('Select Given Name File (Excel/CSV)')
        self.given_name_btn.clicked.connect(self.select_given_name_file)
        self.given_name_label = QLabel('No file selected')
        input_layout.addWidget(self.given_name_btn)
        input_layout.addWidget(self.given_name_label)

        # Ignored Websites file selection
        self.ignored_websites_btn = QPushButton('Select Ignored Websites File (Excel/CSV)')
        self.ignored_websites_btn.clicked.connect(self.select_ignored_websites_file)
        self.ignored_websites_label = QLabel('No file selected')
        input_layout.addWidget(self.ignored_websites_btn)
        input_layout.addWidget(self.ignored_websites_label)

        # Output folder selection
        self.output_folder_btn = QPushButton('Select Output Folder')
        self.output_folder_btn.clicked.connect(self.select_output_folder)
        self.output_folder_label = QLabel('No folder selected')
        input_layout.addWidget(self.output_folder_btn)
        input_layout.addWidget(self.output_folder_label)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel('Ready to process')
        progress_layout.addWidget(self.status_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        progress_layout.addWidget(self.log_output)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Process button
        self.process_btn = QPushButton('Start Processing')
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        layout.addWidget(self.process_btn)

        # Set style
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                padding: 5px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Monaco, monospace;
            }
        """)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder (contains Excel/CSV files)")
        if folder:
            self.input_folder = folder
            self.input_folder_label.setText(folder)
            self.check_ready()

    def select_given_name_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Given Name File", "",
            "Data Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if file:
            self.given_name_file = file
            self.given_name_label.setText(os.path.basename(file))
            self.check_ready()

    def select_ignored_websites_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Ignored Websites File", "",
            "Data Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if file:
            self.ignored_websites_file = file
            self.ignored_websites_label.setText(os.path.basename(file))
            self.check_ready()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(folder)
            self.check_ready()

    def check_ready(self):
        # Check if all required files/folders are selected
        all_selected = (
            self.input_folder is not None and
            self.given_name_file is not None and
            self.ignored_websites_file is not None and
            self.output_folder is not None
        )
        self.process_btn.setEnabled(all_selected)

    def start_processing(self):
        self.process_btn.setEnabled(False)
        self.log_output.clear()
        self.log_message("Starting processing...")
        self.progress_bar.setValue(0)

        self.worker = WorkerThread(
            self.input_folder,
            self.given_name_file,
            self.ignored_websites_file,
            self.output_folder
        )

        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.log_message)
        self.worker.finished.connect(self.processing_finished)

        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def log_message(self, message):
        self.log_output.append(f"{time.strftime('%H:%M:%S')} - {message}")
        # Auto-scroll to bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def processing_finished(self, success, message):
        self.log_message(message)
        self.process_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExcelProcessorApp()
    window.show()
    sys.exit(app.exec_())
