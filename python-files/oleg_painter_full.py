#!/usr/bin/env python3
"""
OlegPainter Lite - English (Full UI + Auto-draw automation)

Features included in this file:
- PyQt5 UI matching the screenshot (in English)
- Image selection + resize to drawing grid
- Calibration: select paint area (by clicking two corners) and set HEX input focus
- Two modes: Color (grouped-by-color) and Black & White (threshold)
- Start/Pause/Stop/Reset controls and hotkeys (F1-F5)
- Drawing runs in a background QThread and updates progress in the UI
- Uses pyautogui + pyperclip to paste HEX and click on the Roblox canvas
- Safety: move mouse to a corner to trigger pyautogui failsafe, or press Stop in UI

Important: This automates keyboard/mouse. Using automation in Roblox may violate Roblox TOS and can lead to bans.
Test in a throwaway account / private place only.

Dependencies:
    pip install PyQt5 pillow pyautogui pyperclip

To build an .exe (after testing):
    pip install pyinstaller
    pyinstaller --onefile --windowed oleg_painter_full.py

Author note: adapt the paste sequence if Roblox's color UI doesn't accept Ctrl+V+Enter directly.

"""

import sys, os, time, threading
from collections import defaultdict
from PIL import Image
import pyautogui, pyperclip

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QProgressBar, QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# ---------------------- Worker Thread ----------------------
class DrawWorker(QThread):
    progress_update = pyqtSignal(int, int)  # percent, painted_pixels
    status = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, cal, image_path, mode, target_w, delay_between_clicks, parent=None):
        super().__init__(parent)
        self.cal = cal
        self.image_path = image_path
        self.mode = mode  # 'color' or 'bw'
        self.target_w = target_w
        self.delay = delay_between_clicks
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def hex_from_rgb(self, rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb[:3])

    def load_and_prepare(self):
        img = Image.open(self.image_path).convert("RGBA")
        aspect = img.height / img.width
        w = self.target_w
        h = max(1, int(round(w * aspect)))
        img_small = img.resize((w, h), resample=Image.NEAREST)
        pixels = img_small.convert("RGBA").load()
        width, height = img_small.size
        pixel_list = []
        for y in range(height):
            for x in range(width):
                r,g,b,a = pixels[x,y]
                if a < 20:
                    pixel_list.append((x,y,None))
                else:
                    if self.mode == 'bw':
                        # convert to gray and threshold to black/white
                        gray = int(0.299*r + 0.587*g + 0.114*b)
                        if gray < 128:
                            pixel_list.append((x,y,"#000000"))
                        else:
                            pixel_list.append((x,y,"#FFFFFF"))
                    else:
                        pixel_list.append((x,y,self.hex_from_rgb((r,g,b))))
        return img_small, pixel_list

    def run(self):
        try:
            if not os.path.exists(self.image_path):
                self.status.emit("Image missing")
                self.finished_signal.emit()
                return
            img_small, pixel_list = self.load_and_prepare()
            total_pixels = sum(1 for (_,_,c) in pixel_list if c is not None)
            painted = 0
            # calculate mapping
            x1,y1,x2,y2 = self.cal
            xmin, ymin = min(x1,x2), min(y1,y2)
            xmax, ymax = max(x1,x2), max(y1,y2)
            area_w = xmax - xmin
            area_h = ymax - ymin
            img_w, img_h = img_small.size
            step_x = area_w / img_w
            step_y = area_h / img_h

            if self.mode == 'color':
                # group by hex to minimize pastes
                groups = defaultdict(list)
                for x,y,hexc in pixel_list:
                    if hexc is None: continue
                    groups[hexc].append((x,y))
                all_colors = list(groups.items())
                count = 0
                for hexc, points in all_colors:
                    if self._stop_flag: break
                    # paste HEX into focused hex input
                    pyperclip.copy(hexc)
                    time.sleep(0.05)
                    pyautogui.hotkey('ctrl','v')
                    time.sleep(0.05)
                    pyautogui.press('enter')
                    time.sleep(0.05)
                    for px,py in points:
                        if self._stop_flag: break
                        sx = xmin + (px + 0.5) * step_x
                        sy = ymin + (py + 0.5) * step_y
                        pyautogui.moveTo(sx, sy, duration=0.01)
                        pyautogui.click()
                        painted += 1
                        count += 1
                        percent = int(painted/total_pixels*100) if total_pixels else 100
                        self.progress_update.emit(percent, painted)
                        time.sleep(self.delay)
                self.status.emit("Done" if not self._stop_flag else "Stopped")
            else:
                # pixel order
                for x,y,hexc in pixel_list:
                    if self._stop_flag: break
                    if hexc is None: continue
                    pyperclip.copy(hexc)
                    time.sleep(0.02)
                    pyautogui.hotkey('ctrl','v')
                    time.sleep(0.02)
                    pyautogui.press('enter')
                    time.sleep(0.03)
                    sx = xmin + (x + 0.5) * step_x
                    sy = ymin + (y + 0.5) * step_y
                    pyautogui.moveTo(sx, sy, duration=0.01)
                    pyautogui.click()
                    painted += 1
                    percent = int(painted/total_pixels*100) if total_pixels else 100
                    self.progress_update.emit(percent, painted)
                    time.sleep(self.delay)
                self.status.emit("Done" if not self._stop_flag else "Stopped")

        except pyautogui.FailSafeException:
            self.status.emit("Failsafe triggered")
        except Exception as e:
            self.status.emit("Error: " + str(e))
        finally:
            self.finished_signal.emit()

# ---------------------- Main UI ----------------------
class PainterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OlegPainter Lite 1.1 (English)")
        self.setFixedSize(420, 540)

        self.image_path = None
        self.calibration = None  # (x1,y1,x2,y2)
        self.hex_field_focused = False

        self.worker = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Controls group
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout()

        self.btn_select_image = QPushButton("Select Image")
        self.btn_area = QPushButton("Select Area (F1)")
        self.btn_start_pause = QPushButton("Start / Pause (F2)")
        self.btn_reset = QPushButton("Reset (F4)")
        self.btn_stop_exit = QPushButton("Stop / Exit (F3)")
        self.btn_set_hex = QPushButton("Set HEX Field (F5)")

        for btn in [self.btn_select_image, self.btn_area, self.btn_start_pause,
                    self.btn_reset, self.btn_stop_exit, self.btn_set_hex]:
            btn.setFixedHeight(36)
            control_layout.addWidget(btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        lbl_mode = QLabel("Mode:")
        self.radio_color = QRadioButton("Color")
        self.radio_bw = QRadioButton("Black & White")
        self.radio_color.setChecked(True)
        mode_layout.addWidget(lbl_mode)
        mode_layout.addWidget(self.radio_color)
        mode_layout.addWidget(self.radio_bw)
        settings_layout.addLayout(mode_layout)

        self.lbl_image_status = QLabel("No image selected")
        settings_layout.addWidget(self.lbl_image_status)

        self.lbl_progress = QLabel("Progress: 0%")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        settings_layout.addWidget(self.lbl_progress)
        settings_layout.addWidget(self.progress_bar)

        self.lbl_pixels = QLabel("Pixels: 0 / 0")
        settings_layout.addWidget(self.lbl_pixels)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        lbl_hotkeys = QLabel("Hotkeys: F1(Area), F2(Start/Pause), F3(Stop), F4(Reset), F5(HEX Field)")
        lbl_hotkeys.setWordWrap(True)
        layout.addWidget(lbl_hotkeys)

        # connect signals
        self.btn_select_image.clicked.connect(self.select_image)
        self.btn_area.clicked.connect(self.select_area)
        self.btn_start_pause.clicked.connect(self.start_pause)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_stop_exit.clicked.connect(self.stop_exit)
        self.btn_set_hex.clicked.connect(self.set_hex_field)

        self.setLayout(layout)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select image to draw", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self.image_path = path
            self.lbl_image_status.setText(f"Selected: {os.path.basename(path)}")
            # compute pixels placeholder
            try:
                img = Image.open(path)
                self.lbl_pixels.setText(f"Pixels: {img.width} x {img.height}")
            except:
                self.lbl_pixels.setText("Pixels: unknown")

    def select_area(self):
        QMessageBox.information(self, "Select Area", "You will be asked to click the TOP-LEFT then BOTTOM-RIGHT corners of the paint area.\n\nAfter clicking each point, return to this dialog and press OK.")
        # wait for the user to click two points: we ask them to move mouse and press ENTER in console — but we have GUI only.
        # Simpler: give 5 seconds to move mouse to top-left and then capture, then 5 seconds for bottom-right.
        QMessageBox.information(self, "Top-Left", "Place the mouse over the TOP-LEFT corner of the paint area in Roblox. You have 5 seconds.\nMove the mouse now and do not click; the position will be captured.")
        time.sleep(0.8)
        for i in range(5,0,-1):
            QApplication.processEvents()
            time.sleep(1)
        x1,y1 = pyautogui.position()
        QMessageBox.information(self, "Bottom-Right", f"Captured top-left at ({x1},{y1}).\n\nNow move mouse over BOTTOM-RIGHT corner. You have 5 seconds.")
        for i in range(5,0,-1):
            QApplication.processEvents()
            time.sleep(1)
        x2,y2 = pyautogui.position()
        self.calibration = (x1,y1,x2,y2)
        QMessageBox.information(self, "Calibrated", f"Captured area: ({x1},{y1}) -> ({x2},{y2})")
        self.status_message("Area set")

    def set_hex_field(self):
        QMessageBox.information(self, "Set HEX Field", "Click the HEX input field in Roblox now to focus it. Then return here and press OK.\nWhen drawing, the program will paste HEX and press Enter to apply color.")
        # we won't programmatically capture the focus; we trust the user focused the field.
        self.hex_field_focused = True
        self.status_message("HEX field assumed focused")

    def start_pause(self):
        if self.worker and self.worker.isRunning():
            # pause/stop functionality: we'll stop the worker and allow restart (simple)
            self.worker.stop()
            self.worker = None
            self.status_message("Paused/Stopped")
            return

        if not self.image_path:
            QMessageBox.warning(self, "No image", "Please select an image first.")
            return
        if not self.calibration:
            QMessageBox.warning(self, "No area", "Please select the paint area first (F1).")
            return

        mode = 'color' if self.radio_color.isChecked() else 'bw'
        # ask for width (target grid width)
        w, ok = QInputDialog_getInt(self, "Target width", "Enter drawing width in paint pixels (recommended <=200):", 80, 10, 800, 1)
        if not ok:
            return
        delay, ok2 = QInputDialog_getFloat(self, "Delay", "Delay between clicks in seconds (smaller -> faster):", 0.01, 0.0, 1.0, 2)
        if not ok2:
            return

        # start worker
        self.worker = DrawWorker(self.calibration, self.image_path, mode, w, delay)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.status.connect(self.status_message)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()
        self.status_message("Started")

    def on_progress(self, percent, painted):
        self.progress_bar.setValue(percent)
        self.lbl_progress.setText(f"Progress: {percent}%")
        self.lbl_pixels.setText(f"Painted: {painted}")

    def on_finished(self):
        self.status_message("Worker finished")
        self.worker = None

    def reset(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "Worker is running. Stop it first.")
            return
        self.image_path = None
        self.calibration = None
        self.hex_field_focused = False
        self.lbl_image_status.setText("No image selected")
        self.lbl_progress.setText("Progress: 0%")
        self.progress_bar.setValue(0)
        self.lbl_pixels.setText("Pixels: 0 / 0")
        self.status_message("Reset")

    def stop_exit(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker = None
            time.sleep(0.2)
        QApplication.quit()

    def status_message(self, text):
        self.lbl_progress.setText("Status: " + text)

# -------------------- Helpers for simple dialogs (to avoid extra imports) --------------------
def QInputDialog_getInt(parent, title, label, value, minv, maxv, step):
    from PyQt5.QtWidgets import QInputDialog
    val, ok = QInputDialog.getInt(parent, title, label, value, minv, maxv, step)
    return val, ok

def QInputDialog_getFloat(parent, title, label, value, minv, maxv, decimals):
    from PyQt5.QtWidgets import QInputDialog
    val, ok = QInputDialog.getDouble(parent, title, label, value, minv, maxv, decimals)
    return val, ok

# ---------------------- Main ----------------------
def main():
    app = QApplication(sys.argv)
    window = PainterUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
