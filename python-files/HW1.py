import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QLabel, QFileDialog, QHBoxLayout, QSizePolicy,
    QSlider, QGroupBox, QRadioButton, QSpacerItem
)
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QCategoryAxis
)

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("64x64 Image Processor - Arithmetic Operations")
        self.setGeometry(100, 100, 1400, 1200)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        self.image_array1 = None
        self.image_array2 = None

        # --- Top Row: Input Images Section ---
        input_images_layout = QHBoxLayout()
        main_layout.addLayout(input_images_layout)

        # Section for Image 1
        self.section1_layout = QVBoxLayout()
        input_images_layout.addLayout(self.section1_layout)
        
        self.btn_browse1 = QPushButton("Upload Image 1")
        self.btn_browse1.clicked.connect(lambda: self.browse_file(1))
        self.section1_layout.addWidget(self.btn_browse1)
        
        self.image1_and_chart_layout = QHBoxLayout()
        self.label_image1 = QLabel("Image 1")
        self.label_image1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image1.setFixedSize(300, 300)
        self.image1_and_chart_layout.addWidget(self.label_image1)
        
        self.chart_view1 = QChartView()
        self.chart_view1.setFixedSize(300, 300)
        self.chart_view1.setVisible(False)
        self.image1_and_chart_layout.addWidget(self.chart_view1)
        
        self.section1_layout.addLayout(self.image1_and_chart_layout)

        # Section for Image 2
        self.section2_layout = QVBoxLayout()
        input_images_layout.addLayout(self.section2_layout)
        
        self.btn_browse2 = QPushButton("Upload Image 2")
        self.btn_browse2.clicked.connect(lambda: self.browse_file(2))
        self.section2_layout.addWidget(self.btn_browse2)
        
        self.image2_and_chart_layout = QHBoxLayout()
        self.label_image2 = QLabel("Image 2")
        self.label_image2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image2.setFixedSize(300, 300)
        self.image2_and_chart_layout.addWidget(self.label_image2)
        
        self.chart_view2 = QChartView()
        self.chart_view2.setFixedSize(300, 300)
        self.chart_view2.setVisible(False)
        self.image2_and_chart_layout.addWidget(self.chart_view2)
        
        self.section2_layout.addLayout(self.image2_and_chart_layout)

        # --- Bottom Row: Operations Section ---
        bottom_row_layout = QHBoxLayout()
        main_layout.addLayout(bottom_row_layout)
        
        # Control Panel for Operations
        control_panel = QVBoxLayout()
        bottom_row_layout.addLayout(control_panel, 1)
        
        # Q1: Add or Subtract
        q1_groupbox = QGroupBox("Add or Subtract Constant")
        q1_layout = QVBoxLayout(q1_groupbox)
        self.slider_add_sub = QSlider(Qt.Orientation.Horizontal)
        self.slider_add_sub.setRange(-31, 31)
        self.slider_add_sub.setSingleStep(1)
        self.slider_add_sub.setValue(0)
        self.slider_add_sub.valueChanged.connect(self.update_add_sub_value)
        self.add_sub_label = QLabel("Constant: 0")
        q1_layout.addWidget(self.slider_add_sub)
        q1_layout.addWidget(self.add_sub_label)
        self.btn_apply_add_sub = QPushButton("Apply Add/Subtract")
        self.btn_apply_add_sub.clicked.connect(self.apply_add_subtract)
        q1_layout.addWidget(self.btn_apply_add_sub)
        control_panel.addWidget(q1_groupbox)
        
        # Q2: Multiply
        q2_groupbox = QGroupBox("Multiply Constant")
        q2_layout = QVBoxLayout(q2_groupbox)
        self.slider_mult = QSlider(Qt.Orientation.Horizontal)
        self.slider_mult.setRange(0, 31)
        self.slider_mult.setSingleStep(1)
        self.slider_mult.setValue(1)
        self.slider_mult.valueChanged.connect(self.update_mult_value)
        self.mult_label = QLabel("Constant: 1")
        q2_layout.addWidget(self.slider_mult)
        q2_layout.addWidget(self.mult_label)
        self.btn_apply_mult = QPushButton("Apply Multiply")
        self.btn_apply_mult.clicked.connect(self.apply_multiply)
        q2_layout.addWidget(self.btn_apply_mult)
        control_panel.addWidget(q2_groupbox)
        
        # Q3: Average
        self.btn_average = QPushButton("Create Average Image")
        self.btn_average.clicked.connect(self.create_average_image)
        control_panel.addWidget(self.btn_average)
        
        # Q4: g(x,y) = f(x,y) - f(x-1,y)
        self.btn_fx = QPushButton("g(x,y) = f(x,y) - f(x-1,y)")
        self.btn_fx.clicked.connect(self.apply_fx_operation)
        control_panel.addWidget(self.btn_fx)
        
        control_panel.addStretch()

        # Output Section
        output_layout = QHBoxLayout()
        bottom_row_layout.addLayout(output_layout, 2)
        
        self.output_label = QLabel("Output Image")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        output_layout.addWidget(self.output_label)

        self.output_image_and_chart_layout = QHBoxLayout()
        self.label_output_image = QLabel("Output Image Histogram")
        self.label_output_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_output_image.setFixedSize(400, 400)
        self.output_image_and_chart_layout.addWidget(self.label_output_image)
        
        self.output_chart_view = QChartView()
        self.output_chart_view.setFixedSize(400, 400)
        self.output_chart_view.setVisible(False)
        self.output_image_and_chart_layout.addWidget(self.output_chart_view)
        
        output_layout.addLayout(self.output_image_and_chart_layout)

    def browse_file(self, image_num):
        file_name, _ = QFileDialog.getOpenFileName(
            self, f"Open Image {image_num}", ".", "Image Files (*.64)"
        )
        if not file_name:
            return

        try:
            with open(file_name, 'r') as f:
                data_string = f.read().replace('\n', '').replace('\r', '')

            image_array = np.zeros((64, 64), dtype=np.uint8)
            for i in range(64):
                for j in range(64):
                    char = data_string[i * 64 + j]
                    if '0' <= char <= '9':
                        value = ord(char) - ord('0')
                    elif 'A' <= char <= 'Z':
                        value = ord(char) - ord('A') + 10
                    else:
                        value = 0
                    image_array[i, j] = value

            display_array = image_array * 8
            q_image = QImage(display_array.data, 64, 64, 64, QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)

            if image_num == 1:
                self.label_image1.setPixmap(scaled_pixmap)
                self.image_array1 = image_array
                self.create_and_display_histogram_chart(self.image_array1, self.chart_view1, "Image 1 Histogram")
            elif image_num == 2:
                self.label_image2.setPixmap(scaled_pixmap)
                self.image_array2 = image_array
                self.create_and_display_histogram_chart(self.image_array2, self.chart_view2, "Image 2 Histogram")
        
        except Exception as e:
            error_msg = f"Error processing file: {e}"
            if image_num == 1:
                self.label_image1.setText(error_msg)
            elif image_num == 2:
                self.label_image2.setText(error_msg)

    def create_and_display_histogram_chart(self, image_array, chart_view, title):
        histogram_data = np.bincount(image_array.flatten(), minlength=32)

        bar_set = QBarSet("Frequency")
        for count in histogram_data:
            bar_set.append(int(count))

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        axis_x.setTitleText("Gray Level")
        for i in range(32):
            axis_x.append(str(i), i)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Frequency")
        axis_y.setLabelFormat("%i")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view.setChart(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setVisible(True)

    def update_add_sub_value(self, value):
        self.add_sub_label.setText(f"Constant: {value}")

    def update_mult_value(self, value):
        self.mult_label.setText(f"Constant: {value}")
        
    def display_output(self, output_image_array, title):
        output_display_array = output_image_array * 8
        q_image = QImage(output_display_array.data, 64, 64, 64, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.label_output_image.setPixmap(scaled_pixmap)
        self.create_and_display_histogram_chart(output_image_array, self.output_chart_view, title)

    # --- Arithmetic Operations ---
    
    def apply_add_subtract(self):
        if self.image_array1 is None:
            self.output_label.setText("Please upload Image 1 first.")
            return
        else:
            self.output_label.setText("Output Image")

        constant = self.slider_add_sub.value()
        processed_array = self.image_array1.astype(np.int16) + constant
        
        # Clamp values to the 0-31 range
        processed_array = np.clip(processed_array, 0, 31).astype(np.uint8)
        
        if constant >= 0:
            self.display_output(processed_array, f"Image + {constant}")
        else:
            self.display_output(processed_array, f"Image - {abs(constant)}")
        
    def apply_multiply(self):
        if self.image_array1 is None:
            self.output_label.setText("Please upload Image 1 first.")
            return
        else:
            self.output_label.setText("Output Image")

        constant = self.slider_mult.value()
        processed_array = self.image_array1.astype(np.int16) * constant
        
        # Scale to 0-31 range
        processed_array = np.clip(processed_array, 0, 31).astype(np.uint8)
        
        self.display_output(processed_array, f"Image * {constant}")

    def create_average_image(self):
        if self.image_array1 is None or self.image_array2 is None:
            self.output_label.setText("Please upload both images first.")
            return
        else:
            self.output_label.setText("Output Image")
            
        # Calculate the average and round to the nearest integer
        average_array = (self.image_array1.astype(np.int16) + self.image_array2.astype(np.int16)) / 2
        average_array = np.round(average_array).astype(np.uint8)

        self.display_output(average_array, "Average Image")
        
    def apply_fx_operation(self):
        if self.image_array1 is None:
            self.output_label.setText("Please upload Image 1 first.")
            return
        else:
            self.output_label.setText("Output Image")
            
        processed_array = np.zeros_like(self.image_array1, dtype=np.int16)
        
        # Apply the formula g(x,y) = f(x,y) - f(x-1,y)
        processed_array[:, 1:] = self.image_array1[:, 1:] - self.image_array1[:, :-1]
        
        # Shift and scale the result to fit in the 0-31 range for display
        min_val = np.min(processed_array)
        max_val = np.max(processed_array)
        
        if max_val != min_val:
            processed_array = 31 * (processed_array - min_val) / (max_val - min_val)
        else:
            processed_array.fill(15) # Center the value if no change
        
        processed_array = processed_array.astype(np.uint8)
        
        self.display_output(processed_array, "g(x,y) = f(x,y) - f(x-1,y)")

def main():
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()