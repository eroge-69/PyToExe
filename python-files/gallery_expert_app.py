#!/usr/bin/env python3
# gallery_expert_advanced_full.py
# Gelişmiş Galeri Ekspertiz - PyQt5 (tek dosya, tüm marker state seçenekleri)

import sys, os, json, sqlite3
from datetime import datetime
from io import BytesIO

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QLineEdit, QFormLayout, QDialog, QTextEdit, QDateEdit,
    QSpinBox, QFileDialog, QMessageBox, QSplitter, QListWidgetItem, QComboBox
)

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

DB_FILE = 'vehicles_advanced.db'

# Marker state constants
STATE_NONE = 0
STATE_BOYA = 1
STATE_LOKAL = 2
STATE_DEGISEN = 3
STATE_ORIJINAL = 4

STATE_COLORS = {
    STATE_BOYA: QColor(50, 120, 220, 200),     # mavi
    STATE_LOKAL: QColor(240, 200, 50, 200),    # sarı
    STATE_DEGISEN: QColor(220, 40, 40, 200),   # kırmızı
    STATE_ORIJINAL: QColor(80, 200, 120, 200), # yeşil
    STATE_NONE: QColor(120, 120, 120, 120)
}

STATE_LABEL = {
    STATE_BOYA: 'Boya',
    STATE_LOKAL: 'Lokal',
    STATE_DEGISEN: 'Değişen',
    STATE_ORIJINAL: 'Orijinal',
    STATE_NONE: 'Belirtilmedi'
}

class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self._create()

    def _create(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY,
                plate TEXT UNIQUE,
                chassis TEXT,
                model TEXT,
                km INTEGER,
                color TEXT,
                notes TEXT,
                inspection_date TEXT,
                image_path TEXT,
                markers_json TEXT
            )
        ''')
        self.conn.commit()

    def add_vehicle(self, data):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO vehicles (plate,chassis,model,km,color,notes,inspection_date,image_path,markers_json)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (data.get('plate'), data.get('chassis'), data.get('model'), data.get('km'),
              data.get('color'), data.get('notes'), data.get('inspection_date'),
              data.get('image_path'), data.get('markers_json')))
        self.conn.commit()
        return c.lastrowid

    def update_vehicle(self, vid, data):
        c = self.conn.cursor()
        c.execute('''
            UPDATE vehicles SET plate=?,chassis=?,model=?,km=?,color=?,notes=?,inspection_date=?,image_path=?,markers_json=? WHERE id=?
        ''', (data.get('plate'), data.get('chassis'), data.get('model'), data.get('km'),
              data.get('color'), data.get('notes'), data.get('inspection_date'),
              data.get('image_path'), data.get('markers_json'), vid))
        self.conn.commit()

    def delete_vehicle(self, vid):
        c = self.conn.cursor()
        c.execute('DELETE FROM vehicles WHERE id=?', (vid,))
        self.conn.commit()

    def list_vehicles(self):
        c = self.conn.cursor()
        c.execute('SELECT id, plate, model FROM vehicles ORDER BY id DESC')
        return c.fetchall()

    def get_vehicle(self, vid):
        c = self.conn.cursor()
        c.execute('SELECT * FROM vehicles WHERE id=?', (vid,))
        row = c.fetchone()
        if not row:
            return None
        cols = [x[0] for x in c.description]
        return dict(zip(cols, row))

class VehicleDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Araç Bilgileri")
        self.resize(420, 380)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.plate = QLineEdit(); form.addRow("Plaka:", self.plate)
        self.chassis = QLineEdit(); form.addRow("Şasi No:", self.chassis)
        self.model = QLineEdit(); form.addRow("Model:", self.model)
        self.km = QSpinBox(); self.km.setMaximum(2000000); form.addRow("KM:", self.km)
        self.color = QLineEdit(); form.addRow("Renk:", self.color)
        self.inspection = QDateEdit(); self.inspection.setCalendarPopup(True); form.addRow("Muayene T.:", self.inspection)
        self.image_path = QLineEdit(); form.addRow("Görsel Dosyası:", self.image_path)
        self.btn_browse = QPushButton("Gözat"); self.btn_browse.clicked.connect(self.browse_image)
        form.addRow("", self.btn_browse)
        self.notes = QTextEdit(); form.addRow("Notlar:", self.notes)

        layout.addLayout(form)
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Kaydet"); self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("İptal"); self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_save); btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        if data:
            self.plate.setText(data.get('plate') or '')
            self.chassis.setText(data.get('chassis') or '')
            self.model.setText(data.get('model') or '')
            self.km.setValue(int(data.get('km') or 0))
            self.color.setText(data.get('color') or '')
            if data.get('inspection_date'):
                try:
                    d = datetime.fromisoformat(data.get('inspection_date')).date()
                    self.inspection.setDate(d)
                except Exception:
                    pass
            self.image_path.setText(data.get('image_path') or '')
            self.notes.setPlainText(data.get('notes') or '')

    def browse_image(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Images (*.png *.jpg *.jpeg)")
        if fn:
            self.image_path.setText(fn)

    def get_data(self):
        insp = self.inspection.date().toPyDate()
        return {
            'plate': self.plate.text().strip(),
            'chassis': self.chassis.text().strip(),
            'model': self.model.text().strip(),
            'km': self.km.value(),
            'color': self.color.text().strip(),
            'inspection_date': insp.isoformat(),
            'image_path': self.image_path.text().strip(),
            'notes': self.notes.toPlainText(),
            'markers_json': json.dumps([])
        }

class ExpertCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = None  # QPixmap
        self.markers = []       # [{'x':0..1,'y':0..1,'state':int}]
        self.selected_index = None
        self.dragging = False
        self.drag_offset = (0, 0)
        self.setMinimumSize(640, 360)
        self.setMouseTracking(True)

    def load_background(self, path=None):
        if path and os.path.exists(path):
            self.background = QPixmap(path)
        else:
            w, h = 800, 400
            img = QImage(w, h, QImage.Format_ARGB32)
            img.fill(QColor(245,245,245))
            p = QPainter(img)
            p.setBrush(QBrush(QColor(220,220,220)))
            p.drawRoundedRect(QRectF(w*0.08, h*0.25, w*0.84, h*0.45), 20, 20)
            p.end()
            self.background = QPixmap.fromImage(img)
        self.update()

    def load_markers_json(self, mj):
        try:
            self.markers = json.loads(mj) if mj else []
        except Exception:
            self.markers = []
        self.update()

    def markers_to_json(self):
        return json.dumps(self.markers)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self.background:
            pix = self.background.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px = (w - pix.width())//2
            py = (h - pix.height())//2
            p.drawPixmap(px, py, pix)
            self._img_origin = (px, py)
            self._img_size = (pix.width(), pix.height())
        else:
            p.fillRect(0,0,w,h, QColor(245,245,245))
            self._img_origin = (0,0)
            self._img_size = (w,h)
        for idx, m in enumerate(self.markers):
            mx = self._img_origin[0] + m['x'] * self._img_size[0]
            my = self._img_origin[1] + m['y'] * self._img_size[1]
            state = m.get('state', STATE_NONE)
            color = STATE_COLORS.get(state, STATE_COLORS[STATE_NONE])
            p.setBrush(QBrush(color))
            p.setPen(QPen(QColor(30,30,30)))
            r = 10
            p.drawEllipse(QPointF(mx, my), r, r)
            if idx == self.selected_index:
                p.setPen(QPen(QColor(0,0,0),2, Qt.DashLine))
                p.drawEllipse(QPointF(mx, my), r+6, r+6)

    def _hit_test(self, x, y):
        for idx, m in enumerate(self.markers):
            mx = self._img_origin[0] + m['x'] * self._img_size[0]
            my = self._img_origin[1] + m['y'] * self._img_size[1]
            if (mx - x)**2 + (my - y)**2 <= (14**2):
                return idx
        return None

    def mousePressEvent(self, ev):
        x, y = ev.x(), ev.y()
        idx = self._hit_test(x,y)
        if ev.button() == Qt.LeftButton:
            if idx is not None:
                self.selected_index = idx
                mx = self._img_origin[0] + self.markers[idx]['x'] * self._img_size[0]
                my = self._img_origin[1] + self.markers[idx]['y'] * self._img_size[1]
                self.dragging = True
                self.drag_offset = (x - mx, y - my)
            else:
                ox, oy = self._img_origin
                iw, ih = self._img_size
                if ox <= x <= ox+iw and oy <= y <= oy+ih:
                    nx = (x - ox) / iw
                    ny = (y - oy) / ih
                    sel_text = "Boyalı"
                    if self.parent() and hasattr(self.parent(), "state_selector"):
                        sel_text = self.parent().state_selector.currentText()
                    state_map = {
                        "Boyalı": STATE_BOYA,
                        "Lokal Boya": STATE_LOKAL,
                        "Değişen": STATE_DEGISEN,
                        "Orijinal": STATE_ORIJINAL
                    }
                    state = state_map.get(sel_text, STATE_BOYA)
                    self.markers.append({'x': nx, 'y': ny, 'state': state})
                    self.selected_index = len(self.markers) - 1
            self.update()
        elif ev.button() == Qt.RightButton:
            if idx is not None:
                cur = self.markers[idx].get('state', STATE_NONE)
                order = [STATE_BOYA, STATE_LOKAL, STATE_DEGISEN, STATE_ORIJINAL, STATE_NONE]
                try:
                    ni = (order.index(cur) + 1) % len(order)
                except ValueError:
                    ni = 0
                self.markers[idx]['state'] = order[ni]
                self.selected_index = idx
                self.update()

    def mouseMoveEvent(self, ev):
        if self.dragging and self.selected_index is not None:
            x, y = ev.x(), ev.y()
            ox, oy = self._img_origin
            iw, ih = self._img_size
            mx = x - self.drag_offset[0]
            my = y - self.drag_offset[1]
            mx = max(ox, min(ox+iw, mx))
            my = max(oy, min(oy+ih, my))
            nx = (mx - ox) / iw
            ny = (my - oy) / ih
            self.markers[self.selected_index]['x'] = nx
            self.markers[self.selected_index]['y'] = ny
            self.update()

    def mouseReleaseEvent(self, ev):
        self.dragging = False

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Delete and self.selected_index is not None:
            self.markers.pop(self.selected_index)
            self.selected_index = None
            self.update()

    def export_image(self, path):
        img = QImage(self.size(), QImage.Format_ARGB32)
        painter = QPainter(img)
        self.render(painter)
        painter.end()
        img.save(path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("Galeri Ekspertiz - Gelişmiş")
        self.resize(1200, 700)

        splitter = QSplitter()
        left = QWidget(); left_layout = QVBoxLayout(left)
        right = QWidget(); right_layout = QVBoxLayout(right)

        self.listw = QListWidget()
        left_layout.addWidget(QLabel("Kayıtlı Araçlar"))
        left_layout.addWidget(self.listw)
        btns_row = QHBoxLayout()
        self.btn_new = QPushButton("Yeni")
        self.btn_edit = QPushButton("Düzenle")
        self.btn_del = QPushButton("Sil")
        btns_row.addWidget(self.btn_new); btns_row.addWidget(self.btn_edit); btns_row.addWidget(self.btn_del)
        left_layout.addLayout(btns_row)
        left_layout.addStretch()

        self.canvas = ExpertCanvas()
        right_layout.addWidget(self.canvas)

        controls = QHBoxLayout()
        self.btn_load_image = QPushButton("Fotoğraf Yükle")
        self.btn_clear = QPushButton("Temizle")
        self.btn_save_markers = QPushButton("Mark. Kaydet")
        self.btn_export_pdf = QPushButton("PDF Dışa Aktar")
        controls.addWidget(self.btn_load_image); controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_save_markers); controls.addWidget(self.btn_export_pdf)

        # --- EKLENDİ: Marker state combobox ---
        self.state_selector = QComboBox()
        self.state_selector.addItems(["Boyalı","Lokal Boya","Değişen","Orijinal"])
        controls.addWidget(QLabel("Yeni Marker:"))
        controls.addWidget(self.state_selector)

        right_layout.addLayout(controls)

        self.info_label = QLabel("Seçili: -")
        right_layout.addWidget(self.info_label)
        self.legend_label = QLabel(self._legend_text())
        self.legend_label.setWordWrap(True)
        right_layout.addWidget(self.legend_label)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([300, 900])
        self.setCentralWidget(splitter)

        self.btn_new.clicked.connect(self.new_vehicle)
        self.btn_edit.clicked.connect(self.edit_vehicle)
        self.btn_del.clicked.connect(self.delete_vehicle)
        self.listw.currentItemChanged.connect(self.on_selection_changed)
        self.btn_load_image.clicked.connect(self.load_image)
        self.btn_clear.clicked.connect(self.clear_markers)
        self.btn_save_markers.clicked.connect(self.save_markers)
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self._load_list()
        self.canvas.mouseReleaseEvent = self._wrap_mouse_release(self.canvas.mouseReleaseEvent)
        self.canvas.mousePressEvent = self._wrap_mouse_press(self.canvas.mousePressEvent)

    def _legend_text(self):
        t = "<b>Hasar Tanımları:</b><br>"
        for k in [STATE_BOYA, STATE_LOKAL, STATE_DEGISEN, STATE_ORIJINAL]:
            t += f"{STATE_LABEL[k]} : <span style='color: rgb({STATE_COLORS[k].red()},{STATE_COLORS[k].green()},{STATE_COLORS[k].blue()})'>&#9632;</span> &nbsp;&nbsp;"
        return t

    def _wrap_mouse_release(self, fn):
        def inner(ev):
            fn(ev)
            self._update_info()
        return inner

    def _wrap_mouse_press(self, fn):
        def inner(ev):
            fn(ev)
            self._update_info()
        return inner

    def _update_info(self):
        idx = self.canvas.selected_index
        if idx is None:
            self.info_label.setText("Seçili: -")
        else:
            s = self.canvas.markers[idx].get('state', STATE_NONE)
            self.info_label.setText(f"Seçili: #{idx+1} - {STATE_LABEL.get(s,'-')}")

        counts = {STATE_BOYA:0, STATE_LOKAL:0, STATE_DEGISEN:0, STATE_ORIJINAL:0}
        for m in self.canvas.markers:
            st = m.get('state', STATE_NONE)
            if st in counts:
                counts[st] += 1
        summary = " | ".join([f"{STATE_LABEL[k]}: {counts[k]}" for k in counts])
        self.legend_label.setText(self._legend_text() + "<br><b>Sayac:</b> " + summary)

    def _load_list(self):
        self.listw.clear()
        for v in self.db.list_vehicles():
            item = QListWidgetItem(f"{v[1]} - {v[2]}")
            item.setData(Qt.UserRole, v[0])
            self.listw.addItem(item)

    def on_selection_changed(self, cur, prev):
        if not cur:
            return
        vid = cur.data(Qt.UserRole)
        data = self.db.get_vehicle(vid)
        self.canvas.load_background(data.get('image_path'))
        self.canvas.load_markers_json(data.get('markers_json'))

    def new_vehicle(self):
        dlg = VehicleDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            vid = self.db.add_vehicle(data)
            self._load_list()

    def edit_vehicle(self):
        cur = self.listw.currentItem()
        if not cur: return
        vid = cur.data(Qt.UserRole)
        data = self.db.get_vehicle(vid)
        dlg = VehicleDialog(self, data)
        if dlg.exec():
            new_data = dlg.get_data()
            new_data['markers_json'] = data.get('markers_json', json.dumps([]))
            self.db.update_vehicle(vid, new_data)
            self._load_list()

    def delete_vehicle(self):
        cur = self.listw.currentItem()
        if not cur: return
        if QMessageBox.question(self, "Sil?", "Araç silinsin mi?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            vid = cur.data(Qt.UserRole)
            self.db.delete_vehicle(vid)
            self._load_list()
            self.canvas.load_background(None)
            self.canvas.markers = []
            self.canvas.update()

    def load_image(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Images (*.png *.jpg *.jpeg)")
        if fn:
            self.canvas.load_background(fn)

    def clear_markers(self):
        self.canvas.markers = []
        self.canvas.update()
        self._update_info()

    def save_markers(self):
        cur = self.listw.currentItem()
        if not cur: return
        vid = cur.data(Qt.UserRole)
        data = self.db.get_vehicle(vid)
        data['markers_json'] = self.canvas.markers_to_json()
        self.db.update_vehicle(vid, data)
        QMessageBox.information(self, "Kaydedildi", "Marker bilgileri kaydedildi.")

    def export_pdf(self):
        cur = self.listw.currentItem()
        if not cur: return
        vid = cur.data(Qt.UserRole)
        data = self.db.get_vehicle(vid)
        if not data.get('image_path'):
            QMessageBox.warning(self, "Uyarı", "Araç görseli yok!")
            return
        fn, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", f"{data.get('plate')}.pdf", "PDF Files (*.pdf)")
        if not fn: return

        img_io = BytesIO()
        self.canvas.export_image(img_io)
        img_io.seek(0)
        pdf = canvas.Canvas(fn, pagesize=A4)
        w, h = A4
        pdf.drawString(50, h-50, f"Plaka: {data.get('plate')}")
        pdf.drawString(50, h-70, f"Model: {data.get('model')}")
        pdf.drawString(50, h-90, f"KM: {data.get('km')}")
        pdf.drawString(50, h-110, f"Renk: {data.get('color')}")
        pdf.drawImage(ImageReader(Image.open(img_io)), 50, h-400, width=500, height=300)
        pdf.save()
        QMessageBox.information(self, "PDF Kaydedildi", "PDF başarıyla kaydedildi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
