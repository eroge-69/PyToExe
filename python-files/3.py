import sys
import os
import traceback
import wave
from typing import Optional, List, Tuple

import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QSpinBox, QMessageBox, QHBoxLayout, QLineEdit, QCheckBox,
    QSlider, QFileDialog, QComboBox, QDialog, QFormLayout, QDialogButtonBox, QInputDialog
)
from PyQt5.QtCore import (
    Qt, QTimer, QUrl, QRect, QPoint, QSettings, QByteArray, QCoreApplication
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtGui import QImage, QFont
from PyQt5.QtNetwork import QAuthenticator

# Dźwięk (opcjonalny)
try:
    from PyQt5.QtMultimedia import QSoundEffect
except Exception:
    QSoundEffect = None


# -----------------------
# Generowanie plików WAV
# -----------------------
def ensure_pattern_wav(path: str, pattern: List[Tuple[float, float, float]], sample_rate: int = 44100) -> None:
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                head = f.read(12)
                if head.startswith(b"RIFF"):
                    return
    except Exception:
        pass

    data = np.array([], dtype=np.int16)
    for freq, dur, sil in pattern:
        if dur > 0:
            n = int(sample_rate * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            if freq > 0:
                wave_chunk = (0.30 * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
            else:
                wave_chunk = np.zeros(n, dtype=np.int16)
            data = np.concatenate([data, wave_chunk])
        if sil > 0:
            ns = int(sample_rate * sil)
            data = np.concatenate([data, np.zeros(ns, dtype=np.int16)])

    try:
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(data.tobytes())
    except Exception:
        pass


# -----------------------
# Dialog uwierzytelnienia
# -----------------------
class AuthDialog(QDialog):
    def __init__(self, url: QUrl, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Uwierzytelnienie wymagane")
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        form = QFormLayout()
        form.addRow(QLabel(f"Adres: {url.toString()}"))
        form.addRow("Użytkownik:", self.user_edit)
        form.addRow("Hasło:", self.pass_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)
        self.setLayout(form)

    def get_credentials(self) -> Optional[Tuple[str, str]]:
        if self.exec_() == QDialog.Accepted:
            return self.user_edit.text(), self.pass_edit.text()
        return None


# -----------------------
# Okno alarmu
# -----------------------
class AlarmWindow(QMainWindow):
    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        self.setWindowTitle("NG Alarm")
        self.resize(400, 200)

        self.label = QLabel("NG Alarm", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 28, QFont.Bold))
        self.setStyleSheet("background-color: red;")
        self.label.setStyleSheet("color: black; font-weight: bold;")

        self._blink_state = False
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_colors)

        self._auto_stop_timer = QTimer(self)
        self._auto_stop_timer.setSingleShot(True)
        self._auto_stop_timer.timeout.connect(self.stop_alarm)

        self._sound_enabled: bool = True
        self._sound_volume: float = 0.8
        self._sound_path: Optional[str] = None
        self._sound: Optional[QSoundEffect] = None
        if QSoundEffect is not None:
            self._sound = QSoundEffect(self)
            self._sound.setLoopCount(QSoundEffect.Infinite)

        self._restore_geometry()

    def _restore_geometry(self):
        try:
            ba = self._settings.value("alarm/geometry", None)
            if isinstance(ba, (QByteArray, bytes, bytearray)):
                self.restoreGeometry(ba if isinstance(ba, QByteArray) else QByteArray(ba))
        except Exception:
            pass

    def _save_geometry(self):
        try:
            self._settings.setValue("alarm/geometry", self.saveGeometry())
        except Exception:
            pass

    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.height())
        self._save_geometry()
        super().resizeEvent(event)

    def moveEvent(self, event):
        self._save_geometry()
        super().moveEvent(event)

    def set_sound_enabled(self, enabled: bool) -> None:
        self._sound_enabled = enabled
        self._settings.setValue("sound/enabled", enabled)

    def set_volume(self, vol_0_1: float) -> None:
        self._sound_volume = max(0.0, min(1.0, vol_0_1))
        if self._sound is not None:
            self._sound.setVolume(self._sound_volume)
        self._settings.setValue("sound/volume", int(self._sound_volume * 100))

    def set_sound_path(self, path: Optional[str]) -> None:
        self._sound_path = path
        self._settings.setValue("sound/path", path if path else "")

    def start_alarm(self, duration_seconds: int, fallback_initial_geometry: Optional[List[int]] = None):
        ba = self._settings.value("alarm/geometry", None)
        if ba is None and fallback_initial_geometry:
            try:
                x, y, w, h = map(int, fallback_initial_geometry)
                self.setGeometry(x, y, w, h)
            except Exception:
                pass

        self.showNormal()
        self.raise_()
        self._blink_state = False
        self._apply_colors()
        self._blink_timer.start(500)
        self._auto_stop_timer.start(max(1, duration_seconds) * 1000)

        if self._sound is not None and self._sound_enabled and self._sound_path:
            try:
                self._sound.setSource(QUrl.fromLocalFile(self._sound_path))
                self._sound.setVolume(self._sound_volume)
                self._sound.play()
            except Exception:
                pass

    def stop_alarm(self):
        self._blink_timer.stop()
        if self._sound is not None:
            try:
                self._sound.stop()
            except Exception:
                pass
        self.hide()

    def _toggle_colors(self):
        self._blink_state = not self._blink_state
        self._apply_colors()

    def _apply_colors(self):
        if self._blink_state:
            self.setStyleSheet("background-color: black;")
            self.label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.setStyleSheet("background-color: red;")
            self.label.setStyleSheet("color: black; font-weight: bold;")


# -----------------------
# ROI
# -----------------------
class RoiSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start = None
        self.end = None
        self.drawing = False
        self.saved_rect = None
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent;")
        self.hide()

    def enable_selection(self):
        self.start = None
        self.end = None
        self.drawing = False
        self.saved_rect = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.show()
        self.raise_()
        self.update()

    def disable_selection(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing and self.start:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start:
            self.end = event.pos()
            self.saved_rect = QRect(self.start, self.end).normalized()
            self.drawing = False
            self.disable_selection()
            self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        if self.drawing and self.start and self.end:
            painter.drawRect(QRect(self.start, self.end).normalized())
        elif self.saved_rect:
            painter.drawRect(self.saved_rect)

    def getRect(self) -> Optional[QRect]:
        return self.saved_rect


# -----------------------
# CustomWebEnginePage
# -----------------------
class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)

    def createWindow(self, web_window_type):
        popup_view = QWebEngineView()
        popup_view.setAttribute(Qt.WA_DeleteOnClose)
        popup_view.setWindowTitle("Popup")
        popup_view.resize(900, 700)

        popup_page = CustomWebEnginePage(self.profile(), popup_view)
        popup_view.setPage(popup_page)
        popup_view.show()
        return popup_page

    def javaScriptAlert(self, securityOrigin, msg):
        QMessageBox.information(None, f"Alert: {securityOrigin.host()}", msg)

    def javaScriptConfirm(self, securityOrigin, msg):
        ret = QMessageBox.question(None, f"Potwierdź: {securityOrigin.host()}", msg)
        return ret == QMessageBox.Yes

    def javaScriptPrompt(self, securityOrigin, msg, defaultValue):
        text, ok = QInputDialog.getText(None, f"Prompt: {securityOrigin.host()}", msg, QLineEdit.Normal, defaultValue)
        if ok:
            return text
        return None

    def javaScriptConsoleMessage(self, level, msg, lineNumber, sourceID):
        print(f"[JS:{level}] {sourceID}:{lineNumber} {msg}")


# -----------------------
# OCRMonitor
# -----------------------
class OCRMonitor(QMainWindow):
    def __init__(self, settings: QSettings, beeps: dict):
        super().__init__()
        self._settings = settings
        self._beeps = beeps
        self.setWindowTitle("OCR w ROI – wykrywanie słowa i alarm")
        self.setGeometry(200, 100, 1280, 800)

        root = QVBoxLayout()

        url_bar = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Wpisz adres (np. https://...)")
        self.go_btn = QPushButton("Idź")
        self.go_btn.clicked.connect(self.load_page)
        url_bar.addWidget(self.url_input)
        url_bar.addWidget(self.go_btn)
        root.addLayout(url_bar)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)

        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)

        # ✅ poprawione — sygnały auth na page
        self.page.authenticationRequired.connect(self.on_auth_required)
        self.page.proxyAuthenticationRequired.connect(self.on_proxy_auth_required)

        s = self.browser.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        self.browser.setUrl(QUrl("https://www.example.com"))
        root.addWidget(self.browser)

        row1 = QHBoxLayout()
        self.roi_btn = QPushButton("Zaznacz ROI")
        self.roi_btn.clicked.connect(self.activate_roi_selection)
        row1.addWidget(self.roi_btn)

        row1.addWidget(QLabel("Szukane słowo:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("np. NG, Błąd, ALERT ...")
        row1.addWidget(self.keyword_input)

        row1.addWidget(QLabel("Częstotliwość (s):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(1)
        row1.addWidget(self.interval_spin)

        row1.addWidget(QLabel("Czas alarmu (s):"))
        self.alarm_time_spin = QSpinBox()
        self.alarm_time_spin.setRange(1, 120)
        self.alarm_time_spin.setValue(10)
        row1.addWidget(self.alarm_time_spin)
        root.addLayout(row1)

        row2 = QHBoxLayout()
        self.case_insensitive = QCheckBox("Ignoruj wielkość liter")
        self.case_insensitive.setChecked(True)
        row2.addWidget(self.case_insensitive)

        self.whole_word = QCheckBox("Tylko całe słowo")
        self.whole_word.setChecked(False)
        row2.addWidget(self.whole_word)

        row2.addWidget(QLabel("Dźwięk:"))
        self.sound_select = QComboBox()
        self.sound_select.addItems(["Beep 1", "Beep 2", "Beep 3", "Własny (WAV)"])
        row2.addWidget(self.sound_select)

        self.choose_wav_btn = QPushButton("Wybierz plik…")
        self.choose_wav_btn.clicked.connect(self.choose_custom_wav)
        row2.addWidget(self.choose_wav_btn)

        self.sound_checkbox = QCheckBox("Włącz dźwięk")
        self.sound_checkbox.setChecked(True)
        row2.addWidget(self.sound_checkbox)

        row2.addWidget(QLabel("Głośność (%)"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(140)
        row2.addWidget(self.volume_slider)

        self.test_sound_btn = QPushButton("Test dźwięku")
        self.test_sound_btn.clicked.connect(self.test_sound)
        row2.addWidget(self.test_sound_btn)

        self.start_btn = QPushButton("Start monitoringu")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        row2.addWidget(self.start_btn)

        root.addLayout(row2)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

        self.roi_overlay = RoiSelector(self)
        self.alarm = AlarmWindow(self._settings)

        self._reader = None
        self._ocr_running = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._load_sound_settings()
        self._update_sound_controls_enabled()

    # --- Auth ---
    def on_auth_required(self, url: QUrl, auth: QAuthenticator):
        dlg = AuthDialog(url, self)
        creds = dlg.get_credentials()
        if creds is not None:
            user, pwd = creds
            auth.setUser(user)
            auth.setPassword(pwd)

    def on_proxy_auth_required(self, url: QUrl, auth: QAuthenticator, proxyHost: str):
        dlg = AuthDialog(url, self)
        creds = dlg.get_credentials()
        if creds is not None:
            user, pwd = creds
            auth.setUser(user)
            auth.setPassword(pwd)

    # --- Dźwięk ---
    def _load_sound_settings(self):
        preset = self._settings.value("sound/preset", "Beep 1")
        if preset not in ["Beep 1", "Beep 2", "Beep 3", "Własny (WAV)"]:
            preset = "Beep 1"
        idx = self.sound_select.findText(preset)
        if idx >= 0:
            self.sound_select.setCurrentIndex(idx)

        self._custom_wav_path = self._settings.value("sound/custom_path", "", type=str)
        enabled = self._settings.value("sound/enabled", True, type=bool)
        self.sound_checkbox.setChecked(bool(enabled))
        vol = self._settings.value("sound/volume", 80, type=int)
        vol = max(0, min(100, int(vol)))
        self.volume_slider.setValue(vol)

        self._apply_sound_to_alarm()
        self.sound_select.currentTextChanged.connect(self._on_sound_preset_changed)
        self.sound_checkbox.stateChanged.connect(self._on_sound_enabled_changed)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)

    def _apply_sound_to_alarm(self):
        self.alarm.set_sound_enabled(self.sound_checkbox.isChecked())
        self.alarm.set_volume(self.volume_slider.value() / 100.0)
        preset = self.sound_select.currentText()
        self._settings.setValue("sound/preset", preset)

        if preset == "Własny (WAV)":
            if self._custom_wav_path and os.path.exists(self._custom_wav_path):
                self.alarm.set_sound_path(os.path.abspath(self._custom_wav_path))
                self._settings.setValue("sound/custom_path", self._custom_wav_path)
            else:
                self.alarm.set_sound_path(None)
        else:
            path = self._beeps.get(preset, "")
            if path and os.path.exists(path):
                self.alarm.set_sound_path(os.path.abspath(path))
            else:
                self.alarm.set_sound_path(None)

    def _on_sound_preset_changed(self, _txt):
        self._apply_sound_to_alarm()
        self._update_sound_controls_enabled()

    def _on_sound_enabled_changed(self, _state):
        self._settings.setValue("sound/enabled", self.sound_checkbox.isChecked())
        self.alarm.set_sound_enabled(self.sound_checkbox.isChecked())

    def _on_volume_changed(self, _val):
        self.alarm.set_volume(self.volume_slider.value() / 100.0)

    def _update_sound_controls_enabled(self):
        use_custom = (self.sound_select.currentText() == "Własny (WAV)")
        self.choose_wav_btn.setEnabled(use_custom)

    def choose_custom_wav(self):
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik WAV", "", "Pliki WAV (*.wav)")
        if path:
            self._custom_wav_path = path
            self._settings.setValue("sound/custom_path", path)
            if self.sound_select.currentText() == "Własny (WAV)":
                self._apply_sound_to_alarm()

    def test_sound(self):
        if QSoundEffect is None:
            QMessageBox.information(self, "Audio", "Moduł PyQt5.QtMultimedia nie jest dostępny – dźwięk wyłączony.")
            return
        preset = self.sound_select.currentText()
        if preset == "Własny (WAV)":
            if not (self._custom_wav_path and os.path.exists(self._custom_wav_path)):
                QMessageBox.warning(self, "Audio", "Najpierw wybierz własny plik WAV.")
                return
            src = os.path.abspath(self._custom_wav_path)
        else:
            src = self._beeps.get(preset, "")
            if not (src and os.path.exists(src)):
                QMessageBox.warning(self, "Audio", "Brak pliku dźwiękowego dla wybranego presetu.")
                return

        eff = QSoundEffect(self)
        eff.setSource(QUrl.fromLocalFile(src))
        eff.setLoopCount(1)
        eff.setVolume(self.volume_slider.value() / 100.0)
        self._test_effect = eff
        eff.play()

    # --- Nawigacja ---
    def load_page(self):
        url_text = self.url_input.text().strip()
        if not url_text:
            QMessageBox.warning(self, "Błąd", "Podaj adres strony!")
            return
        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def activate_roi_selection(self):
        QMessageBox.information(self, "Tryb ROI", "Przeciągnij myszką, aby zaznaczyć obszar na stronie.")
        self.roi_overlay.enable_selection()
        self._sync_overlay()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_overlay()

    def _sync_overlay(self):
        top_left_in_main = self.browser.mapTo(self, QPoint(0, 0))
        self.roi_overlay.setGeometry(
            top_left_in_main.x(),
            top_left_in_main.y(),
            self.browser.width(),
            self.browser.height()
        )

    @staticmethod
    def _qimage_to_numpy_bgr(img: QImage) -> np.ndarray:
        if img.isNull():
            return np.zeros((1, 1, 3), dtype=np.uint8)
        qimg = img.convertToFormat(QImage.Format_RGBA8888)
        width, height = qimg.width(), qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        rgb = arr[:, :, :3]
        bgr = rgb[:, :, ::-1].copy()
        return bgr

    def _grab_browser_roi_bgr(self, roi_rect: QRect) -> Optional[np.ndarray]:
        if roi_rect is None or roi_rect.width() <= 1 or roi_rect.height() <= 1:
            return None
        pixmap = self.browser.grab()
        dpr = max(1.0, float(pixmap.devicePixelRatio()))
        img = pixmap.toImage()
        scaled = QRect(
            int(roi_rect.x() * dpr),
            int(roi_rect.y() * dpr),
            int(roi_rect.width() * dpr),
            int(roi_rect.height() * dpr),
        ).intersected(QRect(0, 0, img.width(), img.height()))
        if scaled.width() <= 1 or scaled.height() <= 1:
            return None
        crop = img.copy(scaled)
        return self._qimage_to_numpy_bgr(crop)

    def _ensure_reader(self) -> bool:
        if self._reader is not None:
            return True
        try:
            import easyocr
        except Exception as e:
            QMessageBox.critical(self, "Brak easyocr", f"Zainstaluj: pip install easyocr\n\n{e}")
            return False
        try:
            self._reader = easyocr.Reader(["pl", "en"], gpu=False, verbose=False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Błąd OCR", f"Nie udało się zainicjalizować EasyOCR:\n{e}")
            return False

    def toggle_monitoring(self):
        if self._timer.isActive():
            self._timer.stop()
            self.start_btn.setText("Start monitoringu")
            return

        if not self.roi_overlay.getRect():
            QMessageBox.warning(self, "Brak ROI", "Najpierw kliknij 'Zaznacz ROI' i wybierz obszar!")
            return

        if not self.keyword_input.text().strip():
            QMessageBox.warning(self, "Brak słowa", "Wpisz słowo, którego mamy szukać w ROI.")
            return

        if not self._ensure_reader():
            return

        self._timer.start(self.interval_spin.value() * 1000)
        self.start_btn.setText("Stop monitoringu")

    def _tick(self):
        if self._ocr_running:
            return
        self._ocr_running = True
        try:
            self._scan_once()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.warning(self, "Błąd OCR", f"Wystąpił błąd podczas OCR:\n{e}")
        finally:
            self._ocr_running = False

    def _scan_once(self):
        roi_rect = self.roi_overlay.getRect()
        if roi_rect is None:
            return
        bgr_roi = self._grab_browser_roi_bgr(roi_rect)
        if bgr_roi is None:
            return

        results = self._reader.readtext(bgr_roi, detail=0, paragraph=False)
        found = self._match_keyword(results, self.keyword_input.text())

        self._apply_sound_to_alarm()

        if found and not self.alarm.isVisible():
            initial_geom = [
                self._settings.value("alarm/default_x", 200, type=int),
                self._settings.value("alarm/default_y", 200, type=int),
                self._settings.value("alarm/default_w", 500, type=int),
                self._settings.value("alarm/default_h", 250, type=int),
            ]
            self.alarm.start_alarm(self.alarm_time_spin.value(), fallback_initial_geometry=initial_geom)

        new_interval = self.interval_spin.value() * 1000
        if self._timer.interval() != new_interval:
            self._timer.setInterval(new_interval)

    def _match_keyword(self, texts: List[str], keyword: str) -> bool:
        if not keyword:
            return False
        items = texts
        key = keyword
        if self.case_insensitive.isChecked():
            key = key.lower()
            items = [t.lower() for t in items]
        if self.whole_word.isChecked():
            for t in items:
                for token in t.split():
                    if token == key:
                        return True
            return False
        else:
            return any(key in t for t in items)


# -----------------------
# main
# -----------------------
def main():
    QCoreApplication.setOrganizationName("OCRROI")
    QCoreApplication.setApplicationName("OCR_ROI_Alarm")
    settings = QSettings()

    base_dir = os.path.abspath(os.getcwd())
    beep1 = os.path.join(base_dir, "beep1.wav")
    beep2 = os.path.join(base_dir, "beep2.wav")
    beep3 = os.path.join(base_dir, "beep3.wav")

    ensure_pattern_wav(beep1, [(880, 0.25, 0.10)])
    ensure_pattern_wav(beep2, [(660, 0.12, 0.08), (660, 0.12, 0.08), (660, 0.12, 0.20)])
    ensure_pattern_wav(beep3, [(440, 0.18, 0.05), (880, 0.18, 0.20)])

    beeps = {"Beep 1": beep1, "Beep 2": beep2, "Beep 3": beep3}

    app = QApplication(sys.argv)
    window = OCRMonitor(settings, beeps)

    if settings.value("alarm/default_x", None) is None:
        settings.setValue("alarm/default_x", 200)
    if settings.value("alarm/default_y", None) is None:
        settings.setValue("alarm/default_y", 200)
    if settings.value("alarm/default_w", None) is None:
        settings.setValue("alarm/default_w", 500)
    if settings.value("alarm/default_h", None) is None:
        settings.setValue("alarm/default_h", 250)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
