import sys
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import sqlite3
import os
import math

# --- Face Recognition Import ---
try:
    import face_recognition
except ImportError:
    print("Error: face_recognition library not found.")
    print("Please install it by running: pip install face_recognition")
    sys.exit(1)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStyle, QComboBox, QDialog, QGridLayout, QSizePolicy,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QLineEdit, QProgressBar,
    QSizeGrip
)
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor, QBrush, QPixmap, QPainterPath, QImage
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty, QThread, pyqtSignal, QTimer

# --- Database Management ---
class DatabaseManager:
    """Handles all database operations for the application."""
    def __init__(self, db_name="user_data.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS face_encodings (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    encoding BLOB NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            """)

    def get_all_users(self):
        with self.conn:
            return self.conn.execute("SELECT id, name FROM users;").fetchall()

    def add_user(self, name, images):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (?);", (name,))
            user_id = cursor.lastrowid
            for img in images:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_img)
                if encodings:
                    encoding_blob = encodings[0].tobytes()
                    cursor.execute("INSERT INTO face_encodings (user_id, encoding) VALUES (?, ?);", (user_id, encoding_blob))
            return user_id

    def update_user(self, user_id, new_name):
        with self.conn:
            self.conn.execute("UPDATE users SET name = ? WHERE id = ?;", (new_name, user_id))

    def delete_user(self, user_id):
        with self.conn:
            self.conn.execute("DELETE FROM face_encodings WHERE user_id = ?;", (user_id,))
            self.conn.execute("DELETE FROM users WHERE id = ?;", (user_id,))

    def get_known_face_encodings(self):
        known_encodings = []
        known_names = []
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT u.name, f.encoding
                FROM users u
                JOIN face_encodings f ON u.id = f.user_id;
            """)
            for name, encoding_blob in cursor.fetchall():
                encoding = np.frombuffer(encoding_blob, dtype=np.float64)
                known_encodings.append(encoding)
                known_names.append(name)
        return known_encodings, known_names

# --- Model Pre-loading Thread ---
class ModelLoader(QThread):
    models_loaded = pyqtSignal(list, list)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
    def run(self):
        known_face_encodings, known_face_names = self.db_manager.get_known_face_encodings()
        self.models_loaded.emit(known_face_encodings, known_face_names)

# --- Backend Gesture Recognition Logic ---
class GestureController(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    gesture_detected = pyqtSignal(str)
    user_recognized = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.running = False
        self.camera_index = 0
        self.known_face_encodings = []
        self.known_face_names = []
    def load_models(self, face_encodings, face_names):
        self.known_face_encodings = face_encodings
        self.known_face_names = face_names
    def run(self):
        self.running = True
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=2, model_complexity=1, min_detection_confidence=0.8, min_tracking_confidence=0.7)
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        if not self.known_face_encodings:
            print("Warning: No registered users found. Gesture control will be disabled.")
        cap = cv2.VideoCapture(self.camera_index)
        gesture_counter = 0; COOLDOWN_FRAMES = 15; ZOOM_IN_THRESHOLD = 0.12
        ZOOM_OUT_THRESHOLD = 0.05; is_authorized_user = False; frame_counter = 0
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_counter += 1
            frame = cv2.flip(frame, 1) # Frame is flipped BEFORE processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if frame_counter % 60 == 0:
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                is_authorized_user = False; recognized_name = "Unknown"
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
                    if True in matches:
                        first_match_index = matches.index(True)
                        recognized_name = self.known_face_names[first_match_index]
                        is_authorized_user = True; break
                self.user_recognized.emit(recognized_name)
            if gesture_counter > 0: gesture_counter -= 1
            if is_authorized_user:
                result = hands.process(rgb_frame)
                if result.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
                        handedness_label = result.multi_handedness[idx].classification[0].label
                        landmarks = hand_landmarks.landmark
                        
                        # <<< FIX: The logic blocks have been swapped. >>>
                        if gesture_counter == 0:
                            # --- RIGHT HAND (Detected as 'Right' after flip) ---
                            if handedness_label == 'Right':
                                index_tip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                                index_pip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
                                is_pointing = index_tip_y < index_pip_y
                                
                                if is_pointing:
                                    index_tip_x = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                                    wrist_x = landmarks[mp_hands.HandLandmark.WRIST].x
                                    if index_tip_x < wrist_x:
                                        self.gesture_detected.emit("Previous")
                                        pyautogui.press('left')
                                        gesture_counter = COOLDOWN_FRAMES
                                    elif index_tip_x > wrist_x:
                                        self.gesture_detected.emit("Next")
                                        pyautogui.press('right')
                                        gesture_counter = COOLDOWN_FRAMES
                            
                            # --- LEFT HAND (Detected as 'Left' after flip) ---
                            elif handedness_label == 'Left':
                                thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                                pinch_distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
                                
                                if pinch_distance > ZOOM_IN_THRESHOLD:
                                    self.gesture_detected.emit("Zoom In")
                                    pyautogui.hotkey('ctrl', '+')
                                    gesture_counter = COOLDOWN_FRAMES
                                elif pinch_distance < ZOOM_OUT_THRESHOLD:
                                    self.gesture_detected.emit("Zoom Out")
                                    pyautogui.hotkey('ctrl', '-')
                                    gesture_counter = COOLDOWN_FRAMES
            self.frame_ready.emit(frame)
        cap.release()
    def stop(self): self.running = False; self.wait()

# --- UI Classes ---
class RegisterUserDialog(QDialog):
    def __init__(self, db_manager, camera_index, parent=None):
        super().__init__(parent); self.db_manager = db_manager; self.setWindowTitle("Register New User")
        self.setMinimumSize(500, 450); self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self); self.video_feed = VideoFrame(); layout.addWidget(self.video_feed)
        self.instructions_label = QLabel("Slowly turn your head from left to right during capture.")
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.instructions_label)
        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 30); self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True); layout.addWidget(self.progress_bar)
        input_layout = QHBoxLayout(); self.name_input = QLineEdit(); self.name_input.setPlaceholderText("Enter User's Name...")
        self.capture_button = QPushButton("Start Capture Sequence"); self.capture_button.clicked.connect(self.start_capture_sequence)
        input_layout.addWidget(self.name_input); input_layout.addWidget(self.capture_button); layout.addLayout(input_layout)
        self.camera_thread = QThread(); self.worker = CameraWorker(camera_index)
        self.worker.moveToThread(self.camera_thread); self.camera_thread.started.connect(self.worker.run)
        self.worker.frame_ready.connect(self.video_feed.set_image); self.camera_thread.start()
        self.capture_timer = QTimer(self); self.capture_timer.timeout.connect(self.capture_frame)
        self.capture_count = 0; self.captured_frames = []
    def start_capture_sequence(self):
        self.user_name = self.name_input.text()
        if not self.user_name: QMessageBox.warning(self, "Input Error", "Please enter a name."); return
        self.capture_button.setEnabled(False); self.name_input.setEnabled(False)
        self.capture_count = 0; self.captured_frames = []; self.progress_bar.setValue(0)
        self.capture_timer.start(150)
    def capture_frame(self):
        if self.worker.latest_frame is not None:
            self.captured_frames.append(self.worker.latest_frame); self.capture_count += 1
            self.progress_bar.setValue(self.capture_count)
            if self.capture_count >= 30: self.capture_timer.stop(); self.finish_registration()
    def cleanup(self):
        if self.camera_thread.isRunning():
            self.worker.stop()
            self.camera_thread.quit()
            self.camera_thread.wait()
    def finish_registration(self):
        self.db_manager.add_user(self.user_name, self.captured_frames)
        QMessageBox.information(self, "Success", f"User '{self.user_name}' registered.")
        self.cleanup()
        self.accept()
    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

class CameraWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    def __init__(self, camera_index=0):
        super().__init__(); self.running = True; self.latest_frame = None; self.camera_index = camera_index
    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret: self.latest_frame = cv2.flip(frame, 1); self.frame_ready.emit(self.latest_frame)
        cap.release()
    def stop(self): self.running = False

class ManageUsersDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent); self.db_manager = db_manager; self.setWindowTitle("Manage Users")
        self.setMinimumSize(400, 300); self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self); self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.update_button_states); layout.addWidget(self.user_list)
        button_layout = QHBoxLayout(); self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_user); self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_user); button_layout.addStretch()
        button_layout.addWidget(self.edit_button); button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout); self.load_users(); self.update_button_states()
    def load_users(self):
        self.user_list.clear()
        for user_id, name in self.db_manager.get_all_users():
            item = QListWidgetItem(name); item.setData(Qt.ItemDataRole.UserRole, user_id); self.user_list.addItem(item)
    def update_button_states(self):
        is_selected = bool(self.user_list.selectedItems())
        self.edit_button.setEnabled(is_selected); self.delete_button.setEnabled(is_selected)
    def edit_user(self):
        item = self.user_list.currentItem();
        if not item: return
        user_id, current_name = item.data(Qt.ItemDataRole.UserRole), item.text()
        new_name, ok = QInputDialog.getText(self, "Edit User", "New name:", text=current_name)
        if ok and new_name: self.db_manager.update_user(user_id, new_name); self.load_users()
    def delete_user(self):
        item = self.user_list.currentItem()
        if not item: return
        user_id, user_name = item.data(Qt.ItemDataRole.UserRole), item.text()
        reply = QMessageBox.question(self, "Delete User", f"Delete '{user_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes: self.db_manager.delete_user(user_id); self.load_users()

class GestureGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setModal(True); self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20); background_frame = QFrame(self)
        background_frame.setObjectName("GestureGuideBackground"); main_layout.addWidget(background_frame)
        content_layout = QVBoxLayout(background_frame); content_layout.setSpacing(15)
        title_label = QLabel("GESTURE GUIDE"); title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title_label.setFont(title_font); title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #8e44ad; background: transparent;"); content_layout.addWidget(title_label)
        guide_layout = QHBoxLayout(); guide_layout.setSpacing(40)
        right_hand_layout = QVBoxLayout()
        right_title = QLabel("Right Hand (Navigation)"); font = right_title.font(); font.setBold(True); font.setPointSize(14)
        right_title.setFont(font); right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_hand_layout.addWidget(right_title)
        right_hand_layout.addWidget(self.create_gesture_widget("next.png", "Point Right"))
        right_hand_layout.addWidget(self.create_gesture_widget("previous.png", "Point Left"))
        left_hand_layout = QVBoxLayout()
        left_title = QLabel("Left Hand (Zoom Controls)"); font = left_title.font(); font.setBold(True); font.setPointSize(14)
        left_title.setFont(font); left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_hand_layout.addWidget(left_title)
        left_hand_layout.addWidget(self.create_gesture_widget("zoom_in.png", "Pinch Apart"))
        left_hand_layout.addWidget(self.create_gesture_widget("zoom_out.png", "Pinch Together"))
        guide_layout.addLayout(right_hand_layout); guide_layout.addLayout(left_hand_layout)
        content_layout.addLayout(guide_layout)
    def create_gesture_widget(self, image_path, text):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter); image_label = QLabel()
        target_size = QSize(150, 150)
        try: source_pixmap = QPixmap(image_path)
        except: source_pixmap = QPixmap(target_size); source_pixmap.fill(QColor("#3498db"))
        scaled_pixmap = source_pixmap.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        rounded_pixmap = QPixmap(target_size); rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(0, 0, target_size.width(), target_size.height(), 15, 15)
        painter.setClipPath(path)
        x = (target_size.width() - scaled_pixmap.width()) // 2; y = (target_size.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap); painter.end()
        image_label.setPixmap(rounded_pixmap); image_label.setFixedSize(target_size)
        text_label = QLabel(text); font = text_label.font(); font.setPointSize(12); font.setBold(True)
        text_label.setFont(font); text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("background: transparent; color: #ecf0f1;")
        layout.addWidget(image_label); layout.addWidget(text_label)
        return widget

class VideoFrame(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent); self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter); self.setStyleSheet("background-color: black;")
    def set_image(self, image: np.ndarray):
        h, w, ch = image.shape; bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        source_pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = source_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        final_pixmap = QPixmap(self.size()); final_pixmap.fill(Qt.GlobalColor.black)
        painter = QPainter(final_pixmap)
        x = (self.width() - scaled_pixmap.width()) // 2; y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap); painter.end()
        self.setPixmap(final_pixmap)

class MiniFeedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.container = QFrame(self); self.container.setObjectName("MiniFeedContainer")
        self.main_layout.addWidget(self.container)
        container_layout = QVBoxLayout(self.container); container_layout.setContentsMargins(5, 5, 5, 5)
        self.video_frame = VideoFrame(); container_layout.addWidget(self.video_frame)
        self.grip_size = 16; self.grips = [QSizeGrip(self) for i in range(4)]; self.drag_position = None
    def resizeEvent(self, event):
        super().resizeEvent(event); rect = self.rect()
        self.grips[0].setGeometry(rect.left(), rect.top(), self.grip_size, self.grip_size)
        self.grips[1].setGeometry(rect.right() - self.grip_size, rect.top(), self.grip_size, self.grip_size)
        self.grips[2].setGeometry(rect.left(), rect.bottom() - self.grip_size, self.grip_size, self.grip_size)
        self.grips[3].setGeometry(rect.right() - self.grip_size, rect.bottom() - self.grip_size, self.grip_size, self.grip_size)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); event.accept()
    def mouseMoveEvent(self, event):
        if self.drag_position is not None: self.move(event.globalPosition().toPoint() - self.drag_position); event.accept()
    def mouseReleaseEvent(self, event): self.drag_position = None; event.accept()

# --- Main Application Window ---
class PresentationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Gesture Based Presentation System"); self.setGeometry(100, 100, 1200, 750)
        self.db_manager = DatabaseManager()
        self.gesture_thread = None 
        self.known_face_encodings = []; self.known_face_names = []
        self.mini_feed = None
        self.initUI(); self.connect_signals(); self.preload_models()
    def preload_models(self):
        self.start_button.setEnabled(False); self.start_button.setText("Loading Models...")
        self.model_loader_thread = ModelLoader(self.db_manager)
        self.model_loader_thread.models_loaded.connect(self.on_models_loaded)
        self.model_loader_thread.start()
    def on_models_loaded(self, face_encodings, face_names):
        self.known_face_encodings = face_encodings; self.known_face_names = face_names
        self.start_button.setText("Start System"); self.start_button.setEnabled(True)
        print("Face data has been pre-loaded.")
    def initUI(self):
        self.setStyleSheet("""
            QMainWindow, QFrame#SidebarFrame, QDialog { background-color: #2c3e50; }
            QLabel { color: #ecf0f1; font-family: 'Segoe UI'; }
            QLabel#VideoPlaceholder { background-color: black; border-radius: 8px; }
            QPushButton { color: white; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; padding: 12px 20px; border: 1px solid #555; border-radius: 8px; }
            QPushButton#StartButton { background-color: #27ae60; } QPushButton#StartButton:hover { background-color: #2ecc71; }
            QPushButton#StopButton { background-color: #c0392b; } QPushButton#StopButton:hover { background-color: #e74c3c; }
            QPushButton#RegisterButton { background-color: #d35400; } QPushButton#RegisterButton:hover { background-color: #e67e22; }
            QPushButton#ManageButton { background-color: #f1c40f; } QPushButton#ManageButton:hover { background-color: #f39c12; }
            QPushButton#GuideButton { background-color: #8e44ad; } QPushButton#GuideButton:hover { background-color: #9b59b6; }
            QPushButton#QuitButton { background-color: #7f8c8d; } QPushButton#QuitButton:hover { background-color: #95a5a6; }
            QPushButton#SettingsButton { background-color: transparent; border: none; font-size: 14px; text-align: left; padding-left: 0; color: #ecf0f1; }
            QPushButton#SettingsButton:hover { color: #bdc3c7; }
            QComboBox { background-color: #3498db; color: white; padding: 8px; border-radius: 5px; font-weight: bold; }
            QComboBox:hover { background-color: #2980b9; } QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #34495e; color: white; }
            QFrame#GestureGuideBackground { background-color: rgba(44, 62, 80, 0.9); border-radius: 15px; }
            QLabel#GestureLabel, QLabel#UserLabel { color: white; background-color: rgba(0, 0, 0, 0.6); font-size: 18px; font-weight: bold; padding: 8px; border-radius: 5px; }
            QListWidget { background-color: #f1c40f; border-radius: 5px; color: #2c3e50; }
            QLineEdit { background-color: #34495e; border: 1px solid #2c3e50; border-radius: 5px; padding: 8px; color: white; }
            QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; color: white; }
            QProgressBar::chunk { background-color: #27ae60; width: 10px; margin: 0.5px; }
            QFrame#MiniFeedContainer { border: 2px solid #3498db; border-radius: 5px; }
        """)
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.create_sidebar(); self.create_main_content()
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.main_content_widget, 1)
    def create_sidebar(self):
        self.sidebar = QFrame(); self.sidebar.setObjectName("SidebarFrame")
        sidebar_layout = QVBoxLayout(self.sidebar); sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(15); sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_title = QLabel("Settings"); font = sidebar_title.font(); font.setPointSize(18); font.setBold(True)
        sidebar_title.setFont(font); sidebar_layout.addWidget(sidebar_title)
        sidebar_layout.addWidget(QLabel("Camera Source:"))
        self.camera_combo = QComboBox(); self.camera_combo.addItems(["Built-in Camera (0)", "External Camera (1)"])
        sidebar_layout.addWidget(self.camera_combo)
        self.mini_feed_button = QPushButton("Show Mini-Feed")
        self.mini_feed_button.clicked.connect(self.toggle_mini_feed)
        sidebar_layout.addWidget(self.mini_feed_button)
        self.sidebar.setFixedWidth(0)
    def create_main_content(self):
        self.main_content_widget = QWidget()
        main_content_layout = QVBoxLayout(self.main_content_widget)
        main_content_layout.setContentsMargins(25, 15, 25, 25); main_content_layout.setSpacing(20)
        top_layout = QHBoxLayout()
        self.settings_button = QPushButton(" Settings"); self.settings_button.setObjectName("SettingsButton")
        settings_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.settings_button.setIcon(settings_icon); self.settings_button.setIconSize(QSize(24, 24))
        title_label = QLabel("Hand Gesture Based Presentation System"); title_font = QFont("Segoe UI", 20)
        title_font.setBold(True); title_label.setFont(title_font)
        top_layout.addWidget(self.settings_button); top_layout.addWidget(title_label, 1, Qt.AlignmentFlag.AlignCenter)
        self.video_placeholder = VideoFrame(); self.video_placeholder.setObjectName("VideoPlaceholder")
        self.gesture_label = QLabel(self.video_placeholder); self.gesture_label.setObjectName("GestureLabel"); self.gesture_label.hide()
        self.user_label = QLabel(self.video_placeholder); self.user_label.setObjectName("UserLabel"); self.user_label.hide()
        bottom_layout = QHBoxLayout(); bottom_layout.setSpacing(15)
        self.start_button = QPushButton("Start System"); self.start_button.setObjectName("StartButton")
        self.stop_button = QPushButton("Stop System"); self.stop_button.setObjectName("StopButton"); self.stop_button.setEnabled(False)
        self.register_button = QPushButton("Register User"); self.register_button.setObjectName("RegisterButton")
        self.manage_button = QPushButton("Manage User"); self.manage_button.setObjectName("ManageButton")
        self.guide_button = QPushButton("Gesture Guide"); self.guide_button.setObjectName("GuideButton")
        self.quit_button = QPushButton("Quit"); self.quit_button.setObjectName("QuitButton")
        bottom_layout.addStretch(1); bottom_layout.addWidget(self.start_button); bottom_layout.addWidget(self.stop_button)
        bottom_layout.addWidget(self.register_button); bottom_layout.addWidget(self.manage_button)
        bottom_layout.addWidget(self.guide_button); bottom_layout.addWidget(self.quit_button); bottom_layout.addStretch(1)
        main_content_layout.addLayout(top_layout)
        main_content_layout.addWidget(self.video_placeholder, stretch=1)
        main_content_layout.addLayout(bottom_layout)
    def connect_signals(self):
        self.settings_button.clicked.connect(self.toggle_sidebar); self.quit_button.clicked.connect(self.close)
        self.guide_button.clicked.connect(self.show_gesture_guide); self.manage_button.clicked.connect(self.show_manage_users)
        self.register_button.clicked.connect(self.show_register_user); self.camera_combo.currentIndexChanged.connect(self.camera_source_changed)
        self.start_button.clicked.connect(self.start_gesture_system); self.stop_button.clicked.connect(self.stop_gesture_system)
    def start_gesture_system(self):
        self.gesture_thread = GestureController()
        self.gesture_thread.camera_index = self.camera_combo.currentIndex()
        self.gesture_thread.load_models(self.known_face_encodings, self.known_face_names)
        self.gesture_thread.frame_ready.connect(self.update_video_feeds)
        self.gesture_thread.gesture_detected.connect(self.update_gesture_display)
        self.gesture_thread.user_recognized.connect(self.update_user_display)
        self.gesture_thread.start()
        self.start_button.setEnabled(False); self.stop_button.setEnabled(True); self.camera_combo.setEnabled(False)
    def stop_gesture_system(self):
        if self.gesture_thread and self.gesture_thread.isRunning():
            self.gesture_thread.stop()
            self.start_button.setEnabled(True); self.stop_button.setEnabled(False); self.camera_combo.setEnabled(True)
            self.video_placeholder.clear(); self.video_placeholder.setText("System Stopped")
            self.gesture_label.hide(); self.user_label.hide()
    def update_video_feeds(self, frame):
        self.video_placeholder.set_image(frame)
        if self.mini_feed and self.mini_feed.isVisible(): self.mini_feed.video_frame.set_image(frame)
    def update_gesture_display(self, gesture_name):
        self.gesture_label.setText(f"Gesture: {gesture_name}"); self.gesture_label.adjustSize(); self.gesture_label.show(); self.position_gesture_label()
    def update_user_display(self, user_name):
        self.user_label.setText(f"User: {user_name}"); self.user_label.adjustSize(); self.user_label.show(); self.position_user_label()
    def position_gesture_label(self):
        margin = 15; x = margin; y = self.video_placeholder.height() - self.gesture_label.height() - margin
        self.gesture_label.move(x, y)
    def position_user_label(self):
        margin = 15; x = self.video_placeholder.width() - self.user_label.width() - margin; y = margin
        self.user_label.move(x, y)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'gesture_label'): self.position_gesture_label()
        if hasattr(self, 'user_label'): self.position_user_label()
    def toggle_sidebar(self):
        current_width = self.sidebar.width(); target_width = 250 if current_width == 0 else 0
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300); self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width); self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()
    def toggle_mini_feed(self):
        if not self.mini_feed:
            self.mini_feed = MiniFeedWindow(); self.mini_feed.resize(320, 240)
            self.mini_feed.show(); self.mini_feed_button.setText("Hide Mini-Feed")
        else:
            if self.mini_feed.isVisible(): self.mini_feed.hide(); self.mini_feed_button.setText("Show Mini-Feed")
            else: self.mini_feed.show(); self.mini_feed_button.setText("Hide Mini-Feed")
    def camera_source_changed(self, index):
        if self.gesture_thread is None or not self.gesture_thread.isRunning():
            print(f"Camera source will be set to index {index} on next start.")
        else: print("Stop the system to change the camera source.")
    def show_gesture_guide(self): GestureGuideDialog(self).exec()
    def show_manage_users(self):
        dialog = ManageUsersDialog(self.db_manager, self)
        if dialog.exec(): self.preload_models()
    def show_register_user(self):
        camera_index = self.camera_combo.currentIndex()
        dialog = RegisterUserDialog(self.db_manager, camera_index, self)
        if dialog.exec(): self.preload_models()
    def closeEvent(self, event):
        if self.mini_feed: self.mini_feed.close()
        self.stop_gesture_system(); super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PresentationApp()
    window.show()
    sys.exit(app.exec())