import sys
import os
import pandas as pd
import mysql.connector
import requests
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox,
                               QSpacerItem, QSizePolicy, QFrame, QProgressBar,
                               QMessageBox, QFileDialog, QTabWidget, QTextEdit,
                               QListWidget, QListWidgetItem, QStatusBar)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QAction, QPixmap, QIcon

# ================================
# CONFIGURACIÓN DE LA API DE SMS
# ================================
SMS_API_TOKEN = "sebastian.gomez@teleton.org.mx:kH9PwbqXKyoegTcOZiNrrv8nf5Y0qqpB"
SMS_REMITENTE = "CRIT"
SMS_MODO_PRUEBA = False
SMS_API_URL = "https://api.labsmobile.com/json/send"

# ================================
# CARGA DE ESTILOS QSS DEL TELETÓN
# ================================

def load_teleton_styles(app):
    """
    Carga los estilos QSS oficiales del Teletón.

    Incluye:
    - Colores corporativos (morado #8E44AD, amarillo #FDD835)
    - Gradientes y efectos visuales
    - Estilos para todos los widgets de Qt
    - Componentes específicos del Teletón
    """
    qss_path = Path(__file__).parent / 'style.qss'

    if qss_path.exists():
        try:
            with open(qss_path, 'r', encoding='utf-8') as qss_file:
                styles = qss_file.read()
                app.setStyleSheet(styles)
                print("✓ Estilos QSS del Teletón cargados correctamente")
                print("  - Colores corporativos aplicados: morado #8E44AD, amarillo #FDD835")
                print("  - Gradientes y efectos visuales habilitados")
                print("  - Componentes del Teletón estilizados")
                return True
        except Exception as e:
            print(f"⚠️ Error cargando style.qss: {e}")
            return False
    else:
        print(f"⚠️ Archivo style.qss no encontrado en: {qss_path}")
        print("   Coloca el archivo style.qss en la misma carpeta que main.py")
        return False

def apply_fallback_teleton_styles(app):
    """
    Aplica estilos básicos del Teletón si no se encuentra el archivo QSS.
    """
    basic_teleton_styles = """
    /* Estilos básicos del Teletón si no se encuentra style.qss */
    QMainWindow {
        background-color: #f8f9fa;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 10pt;
    }

    QWidget {
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 10pt;
        color: #2c3e50;
    }

    QPushButton {
        background-color: #8E44AD;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 10pt;
    }

    QPushButton:hover {
        background-color: #6B2C91;
    }

    QPushButton:pressed {
        background-color: #5A1F7A;
    }

    QPushButton:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }

    QLineEdit {
        border: 2px solid rgba(142, 68, 173, 0.2);
        border-radius: 8px;
        padding: 8px 12px;
        background-color: white;
        font-size: 10pt;
    }

    QLineEdit:focus {
        border-color: #8E44AD;
    }

    QTabWidget::pane {
        border: 2px solid rgba(142, 68, 173, 0.2);
        border-radius: 8px;
        background-color: white;
    }

    QTabBar::tab {
        background-color: #ecf0f1;
        color: #2c3e50;
        padding: 12px 24px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
    }

    QTabBar::tab:selected {
        background-color: #8E44AD;
        color: white;
    }

    QProgressBar {
        border: 2px solid rgba(142, 68, 173, 0.2);
        border-radius: 8px;
        background-color: #ecf0f1;
        text-align: center;
        font-weight: bold;
        height: 20px;
    }

    QProgressBar::chunk {
        background-color: #8E44AD;
        border-radius: 6px;
    }
    """

    app.setStyleSheet(basic_teleton_styles)
    print("✓ Estilos básicos del Teletón aplicados como fallback")

# ================================
# CÓDIGO DE LIMPIEZA DEL TELETÓN
# ================================

def conectar(host, user, password, database):
    """Función original del código del Teletón para conectar a MySQL."""
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conexion.is_connected():
            print("Conexión exitosa")
            return conexion
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def cerrar(conexion):
    """Función original del código del Teletón para cerrar conexión."""
    if conexion.is_connected():
        conexion.close()
        print("Conexión cerrada")

def obtener_o_insertar_id(cursor, tabla, columna, valor):
    """Función original del código del Teletón para obtener o insertar IDs."""
    cursor.execute(f"SELECT id FROM {tabla} WHERE {columna} = %s", (valor,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(f"INSERT INTO {tabla} ({columna}) VALUES (%s)", (valor,))
        return cursor.lastrowid
    else:
        return result[0]


def insertar_citas(ruta_excel, connection):
    """Función para insertar citas desde un archivo Excel a la base de datos."""
    if connection is None:
        return False, "No hay conexión a la base de datos"

    try:
        cursor = connection.cursor()

        # Limpiar toda la base antes de insertar
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Cita;")
        cursor.execute("TRUNCATE TABLE Paciente;")
        cursor.execute("TRUNCATE TABLE Colaborador;")
        cursor.execute("TRUNCATE TABLE Servicio;")
        cursor.execute("TRUNCATE TABLE Clinica;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Base de datos limpiada.")

        # Cargar Excel
        df = pd.read_excel(ruta_excel)

        # Validar columnas requeridas
        required_columns = ['Colaborador', 'Servicio', 'Paciente', 'Carnet', 'Clínica', 'Fecha', 'Hora', 'Sesión',
                            'Capacidad', 'Ocupación', 'Estatus', 'Telefono']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Faltan columnas requeridas en el archivo Excel: {', '.join(missing_columns)}")

        # Función para parsear fechas
        def parse_date(date_value):
            """Intenta parsear una fecha en múltiples formatos."""
            if isinstance(date_value, pd.Timestamp) or isinstance(date_value, datetime):
                return date_value.date()

            date_str = str(date_value).strip()
            # Eliminar el nombre del día si está presente (e.g., "Miércoles 27/08/2025" -> "27/08/2025")
            if ' ' in date_str:
                date_str = date_str.split(' ', 1)[-1].strip()

            # Lista de formatos posibles
            date_formats = [
                '%d/%m/%Y',  # 27/08/2025
                '%Y-%m-%d',  # 2025-08-27
                '%m/%d/%Y',  # 08/27/2025
                '%d-%m-%Y',  # 27-08-2025
            ]

            for fmt in date_formats:
                try:
                    return pd.to_datetime(date_str, format=fmt, dayfirst=True).date()
                except ValueError:
                    continue

            raise ValueError(f"Formato de fecha no reconocido: {date_str}")

        # Insertar datos
        records_processed = 0
        for idx, row in df.iterrows():
            try:
                colaborador = row['Colaborador']
                servicio = row['Servicio']
                paciente_nombre = row['Paciente']
                paciente_carnet = int(row['Carnet'])
                clinica = row['Clínica']

                # Parsear fecha
                fecha = parse_date(row['Fecha'])

                # Parsear hora
                hora_str = str(row['Hora']).strip()
                try:
                    hora = pd.to_datetime(hora_str).time()
                except ValueError:
                    # Intentar parsear hora en formato HH:MM o HH:MM:SS
                    hora_formats = ['%H:%M', '%H:%M:%S']
                    for fmt in hora_formats:
                        try:
                            hora = datetime.strptime(hora_str, fmt).time()
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError(f"Formato de hora no reconocido en la fila {idx + 2}: {hora_str}")

                sesion = row['Sesión']
                capacidad = int(row['Capacidad'])
                ocupacion = int(row['Ocupación'])
                estatus = row['Estatus']
                telefono = str(row['Telefono']) if pd.notna(row['Telefono']) else None

                colaborador_id = obtener_o_insertar_id(cursor, 'Colaborador', 'Nombre', colaborador)
                servicio_id = obtener_o_insertar_id(cursor, 'Servicio', 'Nombre', servicio)
                clinica_id = obtener_o_insertar_id(cursor, 'Clinica', 'Nombre', clinica)

                cursor.execute("SELECT id FROM Paciente WHERE Carnet = %s", (paciente_carnet,))
                paciente_result = cursor.fetchone()
                if paciente_result is None:
                    cursor.execute("""
                        INSERT INTO Paciente (Carnet, Nombre, Telefono)
                        VALUES (%s, %s, %s)
                    """, (paciente_carnet, paciente_nombre, telefono))
                    paciente_id = cursor.lastrowid
                else:
                    paciente_id = paciente_result[0]

                cursor.execute("""
                    INSERT INTO Cita (Colaborador_ID, Servicio_ID, Paciente_ID, Clinica_ID, Fecha, Hora, Sesion, Capacidad, Ocupacion, Estatus)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    colaborador_id, servicio_id, paciente_id, clinica_id, fecha, hora,
                    sesion, capacidad, ocupacion, estatus
                ))

                records_processed += 1

            except Exception as e:
                print(f"Error procesando la fila {idx + 2}: {str(e)}")
                continue

        connection.commit()
        print("Datos insertados correctamente.")
        return True, f"Se procesaron {records_processed} registros correctamente"

    except Exception as e:
        print(f"Error en insertar_citas: {e}")
        connection.rollback()
        return False, f"Error procesando archivo: {str(e)}"
# ================================
# CÓDIGO DE EXTRACCIÓN DEL TELETÓN
# ================================

def obtener_conexion(config):
    """Función original del código del Teletón para obtener conexión."""
    return mysql.connector.connect(**config)

def extraer_citas_completas(conn):
    """Función original del código del Teletón para extraer citas."""
    consulta = """
        SELECT 
            pa.Nombre AS Paciente,
            pa.Telefono,
            ci.Fecha,
            ci.Hora,
            ser.Nombre AS Servicio,
            col.Nombre AS Colaborador
        FROM Cita ci
        JOIN Colaborador col ON ci.Colaborador_ID = col.id
        JOIN Servicio ser ON ci.Servicio_ID = ser.id
        JOIN Paciente pa ON ci.Paciente_ID = pa.id
        WHERE ci.Fecha = CURDATE() + INTERVAL 1 DAY
    """

    cursor = conn.cursor()
    cursor.execute(consulta)
    columnas = [desc[0] for desc in cursor.description]
    datos = cursor.fetchall()
    cursor.close()

    df = pd.DataFrame(datos, columns=columnas)

    # Formatear hora
    if not df.empty and 'Hora' in df.columns:
        df["Hora"] = df["Hora"].apply(lambda x: str(x)[-8:] if x else "")

    return df

# ================================
# CÓDIGO DE ENVÍO DE SMS
# ================================

def enviar_sms(nombre, telefono, fecha, hora, servicio, colaborador):
    """Envía un SMS usando la API de LabsMobile."""
    mensaje = (
        f"Hola {nombre}, te recordamos tu cita de {servicio} "
        f"con {colaborador} el {fecha} a las {hora}. Gracias por confiar en nosotros."
    )

    credentials = base64.b64encode(SMS_API_TOKEN.encode()).decode()

    payload = json.dumps({
        "message": mensaje,
        "tpoa": SMS_REMITENTE,
        "recipient": [
            {"msisdn": telefono}
        ]
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {credentials}',
        'Cache-Control': "no-cache"
    }

    try:
        response = requests.post(SMS_API_URL, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"[✓] SMS enviado a {nombre} ({telefono}): {response.text}")
            return True, f"SMS enviado a {nombre} ({telefono})"
        else:
            print(f"[✗] Error al enviar a {nombre} ({telefono}): {response.text}")
            return False, f"Error al enviar a {nombre} ({telefono}): {response.text}"
    except Exception as e:
        print(f"[✗] Excepción al enviar a {nombre} ({telefono}): {str(e)}")
        return False, f"Error al enviar a {nombre} ({telefono}): {str(e)}"

# ================================
# UTILIDADES PARA CARGAR IMÁGENES
# ================================

def load_logo(image_path: str, size: tuple = (60, 60), fallback_text: str = "🤝") -> QLabel:
    """
    Carga un logo desde un archivo de imagen o usa texto como fallback.
    """
    label = QLabel()
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    if os.path.exists(image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    size[0], size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)
                return label
        except Exception as e:
            print(f"Error cargando imagen {image_path}: {e}")

    label.setText(fallback_text)
    label.setStyleSheet(f"""
        QLabel {{
            font-size: {int(size[1] * 0.4)}px;
            background: transparent;
            border: none;
        }}
    """)

    return label

def get_asset_path(filename: str) -> str:
    """
    Obtiene la ruta completa a un archivo en la carpeta assets.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "assets", filename)

# ================================
# CLASES DE THREADS PARA OPERACIONES ASÍNCRONAS
# ================================

class DatabaseCleaningThread(QThread):
    """Thread para limpieza de base de datos sin bloquear la UI."""
    cleaning_progress = Signal(int)  # progress percentage
    cleaning_finished = Signal(bool, str, int)  # success, message, records_count

    def __init__(self, file_path: str, host: str, user: str, password: str, database: str):
        super().__init__()
        self.file_path = file_path
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def run(self):
        """Ejecuta la limpieza de base de datos."""
        try:
            for i in range(0, 90, 10):
                self.cleaning_progress.emit(i)
                self.msleep(200)

            connection = conectar(self.host, self.user, self.password, self.database)

            if connection is None:
                self.cleaning_finished.emit(False, "No se pudo conectar a la base de datos", 0)
                return

            success, message = insertar_citas(self.file_path, connection)

            records_count = 0
            if success and "Se procesaron" in message:
                try:
                    records_count = int(message.split()[2])
                except:
                    records_count = 0

            cerrar(connection)

            self.cleaning_progress.emit(100)
            self.cleaning_finished.emit(success, message, records_count)

        except Exception as e:
            self.cleaning_finished.emit(False, f"Error inesperado: {str(e)}", 0)

class DataExtractionThread(QThread):
    """Thread para extracción de datos sin bloquear la UI."""
    extraction_progress = Signal(int)  # progress percentage
    extraction_finished = Signal(bool, str, str, int)  # success, message, output_file, records_count

    def __init__(self, host: str, user: str, password: str, database: str):
        super().__init__()
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def run(self):
        """Ejecuta la extracción de datos."""
        try:
            for i in range(0, 90, 15):
                self.extraction_progress.emit(i)
                self.msleep(300)

            config = {
                "user": self.user,
                "password": self.password,
                "host": self.host,
                "database": self.database
            }

            conn = obtener_conexion(config)
            df_citas = extraer_citas_completas(conn)
            conn.close()

            if df_citas.empty:
                self.extraction_progress.emit(100)
                self.extraction_finished.emit(True, "No se encontraron citas para mañana", "", 0)
                return

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"citas_teleton_{timestamp}.csv"

            df_citas.to_csv(output_path, index=False, encoding="utf-8-sig")

            self.extraction_progress.emit(100)
            self.extraction_finished.emit(
                True,
                f"Datos extraídos correctamente. {len(df_citas)} citas encontradas.",
                output_path,
                len(df_citas)
            )

        except Exception as e:
            self.extraction_finished.emit(False, f"Error inesperado: {str(e)}", "", 0)

class SMSSendingThread(QThread):
    """Thread para enviar SMS sin bloquear la UI."""
    sms_progress = Signal(int)  # progress percentage
    sms_finished = Signal(bool, str, int, int)  # success, message, sent_count, failed_count

    def __init__(self, csv_file: str):
        super().__init__()
        self.csv_file = csv_file

    def run(self):
        """Ejecuta el envío de SMS."""
        try:
            df = pd.read_csv(self.csv_file, encoding="utf-8-sig")
            total_records = len(df)
            sent_count = 0
            failed_count = 0

            for idx, row in df.iterrows():
                nombre = row["Paciente"]
                telefono = str(row["Telefono"]).strip().replace(" ", "")
                fecha = row["Fecha"]
                hora = row["Hora"]
                servicio = row["Servicio"]
                colaborador = row["Colaborador"]

                if pd.notna(telefono) and telefono.strip() != "":
                    success, message = enviar_sms(nombre, telefono, fecha, hora, servicio, colaborador)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                else:
                    print(f"[!] Teléfono no válido para {nombre}. No se envió SMS.")
                    failed_count += 1

                self.sms_progress.emit(int((idx + 1) / total_records * 100))
                self.msleep(100)  # Pequeña pausa para evitar sobrecarga de la API

            self.sms_finished.emit(
                True,
                f"Envío de SMS completado. Enviados: {sent_count}, Fallidos: {failed_count}",
                sent_count,
                failed_count
            )

        except Exception as e:
            self.sms_finished.emit(False, f"Error inesperado al enviar SMS: {str(e)}", 0, 0)

# ================================
# CLASES DE INTERFAZ DE USUARIO
# ================================

class DatabaseCredentials:
    """Modelo para almacenar credenciales de la base de datos."""
    def __init__(self, user: str, password: str, host: str, database: str):
        self.user = user
        self.password = password
        self.host = host
        self.database = database

class DatabaseConnectionWidget(QWidget):
    """Widget para la conexión a la base de datos con diseño del Teletón."""
    connection_successful = Signal(DatabaseCredentials)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setObjectName("connection_widget")

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        central_container = QWidget()
        central_container.setMaximumWidth(500)
        central_container.setMinimumWidth(400)
        central_container.setObjectName("connection_form")

        central_layout = QVBoxLayout(central_container)
        central_layout.setSpacing(30)

        header_widget = self.create_header()
        central_layout.addWidget(header_widget)

        connection_card = self.create_connection_card()
        central_layout.addWidget(connection_card)

        h_layout = QHBoxLayout()
        h_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        h_layout.addWidget(central_container)
        h_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        layout.addLayout(h_layout)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def create_header(self):
        """Crea el header con los logos del Teletón."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(20)

        logo_container = QFrame()
        logo_container.setFixedSize(140, 140)
        logo_container.setObjectName("logo_container")

        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(10, 10, 10, 10)

        teleton_logo_path = get_asset_path("teleton_logo.png")
        logo_label = load_logo(teleton_logo_path, (120, 120), "🤝")
        logo_layout.addWidget(logo_label)

        logo_h_layout = QHBoxLayout()
        logo_h_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        logo_h_layout.addWidget(logo_container)
        logo_h_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header_layout.addLayout(logo_h_layout)

        title_label = QLabel("Sistema de Mensajería SMS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title_label")
        header_layout.addWidget(title_label)

        capacidad_logo_path = get_asset_path("capacidad_logo.png")
        capacidad_logo_label = load_logo(capacidad_logo_path, (200, 40), "Capacidad Sin Límites")
        capacidad_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(capacidad_logo_label)

        subtitle_label = QLabel("Fundación Teletón México")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)

        return header_widget

    def create_connection_card(self):
        """Crea la tarjeta de conexión a la base de datos."""
        card = QGroupBox("🔌 Conexión a Base de Datos")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        desc_label = QLabel("Configura la conexión a MySQL para continuar")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        self.user_input = self.create_input_field("Usuario", "root")
        self.password_input = self.create_input_field("Contraseña", "", password=True)
        self.host_input = self.create_input_field("Host", "localhost")
        self.database_input = self.create_input_field("Base de Datos", "Crit_data")

        layout.addWidget(self.user_input[0])
        layout.addWidget(self.user_input[1])
        layout.addWidget(self.password_input[0])
        layout.addWidget(self.password_input[1])
        layout.addWidget(self.host_input[0])
        layout.addWidget(self.host_input[1])
        layout.addWidget(self.database_input[0])
        layout.addWidget(self.database_input[1])

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        self.connect_button = QPushButton("Conectar a Base de Datos")
        self.connect_button.clicked.connect(self.test_connection)
        self.connect_button.setObjectName("connect_button")
        layout.addWidget(self.connect_button)

        return card

    def create_input_field(self, label_text, default_value="", password=False):
        """Crea un campo de entrada con su etiqueta."""
        label = QLabel(label_text)

        input_field = QLineEdit()
        input_field.setText(default_value)
        if password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)

        return label, input_field

    def test_connection(self):
        """Prueba la conexión a la base de datos."""
        try:
            connection = conectar(
                host=self.host_input[1].text().strip(),
                user=self.user_input[1].text().strip(),
                password=self.password_input[1].text().strip(),
                database=self.database_input[1].text().strip()
            )

            if connection:
                cerrar(connection)
                credentials = DatabaseCredentials(
                    user=self.user_input[1].text().strip(),
                    password=self.password_input[1].text().strip(),
                    host=self.host_input[1].text().strip(),
                    database=self.database_input[1].text().strip()
                )

                self.show_status_message("¡Conexión exitosa! Redirigiendo...", "success")
                QTimer.singleShot(1500, lambda: self.connection_successful.emit(credentials))
            else:
                self.show_status_message("Error de conexión. Verifica los datos.", "error")

        except Exception as e:
            self.show_status_message(f"Error: {str(e)}", "error")

    def show_status_message(self, message, status_type):
        """Muestra un mensaje de estado."""
        self.status_label.setText(message)
        self.status_label.setVisible(True)

        if status_type == "success":
            self.status_label.setObjectName("status_label")
            icon = "✓"
        else:  # error
            self.status_label.setObjectName("error_label")
            icon = "✗"

        self.status_label.setText(f"{icon} {message}")

class SMSManagerWidget(QWidget):
    """Widget principal para el manejo de SMS con diseño del Teletón."""
    disconnect_requested = Signal()

    def __init__(self):
        super().__init__()
        self.credentials = None
        self.selected_file = None
        self.extracted_csv_file = None
        self.stats = {
            'files_loaded': [],
            'total_records': 0,
            'tomorrow_appointments': 0,
            'sms_sent': 0
        }

        self.cleaning_thread = None
        self.extraction_thread = None
        self.sms_thread = None

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self.create_header()
        layout.addWidget(header)

        main_content = QWidget()
        main_layout = QHBoxLayout(main_content)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        main_panel = self.create_main_panel()
        main_layout.addWidget(main_panel, 2)

        stats_panel = self.create_stats_panel()
        main_layout.addWidget(stats_panel, 1)

        layout.addWidget(main_content)

        footer = self.create_footer()
        layout.addWidget(footer)

    def create_header(self):
        """Crea el header con branding oficial del Teletón."""
        header = QFrame()
        header.setMinimumHeight(80)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)

        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)

        teleton_logo_path = get_asset_path("teleton_logo.png")
        header_logo_label = load_logo(teleton_logo_path, (50, 50), "🤝")
        left_layout.addWidget(header_logo_label)

        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title_label = QLabel("Sistema SMS Teletón ⭐")
        title_label.setObjectName("title_label")
        title_layout.addWidget(title_label)

        self.connection_label = QLabel("Conectado a: -")
        title_layout.addWidget(self.connection_label)

        left_layout.addWidget(title_section)

        layout.addWidget(left_section)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        capacidad_logo_path = get_asset_path("capacidad_logo.png")
        capacidad_header_label = load_logo(capacidad_logo_path, (120, 20), "Capacidad Sin Límites")
        right_layout.addWidget(capacidad_header_label)

        disconnect_button = QPushButton("🔌 Desconectar")
        disconnect_button.clicked.connect(self.disconnect_requested.emit)
        disconnect_button.setObjectName("secondary_button")
        right_layout.addWidget(disconnect_button)

        layout.addWidget(right_section)

        return header

    def create_main_panel(self):
        """Crea el panel principal con pestañas."""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.tab_widget = QTabWidget()

        upload_tab = self.create_upload_tab()
        self.tab_widget.addTab(upload_tab, "📁 Cargar Datos")

        process_tab = self.create_process_tab()
        self.tab_widget.addTab(process_tab, "⚙️ Procesar")

        layout.addWidget(self.tab_widget)

        self.progress_container = self.create_progress_container()
        layout.addWidget(self.progress_container)

        return main_widget

    def create_upload_tab(self):
        """Crea la pestaña de carga de archivos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        card = QGroupBox("📁 Cargar Archivo Excel del Teletón")

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        desc_label = QLabel("Selecciona el archivo Excel con las citas del Teletón (.xlsx)")
        card_layout.addWidget(desc_label)

        info_label = QLabel(
            "Columnas requeridas: Colaborador, Servicio, Paciente, Carnet, Clínica, Fecha, Hora, Sesión, Capacidad, Ocupación, Estatus, Telefono")
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)

        file_button_layout = QHBoxLayout()

        self.select_file_button = QPushButton("📄 Seleccionar Archivo Excel")
        self.select_file_button.clicked.connect(self.select_file)
        self.select_file_button.setObjectName("file_button")
        file_button_layout.addWidget(self.select_file_button)

        self.file_label = QLabel("Ningún archivo seleccionado")
        file_button_layout.addWidget(self.file_label)

        card_layout.addLayout(file_button_layout)

        self.clean_button = QPushButton("⚙️ Limpiar Base de Datos y Cargar Citas")
        self.clean_button.clicked.connect(self.clean_database)
        self.clean_button.setEnabled(False)
        self.clean_button.setObjectName("primary_button")
        card_layout.addWidget(self.clean_button)

        layout.addWidget(card)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return tab

    def create_process_tab(self):
        """Crea la pestaña de procesamiento."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        card = QGroupBox("💾 Procesamiento de Citas")

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        desc_label = QLabel(
            "Extrae las citas del día siguiente y envía recordatorios SMS a los pacientes")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        query_info = QLabel("La consulta incluye: Nombre del Paciente, Teléfono, Fecha, Hora, Servicio y Colaborador")
        query_info.setWordWrap(True)
        card_layout.addWidget(query_info)

        self.extract_button = QPushButton("💾 Extraer Citas de Mañana a CSV")
        self.extract_button.clicked.connect(self.extract_data)
        self.extract_button.setEnabled(False)
        self.extract_button.setObjectName("secondary_button")
        card_layout.addWidget(self.extract_button)

        self.send_sms_button = QPushButton("📱 Enviar Recordatorios SMS")
        self.send_sms_button.clicked.connect(self.send_sms)
        self.send_sms_button.setEnabled(False)
        self.send_sms_button.setObjectName("secondary_button")
        card_layout.addWidget(self.send_sms_button)

        self.csv_info_label = QLabel("")
        self.csv_info_label.setVisible(False)
        self.csv_info_label.setWordWrap(True)
        self.csv_info_label.setObjectName("status_label")
        card_layout.addWidget(self.csv_info_label)

        self.sms_info_label = QLabel("")
        self.sms_info_label.setVisible(False)
        self.sms_info_label.setWordWrap(True)
        self.sms_info_label.setObjectName("status_label")
        card_layout.addWidget(self.sms_info_label)

        layout.addWidget(card)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return tab

    def create_progress_container(self):
        """Crea el contenedor de la barra de progreso."""
        container = QGroupBox()
        container.setVisible(False)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        status_layout = QHBoxLayout()

        self.progress_status_label = QLabel("")
        self.progress_status_label.setObjectName("section_label")
        status_layout.addWidget(self.progress_status_label)

        status_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.progress_percent_label = QLabel("0%")
        status_layout.addWidget(self.progress_percent_label)

        layout.addLayout(status_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        inspiration_layout = QHBoxLayout()
        inspiration_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        teleton_logo_path = get_asset_path("teleton_logo.png")
        progress_logo_label = load_logo(teleton_logo_path, (16, 16), "🤝")
        inspiration_layout.addWidget(progress_logo_label)

        inspiration_label = QLabel("Procesando con amor")
        inspiration_layout.addWidget(inspiration_label)

        heart_emoji = QLabel("💜")
        inspiration_layout.addWidget(heart_emoji)

        layout.addLayout(inspiration_layout)

        return container

    def create_stats_panel(self):
        """Crea el panel de estadísticas."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        stats_card = QGroupBox("📊 Estado del Sistema")
        stats_card.setObjectName("stats_widget")

        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(15)

        self.create_metric_row("Archivos Cargados:", "0", stats_layout)
        self.create_metric_row("Registros Totales:", "0", stats_layout)
        self.create_metric_row("Citas de Mañana:", "0", stats_layout)
        self.create_metric_row("SMS Enviados:", "0", stats_layout)

        inspiration_frame = QFrame()
        inspiration_layout = QVBoxLayout(inspiration_frame)
        inspiration_layout.setContentsMargins(15, 15, 15, 15)
        inspiration_layout.setSpacing(8)

        teleton_logo_path = get_asset_path("teleton_logo.png")
        stats_logo_label = load_logo(teleton_logo_path, (20, 20), "🤝")
        stats_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inspiration_layout.addWidget(stats_logo_label)

        motto_label = QLabel("\"Juntos hacemos posible lo imposible\"")
        motto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inspiration_layout.addWidget(motto_label)

        emojis_label = QLabel("💙⭐💙")
        emojis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inspiration_layout.addWidget(emojis_label)

        stats_layout.addWidget(inspiration_frame)

        layout.addWidget(stats_card)

        self.files_card = QGroupBox("📋 Archivos Procesados")
        self.files_card.setVisible(False)

        files_layout = QVBoxLayout(self.files_card)
        files_layout.setContentsMargins(20, 20, 20, 20)

        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)

        layout.addWidget(self.files_card)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return panel

    def create_metric_row(self, label_text, value, parent_layout):
        """Crea una fila de métrica."""
        row_layout = QHBoxLayout()

        label = QLabel(label_text)
        row_layout.addWidget(label)

        row_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        value_label = QLabel(value)
        if "Archivos" in label_text:
            value_label.setObjectName("file_count_label")
            self.files_count_label = value_label
        elif "Registros Totales" in label_text:
            value_label.setObjectName("success_count_label")
            self.records_count_label = value_label
        elif "Citas de Mañana" in label_text:
            value_label.setObjectName("error_count_label")
            self.tomorrow_count_label = value_label
        elif "SMS Enviados" in label_text:
            value_label.setObjectName("sms_count_label")
            self.sms_count_label = value_label

        row_layout.addWidget(value_label)

        parent_layout.addLayout(row_layout)

    def create_footer(self):
        """Crea el footer con información del Teletón."""
        footer = QFrame()
        footer.setObjectName("footer_widget")
        footer.setMinimumHeight(80)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(30, 20, 30, 20)

        left_info = QWidget()
        left_layout = QHBoxLayout(left_info)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        teleton_logo_path = get_asset_path("teleton_logo.png")
        footer_logo_label = load_logo(teleton_logo_path, (36, 36), "🤝")
        left_layout.addWidget(footer_logo_label)

        org_info = QWidget()
        org_layout = QVBoxLayout(org_info)
        org_layout.setContentsMargins(0, 0, 0, 0)
        org_layout.setSpacing(2)

        org_label = QLabel("Fundación Teletón México A.C.")
        org_label.setObjectName("footer_label")
        org_layout.addWidget(org_label)

        system_label = QLabel("Sistema de Comunicación SMS")
        system_label.setObjectName("footer_label")
        org_layout.addWidget(system_label)

        left_layout.addWidget(org_info)

        layout.addWidget(left_info)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        right_info = QWidget()
        right_layout = QVBoxLayout(right_info)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        capacidad_logo_path = get_asset_path("capacidad_logo.png")
        capacidad_footer_label = load_logo(capacidad_logo_path, (100, 16), "Capacidad Sin Límites")
        capacidad_footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(capacidad_footer_label)

        emojis_label = QLabel("💜⭐💜")
        emojis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(emojis_label)

        layout.addWidget(right_info)

        return footer

    def set_credentials(self, credentials: DatabaseCredentials):
        """Establece las credenciales de la base de datos."""
        self.credentials = credentials
        connection_text = f"Conectado a: {credentials.database}@{credentials.host}"
        self.connection_label.setText(connection_text)

    def select_file(self):
        """Abre el diálogo de selección de archivo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel de citas del Teletón",
            os.path.expanduser("~/Downloads"),
            "Archivos Excel (*.xlsx);;Todos los archivos (*.*)"
        )

        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"📄 {filename}")
            self.clean_button.setEnabled(True)

    def clean_database(self):
        """Inicia el proceso de limpieza de la base de datos."""
        if not self.selected_file or not self.credentials:
            return

        reply = QMessageBox.question(
            self,
            "Confirmar Limpieza de Base de Datos",
            "⚠️ ADVERTENCIA: Esta acción eliminará TODOS los datos existentes en las tablas:\n\n"
            "• Cita\n• Paciente\n• Colaborador\n• Servicio\n• Clínica\n\n"
            "Y los reemplazará con los datos del archivo Excel seleccionado.\n\n"
            "¿Estás seguro de continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.show_progress("🔄 Limpiando base de datos y cargando citas...")

        self.cleaning_thread = DatabaseCleaningThread(
            self.selected_file,
            self.credentials.host,
            self.credentials.user,
            self.credentials.password,
            self.credentials.database
        )
        self.cleaning_thread.cleaning_progress.connect(self.update_progress)
        self.cleaning_thread.cleaning_finished.connect(self.on_cleaning_finished)
        self.cleaning_thread.start()

        self.clean_button.setEnabled(False)
        self.select_file_button.setEnabled(False)

    def extract_data(self):
        """Inicia el proceso de extracción de datos."""
        if not self.credentials:
            return

        self.show_progress("🔄 Extrayendo citas de mañana...")

        self.extraction_thread = DataExtractionThread(
            self.credentials.host,
            self.credentials.user,
            self.credentials.password,
            self.credentials.database
        )
        self.extraction_thread.extraction_progress.connect(self.update_progress)
        self.extraction_thread.extraction_finished.connect(self.on_extraction_finished)
        self.extraction_thread.start()

        self.extract_button.setEnabled(False)

    def send_sms(self):
        """Inicia el proceso de envío de SMS."""
        if not self.extracted_csv_file or not os.path.exists(self.extracted_csv_file):
            QMessageBox.warning(self, "Advertencia", "No hay un archivo CSV de citas para enviar SMS. Extrae las citas primero.")
            return

        reply = QMessageBox.question(
            self,
            "Confirmar Envío de SMS",
            f"¿Estás seguro de que quieres enviar recordatorios SMS a los pacientes listados en {os.path.basename(self.extracted_csv_file)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.show_progress("📱 Enviando recordatorios SMS...")

        self.sms_thread = SMSSendingThread(self.extracted_csv_file)
        self.sms_thread.sms_progress.connect(self.update_progress)
        self.sms_thread.sms_finished.connect(self.on_sms_finished)
        self.sms_thread.start()

        self.send_sms_button.setEnabled(False)

    def update_progress(self, progress):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(progress)
        self.progress_percent_label.setText(f"{progress}%")

    def on_cleaning_finished(self, success, message, records_count):
        """Maneja la finalización de la limpieza de base de datos."""
        self.hide_progress()

        self.select_file_button.setEnabled(True)

        if success:
            filename = os.path.basename(self.selected_file)
            self.stats['files_loaded'].append(filename)
            self.stats['total_records'] = records_count

            self.files_count_label.setText(str(len(self.stats['files_loaded'])))
            self.records_count_label.setText(f"{self.stats['total_records']:,}")

            self.files_list.addItem(f"📄 {filename} ({records_count:,} registros) ✓")
            self.files_card.setVisible(True)

            self.extract_button.setEnabled(True)

            QMessageBox.information(self, "Éxito",
                                    f"✅ {message}\n\nProcesados: {records_count:,} registros\n\nAhora puedes extraer las citas de mañana.")
        else:
            self.clean_button.setEnabled(True)
            QMessageBox.critical(self, "Error", f"❌ Error en la limpieza de base de datos:\n\n{message}")

    def on_extraction_finished(self, success, message, output_file, records_count):
        """Maneja la finalización de la extracción de datos."""
        self.hide_progress()

        self.extract_button.setEnabled(True)

        if success:
            self.extracted_csv_file = output_file

            self.stats['tomorrow_appointments'] = records_count
            self.tomorrow_count_label.setText(f"{records_count:,}")

            if output_file and records_count > 0:
                self.csv_info_label.setText(
                    f"✅ Archivo generado: {os.path.basename(output_file)}\n"
                    f"Citas encontradas: {records_count:,}"
                )
                self.csv_info_label.setVisible(True)
                self.send_sms_button.setEnabled(True)
            else:
                self.csv_info_label.setText("ℹ️ No se encontraron citas para mañana")
                self.csv_info_label.setVisible(True)

            QMessageBox.information(self, "Extracción Completada", f"✅ {message}")
        else:
            QMessageBox.critical(self, "Error", f"❌ Error en la extracción de datos:\n\n{message}")

    def on_sms_finished(self, success, message, sent_count, failed_count):
        """Maneja la finalización del envío de SMS."""
        self.hide_progress()

        self.send_sms_button.setEnabled(True)

        if success:
            self.stats['sms_sent'] += sent_count
            self.sms_count_label.setText(f"{self.stats['sms_sent']:,}")

            self.sms_info_label.setText(
                f"✅ {message}\nEnviados: {sent_count:,}, Fallidos: {failed_count:,}"
            )
            self.sms_info_label.setVisible(True)

            QMessageBox.information(self, "Envío Completado", f"✅ {message}")
        else:
            QMessageBox.critical(self, "Error", f"❌ Error en el envío de SMS:\n\n{message}")

    def show_progress(self, message):
        """Muestra la barra de progreso."""
        self.progress_status_label.setText(message)
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        self.progress_container.setVisible(True)

    def hide_progress(self):
        """Oculta la barra de progreso."""
        self.progress_container.setVisible(False)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación SMS Teletón."""
    def __init__(self):
        super().__init__()
        self.credentials = None
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()

    def setup_ui(self):
        """Configura la interfaz de usuario principal."""
        self.setWindowTitle("Sistema SMS Teletón - Capacidad Sin Límites")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.current_widget = None

        self.db_connection_widget = DatabaseConnectionWidget()
        self.sms_manager_widget = SMSManagerWidget()

        self.db_connection_widget.connection_successful.connect(self.on_database_connected)
        self.sms_manager_widget.disconnect_requested.connect(self.on_disconnect_requested)

        self.show_connection_screen()

    def show_connection_screen(self):
        """Muestra la pantalla de conexión."""
        if self.current_widget:
            self.centralWidget().layout().removeWidget(self.current_widget)
            self.current_widget.setParent(None)

        self.current_widget = self.db_connection_widget
        self.centralWidget().layout().addWidget(self.current_widget)

    def show_sms_manager(self):
        """Muestra la pantalla del gestor SMS."""
        if self.current_widget:
            self.centralWidget().layout().removeWidget(self.current_widget)
            self.current_widget.setParent(None)

        self.current_widget = self.sms_manager_widget
        self.centralWidget().layout().addWidget(self.current_widget)

    def setup_menu(self):
        """Configura la barra de menú."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Archivo")

        connect_action = QAction("&Conectar a Base de Datos", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.triggered.connect(self.show_connection_screen)
        file_menu.addAction(connect_action)

        file_menu.addSeparator()

        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Acerca de")

        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Configura la barra de estado."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.statusbar.showMessage("Sistema SMS Teletón - Listo para usar", 5000)

        self.connection_status = QLabel("No conectado")
        self.statusbar.addPermanentWidget(self.connection_status)

    def on_database_connected(self, credentials: DatabaseCredentials):
        """Maneja la conexión exitosa a la base de datos."""
        self.credentials = credentials
        self.sms_manager_widget.set_credentials(credentials)

        self.connection_status.setText(f"Conectado: {credentials.database}")

        self.show_sms_manager()
        self.statusbar.showMessage("Conexión exitosa a la base de datos", 3000)

    def on_disconnect_requested(self):
        """Maneja la solicitud de desconexión."""
        reply = QMessageBox.question(
            self,
            "Confirmar Desconexión",
            "¿Estás seguro de que quieres desconectarte de la base de datos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.credentials = None
            self.connection_status.setText("No conectado")
            self.show_connection_screen()
            self.statusbar.showMessage("Desconectado de la base de datos", 3000)

    def show_about(self):
        """Muestra el diálogo Acerca de."""
        QMessageBox.about(self, "Acerca del Sistema SMS Teletón",
                          """
                          <h3>Sistema SMS Teletón</h3>
                          <p><b>Versión:</b> 1.0</p>
                          <p><b>Desarrollado para:</b> Fundación Teletón México, CRIT Tijuana, Baja California A.C.</p>
                          <p><b>Desarrollado por:</b> Jorge Torres Perez, Armando Ibarra Marquez,
                          Cristian Deraz Marquez,
                          Jesus Trejo Silva,
                          Julio Ricoy Ramos,
                          Rodolfo Goku Santiago. .</p>
                          <p><b>Propósito:</b> Gestión y envío masivo de mensajes SMS</p>
                          <br>
                          <p style="color: #8E44AD; font-weight: bold;">
                          "Juntos hacemos posible lo imposible"<br>
                          Capacidad Sin Límites
                          </p>
                          <p><small>💜 Sistema desarrollado con amor para la comunidad del Teletón 💜</small></p>
                          """)

# ================================
# FUNCIÓN PRINCIPAL MAIN
# ================================

def main():
    """
    Función principal de la aplicación SMS del Teletón.
    """
    app = QApplication(sys.argv)

    app.setApplicationName("Sistema SMS Teletón")
    app.setApplicationDisplayName("Sistema de Mensajería SMS - Fundación Teletón México")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fundación Teletón México A.C.")
    app.setOrganizationDomain("teleton.org")

    print("=" * 60)
    print("🤝 SISTEMA SMS TELETÓN - FUNDACIÓN TELETÓN MÉXICO A.C. 🤝")
    print("=" * 60)
    print("\"Juntos hacemos posible lo imposible\" - Capacidad Sin Límites")
    print("=" * 60)

    print("\n🎨 Cargando estilos visuales del Teletón...")
    styles_loaded = load_teleton_styles(app)

    if not styles_loaded:
        print("📋 Aplicando estilos básicos del Teletón como respaldo...")
        apply_fallback_teleton_styles(app)

    icon_path = Path(__file__).parent / 'assets' / 'teleton_logo.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        print(f"✓ Icono de aplicación cargado: {icon_path}")
    else:
        print(f"⚠️ Icono de aplicación no encontrado: {icon_path}")
        print("   Coloca teleton_logo.png en la carpeta assets/")

    print("\n🚀 Iniciando aplicación...")

    window = MainWindow()
    window.show()

    print("✓ Aplicación iniciada correctamente")
    print("💜 ¡Bienvenido al Sistema SMS del Teletón! 💜")
    print("=" * 60)

    try:
        return app.exec()
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        return 1
    finally:
        print("\n👋 Cerrando Sistema SMS Teletón...")
        print("¡Gracias por usar nuestro sistema!")

if __name__ == "__main__":
    sys.exit(main())
