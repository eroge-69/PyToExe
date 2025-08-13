import sys
import time
import cv2
import numpy as np
from ultralytics import YOLO

# ---------- PyQt5 ----------
from PyQt5 import QtCore, QtGui, QtWidgets

# ================== TU LÓGICA ORIGINAL: VARIABLES GLOBALES ==================
model = YOLO("yolov8s.pt")

target_box = None
target_cls = None
tracking = False
zoom_scale = 2
zoom_window_name = "Zoom"            # (seguimos respetando el nombre, aunque el zoom será un QLabel)
zoom_window_size = (300, 300)
tracking_lost = False
last_detection_time = None
recovery_timeout = 5
fps = 30
prev_time = 0
selection_start = None
selection_end = None
selecting = False
manual_selection = False
auto_detection = True
tracker = None
boxes = []
using_tracker = False
current_frame = None  # mantenemos esto para la lógica existente

# ================== UTIL: LOGS A CONSOLA Y UI ==================
class LogBuffer(QtCore.QObject):
    appended = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._lines = []

    def add(self, msg: str):
        self._lines.append(msg)
        print(msg)
        self.appended.emit(msg)

log_buffer = LogBuffer()

# ================== FUNCIONES ORIGINALES (SIN CAMBIAR LÓGICA) ==================
def reset_tracking():
    global target_box, target_cls, tracking, tracking_lost, selection_start, selection_end, selecting, tracker, using_tracker
    target_box = None
    target_cls = None
    tracking = False
    tracking_lost = False
    selection_start = None
    selection_end = None
    selecting = False
    tracker = None
    using_tracker = False
    # La ventana de zoom ahora es un QLabel en Qt; no usamos cv2.destroyWindow aquí.
    log_buffer.add("Tracking reseteado. Selecciona un nuevo objeto.")

def init_tracker(bbox, frame):
    global tracker, using_tracker
    try:
        tracker = cv2.legacy.TrackerCSRT_create()
        using_tracker = True
        return tracker.init(frame, bbox)
    except Exception as e:
        log_buffer.add(f"Error al iniciar tracker: {e}")
        return False

# click_event original. Lo llamaremos manualmente desde eventos de ratón Qt.
def click_event(event, x, y, flags, param):
    global target_box, target_cls, tracking, tracking_lost, last_detection_time, using_tracker, manual_selection, tracker, current_frame, selecting, boxes

    if event == cv2.EVENT_LBUTTONDOWN:
        if manual_selection:
            # Centrar un cuadro de 30x30 en el click
            w, h = 30, 30
            x1 = max(x - w // 2, 0)
            y1 = max(y - h // 2, 0)
            x2 = min(x1 + w, current_frame.shape[1])
            y2 = min(y1 + h, current_frame.shape[0])
            target_box = (x1, y1, x2, y2)
            target_cls = None
            bbox = (x1, y1, x2 - x1, y2 - y1)
            if init_tracker(bbox, current_frame):
                tracking = True
                tracking_lost = False
                last_detection_time = time.time()
                log_buffer.add(f"Objeto seleccionado manualmente en ({x1},{y1})-({x2},{y2})")
            else:
                log_buffer.add("Error al iniciar tracker manual")
        elif not tracking or tracking_lost:
            for box in boxes:
                x1, y1, x2, y2, cls, conf = box
                if x1 <= x <= x2 and y1 <= y <= y2:
                    target_box = (x1, y1, x2, y2)
                    target_cls = cls
                    tracking = True
                    tracking_lost = False
                    last_detection_time = time.time()
                    using_tracker = False  # YOLO tracking automático
                    log_buffer.add(f"Objeto fijado (YOLO): {model.names[cls]} (Confianza: {conf:.2f})")
                    break

    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        # Tu código soporta selección por arrastre si 'selecting' es True.
        # Mantenemos el comportamiento.
        pass

    elif event == cv2.EVENT_LBUTTONUP and selecting:
        # Si alguna vez activas 'selecting', se respetará este bloque.
        pass


# ================== WIDGET DE VIDEO (EMBEBE EL FRAME EN UN QLabel) ==================
class VideoView(QtWidgets.QLabel):
    # Señales para click (x, y) en coords del frame original
    clicked = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        self.setMinimumSize(640, 480)
        self._frame_w = None
        self._frame_h = None
        self.setStyleSheet("background:#000; border-radius:12px;")

    def set_frame(self, frame_bgr):
        # Guardamos tamaño original para mapear clicks
        self._frame_h, self._frame_w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format.Format_RGB888)
        self.setPixmap(QtGui.QPixmap.fromImage(qimg))

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if self.pixmap() is None or self._frame_w is None:
            return
        # Mapeo de coordenadas del QLabel al frame original (aspect-fit)
        label_w = self.width()
        label_h = self.height()
        pix = self.pixmap()
        pix_w = pix.width()
        pix_h = pix.height()

        # El pixmap ya está escalado por setScaledContents=True: mapear proporcionalmente
        sx = self._frame_w / label_w
        sy = self._frame_h / label_h
        x = int(e.x() * sx)
        y = int(e.y() * sy)
        self.clicked.emit(x, y)


# ================== UI PRINCIPAL ==================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seguimiento YOLO - Interfaz PyQt5")
        self.resize(1200, 720)
        self.setStyleSheet("""
            * { font-family: Inter, Segoe UI, Arial; }
            QMainWindow { background: #0b1220; }
            QLabel#title { color: #e5e7eb; font-size:18px; font-weight:600; }
            QLabel#stat { color:#9ca3af; }
            QPushButton { background:#111827; color:#e5e7eb; border:1px solid #1f2937; padding:8px 12px; border-radius:10px; }
            QPushButton:hover { background:#1f2937; }
            QListWidget, QTextEdit { background:#0f172a; color:#e5e7eb; border:1px solid #1f2937; border-radius:10px; }
            QGroupBox { border:1px solid #1f2937; border-radius:14px; margin-top:14px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color:#9ca3af; }
        """)

        # ------- Widgets -------
        self.video = VideoView()

        # Panel derecho (controles/estado)
        self.btn_mode = QtWidgets.QPushButton("Cambiar modo (m)")
        self.btn_auto = QtWidgets.QPushButton("Detección ON/OFF (a)")
        self.btn_reset = QtWidgets.QPushButton("Reset (r)")

        self.lbl_mode = QtWidgets.QLabel("Modo: AUTOMÁTICO")
        self.lbl_mode.setObjectName("stat")
        self.lbl_status = QtWidgets.QLabel("Estado: SELECCIONA OBJETO")
        self.lbl_status.setObjectName("stat")
        self.lbl_fps = QtWidgets.QLabel("FPS: 0.0")
        self.lbl_fps.setObjectName("stat")

        self.list_dets = QtWidgets.QListWidget()
        self.logs = QtWidgets.QTextEdit()
        self.logs.setReadOnly(True)

        # Zoom embebido
        self.zoom_label = QtWidgets.QLabel()
        self.zoom_label.setFixedSize(*zoom_window_size)
        self.zoom_label.setStyleSheet("background:#000; border-radius:12px;")
        self.zoom_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # ------- Layouts -------
        right = QtWidgets.QWidget()
        r_layout = QtWidgets.QVBoxLayout(right)
        r_layout.setContentsMargins(12, 12, 12, 12)
        r_layout.setSpacing(12)

        title = QtWidgets.QLabel("Panel de Control")
        title.setObjectName("title")
        r_layout.addWidget(title)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.btn_mode)
        btn_row.addWidget(self.btn_auto)
        btn_row.addWidget(self.btn_reset)
        r_layout.addLayout(btn_row)

        # Estado
        state_box = QtWidgets.QGroupBox("Estado")
        sb_l = QtWidgets.QVBoxLayout(state_box)
        sb_l.addWidget(self.lbl_mode)
        sb_l.addWidget(self.lbl_status)
        sb_l.addWidget(self.lbl_fps)
        r_layout.addWidget(state_box)

        # Detecciones
        det_box = QtWidgets.QGroupBox("Detecciones (clase, conf)")
        db_l = QtWidgets.QVBoxLayout(det_box)
        db_l.addWidget(self.list_dets)
        r_layout.addWidget(det_box)

        # Zoom
        zoom_box = QtWidgets.QGroupBox("Zoom")
        zb_l = QtWidgets.QVBoxLayout(zoom_box)
        zb_l.addWidget(self.zoom_label)
        r_layout.addWidget(zoom_box)

        # Logs
        log_box = QtWidgets.QGroupBox("Logs")
        lb_l = QtWidgets.QVBoxLayout(log_box)
        lb_l.addWidget(self.logs)
        r_layout.addWidget(log_box)
        r_layout.addStretch(1)

        central = QtWidgets.QWidget()
        main = QtWidgets.QHBoxLayout(central)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(12)
        main.addWidget(self.video, 2)
        main.addWidget(right, 1)
        self.setCentralWidget(central)

        # ------- Conexiones -------
        self.btn_mode.clicked.connect(self.toggle_mode)
        self.btn_auto.clicked.connect(self.toggle_detection)
        self.btn_reset.clicked.connect(self.do_reset)
        self.video.clicked.connect(self.on_video_click)
        log_buffer.appended.connect(self.append_log)

        # Atajos de teclado (mantienen m, a, r, Esc)
        QtWidgets.QShortcut(QtGui.QKeySequence("M"), self, activated=self.toggle_mode)
        QtWidgets.QShortcut(QtGui.QKeySequence("A"), self, activated=self.toggle_detection)
        QtWidgets.QShortcut(QtGui.QKeySequence("R"), self, activated=self.do_reset)
        QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self, activated=self.close)

        # Cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            log_buffer.add("Error: No se pudo abrir la cámara")
            QtCore.QTimer.singleShot(0, self.close)
            return

        # Timer de captura/procesado (bucle principal)
        self.prev_time = time.time()
        self.frame_count = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1)  # ~ lo más rápido posible sin bloquear UI

    # ---------- UI Actions ----------
    def append_log(self, text: str):
        self.logs.append(text)

    def toggle_mode(self):
        global manual_selection
        manual_selection = not manual_selection
        reset_tracking()
        self.update_state_labels()

    def toggle_detection(self):
        global auto_detection
        auto_detection = not auto_detection
        log_buffer.add(f"Detección automática {'ACTIVADA' if auto_detection else 'DESACTIVADA'}")
        self.update_state_labels()

    def do_reset(self):
        reset_tracking()
        self.update_state_labels()

    def on_video_click(self, x, y):
        # Simulamos el callback original de OpenCV
        click_event(cv2.EVENT_LBUTTONDOWN, x, y, None, None)

    def closeEvent(self, event):
        # Liberamos cámara al cerrar
        try:
            self.cap.release()
        except:
            pass
        event.accept()

    # ---------- Procesado por frame (tu misma lógica) ----------
    def process_frame(self):
        global current_frame, boxes, fps, prev_time, frame_count, tracking, tracking_lost, last_detection_time, using_tracker, target_box, target_cls

        ret, frame = self.cap.read()
        if not ret:
            log_buffer.add("Error: No se pudo capturar el frame")
            self.timer.stop()
            return

        # Panel original dibujado bajo el frame: ahora se muestra en la UI,
        # pero respetamos el cálculo de FPS y todos los textos/estados.
        panel_height = 150
        panel = np.zeros((panel_height, frame.shape[1], 3), dtype=np.uint8)

        current_frame = frame.copy()
        boxes = []

        # FPS (igual que tu código)
        self.frame_count += 1
        curr_time = time.time()
        if curr_time - self.prev_time >= 1.0:
            fps = self.frame_count / (curr_time - self.prev_time)
            self.prev_time = curr_time
            self.frame_count = 0

        # Detección YOLO (si está activa)
        if auto_detection:
            results = model(frame, verbose=False)[0]
            for box in results.boxes:
                cls = int(box.cls[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                if conf > 0.5:
                    boxes.append((x1, y1, x2, y2, cls, conf))

        # ---------- Tracking del objeto seleccionado (idéntico a tu código) ----------
        if tracking and not tracking_lost:
            if using_tracker and tracker is not None:
                # Tracking con CSRT (modo manual)
                success, bbox = tracker.update(frame)
                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    target_box = (x, y, x + w, y + h)
                    last_detection_time = time.time()
                else:
                    if time.time() - last_detection_time > recovery_timeout:
                        tracking_lost = True
                        log_buffer.add("Objeto manual perdido. Selecciona otro")
            else:
                # Tracking con YOLO (modo automático)
                same_class_boxes = [b for b in boxes if b[4] == target_cls] if target_cls is not None else []

                if same_class_boxes:
                    tx1, ty1, tx2, ty2 = target_box
                    tcx, tcy = (tx1 + tx2) // 2, (ty1 + ty2) // 2

                    closest_box = None
                    min_dist = float('inf')

                    for box in same_class_boxes:
                        x1, y1, x2, y2, cls, conf = box
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        dist = np.hypot(cx - tcx, cy - tcy)
                        if dist < min_dist:
                            min_dist = dist
                            closest_box = box

                    if closest_box:
                        x1, y1, x2, y2, cls, conf = closest_box
                        target_box = (x1, y1, x2, y2)
                        last_detection_time = time.time()
                else:
                    if time.time() - last_detection_time > recovery_timeout:
                        tracking_lost = True
                        log_buffer.add("Objeto perdido. Buscando reencuentro...")
                    else:
                        time_left = recovery_timeout - (time.time() - last_detection_time)
                        # Mantengo el comportamiento de imprimir
                        print(f"Buscando objeto YOLO... {time_left:.1f}s restantes")

        # Intento de recuperación automática (solo YOLO)
        if tracking and tracking_lost and (time.time() - last_detection_time) <= recovery_timeout and not using_tracker and target_cls is not None:
            same_class_boxes = [b for b in boxes if b[4] == target_cls]
            if same_class_boxes:
                tx1, ty1, tx2, ty2 = target_box
                tcx, tcy = (tx1 + tx2) // 2, (ty1 + ty2) // 2

                closest_box = None
                min_dist = float('inf')

                for box in same_class_boxes:
                    x1, y1, x2, y2, cls, conf = box
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    dist = np.hypot(cx - tcx, cy - tcy)
                    if dist < min_dist:
                        min_dist = dist
                        closest_box = box

                if closest_box:
                    x1, y1, x2, y2, cls, conf = closest_box
                    target_box = (x1, y1, x2, y2)
                    tracking_lost = False
                    last_detection_time = time.time()
                    log_buffer.add(f"Objeto recuperado automáticamente: {model.names[cls]} (Confianza: {conf:.2f})")

        # ---------- Dibujo de detecciones si no hay tracking activo o está perdido ----------
        draw_frame = frame.copy()
        if (not tracking or tracking_lost) and auto_detection:
            for box in boxes:
                x1, y1, x2, y2, cls, conf = box
                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{model.names[cls]} {conf:.2f}"
                cv2.putText(draw_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # ---------- Dibujo de selección en progreso (si algún día activas 'selecting') ----------
        if selecting and selection_start and selection_end:
            cv2.rectangle(draw_frame, selection_start, selection_end, (255, 0, 0), 2)

        # ---------- Dibujo del objeto trackeado y zoom ----------
        if tracking and not tracking_lost and target_box:
            x1, y1, x2, y2 = target_box
            cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            label = "TRACKING: " + (f"{model.names[target_cls]}" if target_cls is not None else "Manual")
            cv2.putText(draw_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            zoom = frame[y1:y2, x1:x2]
            if zoom.size > 0:
                h_zoom, w_zoom = zoom.shape[:2]
                aspect_ratio = w_zoom / h_zoom if h_zoom != 0 else 1.0
                if aspect_ratio > 1:
                    new_w = zoom_window_size[0]
                    new_h = int(new_w / max(aspect_ratio, 1e-6))
                else:
                    new_h = zoom_window_size[1]
                    new_w = int(new_h * aspect_ratio)
                if new_w > 0 and new_h > 0:
                    zoom = cv2.resize(zoom, (new_w, new_h))
                    z_rgb = cv2.cvtColor(zoom, cv2.COLOR_BGR2RGB)
                    z_h, z_w, z_ch = z_rgb.shape
                    z_qimg = QtGui.QImage(z_rgb.data, z_w, z_h, z_ch * z_w, QtGui.QImage.Format.Format_RGB888)
                    self.zoom_label.setPixmap(QtGui.QPixmap.fromImage(z_qimg))
        else:
            # Si no hay tracking activo, limpiamos zoom
            self.zoom_label.clear()
            self.zoom_label.setText("Sin zoom")

        # ---------- Estado / textos como en tu panel ----------
        if tracking and not tracking_lost:
            status_text = "TRACKING ACTIVO"
        elif tracking_lost:
            status_text = "OBJETO PERDIDO"
        else:
            status_text = "SELECCIONA OBJETO"

        mode_text = f"MODO: {'MANUAL' if manual_selection else 'AUTOMATICO'}"
        self.lbl_status.setText(f"Estado: {status_text}")
        self.lbl_mode.setText(mode_text)
        self.lbl_fps.setText(f"FPS: {fps:.1f}")

        # Lista de detecciones
        self.list_dets.clear()
        for (x1, y1, x2, y2, cls, conf) in boxes:
            self.list_dets.addItem(f"{model.names[cls]} — {conf:.2f}  [{x1},{y1},{x2},{y2}]")

        # Mostrar frame en el widget de vídeo
        self.video.set_frame(draw_frame)

    def update_state_labels(self):
        mode_text = f"MODO: {'MANUAL' if manual_selection else 'AUTOMATICO'}"
        self.lbl_mode.setText(mode_text)
        if tracking and not tracking_lost:
            self.lbl_status.setText("Estado: TRACKING ACTIVO")
        elif tracking_lost:
            self.lbl_status.setText("Estado: OBJETO PERDIDO")
        else:
            self.lbl_status.setText("Estado: SELECCIONA OBJETO")


# ================== MAIN ==================
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
