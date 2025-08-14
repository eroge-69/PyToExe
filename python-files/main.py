import sys
import time
import json
import threading
from dataclasses import dataclass, asdict
from typing import List
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

@dataclass
class InputEvent:
    timestamp: float
    kind: str   # 'mouse_move','mouse_click','mouse_scroll','key_down','key_up'
    x: int = 0
    y: int = 0
    button: str = ''
    pressed: bool = False
    dx: int = 0
    dy: int = 0
    key: str = ''

class Recorder:
    def __init__(self):
        self.reset()
        self._mouse_listener = None
        self._key_listener = None

    def reset(self):
        self.start_time = None
        self.events: List[InputEvent] = []
        self.recording = False

    def _timestamp(self):
        return (time.time() - self.start_time) * 1000.0  # ms

    def start(self):
        if self.recording:
            return
        self.reset()
        self.start_time = time.time()
        self.recording = True
        self._mouse_listener = mouse.Listener(on_move=self.on_move,
                                              on_click=self.on_click,
                                              on_scroll=self.on_scroll)
        self._key_listener = keyboard.Listener(on_press=self.on_press,
                                               on_release=self.on_release)
        self._mouse_listener.start()
        self._key_listener.start()

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._key_listener:
            self._key_listener.stop()
            self._key_listener = None

    def on_move(self, x, y):
        if not self.recording: return
        self.events.append(InputEvent(timestamp=self._timestamp(),
                                      kind='mouse_move', x=int(x), y=int(y)))
    def on_click(self, x, y, button, pressed):
        if not self.recording: return
        self.events.append(InputEvent(timestamp=self._timestamp(),
                                      kind='mouse_click', x=int(x), y=int(y),
                                      button=str(button), pressed=bool(pressed)))
    def on_scroll(self, x, y, dx, dy):
        if not self.recording: return
        self.events.append(InputEvent(timestamp=self._timestamp(),
                                      kind='mouse_scroll', x=int(x), y=int(y),
                                      dx=int(dx), dy=int(dy)))
    def on_press(self, key):
        if not self.recording: return
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        self.events.append(InputEvent(timestamp=self._timestamp(), kind='key_down', key=k))
    def on_release(self, key):
        if not self.recording: return
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        self.events.append(InputEvent(timestamp=self._timestamp(), kind='key_up', key=k))

class Player:
    def __init__(self):
        self._mouse = MouseController()
        self._key = KeyboardController()
        self._stop = threading.Event()
        self.speed = 1.0
        self.loop = False
        self.thread = None

    def play(self, events, speed=1.0, loop=False):
        if self.thread and self.thread.is_alive():
            return
        self._stop.clear()
        self.speed = max(0.01, speed)
        self.loop = loop
        self.thread = threading.Thread(target=self._run, args=(events,), daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self, events):
        if not events:
            return
        while not self._stop.is_set():
            t0 = events[0].timestamp
            prev = t0
            for e in events:
                if self._stop.is_set():
                    break
                wait = max(0.0, (e.timestamp - prev) / self.speed / 1000.0)
                time.sleep(wait)
                prev = e.timestamp
                if e.kind == 'mouse_move':
                    try:
                        self._mouse.position = (e.x, e.y)
                    except Exception:
                        pass
                elif e.kind == 'mouse_click':
                    try:
                        btn = Button.left if 'Button.left' in e.button or 'left' in e.button.lower() else Button.right
                        if e.pressed:
                            self._mouse.press(btn)
                        else:
                            self._mouse.release(btn)
                    except Exception:
                        pass
                elif e.kind == 'mouse_scroll':
                    try:
                        self._mouse.scroll(e.dx, e.dy)
                    except Exception:
                        pass
                elif e.kind == 'key_down':
                    try:
                        k = _to_key_obj(e.key)
                        if isinstance(k, Key):
                            self._key.press(k)
                        else:
                            self._key.press(k)
                    except Exception:
                        pass
                elif e.kind == 'key_up':
                    try:
                        k = _to_key_obj(e.key)
                        if isinstance(k, Key):
                            self._key.release(k)
                        else:
                            self._key.release(k)
                    except Exception:
                        pass
            if not self.loop:
                break

def _to_key_obj(kstr):
    # try to map string back to Key or char
    if kstr.startswith("Key."):
        name = kstr.split('.',1)[1]
        try:
            return getattr(Key, name)
        except Exception:
            return kstr
    if len(kstr) == 1:
        return kstr
    return kstr

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('dis7inked Macro (Python)')
        self.resize(900, 600)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.record_btn = QtWidgets.QPushButton('⏺ Record')
        self.play_btn = QtWidgets.QPushButton('▶ Play')
        self.stop_btn = QtWidgets.QPushButton('⏹ Stop')
        toolbar.addWidget(self.record_btn)
        toolbar.addWidget(self.play_btn)
        toolbar.addWidget(self.stop_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Controls
        ctrl_layout = QtWidgets.QHBoxLayout()
        self.loop_cb = QtWidgets.QCheckBox('Loop')
        ctrl_layout.addWidget(self.loop_cb)
        ctrl_layout.addWidget(QtWidgets.QLabel('Speed:'))
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(500)
        self.speed_slider.setValue(100)
        ctrl_layout.addWidget(self.speed_slider)
        self.speed_label = QtWidgets.QLabel('1.00×')
        ctrl_layout.addWidget(self.speed_label)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # List
        self.listw = QtWidgets.QListWidget()
        layout.addWidget(self.listw)

        # Save/Load/Clear
        bottom = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton('⬇ Save Macro')
        self.load_btn = QtWidgets.QPushButton('⬆ Load Macro')
        self.clear_btn = QtWidgets.QPushButton('🗑 Clear')
        bottom.addWidget(self.save_btn)
        bottom.addWidget(self.load_btn)
        bottom.addWidget(self.clear_btn)
        bottom.addStretch()
        layout.addLayout(bottom)

        # Status bar
        self.status = self.statusBar()
        self.status.showMessage('Idle')

        # Recorder and player
        self.rec = Recorder()
        self.player = Player()

        # Connections
        self.record_btn.clicked.connect(self.toggle_record)
        self.play_btn.clicked.connect(self.start_play)
        self.stop_btn.clicked.connect(self.stop_all)
        self.save_btn.clicked.connect(self.save_macro)
        self.load_btn.clicked.connect(self.load_macro)
        self.clear_btn.clicked.connect(self.clear_macro)
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        self._hotkey_listener = keyboard.GlobalHotKeys({ '<ctrl>+<shift>+r': self._hotkey_record,
                                                          '<ctrl>+<shift>+p': self._hotkey_play,
                                                          '<ctrl>+<shift>+s': self._hotkey_stop })
        self._hotkey_listener.start()

    def _hotkey_record(self):
        QtCore.QMetaObject.invokeMethod(self, 'toggle_record', QtCore.Qt.ConnectionType.QueuedConnection)
    def _hotkey_play(self):
        QtCore.QMetaObject.invokeMethod(self, 'start_play', QtCore.Qt.ConnectionType.QueuedConnection)
    def _hotkey_stop(self):
        QtCore.QMetaObject.invokeMethod(self, 'stop_all', QtCore.Qt.ConnectionType.QueuedConnection)

    @QtCore.pyqtSlot()
    def toggle_record(self):
        if not self.rec.recording:
            self.rec.start()
            self.listw.clear()
            self.status.showMessage('Recording...')
            self.record_btn.setText('⏹ Stop Recording')
            # spawn a small updater to add entries live
            self._update_timer = QtCore.QTimer(self)
            self._update_timer.timeout.connect(self._refresh_list)
            self._update_timer.start(200)
        else:
            self.rec.stop()
            self._update_timer.stop()
            self._refresh_list()
            self.status.showMessage('Idle')
            self.record_btn.setText('⏺ Record')

    def _refresh_list(self):
        self.listw.clear()
        for i,e in enumerate(self.rec.events):
            if e.kind.startswith('mouse'):
                txt = f"{i+1}: {e.kind} @ {e.x},{e.y} t={int(e.timestamp)}ms"
            else:
                txt = f"{i+1}: {e.kind} {e.key} t={int(e.timestamp)}ms"
            self.listw.addItem(txt)

    @QtCore.pyqtSlot()
    def start_play(self):
        if not self.rec.events:
            QMessageBox.information(self, 'Empty', 'No recorded events to play.')
            return
        # prepare events copy
        events_copy = list(self.rec.events)
        speed = self.speed_slider.value() / 100.0
        loop = self.loop_cb.isChecked()
        self.status.showMessage('Playing...')
        self.player.play(events_copy, speed=speed, loop=loop)

    @QtCore.pyqtSlot()
    def stop_all(self):
        self.rec.stop()
        self.player.stop()
        self.status.showMessage('Idle')
        self.record_btn.setText('⏺ Record')

    def save_macro(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Macro', filter='Macro Files (*.json)')
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([asdict(e) for e in self.rec.events], f, indent=2)

    def load_macro(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load Macro', filter='Macro Files (*.json)')
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.rec.events = [InputEvent(**d) for d in data]
        self._refresh_list()

    def clear_macro(self):
        self.rec.reset()
        self.listw.clear()

    def _on_speed_change(self, v):
        val = v / 100.0
        self.speed_label.setText(f"{val:.2f}×")

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
