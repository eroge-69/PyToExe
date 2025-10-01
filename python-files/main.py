import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QComboBox, QFileDialog, QMessageBox, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt

# Ensure PyInstaller includes these modules
# hiddenimports=['pyqtgraph', 'pandas', 'numpy']

# Log uncaught exceptions to debug.txt
def log_exception(exc_type, exc_value, exc_traceback):
    with open("debug.txt", "a") as debug_file:
        debug_file.write(f"Uncaught exception:\n{exc_type.__name__}: {exc_value}\n")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = log_exception

class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplified CSV Plotter")
        self.setGeometry(100, 100, 1200, 800)
        self.data = None
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout(self.central_widget)

        # Control panel layout
        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        # File and Plot Controls
        file_group = QGroupBox("File and Plot Controls")
        file_layout = QHBoxLayout(file_group)
        self.load_button = QPushButton("Load CSV")
        self.plot_button = QPushButton("Plot")
        self.autofit_button = QPushButton("Autofit Data")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.plot_button)
        file_layout.addWidget(self.autofit_button)
        control_layout.addWidget(file_group)

        # Axis Selection
        axis_group = QGroupBox("Axis Selection")
        axis_layout = QHBoxLayout(axis_group)
        self.x_label = QLabel("X-axis:")
        self.x_dropdown = QComboBox()
        self.y_label = QLabel("Y-axis:")
        self.y_dropdown = QComboBox()
        axis_layout.addWidget(self.x_label)
        axis_layout.addWidget(self.x_dropdown)
        axis_layout.addWidget(self.y_label)
        axis_layout.addWidget(self.y_dropdown)
        control_layout.addWidget(axis_group)

        # Plot widget
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.plot_widget)

        # Connections
        self.load_button.clicked.connect(self.load_csv)
        self.plot_button.clicked.connect(self.plot_data)
        self.autofit_button.clicked.connect(self.autofit_data)

    def autofit_data(self):
        try:
            self.plot_widget.getPlotItem().vb.autoRange()
        except Exception as e:
            QMessageBox.critical(self, "Autofit Error", str(e))

    def log_error(self, error_message):
        with open("debug.txt", "a") as debug_file:
            debug_file.write(error_message + "\n")
        QMessageBox.critical(self, "Error", error_message)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return
        try:
            self.plot_widget.clear()
            self.data = pd.read_csv(file_path, engine='python', na_values=["####"], on_bad_lines='skip')
            self.x_dropdown.clear()
            self.y_dropdown.clear()
            columns = self.data.columns.tolist()
            self.x_dropdown.addItems(columns)
            self.y_dropdown.addItems(columns)
            QMessageBox.information(self, "Success", "CSV loaded successfully!")
        except Exception as e:
            self.log_error(f"Failed to load CSV: {e}")

    def plot_data(self):
        try:
            if self.data is None:
                QMessageBox.warning(self, "No Data", "Please load a CSV file first.")
                return
            x_col = self.x_dropdown.currentText()
            y_col = self.y_dropdown.currentText()
            self.plot_widget.clear()
            if x_col and y_col:
                valid_data = self.data[[x_col, y_col]].dropna()
                x_data = pd.to_numeric(valid_data[x_col], errors='coerce')
                y_data = pd.to_numeric(valid_data[y_col], errors='coerce')
                self.plot_widget.plot(x_data, y_data, pen='b')
                self.plot_widget.setLabel('bottom', x_col)
                self.plot_widget.setLabel('left', y_col)
        except Exception as e:
            self.log_error(f"Plot Error: {e}")

def main():
    app = QApplication(sys.argv)
    window = CSVPlotterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()