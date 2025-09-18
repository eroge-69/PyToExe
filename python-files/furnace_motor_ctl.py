import sys
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import Qt


class ArrowSliderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.direction_status = ''
        self.speed_status = 0
        self.welding_status = 0

        self.setWindowTitle("Slider and Arrow Buttons")
        self.setGeometry(100, 100, 700, 300)

        # Create a vertical layout
        self.layout = QVBoxLayout()

        self.combobox1 = QComboBox()
        self.isLeftorRight = False
        
        # ports = []
        self.port_data = []
        
        self.check_for_comports()
        

        self.com_desc_label = QLabel()
        self.com_desc_label.setText(f"Serial Port: {self.port_data[0]['Description']}") if len(self.port_data) != 0 else self.com_desc_label.setText('No ports found')
            
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton('Disconnect')
        self.refresh_button = QPushButton('↻')
        # self.button.setFixedSize(120, 60)
        
        # self.welding_checkbox = QCheckBox("Toggle welding")
        # self.welding_checkbox.stateChanged.connect(self.update_status_label)
        
        self.sel_button_stylesheet = """
                                        background-color: green; 
                                        border-style: outset; 
                                        border-width: 2px;
                                        border-radius: 10px;
                                        border-color: beige;
                                        font: bold 14px; 
                                        min-width: 10em;
                                        padding: 6px;
                                        color: white
                                        """
                                        
        self.unsel_button_stylesheet = """
                                            background-color: red; 
                                            border-style: outset; 
                                            border-width: 2px;
                                            border-radius: 10px;
                                            border-color: beige;
                                            font: bold 14px; 
                                            min-width: 7em;
                                            padding: 6px; 
                                            color: white
                                            """
        
        # self.combobox1.addItems([port['Name'] for port in self.port_data])
        self.combobox1.activated.connect(self.activated)
        self.connect_button.clicked.connect(lambda: self.onClick(True))
        self.disconnect_button.clicked.connect(lambda: self.onClick(False))
        self.refresh_button.clicked.connect(self.check_for_comports)
        
        self.serial_port_layout = QHBoxLayout()
        self.serial_port_layout.addWidget(self.combobox1)
        self.serial_port_layout.setSpacing(10)
        # self.serial_port_layout.addWidget(self.connect_button)
        # self.serial_port_layout.addWidget(self.disconnect_button) 
        self.serial_port_layout.addWidget(self.refresh_button)
        # self.serial_port_layout.addWidget(self.welding_checkbox)

        
        self.layout.addWidget(self.com_desc_label)
        self.layout.addLayout(self.serial_port_layout)

        self.carriage_start_stop = QPushButton('▶')
        self.carriage_start_stop.setCheckable(True)
        self.carriage_start_stop.clicked.connect(self.carriage_on_off_click)
        
        # Create the slider in the first row
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 255)  # Set slider range
        self.slider.setValue(0)      # Set default slider value
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(25)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.valuechange)
        self.header_for_speed = QLabel(f'Set Speed: 0') 
        self.layout.addWidget(self.header_for_speed)
        self.layout.addWidget(self.slider)

        # Create a horizontal layout for buttons in the second row
        button_layout = QHBoxLayout()

        # Create the left arrow button
        self.left_button = QPushButton("←", self)
        self.left_button.clicked.connect(self.on_left_button_click)  # Connect button click to function
        self.left_button.setStyleSheet(self.sel_button_stylesheet)
        button_layout.addWidget(self.left_button)

        # Create the right arrow button
        self.right_button = QPushButton("→", self)
        self.right_button.clicked.connect(self.on_right_button_click)  # Connect button click to function
        self.right_button.setStyleSheet(self.unsel_button_stylesheet)
        button_layout.addWidget(self.right_button)
        button_layout.addWidget(self.carriage_start_stop)

        # Add the button layout to the main vertical layout
        self.layout.addWidget(QLabel('Set Direction and Speed: '))
        self.layout.addLayout(button_layout)

        # Set the layout for the window
        self.setLayout(self.layout)
    
    def update_status_label(self, state):
        if state == Qt.Checked:
            self.welding_checkbox.setText("Checkbox state: Checked")
            self.welding_status = 1
            if self.carriage_start_stop.isChecked() and len(self.port_data) > 0:
                print(f"{self.direction_status} {self.speed_status} {self.welding_status}")
                self.send_serial_data()
            
        else:
            self.welding_checkbox.setText("Checkbox state: Unchecked")
            self.welding_status = 0
            if self.carriage_start_stop.isChecked() and len(self.port_data) > 0:
                print(f"{self.direction_status} {self.speed_status} {self.welding_status}")
                self.send_serial_data()
    
    def map_range(self, value, in_min, in_max, out_min, out_max):
        """
        Maps a value from one numerical range to another.

        Args:
            value: The input value to be mapped.
            in_min: The minimum value of the input range.
            in_max: The maximum value of the input range.
            out_min: The minimum value of the output range.
            out_max: The maximum value of the output range.

        Returns:
            The mapped value in the output range.
        """
        return ((value - in_min) / (in_max - in_min)) * (out_max - out_min) + out_min
    
    def send_serial_data(self):
        self.ser.write(f"{self.direction_status} {self.speed_status} {self.welding_status}".encode('utf-8'))
    
    def valuechange(self):

        if self.carriage_start_stop.isChecked() and len(self.port_data) > 0 and self.isLeftorRight == True:
            # self.ser.write(f'R {self.slider.value()}'.encode('utf-8'))
            self.direction_status = 'R'
            self.speed_status = self.slider.value()
            print(f"R {self.slider.value()} {self.welding_status}")
            self.send_serial_data()

        elif self.carriage_start_stop.isChecked() and len(self.port_data) > 0 and self.isLeftorRight == False:
            # self.ser.write(f'L {self.slider.value()}'.encode('utf-8'))
            self.direction_status = 'L'
            self.speed_status = self.slider.value()
            print(f"L {self.slider.value()} {self.welding_status}")
            self.send_serial_data()
        
        # self.header_for_speed.setText(f'Set Speed: {self.slider.value() / 10}')
        self.header_for_speed.setText(f'Set Speed: {self.slider.value()}')
  
    def check_for_comports(self):
        self.port_data = []
        
        for port in serial.tools.list_ports.comports():
            
            info = dict(
                {
                    "Name": port.name,
                    "Description": port.description,
                    "Manufacturer": port.manufacturer,
                    "Hwid": port.hwid,
                }
            ) 
            self.port_data.append(info)
            
        self.combobox1.clear()
        print(self.port_data)
        self.combobox1.addItems([port['Name'] for port in self.port_data])
        if len(self.port_data) > 0:
            self.ser = serial.Serial(f"{self.port_data[0]['Name']}", baudrate=9600)
    
    def closeEvent(self, event):
        if self.carriage_start_stop.isChecked() and len(self.port_data) > 0:
            self.ser.write(b'R 0 0\n')

        
    
    def onClick(self, check_click):
        if check_click:
            print('connect')
        else:
            print('disconnect')
  
    def carriage_on_off_click(self):
        if len(self.port_data) > 0:
            self.ser.write(b'R 0 0\n') if self.carriage_start_stop.isChecked() else self.ser.write(b'R 0 0\n')
            

    # Slot to handle left button click
    def on_left_button_click(self):
        self.clicked_left_button()
        if self.carriage_start_stop.isChecked() and len(self.port_data) > 0:
            # self.ser.write(f'L {self.slider.value()}'.encode('utf-8')) 
            self.speed_status = self.slider.value()
            self.direction_status = 'L'
            self.send_serial_data()
            print(f'L {self.slider.value()} {self.welding_status}')
        self.isLeftorRight = False
            
        # current_value = self.slider.value()
        # new_value = max(0, current_value - 1)  # Decrease slider value but ensure it doesn't go below 0
        # self.slider.setValue(new_value)

    # Slot to handle right button click
    def on_right_button_click(self):
        self.clicked_right_button()
        if self.carriage_start_stop.isChecked() and len(self.port_data) > 0:
            # self.ser.write(f'R {self.slider.value()}'.encode('utf-8'))
            self.speed_status = self.slider.value()
            self.direction_status = 'R'
            self.send_serial_data()
            print(f'R {self.slider.value()} {self.welding_status}')
        self.isLeftorRight = True
        # current_value = self.slider.value()
        # new_value = min(100, current_value + 1)  # Increase slider value but ensure it doesn't exceed 100
        # self.slider.setValue(new_value)
    
    def activated(self, index):
        # print("Activated index:", index)
        self.ser.close()
        self.com_desc_label.setText(f"Serial Port: {self.port_data[index]['Description']}")
        self.ser = serial.Serial(f"{self.port_data[index]['Name']}", baudrate=9600)
        
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key.Key_Space:
            # self.carriage_start_stop.setStyleSheet("background-color : lightblue, ")
            # self.carriage_start_stop.setText('⏸')
            self.carriage_start_stop.click()
            self.carriage_start_stop.setText('◼') if self.carriage_start_stop.isChecked() else self.carriage_start_stop.setText('▶')
            print(self.carriage_start_stop.isChecked())
        
        if event.key() == Qt.Key.Key_A:
            # Simulate left button click when the left arrow key is pressed
            self.left_button.click()
            self.clicked_left_button()

 
        elif event.key() == Qt.Key.Key_D:
            # Simulate right button click when the right arrow key is pressed
            self.right_button.click()
            self.clicked_right_button()

    
    def clicked_left_button(self):
            self.left_button.setStyleSheet(self.sel_button_stylesheet)
            self.right_button.setStyleSheet(self.unsel_button_stylesheet)
    
    def clicked_right_button(self):
            self.right_button.setStyleSheet(self.sel_button_stylesheet)
            self.left_button.setStyleSheet(self.unsel_button_stylesheet)


# Main loop
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArrowSliderWindow()
    window.show()
    sys.exit(app.exec())