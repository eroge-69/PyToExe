import sys
import time
import random
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QTextEdit, QHBoxLayout,
                             QCheckBox, QFrame, QShortcut)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QKeySequence

class AutoTyperThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, messages, count, delay, line_cooldown, random_variation, typing_speed):
        super().__init__()
        self.messages = messages
        self.count = count
        self.delay = delay
        self.line_cooldown = line_cooldown
        self.random_variation = random_variation
        self.typing_speed = typing_speed
        self._is_running = True

    def run(self):
        self.update_signal.emit(f"Starting in {self.delay} seconds...")
        time.sleep(self.delay)
        
        for i in range(self.count):
            if not self._is_running:
                break
                
            for message in self.messages:
                if not self._is_running:
                    break
                    
                self.update_signal.emit(f"Sending message {i+1}/{self.count}: {message[:20]}...")
                
                # Type with specified speed
                if self.typing_speed > 0:
                    for char in message:
                        if not self._is_running:
                            break
                        pyautogui.typewrite(char)
                        time.sleep(60.0/(self.typing_speed*100))  # Convert to seconds per character
                else:
                    # Instant typing if speed is 0
                    pyautogui.typewrite(message)
                
                pyautogui.press('enter')
                
                # Calculate cooldown with optional random variation
                cooldown = self.line_cooldown
                if self.random_variation:
                    cooldown = max(0.1, cooldown * (0.8 + 0.4 * random.random()))
                
                if i < self.count - 1 or message != self.messages[-1]:  # Don't wait after last message
                    time.sleep(cooldown)
        
        self.finished_signal.emit()

    def stop(self):
        self._is_running = False
        self.update_signal.emit("Stopped by user")

class DiscordAutoTyper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord AutoTyper Pro")
        self.setGeometry(100, 100, 650, 650)  # Increased height for new controls
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.thread = None
        self.start_shortcut = "F6"
        self.stop_shortcut = "F7"
        self.init_ui()
        self.apply_styles()
        self.setup_shortcuts()
        
    def init_ui(self):
        # Main container
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Title bar
        title_bar = QWidget()
        title_bar.setObjectName("TitleBar")
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("Discord AutoTyper Pro")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        # Message Group
        message_group = QGroupBox("Message Settings")
        message_group.setObjectName("MessageGroup")
        message_layout = QVBoxLayout()
        message_layout.setSpacing(10)
        
        self.message_input = QTextEdit()
        self.message_input.setObjectName("MessageInput")
        self.message_input.setPlaceholderText("Type your messages here (one per line)...")
        self.message_input.setMinimumHeight(120)
        message_layout.addWidget(self.message_input)
        
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Repeat Count:"))
        self.count_spin = QSpinBox()
        self.count_spin.setObjectName("CountSpin")
        self.count_spin.setRange(1, 1000)
        self.count_spin.setValue(5)
        count_layout.addWidget(self.count_spin)
        message_layout.addLayout(count_layout)
        
        message_group.setLayout(message_layout)
        
        # Typing Speed Group
        speed_group = QGroupBox("Typing Speed")
        speed_group.setObjectName("SpeedGroup")
        speed_layout = QVBoxLayout()
        
        speed_control_layout = QHBoxLayout()
        speed_control_layout.addWidget(QLabel("Typing Speed (WPM):"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setObjectName("SpeedSpin")
        self.speed_spin.setRange(0, 500)
        self.speed_spin.setValue(250)
        self.speed_spin.setToolTip("0 = instant typing, 40 = slow, 250 = average, 500 = very fast")
        speed_control_layout.addWidget(self.speed_spin)
        
        speed_example = QLabel("Example speeds: 40 (slow), 250 (normal), 400 (fast)")
        speed_example.setObjectName("SpeedExample")
        
        speed_layout.addLayout(speed_control_layout)
        speed_layout.addWidget(speed_example)
        speed_group.setLayout(speed_layout)
        
        # Timing Group
        timing_group = QGroupBox("Timing Settings")
        timing_group.setObjectName("TimingGroup")
        timing_layout = QVBoxLayout()
        timing_layout.setSpacing(10)
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Initial Delay (seconds):"))
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setObjectName("DelaySpin")
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(5)
        delay_layout.addWidget(self.delay_spin)
        timing_layout.addLayout(delay_layout)
        
        cooldown_layout = QHBoxLayout()
        cooldown_layout.addWidget(QLabel("Cooldown Between Lines (seconds):"))
        self.cooldown_spin = QDoubleSpinBox()
        self.cooldown_spin.setObjectName("CooldownSpin")
        self.cooldown_spin.setRange(0.1, 60)
        self.cooldown_spin.setValue(1)
        self.cooldown_spin.setSingleStep(0.1)
        cooldown_layout.addWidget(self.cooldown_spin)
        timing_layout.addLayout(cooldown_layout)
        
        self.random_check = QCheckBox("Add random variation to cooldown (80-120%)")
        self.random_check.setObjectName("RandomCheck")
        timing_layout.addWidget(self.random_check)
        
        timing_group.setLayout(timing_layout)
        
        # Shortcut Settings Group
        shortcut_group = QGroupBox("Keyboard Shortcuts")
        shortcut_group.setObjectName("ShortcutGroup")
        shortcut_layout = QVBoxLayout()
        
        # Start Shortcut
        start_shortcut_layout = QHBoxLayout()
        start_shortcut_layout.addWidget(QLabel("Start Shortcut:"))
        self.start_shortcut_edit = QLineEdit(self.start_shortcut)
        self.start_shortcut_edit.setObjectName("StartShortcutEdit")
        self.start_shortcut_edit.setMaximumWidth(100)
        self.start_shortcut_edit.setPlaceholderText("Press a key...")
        self.start_shortcut_edit.keyPressEvent = self.start_key_press_event
        start_shortcut_layout.addWidget(self.start_shortcut_edit)
        start_shortcut_layout.addStretch()
        shortcut_layout.addLayout(start_shortcut_layout)
        
        # Stop Shortcut
        stop_shortcut_layout = QHBoxLayout()
        stop_shortcut_layout.addWidget(QLabel("Stop Shortcut:"))
        self.stop_shortcut_edit = QLineEdit(self.stop_shortcut)
        self.stop_shortcut_edit.setObjectName("StopShortcutEdit")
        self.stop_shortcut_edit.setMaximumWidth(100)
        self.stop_shortcut_edit.setPlaceholderText("Press a key...")
        self.stop_shortcut_edit.keyPressEvent = self.stop_key_press_event
        stop_shortcut_layout.addWidget(self.stop_shortcut_edit)
        stop_shortcut_layout.addStretch()
        shortcut_layout.addLayout(stop_shortcut_layout)
        
        shortcut_group.setLayout(shortcut_layout)
        
        # Button Group
        button_group = QFrame()
        button_group.setObjectName("ButtonGroup")
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_btn = QPushButton("Start Typing")
        self.start_btn.setObjectName("StartButton")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_typing)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.clicked.connect(self.stop_typing)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        # Status Log
        self.log_output = QTextEdit()
        self.log_output.setObjectName("LogOutput")
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Status messages will appear here...")
        self.log_output.setMinimumHeight(100)
        
        # Warning Label
        warning = QLabel("⚠️ Important: Switch to Discord window after starting and keep it active!")
        warning.setObjectName("WarningLabel")
        
        # Add widgets to main layout
        main_layout.addWidget(title_bar)
        main_layout.addWidget(message_group)
        main_layout.addWidget(speed_group)
        main_layout.addWidget(timing_group)
        main_layout.addWidget(shortcut_group)
        main_layout.addWidget(button_group)
        main_layout.addWidget(self.log_output)
        main_layout.addWidget(warning)
        
    def apply_styles(self):
        self.setStyleSheet("""
            #MainWidget {
                background-color: #2e2e2e;
                border-radius: 10px;
                border: 1px solid #444;
            }
            
            #TitleBar {
                background-color: #1e1e1e;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding-left: 15px;
            }
            
            #TitleLabel {
                color: #f0f0f0;
                font-size: 16px;
                font-weight: bold;
            }
            
            #CloseButton {
                background-color: #ff5f56;
                color: #1e1e1e;
                border-radius: 15px;
                font-weight: bold;
                border: none;
            }
            
            #CloseButton:hover {
                background-color: #ff3b30;
            }
            
            QGroupBox {
                color: #a0a0a0;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            
            #MessageGroup, #SpeedGroup, #TimingGroup, #ShortcutGroup {
                background-color: #252525;
            }
            
            #MessageInput, #LogOutput {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                selection-background-color: #3a6ea5;
            }
            
            QLabel {
                color: #e0e0e0;
            }
            
            #SpeedExample {
                color: #a0a0a0;
                font-size: 11px;
            }
            
            QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-width: 60px;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                width: 20px;
                border-left: 1px solid #444;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 20px;
                border-left: 1px solid #444;
            }
            
            QCheckBox {
                color: #e0e0e0;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            #ButtonGroup {
                background-color: transparent;
            }
            
            #StartButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            
            #StartButton:hover {
                background-color: #45a049;
            }
            
            #StopButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            
            #StopButton:hover {
                background-color: #d32f2f;
            }
            
            #WarningLabel {
                color: #ff6b6b;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
        """)
        
        # Set font
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
    def setup_shortcuts(self):
        # Initialize shortcuts with default values
        self.start_shortcut_obj = QShortcut(QKeySequence(self.start_shortcut), self)
        self.start_shortcut_obj.activated.connect(self.start_typing)
        
        self.stop_shortcut_obj = QShortcut(QKeySequence(self.stop_shortcut), self)
        self.stop_shortcut_obj.activated.connect(self.stop_typing)
        
    def update_shortcuts(self):
        # Remove old shortcuts
        self.start_shortcut_obj.deleteLater()
        self.stop_shortcut_obj.deleteLater()
        
        # Create new shortcuts
        self.start_shortcut_obj = QShortcut(QKeySequence(self.start_shortcut), self)
        self.start_shortcut_obj.activated.connect(self.start_typing)
        
        self.stop_shortcut_obj = QShortcut(QKeySequence(self.stop_shortcut), self)
        self.stop_shortcut_obj.activated.connect(self.stop_typing)
        
        self.log_output.append(f"Shortcuts updated - Start: {self.start_shortcut}, Stop: {self.stop_shortcut}")
        
    def start_key_press_event(self, event):
        key = event.key()
        modifiers = event.modifiers()
        
        # Get the key sequence
        key_sequence = QKeySequence(modifiers + key).toString()
        
        # Update the shortcut
        self.start_shortcut = key_sequence
        self.start_shortcut_edit.setText(key_sequence)
        self.update_shortcuts()
        
    def stop_key_press_event(self, event):
        key = event.key()
        modifiers = event.modifiers()
        
        # Get the key sequence
        key_sequence = QKeySequence(modifiers + key).toString()
        
        # Update the shortcut
        self.stop_shortcut = key_sequence
        self.stop_shortcut_edit.setText(key_sequence)
        self.update_shortcuts()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

    def start_typing(self):
        messages = [msg.strip() for msg in self.message_input.toPlainText().split('\n') if msg.strip()]
        if not messages:
            self.log_output.append("Error: Please enter at least one message!")
            return
            
        count = self.count_spin.value()
        delay = self.delay_spin.value()
        cooldown = self.cooldown_spin.value()
        random_variation = self.random_check.isChecked()
        typing_speed = self.speed_spin.value()
        
        self.log_output.append(f"Preparing to send {len(messages)} messages, repeated {count} times...")
        self.log_output.append(f"Typing speed: {'instant' if typing_speed == 0 else f'{typing_speed} WPM'}")
        self.log_output.append(f"Cooldown between lines: {cooldown} seconds" + 
                              (" with random variation" if random_variation else ""))
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Animate button press
        self.animate_button(self.start_btn)
        
        self.thread = AutoTyperThread(messages, count, delay, cooldown, random_variation, typing_speed)
        self.thread.update_signal.connect(self.update_log)
        self.thread.finished_signal.connect(self.typing_finished)
        self.thread.start()
        
    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        
        original_rect = button.geometry()
        pressed_rect = original_rect.adjusted(0, 2, 0, -2)
        
        animation.setKeyValueAt(0, original_rect)
        animation.setKeyValueAt(0.5, pressed_rect)
        animation.setKeyValueAt(1, original_rect)
        
        animation.start()
        
    def stop_typing(self):
        if self.thread and self.thread.isRunning():
            self.animate_button(self.stop_btn)
            self.thread.stop()
            self.thread.wait()
            
    def typing_finished(self):
        self.log_output.append("Finished sending all messages!")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def update_log(self, message):
        self.log_output.append(message)
        # Auto-scroll to bottom
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.End)
        self.log_output.setTextCursor(cursor)
        
    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiscordAutoTyper()
    window.show()
    sys.exit(app.exec_())