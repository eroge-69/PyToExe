# Decompiled with PyLingual (https://pylingual.io) - AND THEN FIXED
# Internal filename: OblivionX.py
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import sys
import math
import base64
import time
import glob
import ctypes
import os
import cv2
import numpy as np
import mss
import requests
import PyQt6
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QSlider, QComboBox, QPushButton, QGroupBox, QFrame, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QIcon
import pyautogui

# --- ライブラリのインポートとエラーハンドリング ---
# 必要なライブラリが見つからない場合でもプログラムがクラッシュしないように設定
try:
    from ultralytics import YOLO
    YOLO_OK = True
except ImportError as e:
    print(f"[YOLO Import ERROR] {e}. YOLO features will be disabled.")
    YOLO_OK = False
    model = None

try:
    import pyxinput
    PYXINPUT_AVAILABLE = True
except ImportError:
    print("[PyXInput Import ERROR] Controller features might not work.")
    PYXINPUT_AVAILABLE = False

try:
    from inputs import get_gamepad
    INPUTS_AVAILABLE = True
except ImportError:
    INPUTS_AVAILABLE = False

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # --- 修正: try-exceptブロックの構造を修正 ---
    try:
        # PyInstallerは一時フォルダを作成し、そのパスを_MEIPASSに格納する
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

# --- Windows APIを介したマウス操作 ---
def move_mouse(dx, dy):
    """相対座標でマウスを移動させる"""
    ctypes.windll.user32.mouse_event(1, int(dx), int(dy), 0, 0)

def move_mouse_to(x, y):
    """絶対座標にマウスカーソルを移動させる"""
    ctypes.windll.user32.SetCursorPos(int(x), int(y))

def validate_key(input_key):
    """
    ライセンスキーの検証をバイパスする。
    --- 修正: 常にTrueを返すことで認証を不要にする ---
    """
    return True

class LearningBrain:
    def __init__(self):
        self.history = []
        self.learn_rate = 0.3

    def predict(self, cx, cy):
        self.history.append((cx, cy, time.time()))
        # --- 修正: if文の構文エラーを修正 ---
        if len(self.history) > 10:
            self.history.pop(0)
            
        if len(self.history) < 3:
            return (cx, cy)
        
        # 予測ロジックが不完全だが、クラッシュしないように元の座標を返す
        return (cx, cy)

    def adapt_strength(self, error, current_strength):
        return min(100, current_strength + 2) if error > 100 else max(10, current_strength - 1)

class MimicBrain:
    def __init__(self):
        self.mimic_history = []

    def record_aim_vector(self, dx, dy):
        self.mimic_history.append((dx, dy))
        if len(self.mimic_history) > 30:
            self.mimic_history.pop(0)

    def get_mimic_aim(self):
        if not self.mimic_history:
            return (0, 0)
        
        # --- 修正: 構文エラーを修正し、平均移動ベクトルを計算するロジックを実装 ---
        count = len(self.mimic_history)
        avg_dx = sum(v[0] for v in self.mimic_history) / count
        avg_dy = sum(v[1] for v in self.mimic_history) / count
        return (avg_dx, avg_dy)

class FOVOverlay(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, pyautogui.size().width, pyautogui.size().height)
        self.bounding_box = None
        self.show()

    def update_box(self, box_coords):
        self.bounding_box = box_coords
        self.update() # ウィジェットを再描画

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # FOV（視野）の描画
        pen = QPen(QColor(170, 0, 0, 180), 2)
        qp.setPen(pen)
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = self.parent.fov_slider.value()
        # FOVは横長の長方形として描画される
        qp.drawRect(center.x() - radius, center.y() - radius // 2, radius * 2, radius)
        
        # 検出したターゲットへのスナップラインの描画
        if self.bounding_box:
            x1, y1, x2, y2 = self.bounding_box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            center_x = self.width() // 2
            center_y = self.height() // 2
            snap_pen = QPen(QColor(255, 0, 0, 200), 2)
            qp.setPen(snap_pen)
            qp.drawLine(center_x, center_y, cx, cy)
        qp.end()

class OblivionXGUI(QWidget):
    def __init__(self):
        super().__init__()
        # --- YOLOモデルの読み込み ---
        global model
        global YOLO_OK
        if YOLO_OK:
            try:
                weights_path = resource_path('weights.pt')
                if os.path.exists(weights_path):
                    model = YOLO(weights_path)
                else:
                    print(f"YOLO weights not found at {weights_path}. YOLO will be disabled.")
                    YOLO_OK = False
            except Exception as e:
                print(f"[YOLO init ERROR] {e}")
                YOLO_OK = False

        self.setWindowTitle('Oblivion X v2 - Smart Snap Assist')
        self.setGeometry(100, 100, 520, 600)
        icon_path = resource_path('assets/icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setup_styles()
        self.setup_ui()
        self.init_variables()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a; color: #f1f5f9;
                font-family: 'Segoe UI', Roboto, Arial, sans-serif; font-size: 12px;
            }
            QGroupBox {
                font-weight: 600; font-size: 13px; border: 2px solid #334155;
                border-radius: 8px; margin-top: 12px; padding-top: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(30, 41, 59, 0.6), stop:1 rgba(15, 23, 42, 0.8));
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 3px 10px; background-color: #dc2626; color: white;
                border-radius: 4px; font-weight: 700; font-size: 11px; margin-left: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
                color: white; border: 1px solid #991b1b; border-radius: 6px;
                padding: 8px 12px; font-weight: 600; min-height: 16px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626); }
            QPushButton#toggleButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #059669, stop:1 #047857);
                font-size: 13px; font-weight: 700; min-height: 25px; margin-top: 10px;
            }
            QPushButton#toggleButton:checked { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c); }
            QComboBox {
                background: #1e293b; border: 1px solid #475569; border-radius: 6px;
                padding: 6px 8px; color: #f1f5f9; min-height: 16px;
            }
            QComboBox:hover { border-color: #64748b; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow { image: none; border-style: solid; 
                border-width: 4px 4px 0px 4px; border-color: #94a3b8 transparent transparent transparent; }
            QComboBox QAbstractItemView {
                background: #1e293b; border: 1px solid #475569; border-radius: 6px;
                selection-background-color: #dc2626;
            }
            QSlider::groove:horizontal { background: #334155; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
                border: 2px solid #991b1b; width: 18px; height: 18px; margin: -6px 0; border-radius: 9px;
            }
            QSlider::handle:horizontal:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626); }
            QSlider::sub-page:horizontal { background: #dc2626; border-radius: 3px; }
            QLabel { color: #cbd5e1; font-weight: 500; margin: 2px 0; }
            QLabel#statusLabel {
                color: #22c55e; font-weight: 600; padding: 6px 12px;
                background: rgba(34, 197, 94, 0.1); border: 1px solid #16a34a;
                border-radius: 6px; text-align: center;
            }
            QLabel#titleImage { background: transparent; padding: 10px; margin: 5px 0; border-radius: 8px; }
        """)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        title_image = QLabel()
        title_image.setObjectName('titleImage')
        title_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path('assets/logo.png')
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            window_width = self.width() - 32
            scaled_width = min(window_width, 500)
            # --- 修正: 画像のアスペクト比を正しく計算 ---
            if pixmap.width() > 0:
                scaled_height = int(pixmap.height() * (scaled_width / pixmap.width()))
                scaled_pixmap = pixmap.scaled(
                    scaled_width, scaled_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                title_image.setPixmap(scaled_pixmap)
                title_image.setMinimumHeight(scaled_height + 20)
        layout.addWidget(title_image)
        self.status_label = QLabel('Status: Inactive')
        self.status_label.setObjectName('statusLabel')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        main_group = QGroupBox('Primary Controls')
        main_layout = QGridLayout()
        main_layout.setSpacing(8)
        main_layout.addWidget(QLabel('FOV Radius'), 0, 0)
        self.fov_slider = QSlider(Qt.Orientation.Horizontal)
        self.fov_slider.setRange(50, 500)
        self.fov_slider.setValue(150)
        self.fov_slider.valueChanged.connect(self.repaint_fov)
        main_layout.addWidget(self.fov_slider, 0, 1)
        main_layout.addWidget(QLabel('Assist Strength'), 1, 0)
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(10, 100)
        self.strength_slider.setValue(60)
        main_layout.addWidget(self.strength_slider, 1, 1)
        main_layout.addWidget(QLabel('Target Bone'), 2, 0)
        self.bone_select = QComboBox()
        self.bone_select.addItems(['HEAD', 'CHEST', 'CENTER MASS'])
        main_layout.addWidget(self.bone_select, 2, 1)
        main_layout.addWidget(QLabel('Input Mode'), 3, 0)
        self.input_mode = QComboBox()
        self.input_mode.addItems(['Mouse & Keyboard', 'Controller', 'Mirror Controller'])
        main_layout.addWidget(self.input_mode, 3, 1)
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        ai_group = QGroupBox('AI Features')
        ai_layout = QGridLayout()
        ai_layout.setSpacing(8)
        ai_layout.addWidget(QLabel('Snap Assist'), 0, 0)
        self.snap_mode = QComboBox()
        self.snap_mode.addItems(['Disabled', 'Enabled'])
        ai_layout.addWidget(self.snap_mode, 0, 1)
        ai_layout.addWidget(QLabel('YOLO Detection'), 1, 0)
        self.yolo_mode = QComboBox()
        self.yolo_mode.addItems(['Disabled', 'Enabled'])
        if not YOLO_OK: self.yolo_mode.setEnabled(False)
        ai_layout.addWidget(self.yolo_mode, 1, 1)
        ai_layout.addWidget(QLabel('Movement Prediction'), 2, 0)
        self.prediction_mode = QComboBox()
        self.prediction_mode.addItems(['Disabled', 'Enabled'])
        ai_layout.addWidget(self.prediction_mode, 2, 1)
        ai_layout.addWidget(QLabel('Player Mimic'), 3, 0)
        self.mimic_mode = QComboBox()
        self.mimic_mode.addItems(['Disabled', 'Enabled'])
        ai_layout.addWidget(self.mimic_mode, 3, 1)
        ai_layout.addWidget(QLabel('Tracking Mode'), 4, 0)
        self.mode_select = QComboBox()
        self.mode_select.addItems(['Template Lock-On', 'Constant Tracking'])
        ai_layout.addWidget(self.mode_select, 4, 1)
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        self.toggle_button = QPushButton('START ASSIST')
        self.toggle_button.setObjectName('toggleButton')
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_aim)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)

    def init_variables(self):
        self.aim_active = False
        self.locked = False
        self.controller_moved_this_tick = False
        self.vcontroller = None
        if PYXINPUT_AVAILABLE:
            try:
                self.vcontroller = pyxinput.vController()
            except Exception as e:
                print(f"Failed to initialize virtual controller: {e}")
                self.vcontroller = None

        self.templates = []
        for path in glob.glob(resource_path('templates/*.png')) + glob.glob(resource_path('templates/*.jpeg')):
            template = cv2.imread(path, 0)
            if template is not None:
                self.templates.append(template)
        if not self.templates:
            print("No templates found in 'templates' folder.")

        self.fov_overlay = FOVOverlay(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(10)
        
        self.detector = DetectionThread(self)
        self.detector.result_signal.connect(self.process_detection_result)
        self.detector.start()
        
        self.brain = LearningBrain()
        self.mimic_brain = MimicBrain()

    def inject_right_stick(self, x, y):
        self.controller_moved_this_tick = True
        if self.vcontroller:
            try:
                strength = self.strength_slider.value() / 100.0
                # pyxinputは-1.0から1.0のfloat値を期待する
                # xとyを-32767から32767の範囲と仮定して正規化し、strengthを適用
                # 最終的な値は-1.0と1.0の間にクランプされるべき
                norm_x = max(-1.0, min(1.0, (x / 32767.0) * strength))
                # ゲームではY軸が反転していることが多いため、-yを使用
                norm_y = max(-1.0, min(1.0, (-y / 32767.0) * strength))
                self.vcontroller.set_value('AxisRx', norm_x)
                self.vcontroller.set_value('AxisRy', norm_y)
            except Exception as e:
                print(f'[pyxinput inject error] {e}')

    def toggle_aim(self):
        self.aim_active = not self.aim_active
        if self.aim_active:
            self.toggle_button.setText('STOP ASSIST')
            self.toggle_button.setChecked(True)
            self.status_label.setText('Status: Active')
            self.status_label.setStyleSheet("color: #22c55e; background: rgba(34, 197, 94, 0.1); border: 1px solid #16a34a;")
        else:
            self.toggle_button.setText('START ASSIST')
            self.toggle_button.setChecked(False)
            self.status_label.setText('Status: Inactive')
            self.status_label.setStyleSheet("color: #f87171; background: rgba(248, 113, 113, 0.1); border: 1px solid #ef4444;")

    def repaint_fov(self):
        self.fov_overlay.update()

    def tick(self):
        if self.input_mode.currentText() in ['Controller', 'Mirror Controller'] and self.vcontroller and not self.controller_moved_this_tick:
            try:
                self.vcontroller.set_value('AxisRx', 0)
                self.vcontroller.set_value('AxisRy', 0)
            except Exception as e:
                print(f'[tick reset error] {e}')
        self.controller_moved_this_tick = False

    def process_detection_result(self, result):
        """
        検出スレッドからの結果を処理し、エイム操作とオーバーレイ更新を行う。
        --- 修正: 欠落していたエイムロジックを実装 ---
        """
        location, size, box_coords = result
        self.fov_overlay.update_box(box_coords)

        is_target_found = location != (0, 0) and size != (0, 0)
        self.locked = is_target_found

        if not self.aim_active or not is_target_found or self.snap_mode.currentText() == 'Disabled':
            return

        screen_w, screen_h = pyautogui.size()
        screen_center_x, screen_center_y = screen_w // 2, screen_h // 2

        w, h = size
        target_x = location[0] + w // 2
        target_y = location[1] + h // 2

        bone = self.bone_select.currentText()
        if bone == 'HEAD':
            target_y -= h * 0.35
        elif bone == 'CHEST':
            target_y -= h * 0.15

        dx = target_x - screen_center_x
        dy = target_y - screen_center_y
        
        strength = self.strength_slider.value() / 100.0

        input_mode = self.input_mode.currentText()
        if input_mode == 'Mouse & Keyboard':
            # この係数はゲーム内感度に応じて調整が必要
            mouse_sensitivity = 0.2
            move_x = dx * strength * mouse_sensitivity
            move_y = dy * strength * mouse_sensitivity
            move_mouse(move_x, move_y)
        elif input_mode in ['Controller', 'Mirror Controller']:
            # ピクセル移動量をコントローラーの仮想的な入力値に変換
            controller_sensitivity = 500
            joy_x = int(dx * controller_sensitivity)
            joy_y = int(dy * controller_sensitivity)
            self.inject_right_stick(joy_x, joy_y)

        if self.mimic_mode.currentText() == 'Enabled':
            self.mimic_brain.record_aim_vector(dx, dy)

class DetectionThread(QThread):
    result_signal = pyqtSignal(tuple)

    def __init__(self, gui_ref):
        super().__init__()
        self.gui = gui_ref
        self.running = True

    def run(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screen_center_x = monitor['width'] // 2
            screen_center_y = monitor['height'] // 2

            while self.running:
                if not self.gui.aim_active or (self.gui.locked and self.gui.mode_select.currentText() == 'Template Lock-On'):
                    time.sleep(0.01)
                    continue

                frame_np = np.array(sct.grab(monitor))
                frame = frame_np[:, :, :3] # BGRAからBGRへ変換
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                best_target = None
                best_target_score = 0.0
                fov_radius = self.gui.fov_slider.value()
                
                if YOLO_OK and self.gui.yolo_mode.currentText() == 'Enabled':
                    try:
                        results = model.predict(frame, imgsz=640, conf=0.4, verbose=False)[0]
                        for box in results.boxes:
                            if int(box.cls[0]) == 0 and float(box.conf[0]) > 0.6: # クラス0(人)かつ信頼度0.6以上
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                conf = float(box.conf[0])
                                cx = (x1 + x2) // 2
                                cy = (y1 + y2) // 2
                                dist = math.hypot(cx - screen_center_x, cy - screen_center_y)
                                
                                if dist <= fov_radius and conf > best_target_score:
                                    best_target_score = conf
                                    best_target = ((x1, y1), (x2 - x1, y2 - y1), (x1, y1, x2, y2))
                    except Exception as e:
                        print(f"[YOLO Predict ERROR] {e}")
                
                if self.gui.templates and (not best_target or self.gui.yolo_mode.currentText() == 'Disabled'):
                    for template in self.gui.templates:
                        w, h = template.shape[::-1]
                        res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(res)
                        
                        if max_val > 0.7 and max_val > best_target_score:
                            cx = max_loc[0] + w // 2
                            cy = max_loc[1] + h // 2
                            dist = math.hypot(cx - screen_center_x, cy - screen_center_y)
                            
                            if dist <= fov_radius:
                                best_target_score = max_val
                                best_target = (max_loc, (w, h), (max_loc[0], max_loc[1], max_loc[0] + w, max_loc[1] + h))

                if best_target:
                    location, size, box_coords = best_target
                    monitor_offset_x, monitor_offset_y = monitor['left'], monitor['top']
                    abs_location = (location[0] + monitor_offset_x, location[1] + monitor_offset_y)
                    abs_box_coords = (box_coords[0] + monitor_offset_x, box_coords[1] + monitor_offset_y,
                                      box_coords[2] + monitor_offset_x, box_coords[3] + monitor_offset_y)
                    self.result_signal.emit((abs_location, size, abs_box_coords))
                else:
                    self.result_signal.emit(((0, 0), (0, 0), None))
                
                time.sleep(0.01)

    def stop(self):
        self.running = False
        self.wait() # スレッドが完全に終了するのを待つ

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OblivionXGUI()
    window.show()
    exit_code = app.exec()
    window.detector.stop() # アプリケーション終了時にスレッドを安全に停止
    sys.exit(exit_code)