import sys, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QSpinBox, QComboBox,
    QToolButton, QHBoxLayout, QVBoxLayout, QGroupBox, QMessageBox,
    QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt, QSize, QProcess, QStandardPaths, QTimer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # --- Ölçek faktörü (320x240 -> 640x480: 2x) ---
        self.SCALE = 2
        s = self.SCALE

        self.setWindowTitle("TRV-BORESIGHT")
        self.setFixedSize(QSize(320*s, 240*s))  # 640x480
        self.setStyleSheet(f"""
            QWidget {{ font-size: {12*s}px; }}
            QGroupBox {{
                font-weight: bold;
                border: {max(1, int(1*s))}px solid #bfbfbf;
                border-radius: {6*s}px;
                margin-top: {6*s}px;
            }}
            QGroupBox::title {{ left: {8*s}px; top: {-2*s}px; padding: 0 {4*s}px; }}
            QToolButton {{ padding: {4*s}px; }}
            QToolButton::menu-indicator {{ image: none; }}
        """)

        # --- Üstte ortada: Bağlan ikonu ---
        self.connect_icon = QToolButton()
        self.connect_icon.setText("Bağlan")
        self.connect_icon.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton))
        self.connect_icon.setIconSize(QSize(24*s, 24*s))
        self.connect_icon.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.connect_icon.setAutoRaise(True)
        self.connect_icon.clicked.connect(self.on_connect_clicked)

        # Üst satır: ortada bağlan
        header = QHBoxLayout()
        header.setContentsMargins(8*s, 8*s, 8*s, 0)
        header.addStretch(1); header.addWidget(self.connect_icon); header.addStretch(1)

        # x, y, Tzoom
        self.x_spin = self._make_coord_spin("x"); self.x_spin.setRange(-75, 75)
        self.y_spin = self._make_coord_spin("y"); self.y_spin.setRange(-40, 40)
        self.Tzoom_spin = self._make_coord_spin("Termal Zoom"); self.Tzoom_spin.setRange(-10, 10)

        # --- 1) Koordinatlar GroupBox ---
        self.coords_box = QGroupBox("")
        coords_row = QHBoxLayout()
        coords_row.setContentsMargins(8*s, 8*s, 8*s, 8*s)
        coords_row.setSpacing(6*s)
        coords_row.addWidget(QLabel("x:")); coords_row.addWidget(self.x_spin); coords_row.addSpacing(4*s)
        coords_row.addWidget(QLabel("y:")); coords_row.addWidget(self.y_spin); coords_row.addSpacing(4*s)
        coords_row.addWidget(QLabel("Tzoom:")); coords_row.addWidget(self.Tzoom_spin); coords_row.addStretch(1)
        self.coords_box.setLayout(coords_row)

        # --- 2) Zoom GroupBox ---
        self.zoom_center = QComboBox(); self.zoom_center.addItems(["Sol Üst","Sol Alt","Merkez","Sağ Üst","Sağ Alt"])
        self.zoom_center.setCurrentText("Merkez"); self.zoom_center.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.zoom_center.setFixedWidth(90*s)

        self.zoom_level = QComboBox(); self.zoom_level.addItems(["x1","x2","x4","x8"])
        self.zoom_level.setCurrentText("x1"); self.zoom_level.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.zoom_level.setFixedWidth(60*s)

        self.zoom_box = QGroupBox("")
        zoom_row = QHBoxLayout()
        zoom_row.setContentsMargins(8*s, 8*s, 8*s, 8*s)
        zoom_row.setSpacing(6*s)
        zoom_row.addWidget(QLabel("Zoom Merkezi:")); zoom_row.addWidget(self.zoom_center); zoom_row.addSpacing(14*s)
        zoom_row.addWidget(QLabel("Zoom:"));        zoom_row.addWidget(self.zoom_level)
        zoom_row.addStretch(1)
        self.zoom_box.setLayout(zoom_row)

        # --- 3) Kamera GroupBox ---
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["FÜZYON", "TERMAL", "GÜNDÜZ"])
        self.camera_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.camera_combo.setFixedWidth(120*s)

        self.camera_box = QGroupBox("")
        camera_row = QHBoxLayout()
        camera_row.setContentsMargins(8*s, 8*s, 8*s, 8*s)
        camera_row.setSpacing(6*s)
        camera_row.addWidget(QLabel("Kamera:"))
        camera_row.addWidget(self.camera_combo)
        camera_row.addStretch(1)
        self.camera_box.setLayout(camera_row)

        # --- Root layout ---
        root = QVBoxLayout()
        root.setContentsMargins(8*s, 8*s, 8*s, 8*s)
        root.setSpacing(8*s)
        root.addLayout(header)
        root.addSpacing(10*s)
        root.addWidget(self.coords_box)
        root.addWidget(self.zoom_box)
        root.addWidget(self.camera_box)
        root.addStretch(1)
        self.setLayout(root)

        # --- ADB / yollar ---
        self.proc = None
        self.stage = None
        self.adb_output = ""
        self.selected_serial = None
        self.remote_path_pull = "/root/.msaCfgFiles/cameraFusion.txt"         # doğrulama için
        self.remote_path_push = "/tmp/remoteBoresight.txt"
        temp_dir = QStandardPaths.writableLocation(QStandardPaths.TempLocation) or os.getcwd()
        self.local_pull_path = os.path.join(temp_dir, "cameraFusion.txt")
        self.local_push_path = os.path.join(temp_dir, "remoteBoresight.txt")
        self.adb_program = "adb.exe" if sys.platform.startswith("win") else "adb"

        # Başlangıç: pasif
        self.sequence_active = False     # zoom center iki aşamalı push sırasında kilit
        self.push_sequence = None        # [1, desired_zoom] gibi
        self.is_busy = False
        self.can_push = False

        # İki aşamalı zoom sıraları için bekleme (ms)
        self.SEQ_DELAY_MS = 600

        self._set_groups_enabled(False)
        self._set_connected_ui(False)

        # Debounce
        self.push_timer = QTimer(self); self.push_timer.setSingleShot(True)
        self.push_timer.timeout.connect(self._start_push)

        # Değer değişimlerinde push
        self.x_spin.valueChanged.connect(self._schedule_push)
        self.y_spin.valueChanged.connect(self._schedule_push)
        self.Tzoom_spin.valueChanged.connect(self._schedule_push)
        self.zoom_level.currentIndexChanged.connect(self._schedule_push)
        self.zoom_center.currentIndexChanged.connect(self._schedule_push)
        # KAMERA: hem UI aç/kapa kuralını uygula hem push planla
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)

        # Eşleştirme tabloları
        self.ZOOM_LEVEL_MAP  = {"x1": 1, "x2": 2, "x4": 4, "x8": 8}
        self.ZOOM_CENTER_MAP = {"Merkez": 0, "Sol Üst": 1, "Sağ Üst": 2, "Sol Alt": 3, "Sağ Alt": 4}
        self.CAMERA_MAP      = {"TERMAL": 1, "GÜNDÜZ": 2, "FÜZYON": 3}
        self.CAMERA_CODE_TO_TEXT = {1: "TERMAL", 2: "GÜNDÜZ", 3: "FÜZYON"}

        # Bağlantı izleme
        self.monitor_proc = None
        self.monitor_stage = None
        self.monitor_output = ""
        self.monitor_timer = QTimer(self)
        self.monitor_timer.setInterval(2000)  # 2 sn
        self.monitor_timer.timeout.connect(self._tick_monitor)
        self.monitor_timer.start()

        # İlk açılışta da kural uygula (bağlantı kapalıyken zaten pasifler)
        self._apply_camera_rule_after_enable()

    # ---------- Yardımcılar ----------
    def _make_coord_spin(self, name: str) -> QSpinBox:
        s = self.SCALE
        sp = QSpinBox(); sp.setObjectName(name)
        sp.setRange(-1_000_000, 1_000_000); sp.setSingleStep(1)
        sp.setKeyboardTracking(False); sp.setFixedWidth(60*s)
        sp.setToolTip(f"{name} için tam sayı girin veya oklarla değiştirin."); return sp

    def _is_fusion_selected(self) -> bool:
        cam = self.camera_combo.currentText().strip().upper()
        return cam in ("FÜZYON", "FUSION")

    def _set_groups_enabled(self, enabled: bool):
        # Zoom ve kamera kutuları doğrudan bağlantıya bağlı
        self.zoom_box.setEnabled(enabled)
        self.camera_box.setEnabled(enabled)
        # Koordinatlar: hem bağlantı açık olmalı hem de FÜZYON seçili olmalı
        self.coords_box.setEnabled(enabled and self._is_fusion_selected())

    def _set_connected_ui(self, connected: bool):
        s = self.SCALE
        if connected:
            self.connect_icon.setEnabled(False)
            self.connect_icon.setText("Bağlandı")
            self.connect_icon.setStyleSheet(
                f"QToolButton {{ background-color: #27ae60; color: white; padding: {4*s}px; "
                f"border: {max(1, int(1*s))}px solid #1e874b; border-radius: {6*s}px; }}"
            )
        else:
            self.connect_icon.setEnabled(True)
            self.connect_icon.setText("Bağlan")
            self.connect_icon.setStyleSheet("")

    def _apply_camera_rule_after_enable(self):
        """Bağlantı açıkken FÜZYON değilse koordinat kutusunu kapat."""
        if not (self.zoom_box.isEnabled() and self.camera_box.isEnabled()):
            self.coords_box.setEnabled(False); return
        self.coords_box.setEnabled(self._is_fusion_selected())

    def _begin_busy(self):
        if not self.is_busy:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.is_busy = True

    def _end_busy(self):
        if self.is_busy:
            QApplication.restoreOverrideCursor()
            self.is_busy = False

    # --------- Bağlan akışı (pull ile doğrula) ---------
    def on_connect_clicked(self):
        if self.is_busy:
            return
        self._begin_busy()
        self._set_groups_enabled(False)
        self.can_push = False
        self._run_adb(["devices"], stage="check_devices")

    def _run_adb(self, args, stage):
        if self.proc and self.proc.state() != QProcess.NotRunning:
            return
        self.stage = stage
        self.adb_output = ""
        myproc = QProcess(self)
        self.proc = myproc
        myproc.setProgram(self.adb_program)
        myproc.setArguments(args)
        myproc.setProcessChannelMode(QProcess.MergedChannels)
        myproc.readyReadStandardOutput.connect(self._collect_output)
        myproc.finished.connect(self._on_proc_finished)
        myproc.errorOccurred.connect(self._on_proc_error)
        myproc.start()

    def _collect_output(self):
        self.adb_output += bytes(self.proc.readAll()).decode(errors="ignore")

    def _on_proc_finished(self, exit_code, status):
        if self.stage == "check_devices":
            serials = []
            for ln in self.adb_output.splitlines():
                ln = ln.strip()
                if "\tdevice" in ln and not ln.startswith("List of devices"):
                    serials.append(ln.split("\t")[0])
            if not serials:
                self._finish_with_error("Bağlı/yetkili cihaz bulunamadı.")
                return
            self.selected_serial = serials[0]
            self._run_adb(["-s", self.selected_serial, "shell", "ls", "-l", self.remote_path_pull], stage="check_remote")
            return

        if self.stage == "check_remote":
            if exit_code != 0 or "No such file" in self.adb_output or "Permission denied" in self.adb_output:
                self._finish_with_error(
                    f"Uzak dosya erişilemedi: {self.remote_path_pull}\n{self.adb_output.strip()}"
                )
                return
            try:
                if os.path.exists(self.local_pull_path):
                    os.remove(self.local_pull_path)
            except Exception:
                pass
            self._run_adb(["-s", self.selected_serial, "pull", self.remote_path_pull, self.local_pull_path], stage="pull_file")
            return

        if self.stage == "pull_file":
            if exit_code != 0 or not os.path.exists(self.local_pull_path) or os.path.getsize(self.local_pull_path) == 0:
                self._finish_with_error(f"'adb pull' başarısız veya dosya boş.\n{self.adb_output.strip()}")
                return

            # 1) PULL DOSYAYI OKU (önce değerleri set et, sonra UI'yi aç)
            try:
                with open(self.local_pull_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()

                # --- Kamera (1. satır) ---
                cam_code = None
                if len(lines) >= 1:
                    first = (lines[0] or "").strip().upper()
                    try:
                        cam_code = int(''.join(ch for ch in first if ch.isdigit()))
                        if cam_code not in (1, 2, 3):
                            cam_code = None
                    except Exception:
                        cam_code = None
                    if cam_code is None:
                        if "FUSION" in first or "FÜZYON" in first or "FUZYON" in first:
                            cam_code = 3
                        elif "THERMAL" in first or "TERMAL" in first:
                            cam_code = 1
                        elif "LOW" in first or "LOW LIGHT" in first or "GÜNDÜZ" in first or "GUNDUZ" in first:
                            cam_code = 2

                # Sinyalleri blokla; can_push kapalıyken set yap
                self.camera_combo.blockSignals(True)
                if cam_code in self.CAMERA_CODE_TO_TEXT:
                    cam_text = self.CAMERA_CODE_TO_TEXT[cam_code]
                    idx = self.camera_combo.findText(cam_text, Qt.MatchFixedString)
                    if idx >= 0:
                        self.camera_combo.setCurrentIndex(idx)
                self.camera_combo.blockSignals(False)

                # --- Tzoom (6), x (9), y (10) ---
                def read_int_line(n):
                    try:
                        return int((lines[n-1] if len(lines) >= n else "").strip())
                    except Exception:
                        return None

                val_tzoom = read_int_line(6)
                val_x     = read_int_line(9)
                val_y     = read_int_line(10)

                self.x_spin.blockSignals(True)
                self.y_spin.blockSignals(True)
                self.Tzoom_spin.blockSignals(True)
                if val_x is not None: self.x_spin.setValue(val_x)
                if val_y is not None: self.y_spin.setValue(val_y)
                if val_tzoom is not None: self.Tzoom_spin.setValue(val_tzoom)
                self.x_spin.blockSignals(False)
                self.y_spin.blockSignals(False)
                self.Tzoom_spin.blockSignals(False)

            except Exception as e:
                QMessageBox.warning(self, "ADB", f"Ön değerler okunamadı: {e}")

            # 2) UI'yi aç
            self._set_groups_enabled(True)
            self._set_connected_ui(True)

            # --- İSTENEN RESET: Kamerayı FÜZYON, merkez ve x1 yap; bunu hem UI'da hem cihazda uygula ---
            # UI'yi güncelle (sinyal üretmeden)
            self.camera_combo.blockSignals(True)
            self.zoom_center.blockSignals(True)
            self.zoom_level.blockSignals(True)

            # Kamera: FÜZYON
            fusion_index = self.camera_combo.findText("FÜZYON", Qt.MatchFixedString)
            if fusion_index >= 0:
                self.camera_combo.setCurrentIndex(fusion_index)
            else:
                self.camera_combo.setCurrentText("FÜZYON")

            # Zoom merkezi ve düzeyi
            self.zoom_center.setCurrentText("Merkez")
            self.zoom_level.setCurrentText("x1")

            self.camera_combo.blockSignals(False)
            self.zoom_center.blockSignals(False)
            self.zoom_level.blockSignals(False)

            # Kamera kuralını uygula (FÜZYON seçildiği için koordinatlar aktif olur)
            self._apply_camera_rule_after_enable()

            # Bundan sonra değişimler push edebilir; ilk ayarı hemen gönder (x1 + Merkez + FÜZYON)
            self.can_push = True
            self._begin_busy()
            self._push_with_zoom_code(1)  # _build_and_write_push_file() merkez ve kamera ayarlarını da dosyaya yazar
            return  # push bittiğinde push_file aşamasında finalize edilir

        if self.stage == "push_file":
            if exit_code != 0:
                # Hata: sekansı bitir
                self.sequence_active = False
                self.push_sequence = None
                QMessageBox.warning(self, "ADB", f"'adb push' başarısız:\n{self.adb_output.strip()}")
                self._finalize(); return

            # Sekans devam ediyor mu?
            if self.push_sequence:
                self.push_sequence.pop(0)
                if self.push_sequence:
                    next_zoom = self.push_sequence[0]
                    QTimer.singleShot(self.SEQ_DELAY_MS, lambda nz=next_zoom: self._push_with_zoom_code(nz))
                    return
                else:
                    self.sequence_active = False
                    self.push_sequence = None
                    self._finalize(); return

            # Sekans yoksa normal finalize
            self._finalize(); return

        self._finalize()

    def _on_proc_error(self, err):
        self.sequence_active = False
        self.push_sequence = None
        self._finish_with_error(
            "ADB başlatılamadı (PATH içinde mi?).\n"
            f"Hata kodu: {int(err)}\n\nSon çıktı:\n{self.adb_output.strip()}"
        )

    def _finish_with_error(self, msg):
        self.selected_serial = None
        self.sequence_active = False
        self.push_sequence = None
        self._set_connected_ui(False)
        self._set_groups_enabled(False)
        QMessageBox.critical(self, "ADB Hatası", msg)
        self._finalize()

    def _finalize(self):
        self._end_busy()
        self.stage = None
        self.proc = None

    # --------- Push tetikleme / dosya yazma ---------
    def _schedule_push(self):
        if (not self.selected_serial) or (not self.can_push):
            return

        sender = self.sender()

        # Zoom merkezi değiştiyse ve zoom x1 değilse -> iki aşamalı push
        if sender is self.zoom_center and self.zoom_level.currentText() != "x1":
            desired = self.ZOOM_LEVEL_MAP.get(self.zoom_level.currentText(), 1)
            self.push_sequence = [1, desired]
            self.sequence_active = True
            self.push_timer.stop()
            self.push_timer.start(50)
            return

        # Sekans çalışırken başka tetiklemeleri yut
        if self.sequence_active:
            return

        # Koordinatlar ancak coords_box açıkken (FÜZYON)
        if sender in (self.x_spin, self.y_spin, self.Tzoom_spin) and not self.coords_box.isEnabled():
            return
        # Zoom değişimleri için zoom_box açık olmalı
        if sender in (self.zoom_level, self.zoom_center) and not self.zoom_box.isEnabled():
            return
        # Kamera için camera_box açık olmalı
        if sender is self.camera_combo and not self.camera_box.isEnabled():
            return

        self.push_timer.start(150)

    def _build_and_write_push_file(self, zoom_code):
        center_code = self.ZOOM_CENTER_MAP.get(self.zoom_center.currentText(), 0)
        cam_text    = self.camera_combo.currentText().strip().upper()
        if cam_text in ("FUSION", "FÜZYON", "FUZYON"):
            camera_code = 3
        elif cam_text in ("THERMAL", "TERMAL"):
            camera_code = 1
        else:
            camera_code = 2  # LOW LIGHT / GÜNDÜZ

        lines = [
            str(self.x_spin.value()),         # 1: x
            str(self.y_spin.value()),         # 2: y
            str(self.Tzoom_spin.value()),     # 3: Tzoom
            str(zoom_code),                   # 4: Zoom (kod)
            str(center_code),                 # 5: Zoom Merkezi (kod)
            str(camera_code),                 # 6: Kamera (kod)
        ]
        with open(self.local_push_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _push_with_zoom_code(self, zoom_code):
        try:
            self._build_and_write_push_file(zoom_code)
        except Exception as e:
            self.sequence_active = False
            self.push_sequence = None
            QMessageBox.warning(self, "Dosya", f"remoteBoresight.txt oluşturulamadı:\n{e}")
            self._end_busy()
            return
        self._run_adb(["-s", self.selected_serial, "push", self.local_push_path, self.remote_path_push],
                      stage="push_file")

    def _start_push(self):
        if self.is_busy or (self.proc and self.proc.state() != QProcess.NotRunning):
            self.push_timer.start(100); return
        if not self.selected_serial or not self.can_push:
            return

        # Gönderilecek zoom kodu
        zoom_code = self.push_sequence[0] if self.push_sequence else self.ZOOM_LEVEL_MAP.get(self.zoom_level.currentText(), 1)

        self._begin_busy()
        self._push_with_zoom_code(zoom_code)

    # --------- Otomatik bağlantı izleme ---------
    def _tick_monitor(self):
        if self.is_busy or (self.proc and self.proc.state() != QProcess.NotRunning):
            return
        if getattr(self, "monitor_proc", None) and self.monitor_proc.state() != QProcess.NotRunning:
            return

        self.monitor_output = ""
        self.monitor_proc = QProcess(self)
        self.monitor_proc.setProgram(self.adb_program)
        if self.selected_serial:
            self.monitor_stage = "mon_get_state"
            self.monitor_proc.setArguments(["-s", self.selected_serial, "get-state"])
        else:
            self.monitor_stage = "mon_devices"
            self.monitor_proc.setArguments(["devices"])

        self.monitor_proc.setProcessChannelMode(QProcess.MergedChannels)
        self.monitor_proc.readyReadStandardOutput.connect(
            lambda: self._collect_monitor_output()
        )
        self.monitor_proc.finished.connect(self._on_monitor_finished)
        self.monitor_proc.start()

    def _collect_monitor_output(self):
        self.monitor_output += bytes(self.monitor_proc.readAll()).decode(errors="ignore")

    def _on_monitor_finished(self, exit_code, status):
        out = (self.monitor_output or "").strip()

        if self.monitor_stage == "mon_get_state":
            still_ok = (exit_code == 0 and "device" in out.lower())
            if not still_ok:
                self.selected_serial = None
                self.sequence_active = False
                self.push_sequence = None
                self._set_connected_ui(False)
                self._set_groups_enabled(False)
        # mon_devices: yalnız buton aktif kalır
        self.monitor_proc = None
        self.monitor_stage = None
        self.monitor_output = ""

    # --------- Kamera değişimi: koordinatları yönet + push planla ---------
    def _on_camera_changed(self, *_):
        # Bağlantı durumu uygunsa koordinat kutusunu aç/kapat
        self._apply_camera_rule_after_enable()
        # Değişikliği cihaza iletilsin (bağlıysa)
        self._schedule_push()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
