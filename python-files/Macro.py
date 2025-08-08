import sys
import os
import json
import time
import threading
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QFileDialog, QMessageBox, QLineEdit, QTextEdit,
    QInputDialog
)
from PyQt6.QtCore import Qt, QTimer

from pynput import keyboard, mouse

# ----------------------- Data structures -----------------------

@dataclass
class Event:
    type: str  # 'key', 'button', 'move', 'scroll'
    time: float
    data: Dict[str, Any]

@dataclass
class Macro:
    name: str
    events: List[Event] = field(default_factory=list)
    hotkey: str = ""  # optional assigned hotkey (string representation)

    def to_json(self):
        return {
            'name': self.name,
            'hotkey': self.hotkey,
            'events': [asdict(e) for e in self.events]
        }

    @staticmethod
    def from_json(obj):
        m = Macro(name=obj.get('name', 'Unnamed'))
        m.hotkey = obj.get('hotkey', '')
        for e in obj.get('events', []):
            m.events.append(Event(type=e['type'], time=e['time'], data=e['data']))
        return m

# ----------------------- Recorder & Player -----------------------

class Recorder:
    def __init__(self):
        self.events: List[Event] = []
        self.start_time = None
        self.k_listener = None
        self.m_listener = None
        self.running = False

    def _stamp(self):
        return time.time() - self.start_time

    def start(self):
        if self.running:
            return
        self.events.clear()
        self.start_time = time.time()
        self.running = True

        # Keyboard
        def on_press(key):
            try:
                keyname = key.char
            except AttributeError:
                keyname = str(key)
            self.events.append(Event('key', self._stamp(), {'action': 'press', 'key': keyname}))

        def on_release(key):
            try:
                keyname = key.char
            except AttributeError:
                keyname = str(key)
            self.events.append(Event('key', self._stamp(), {'action': 'release', 'key': keyname}))

        # Mouse
        def on_move(x, y):
            self.events.append(Event('move', self._stamp(), {'x': x, 'y': y}))

        def on_click(x, y, button, pressed):
            self.events.append(Event('button', self._stamp(), {'x': x, 'y': y, 'button': str(button), 'pressed': pressed}))

        def on_scroll(x, y, dx, dy):
            self.events.append(Event('scroll', self._stamp(), {'x': x, 'y': y, 'dx': dx, 'dy': dy}))

        self.k_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.m_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self.k_listener.start()
        self.m_listener.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.k_listener:
            self.k_listener.stop()
            self.k_listener = None
        if self.m_listener:
            self.m_listener.stop()
            self.m_listener = None
        return self.events.copy()

class Player:
    def __init__(self):
        self.k_controller = keyboard.Controller()
        self.m_controller = mouse.Controller()
        self._stop_flag = threading.Event()

    def play(self, events: List[Event], speed=1.0):
        self._stop_flag.clear()
        if not events:
            return

        def runner():
            t0 = events[0].time
            start = time.time()
            for ev in events:
                if self._stop_flag.is_set():
                    break
                # compute target time considering speed
                target = start + (ev.time - t0) / speed
                to_wait = target - time.time()
                if to_wait > 0:
                    time.sleep(to_wait)
                # execute
                if ev.type == 'key':
                    action = ev.data.get('action')
                    key = ev.data.get('key')
                    # try to parse special keys
                    try:
                        if len(key) == 1:
                            k = key
                        else:
                            # string like 'Key.space' or "Key.enter"
                            name = key.replace('Key.', '')
                            k = getattr(keyboard.Key, name)
                    except Exception:
                        k = key
                    if action == 'press':
                        try:
                            self.k_controller.press(k)
                        except Exception:
                            pass
                    else:
                        try:
                            self.k_controller.release(k)
                        except Exception:
                            pass
                elif ev.type == 'move':
                    x, y = ev.data.get('x'), ev.data.get('y')
                    try:
                        self.m_controller.position = (x, y)
                    except Exception:
                        pass
                elif ev.type == 'button':
                    btn = ev.data.get('button').replace('Button.', '')
                    pressed = ev.data.get('pressed')
                    try:
                        btn_obj = getattr(mouse.Button, btn)
                    except Exception:
                        btn_obj = mouse.Button.left
                    if pressed:
                        self.m_controller.press(btn_obj)
                    else:
                        self.m_controller.release(btn_obj)
                elif ev.type == 'scroll':
                    dx = ev.data.get('dx')
                    dy = ev.data.get('dy')
                    try:
                        self.m_controller.scroll(dx, dy)
                    except Exception:
                        pass

        t = threading.Thread(target=runner, daemon=True)
        t.start()

    def stop(self):
        self._stop_flag.set()

# ----------------------- Macro manager -----------------------

class MacroManager:
    def __init__(self):
        self.macros: List[Macro] = []
        self.players: Dict[str, Player] = {}
        self.hotkey_registry = {}  # hotkey string -> macro name
        self.gh = None  # GlobalHotKeys instance
        self.gh_thread = None

    def add_macro(self, macro: Macro):
        self.macros.append(macro)

    def remove_macro(self, idx: int):
        del self.macros[idx]

    def save_to_file(self, path: str):
        data = {'macros': [m.to_json() for m in self.macros]}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.macros.clear()
        for m in data.get('macros', []):
            self.macros.append(Macro.from_json(m))

    def import_json(self, json_text: str):
        data = json.loads(json_text)
        imported = []
        for m in data.get('macros', []):
            imported.append(Macro.from_json(m))
        self.macros.extend(imported)

    def export_json(self):
        return json.dumps({'macros': [m.to_json() for m in self.macros]}, indent=2)

    # Hotkey registration using pynput's GlobalHotKeys
    def register_hotkeys(self, callback):
        # callback: function(macro_name) -> None
        if self.gh:
            try:
                self.gh.stop()
            except Exception:
                pass
        # build mapping like '<ctrl>+<alt>+h': lambda: callback('macro')
        mapping = {}
        for m in self.macros:
            if m.hotkey:
                # pynput uses format: '<ctrl>+<alt>+h' or '<f8>' etc. We'll assume user stores in that format.
                keystr = m.hotkey
                def make_cb(name):
                    return lambda: callback(name)
                mapping[keystr] = make_cb(m.name)
        if mapping:
            try:
                self.gh = keyboard.GlobalHotKeys(mapping)
                self.gh.start()
            except Exception as e:
                print('Hotkey registration failed:', e)

    def unregister_hotkeys(self):
        if self.gh:
            try:
                self.gh.stop()
            except Exception:
                pass
            self.gh = None

# ----------------------- GUI -----------------------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MacroMaster — Prototype')
        self.resize(900, 500)

        self.manager = MacroManager()
        self.recorder = Recorder()
        self.player = Player()

        # Left: macro list
        self.list = QListWidget()
        self.list_label = QLabel('Macros')

        # Right: controls
        self.record_btn = QPushButton('Record New Macro')
        self.stop_btn = QPushButton('Stop Recording')
        self.play_btn = QPushButton('Play Selected')
        self.stop_play_btn = QPushButton('Stop Playback')
        self.new_btn = QPushButton('New Empty Macro')
        self.delete_btn = QPushButton('Delete Selected')
        self.edit_btn = QPushButton('Edit Selected (JSON)')
        self.assign_hotkey_btn = QPushButton('Assign Hotkey')
        self.save_btn = QPushButton('Save Project')
        self.load_btn = QPushButton('Load Project')
        self.import_btn = QPushButton('Import JSON')
        self.export_btn = QPushButton('Export JSON')

        # Layout
        left_v = QVBoxLayout()
        left_v.addWidget(self.list_label)
        left_v.addWidget(self.list)

        right_v = QVBoxLayout()
        right_v.addWidget(self.record_btn)
        right_v.addWidget(self.stop_btn)
        right_v.addWidget(self.play_btn)
        right_v.addWidget(self.stop_play_btn)
        right_v.addWidget(self.new_btn)
        right_v.addWidget(self.delete_btn)
        right_v.addWidget(self.edit_btn)
        right_v.addWidget(self.assign_hotkey_btn)
        right_v.addStretch()
        right_v.addWidget(self.import_btn)
        right_v.addWidget(self.export_btn)
        right_v.addWidget(self.save_btn)
        right_v.addWidget(self.load_btn)

        main_h = QHBoxLayout()
        main_h.addLayout(left_v, 2)
        main_h.addLayout(right_v, 1)
        self.setLayout(main_h)

        # connections
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.play_btn.clicked.connect(self.play_selected)
        self.stop_play_btn.clicked.connect(self.stop_playing)
        self.new_btn.clicked.connect(self.new_macro)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.assign_hotkey_btn.clicked.connect(self.assign_hotkey)
        self.save_btn.clicked.connect(self.save_project)
        self.load_btn.clicked.connect(self.load_project)
        self.import_btn.clicked.connect(self.import_json)
        self.export_btn.clicked.connect(self.export_json)

        self.refresh_timer = QTimer(self)\)
        self.refresh_timer.timeout.connect(self.refresh_list)
        self.refresh_timer.start(500)

        # playback thread reference
        self.playback_threads: Dict[str, Player] = {}

    def refresh_list(self):
        sel = self.list.currentRow()
        self.list.blockSignals(True)
        self.list.clear()
        for m in self.manager.macros:
            hk = f' [{m.hotkey}]' if m.hotkey else ''
            self.list.addItem(m.name + hk)
        self.list.blockSignals(False)
        if 0 <= sel < self.list.count():
            self.list.setCurrentRow(sel)

    # ---------------- UI actions ----------------
    def start_recording(self):
        # when recording, we ask user for a name
        name, ok = QInputDialog.getText(self, 'Record Macro', 'Macro name:')
        if not ok or not name.strip():
            return
        self.recorder.start()
        self._current_record_name = name.strip()
        QMessageBox.information(self, 'Recording', 'Recording started. Use Stop Recording to finish.')

    def stop_recording(self):
        events = self.recorder.stop()
        if events is None:
            QMessageBox.warning(self, 'Not recording', 'No active recording found.')
            return
        macro = Macro(name=self._current_record_name, events=events)
        self.manager.add_macro(macro)
        QMessageBox.information(self, 'Saved', f'Macro "{macro.name}" saved with {len(events)} events.')
        # refresh list will show it

    def play_selected(self):
        idx = self.list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, 'None selected', 'Select a macro first.')
            return
        macro = self.manager.macros[idx]
        # start a player for this macro
        p = Player()
        p.play(macro.events)
        self.playback_threads[macro.name] = p
        QMessageBox.information(self, 'Playing', f'Playing macro "{macro.name}"')

    def stop_playing(self):
        for p in self.playback_threads.values():
            try:
                p.stop()
            except Exception:
                pass
        self.playback_threads.clear()
        QMessageBox.information(self, 'Stopped', 'All playback stopped.')

    def new_macro(self):
        name, ok = QInputDialog.getText(self, 'New Macro', 'Macro name:')
        if not ok or not name.strip():
            return
        self.manager.add_macro(Macro(name=name.strip()))

    def delete_selected(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        name = self.manager.macros[idx].name
        reply = QMessageBox.question(self, 'Delete', f'Delete macro "{name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.remove_macro(idx)

    def edit_selected(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        macro = self.manager.macros[idx]
        text = json.dumps(macro.to_json(), indent=2)
        editor = QTextEdit()
        editor.setPlainText(text)
        editor.setWindowTitle(f'Edit Macro JSON — {macro.name}')
        editor.resize(700, 500)

        def save_and_close():
            try:
                obj = json.loads(editor.toPlainText())
                newm = Macro.from_json(obj)
                # replace
                self.manager.macros[idx] = newm
                editor.close()
                QMessageBox.information(self, 'Saved', f'Macro "{newm.name}" saved.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', 'Invalid JSON: ' + str(e))

        save_btn = QPushButton('Save')
        save_btn.clicked.connect(save_and_close)
        layout = QVBoxLayout()
        layout.addWidget(editor)
        layout.addWidget(save_btn)
        w = QWidget()
        w.setLayout(layout)
        w.setWindowModality(Qt.WindowModality.ApplicationModal)
        w.show()

    def assign_hotkey(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        macro = self.manager.macros[idx]
        hk, ok = QInputDialog.getText(self, 'Assign Hotkey', 'Enter hotkey in pynput format (e.g. "<ctrl>+<alt>+h" or "<f8>"):\nSee pynput docs for supported keys')
        if not ok or not hk.strip():
            return
        macro.hotkey = hk.strip()
        # re-register hotkeys
        self.manager.register_hotkeys(self.hotkey_triggered)
        QMessageBox.information(self, 'Hotkey assigned', f'Hotkey {macro.hotkey} -> {macro.name}')

    def hotkey_triggered(self, macro_name):
        # called in separate thread by global hotkey; we must not touch Qt widgets from here
        print('Hotkey triggered for', macro_name)
        # play macro by name
        for m in self.manager.macros:
            if m.name == macro_name:
                p = Player()
                p.play(m.events)
                self.playback_threads[m.name] = p
                break

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Project', filter='JSON files (*.json)')
        if not path:
            return
        self.manager.save_to_file(path)
        QMessageBox.information(self, 'Saved', f'Project saved to {path}')

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load Project', filter='JSON files (*.json)')
        if not path:
            return
        try:
            self.manager.load_from_file(path)
            self.manager.register_hotkeys(self.hotkey_triggered)
        except Exception as e:
            QMessageBox.critical(self, 'Failed', 'Could not load: ' + str(e))

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Import JSON', filter='JSON files (*.json)')
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                txt = f.read()
            self.manager.import_json(txt)
            QMessageBox.information(self, 'Imported', 'Imported macros from JSON')
        except Exception as e:
            QMessageBox.critical(self, 'Failed', 'Import failed: ' + str(e))

    def export_json(self):
        txt = self.manager.export_json()
        path, _ = QFileDialog.getSaveFileName(self, 'Export JSON', filter='JSON files (*.json)')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(txt)
            QMessageBox.information(self, 'Exported', f'Exported to {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Failed', 'Export failed: ' + str(e))

# ----------------------- Main -----------------------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
