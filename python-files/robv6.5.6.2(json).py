import sys
import os
import time
import threading
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtGui import QPixmap, QImage, QColor, QCursor, QPainter, QPalette, QBrush, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QGraphicsDropShadowEffect, QFrame, QSpacerItem, QSizePolicy, QStackedLayout, QMenu, QAction, QDialog, QLineEdit, QMessageBox, QWidgetAction, QGraphicsDropShadowEffect

#from xarm import version
from xarm import __version__ as version
from xarm.wrapper import XArmAPI
import mediapipe as mp

#import camera
# from ultralytics import YOLO
import json
import os

with open("robot_trigger.json", "r") as f:
    trigger_config = json.load(f)
with open("robot_limits.json", "r") as f: 
    robot_limits = json.load(f)

# Robot control class
class RobotMain:
    def __init__(self, robot):
        self._arm = robot
        self._tcp_speed = 300
        self._tcp_acc = 700
        self.is_busy = threading.Event() 
        self.moves = self._load_moves()
        self._init_robot()

    def _init_robot(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)

    def _load_moves(self):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, "robot_position.json")
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Robot] Failed to load movement file: {e}")
            return {}
        
    def _run_sequence(self, name):
        if name not in self.moves:
            print(f"[Robot] Sequence '{name}' not found.")
            return

        try:
            for step in self.moves[name]:
                if "action" in step:
                    if step["action"] == "open_lite6_gripper":
                        code = self._arm.open_lite6_gripper()
                    elif step["action"] == "close_lite6_gripper":
                        code = self._arm.close_lite6_gripper()
                    else:
                        print(f"[Robot] Unknown action: {step['action']}")
                        continue
                elif "pos" in step:
                    self._tcp_speed = step["speed"]
                    code = self._arm.set_position(
                        *step["pos"],
                        speed=step["speed"],
                        mvacc=step["accel"],
                        radius=0.0,
                        wait=step.get("wait", True)
                    )
                else:
                    print("[Robot] Invalid step format.")
                    continue

                if not self._check_code(code, f"{name} step"):
                    return

            self._tcp_speed = 300  # Reset speed after sequence

        except Exception as e:
            print(f"[RobotMain][Exception]: {e}")
            self._reset_robot()

    def _check_code(self, code, label=''):
        if code != 0:
            print(f"[Robot][Error] {label} failed with code: {code}")
            return False
        return True
    
    @staticmethod
    def pprint(msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def _reset_robot(self):
        
        for _ in range(3):
            self._arm.clean_warn()
            self._arm.clean_error()
            time.sleep(0.5)

        # Ensure motion is enabled
        code = self._arm.motion_enable(True)
        if code != 0:
            print(f"[Robot] motion_enable failed with code {code}")

        # Set mode and state (ready to move)
        self._arm.set_mode(0)    # Position mode
        self._arm.set_state(0)   # Ready
        time.sleep(1)

        print("[Robot] Robot reset complete and ready (no movement performed).")
    
    def _reset_and_clear_busy(self):
        self._reset_robot()
        self.is_busy.clear()  # allow movement again

    def move_to(self, x, y, z):
        if self.is_busy.is_set():  # robot is busy (e.g., resetting)
            return  # skip sending moves

        code = self._arm.set_position(
            x, y, z, 180, 0, 0,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            wait=False,
            radius=5
        )
        if code != 0:
            print(f"[Robot] Move failed: code {code}. Resetting robot...")
            self.is_busy.set()  # block further movement
            threading.Thread(target=self._reset_and_clear_busy, daemon=True).start()

    def open_gripper(self):
        self._arm.open_lite6_gripper()

    def close_gripper(self):
        self._arm.close_lite6_gripper()

    def move_pick1(self):

        self._run_sequence("pick1")

    def move_pick2(self):

       self._run_sequence("pick2")

    def move_place1(self):

        self._run_sequence("place1")

    def move_place2(self):

        self._run_sequence("place2")

# ============================
# Mapping & Filtering
# ============================
def map_coord(value, input_range, output_range):
    input_min, input_max = input_range
    output_min, output_max = output_range
    return output_min + (value - input_min) / (input_max - input_min) * (output_max - output_min)

def smooth_position(prev, curr, alpha=0.5):
    return alpha * curr + (1 - alpha) * prev

def is_hand_closed(hand_landmarks):
    def is_folded(tip, pip):
        return hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y

    return all([
        is_folded(8, 6),   # index
        is_folded(12, 10), # middle
        is_folded(16, 14), # ring
        is_folded(20, 18)  # pinky
    ])
def is_hand_open(hand_landmarks):
    def is_extended(tip, pip):
        return hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y  # tip above pip

    return all([
        is_extended(8, 6),   # index
        is_extended(12, 10), # middle
        is_extended(16, 14), # ring
        is_extended(20, 18)  # pinky
        # Thumb is excluded to avoid false blocking on open palm
    ])

# Main GUI class
class RobotW(QMainWindow):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.current_step = 0
        self.script_dir = os.path.dirname(__file__)

        self.setWindowIcon(QIcon(os.path.join(self.script_dir, 'OIP.jpg')))

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        # Calculate a suitable window size (e.g., 90% of the screen size)
        window_width = int(0.9 * self.screen_width)
        window_height = int(0.9 * self.screen_height)

        # Set the window geometry within the screen's constraints
        self.setGeometry(0, 0, window_width, window_height)

        # Ensure the window doesn't exceed the screen size
        self.setMinimumSize(int(0.5 * self.screen_width), int(0.5 * self.screen_height))
        self.setMaximumSize(self.screen_width, self.screen_height)

        # Ensure all widgets inside scale according to the window size
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize other components
        self.init_files()
        self.init_title_frame()

        # Maximize the window
        self.showMaximized()

        self.setWindowTitle("Robot")
        self.setWindowState(Qt.WindowMaximized)

    def init_files(self):
        self.script_dir = os.path.dirname(__file__)
        self.title_image = os.path.join(self.script_dir, 'title_bg.png')
        self.background_image = os.path.join(self.script_dir, 'main_bg.png')

    def show_title_screen(self):
        self.init_title_frame()

    def init_title_frame(self):
        container = QWidget()
        self.setCentralWidget(container)

        background_pixmap = QPixmap(self.title_image)
        if not background_pixmap.isNull():
            # Calculate the size of the pixmap while maintaining the aspect ratio
            scaled_pixmap = background_pixmap.scaled(self.screen_width, self.screen_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create a QPixmap for the background
            final_pixmap = QPixmap(self.screen_width, self.screen_height)
            final_pixmap.fill(Qt.transparent)  # Fill it with transparency

            # Calculate the position to center the background image
            x_offset = (self.screen_width - scaled_pixmap.width()) // 2
            y_offset = (self.screen_height - scaled_pixmap.height()) // 2

            # Paint the scaled pixmap onto the final pixmap at the calculated position
            painter = QPainter(final_pixmap)
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()

            # Set the final pixmap as the background
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(final_pixmap))
            container.setPalette(palette)
            container.setAutoFillBackground(True)

        layout = QVBoxLayout(container)

        # Add stretch before the button to push it to the center vertically

        self.title_button = QPushButton("START")
        self.title_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.title_button.setStyleSheet("""
            QPushButton {
                font-size: 70pt;
                font-weight: bold;
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 0);
                padding: 20px;
                border: none;
            }
            QPushButton:hover {
                color: #0000FF;
            }
        """)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(200)
        glow.setColor(QColor(0, 0, 255, 255))
        glow.setOffset(0, 0)
        self.title_button.setGraphicsEffect(glow)
        self.title_button.clicked.connect(self.init_main_frame)

        layout.addStretch(1)
        layout.addWidget(self.title_button, alignment=Qt.AlignCenter)
        layout.addStretch(1)

    def init_main_frame(self):

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        back_button = QPushButton("BACK")
        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 120);
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 180);
            }
        """)
        back_button.clicked.connect(self.show_title_screen)
        layout.addWidget(back_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Camera feed label
        layout.addStretch(2)
        self.video_label = QLabel("Camera Feed")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_label)
        layout.addWidget(self.video_label, stretch=35)
        layout.addStretch(3)

        # Start gesture detection
        self.detection_thread = threading.Thread(target=self.hand_follow_control, daemon=True)
        self.detection_thread.start()

        # Optional: background image
        background_pixmap = QPixmap(self.background_image)
        if not background_pixmap.isNull():
            scaled_pixmap = background_pixmap.scaled(self.screen_width, self.screen_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            final_pixmap = QPixmap(self.screen_width, self.screen_height)
            final_pixmap.fill(Qt.transparent)
            painter = QPainter(final_pixmap)
            painter.drawPixmap((self.screen_width - scaled_pixmap.width()) // 2,
                            (self.screen_height - scaled_pixmap.height()) // 2,
                            scaled_pixmap)
            painter.end()
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(final_pixmap))
            container.setPalette(palette)
            container.setAutoFillBackground(True)

        if not background_pixmap.isNull():
            # Calculate the size of the pixmap while maintaining the aspect ratio
            scaled_pixmap = background_pixmap.scaled(self.screen_width, self.screen_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create a QPixmap for the background
            final_pixmap = QPixmap(self.screen_width, self.screen_height)
            final_pixmap.fill(Qt.transparent)  # Fill it with transparency

            # Calculate the position to center the background image
            x_offset = (self.screen_width - scaled_pixmap.width()) // 2
            y_offset = (self.screen_height - scaled_pixmap.height()) // 2

            # Paint the scaled pixmap onto the final pixmap at the calculated position
            painter = QPainter(final_pixmap)
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()

            # Set the final pixmap as the background
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(final_pixmap))
            container.setPalette(palette)
            container.setAutoFillBackground(True)

    # ============================
    # Main Hand-Controlled Loop
    # ============================
    def hand_follow_control(self):
        robot = self.robot
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        cap = cv2.VideoCapture(0)

        prev_x, prev_y, prev_z = 300, 75, 120
        alpha = 0.5

        robot_busy_event = threading.Event()

        sequence = ["pick1", "place2", "pick2", "place1"]

        # Track gripper state to prevent spamming commands
        last_gripper_state = None

        def run_robot_task(task_func):
            task_func()
            robot_busy_event.clear()

        size_range = [0.15, 0.4]
        x_range = [0.1, 0.9]
        y_range = [0.1, 0.9]

        with mp_hands.Hands(min_detection_confidence=0.8,
                            min_tracking_confidence=0.5,
                            max_num_hands=1) as hands:

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(image_rgb)
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                if result.multi_hand_landmarks:
                    handLms = result.multi_hand_landmarks[0]
                    mp_draw.draw_landmarks(image_bgr, handLms, mp_hands.HAND_CONNECTIONS)

                    palm_indices = [0, 1, 5, 9, 13, 17]
                    palm_x = np.mean([handLms.landmark[i].x for i in palm_indices])
                    palm_y = np.mean([handLms.landmark[i].y for i in palm_indices])

                    palm_xs = [handLms.landmark[i].x for i in palm_indices]
                    palm_ys = [handLms.landmark[i].y for i in palm_indices]
                    bbox_width = max(palm_xs) - min(palm_xs)
                    bbox_height = max(palm_ys) - min(palm_ys)
                    hand_size = max(bbox_width, bbox_height)

                    # Map hand coordinates to robot coordinates
                    robot_x = map_coord(palm_y, y_range, [robot_limits["axes"]["x"]["min"], robot_limits["axes"]["x"]["max"]])  # up/down → X
                    robot_y = map_coord(palm_x, x_range, [robot_limits["axes"]["y"]["min"], robot_limits["axes"]["y"]["max"]])  # left/right → Y

                    # Depth (Z) is inverted: close → high Z, far → low Z
                    robot_z = map_coord(hand_size, size_range, [robot_limits["axes"]["z"]["max"], robot_limits["axes"]["z"]["min"]])  # depth → Z inverted

                    # Clip values to limits
                    robot_x = np.clip(robot_x, robot_limits["axes"]["x"]["min"], robot_limits["axes"]["x"]["max"])
                    robot_y = np.clip(robot_y, robot_limits["axes"]["y"]["min"], robot_limits["axes"]["y"]["max"])
                    robot_z = np.clip(robot_z, robot_limits["axes"]["z"]["min"], robot_limits["axes"]["z"]["max"])

                    prev_x = smooth_position(prev_x, robot_x, alpha)
                    prev_y = smooth_position(prev_y, robot_y, alpha)
                    prev_z = smooth_position(prev_z, robot_z, alpha)

                    # Detect hand state
                    palm_open = is_hand_open(handLms)
                    fist = is_hand_closed(handLms)

                    current_action = sequence[self.current_step]
                    pick_mode = current_action in ["pick1", "pick2"]

                    # ---------------------------
                    # Gripper control (only in pick mode)
                    # ---------------------------
                    if pick_mode:
                        if palm_open and last_gripper_state != "open":
                            robot.open_gripper()
                            last_gripper_state = "open"
                        elif fist and last_gripper_state != "close":
                            robot.close_gripper()
                            last_gripper_state = "close"

                    # ---------------------------
                    # Movement control
                    # ---------------------------
                    move_condition = False
                    if pick_mode:
                        # Move on both palm open or fist
                        if palm_open or fist:
                            move_condition = True
                    else:
                        # Move only when palm open
                        if palm_open:
                            move_condition = True

                    if move_condition and not robot_busy_event.is_set() and not robot.is_busy.is_set():
                        robot.move_to(prev_x, prev_y, prev_z)

                    # ---------------------------
                    # Task sequence execution
                    # ---------------------------
                    if not robot_busy_event.is_set() and palm_open:
                        if current_action == "pick1":
                            if prev_y > trigger_config["pick1"]["y_min"] and trigger_config["pick1"]["x_min"] <= prev_x <= trigger_config["pick1"]["x_max"]:
                                robot_busy_event.set()
                                threading.Thread(target=run_robot_task, args=(robot.move_pick1,)).start()
                                self.current_step = (self.current_step + 1) % len(sequence)

                        elif current_action == "place2":
                            if prev_y < trigger_config["place2"]["y_max"] and trigger_config["place2"]["x_min"] <= prev_x <= trigger_config["place2"]["x_max"]:
                                robot_busy_event.set()
                                threading.Thread(target=run_robot_task, args=(robot.move_place2,)).start()
                                self.current_step = (self.current_step + 1) % len(sequence)

                        elif current_action == "pick2":
                            if prev_y < trigger_config["pick2"]["y_max"] and trigger_config["pick2"]["x_min"] <= prev_x <= trigger_config["pick2"]["x_max"]:
                                robot_busy_event.set()
                                threading.Thread(target=run_robot_task, args=(robot.move_pick2,)).start()
                                self.current_step = (self.current_step + 1) % len(sequence)

                        elif current_action == "place1":
                            if prev_y > trigger_config["place1"]["y_min"] and trigger_config["place1"]["x_min"] <= prev_x <= trigger_config["place1"]["x_max"]:
                                robot_busy_event.set()
                                threading.Thread(target=run_robot_task, args=(robot.move_place1,)).start()
                                self.current_step = (self.current_step + 1) % len(sequence)

                    # Debug UI text
                    if robot.is_busy.is_set():
                        cv2.putText(image_bgr, "Resetting...", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                    cv2.putText(image_bgr, f"Step: {current_action}", (10, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(image_bgr, f"Hand size: {hand_size:.3f}", (10, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                rgb_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                    self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))

            cap.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    # Load robot IP from JSON config
    with open("robot_ip.json", "r") as f:
        config = json.load(f)
    robot_ip = config.get("robot_ip") 
    #robot_ip = config.get("robot_ip", "192.168.1.151")  # default if missing


    print(f"[System] xArm SDK Version: {version}")
    print(f"[System] Connecting to robot at {robot_ip}")

    arm = XArmAPI(robot_ip, baud_checkset=False)
    robot = RobotMain(arm)

    app = QApplication(sys.argv)
    window = RobotW(robot)
    window.show()
    sys.exit(app.exec_())
