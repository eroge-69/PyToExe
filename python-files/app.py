#!/usr/bin/env python3
# GYM ONCE — Acceso (v1.1)
import sys, os, sqlite3, datetime
from PyQt5 import QtCore, QtGui, QtWidgets

APP_TITLE_BASE = "GYM ONCE — Acceso"
DB_PATH = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GYM_ONCE", "usuarios.db")
ICON_PNG = "oncelio.png"
ICON_ICO = "oncelio.ico"
SPLASH_MS = 5000

def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        dni TEXT UNIQUE NOT NULL,
        telefono TEXT,
        tipo_membresia TEXT,
        fecha_inicio TEXT,
        fecha_vencimiento TEXT,
        fecha_registro TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS accesos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        timestamp TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    conn.commit()
    conn.close()

class Splash(QtWidgets.QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.95)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE_BASE + " | " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        if os.path.exists(ICON_ICO):
            self.setWindowIcon(QtGui.QIcon(ICON_ICO))
        elif os.path.exists(ICON_PNG):
            self.setWindowIcon(QtGui.QIcon(ICON_PNG))
        self.resize(1200,700)
        # load stylesheet if exists
        qss_path = os.path.join("resources","ui_dark.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        self.setup_ui()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_clock_title)
        self.timer.start(1000)

    def update_clock_title(self):
        self.setWindowTitle(APP_TITLE_BASE + " | " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)

        # sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(180)
        sb_layout = QtWidgets.QVBoxLayout(sidebar)
        logo_lbl = QtWidgets.QLabel()
        if os.path.exists(ICON_PNG):
            pix = QtGui.QPixmap(ICON_PNG).scaled(72,72, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        sb_layout.addWidget(logo_lbl, alignment=QtCore.Qt.AlignHCenter)
        sb_layout.addSpacing(10)
        btn_users = QtWidgets.QPushButton("🧍 Usuarios")
        btn_records = QtWidgets.QPushButton("📊 Registros")
        btn_conf = QtWidgets.QPushButton("⚙️ Configuración")
        btn_exit = QtWidgets.QPushButton("Salir")
        btn_exit.clicked.connect(self.close_with_confirm)
        for b in (btn_users, btn_records, btn_conf, btn_exit):
            b.setMinimumHeight(44)
            sb_layout.addWidget(b)
        sb_layout.addStretch()

        # main area
        area = QtWidgets.QFrame()
        area_layout = QtWidgets.QVBoxLayout(area)
        # top controls
        top_h = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit(); self.search_input.setPlaceholderText("Buscar por nombre o DNI...")
        btn_search = QtWidgets.QPushButton("Buscar"); btn_search.clicked.connect(self.on_search)
        btn_register = QtWidgets.QPushButton("Registrar acceso") ; btn_register.clicked.connect(self.on_register_access)
        area_layout.addLayout(top_h)
        top_h.addWidget(self.search_input); top_h.addWidget(btn_search); top_h.addWidget(btn_register)
        # table
        self.table = QtWidgets.QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(["ID","Nombre","DNI","Teléfono","Membresía","Inicio","Vencimiento","Estado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        area_layout.addWidget(self.table)
        # bottom buttons
        btn_h = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("➕ Agregar"); btn_add.clicked.connect(self.add_user_dialog)
        btn_edit = QtWidgets.QPushButton("✏️ Editar"); btn_edit.clicked.connect(self.edit_user_dialog)
        btn_del = QtWidgets.QPushButton("❌ Eliminar"); btn_del.clicked.connect(self.delete_user)
        btn_export = QtWidgets.QPushButton("📤 Exportar Excel"); btn_export.clicked.connect(self.export_excel)
        btn_h.addWidget(btn_add); btn_h.addWidget(btn_edit); btn_h.addWidget(btn_del); btn_h.addStretch(); btn_h.addWidget(btn_export)
        area_layout.addLayout(btn_h)

        main_layout.addWidget(sidebar); main_layout.addWidget(area)
        self.load_users()

    def load_users(self, term=""):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if term:
            q = f"%{term}%"
            cur.execute("SELECT id,nombre,dni,telefono,tipo_membresia,fecha_inicio,fecha_vencimiento FROM usuarios WHERE nombre LIKE ? OR dni LIKE ? ORDER BY nombre", (q,q))
        else:
            cur.execute("SELECT id,nombre,dni,telefono,tipo_membresia,fecha_inicio,fecha_vencimiento FROM usuarios ORDER BY nombre")
        rows = cur.fetchall()
        self.table.setRowCount(0)
        for r in rows:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            uid, nombre, dni, tel, mem, inicio, venc = r
            estado = "Activo"
            try:
                venc_date = datetime.datetime.strptime(venc, "%Y-%m-%d").date()
                if venc_date < datetime.date.today():
                    estado = "Vencido"
            except Exception:
                estado = "Desconocido"
            vals = [str(uid), nombre, dni, tel or "", mem or "", inicio or "", venc or "", estado]
            for i, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                if i==7:
                    if v=="Activo":
                        item.setBackground(QtGui.QColor("#2e7d32"))
                    elif v=="Vencido":
                        item.setBackground(QtGui.QColor("#c62828"))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row_pos, i, item)
        conn.close()

    def on_search(self):
        term = self.search_input.text().strip()
        self.load_users(term)

    def add_user_dialog(self):
        dlg = UserDialog(parent=self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("INSERT INTO usuarios (nombre,dni,telefono,tipo_membresia,fecha_inicio,fecha_vencimiento,fecha_registro) VALUES (?,?,?,?,?,?,?)",
                        (data['nombre'], data['dni'], data['telefono'], data['membresia'], data['inicio'], data['vencimiento'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit(); conn.close()
            self.load_users()

    def edit_user_dialog(self):
        sel = self.table.selectedItems()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Atención", "Selecciona un usuario para editar.")
            return
        user_id = int(sel[0].text())
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("SELECT nombre,dni,telefono,tipo_membresia,fecha_inicio,fecha_vencimiento FROM usuarios WHERE id=?", (user_id,))
        row = cur.fetchone(); conn.close()
        if not row: return
        dlg = UserDialog(parent=self, data={'nombre':row[0],'dni':row[1],'telefono':row[2],'membresia':row[3],'inicio':row[4],'vencimiento':row[5]})
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("UPDATE usuarios SET nombre=?,dni=?,telefono=?,tipo_membresia=?,fecha_inicio=?,fecha_vencimiento=? WHERE id=?",
                        (data['nombre'], data['dni'], data['telefono'], data['membresia'], data['inicio'], data['vencimiento'], user_id))
            conn.commit(); conn.close()
            self.load_users()

    def delete_user(self):
        sel = self.table.selectedItems()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Atención", "Selecciona un usuario para eliminar.")
            return
        user_id = int(sel[0].text())
        ans = QtWidgets.QMessageBox.question(self, "Confirmar", "¿Eliminar usuario?")
        if ans == QtWidgets.QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            conn.commit(); conn.close()
            self.load_users()

    def on_register_access(self):
        sel = self.table.selectedItems()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Atención", "Selecciona un usuario para registrar acceso.")
            return
        user_id = int(sel[0].text())
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("INSERT INTO accesos (usuario_id,timestamp) VALUES (?,?)", (user_id, now))
        conn.commit(); conn.close()
        QtWidgets.QMessageBox.information(self, "Acceso", "Acceso registrado.")
        self.load_users()

    def export_excel(self):
        try:
            import pandas as pd
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT u.id,u.nombre,u.dni,u.telefono,u.tipo_membresia,u.fecha_inicio,u.fecha_vencimiento,a.timestamp FROM usuarios u LEFT JOIN accesos a ON u.id=a.usuario_id ORDER BY a.timestamp DESC", conn)
            conn.close()
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            fname = f"registros_gym_{datetime.date.today().isoformat()}.xlsx"
            out_path = os.path.join(desktop, fname)
            df.to_excel(out_path, index=False)
            QtWidgets.QMessageBox.information(self, "Exportado", f"Exportado a:\n{out_path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def close_with_confirm(self):
        ans = QtWidgets.QMessageBox.question(self, "Salir", "¿Desea salir de GYM ONCE?")
        if ans == QtWidgets.QMessageBox.Yes:
            QtWidgets.qApp.quit()

class UserDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Usuario")
        self.setModal(True)
        layout = QtWidgets.QFormLayout(self)
        self.name = QtWidgets.QLineEdit(); self.dni = QtWidgets.QLineEdit(); self.phone = QtWidgets.QLineEdit()
        self.mem = QtWidgets.QLineEdit(); self.start = QtWidgets.QDateEdit(); self.end = QtWidgets.QDateEdit()
        self.start.setCalendarPopup(True); self.end.setCalendarPopup(True)
        if data:
            self.name.setText(data.get('nombre','')); self.dni.setText(data.get('dni','')); self.phone.setText(data.get('telefono',''))
            self.mem.setText(data.get('membresia','')); 
            try:
                self.start.setDate(QtCore.QDate.fromString(data.get('inicio',''), "yyyy-MM-dd"))
                self.end.setDate(QtCore.QDate.fromString(data.get('vencimiento',''), "yyyy-MM-dd"))
            except Exception:
                pass
        else:
            self.start.setDate(QtCore.QDate.currentDate())
            self.end.setDate(QtCore.QDate.currentDate().addDays(30))
        layout.addRow("Nombre:", self.name); layout.addRow("DNI:", self.dni); layout.addRow("Teléfono:", self.phone)
        layout.addRow("Membresía:", self.mem); layout.addRow("Inicio:", self.start); layout.addRow("Vencimiento:", self.end)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def get_data(self):
        return {
            'nombre': self.name.text().strip(),
            'dni': self.dni.text().strip(),
            'telefono': self.phone.text().strip(),
            'membresia': self.mem.text().strip(),
            'inicio': self.start.date().toString("yyyy-MM-dd"),
            'vencimiento': self.end.date().toString("yyyy-MM-dd")
        }

def main():
    ensure_db()
    app = QtWidgets.QApplication(sys.argv)
    # splash
    if os.path.exists(ICON_PNG):
        pix = QtGui.QPixmap(ICON_PNG).scaled(360,360, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        splash = Splash(pix)
        splash.show()
        QtCore.QTimer.singleShot(SPLASH_MS, splash.close)
        while splash.isVisible():
            app.processEvents()
            QtCore.QThread.msleep(50)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
