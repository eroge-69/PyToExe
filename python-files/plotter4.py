import sys
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter  # Explicitly import the ImageExporter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QComboBox, QFileDialog, QMessageBox, QCheckBox, QHBoxLayout, QDialog, QListWidget, QSplashScreen
)
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
        self.setGeometry(100, 100, 900, 700)

        self.data = None
        self.secondary_axis_enabled = False
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Load CSV Button
        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_button)

        # X-axis selection
        self.x_label = QLabel("X-axis:")
        self.layout.addWidget(self.x_label)
        self.x_dropdown = QComboBox()
        self.layout.addWidget(self.x_dropdown)

        # Y-axis selection
        self.y_label = QLabel("Y-axis:")
        self.layout.addWidget(self.y_label)
        self.y_dropdown = QComboBox()
        self.layout.addWidget(self.y_dropdown)

        # Secondary Y-axis selection
        self.y2_label = QLabel("Secondary Y-axis:")
        self.layout.addWidget(self.y2_label)
        self.y2_dropdown = QComboBox()
        self.layout.addWidget(self.y2_dropdown)

        # Secondary Y-axis enable/disable checkbox
        self.secondary_axis_checkbox = QCheckBox("Enable Secondary Y-axis")
        self.secondary_axis_checkbox.stateChanged.connect(self.toggle_secondary_axis)
        self.layout.addWidget(self.secondary_axis_checkbox)

        # Secondary Y-axis customization controls
        secondary_customization_layout = QHBoxLayout()

        self.line_dropdown_secondary = QComboBox()
        self.line_dropdown_secondary.addItems(["Solid", "Dashed", "Dotted", "DashDot"])
        secondary_customization_layout.addWidget(QLabel("Secondary Line Style:"))
        secondary_customization_layout.addWidget(self.line_dropdown_secondary)

        self.line_width_dropdown_secondary = QComboBox()
        self.line_width_dropdown_secondary.addItems(["1", "2", "3", "4", "5"])
        secondary_customization_layout.addWidget(QLabel("Secondary Line Width:"))
        secondary_customization_layout.addWidget(self.line_width_dropdown_secondary)

        self.symbol_size_dropdown_secondary = QComboBox()
        self.symbol_size_dropdown_secondary.addItems(["Small", "Medium", "Large"])
        secondary_customization_layout.addWidget(QLabel("Secondary Symbol Size:"))
        secondary_customization_layout.addWidget(self.symbol_size_dropdown_secondary)

        self.symbol_fill_dropdown_secondary = QComboBox()
        self.symbol_fill_dropdown_secondary.addItems(["Transparent", "Gray", "White"])
        secondary_customization_layout.addWidget(QLabel("Secondary Fill Color:"))
        secondary_customization_layout.addWidget(self.symbol_fill_dropdown_secondary)

        self.symbol_line_dropdown_secondary = QComboBox()
        self.symbol_line_dropdown_secondary.addItems(["Transparent", "Gray", "White"])
        secondary_customization_layout.addWidget(QLabel("Secondary Outline Color:"))
        secondary_customization_layout.addWidget(self.symbol_line_dropdown_secondary)

        self.layout.addLayout(secondary_customization_layout)


        # Gridlines checkbox
        self.grid_checkbox = QCheckBox("Show Gridlines")
        self.grid_checkbox.stateChanged.connect(self.toggle_gridlines)
        self.layout.addWidget(self.grid_checkbox)

        # Combined customization options
        customization_layout = QHBoxLayout()
        self.line_dropdown = QComboBox()
        self.line_dropdown.addItems(["Solid", "Dashed", "Dotted", "DashDot"])
        customization_layout.addWidget(QLabel("Line Style:"))
        customization_layout.addWidget(self.line_dropdown)

        self.line_width_dropdown = QComboBox()
        self.line_width_dropdown.addItems(["1", "2", "3", "4", "5"])
        customization_layout.addWidget(QLabel("Line Width:"))
        customization_layout.addWidget(self.line_width_dropdown)

        self.symbol_size_dropdown = QComboBox()
        self.symbol_size_dropdown.addItems(["Small", "Medium", "Large"])
        customization_layout.addWidget(QLabel("Symbol Size:"))
        customization_layout.addWidget(self.symbol_size_dropdown)

        self.symbol_fill_dropdown = QComboBox()
        self.symbol_fill_dropdown.addItems(["Transparent", "Gray", "White"])
        self.symbol_fill_dropdown.setCurrentText("Transparent")  # Default to Transparent
        customization_layout.addWidget(QLabel("Fill Color:"))
        customization_layout.addWidget(self.symbol_fill_dropdown)

        self.symbol_line_dropdown = QComboBox()
        self.symbol_line_dropdown.addItems(["Transparent", "Gray", "White"])
        self.symbol_line_dropdown.setCurrentText("Transparent")  # Default to Transparent
        customization_layout.addWidget(QLabel("Outline Color:"))
        customization_layout.addWidget(self.symbol_line_dropdown)

        self.layout.addLayout(customization_layout)

        # Plot Button
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_data)
        self.layout.addWidget(self.plot_button)

        # Export Button
        self.export_button = QPushButton("Export Plot as JPEG")
        self.export_button.clicked.connect(self.export_plot)
        self.layout.addWidget(self.export_button)

        # PyQtGraph Plot Widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Add the logo in the bottom right corner
        logo_pixmap = QPixmap("logo.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.layout.addWidget(self.logo_label)



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
        show = self.grid_checkbox.isChecked()
        self.plot_widget.showGrid(x=show, y=show)

    def toggle_secondary_axis(self):
        self.secondary_axis_enabled = self.secondary_axis_checkbox.isChecked()

        if not self.secondary_axis_enabled:
            # Clear and remove the secondary axis and its data
            if hasattr(self, 'secondary_view'):
                self.secondary_view.clear()
                self.plot_widget.scene().removeItem(self.secondary_view)
                del self.secondary_view
            if hasattr(self, 'axis2'):
                self.plot_widget.getPlotItem().layout.removeItem(self.axis2)
                del self.axis2

            self.plot_widget.update()

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

            # Primary Y-Axis Plot
            if x_col and y_col:
                valid_data = self.data[[x_col, y_col]].dropna()
                x_data = pd.to_numeric(valid_data[x_col], errors='coerce')
                y_data = pd.to_numeric(valid_data[y_col], errors='coerce')

                if x_data.empty or y_data.empty:
                    raise ValueError("Selected columns contain no numeric data after cleaning.")

                primary_color = 'b'
                line_width = int(self.line_width_dropdown.currentText())
                line_style = {"Solid": Qt.SolidLine, "Dashed": Qt.DashLine, "Dotted": Qt.DotLine, "DashDot": Qt.DashDotLine}[self.line_dropdown.currentText()]
                symbol_size = {"Small": 5, "Medium": 10, "Large": 15}[self.symbol_size_dropdown.currentText()]
                symbol_fill = self.parse_color(self.symbol_fill_dropdown.currentText())
                symbol_line = self.parse_color(self.symbol_line_dropdown.currentText())

                self.plot_widget.plot(
                    x_data, y_data,
                    pen=pg.mkPen(color=primary_color, width=line_width, style=line_style),
                    symbol='o',
                    symbolSize=symbol_size,
                    symbolBrush=symbol_fill,
                    symbolPen=symbol_line
                )
                self.plot_widget.getAxis('left').setPen(pg.mkPen(primary_color))
                self.plot_widget.getAxis('left').setTextPen(pg.mkPen(primary_color))

            # Secondary Y-Axis Plot
            if self.secondary_axis_enabled and x_col and y2_col:
                valid_data = self.data[[x_col, y2_col]].dropna()
                x_data = pd.to_numeric(valid_data[x_col], errors='coerce')
                y2_data = pd.to_numeric(valid_data[y2_col], errors='coerce')

                if x_data.empty or y2_data.empty:
                    raise ValueError("Secondary Y-axis columns contain no numeric data after cleaning.")

                # Ensure secondary ViewBox and axis are created only once
                if not hasattr(self, 'secondary_view'):
                    self.secondary_view = pg.ViewBox()
                    self.plot_widget.scene().addItem(self.secondary_view)
                    self.plot_widget.getPlotItem().layout.addItem(self.secondary_view, 2, 1)
                    self.secondary_view.setXLink(self.plot_widget.getViewBox())

                if not hasattr(self, 'axis2'):
                    self.axis2 = pg.AxisItem("right")
                    self.plot_widget.getPlotItem().layout.addItem(self.axis2, 2, 3)
                    self.axis2.linkToView(self.secondary_view)

                secondary_color = 'r'
                line_width_secondary = int(self.line_width_dropdown_secondary.currentText())
                line_style_secondary = {"Solid": Qt.SolidLine, "Dashed": Qt.DashLine, "Dotted": Qt.DotLine, "DashDot": Qt.DashDotLine}[self.line_dropdown_secondary.currentText()]
                symbol_size_secondary = {"Small": 5, "Medium": 10, "Large": 15}[self.symbol_size_dropdown_secondary.currentText()]
                symbol_fill_secondary = self.parse_color(self.symbol_fill_dropdown_secondary.currentText())
                symbol_line_secondary = self.parse_color(self.symbol_line_dropdown_secondary.currentText())

                curve2 = pg.PlotDataItem(
                    x_data, y2_data,
                    pen=pg.mkPen(color=secondary_color, width=line_width_secondary, style=line_style_secondary),
                    symbol='o',
                    symbolSize=symbol_size_secondary,
                    symbolBrush=symbol_fill_secondary,
                    symbolPen=symbol_line_secondary
                )
                self.secondary_view.addItem(curve2)

                y2_min, y2_max = y2_data.min(), y2_data.max()
                if pd.notna(y2_min) and pd.notna(y2_max):
                    self.secondary_view.setYRange(y2_min, y2_max, padding=0.1)
                else:
                    raise ValueError("Secondary Y-axis data has an invalid range.")

                self.axis2.setPen(pg.mkPen(secondary_color))
                self.axis2.setTextPen(pg.mkPen(secondary_color))

            # Update axis titles dynamically
            self.update_axis_titles()

        except Exception as e:
            self.log_error(f"Failed to plot data: {e}")
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
