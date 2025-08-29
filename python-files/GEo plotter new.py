import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QLabel, QMessageBox, QHBoxLayout, QStackedWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QDesktopServices, QFont # Keep QFont for potential use, but won't be explicitly set here for default
import os

# --- Qt Style Sheet (QSS) for the previous dark theme ---
QSS = """
QMainWindow {
    background-color: #333333; /* Dark background */
    color: #F0F0F0; /* Light text color */
}

QWidget {
    background-color: #333333;
    color: #F0F0F0;
    font-family: Arial;
    font-size: 14px;
}

QPushButton {
    background-color: #555555; /* Darker button background */
    color: #F0F0F0;
    border: 1px solid #777777;
    padding: 10px 20px;
    border-radius: 5px; /* Rounded corners */
    min-height: 30px; /* Ensure buttons have a minimum height */
}

QPushButton:hover {
    background-color: #666666; /* Lighter on hover */
}

QPushButton:pressed {
    background-color: #444444; /* Darker when pressed */
    border: 1px solid #999999;
}

/* Style for "tab" buttons in CombinedApp */
QPushButton#NavButton {
    background-color: #444444;
    border: none; /* No border for 'tabs' */
    border-radius: 0px; /* Square corners for 'tabs' */
    padding: 15px 25px; /* Larger padding for 'tabs' */
    margin: 0px;
}

QPushButton#NavButton:hover {
    background-color: #555555;
}

QPushButton#NavButton.active { /* Style for the active 'tab' button */
    background-color: #007ACC; /* Blue for active tab */
    color: #FFFFFF;
    font-weight: bold;
}

QLabel {
    color: #F0F0F0;
    padding: 5px;
}

QProgressBar {
    text-align: center;
    color: #F0F0F0;
    background-color: #555555;
    border-radius: 5px;
    height: 25px;
}

QProgressBar::chunk {
    background-color: #007ACC; /* Blue progress bar */
    border-radius: 5px;
}
"""

# --- ExcelToCsvConverter Class (Reverted padding/spacing, kept progress bar) ---
class ExcelToCsvConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) # Reverted padding
        layout.setSpacing(15) # Reverted spacing

        self.input_file_label = QLabel("No files selected.")
        self.input_file_label.setAlignment(Qt.AlignCenter)
        # Removed explicit font setting here
        layout.addWidget(self.input_file_label)

        self.select_files_button = QPushButton("Select Excel Files")
        self.select_files_button.clicked.connect(self.select_excel_files)
        layout.addWidget(self.select_files_button)

        self.convert_button = QPushButton("Convert to Combined CSV")
        self.convert_button.clicked.connect(self.convert_files)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        # Loading animation/progress bar (KEPT)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0) # Indeterminate mode
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False) # Hidden initially
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        # Removed explicit font setting here
        layout.addWidget(self.status_label)

        self.excel_file_paths = []

    def set_loading_state(self, is_loading, message=""):
        self.progress_bar.setVisible(is_loading)
        self.progress_bar.setFormat(message)
        self.select_files_button.setEnabled(not is_loading)
        self.convert_button.setEnabled(not is_loading and bool(self.excel_file_paths))
        QApplication.processEvents()

    def select_excel_files(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Excel Files", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options
        )
        if file_paths:
            self.excel_file_paths = file_paths
            self.input_file_label.setText(f"{len(file_paths)} files selected.")
            self.convert_button.setEnabled(True)
            self.status_label.setText("")
        else:
            self.excel_file_paths = []
            self.input_file_label.setText("No files selected.")
            self.convert_button.setEnabled(False)
            self.status_label.setText("")

    def convert_files(self):
        if not self.excel_file_paths:
            QMessageBox.warning(self, "No Files Selected", "Please select one or more Excel files first.")
            return

        self.set_loading_state(True, "Processing files...")
        
        all_converted_dfs = []
        failed_files = []
        required_input_cols = ['GpsLatitude', 'GpsLongitude', 'vin', 'Timestamp']

        for i, file_path in enumerate(self.excel_file_paths):
            self.progress_bar.setFormat(f"Processing file {i+1}/{len(self.excel_file_paths)}: {os.path.basename(file_path)}")
            QApplication.processEvents()

            try:
                df = pd.read_excel(file_path)
                missing_cols = [col for col in required_input_cols if col not in df.columns]
                if missing_cols:
                    failed_files.append(f"{os.path.basename(file_path)} (Missing columns: {', '.join(missing_cols)})")
                    continue

                output_df = pd.DataFrame()
                output_df['lat'] = pd.to_numeric(df['GpsLatitude'], errors='coerce')
                output_df['lng'] = pd.to_numeric(df['GpsLongitude'], errors='coerce')
                output_df['name'] = df['vin']
                output_df['color'] = 'red'
                output_df['note'] = df['Timestamp'].astype(str)
                output_df.dropna(subset=['lat', 'lng'], inplace=True)
                all_converted_dfs.append(output_df)

            except Exception as e:
                failed_files.append(f"{os.path.basename(file_path)} (Error: {e})")
                continue

        self.set_loading_state(False)

        if not all_converted_dfs:
            error_message = "No files were successfully converted."
            if failed_files:
                error_message += "\nFailed files:\n" + "\n".join(failed_files)
            QMessageBox.critical(self, "Conversion Failed", error_message)
            self.status_label.setText("Conversion failed for all selected files.")
            return

        combined_df = pd.concat(all_converted_dfs, ignore_index=True)

        options = QFileDialog.Options()
        output_file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Combined CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if output_file_path:
            if not output_file_path.lower().endswith('.csv'):
                output_file_path += '.csv'

            try:
                combined_df.to_csv(output_file_path, index=False)
                success_message = f"All selected files converted and combined into:\n{output_file_path}"
                if failed_files:
                    success_message += "\n\nHowever, some files failed:\n" + "\n".join(failed_files)
                    QMessageBox.warning(self, "Conversion Completed with Warnings", success_message)
                else:
                    QMessageBox.information(self, "Conversion Successful", success_message)

                self.status_label.setText(f"Combined into: {os.path.basename(output_file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save the combined CSV: {e}")
                self.status_label.setText("Saving combined CSV failed.")
        else:
            self.status_label.setText("Conversion cancelled by user (save file).")

# --- GpsVisualizerWidget (Opens in external browser - Reverted padding/spacing) ---
class GpsVisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) # Reverted padding
        layout.setSpacing(15) # Reverted spacing

        info_label = QLabel("Click the button below to open GPS Visualizer in your default web browser.")
        info_label.setAlignment(Qt.AlignCenter)
        # Removed explicit font setting here
        layout.addWidget(info_label)

        open_button = QPushButton("Open GPS Visualizer")
        open_button.clicked.connect(self.open_gps_visualizer_external)
        layout.addWidget(open_button)

    def open_gps_visualizer_external(self):
        url = QUrl("https://www.gpsvisualizer.com/")
        QDesktopServices.openUrl(url)

# --- CombinedApp (Main Window - QSS applied) ---
class CombinedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combined GPS Tools")
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet(QSS) # Apply the QSS to the whole application

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Top Control Buttons (simulating tabs) ---
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(1)

        self.excel_converter_button = QPushButton("Excel to CSV Converter")
        self.excel_converter_button.setObjectName("NavButton")
        self.excel_converter_button.clicked.connect(self.show_excel_converter)
        button_layout.addWidget(self.excel_converter_button)

        self.gps_visualizer_button = QPushButton("GPS Visualizer (External)")
        self.gps_visualizer_button.setObjectName("NavButton")
        self.gps_visualizer_button.clicked.connect(self.show_gps_visualizer)
        button_layout.addWidget(self.gps_visualizer_button)

        main_layout.addLayout(button_layout)

        # --- Stacked Widget for content ---
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.excel_converter_widget = ExcelToCsvConverterWidget()
        self.gps_visualizer_widget = GpsVisualizerWidget()

        self.stacked_widget.addWidget(self.excel_converter_widget)
        self.stacked_widget.addWidget(self.gps_visualizer_widget)

        self.show_excel_converter() # Show converter by default

    def update_button_styles(self):
        # Clear 'active' class from all navigation buttons
        self.excel_converter_button.setProperty("class", "")
        self.gps_visualizer_button.setProperty("class", "")

        # Set 'active' class on the current navigation button
        if self.stacked_widget.currentWidget() == self.excel_converter_widget:
            self.excel_converter_button.setProperty("class", "active")
            self.setWindowTitle("Geoplotter ,Jamshedpur ,Vehicle Despatch - File Converter")
        elif self.stacked_widget.currentWidget() == self.gps_visualizer_widget:
            self.gps_visualizer_button.setProperty("class", "active")
            self.setWindowTitle("Geoplotter ,Jamshedpur ,Vehicle Despatch- GPS Visualizer (External)")

        # Re-polish the styles to apply the class change immediately
        self.excel_converter_button.style().polish(self.excel_converter_button)
        self.gps_visualizer_button.style().polish(self.gps_visualizer_button)


    def show_excel_converter(self):
        self.stacked_widget.setCurrentWidget(self.excel_converter_widget)
        self.update_button_styles()

    def show_gps_visualizer(self):
        self.stacked_widget.setCurrentWidget(self.gps_visualizer_widget)
        self.update_button_styles()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = CombinedApp()
    main_app.show()
    sys.exit(app.exec_())