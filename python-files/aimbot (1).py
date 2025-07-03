"code-keyword">import sys
"code-keyword">import time
"code-keyword">import threading
"code-keyword">from PyQt5.QtWidgets "code-keyword">import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QCheckBox, QSlider, QComboBox)
"code-keyword">from PyQt5.QtCore "code-keyword">import Qt, QTimer
"code-keyword">from PyQt5.QtGui "code-keyword">import QPalette, QColor
"code-keyword">import mss  # For screen capture (install: pip install mss)
"code-keyword">import numpy "code-keyword">as np  # For image processing (install: pip install numpy)
"code-keyword">import cv2  # For image processing (install: pip install opencv-python)
"code-keyword">import pydirectinput  # For mouse/keyboard control (install: pip install pydirectinput)
# Note: pydirectinput requires admin privileges.  Consider alternatives like PyAutoGUI
#       "code-keyword">if you have issues "code-keyword">with administrator access.  PyAutoGUI: pip install pyautogui

"code-keyword">class AimbotGUI(QWidget):
    "code-keyword">class="code-keyword">def __init__(self):
        super().__init__()
        self.setWindowTitle("Aimbot - Educational Sketch")
        self.setGeometry(100, 100, 400, 600)  # Adjusted window size

        self.dark_mode = True # default to dark mode
        self.toggle_theme()

        # Aimbot Parameters (These would be adjusted "code-keyword">in the GUI)
        self.aim_key = "alt"  # Key to activate the aimbot
        self.trigger_key = "shift" # Key to activate triggerbot
        self.target_color_hsv = (0, 255, 255)  # Example: bright red "code-keyword">in HSV
        self.color_tolerance = 20  # How much color variation to allow
        self.fov_width = 100  # Field of View Width
        self.fov_height = 100  # Field of View Height
        self.smoothing = 0.1  # Mouse smoothing factor (0 to 1)
        self.triggerbot_enabled = False
        self.aimbot_enabled = False
        self.screen_width = 1920  # Replace "code-keyword">with your actual screen width
        self.screen_height = 1080  # Replace "code-keyword">with your actual screen height

        self.running = True # control the main loop

        self.initUI()

        # Start the aimbot thread
        self.aimbot_thread = threading.Thread(target=self.aimbot_loop, daemon=True)
        self.aimbot_thread.start()

        self.triggerbot_thread = threading.Thread(target=self.triggerbot_loop, daemon=True)
        self.triggerbot_thread.start()


    "code-keyword">class="code-keyword">def initUI(self):
        # --- Labels "code-keyword">and Input Fields ---
        self.aim_key_label = QLabel("Aim Key:")
        self.aim_key_input = QLineEdit(self.aim_key)

        self.trigger_key_label = QLabel("Trigger Key:")
        self.trigger_key_input = QLineEdit(self.trigger_key)

        self.color_label = QLabel("Target Color (HSV - H):")
        self.color_input = QLineEdit(str(self.target_color_hsv[0]))

        self.tolerance_label = QLabel("Color Tolerance:")
        self.tolerance_input = QLineEdit(str(self.color_tolerance))

        self.fov_width_label = QLabel("FOV Width:")
        self.fov_width_input = QLineEdit(str(self.fov_width))

        self.fov_height_label = QLabel("FOV Height:")
        self.fov_height_input = QLineEdit(str(self.fov_height))

        self.smoothing_label = QLabel("Smoothing:")
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setMinimum(0)
        self.smoothing_slider.setMaximum(100)
        self.smoothing_slider.setValue(int(self.smoothing * 100))
        self.smoothing_slider.valueChanged.connect(self.update_smoothing)

        # --- Checkboxes ---
        self.triggerbot_checkbox = QCheckBox("Enable Triggerbot")
        self.triggerbot_checkbox.stateChanged.connect(self.toggle_triggerbot)

        self.aimbot_checkbox = QCheckBox("Enable Aimbot")
        self.aimbot_checkbox.stateChanged.connect(self.toggle_aimbot)

        # Dark Theme Toggle
        self.dark_theme_button = QPushButton("Toggle Theme")
        self.dark_theme_button.clicked.connect(self.toggle_theme)

        # --- Layout ---
        vbox = QVBoxLayout()

        vbox.addWidget(self.aim_key_label)
        vbox.addWidget(self.aim_key_input)

        vbox.addWidget(self.trigger_key_label)
        vbox.addWidget(self.trigger_key_input)

        vbox.addWidget(self.color_label)
        vbox.addWidget(self.color_input)

        vbox.addWidget(self.tolerance_label)
        vbox.addWidget(self.tolerance_input)

        vbox.addWidget(self.fov_width_label)
        vbox.addWidget(self.fov_width_input)

        vbox.addWidget(self.fov_height_label)
        vbox.addWidget(self.fov_height_input)

        vbox.addWidget(self.smoothing_label)
        vbox.addWidget(self.smoothing_slider)

        vbox.addWidget(self.triggerbot_checkbox)
        vbox.addWidget(self.aimbot_checkbox)

        vbox.addWidget(self.dark_theme_button)

        self.setLayout(vbox)


    "code-keyword">class="code-keyword">def update_smoothing(self, value):
        self.smoothing = value / 100.0

    "code-keyword">class="code-keyword">def toggle_triggerbot(self, state):
        self.triggerbot_enabled = (state == Qt.Checked)

    "code-keyword">class="code-keyword">def toggle_aimbot(self, state):
        self.aimbot_enabled = (state == Qt.Checked)


    "code-keyword">class="code-keyword">def toggle_theme(self):
        self.dark_mode = "code-keyword">not self.dark_mode
        "code-keyword">if self.dark_mode:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)
        "code-keyword">else:
            self.setPalette(QPalette()) # Resets to the default theme

    "code-keyword">class="code-keyword">def is_color_in_range(self, color, target_color, tolerance):
        # Simple color distance check (can be improved)
        distance = sum([(a - b) ** 2 "code-keyword">for a, b "code-keyword">in zip(color, target_color)])
        "code-keyword">return distance <= tolerance ** 2

    "code-keyword">class="code-keyword">def aimbot_loop(self):
        "code-keyword">with mss.mss() "code-keyword">as sct:
            monitor = sct.monitors[1]  # 0 "code-keyword">is all monitors, 1 "code-keyword">is the primary
            "code-keyword">while self.running:
                "code-keyword">if self.aimbot_enabled "code-keyword">and pydirectinput.is_pressed(self.aim_key):  # Replace "code-keyword">with your keybind library
                    # Capture a region of the screen (FOV)
                    screen_width = self.screen_width  # Replace "code-keyword">with your screen width
                    screen_height = self.screen_height # Replace "code-keyword">with your screen height
                    fov_width = int(self.fov_width_input.text())  # Get FOV "code-keyword">from input
                    fov_height = int(self.fov_height_input.text())  # Get FOV "code-keyword">from input

                    x = (screen_width // 2) - (fov_width // 2)
                    y = (screen_height // 2) - (fov_height // 2)

                    bbox = (x, y, x + fov_width, y + fov_height)  # Bounding box
                    sct_img = sct.grab(bbox)
                    img = np.array(sct_img)
                    img_bgr = cv2.cvtColor(img, cv2.RGBA2BGR) # convert RGBA to BGR

                    # Convert to HSV
                    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

                    # Get target color "code-keyword">and tolerance "code-keyword">from GUI
                    target_hue = int(self.color_input.text()) # Get hue "code-keyword">from text input
                    tolerance = int(self.tolerance_input.text()) # Get color tolerance "code-keyword">from text input

                    # Define the color range
                    lower_color = np.array([max(0, target_hue - tolerance), 50, 50]) # Example values "code-keyword">for S "code-keyword">and V
                    upper_color = np.array([min(255, target_hue + tolerance), 255, 255])

                    # Create a mask to only select the pixels "code-keyword">in the color range
                    mask = cv2.inRange(hsv, lower_color, upper_color)

                    # Find the coordinates of the pixels that match the target color
                    coords = np.column_stack(np.where(mask > 0))

                    "code-keyword">if len(coords) > 0:
                        # Calculate the average x "code-keyword">and y coordinates of the target pixels
                        x_avg = np.mean(coords[:, 1])
                        y_avg = np.mean(coords[:, 0])

                        # Calculate the relative position of the target "code-keyword">in the FOV
                        x_rel = x_avg - (fov_width // 2)
                        y_rel = y_avg - (fov_height // 2)

                        # Adjust mouse position
                        smoothing = float(self.smoothing_slider.value()) / 100.0 # Smoothing value "code-keyword">from the slider

                        "code-keyword">if abs(x_rel) > 5 "code-keyword">or abs(y_rel) > 5:
                            pydirectinput.move(int(x_rel * smoothing), int(y_rel * smoothing))


                time.sleep(0.005)  # Small delay to avoid hogging CPU

    "code-keyword">class="code-keyword">def triggerbot_loop(self):
        "code-keyword">with mss.mss() "code-keyword">as sct:
            monitor = sct.monitors[1]  # 0 "code-keyword">is all monitors, 1 "code-keyword">is the primary
            "code-keyword">while self.running:
                "code-keyword">if self.triggerbot_enabled "code-keyword">and pydirectinput.is_pressed(self.trigger_key):
                    # Capture a small region around the crosshair
                    screen_width = self.screen_width  # Replace "code-keyword">with your screen width
                    screen_height = self.screen_height # Replace "code-keyword">with your screen height
                    crosshair_size = 5  # Adjust the size of the capture area

                    x = (screen_width // 2) - (crosshair_size // 2)
                    y = (screen_height // 2) - (crosshair_size // 2)

                    bbox = (x, y, x + crosshair_size, y + crosshair_size)
                    sct_img = sct.grab(bbox)
                    img = np.array(sct_img)
                    img_bgr = cv2.cvtColor(img, cv2.RGBA2BGR)

                    # Convert the captured region to HSV
                    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

                    # Get target color "code-keyword">and tolerance "code-keyword">from GUI
                    target_hue = int(self.color_input.text()) # Get hue "code-keyword">from text input
                    tolerance = int(self.tolerance_input.text()) # Get color tolerance "code-keyword">from text input

                    # Define the color range
                    lower_color = np.array([max(0, target_hue - tolerance), 50, 50])
                    upper_color = np.array([min(255, target_hue + tolerance), 255, 255])

                    # Create a mask to only select the pixels "code-keyword">in the color range
                    mask = cv2.inRange(hsv, lower_color, upper_color)

                    # Check "code-keyword">if any pixel "code-keyword">in the crosshair region matches the target color
                    "code-keyword">if np.any(mask):
                        # Simulate a mouse click
                        pydirectinput.mouseDown()
                        time.sleep(0.01)  # Short delay to simulate a tap
                        pydirectinput.mouseUp()

                time.sleep(0.005)  # Small delay

    "code-keyword">class="code-keyword">def closeEvent(self, event):
        self.running = False # Stop the thread when the window closes
        self.aimbot_thread.join()
        self.triggerbot_thread.join()
        event.accept() # Let the window close


"code-keyword">if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AimbotGUI()
    ex.show()
    sys.exit(app.exec_())