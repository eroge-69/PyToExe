import sys
import bcrypt
import mysql.connector
import requests
import re
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QComboBox, QStackedWidget, QTableWidget, QTableWidgetItem, QFormLayout, 
                             QHBoxLayout, QTabWidget, QGroupBox, QFrame, QSizePolicy, QHeaderView, 
                             QGraphicsDropShadowEffect, QDialog, QDialogButtonBox, QTextEdit, QInputDialog,
                             QScrollArea, QScrollBar, QAbstractItemView, QDateEdit, QListWidget,
                             QListWidgetItem, QGridLayout, QStatusBar, QCheckBox, QFileDialog)
from PyQt6.QtGui import (QColor, QFont, QIcon, QPixmap, QPalette, QLinearGradient, QBrush, 
                         QPainter, QPainterPath, QFontDatabase, QMovie)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QDate, QTimer, QPoint

# --------------------- Configuración ---------------------
DB_CONFIG = {
    'host': '34.176.38.245',
    'user': 'root',
    'password': '0]4~H|->]Dx$f6:a',
    'database': 'bedsense_db'
}

API_URL = "https://api.apis.net.pe/v1/dni?numero="
API_TOKEN = "TU_TOKEN_AQUI"  # Reemplazar con token válido

# --------------------- Estilos Globales ---------------------
def aplicar_estilos(app):
    # Cargar fuentes personalizadas
    try:
        QFontDatabase.addApplicationFont("fonts/Montserrat-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Montserrat-SemiBold.ttf")
    except:
        pass
    
    estilo = """
    /* ---------- ESTILOS GLOBALES ---------- */
    * {
        font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
        outline: none;
    }
    
    QWidget {
        background-color: #f8fafc;
        color: #334155;
    }
    
    /* ---------- TÍTULOS Y TEXTOS ---------- */
    QLabel#tituloPrincipal {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    
    QLabel#subtitulo {
        font-size: 16px;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 15px;
    }
    
    QLabel#etiquetaSeccion {
        font-size: 18px;
        font-weight: 600;
        color: #0f172a;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 15px;
    }
    
    /* ---------- ENTRADAS DE TEXTO ---------- */
    QLineEdit, QComboBox, QDateEdit {
        background-color: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 15px;
        color: #0f172a;
        min-height: 44px;
        selection-background-color: #dbeafe;
    }
    
    QLineEdit:focus, QComboBox:focus, QLineEdit:hover, QComboBox:hover, 
    QDateEdit:focus, QDateEdit:hover {
        border: 2px solid #3b82f6;
    }
    
    QLineEdit[error="true"] {
        border: 2px solid #ef4444;
    }
    
    QTextEdit {
        background-color: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        font-size: 15px;
        color: #0f172a;
    }
    
    /* ---------- BOTONES ---------- */
    QPushButton {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-size: 15px;
        font-weight: 600;
        min-height: 44px;
        transition: background-color 0.3s ease, transform 0.1s ease;
    }
    
    QPushButton:hover {
        background-color: #2563eb;
    }
    
    QPushButton:pressed {
        background-color: #1d4ed8;
        transform: scale(0.98);
    }
    
    QPushButton#botonPrimario {
        background-color: #3b82f6;
        color: white;
    }
    
    QPushButton#botonPrimario:hover {
        background-color: #2563eb;
    }
    
    QPushButton#botonSecundario {
        background-color: #64748b;
        color: white;
    }
    
    QPushButton#botonSecundario:hover {
        background-color: #475569;
    }
    
    QPushButton#botonExito {
        background-color: #10b981;
        color: white;
    }
    
    QPushButton#botonExito:hover {
        background-color: #059669;
    }
    
    QPushButton#botonPeligro {
        background-color: #ef4444;
        color: white;
    }
    
    QPushButton#botonPeligro:hover {
        background-color: #dc2626;
    }
    
    QPushButton[icon] {
        padding-left: 15px;
        padding-right: 15px;
    }
    
    /* ---------- PESTAÑAS ---------- */
    QTabWidget::pane {
        border: none;
        border-radius: 12px;
        background: white;
        margin-top: 10px;
    }
    
    QTabBar::tab {
        background: #f1f5f9;
        color: #64748b;
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        font-weight: 600;
        font-size: 14px;
    }
    
    QTabBar::tab:selected {
        background: white;
        color: #3b82f6;
        border-bottom: 3px solid #3b82f6;
    }
    
    QTabBar::tab:hover {
        background: #e2e8f0;
        color: #3b82f6;
    }
    
    /* ---------- GRUPOS Y CONTENEDORES ---------- */
    QGroupBox {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-top: 20px;
        padding-top: 30px;
        font-weight: bold;
        font-size: 16px;
        color: #0f172a;
        background: white;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        background-color: white;
    }
    
    #contenedorSombra {
        background-color: white;
        border-radius: 16px;
    }
    
    /* ---------- TABLAS ---------- */
    QTableWidget {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        gridline-color: #f1f5f9;
        font-size: 14px;
        selection-background-color: #dbeafe;
        selection-color: #1e40af;
        alternate-background-color: #f8fafc;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        color: #334155;
        padding: 14px;
        font-weight: 600;
        border: none;
        border-bottom: 2px solid #e2e8f0;
    }
    
    QTableCornerButton::section {
        background-color: #f8fafc;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
    }
    
    QScrollBar:vertical {
        border: none;
        background: #f8fafc;
        width: 10px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        border-radius: 5px;
        min-height: 20px;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    
    /* ---------- BARRA DE NAVEGACIÓN ---------- */
    #barraNavegacion {
        background-color: white;
        border-bottom: 1px solid #e2e8f0;
        padding: 0 20px;
        border-radius: 0;
    }
    
    #botonNavegacion {
        background-color: transparent;
        color: #64748b;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        text-align: center;
        min-width: 140px;
        font-size: 15px;
    }
    
    #botonNavegacion:hover {
        background-color: #f1f5f9;
        color: #3b82f6;
    }
    
    #botonNavegacion:checked {
        background-color: #dbeafe;
        color: #3b82f6;
    }
    
    #botonCerrarSesion {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }
    
    #botonCerrarSesion:hover {
        background-color: #e2e8f0;
        color: #3b82f6;
    }
    
    /* ---------- ESTADOS DE CAMAS ---------- */
    .cama-disponible {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
    }
    
    .cama-ocupada {
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
    }
    
    .cama-mantenimiento {
        background-color: #ffedd5;
        color: #c2410c;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
    }
    
    .cama-sucia {
        background-color: #fef3c7;
        color: #d97706;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
    }
    
    /* ---------- LOGIN ---------- */
    #contenedorLogin {
        background-color: white;
        border-radius: 20px;
        padding: 50px;
        min-width: 450px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    }
    
    #tituloLogin {
        color: #3b82f6;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 8px;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    #subtituloLogin {
        color: #64748b;
        font-size: 18px;
        margin-bottom: 40px;
        text-align: center;
    }
    
    /* ---------- ANIMACIONES ---------- */
    QPushButton#botonAnimado {
        transition: all 0.3s ease;
    }
    
    /* ---------- DIALOGOS ---------- */
    QDialog {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
    }
    
    QDialog QLabel {
        font-size: 15px;
        color: #334155;
        margin-bottom: 5px;
    }
    
    /* ---------- NOTIFICACIONES ---------- */
    .notificacion-contenedor {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .notificacion-titulo {
        font-weight: 700;
        font-size: 16px;
        color: #0f172a;
        margin-bottom: 5px;
    }
    
    .notificacion-contenido {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 10px;
    }
    
    .notificacion-fecha {
        font-size: 12px;
        color: #94a3b8;
        text-align: right;
    }
    
    /* ---------- ESTADO DE CAMAS EN TABLAS ---------- */
    .estado-disponible {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
        text-align: center;
    }
    
    .estado-ocupada {
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
        text-align: center;
    }
    
    .estado-mantenimiento {
        background-color: #ffedd5;
        color: #c2410c;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
        text-align: center;
    }
    
    .estado-sucio {
        background-color: #fef3c7;
        color: #d97706;
        font-weight: 600;
        border-radius: 6px;
        padding: 4px 8px;
        text-align: center;
    }
    
    /* ---------- SCROLL AREA ---------- */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:horizontal {
        height: 10px;
        background: #f8fafc;
    }
    
    QScrollBar::handle:horizontal {
        background: #cbd5e1;
        border-radius: 5px;
        min-width: 20px;
    }
    
    /* ---------- TARJETAS ---------- */
    .tarjeta {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
    }
    
    .tarjeta-titulo {
        font-size: 16px;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 10px;
    }
    
    .tarjeta-valor {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
    }
    
    .tarjeta-icono {
        font-size: 24px;
        width: 50px;
        height: 50px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    
    /* ---------- BUSCADOR ---------- */
    #contenedorBuscador {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 15px;
    }
    
    #buscadorInput {
        border: none;
        background: transparent;
        padding: 5px;
        font-size: 15px;
    }
    
    #buscadorInput:focus {
        outline: none;
    }
    
    /* ---------- LOADING ---------- */
    #loadingContainer {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 12px;        
    }

    /* Estilos para botones en tablas */
    QTableWidget QPushButton {
        padding: 5px 10px;
        font-size: 13px;
        min-height: 30px;
    } 
    QTableWidget QPushButton:hover {
        transform: scale(1.02);
    }
    """
    app.setStyleSheet(estilo)

# --------------------- Widget Circular para Avatar ---------------------
class AvatarWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(40, 40)
        self.radius = 20
        
    def setPixmap(self, pixmap):
        target = QPixmap(self.size())
        target.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.IgnoreAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        painter.end()
        
        super().setPixmap(target)

# --------------------- Animación de Carga ---------------------
class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setAutoFillBackground(False)
        
        container = QWidget(self)
        container.setObjectName("loadingContainer")
        container.setFixedSize(200, 200)
        container.move(parent.width()//2 - 100, parent.height()//2 - 100)
        
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.loading_label = QLabel()
        self.movie = QMovie("loading.gif")
        self.loading_label.setMovie(self.movie)
        self.movie.start()
        
        layout.addWidget(self.loading_label)
        
        self.hide()
        
    def showEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().showEvent(event)

# --------------------- Conexión ---------------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --------------------- Seguridad ---------------------
def sanitizar_input(texto):
    """Elimina caracteres potencialmente peligrosos"""
    return re.sub(r'[;\\\'"<>]', '', texto)[:100]

def hash_password(password):
    """Encripta la contraseña con bcrypt"""
    salt = bcrypt.gensalt(rounds=14)
    return bcrypt.hashpw(password.encode(), salt).decode()

# --------------------- Verificación ---------------------
def verificar_usuario(usuario, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, rol, nombre_completo FROM usuarios WHERE usuario = %s", (usuario,))
        row = cursor.fetchone()
        
        if row and bcrypt.checkpw(password.encode(), row[0].encode()):
            return row[1], row[2]  # Si la contraseña es correcta, retorna rol y nombre
        return None, None
    except Exception as e:
        print("Error de login:", e)
    return None, None

# --------------------- Login ---------------------
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BEDSENSE - Login")
        self.setWindowIcon(QIcon("hospital_icon.png"))
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Contenedor de login con sombra
        login_container = QWidget()
        login_container.setObjectName("contenedorLogin")
        
        # Aplicar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        login_container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(login_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo y título
        logo = QLabel()
        logo_pixmap = QPixmap("hospital_icon.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("BEDSENSE")
        title.setObjectName("tituloLogin")
        
        subtitle = QLabel("Sistema de Gestión Hospitalaria Inteligente")
        subtitle.setObjectName("subtituloLogin")
        
        # Campos de formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setContentsMargins(20, 0, 20, 0)
        
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Ingrese su usuario")
        self.usuario_input.setMinimumHeight(50)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        
        form_layout.addRow(QLabel("Usuario:"), self.usuario_input)
        form_layout.addRow(QLabel("Contraseña:"), self.password_input)
        
        # Botón de login
        login_btn = QPushButton("Ingresar al sistema")
        login_btn.setObjectName("botonPrimario")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.login)
        
        # Footer
        footer = QLabel("© 2025")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 30px;")
        
        # Añadir elementos al layout
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form_layout)
        layout.addWidget(login_btn)
        layout.addWidget(footer)
        
        main_layout.addWidget(login_container)
        self.setLayout(main_layout)
        
        # Fondo con gradiente
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(241, 245, 249))
        gradient.setColorAt(1, QColor(226, 232, 240))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

    def login(self):
        usuario = sanitizar_input(self.usuario_input.text())
        password = self.password_input.text()
        rol, nombre_completo = verificar_usuario(usuario, password)
        if rol:
            try:
                # Crear la ventana principal sin hacerla visible aún
                self.main = Principal(usuario, rol, nombre_completo)
                
                # Cerrar la ventana de login primero
                self.hide()
                
                # Ahora mostrar la ventana principal
                self.main.show()
                self.main.activateWindow()
                self.main.raise_()
                
                # Liberar recursos de la ventana de login
                self.deleteLater()
            except Exception as e:
                # Si hay error, mostrar nuevamente el login
                self.show()
                QMessageBox.critical(self, "Error", f"No se pudo abrir la aplicación: {str(e)}")
        else:
            # Animación de error
            anim = QPropertyAnimation(self.usuario_input, b"geometry")
            anim.setDuration(200)
            anim.setKeyValueAt(0, QRect(self.usuario_input.x(), self.usuario_input.y(), 
                                       self.usuario_input.width(), self.usuario_input.height()))
            anim.setKeyValueAt(0.25, QRect(self.usuario_input.x()-5, self.usuario_input.y(), 
                                          self.usuario_input.width(), self.usuario_input.height()))
            anim.setKeyValueAt(0.5, QRect(self.usuario_input.x()+5, self.usuario_input.y(), 
                                          self.usuario_input.width(), self.usuario_input.height()))
            anim.setKeyValueAt(0.75, QRect(self.usuario_input.x()-5, self.usuario_input.y(), 
                                          self.usuario_input.width(), self.usuario_input.height()))
            anim.setKeyValueAt(1, QRect(self.usuario_input.x(), self.usuario_input.y(), 
                                       self.usuario_input.width(), self.usuario_input.height()))
            anim.start()
            
            self.usuario_input.setStyleSheet("border: 2px solid #ef4444;")
            self.password_input.setStyleSheet("border: 2px solid #ef4444;")
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")

# --------------------- Ventana Principal ---------------------
class Principal(QMainWindow):
    def __init__(self, usuario, rol, nombre_completo):
        super().__init__()
        self.setWindowTitle(f"BEDSENSE - {usuario} ({rol})")
        self.setWindowIcon(QIcon("hospital_icon.png"))
        self.resize(1400, 850)
        self.usuario = usuario
        self.rol = rol
        self.nombre_completo = nombre_completo
        self.ultima_actualizacion = datetime.now()

        # Contenedor principal
        contenedor = QWidget()
        layout_principal = QVBoxLayout(contenedor)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # Barra superior con botones de navegación y cerrar sesión
        nav_bar = QFrame()
        nav_bar.setObjectName("barraNavegacion")
        nav_bar.setFixedHeight(80)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo y título de la aplicación
        app_title_layout = QHBoxLayout()
        app_title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        app_title_layout.setSpacing(15)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("hospital_icon.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        
        title = QLabel("BEDSENSE")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(700)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        
        app_title_layout.addWidget(logo_label)
        app_title_layout.addWidget(title)
        nav_layout.addLayout(app_title_layout)
        
        # Botones de navegación
        self.panel_camas = PanelCamas(rol, nombre_completo)
        self.panel_admin = PanelAdmin()
        self.panel_pacientes = PanelPacientes(nombre_completo)
        self.panel_notificaciones = PanelNotificaciones(rol, nombre_completo)
        self.panel_dashboard = DashboardPanel(rol, nombre_completo)
        self.panel_reportes = ReportesPanel()
        
        self.panel = QStackedWidget()
        self.panel.addWidget(self.panel_dashboard)  # 0
        self.panel.addWidget(self.panel_camas)      # 1
        self.panel.addWidget(self.panel_admin)      # 2
        self.panel.addWidget(self.panel_pacientes)  # 3
        self.panel.addWidget(self.panel_notificaciones) # 4
        self.panel.addWidget(self.panel_reportes)   # 5
        
        # Botones comunes para todos los roles
        btn_dashboard = QPushButton("Dashboard")
        btn_dashboard.setObjectName("botonNavegacion")
        btn_dashboard.setCheckable(True)
        btn_dashboard.setChecked(True)
        
        btn_camas = QPushButton("Gestión de camas")
        btn_camas.setObjectName("botonNavegacion")
        btn_camas.setCheckable(True)
        
        btn_notificaciones = QPushButton("Notificaciones")
        btn_notificaciones.setObjectName("botonNavegacion")
        btn_notificaciones.setCheckable(True)
        
        # Botones específicos para admin
        if rol == "admin":
            btn_usuarios = QPushButton("Gestionar usuarios")
            btn_usuarios.setObjectName("botonNavegacion")
            btn_usuarios.setCheckable(True)
            
            btn_pacientes = QPushButton("Gestión de pacientes")
            btn_pacientes.setObjectName("botonNavegacion")
            btn_pacientes.setCheckable(True)
            
            btn_reportes = QPushButton("Reportes")
            btn_reportes.setObjectName("botonNavegacion")
            btn_reportes.setCheckable(True)
            
            btn_dashboard.clicked.connect(lambda: self.cambiar_panel(btn_dashboard, self.panel_dashboard))
            btn_camas.clicked.connect(lambda: self.cambiar_panel(btn_camas, self.panel_camas))
            btn_usuarios.clicked.connect(lambda: self.cambiar_panel(btn_usuarios, self.panel_admin))
            btn_pacientes.clicked.connect(lambda: self.cambiar_panel(btn_pacientes, self.panel_pacientes))
            btn_notificaciones.clicked.connect(lambda: self.cambiar_panel(btn_notificaciones, self.panel_notificaciones))
            btn_reportes.clicked.connect(lambda: self.cambiar_panel(btn_reportes, self.panel_reportes))
            
            # Grupo de botones para mantener el estado de selección
            self.button_group = []
            self.button_group.append(btn_dashboard)
            self.button_group.append(btn_camas)
            self.button_group.append(btn_usuarios)
            self.button_group.append(btn_pacientes)
            self.button_group.append(btn_notificaciones)
            self.button_group.append(btn_reportes)
            
            nav_layout.addWidget(btn_dashboard)
            nav_layout.addWidget(btn_camas)
            nav_layout.addWidget(btn_usuarios)
            nav_layout.addWidget(btn_pacientes)
            nav_layout.addWidget(btn_notificaciones)
            nav_layout.addWidget(btn_reportes)
        else:
            # Botones para roles no admin
            btn_dashboard.clicked.connect(lambda: self.cambiar_panel(btn_dashboard, self.panel_dashboard))
            btn_camas.clicked.connect(lambda: self.cambiar_panel(btn_camas, self.panel_camas))
            btn_notificaciones.clicked.connect(lambda: self.cambiar_panel(btn_notificaciones, self.panel_notificaciones))
            
            if rol in ["medico", "enfermera"]:
                btn_pacientes = QPushButton("Gestión de pacientes")
                btn_pacientes.setObjectName("botonNavegacion")
                btn_pacientes.setCheckable(True)
                btn_pacientes.clicked.connect(lambda: self.cambiar_panel(btn_pacientes, self.panel_pacientes))
                
                self.button_group = []
                self.button_group.append(btn_dashboard)
                self.button_group.append(btn_camas)
                self.button_group.append(btn_pacientes)
                self.button_group.append(btn_notificaciones)
                
                nav_layout.addWidget(btn_dashboard)
                nav_layout.addWidget(btn_camas)
                nav_layout.addWidget(btn_pacientes)
                nav_layout.addWidget(btn_notificaciones)
            else:
                self.button_group = []
                self.button_group.append(btn_dashboard)
                self.button_group.append(btn_camas)
                self.button_group.append(btn_notificaciones)
                
                nav_layout.addWidget(btn_dashboard)
                nav_layout.addWidget(btn_camas)
                nav_layout.addWidget(btn_notificaciones)
        
        # Espaciador
        nav_layout.addStretch()
        
        # Información de usuario
        user_layout = QHBoxLayout()
        user_layout.setSpacing(12)
        
        # Avatar de usuario
        avatar = AvatarWidget()
        avatar_pixmap = QPixmap(50, 50)
        avatar_pixmap.fill(QColor("#3b82f6"))
        avatar.setPixmap(avatar_pixmap)
        
        user_info = QLabel(f"{nombre_completo}\n<small>{rol.capitalize()}</small>")
        user_info.setStyleSheet("font-weight: 600; color: #334155;")
        user_info.setTextFormat(Qt.TextFormat.RichText)
        
        user_layout.addWidget(avatar)
        user_layout.addWidget(user_info)
        nav_layout.addLayout(user_layout)
        
        # Botón para cerrar sesión
        btn_cerrar_sesion = QPushButton("Cerrar sesión")
        btn_cerrar_sesion.setObjectName("botonCerrarSesion")
        btn_cerrar_sesion.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar_sesion.setIcon(QIcon.fromTheme("system-log-out"))
        btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        nav_layout.addWidget(btn_cerrar_sesion)
        
        # Añadir barra de navegación
        layout_principal.addWidget(nav_bar)
        
        # Añadir panel principal
        layout_principal.addWidget(self.panel, 1)
        
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.actualizar_barra_estado()
        
        # Timer para actualizar la barra de estado
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_barra_estado)
        self.timer.start(60000)  # Actualizar cada minuto
        
        self.setCentralWidget(contenedor)
        
        # Mostrar el panel inicial
        self.panel.setCurrentWidget(self.panel_dashboard)
        btn_dashboard.setChecked(True)
            
        # Fondo sutil
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f1f5f9"))
        self.setPalette(palette)
        
        # Mostrar notificaciones para técnicos y limpieza
        if rol in ["tecnico", "limpieza"]:
            self.mostrar_notificaciones()
            

    def cambiar_panel(self, button, widget):
        if button:
            for btn in self.button_group:
                btn.setChecked(False)
            button.setChecked(True)
        self.panel.setCurrentWidget(widget)
        

    def cerrar_sesion(self):
        self.login = Login()
        self.login.show()
        self.close()
        
    def mostrar_notificaciones(self):
        dialog = NotificacionesDialog(self.rol, self.nombre_completo)
        dialog.exec()
        
        # Animación de entrada
        anim = QPropertyAnimation(dialog, b"windowOpacity")
        anim.setDuration(800)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        
    def actualizar_barra_estado(self):
        hora_actual = datetime.now().strftime("%H:%M:%S")
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.status_bar.showMessage(f"Usuario: {self.nombre_completo} | Rol: {self.rol.capitalize()} | {fecha_actual} {hora_actual}")

# --------------------- Dashboard ---------------------
class DashboardPanel(QWidget):
    def __init__(self, rol, nombre_completo):
        super().__init__()
        self.rol = rol
        self.nombre_completo = nombre_completo
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Título
        title = QLabel("Dashboard")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        # Tarjetas resumen
        resumen_layout = QGridLayout()
        resumen_layout.setSpacing(20)
        
        # Tarjeta 1: Camas totales
        tarjeta_total = self.crear_tarjeta("🛏️", "Camas Totales", "0", "#dbeafe", "#3b82f6")
        # Tarjeta 2: Camas disponibles
        tarjeta_disponibles = self.crear_tarjeta("✅", "Camas Disponibles", "0", "#dcfce7", "#16a34a")
        # Tarjeta 3: Camas ocupadas
        tarjeta_ocupadas = self.crear_tarjeta("⛔", "Camas Ocupadas", "0", "#fee2e2", "#dc2626")
        # Tarjeta 4: Notificaciones pendientes
        tarjeta_notificaciones = self.crear_tarjeta("🔔", "Notificaciones Pendientes", "0", "#fef3c7", "#d97706")
        # Tarjeta 5: Camas en mantenimiento
        tarjeta_mantenimiento = self.crear_tarjeta("🛠️", "En Mantenimiento", "0", "#ffedd5", "#c2410c")
        # Tarjeta 6: Camas sucias
        tarjeta_sucias = self.crear_tarjeta("🧹", "Camas Sucias", "0", "#fef3c7", "#d97706")
        
        resumen_layout.addWidget(tarjeta_total, 0, 0)
        resumen_layout.addWidget(tarjeta_disponibles, 0, 1)
        resumen_layout.addWidget(tarjeta_ocupadas, 0, 2)
        resumen_layout.addWidget(tarjeta_notificaciones, 1, 0)
        resumen_layout.addWidget(tarjeta_mantenimiento, 1, 1)
        resumen_layout.addWidget(tarjeta_sucias, 1, 2)
        
        layout.addLayout(resumen_layout)
        
        # Tareas pendientes (solo para técnico y limpieza)
        if self.rol in ["tecnico", "limpieza"]:
            tareas_group = QGroupBox("Tareas Pendientes")
            tareas_layout = QVBoxLayout(tareas_group)
            
            self.lista_tareas = QListWidget()
            self.lista_tareas.setStyleSheet("border: none;")
            
            tareas_layout.addWidget(self.lista_tareas)
            layout.addWidget(tareas_group)
        
        self.setLayout(layout)
        
        # Cargar datos
        self.cargar_datos()
        
    def crear_tarjeta(self, icono, titulo, valor, color_fondo, color_texto):
        tarjeta = QWidget()
        tarjeta.setObjectName("tarjeta")
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(20, 20, 20, 20)
        
        icono_label = QLabel(icono)
        icono_label.setObjectName("tarjeta-icono")
        icono_label.setStyleSheet(f"background-color: {color_fondo}; color: {color_texto};")
        icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("tarjeta-titulo")
        
        valor_label = QLabel(valor)
        valor_label.setObjectName("tarjeta-valor")
        
        tarjeta_layout.addWidget(icono_label)
        tarjeta_layout.addWidget(titulo_label)
        tarjeta_layout.addWidget(valor_label)
        
        # Guardar referencia para actualización
        if titulo == "Camas Totales":
            self.valor_total = valor_label
        elif titulo == "Camas Disponibles":
            self.valor_disponibles = valor_label
        elif titulo == "Camas Ocupadas":
            self.valor_ocupadas = valor_label
        elif titulo == "Notificaciones Pendientes":
            self.valor_notificaciones = valor_label
        elif titulo == "En Mantenimiento":
            self.valor_mantenimiento = valor_label
        elif titulo == "Camas Sucias":
            self.valor_sucias = valor_label
        
        return tarjeta

    def cargar_datos(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Camas totales
            cursor.execute("SELECT COUNT(*) FROM camas")
            total = cursor.fetchone()[0]
            self.valor_total.setText(str(total))
            
            # Camas disponibles
            cursor.execute("""
                SELECT COUNT(*) 
                FROM camas 
                WHERE disponible = TRUE 
                AND id NOT IN (SELECT cama_id FROM estado_equipos WHERE operatividad = FALSE)
                AND id NOT IN (SELECT cama_id FROM limpieza_camas WHERE limpieza_realizada = FALSE)
            """)
            disponibles = cursor.fetchone()[0]
            self.valor_disponibles.setText(str(disponibles))
            
            # Camas ocupadas
            cursor.execute("SELECT COUNT(*) FROM camas WHERE disponible = FALSE")
            ocupadas = cursor.fetchone()[0]
            self.valor_ocupadas.setText(str(ocupadas))
            
            # Notificaciones pendientes
            if self.rol == "admin":
                cursor.execute("SELECT COUNT(*) FROM notificaciones WHERE resuelta = FALSE")
            else:
                cursor.execute("SELECT COUNT(*) FROM notificaciones WHERE destinatario_rol = %s AND resuelta = FALSE", (self.rol,))
            notificaciones = cursor.fetchone()[0]
            self.valor_notificaciones.setText(str(notificaciones))
            
            # Camas en mantenimiento
            cursor.execute("SELECT COUNT(*) FROM estado_equipos WHERE operatividad = FALSE")
            mantenimiento = cursor.fetchone()[0]
            self.valor_mantenimiento.setText(str(mantenimiento))
            
            # Camas sucias
            cursor.execute("SELECT COUNT(*) FROM limpieza_camas WHERE limpieza_realizada = FALSE")
            sucias = cursor.fetchone()[0]
            self.valor_sucias.setText(str(sucias))
            
            # Tareas pendientes para técnico y limpieza
            if self.rol in ["tecnico", "limpieza"]:
                self.lista_tareas.clear()
                cursor.execute("""
                    SELECT id, cama_id, mensaje, fecha 
                    FROM notificaciones 
                    WHERE destinatario_rol = %s AND resuelta = FALSE
                    ORDER BY fecha DESC
                """, (self.rol,))
                tareas = cursor.fetchall()
                for tarea in tareas:
                    item = QListWidgetItem(f"Cama {tarea[1]}: {tarea[2]} - {tarea[3].strftime('%d/%m/%Y')}")
                    item.setData(Qt.ItemDataRole.UserRole, tarea[0])
                    self.lista_tareas.addItem(item)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar datos: {str(e)}")

# --------------------- Panel Reportes ---------------------
class ReportesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Título
        title = QLabel("Generador de Reportes")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        # Formulario de filtros
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_inicio.setCalendarPopup(True)
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        
        self.tipo_reporte = QComboBox()
        self.tipo_reporte.addItems([
            "Ocupación de Camas", 
            "Actividad de Usuarios",
            "Notificaciones por Tipo",
            "Estados de Camas por Área"
        ])
        
        form_layout.addRow("Fecha Inicio:", self.fecha_inicio)
        form_layout.addRow("Fecha Fin:", self.fecha_fin)
        form_layout.addRow("Tipo de Reporte:", self.tipo_reporte)
        
        layout.addLayout(form_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_generar = QPushButton("Generar Reporte")
        btn_generar.setObjectName("botonExito")
        btn_generar.clicked.connect(self.generar_reporte)
        
        btn_exportar = QPushButton("Exportar a PDF")
        btn_exportar.setObjectName("botonSecundario")
        btn_exportar.clicked.connect(self.exportar_pdf)
        
        btn_layout.addWidget(btn_generar)
        btn_layout.addWidget(btn_exportar)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Área de visualización
        self.reporte_text = QTextEdit()
        self.reporte_text.setReadOnly(True)
        layout.addWidget(self.reporte_text, 1)
    
    def generar_reporte(self):
        fecha_ini = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        tipo = self.tipo_reporte.currentText()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            reporte = {
                'titulo': f"Reporte: {tipo}",
                'periodo': f"Período: {fecha_ini} a {fecha_fin}",
                'encabezados': [],
                'datos': [],
                'resumen': ""
            }
            
            if tipo == "Ocupación de Camas":
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN disponible = TRUE THEN 1 ELSE 0 END) as disponibles,
                        SUM(CASE WHEN disponible = FALSE THEN 1 ELSE 0 END) as ocupadas
                    FROM camas
                """)
                
                total, disponibles, ocupadas = cursor.fetchone()
                porcentaje = round((ocupadas/total)*100, 2) if total > 0 else 0
                
                reporte['encabezados'] = ["Total", "Disponibles", "Ocupadas", "% Ocupación"]
                reporte['datos'] = [[total, disponibles, ocupadas, f"{porcentaje}%"]]
                reporte['resumen'] = "Resumen de ocupación de camas en el sistema"
                
            elif tipo == "Actividad de Usuarios":
                cursor.execute("""
                    SELECT 
                        u.nombre_completo,
                        u.rol,
                        COUNT(n.id) as notificaciones
                    FROM usuarios u
                    LEFT JOIN notificaciones n ON u.nombre_completo = n.remitente
                    WHERE n.fecha BETWEEN %s AND %s
                    GROUP BY u.nombre_completo, u.rol
                    ORDER BY notificaciones DESC
                """, (fecha_ini, fecha_fin))
                
                reporte['encabezados'] = ["Usuario", "Rol", "Notificaciones"]
                reporte['datos'] = cursor.fetchall()
                reporte['resumen'] = "Actividad de usuarios por cantidad de notificaciones creadas"
                
            elif tipo == "Notificaciones por Tipo":
                cursor.execute("""
                    SELECT 
                        tipo_problema,
                        COUNT(*) as cantidad
                    FROM notificaciones
                    WHERE fecha BETWEEN %s AND %s
                    GROUP BY tipo_problema
                    ORDER BY cantidad DESC
                """, (fecha_ini, fecha_fin))
                
                reporte['encabezados'] = ["Tipo de Problema", "Cantidad"]
                reporte['datos'] = cursor.fetchall()
                reporte['resumen'] = "Distribución de notificaciones por tipo de problema"
                
            elif tipo == "Estados de Camas por Área":
                cursor.execute("""
                    SELECT 
                        a.nombre as area,
                        COUNT(c.id) as total,
                        SUM(CASE WHEN c.disponible = TRUE THEN 1 ELSE 0 END) as disponibles,
                        SUM(CASE WHEN c.disponible = FALSE THEN 1 ELSE 0 END) as ocupadas
                    FROM camas c
                    JOIN cama_area ca ON c.id = ca.cama_id
                    JOIN areas a ON ca.area_id = a.id
                    GROUP BY a.nombre
                """)
                
                reporte['encabezados'] = ["Área", "Total", "Disponibles", "Ocupadas", "% Ocupación"]
                datos = []
                for area, total, disp, ocup in cursor:
                    porcentaje = round((ocup/total)*100, 2) if total > 0 else 0
                    datos.append([area, total, disp, ocup, f"{porcentaje}%"])
                reporte['datos'] = datos
                reporte['resumen'] = "Distribución de estados de camas por área hospitalaria"
            
            # Generar texto plano para visualización
            texto = f"{reporte['titulo']}\n{reporte['periodo']}\n\n"
            texto += f"{reporte['resumen']}\n\n"
            
            if reporte['encabezados']:
                texto += "\t".join(reporte['encabezados']) + "\n"
                texto += "-" * 50 + "\n"
                
                for fila in reporte['datos']:
                    texto += "\t".join(str(x) for x in fila) + "\n"
            
            self.reporte_text.setPlainText(texto)
            self.reporte_data = reporte  # Guardar datos para exportación
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def exportar_pdf(self):
        if not hasattr(self, 'reporte_data') or not self.reporte_data['datos']:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar. Genere un reporte primero.")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Reporte a PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_name:
            return
            
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Configuración inicial
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, self.reporte_data['titulo'], 0, 1, 'C')
            
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, self.reporte_data['periodo'], 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'I', 12)
            pdf.multi_cell(0, 10, self.reporte_data['resumen'])
            pdf.ln(10)
            
            # Configurar tabla
            pdf.set_font("Arial", 'B', 12)
            col_widths = [pdf.get_string_width(h)+6 for h in self.reporte_data['encabezados']]
            
            # Ajustar anchos si es necesario
            page_width = pdf.w - 2*pdf.l_margin
            total_width = sum(col_widths)
            
            if total_width > page_width:
                ratio = page_width / total_width
                col_widths = [w*ratio for w in col_widths]
            
            # Encabezados de la tabla
            for i, header in enumerate(self.reporte_data['encabezados']):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
            pdf.ln()
            
            # Datos de la tabla
            pdf.set_font("Arial", '', 10)
            for fila in self.reporte_data['datos']:
                for i, dato in enumerate(fila):
                    pdf.cell(col_widths[i], 10, str(dato), 1, 0, 'C')
                pdf.ln()
            
            # Pie de página
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 10, f"Generado el {QDate.currentDate().toString('dd/MM/yyyy')}", 0, 0, 'R')
            
            # Guardar PDF
            if not file_name.endswith('.pdf'):
                file_name += '.pdf'
            
            pdf.output(file_name)
            QMessageBox.information(self, "Éxito", f"Reporte exportado a:\n{file_name}")
            
        except ImportError:
            QMessageBox.critical(self, "Error", 
                "La librería FPDF no está instalada. Instálela con:\n\npip install fpdf2")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el PDF: {str(e)}")


# --------------------- Diálogo de Notificaciones ---------------------
class NotificacionesDialog(QDialog):
    def __init__(self, rol, nombre_completo):
        super().__init__()
        self.setWindowTitle("Notificaciones Pendientes")
        self.setMinimumSize(600, 400)
        self.rol = rol
        self.nombre_completo = nombre_completo
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        title = QLabel(f"Notificaciones para {rol.capitalize()}")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        # Contenedor de notificaciones
        self.scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.scroll_widget)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        layout.addWidget(scroll_area, 1)
        
        # Cargar notificaciones
        self.cargar_notificaciones()
        
        # Botones
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)
        
    def cargar_notificaciones(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Obtener notificaciones no resueltas para este rol
            cursor.execute("""
                SELECT id, cama_id, remitente, mensaje, fecha 
                FROM notificaciones 
                WHERE destinatario_rol = %s AND resuelta = FALSE
            """, (self.rol,))
            
            notificaciones = cursor.fetchall()
            
            if not notificaciones:
                no_notif = QLabel("No hay notificaciones pendientes")
                no_notif.setStyleSheet("text-align: center; color: #64748b; font-style: italic; padding: 20px;")
                self.scroll_widget.layout().addWidget(no_notif)
                return
                
            for notif in notificaciones:
                notif_id, cama_id, remitente, mensaje, fecha = notif
                
                # Contenedor de notificación
                contenedor = QFrame()
                contenedor.setObjectName("notificacion-contenedor")
                contenedor_layout = QVBoxLayout(contenedor)
                contenedor_layout.setContentsMargins(10, 10, 10, 10)
                
                # Título
                titulo = QLabel(f"Notificación para cama #{cama_id}")
                titulo.setObjectName("notificacion-titulo")
                
                # Contenido
                contenido = QLabel(f"{mensaje}")
                contenido.setObjectName("notificacion-contenido")
                contenido.setWordWrap(True)
                
                # Remitente y fecha
                info_layout = QHBoxLayout()
                
                remitente_label = QLabel(f"Reportado por: {remitente}")
                remitente_label.setStyleSheet("font-size: 12px; color: #64748b;")
                
                fecha_label = QLabel(fecha.strftime("%d/%m/%Y %H:%M"))
                fecha_label.setObjectName("notificacion-fecha")
                
                info_layout.addWidget(remitente_label)
                info_layout.addStretch()
                info_layout.addWidget(fecha_label)
                
                # Botones de acción
                btn_layout = QHBoxLayout()
                
                resolver_btn = QPushButton("Marcar como resuelto")
                resolver_btn.setObjectName("botonExito")
                resolver_btn.clicked.connect(lambda _, nid=notif_id: self.resolver_notificacion(nid))
                
                responder_btn = QPushButton("Responder")
                responder_btn.setObjectName("botonSecundario")
                responder_btn.clicked.connect(lambda _, nid=notif_id: self.responder_notificacion(nid))
                
                btn_layout.addWidget(resolver_btn)
                btn_layout.addWidget(responder_btn)
                
                # Agregar elementos al contenedor
                contenedor_layout.addWidget(titulo)
                contenedor_layout.addWidget(contenido)
                contenedor_layout.addLayout(info_layout)
                contenedor_layout.addLayout(btn_layout)
                
                # Agregar al layout principal
                self.scroll_widget.layout().addWidget(contenedor)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las notificaciones: {str(e)}")
            
    def resolver_notificacion(self, notif_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE notificaciones SET resuelta = TRUE, resolutor = %s WHERE id = %s", 
                          (self.nombre_completo, notif_id))
            conn.commit()
            QMessageBox.information(self, "Éxito", "Notificación marcada como resuelta")
            
            # Recargar notificaciones
            for i in reversed(range(self.scroll_widget.layout().count())): 
                widget = self.scroll_widget.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            self.cargar_notificaciones()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo resolver la notificación: {str(e)}")
            
    def responder_notificacion(self, notif_id):
        respuesta, ok = QInputDialog.getMultiLineText(
            self, 
            "Responder Notificación", 
            "Escriba su respuesta:", 
            ""
        )
        
        if ok and respuesta.strip():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE notificaciones SET respuesta = %s, resolutor = %s WHERE id = %s", 
                             (respuesta, self.nombre_completo, notif_id))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Respuesta enviada correctamente")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo enviar la respuesta: {str(e)}")

# --------------------- Panel Admin ---------------------
class PanelAdmin(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Título del panel
        title = QLabel("Gestión de Usuarios")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Pestaña Crear Usuario
        crear_tab = QWidget()
        crear_layout = QVBoxLayout(crear_tab)
        crear_layout.setContentsMargins(30, 30, 30, 30)
        crear_layout.setSpacing(25)
        
        form = QFormLayout()
        form.setVerticalSpacing(20)
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nombre de usuario")
        
        self.input_nombre_completo = QLineEdit()
        self.input_nombre_completo.setPlaceholderText("Nombre completo del usuario")
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contraseña")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Administrador", "Médico", "Enfermera", "Técnico", "Limpieza"])
        
        form.addRow(QLabel("Usuario:"), self.input_user)
        form.addRow(QLabel("Nombre completo:"), self.input_nombre_completo)
        form.addRow(QLabel("Contraseña:"), self.input_pass)
        form.addRow(QLabel("Rol:"), self.combo_rol)
        
        crear_layout.addLayout(form)
        
        crear_btn = QPushButton("Crear usuario")
        crear_btn.setObjectName("botonExito")
        crear_btn.clicked.connect(self.crear_usuario)
        crear_layout.addWidget(crear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Pestaña Modificar Usuario
        modificar_tab = QWidget()
        modificar_layout = QVBoxLayout(modificar_tab)
        modificar_layout.setContentsMargins(30, 30, 30, 30)
        modificar_layout.setSpacing(25)
        
        mod_form = QFormLayout()
        mod_form.setVerticalSpacing(20)
        
        self.combo_usuarios = QComboBox()
        self.cargar_usuarios()
        
        self.nuevo_rol_combo = QComboBox()
        self.nuevo_rol_combo.addItems(["Administrador", "Médico", "Enfermera", "Técnico", "Limpieza"])
        
        self.nueva_pass_input = QLineEdit()
        self.nueva_pass_input.setPlaceholderText("Dejar en blanco para mantener la actual")
        self.nueva_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        mod_form.addRow(QLabel("Usuario a modificar:"), self.combo_usuarios)
        mod_form.addRow(QLabel("Nuevo rol:"), self.nuevo_rol_combo)
        mod_form.addRow(QLabel("Nueva contraseña:"), self.nueva_pass_input)
        
        modificar_layout.addLayout(mod_form)
        
        modificar_btn = QPushButton("Actualizar usuario")
        modificar_btn.setObjectName("botonExito")
        modificar_btn.clicked.connect(self.modificar_usuario)
        modificar_layout.addWidget(modificar_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.tab_widget.addTab(crear_tab, "Crear Usuario")
        self.tab_widget.addTab(modificar_tab, "Modificar Usuario")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def cargar_usuarios(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT usuario FROM usuarios")
            self.combo_usuarios.clear()
            self.combo_usuarios.addItems([r[0] for r in cursor.fetchall()])
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def crear_usuario(self):
        user = sanitizar_input(self.input_user.text())
        nombre_completo = sanitizar_input(self.input_nombre_completo.text())
        pwd = self.input_pass.text()
        rol = self.combo_rol.currentText().lower()
        
        if not user or not pwd or not nombre_completo:
            QMessageBox.warning(self, "Campos requeridos", "Debe completar todos los campos")
            return
            
        pwd_hash = hash_password(pwd)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) VALUES (%s, %s, %s, %s)", 
                         (user, pwd_hash, rol, nombre_completo))
            conn.commit()
            
            # Animación de éxito
            anim = QPropertyAnimation(self.input_user, b"geometry")
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            anim.setStartValue(QRect(self.input_user.x(), self.input_user.y(), 
                               self.input_user.width(), self.input_user.height()))
            anim.setEndValue(QRect(self.input_user.x(), self.input_user.y(), 
                              self.input_user.width(), self.input_user.height()))
            anim.start()
            
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente")
            self.input_user.clear()
            self.input_nombre_completo.clear()
            self.input_pass.clear()
            self.cargar_usuarios()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar_usuario(self):
        usuario = self.combo_usuarios.currentText()
        nuevo_rol = self.nuevo_rol_combo.currentText().lower()
        nueva_pass = self.nueva_pass_input.text()
        
        if not usuario:
            QMessageBox.warning(self, "Selección requerida", "Debe seleccionar un usuario")
        return
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if nueva_pass:
                pwd_hash = hash_password(nueva_pass)
                cursor.execute("UPDATE usuarios SET rol = %s, password_hash = %s WHERE usuario = %s", 
                              (nuevo_rol, pwd_hash, usuario))
            else:
                cursor.execute("UPDATE usuarios SET rol = %s WHERE usuario = %s", 
                              (nuevo_rol, usuario))
                
            conn.commit()
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
            self.nueva_pass_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

# --------------------- Panel Pacientes ---------------------
class PanelPacientes(QWidget):
    def __init__(self, nombre_completo):
        super().__init__()
        self.nombre_completo = nombre_completo
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Título del panel
        title = QLabel("Gestión de Pacientes")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        # Filtros y selección de área
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        filter_layout.addWidget(QLabel("Área hospitalaria:"))
        self.area_combo = QComboBox()
        self.area_combo.setMinimumWidth(250)
        filter_layout.addWidget(self.area_combo)
        
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setObjectName("botonSecundario")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.clicked.connect(self.cargar_camas)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Tabla de camas
        self.tabla = QTableWidget()
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSortingEnabled(True)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla, 1)
        
        # Formulario para asignar paciente
        form_group = QGroupBox("Asignar paciente a cama")
        form_layout = QVBoxLayout(form_group)
        form_layout.setContentsMargins(25, 30, 25, 25)
        form_layout.setSpacing(20)
        
        form = QFormLayout()
        form.setVerticalSpacing(15)
        
        self.dni = QLineEdit()
        self.dni.setPlaceholderText("Ingrese DNI del paciente")
        
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo o deje en blanco para buscar")
        
        form.addRow(QLabel("DNI:"), self.dni)
        form.addRow(QLabel("Nombre:"), self.nombre)
        
        form_layout.addLayout(form)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.asignar_btn = QPushButton("Asignar cama")
        self.asignar_btn.setObjectName("botonExito")
        self.asignar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.asignar_btn.clicked.connect(self.asignar_paciente)
        self.asignar_btn.setEnabled(False)
        
        self.alta_btn = QPushButton("Dar de alta")
        self.alta_btn.setObjectName("botonPeligro")
        self.alta_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.alta_btn.clicked.connect(self.dar_alta)
        self.alta_btn.setEnabled(False)
        
        btn_layout.addWidget(self.asignar_btn)
        btn_layout.addWidget(self.alta_btn)
        btn_layout.addStretch()
        
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(form_group)
        self.setLayout(layout)
        
        self.cargar_areas()
        self.tabla.itemSelectionChanged.connect(self.actualizar_botones)
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def cargar_areas(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM areas")
            self.area_combo.clear()
            self.area_combo.addItems([r[0] for r in cursor.fetchall()])
            self.area_combo.currentTextChanged.connect(self.cargar_camas)
            self.cargar_camas()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def cargar_camas(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.ubicacion, 
                       CASE 
                           WHEN c.disponible AND COALESCE(lc.limpieza_realizada, TRUE) THEN 'Disponible'
                           WHEN NOT c.disponible THEN 'Ocupada'
                           WHEN NOT COALESCE(lc.limpieza_realizada, TRUE) THEN 'Sucio'
                           ELSE 'No disponible'
                       END as estado,
                       IFNULL(c.paciente_dni, ''), IFNULL(c.paciente_nombre, '')
                FROM camas c
                JOIN cama_area ca ON c.id = ca.cama_id
                JOIN areas a ON ca.area_id = a.id
                LEFT JOIN limpieza_camas lc ON c.id = lc.cama_id
                WHERE a.nombre = %s
            ''', (self.area_combo.currentText(),))
            
            rows = cursor.fetchall()
            self.tabla.setRowCount(len(rows))
            self.tabla.setColumnCount(5)
            self.tabla.setHorizontalHeaderLabels(["ID", "Ubicación", "Estado", "DNI", "Nombre"])
            self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            
            for i, fila in enumerate(rows):
                for j, val in enumerate(fila):
                    item = QTableWidgetItem(str(val))
                    
                    # Resaltar estado
                    if j == 2:
                        estado = val
                        if estado == 'Disponible':
                            item.setData(Qt.ItemDataRole.UserRole, "disponible")
                            item.setBackground(QColor(220, 252, 231))
                        elif estado == 'Ocupada':
                            item.setData(Qt.ItemDataRole.UserRole, "ocupada")
                            item.setBackground(QColor(254, 226, 226))
                        elif estado == 'Sucio':
                            item.setData(Qt.ItemDataRole.UserRole, "sucio")
                            item.setBackground(QColor(254, 245, 231))
                        else:
                            item.setData(Qt.ItemDataRole.UserRole, "no_disponible")
                            item.setBackground(QColor(241, 245, 249))
                            
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla.setItem(i, j, item)
                    
            # Ajustar tamaño de columnas
            for i in range(4):
                self.tabla.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            self.tabla.resizeRowsToContents()
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def actualizar_botones(self):
        row = self.tabla.currentRow()
        if row >= 0:
            estado_item = self.tabla.item(row, 2)
            estado = estado_item.data(Qt.ItemDataRole.UserRole) if estado_item else ""
            self.asignar_btn.setEnabled(estado == "disponible")
            self.alta_btn.setEnabled(estado == "ocupada")

    def asignar_paciente(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
            
        cama_id = self.tabla.item(row, 0).text()
        dni_paciente = self.dni.text()
        nombre_paciente = self.nombre.text()

        if not dni_paciente:
            QMessageBox.warning(self, "DNI requerido", "Debe ingresar el DNI del paciente")
            return

        if not nombre_paciente.strip():
            try:
                headers = {"Authorization": f"Bearer {API_TOKEN}"}
                response = requests.get(API_URL + dni_paciente, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    nombre_paciente = f"{data['nombres']} {data['apellidoPaterno']} {data['apellidoMaterno']}"
                    self.nombre.setText(nombre_paciente)
                else:
                    QMessageBox.warning(self, "Error", "DNI no encontrado o token inválido.")
                    return
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE camas SET disponible = FALSE, paciente_dni = %s, paciente_nombre = %s WHERE id = %s",
                         (dni_paciente, nombre_paciente, cama_id))
            conn.commit()
            self.cargar_camas()
            
            # Animación de éxito
            self.tabla.clearSelection()
            self.tabla.selectRow(row)
            
            QMessageBox.information(self, "Éxito", "Paciente asignado correctamente")
            self.dni.clear()
            self.nombre.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def dar_alta(self):
        row = self.tabla.currentRow()
        if row < 0:
            return
            
        cama_id = self.tabla.item(row, 0).text()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE camas SET disponible = TRUE, paciente_dni = NULL, paciente_nombre = NULL WHERE id = %s",
                         (cama_id,))
            
            # Marcar cama como sucia
            cursor.execute("REPLACE INTO limpieza_camas (cama_id, limpieza_realizada) VALUES (%s, FALSE)", (cama_id,))
            
            conn.commit()
            self.cargar_camas()
            QMessageBox.information(self, "Éxito", "Paciente dado de alta. Cama marcada como sucia")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

# --------------------- Panel Camas ---------------------
class PanelCamas(QWidget):
    def __init__(self, rol, nombre_completo):
        super().__init__()
        self.rol = rol
        self.nombre_completo = nombre_completo
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Título del panel
        title_text = {
            "admin": "Gestión de Camas Hospitalarias",
            "medico": "Asignación de Camas",
            "enfermera": "Asignación de Camas",
            "tecnico": "Estado Técnico de Camas",
            "limpieza": "Limpieza de Camas"
        }.get(rol, "Gestión de Camas")
        
        title = QLabel(title_text)
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)
        
        # Filtros y selección de área
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        filter_layout.addWidget(QLabel("Área hospitalaria:"))
        self.area_combo = QComboBox()
        self.area_combo.setMinimumWidth(250)
        filter_layout.addWidget(self.area_combo)
        
        # Buscador
        buscador = QWidget()
        buscador.setObjectName("contenedorBuscador")
        buscador_layout = QHBoxLayout(buscador)
        buscador_layout.setContentsMargins(10, 5, 10, 5)
        
        self.buscador = QLineEdit()
        self.buscador.setObjectName("buscadorInput")
        self.buscador.setPlaceholderText("Buscar cama...")
        self.buscador.textChanged.connect(self.filtrar_tabla)
        
        buscador_layout.addWidget(QLabel("🔍"))
        buscador_layout.addWidget(self.buscador)
        filter_layout.addWidget(buscador)
        
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setObjectName("botonSecundario")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.clicked.connect(self.cargar_camas_area)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Tabla de camas
        self.tabla = QTableWidget()
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSortingEnabled(True)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla, 1)
        
        # Funcionalidades específicas por rol
        if rol in ["medico", "enfermera"]:
            # Formulario para asignar paciente
            form_group = QGroupBox("Asignar paciente a cama")
            form_layout = QVBoxLayout(form_group)
            form_layout.setContentsMargins(25, 30, 25, 25)
            form_layout.setSpacing(20)
            
            form = QFormLayout()
            form.setVerticalSpacing(15)
            
            self.dni = QLineEdit()
            self.dni.setPlaceholderText("Ingrese DNI del paciente")
            
            self.nombre = QLineEdit()
            self.nombre.setPlaceholderText("Nombre completo o deje en blanco para buscar")
            
            form.addRow(QLabel("DNI:"), self.dni)
            form.addRow(QLabel("Nombre:"), self.nombre)
            
            form_layout.addLayout(form)
            
            # Botones
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)
            
            self.asignar_btn = QPushButton("Asignar cama")
            self.asignar_btn.setObjectName("botonExito")
            self.asignar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.asignar_btn.clicked.connect(self.asignar_paciente)
            self.asignar_btn.setEnabled(False)
            
            self.liberar_btn = QPushButton("Liberar cama")
            self.liberar_btn.setObjectName("botonPeligro")
            self.liberar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.liberar_btn.clicked.connect(self.liberar_cama)
            self.liberar_btn.setEnabled(False)
            
            # Botón para notificar
            self.notificar_btn = QPushButton("Notificar problema")
            self.notificar_btn.setObjectName("botonSecundario")
            self.notificar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.notificar_btn.clicked.connect(self.notificar_problema)
            self.notificar_btn.setEnabled(False)
            
            btn_layout.addWidget(self.asignar_btn)
            btn_layout.addWidget(self.liberar_btn)
            btn_layout.addWidget(self.notificar_btn)
            btn_layout.addStretch()
            
            form_layout.addLayout(btn_layout)
            
            layout.addWidget(form_group)
            self.tabla.itemSelectionChanged.connect(self.actualizar_botones)
            
        elif rol == "admin":
            # Grupo para gestión de camas
            gestion_group = QGroupBox("Gestión de Camas")
            gestion_layout = QVBoxLayout(gestion_group)
            gestion_layout.setContentsMargins(25, 30, 25, 25)
            gestion_layout.setSpacing(25)
            
            # Layout para crear y modificar
            gestion_row = QHBoxLayout()
            gestion_row.setSpacing(25)
            
            # Crear cama
            crear_group = QGroupBox("Crear Nueva Cama")
            crear_layout = QVBoxLayout(crear_group)
            crear_layout.setContentsMargins(20, 25, 20, 20)
            
            form_crear = QFormLayout()
            form_crear.setVerticalSpacing(15)
            
            self.nueva_cama_id = QLineEdit()
            self.nueva_cama_id.setPlaceholderText("ID único para la cama")
            
            self.nueva_cama_ubicacion = QLineEdit()
            self.nueva_cama_ubicacion.setPlaceholderText("Ubicación física")
            
            form_crear.addRow(QLabel("ID de la cama:"), self.nueva_cama_id)
            form_crear.addRow(QLabel("Ubicación:"), self.nueva_cama_ubicacion)
            
            crear_layout.addLayout(form_crear)
            
            crear_btn = QPushButton("Crear cama")
            crear_btn.setObjectName("botonExito")
            crear_btn.clicked.connect(self.crear_cama)
            crear_layout.addWidget(crear_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            # Modificar cama
            modificar_group = QGroupBox("Modificar Cama Existente")
            modificar_layout = QVBoxLayout(modificar_group)
            modificar_layout.setContentsMargins(20, 25, 20, 20)
            
            form_modificar = QFormLayout()
            form_modificar.setVerticalSpacing(15)
            
            self.cama_a_modificar = QComboBox()
            self.cargar_todas_camas()
            
            self.nuevo_id_cama = QLineEdit()
            self.nuevo_id_cama.setPlaceholderText("Nuevo ID (opcional)")
            
            self.nueva_ubicacion = QLineEdit()
            self.nueva_ubicacion.setPlaceholderText("Nueva ubicación (opcional)")
            
            form_modificar.addRow(QLabel("Cama a modificar:"), self.cama_a_modificar)
            form_modificar.addRow(QLabel("Nuevo ID:"), self.nuevo_id_cama)
            form_modificar.addRow(QLabel("Nueva ubicación:"), self.nueva_ubicacion)
            
            modificar_layout.addLayout(form_modificar)
            
            modificar_btn = QPushButton("Actualizar cama")
            modificar_btn.setObjectName("botonExito")
            modificar_btn.clicked.connect(self.modificar_cama)
            modificar_layout.addWidget(modificar_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            # Botón para notificar
            self.notificar_btn = QPushButton("Notificar problema")
            self.notificar_btn.setObjectName("botonSecundario")
            self.notificar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.notificar_btn.clicked.connect(self.notificar_problema)
            self.notificar_btn.setEnabled(False)
            
            # Añadir grupos al layout
            gestion_row.addWidget(crear_group)
            gestion_row.addWidget(modificar_group)
            gestion_layout.addLayout(gestion_row)
            gestion_layout.addWidget(self.notificar_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            layout.addWidget(gestion_group)
            
            # Cargar datos iniciales
            self.cargar_todas_camas()
            self.tabla.itemSelectionChanged.connect(self.actualizar_botones)
            
        elif rol == "tecnico":
            btn = QPushButton("Alternar operatividad")
            btn.setObjectName("botonExito")
            btn.setIcon(QIcon.fromTheme("preferences-system"))
            btn.setIconSize(QSize(20, 20))
            btn.clicked.connect(self.operatividad)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            # Calendario de mantenimiento
            calendario_group = QGroupBox("Programar Mantenimiento")
            calendario_layout = QVBoxLayout(calendario_group)
            calendario_layout.setContentsMargins(20, 25, 20, 20)
            
            form = QFormLayout()
            form.setVerticalSpacing(15)
            
            self.cama_mantenimiento = QComboBox()
            self.cargar_camas_operativas()
            
            self.fecha_mantenimiento = QDateEdit()
            self.fecha_mantenimiento.setDate(QDate.currentDate().addDays(1))
            self.fecha_mantenimiento.setCalendarPopup(True)
            
            form.addRow(QLabel("Cama:"), self.cama_mantenimiento)
            form.addRow(QLabel("Fecha:"), self.fecha_mantenimiento)
            
            calendario_layout.addLayout(form)
            
            programar_btn = QPushButton("Programar")
            programar_btn.setObjectName("botonExito")
            programar_btn.clicked.connect(self.programar_mantenimiento)
            calendario_layout.addWidget(programar_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
            layout.addWidget(calendario_group)
            
        elif rol == "limpieza":
            btn = QPushButton("Marcar como limpia")
            btn.setObjectName("botonExito")
            btn.setIcon(QIcon.fromTheme("edit-clear"))
            btn.setIconSize(QSize(20, 20))
            btn.clicked.connect(self.limpiar)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.cargar_areas()
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def cargar_areas(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM areas")
            self.area_combo.clear()
            self.area_combo.addItems([r[0] for r in cursor.fetchall()])
            self.area_combo.currentTextChanged.connect(self.cargar_camas_area)
            self.cargar_camas_area()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def actualizar_botones(self):
        if self.rol in ["admin", "medico", "enfermera"]:
            row = self.tabla.currentRow()
            if row >= 0:
                estado_item = self.tabla.item(row, 2)
                estado = estado_item.data(Qt.ItemDataRole.UserRole) if estado_item else ""
                self.asignar_btn.setEnabled(estado == "disponible")
                self.liberar_btn.setEnabled(estado == "ocupada")
                self.notificar_btn.setEnabled(True)

    def cargar_todas_camas(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM camas ORDER BY id")
            self.cama_a_modificar.clear()
            self.cama_a_modificar.addItems([str(r[0]) for r in cursor.fetchall()])
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def cargar_camas_operativas(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM camas")
            self.cama_mantenimiento.clear()
            self.cama_mantenimiento.addItems([str(r[0]) for r in cursor.fetchall()])
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def cargar_camas_area(self):
        try:
            area = self.area_combo.currentText()
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.rol in ["admin", "medico", "enfermera"]:
                cursor.execute('''
                    SELECT c.id, c.ubicacion, 
                           CASE 
                               WHEN c.disponible AND COALESCE(lc.limpieza_realizada, TRUE) AND COALESCE(ee.operatividad, TRUE) THEN 'Disponible'
                               WHEN NOT c.disponible THEN 'Ocupada'
                               WHEN NOT COALESCE(lc.limpieza_realizada, TRUE) THEN 'Sucio'
                               WHEN NOT COALESCE(ee.operatividad, TRUE) THEN 'Mantenimiento'
                               ELSE 'No disponible'
                           END as estado,
                           IFNULL(c.paciente_dni, ''), IFNULL(c.paciente_nombre, '')
                    FROM camas c
                    JOIN cama_area ca ON c.id = ca.cama_id
                    JOIN areas a ON ca.area_id = a.id
                    LEFT JOIN limpieza_camas lc ON c.id = lc.cama_id
                    LEFT JOIN estado_equipos ee ON c.id = ee.cama_id
                    WHERE a.nombre = %s
                    ORDER BY c.id
                ''', (area,))
            elif self.rol == "tecnico":
                cursor.execute('''
                    SELECT c.id, c.ubicacion, 
                           CASE 
                               WHEN COALESCE(ee.operatividad, TRUE) THEN 'Operativa' 
                               ELSE 'En mantenimiento' 
                           END as estado,
                           IFNULL(c.paciente_dni, ''), IFNULL(c.paciente_nombre, '')
                    FROM camas c
                    JOIN cama_area ca ON c.id = ca.cama_id
                    JOIN areas a ON ca.area_id = a.id
                    LEFT JOIN estado_equipos ee ON c.id = ee.cama_id
                    WHERE a.nombre = %s
                ''', (area,))
            elif self.rol == "limpieza":
                cursor.execute('''
                    SELECT c.id, c.ubicacion, 
                           CASE 
                               WHEN COALESCE(lc.limpieza_realizada, TRUE) THEN 'Limpia' 
                               ELSE 'Sucia' 
                           END as estado,
                           IFNULL(c.paciente_dni, ''), IFNULL(c.paciente_nombre, '')
                    FROM camas c
                    JOIN cama_area ca ON c.id = ca.cama_id
                    JOIN areas a ON ca.area_id = a.id
                    LEFT JOIN limpieza_camas lc ON c.id = lc.cama_id
                    WHERE a.nombre = %s
                ''', (area,))
            
            rows = cursor.fetchall()
            self.tabla.setRowCount(len(rows))
            self.tabla.setColumnCount(5)
            headers = ["ID", "Ubicación", "Estado", "DNI", "Nombre"]
            self.tabla.setHorizontalHeaderLabels(headers)
            self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            
            for i, fila in enumerate(rows):
                for j, val in enumerate(fila):
                    item = QTableWidgetItem(str(val))
                    
                    # Resaltar estado para todos los roles
                    if j == 2:
                        estado = val
                        if estado == 'Disponible' or estado == 'Operativa' or estado == 'Limpia':
                            item.setBackground(QColor(220, 252, 231))
                            item.setData(Qt.ItemDataRole.UserRole, "disponible")
                        elif estado == 'Ocupada':
                            item.setBackground(QColor(254, 226, 226))
                            item.setData(Qt.ItemDataRole.UserRole, "ocupada")
                        elif estado == 'Sucio' or estado == 'Sucia':
                            item.setBackground(QColor(254, 245, 231))
                            item.setData(Qt.ItemDataRole.UserRole, "sucio")
                        elif estado == 'Mantenimiento' or estado == 'En mantenimiento':
                            item.setBackground(QColor(255, 237, 213))
                            item.setData(Qt.ItemDataRole.UserRole, "mantenimiento")
                        else:
                            item.setBackground(QColor(241, 245, 249))
                            item.setData(Qt.ItemDataRole.UserRole, "no_disponible")
                    
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla.setItem(i, j, item)
            
            # Ajustar tamaño de columnas
            for i in range(4):
                self.tabla.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            self.tabla.resizeRowsToContents()
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def filtrar_tabla(self):
        texto = self.buscador.text().lower()
        for i in range(self.tabla.rowCount()):
            match = False
            for j in range(self.tabla.columnCount()):
                item = self.tabla.item(i, j)
                if item and texto in item.text().lower():
                    match = True
                    break
            self.tabla.setRowHidden(i, not match)

    def asignar_paciente(self):
        if self.rol in ["medico", "enfermera"]:
            row = self.tabla.currentRow()
            if row < 0:
                return
                
            cama_id = self.tabla.item(row, 0).text()
            dni_paciente = self.dni.text()
            nombre_paciente = self.nombre.text()

            if not dni_paciente:
                QMessageBox.warning(self, "DNI requerido", "Debe ingresar el DNI del paciente")
                return

            if not nombre_paciente.strip():
                try:
                    headers = {"Authorization": f"Bearer {API_TOKEN}"}
                    response = requests.get(API_URL + dni_paciente, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        nombre_paciente = f"{data['nombres']} {data['apellidoPaterno']} {data['apellidoMaterno']}"
                        self.nombre.setText(nombre_paciente)
                    else:
                        QMessageBox.warning(self, "Error", "DNI no encontrado o token inválido.")
                        return
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))
                    return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE camas SET disponible = FALSE, paciente_dni = %s, paciente_nombre = %s WHERE id = %s",
                             (dni_paciente, nombre_paciente, cama_id))
                conn.commit()
                self.cargar_camas_area()
                
                # Animación de éxito
                self.tabla.clearSelection()
                self.tabla.selectRow(row)
                
                QMessageBox.information(self, "Éxito", "Paciente asignado correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def liberar_cama(self):
        if self.rol in ["medico", "enfermera"]:
            row = self.tabla.currentRow()
            if row < 0:
                return
                
            cama_id = self.tabla.item(row, 0).text()
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE camas SET disponible = TRUE, paciente_dni = NULL, paciente_nombre = NULL WHERE id = %s",
                             (cama_id,))
                
                # Marcar cama como sucia
                cursor.execute("REPLACE INTO limpieza_camas (cama_id, limpieza_realizada) VALUES (%s, FALSE)", (cama_id,))
                
                conn.commit()
                self.cargar_camas_area()
                
                # Animación de éxito
                self.tabla.clearSelection()
                self.tabla.selectRow(row)
                
                QMessageBox.information(self, "Éxito", "Cama liberada y marcada como sucia")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def crear_cama(self):
        if self.rol == "admin":
            cama_id = self.nueva_cama_id.text()
            ubicacion = self.nueva_cama_ubicacion.text()
            area = self.area_combo.currentText()
            
            if not cama_id or not ubicacion:
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
                return
                
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute("INSERT INTO camas (id, ubicacion, disponible) VALUES (%s, %s, TRUE)", 
                             (cama_id, ubicacion))
                
                cursor.execute("SELECT id FROM areas WHERE nombre = %s", (area,))
                area_id = cursor.fetchone()[0]
                
                cursor.execute("INSERT INTO cama_area (cama_id, area_id) VALUES (%s, %s)", 
                             (cama_id, area_id))
                
                conn.commit()
                
                # Animación de éxito
                anim = QPropertyAnimation(self.nueva_cama_id, b"geometry")
                anim.setDuration(300)
                anim.setEasingCurve(QEasingCurve.Type.OutBack)
                anim.setStartValue(QRect(self.nueva_cama_id.x(), self.nueva_cama_id.y(), 
                                         self.nueva_cama_id.width(), self.nueva_cama_id.height()))
                anim.setEndValue(QRect(self.nueva_cama_id.x(), self.nueva_cama_id.y(), 
                                       self.nueva_cama_id.width(), self.nueva_cama_id.height()))
                anim.start()
                
                QMessageBox.information(self, "Éxito", "Cama creada y asignada al área correctamente")
                self.cargar_todas_camas()
                self.cargar_camas_area()
                self.nueva_cama_id.clear()
                self.nueva_cama_ubicacion.clear()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def modificar_cama(self):
        if self.rol == "admin":
            cama_actual = self.cama_a_modificar.currentText()
            nuevo_id = self.nuevo_id_cama.text()
            nueva_ubicacion = self.nueva_ubicacion.text()
            
            if not nuevo_id and not nueva_ubicacion:
                QMessageBox.warning(self, "Error", "Debe proporcionar al menos un campo a modificar")
                return
                
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                if nuevo_id and nueva_ubicacion:
                    cursor.execute("UPDATE camas SET id = %s, ubicacion = %s WHERE id = %s", 
                                 (nuevo_id, nueva_ubicacion, cama_actual))
                elif nuevo_id:
                    cursor.execute("UPDATE camas SET id = %s WHERE id = %s", 
                                 (nuevo_id, cama_actual))
                else:
                    cursor.execute("UPDATE camas SET ubicacion = %s WHERE id = %s", 
                                 (nueva_ubicacion, cama_actual))
                    
                conn.commit()
                
                # Animación de éxito
                anim = QPropertyAnimation(self.cama_a_modificar, b"geometry")
                anim.setDuration(300)
                anim.setEasingCurve(QEasingCurve.Type.OutBack)
                anim.setStartValue(QRect(self.cama_a_modificar.x(), self.cama_a_modificar.y(), 
                                         self.cama_a_modificar.width(), self.cama_a_modificar.height()))
                anim.setEndValue(QRect(self.cama_a_modificar.x(), self.cama_a_modificar.y(), 
                                       self.cama_a_modificar.width(), self.cama_a_modificar.height()))
                anim.start()
                
                QMessageBox.information(self, "Éxito", "Cama modificada correctamente")
                self.cargar_todas_camas()
                self.cargar_camas_area()
                self.nuevo_id_cama.clear()
                self.nueva_ubicacion.clear()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def cama_seleccionada(self):
        row = self.tabla.currentRow()
        if row >= 0:
            return self.tabla.item(row, 0).text()
        return None

    def limpiar(self):
        if self.rol == "limpieza":
            cama_id = self.cama_seleccionada()
            if not cama_id:
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("REPLACE INTO limpieza_camas (cama_id, limpieza_realizada) VALUES (%s, TRUE)", (cama_id,))
                conn.commit()
                
                # Animación de éxito
                row = self.tabla.currentRow()
                self.tabla.clearSelection()
                self.tabla.selectRow(row)
                
                QMessageBox.information(self, "Éxito", "Cama marcada como limpia")
                self.cargar_camas_area()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def operatividad(self):
        if self.rol == "tecnico":
            cama_id = self.cama_seleccionada()
            if not cama_id:
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT operatividad FROM estado_equipos WHERE cama_id = %s", (cama_id,))
                actual = cursor.fetchone()
                nuevo_estado = not actual[0] if actual else True
                cursor.execute("REPLACE INTO estado_equipos (cama_id, operatividad) VALUES (%s, %s)", (cama_id, nuevo_estado))
                conn.commit()
                
                # Animación de éxito
                row = self.tabla.currentRow()
                self.tabla.clearSelection()
                self.tabla.selectRow(row)
                
                estado = "operativa" if nuevo_estado else "en mantenimiento"
                QMessageBox.information(self, "Éxito", f"Estado de la cama actualizado a {estado}")
                self.cargar_camas_area()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def programar_mantenimiento(self):
        if self.rol == "tecnico":
            cama_id = self.cama_mantenimiento.currentText()
            fecha = self.fecha_mantenimiento.date().toString("yyyy-MM-dd")
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mantenimiento_programado (cama_id, fecha, completado)
                    VALUES (%s, %s, FALSE)
                """, (cama_id, fecha))
                conn.commit()
                
                QMessageBox.information(self, "Éxito", "Mantenimiento programado correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
            
    def notificar_problema(self):
        cama_id = self.cama_seleccionada()
        if not cama_id:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Reportar Problema")
        dialog.setMinimumSize(500, 350)
        
        layout = QVBoxLayout(dialog)
        
        # Información de la cama
        cama_info = QLabel(f"Cama #{cama_id} - {self.tabla.item(self.tabla.currentRow(), 1).text()}")
        cama_info.setStyleSheet("font-weight: 700; font-size: 16px; margin-bottom: 15px;")
        
        # Selección de tipo de problema
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.tipo_problema = QComboBox()
        self.tipo_problema.addItems([
            "Problema técnico", 
            "Requiere limpieza especial", 
            "Daño en equipos",
            "Falta de suministros"
        ])
        
        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setPlaceholderText("Describa el problema en detalle...")
        self.descripcion_edit.setMinimumHeight(120)
        
        form_layout.addRow(QLabel("Tipo de problema:"), self.tipo_problema)
        form_layout.addRow(QLabel("Descripción:"), self.descripcion_edit)
        
        layout.addWidget(cama_info)
        layout.addLayout(form_layout)
        
        # Botones
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(lambda: self.enviar_notificacion(cama_id, dialog))
        btn_box.rejected.connect(dialog.reject)
        
        layout.addWidget(btn_box)
        dialog.exec()
        
    def enviar_notificacion(self, cama_id, dialog):
        tipo_problema = self.tipo_problema.currentText()
        mensaje = self.descripcion_edit.toPlainText()
        
        if not mensaje.strip():
            QMessageBox.warning(self, "Error", "Debe escribir una descripción")
            return
            
        destinatario = "tecnico" if "técnico" in tipo_problema or "equipos" in tipo_problema else "limpieza"
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notificaciones (cama_id, remitente, destinatario_rol, tipo_problema, mensaje, fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cama_id, self.nombre_completo, destinatario, tipo_problema, mensaje, datetime.now()))
            conn.commit()
            
            QMessageBox.information(self, "Éxito", "Notificación enviada correctamente")
            dialog.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo enviar la notificación: {str(e)}")

# --------------------- Panel de Notificaciones ---------------------
class PanelNotificaciones(QWidget):
    def __init__(self, rol, nombre_completo):
        super().__init__()
        self.rol = rol
        self.nombre_completo = nombre_completo
        self.setup_ui()
        self.cargar_notificaciones()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Título del panel
        title = QLabel("Gestión de Notificaciones")
        title.setObjectName("etiquetaSeccion")
        layout.addWidget(title)

        # Filtros y controles
        control_layout = QHBoxLayout()
        
        # Filtro para mostrar/no mostrar resueltas (solo para admin)
        if self.rol == "admin":
            self.filtro_resueltas = QCheckBox("Mostrar notificaciones resueltas")
            self.filtro_resueltas.stateChanged.connect(self.cargar_notificaciones)
            control_layout.addWidget(self.filtro_resueltas)
        
        control_layout.addStretch()
        
        # Botón de actualizar
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setObjectName("botonSecundario")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.clicked.connect(self.cargar_notificaciones)
        control_layout.addWidget(refresh_btn)
        
        layout.addLayout(control_layout)

        # Tabla de notificaciones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)  # Reducido a 7 columnas (sin columna de estado)
        headers = ["ID", "Cama", "Remitente", "Destinatario", "Tipo Problema", "Mensaje", "Acción"]
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSortingEnabled(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Ajustar tamaño de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Cama
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Remitente
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Destinatario
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)          # Tipo Problema
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)          # Mensaje
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents) # Acción
        
        layout.addWidget(self.tabla, 1)

    def cargar_notificaciones(self):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if self.rol == "admin":
                if hasattr(self, 'filtro_resueltas') and self.filtro_resueltas.isChecked():
                    cursor.execute("SELECT * FROM notificaciones ORDER BY fecha DESC")
                else:
                    cursor.execute("SELECT * FROM notificaciones WHERE resuelta = FALSE ORDER BY fecha DESC")
            else:
                cursor.execute("""
                    SELECT * FROM notificaciones 
                    WHERE (remitente = %s OR destinatario_rol = %s) 
                    AND resuelta = FALSE
                    ORDER BY fecha DESC
                """, (self.nombre_completo, self.rol))
            
            self.tabla.setRowCount(0)
            
            for notif in cursor:
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                
                # Llenar datos de la notificación
                self.tabla.setItem(row, 0, QTableWidgetItem(str(notif['id'])))
                self.tabla.setItem(row, 1, QTableWidgetItem(str(notif['cama_id'])))
                self.tabla.setItem(row, 2, QTableWidgetItem(notif['remitente']))
                self.tabla.setItem(row, 3, QTableWidgetItem(notif['destinatario_rol']))
                self.tabla.setItem(row, 4, QTableWidgetItem(notif['tipo_problema']))
                self.tabla.setItem(row, 5, QTableWidgetItem(notif['mensaje']))
                
                # Solo mostrar botón de resolver si es una notificación pendiente
                if not notif['resuelta']:
                    btn_resolver = QPushButton("Resolver")
                    btn_resolver.setObjectName("botonExito")
                    btn_resolver.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_resolver.clicked.connect(lambda _, id=notif['id']: self.resolver_notificacion(id))
                    self.tabla.setCellWidget(row, 6, btn_resolver)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las notificaciones: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def resolver_notificacion(self, notificacion_id):
        try:
            # Confirmar con el usuario
            respuesta = QMessageBox.question(
                self,
                "Confirmar resolución",
                "¿Está seguro que desea resolver y eliminar esta notificación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Eliminar la notificación completamente
                cursor.execute("DELETE FROM notificaciones WHERE id = %s", (notificacion_id,))
                conn.commit()
                
                # Actualizar la tabla
                self.cargar_notificaciones()
                
                QMessageBox.information(self, "Éxito", "Notificación resuelta y eliminada correctamente")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo resolver la notificación: {str(e)}")
        finally:
            cursor.close()
            conn.close()
# --------------------- Ejecución ---------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    aplicar_estilos(app)
    
    # Crear gradiente de fondo para la aplicación
    palette = QPalette()
    gradient = QLinearGradient(0, 0, 0, 400)
    gradient.setColorAt(0, QColor(241, 245, 249))
    gradient.setColorAt(1, QColor(226, 232, 240))
    palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
    app.setPalette(palette)
    
    login = Login()
    login.show()
    sys.exit(app.exec())
