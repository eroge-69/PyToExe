#!/usr/bin/env python3
"""
Compass Desktop App
- Shows a compass with 360 degree ticks (one-degree granularity)
- Resizable
- "Always on top" toggle
- Global hotkey (default: Ctrl+Alt+C) to show/hide the window

Dependencies:
    pip install PyQt5 pynput

Run:
    python compass_app.py

Notes:
- Global hotkeys use pynput. On some systems you may need elevated privileges.
- If you want to change the default hotkey, click 'Set Hotkey' and press the desired key combo.
"""

import sys
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput import keyboard


class CompassWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.heading = 0.0  # degrees

    def set_heading(self, deg: float):
        self.heading = deg % 360
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        size = min(rect.width(), rect.height())
        cx = rect.center().x()
        cy = rect.center().y()
        radius = int(size * 0.45)

        # background
        painter.fillRect(rect, self.palette().window())

        # draw outer circle
        pen = QtGui.QPen(QtGui.QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(QtCore.QPoint(cx, cy), radius, radius)

        # translate / rotate to draw ticks relative to heading
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.heading)  # rotate so heading points up

        # Draw degree ticks: 360 ticks
        for d in range(360):
            if d % 10 == 0:
                tick_len = int(radius * 0.12)
                pen.setWidth(2)
            elif d % 5 == 0:
                tick_len = int(radius * 0.08)
                pen.setWidth(1)
            else:
                tick_len = int(radius * 0.04)
                pen.setWidth(1)

            painter.setPen(pen)
            painter.drawLine(0, -radius, 0, -radius + tick_len)

            # labels every 30 degrees plus cardinal points
            if d % 30 == 0:
                painter.save()
                painter.translate(0, -radius + tick_len + 12)
                painter.rotate(self.heading - d)
                label = str(d)
                fm = painter.fontMetrics()
                w = fm.horizontalAdvance(label)
                painter.drawText(-w / 2, 0, label)
                painter.restore()

            painter.rotate(1)

        painter.restore()

        # draw heading pointer (triangle)
        pointer_path = QtGui.QPolygon([
            QtCore.QPoint(cx, cy - radius + 6),
            QtCore.QPoint(cx - 10, cy - radius + 30),
            QtCore.QPoint(cx + 10, cy - radius + 30),
        ])
        painter.setBrush(QtGui.QBrush(QtGui.QColor(200, 30, 30)))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.drawPolygon(pointer_path)

        # Draw center circle and heading text
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(240, 240, 240)))
        painter.drawEllipse(QtCore.QPoint(cx, cy), int(radius * 0.14), int(radius * 0.14))

        heading_text = f"{self.heading:.0f}°"
        font = painter.font()
        font.setPointSize(max(8, int(radius * 0.12)))
        painter.setFont(font)
        fm = painter.fontMetrics()
        w = fm.horizontalAdvance(heading_text)
        h = fm.height()
        painter.setPen(QtGui.QPen(QtGui.QColor(10, 10, 10)))
        painter.drawText(cx - w / 2, cy + h / 4, heading_text)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compass")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(380, 380)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        self.compass = CompassWidget()
        layout.addWidget(self.compass, stretch=1)

        controls = QtWidgets.QHBoxLayout()
        layout.addLayout(controls)

        self.always_on_top_cb = QtWidgets.QCheckBox("Always on top")
        self.always_on_top_cb.setChecked(True)
        self.always_on_top_cb.stateChanged.connect(self.toggle_always_on_top)
        controls.addWidget(self.always_on_top_cb)

        self.set_hotkey_btn = QtWidgets.QPushButton("Set Hotkey")
        self.set_hotkey_btn.clicked.connect(self.record_hotkey)
        controls.addWidget(self.set_hotkey_btn)

        self.hotkey_label = QtWidgets.QLabel("Hotkey: Ctrl+Alt+C")
        controls.addWidget(self.hotkey_label)

        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        controls.addItem(spacer)

        self.quit_btn = QtWidgets.QPushButton("Quit")
        self.quit_btn.clicked.connect(self.close_app)
        controls.addWidget(self.quit_btn)

        # heading simulation slider for testing
        slider_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(slider_layout)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 359)
        self.slider.valueChanged.connect(self.compass.set_heading)
        slider_layout.addWidget(QtWidgets.QLabel("Heading"))
        slider_layout.addWidget(self.slider)

        # global hotkey handling
        self.hotkey = '<ctrl>+<alt>+c'
        self.hotkey_display = 'Ctrl+Alt+C'
        self.hotkey_listener = None
        self.hotkey_lock = threading.Lock()
        self._start_hotkey_listener()

        # hotkey recording flag
        self.recording = False

    def toggle_always_on_top(self, state):
        flags = self.windowFlags()
        if state == QtCore.Qt.Checked:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def close_app(self):
        self._stop_hotkey_listener()
        QtWidgets.qApp.quit()

    def _on_hotkey_activate(self):
        # toggle visibility
        QtCore.QMetaObject.invokeMethod(self, "_toggle_visibility", QtCore.Qt.QueuedConnection)

    @QtCore.pyqtSlot()
    def _toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _start_hotkey_listener(self):
        with self.hotkey_lock:
            if self.hotkey_listener:
                try:
                    self.hotkey_listener.stop()
                except Exception:
                    pass

            # convert our simple string into pynput format
            # expected like '<ctrl>+<alt>+c'
            try:
                self.hotkey_listener = keyboard.GlobalHotKeys({self.hotkey: self._on_hotkey_activate})
                thread = threading.Thread(target=self.hotkey_listener.start, daemon=True)
                thread.start()
            except Exception as e:
                print('Hotkey listener start failed:', e)

    def _stop_hotkey_listener(self):
        with self.hotkey_lock:
            if self.hotkey_listener:
                try:
                    self.hotkey_listener.stop()
                except Exception:
                    pass
                self.hotkey_listener = None

    def record_hotkey(self):
        if self.recording:
            return
        self.recording = True
        self.set_hotkey_btn.setText('Press desired combo... (Esc to cancel)')

        # temporary listener to capture key combo
        combo = []

        def on_press(key):
            try:
                k = key.char
            except AttributeError:
                k = str(key).replace('Key.', '<') + '>'
            if k not in combo:
                combo.append(k)

        def on_release(key):
            # stop on release of all keys or on esc
            if key == keyboard.Key.esc:
                return False
            # if at least one non-modifier released, finish
            # simplistic: stop when any alphanumeric key released
            try:
                if hasattr(key, 'char') and key.char is not None:
                    return False
            except Exception:
                pass
            return True

        def listener_thread():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as lis:
                lis.join()
            # process combo
            if not combo:
                self.recording = False
                QtCore.QMetaObject.invokeMethod(self, 'reset_hotkey_button', QtCore.Qt.QueuedConnection)
                return

            # build simple representation
            # convert pynput names into our format
            parts = []
            for item in combo:
                if item.startswith('<') and item.endswith('>'):
                    name = item
                else:
                    name = item.upper()
                parts.append(name)

            # build hotkey pattern for GlobalHotKeys; map common keys
            # very naive: accept modifiers ctrl, alt, shift and one key
            modifiers = []
            key_main = None
            for p in parts:
                pl = p.lower()
                if pl in ('<ctrl>', '<control>'):
                    modifiers.append('<ctrl>')
                elif pl in ('<alt>',):
                    modifiers.append('<alt>')
                elif pl in ('<shift>',):
                    modifiers.append('<shift>')
                else:
                    # assume last is main
                    key_main = pl.strip('<>') if pl.startswith('<') else pl
            if key_main is None:
                # invalid combo
                self.recording = False
                QtCore.QMetaObject.invokeMethod(self, 'reset_hotkey_button', QtCore.Qt.QueuedConnection)
                return

            pattern = '+'.join(modifiers + [key_main])
            # ensure angle brackets around modifiers when needed
            pattern = pattern.replace('ctrl', '<ctrl>').replace('alt', '<alt>').replace('shift', '<shift>')

            self.hotkey = pattern
            display = '+'.join([p.strip('<>').title() for p in (modifiers + [key_main])])
            self.hotkey_display = display
            QtCore.QMetaObject.invokeMethod(self, 'apply_new_hotkey', QtCore.Qt.QueuedConnection)
            self.recording = False

        t = threading.Thread(target=listener_thread, daemon=True)
        t.start()

    @QtCore.pyqtSlot()
    def reset_hotkey_button(self):
        self.set_hotkey_btn.setText('Set Hotkey')

    @QtCore.pyqtSlot()
    def apply_new_hotkey(self):
        self.set_hotkey_btn.setText('Set Hotkey')
        self.hotkey_label.setText(f'Hotkey: {self.hotkey_display}')
        self._start_hotkey_listener()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
