import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import psutil
import keyboard as kb

class SpinnerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(16)
        self.setFixedSize(60, 60)

    def rotate(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        grad = QtGui.QConicalGradient(rect.center(), self.angle)
        grad.setColorAt(0, QtGui.QColor(255,255,255,200))
        grad.setColorAt(0.2, QtGui.QColor(255,255,255,100))
        grad.setColorAt(1, QtGui.QColor(0,0,0,0))
        pen = QtGui.QPen()
        pen.setWidth(8)
        painter.setPen(pen)
        painter.setBrush(grad)
        painter.drawEllipse(rect.adjusted(8,8,-8,-8))

class GradientWidget(QtWidgets.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        gradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QtGui.QColor(20, 20, 20))
        gradient.setColorAt(1, QtGui.QColor(40, 40, 40))
        painter.fillRect(self.rect(), gradient)

def wait_for_notepad(callback):
    def check():
        while True:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == 'RustClient.exe':
                    QtCore.QTimer.singleShot(0, callback)
                    return
            time.sleep(1)
    threading.Thread(target=check, daemon=True).start()

class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 520)
        # Тень
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(32)
        effect.setOffset(0, 8)
        effect.setColor(QtGui.QColor(0,0,0,180))
        self.setGraphicsEffect(effect)
        # Градиентный фон без скруглений
        self.bg = QtWidgets.QLabel(self)
        self.bg.setGeometry(0, 0, 420, 520)
        self.bg.lower()
        self.bg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #181818, stop:1 #232323); border-radius: 0px;")
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(22)
        layout.setAlignment(QtCore.Qt.AlignVCenter)
        # Чекбоксы
        self.check_esp = QtWidgets.QCheckBox("ESP")
        self.check_players = QtWidgets.QCheckBox("players")
        self.check_mobs = QtWidgets.QCheckBox("mobs")
        self.check_npc = QtWidgets.QCheckBox("npc")
        self.check_always_day = QtWidgets.QCheckBox("always day")
        self.check_spiderman = QtWidgets.QCheckBox("spiderman (risk of ban)")
        self.check_silent_aim = QtWidgets.QCheckBox("silent aim")
        # Dropdown
        self.combo_silent_aim = QtWidgets.QComboBox()
        self.combo_silent_aim.addItems(["head", "body", "legs"])
        self.combo_silent_aim.setVisible(False)
        self.combo_silent_aim.setMinimumWidth(220)
        self.check_silent_aim.stateChanged.connect(self.toggle_silent_aim)
        # Стилизация чекбоксов и комбобокса без скруглений
        self.setStyleSheet("""
            QCheckBox {
                color: #fff;
                font-size: 18px;
                font-family: Consolas, monospace;
                padding: 6px 0 6px 0;
            }
            QCheckBox::indicator {
                width: 28px;
                height: 28px;
                border-radius: 0px;
                background: #181818;
                border: 2px solid #444;
                margin-right: 12px;
            }
            QCheckBox::indicator:checked {
                background: #fff;
                border: 2px solid #fff;
            }
            QComboBox {
                background: #181818;
                color: #fff;
                border: 2px solid #444;
                border-radius: 0px;
                font-size: 17px;
                font-family: Consolas, monospace;
                padding: 6px 16px 6px 12px;
                min-width: 220px;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 28px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 10px solid #fff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #232323;
                color: #fff;
                border-radius: 0px;
                selection-background-color: #333;
                font-size: 17px;
            }
        """)
        # Добавляем виджеты
        layout.addWidget(self.check_esp)
        layout.addWidget(self.check_players)
        layout.addWidget(self.check_mobs)
        layout.addWidget(self.check_npc)
        layout.addWidget(self.check_always_day)
        layout.addWidget(self.check_spiderman)
        layout.addWidget(self.check_silent_aim)
        layout.addWidget(self.combo_silent_aim)
        layout.addStretch(1)
        # Для перетаскивания
        self._drag_active = False
        self._drag_pos = None
    def toggle_silent_aim(self, state):
        self.combo_silent_aim.setVisible(state == QtCore.Qt.Checked)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self._drag_active = False
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

class BootLoader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 250)
        self.gradient = GradientWidget(self)
        self.gradient.setGeometry(self.rect())
        self.spinner = SpinnerWidget(self)
        self.spinner.move(170, 40)
        self.label = QtWidgets.QLabel("", self)
        self.label.setStyleSheet("color: white; font-size: 18px; font-family: Consolas;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setGeometry(50, 120, 300, 40)
        self.status = QtWidgets.QLabel("", self)
        self.status.setStyleSheet("color: #aaa; font-size: 14px; font-family: Consolas;")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setGeometry(50, 170, 300, 30)
        self.steps = [
            ("check pc", 2.5),
            ("check drivers", 2.5),
            ("check uefi module", 2.5),
            ("check hyperV", 2.5),
        ]
        self.success_text = "successful"
        self.current_step = 0
        self.start_time = time.time()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.next_step)
        self.timer.start(100)
        self.show()

    def next_step(self):
        elapsed = time.time() - self.start_time
        if self.current_step < len(self.steps):
            step, duration = self.steps[self.current_step]
            self.label.setText(step)
            self.status.setText(f"{int((elapsed/10)*100)}%")
            if elapsed > (self.current_step+1)*2.5:
                self.current_step += 1
        elif self.current_step == len(self.steps):
            self.label.setText(self.success_text)
            self.status.setText("100%")
            self.current_step += 1
            self.success_time = time.time()
        elif self.current_step == len(self.steps)+1:
            if time.time() - self.success_time > 2:
                self.timer.stop()
                self.hide()
                wait_for_notepad(self.on_notepad_found)

    def on_notepad_found(self):
        self.menu = MainMenu()
        self.menu.show()
        # Глобальный хоткей на Insert через keyboard
        kb.add_hotkey('insert', lambda: QtCore.QTimer.singleShot(0, self.menu.toggle_visibility))

    def resizeEvent(self, event):
        self.gradient.setGeometry(self.rect())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loader = BootLoader()
    sys.exit(app.exec_())
