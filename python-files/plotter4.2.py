import sys
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter  # Explicitly import the ImageExporter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QComboBox, QFileDialog, QMessageBox, QCheckBox, QHBoxLayout, QDialog, QListWidget, QSplashScreen
)
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer


# Log uncaught exceptions to debug.txt
def log_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions to debug.txt."""
    with open("debug.txt", "a") as debug_file:
        debug_file.write(
            f"Uncaught exception:\n{exc_type.__name__}: {exc_value}\n"
        )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = log_exception


class CSVPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced CSV Plotter")
        self.setGeometry(100, 100, 1200, 800)

        self.data = None
        self.secondary_axis_enabled = False
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout using a splitter
        main_layout = QVBoxLayout(self.central_widget)
        self.splitter = QSplitter(Qt.Vertical)

        # Control panel layout
        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        # Group 1: File and Plot Controls
        file_group = QGroupBox("File and Plot Controls")
        file_layout = QHBoxLayout(file_group)
        self.load_button = QPushButton("Load CSV")
        self.plot_button = QPushButton("Plot")
        self.autofit_button = QPushButton("Autofit Data")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.plot_button)
        file_layout.addWidget(self.autofit_button)
        control_layout.addWidget(file_group)

        # Group 2: Axis Selection
        axis_group = QGroupBox("Axis Selection")
        axis_layout = QHBoxLayout(axis_group)
        self.x_label = QLabel("X-axis:")
        self.x_dropdown = QComboBox()
        self.y_label = QLabel("Y-axis:")
        self.y_dropdown = QComboBox()
        self.y2_label = QLabel("Secondary Y-axis:")
        self.y2_dropdown = QComboBox()
        self.secondary_axis_checkbox = QCheckBox("Enable Secondary Y-axis")
        axis_layout.addWidget(self.x_label)
        axis_layout.addWidget(self.x_dropdown)
        axis_layout.addWidget(self.y_label)
        axis_layout.addWidget(self.y_dropdown)
        axis_layout.addWidget(self.y2_label)
        axis_layout.addWidget(self.y2_dropdown)
        axis_layout.addWidget(self.secondary_axis_checkbox)
        control_layout.addWidget(axis_group)

        # Group 3: Customization and Cursor
        custom_group = QGroupBox("Customization and Cursor")
        custom_layout = QHBoxLayout(custom_group)
        self.grid_checkbox = QCheckBox("Show Gridlines")
        self.grid_checkbox.stateChanged.connect(self.toggle_gridlines)
        self.cursor_checkbox = QCheckBox("Enable Cursor")
        self.line_dropdown = QComboBox()
        self.line_dropdown.addItems(["Solid", "Dashed", "Dotted", "DashDot"])
        self.line_width_dropdown = QComboBox()
        self.line_width_dropdown.addItems(["1", "2", "3", "4", "5"])
        self.symbol_size_dropdown = QComboBox()
        self.symbol_size_dropdown.addItems(["Small", "Medium", "Large"])
        self.symbol_fill_dropdown = QComboBox()
        self.symbol_fill_dropdown.addItems(["Transparent", "Gray", "White"])
        self.symbol_line_dropdown = QComboBox()
        self.symbol_line_dropdown.addItems(["Transparent", "Gray", "White"])
        custom_layout.addWidget(self.grid_checkbox)
        custom_layout.addWidget(self.cursor_checkbox)
        custom_layout.addWidget(QLabel("Line Style:"))
        custom_layout.addWidget(self.line_dropdown)
        custom_layout.addWidget(QLabel("Line Width:"))
        custom_layout.addWidget(self.line_width_dropdown)
        custom_layout.addWidget(QLabel("Symbol Size:"))
        custom_layout.addWidget(self.symbol_size_dropdown)
        custom_layout.addWidget(QLabel("Fill Color:"))
        custom_layout.addWidget(self.symbol_fill_dropdown)
        custom_layout.addWidget(QLabel("Outline Color:"))
        custom_layout.addWidget(self.symbol_line_dropdown)
        control_layout.addWidget(custom_group)

        # Plot widget
        self.plot_widget = pg.PlotWidget()

        # Draggable cursor
        self.cursor = pg.InfiniteLine(angle=90, movable=True, pen='g')  # Green draggable vertical line
        self.cursor_label = pg.TextItem("", anchor=(0, 1), color='g')  # Text to display values

        # Add control panel and plot widget to the splitter
        self.splitter.addWidget(self.control_panel)
        self.splitter.addWidget(self.plot_widget)

        # Set plot widget to take most space
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        # Add splitter to the main layout
        main_layout.addWidget(self.splitter)

        # Connections
        self.load_button.clicked.connect(self.load_csv)
        self.plot_button.clicked.connect(self.plot_data)
        self.autofit_button.clicked.connect(self.autofit_data)
        self.cursor_checkbox.stateChanged.connect(self.toggle_cursor)
        self.secondary_axis_checkbox.stateChanged.connect(self.toggle_secondary_axis)


    def autofit_data(self):
        try:
            self.plot_widget.getPlotItem().vb.autoRange()
        except Exception as e:
            QMessageBox.critical(self, "Autofit Error", str(e))

    def toggle_cursor(self, state):
        if state == Qt.Checked:
            self.plot_widget.addItem(self.cursor)
            self.plot_widget.addItem(self.cursor_label)
            self.cursor.sigPositionChanged.connect(self.update_cursor_label)
        else:
            self.plot_widget.removeItem(self.cursor)
            self.plot_widget.removeItem(self.cursor_label)

    def update_cursor_label(self):
        """Update the cursor label with the current position for both primary and secondary datasets."""
        x_pos = self.cursor.value()

        # Initialize the text for the cursor label
        label_text = f"X: {x_pos:.2f}"

        if self.data is not None:
            # Primary axis data
            x_col = self.x_dropdown.currentText()
            y_col = self.y_dropdown.currentText()
            if x_col and y_col and x_col in self.data.columns and y_col in self.data.columns:
                x_data = pd.to_numeric(self.data[x_col], errors='coerce').dropna()
                y_data = pd.to_numeric(self.data[y_col], errors='coerce').dropna()
                if not x_data.empty and not y_data.empty:
                    closest_index = (x_data - x_pos).abs().idxmin()
                    y_val = y_data[closest_index]
                    label_text += f"\n{y_col}: {y_val:.2f}"  # Add primary Y value to the label

            # Secondary axis data
            if self.secondary_axis_enabled:
                y2_col = self.y2_dropdown.currentText()
                if x_col and y2_col and x_col in self.data.columns and y2_col in self.data.columns:
                    x_data = pd.to_numeric(self.data[x_col], errors='coerce').dropna()
                    y2_data = pd.to_numeric(self.data[y2_col], errors='coerce').dropna()
                    if not x_data.empty and not y2_data.empty:
                        closest_index = (x_data - x_pos).abs().idxmin()
                        y2_val = y2_data[closest_index]
                        label_text += f"\n{y2_col}: {y2_val:.2f}"  # Add secondary Y value to the label

        # Update the cursor label
        self.cursor_label.setText(label_text)
        self.cursor_label.setPos(x_pos, 0)  # Place the label at the cursor's X position


    def log_error(self, error_message):
        """Log errors to debug.txt and show a dialog box."""
        with open("debug.txt", "a") as debug_file:
            debug_file.write(error_message + "\n")
        QMessageBox.critical(self, "Error", error_message)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return

        try:
            # Clear the plot and reset secondary axis state
            self.plot_widget.clear()
            if hasattr(self, 'secondary_view'):
                self.secondary_view.clear()
                self.plot_widget.scene().removeItem(self.secondary_view)
                del self.secondary_view
            if hasattr(self, 'axis2'):
                self.plot_widget.getPlotItem().layout.removeItem(self.axis2)
                del self.axis2

            # Read the raw file content to avoid skipping rows prematurely
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Allow the user to preview and select the header row
            num_preview_rows = 5
            preview_rows = lines[:num_preview_rows]
            header_idx = self.select_header_row(preview_rows)

            # Reload the file, skipping rows up to the selected header row
            raw_data = pd.read_csv(
                file_path,
                engine='python',
                skiprows=header_idx + 1,  # Skip all rows above the header
                na_values=["####"],  # Treat "####" as NaN
                on_bad_lines='skip'  # Skip malformed rows
            )

            # Set the selected row as the header
            header = lines[header_idx].strip().split(",")
            self.data = pd.DataFrame(raw_data.values, columns=header)

            # Update dropdowns with new column names
            self.x_dropdown.clear()
            self.y_dropdown.clear()
            self.y2_dropdown.clear()
            columns = self.data.columns.tolist()
            self.x_dropdown.addItems(columns)
            self.y_dropdown.addItems(columns)
            self.y2_dropdown.addItems(columns)

            QMessageBox.information(self, "Success", "CSV loaded successfully!")
        except Exception as e:
            self.log_error(f"Failed to load CSV: {e}")
            QMessageBox.critical(self, "Error", str(e))




    def export_plot(self):
        """Export the current plot as a JPEG file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot as JPEG", "", "JPEG Files (*.jpg);;All Files (*)")
            if file_path:
                exporter = ImageExporter(self.plot_widget.plotItem)
                exporter.parameters()['width'] = 800
                exporter.export(file_path)
                QMessageBox.information(self, "Export Successful", f"Plot saved as JPEG: {file_path}")
        except Exception as e:
            self.log_error(f"Failed to export plot: {e}")
            QMessageBox.critical(self, "Export Error", str(e))


    def update_axis_titles(self):
        """Update axis titles based on selected columns or user input."""
        x_col = self.x_dropdown.currentText()
        y_col = self.y_dropdown.currentText()
        y2_col = self.y2_dropdown.currentText()

        # Set default titles based on column names
        if x_col:
            self.plot_widget.setLabel('bottom', x_col)
        if y_col:
            self.plot_widget.setLabel('left', y_col)
        if self.secondary_axis_enabled and y2_col:
            self.axis2.setLabel(y2_col)

    def rename_axis(self, axis):
        """Allow the user to rename the specified axis."""
        axis_mapping = {
            "x": "bottom",
            "y": "left",
            "y2": "right"
        }

        axis_label = axis_mapping[axis]
        current_title = self.plot_widget.getLabel(axis_label) if axis != "y2" else self.axis2.labelText
        new_title, ok = QInputDialog.getText(self, f"Rename {axis.upper()} Axis", "Enter new axis title:", text=current_title)

        if ok and new_title.strip():
            if axis == "x":
                self.plot_widget.setLabel('bottom', new_title)
            elif axis == "y":
                self.plot_widget.setLabel('left', new_title)
            elif axis == "y2" and self.secondary_axis_enabled:
                self.axis2.setLabel(new_title)



    def select_header_row(self, preview_rows):
        """Allow the user to select the header row from preview rows."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Header Row")
        dialog.setMinimumWidth(600)

        layout = QVBoxLayout(dialog)
        list_widget = QListWidget(dialog)
        confirm_button = QPushButton("Confirm", dialog)

        for idx, row in enumerate(preview_rows):
            list_widget.addItem(f"Row {idx}: {row.strip()}")

        layout.addWidget(list_widget)
        layout.addWidget(confirm_button)

        def confirm():
            dialog.done(list_widget.currentRow())

        confirm_button.clicked.connect(confirm)

        dialog.exec_()
        selected_row_index = list_widget.currentRow()

        if selected_row_index == -1:
            raise ValueError("Header row selection was canceled.")

        return selected_row_index   


    def toggle_gridlines(self):
        """Enable or disable gridlines."""
        show_grid = self.grid_checkbox.isChecked()
        self.plot_widget.showGrid(x=show_grid, y=show_grid)

    def toggle_secondary_axis(self, state):
        self.secondary_axis_enabled = state == Qt.Checked

    def parse_color(self, color_name):
        return pg.mkColor(color_name) if color_name != "Transparent" else pg.mkColor(0, 0, 0, 0)

    def plot_data(self):
        try:
            if self.data is None:
                QMessageBox.warning(self, "No Data", "Please load a CSV file first.")
                return

            x_col = self.x_dropdown.currentText()
            y_col = self.y_dropdown.currentText()
            y2_col = self.y2_dropdown.currentText()

            self.plot_widget.clear()

            # Re-enable cursor if enabled
            if self.cursor_checkbox.isChecked():
                self.plot_widget.addItem(self.cursor)
                self.plot_widget.addItem(self.cursor_label)

            # Primary Y-axis plot
            if x_col and y_col:
                valid_data = self.data[[x_col, y_col]].dropna()
                x_data = pd.to_numeric(valid_data[x_col], errors='coerce')
                y_data = pd.to_numeric(valid_data[y_col], errors='coerce')

                primary_pen = pg.mkPen(color='b', width=int(self.line_width_dropdown.currentText()))
                self.plot_widget.plot(x_data, y_data, pen=primary_pen)

                # Set X-axis and Y-axis labels
                self.plot_widget.setLabel('bottom', x_col, color='b')
                self.plot_widget.setLabel('left', y_col, color='b')

                # Set axis color to match the data
                self.plot_widget.getAxis('bottom').setPen(primary_pen)
                self.plot_widget.getAxis('left').setPen(primary_pen)

            # Secondary Y-axis plot
            if self.secondary_axis_enabled and x_col and y2_col:
                valid_data = self.data[[x_col, y2_col]].dropna()
                x_data = pd.to_numeric(valid_data[x_col], errors='coerce')
                y2_data = pd.to_numeric(valid_data[y2_col], errors='coerce')

                # Create secondary axis and ViewBox only once
                if not hasattr(self, "secondary_view"):
                    self.secondary_view = pg.ViewBox()
                    self.plot_widget.getPlotItem().scene().addItem(self.secondary_view)
                    self.plot_widget.getPlotItem().layout.addItem(self.secondary_view, 2, 1)
                    self.secondary_view.setXLink(self.plot_widget)
                    self.secondary_axis = pg.AxisItem("right")
                    self.plot_widget.getPlotItem().layout.addItem(self.secondary_axis, 2, 3)
                    self.secondary_axis.linkToView(self.secondary_view)

                secondary_pen = pg.mkPen(color='r', width=int(self.line_width_dropdown.currentText()))
                secondary_curve = pg.PlotDataItem(x_data, y2_data, pen=secondary_pen)
                self.secondary_view.addItem(secondary_curve)

                # Set range for secondary Y-axis
                y2_min, y2_max = y2_data.min(), y2_data.max()
                self.secondary_view.setYRange(y2_min, y2_max, padding=0.1)

                # Set secondary Y-axis label and color
                self.secondary_axis.setLabel(y2_col, color='r')
                self.secondary_axis.setPen(secondary_pen)

            # Apply gridlines if enabled
            self.toggle_gridlines()

        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))










def main():
    app = QApplication(sys.argv)

    # Splash Screen
    splash_pixmap = QPixmap("logo.png").scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    QTimer.singleShot(3000, splash.close)  # Display splash for 3 seconds

    # Launch Main Window
    window = CSVPlotterApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
