import sys
import os
import json
import openpyxl
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QPushButton, QLabel, QListWidget, QComboBox, 
                             QMenuBar, QFileDialog, QDialog, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QInputDialog, QSplitter,
                             QCheckBox)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

try:
    from PIL import Image, ImageTk
except ImportError:
    # Este bloque debería estar en un messagebox, pero para simplificar lo dejamos en consola
    print("ERROR: Se requiere la librería 'Pillow'. Instálala con: pip install Pillow")
    sys.exit()

try:
    import darkdetect
except ImportError:
    darkdetect = None

# --- Constantes ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_FILE = "GL Conecta Express logo.png"
PROFILES_FILE = "profiles.json"
APP_VERSION = "2.2"
APP_CREATOR = "Eduar Alpuria"
APP_DESCRIPTION = "Herramienta para depurar reportes de Excel eliminando columnas no deseadas y filtrando filas mediante perfiles preconfigurados."

# --- Hojas de Estilo (QSS) ---
THEMES = {
    "Oscuro": """
        QWidget {
            background-color: #1e1e1e; color: #FFFFFF; font-family: Segoe UI; font-size: 10pt;
        }
        QFrame#groupBoxFrame {
            background-color: #333333; border: 1px solid #555555; border-radius: 8px;
        }
        QLabel#groupBoxTitle, QLabel#keywordTitle {
            color: #b0b0b0; font-weight: bold; padding-left: 5px;
        }
        QLabel { background-color: transparent; }
        QPushButton {
            background-color: #4a4a4a; border: 1px solid #555555; border-radius: 5px; padding: 5px;
            min-width: 150px;
        }
        QPushButton:hover { background-color: #5a5a5a; }
        QPushButton:pressed { background-color: #6a6a6a; }
        QPushButton:disabled { background-color: #404040; color: #808080; }
        QListWidget, QLineEdit {
            background-color: #2a2a2a; border: 1px solid #555555; border-radius: 5px; padding: 3px;
        }
        QComboBox {
            background-color: #2a2a2a; border: 1px solid #555555; border-radius: 5px; padding: 3px;
            min-width: 160px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #333333; border: 1px solid #555555; selection-background-color: #0078D4;}
        QListWidget::item:selected { background-color: #0078D4; }
        QMenuBar { background-color: #333333; }
        QMenuBar::item:selected { background-color: #4a4a4a; }
        QMenu { background-color: #333333; border: 1px solid #555555; }
        QMenu::item:selected { background-color: #4a4a4a; }
        QScrollBar:vertical, QScrollBar:horizontal {
            border: none; background: #2a2a2a; width: 10px; height: 10px; margin: 0px; border-radius: 5px;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #555555; min-height: 20px; min-width: 20px; border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #6a6a6a; }
        QScrollBar::add-line, QScrollBar::sub-line { border: none; background: none; height: 0px; width: 0px; }
        QScrollBar::add-page, QScrollBar::sub-page { background: none; }
    """,
    "Claro": """
        QWidget {
            background-color: #ECECEC; color: #000000; font-family: Segoe UI; font-size: 10pt;
        }
        QFrame#groupBoxFrame {
            background-color: #D9D9D9; border: 1px solid #C0C0C0; border-radius: 8px;
        }
        QLabel#groupBoxTitle, QLabel#keywordTitle {
            color: #333333; font-weight: bold; padding-left: 5px;
        }
        QLabel { background-color: transparent; }
        QPushButton {
            background-color: #E0E0E0; border: 1px solid #C0C0C0; border-radius: 5px; padding: 5px;
            min-width: 150px;
        }
        QPushButton:hover { background-color: #F0F0F0; }
        QPushButton:pressed { background-color: #C0C0C0; }
        QPushButton:disabled { background-color: #D3D3D3; color: #808080; }
        QListWidget, QLineEdit {
            background-color: #FFFFFF; border: 1px solid #C0C0C0; border-radius: 5px; padding: 3px;
        }
        QComboBox {
            background-color: #FFFFFF; border: 1px solid #C0C0C0; border-radius: 5px; padding: 3px;
            min-width: 160px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #FFFFFF; border: 1px solid #C0C0C0; selection-background-color: #0078D4;}
        QListWidget::item:selected { background-color: #0078D4; color: #FFFFFF; }
        QMenuBar { background-color: #D9D9D9; }
        QMenuBar::item:selected { background-color: #C0C0C0; }
        QMenu { background-color: #D9D9D9; border: 1px solid #C0C0C0; }
        QMenu::item:selected { background-color: #C0C0C0; }
        QScrollBar:vertical, QScrollBar:horizontal {
            border: none; background: #E0E0E0; width: 10px; height: 10px; margin: 0px; border-radius: 5px;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #A0A0A0; min-height: 20px; min-width: 20px; border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #B0B0B0; }
        QScrollBar::add-line, QScrollBar::sub-line { border: none; background: none; height: 0px; width: 0px; }
        QScrollBar::add-page, QScrollBar::sub-page { background: none; }
    """
}

class ProfileDialog(QDialog):
    def __init__(self, excel_data_df, all_columns, existing_profiles, parent=None, profile_to_edit=None):
        super().__init__(parent)
        self.main_app = parent
        self.setWindowTitle("Crear Nuevo Perfil" if profile_to_edit is None else f"Editar Perfil: {profile_to_edit}")
        self.setMinimumSize(600, 500)
        self.excel_data_df = excel_data_df
        self.all_columns = all_columns
        self.existing_profiles = existing_profiles
        self.profile_to_edit = profile_to_edit
        self.profile_data = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nombre del Perfil:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("1. Selecciona columnas para ELIMINAR:"))
        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.column_list.addItems(self.all_columns)
        left_layout.addWidget(self.column_list)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("2. Añade palabras clave para FILTRAR filas:"))
        search_options_layout = QHBoxLayout()
        search_options_layout.addWidget(QLabel("Buscar en:"))
        self.check_remitente = QCheckBox("Nombre remitente")
        self.check_destinatario = QCheckBox("Nombre destinatario")
        self.check_observaciones = QCheckBox("Observaciones")
        self.check_remitente.setChecked(True)
        self.check_destinatario.setChecked(True)
        self.check_observaciones.setChecked(True)
        search_options_layout.addWidget(self.check_remitente)
        search_options_layout.addWidget(self.check_destinatario)
        search_options_layout.addWidget(self.check_observaciones)
        search_options_layout.addStretch(1)
        right_layout.addLayout(search_options_layout)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Escribe para buscar...")
        self.search_bar.textChanged.connect(self.update_search_results)
        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(QLabel("Resultados de la búsqueda:"))
        self.search_results_list = QListWidget()
        self.search_results_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        right_layout.addWidget(self.search_results_list)
        add_remove_layout = QHBoxLayout()
        add_button = QPushButton("Añadir seleccionados ↓")
        remove_button = QPushButton("↑ Quitar seleccionados")
        add_remove_layout.addWidget(add_button)
        add_remove_layout.addWidget(remove_button)
        right_layout.addLayout(add_remove_layout)
        right_layout.addWidget(QLabel("Palabras Clave Guardadas en este Perfil:"))
        self.chosen_keywords_list = QListWidget()
        self.chosen_keywords_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        right_layout.addWidget(self.chosen_keywords_list)
        add_button.clicked.connect(self.add_keywords)
        remove_button.clicked.connect(self.remove_keywords)
        self.check_remitente.stateChanged.connect(self.update_search_results)
        self.check_destinatario.stateChanged.connect(self.update_search_results)
        self.check_observaciones.stateChanged.connect(self.update_search_results)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        layout.addWidget(splitter)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("Guardar Perfil")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        if self.profile_to_edit:
            self.load_profile_for_editing()
    def load_profile_for_editing(self):
        self.name_edit.setText(self.profile_to_edit)
        self.name_edit.setReadOnly(True)
        data = self.existing_profiles.get(self.profile_to_edit, {})
        cols_to_delete = data.get("columns_to_delete", [])
        for i in range(self.column_list.count()):
            item = self.column_list.item(i)
            if item.text() in cols_to_delete:
                item.setSelected(True)
        keywords = data.get("row_filter_keywords", [])
        self.chosen_keywords_list.addItems(keywords)
    def update_search_results(self):
        text = self.search_bar.text()
        self.search_results_list.clear()
        if not text or len(text) < 3:
            return
        search_text = text.upper()
        search_cols = []
        if self.check_remitente.isChecked(): search_cols.append("Nombre remitente")
        if self.check_destinatario.isChecked(): search_cols.append("Nombre destinatario")
        if self.check_observaciones.isChecked(): search_cols.append("Observaciones")
        valid_search_cols = [col for col in search_cols if col in self.excel_data_df.columns]
        if not valid_search_cols: return
        all_values_series = pd.concat([self.excel_data_df[col].dropna().astype(str) for col in valid_search_cols])
        unique_values = all_values_series.unique()
        matching_values = [val for val in unique_values if search_text in val.upper()]
        self.search_results_list.addItems(sorted(matching_values))
    def add_keywords(self):
        selected_items = self.search_results_list.selectedItems()
        current_keywords = {self.chosen_keywords_list.item(i).text() for i in range(self.chosen_keywords_list.count())}
        for item in selected_items:
            if item.text() not in current_keywords:
                self.chosen_keywords_list.addItem(item.text())
    def remove_keywords(self):
        selected_items = self.chosen_keywords_list.selectedItems()
        for item in selected_items:
            self.chosen_keywords_list.takeItem(self.chosen_keywords_list.row(item))
    def accept(self):
        profile_name = self.name_edit.text().strip()
        selected_columns = self.column_list.selectedItems()
        if not profile_name:
            QMessageBox.warning(self, "Nombre Vacío", "El nombre del perfil no puede estar vacío.")
            return
        if profile_name in self.existing_profiles and self.profile_to_edit is None:
            QMessageBox.warning(self, "Nombre Duplicado", "Ya existe un perfil con este nombre.")
            return
        if not selected_columns:
            QMessageBox.warning(self, "Sin Selección de Columnas", "Debes seleccionar al menos una columna para eliminar.")
            return
        columns_to_delete = [item.text() for item in selected_columns]
        row_filter_keywords = [self.chosen_keywords_list.item(i).text() for i in range(self.chosen_keywords_list.count())]
        self.profile_data = {
            "name": profile_name,
            "data": { 
                "columns_to_delete": columns_to_delete, 
                "all_columns_at_creation": self.all_columns,
                "row_filter_keywords": row_filter_keywords
            }
        }
        super().accept()


class GestorReportesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.perfiles_guardados = {}
        self.ruta_archivo_completa = ""
        self.current_df = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestor de Reportes SAC - GL Conecta v2.2")
        self.setFixedSize(450, 550)
        icon_path = os.path.join(SCRIPT_DIR, LOGO_FILE)
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        self._crear_barra_menu()
        main_content_widget = QWidget()
        self.main_layout = QVBoxLayout(main_content_widget)
        self.main_layout.setContentsMargins(10,10,10,10)
        self._crear_seccion_carga()
        self._crear_seccion_columnas()
        self._crear_seccion_ejecutar()
        self.main_layout.addStretch(1)
        self.outer_layout.addWidget(main_content_widget)
        self._load_profiles_from_json()
        self._update_profile_combo_box()
        self.apply_theme("Automático")
        self.show()

    def _crear_barra_menu(self):
        self.menu_bar = QMenuBar()
        self.outer_layout.addWidget(self.menu_bar)
        opciones_menu = self.menu_bar.addMenu("Opciones")
        tema_menu = opciones_menu.addMenu("Tema")
        if darkdetect:
            accion_auto = QAction("Automático (Tema del Sistema)", self)
            accion_auto.triggered.connect(lambda: self.apply_theme("Automático"))
            tema_menu.addAction(accion_auto)
            tema_menu.addSeparator()
        accion_claro = QAction("Claro", self)
        accion_claro.triggered.connect(lambda: self.apply_theme("Claro"))
        tema_menu.addAction(accion_claro)
        accion_oscuro = QAction("Oscuro", self)
        accion_oscuro.triggered.connect(lambda: self.apply_theme("Oscuro"))
        tema_menu.addAction(accion_oscuro)
        opciones_menu.addSeparator()
        accion_crear = QAction("Crear Perfil...", self)
        accion_crear.triggered.connect(self._open_create_profile_dialog)
        opciones_menu.addAction(accion_crear)
        accion_editar = QAction("Editar Perfil...", self)
        accion_editar.triggered.connect(self._open_edit_profile_dialog)
        opciones_menu.addAction(accion_editar)
        accion_eliminar = QAction("Eliminar Perfil...", self)
        accion_eliminar.triggered.connect(self._open_delete_profile_dialog)
        opciones_menu.addAction(accion_eliminar)
        opciones_menu.addSeparator()
        accion_acerca = QAction("Acerca de...", self)
        accion_acerca.triggered.connect(self._show_about_window)
        opciones_menu.addAction(accion_acerca)
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        opciones_menu.addAction(accion_salir)

    def _show_about_window(self):
        about_text = f"""<h3>Gestor de Reportes SAC</h3><p><b>Versión:</b> {APP_VERSION}</p><p><b>Creado por:</b> {APP_CREATOR}</p><p>{APP_DESCRIPTION}</p>"""
        QMessageBox.about(self, "Acerca de Gestor de Reportes", about_text)

    def _crear_seccion_carga(self):
        container_frame = QFrame()
        container_frame.setObjectName("groupBoxFrame")
        layout = QVBoxLayout(container_frame)
        title_label = QLabel("1. Cargar Archivo")
        title_label.setObjectName("groupBoxTitle")
        self.btn_seleccionar = QPushButton("📂 Seleccionar Archivo")
        self.btn_seleccionar.clicked.connect(self.seleccionar_archivo)
        self.label_ruta_archivo = QLabel("Archivo: (ninguno seleccionado)")
        self.label_ruta_archivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.btn_seleccionar)
        button_layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.label_ruta_archivo)
        self.main_layout.addWidget(container_frame)

    def _crear_seccion_columnas(self):
        container_frame = QFrame()
        container_frame.setObjectName("groupBoxFrame")
        layout = QVBoxLayout(container_frame)
        title_label = QLabel("2. Visualizar Columnas y Selección de Perfil")
        title_label.setObjectName("groupBoxTitle")
        self.combo_perfiles = QComboBox()
        self.lista_columnas = QListWidget()
        self.lista_columnas.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.keyword_title_label = QLabel("Palabras Clave del Perfil:")
        self.keyword_title_label.setObjectName("keywordTitle")
        self.keyword_title_label.setVisible(False)
        self.lista_keywords_display = QListWidget()
        self.lista_keywords_display.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.lista_keywords_display.setMaximumHeight(80)
        self.lista_keywords_display.setVisible(False)
        self.combo_perfiles.currentTextChanged.connect(self.aplicar_perfil)
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.combo_perfiles)
        combo_layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addLayout(combo_layout)
        layout.addWidget(self.lista_columnas)
        layout.addWidget(self.keyword_title_label)
        layout.addWidget(self.lista_keywords_display)
        self.main_layout.addWidget(container_frame)

    def _crear_seccion_ejecutar(self):
        container_frame = QFrame()
        container_frame.setObjectName("groupBoxFrame")
        layout = QVBoxLayout(container_frame)
        title_label = QLabel("3. Ejecutar")
        title_label.setObjectName("groupBoxTitle")
        self.btn_generar = QPushButton("▶ Generar Archivo Actualizado")
        self.btn_generar.setEnabled(False)
        self.btn_generar.clicked.connect(self.generar_archivo)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.btn_generar)
        button_layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addLayout(button_layout)
        self.main_layout.addWidget(container_frame)
        
    def apply_theme(self, theme_name):
        if theme_name == "Automático" and darkdetect:
            if darkdetect.isDark(): self.setStyleSheet(THEMES["Oscuro"])
            else: self.setStyleSheet(THEMES["Claro"])
        else: self.setStyleSheet(THEMES.get(theme_name, THEMES["Claro"]))

    def _save_profiles_to_json(self):
        profiles_path = os.path.join(SCRIPT_DIR, PROFILES_FILE)
        try:
            with open(profiles_path, "w", encoding='utf-8') as f:
                json.dump(self.perfiles_guardados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar Perfiles", f"No se pudo guardar el archivo de perfiles.\n\nError: {e}")

    def _load_profiles_from_json(self):
        profiles_path = os.path.join(SCRIPT_DIR, PROFILES_FILE)
        try:
            if os.path.exists(profiles_path) and os.path.getsize(profiles_path) > 0:
                with open(profiles_path, "r", encoding='utf-8') as f: self.perfiles_guardados = json.load(f)
            else: self.perfiles_guardados = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.perfiles_guardados = {}

    def _update_profile_combo_box(self):
        self.combo_perfiles.clear()
        self.combo_perfiles.addItem("Perfiles...")
        if self.perfiles_guardados:
            self.combo_perfiles.addItems(sorted(self.perfiles_guardados.keys()))

    def seleccionar_archivo(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "", "Archivos de Excel (*.xlsx *.xls)")
        if filepath:
            try:
                self.lista_columnas.clear()
                self.lista_keywords_display.clear()
                self.keyword_title_label.setVisible(False)
                self.lista_keywords_display.setVisible(False)
                self.current_df = pd.read_excel(filepath)
                column_headers = self.current_df.columns.tolist()
                self.lista_columnas.addItems(column_headers)
                self.ruta_archivo_completa = filepath
                self.label_ruta_archivo.setText(f"Archivo: {os.path.basename(filepath)}")
                self.btn_generar.setEnabled(True)
            except Exception as e:
                self.current_df = None
                self.label_ruta_archivo.setText("Error al leer el archivo.")
                self.btn_generar.setEnabled(False)
                QMessageBox.critical(self, "Error de Lectura", f"No se pudo leer el archivo Excel.\n\nError: {e}")

    def aplicar_perfil(self, nombre_perfil):
        self.lista_columnas.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        try:
            self.lista_columnas.clearSelection()
            self.lista_keywords_display.clear()
            self.keyword_title_label.setVisible(False)
            self.lista_keywords_display.setVisible(False)
            if nombre_perfil in ["", "Perfiles..."]: return
            profile_data = self.perfiles_guardados.get(nombre_perfil)
            cols_to_delete, keywords = [], []
            if isinstance(profile_data, dict):
                cols_to_delete = profile_data.get("columns_to_delete", [])
                keywords = profile_data.get("row_filter_keywords", [])
            elif isinstance(profile_data, list):
                cols_to_delete = profile_data
            for i in range(self.lista_columnas.count()):
                item = self.lista_columnas.item(i)
                if item.text() in cols_to_delete: item.setSelected(True)
            if keywords:
                self.lista_keywords_display.addItems(keywords)
                self.keyword_title_label.setVisible(True)
                self.lista_keywords_display.setVisible(True)
        finally:
            self.lista_columnas.setSelectionMode(QListWidget.SelectionMode.NoSelection)

    def _open_create_profile_dialog(self):
        if self.current_df is None:
            QMessageBox.warning(self, "Sin Datos", "Primero debes cargar un archivo para poder crear un perfil basado en sus datos.")
            return
        all_columns = self.current_df.columns.tolist()
        dialog = ProfileDialog(self.current_df, all_columns, self.perfiles_guardados, self)
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec():
            new_profile = dialog.profile_data
            if new_profile:
                self.perfiles_guardados[new_profile["name"]] = new_profile["data"]
                self._save_profiles_to_json()
                self._update_profile_combo_box()
                QMessageBox.information(self, "Éxito", f"Perfil '{new_profile['name']}' guardado correctamente.")

    def _open_edit_profile_dialog(self):
        if not self.perfiles_guardados:
            QMessageBox.warning(self, "Sin Perfiles", "No hay perfiles guardados para editar.")
            return
        profile_names = sorted(self.perfiles_guardados.keys())
        profile_to_edit, ok = QInputDialog.getItem(self, "Editar Perfil", "Selecciona el perfil a editar:", profile_names, 0, False)
        if ok and profile_to_edit:
            profile_data = self.perfiles_guardados.get(profile_to_edit)
            all_columns_for_profile = []
            df_for_dialog = None # Por defecto no hay datos de excel
            if isinstance(profile_data, dict) and "all_columns_at_creation" in profile_data:
                all_columns_for_profile = profile_data.get("all_columns_at_creation", [])
                # Para perfiles nuevos, idealmente no necesitamos el DF, pero la búsqueda en vivo sí
                if self.current_df is not None:
                    df_for_dialog = self.current_df
            elif self.current_df is not None:
                all_columns_for_profile = self.current_df.columns.tolist()
                df_for_dialog = self.current_df
            else:
                QMessageBox.warning(self, "Perfil Antiguo o sin Contexto", "Para editar este perfil, primero debes cargar un archivo Excel de referencia que contenga sus columnas.")
                return
            
            dialog = ProfileDialog(df_for_dialog, all_columns_for_profile, self.perfiles_guardados, self, profile_to_edit=profile_to_edit)
            dialog.setStyleSheet(self.styleSheet())
            if dialog.exec():
                updated_profile = dialog.profile_data
                if updated_profile:
                    self.perfiles_guardados[updated_profile["name"]] = updated_profile["data"]
                    self._save_profiles_to_json()
                    self._update_profile_combo_box()
                    QMessageBox.information(self, "Éxito", f"Perfil '{updated_profile['name']}' actualizado.")

    def _open_delete_profile_dialog(self):
        if not self.perfiles_guardados:
            QMessageBox.warning(self, "Sin Perfiles", "No hay perfiles guardados para eliminar.")
            return
        profile_names = sorted(self.perfiles_guardados.keys())
        profile_to_delete, ok = QInputDialog.getItem(self, "Eliminar Perfil", "Selecciona el perfil a eliminar:", profile_names, 0, False)
        if ok and profile_to_delete:
            reply = QMessageBox.question(self, "Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar el perfil '{profile_to_delete}' permanentemente?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.perfiles_guardados[profile_to_delete]
                self._save_profiles_to_json()
                self._update_profile_combo_box()
                QMessageBox.information(self, "Éxito", f"El perfil '{profile_to_delete}' ha sido eliminado.")

    def _sanitize_sheet_name(self, name):
        # Nombres de hoja en Excel no pueden tener estos caracteres: [] : * ? / \
        invalid_chars = r'[]:*?/\ '
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized[:31] # Limitar a 31 caracteres

    def generar_archivo(self):
        if self.current_df is None:
            QMessageBox.warning(self, "Archivo no encontrado", "Primero debes seleccionar un archivo de origen.")
            return
        selected_profile_name = self.combo_perfiles.currentText()
        if selected_profile_name in ["", "Perfiles..."]:
            QMessageBox.warning(self, "Sin Perfil", "Aplica un perfil para indicar las columnas y filas a procesar.")
            return
        profile_data = self.perfiles_guardados.get(selected_profile_name)
        if not profile_data:
            QMessageBox.critical(self, "Error", f"No se encontraron los datos para el perfil '{selected_profile_name}'.")
            return
        columnas_a_eliminar = []
        keywords = []
        if isinstance(profile_data, dict):
            columnas_a_eliminar = profile_data.get("columns_to_delete", [])
            keywords = profile_data.get("row_filter_keywords", [])
        elif isinstance(profile_data, list):
            columnas_a_eliminar = profile_data
        nombre_base, extension = os.path.splitext(os.path.basename(self.ruta_archivo_completa))
        nombre_sugerido = f"{nombre_base}-{selected_profile_name}{extension}"
        ruta_guardado, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Filtrado", nombre_sugerido, "Archivos de Excel (*.xlsx)")
        if not ruta_guardado:
            return
        try:
            df = self.current_df.copy()
            columnas_a_guardar = [h for h in df.columns if h not in columnas_a_eliminar]
            df_filtrado = df[columnas_a_guardar]
            df_final = df_filtrado
            if keywords:
                search_cols = ["Nombre remitente", "Nombre destinatario", "Observaciones"]
                valid_search_cols = [col for col in search_cols if col in df_filtrado.columns]
                if not valid_search_cols:
                    QMessageBox.warning(self, "Columnas no Encontradas", "Ninguna de las columnas de búsqueda (Nombre remitente, etc.) existe en el archivo. No se puede filtrar por filas.")
                else:
                    mask = pd.Series([False] * len(df_filtrado), index=df_filtrado.index)
                    for col in valid_search_cols:
                        mask |= df_filtrado[col].astype(str).isin(keywords)
                    df_final = df_filtrado[mask]

            sanitized_name = self._sanitize_sheet_name(selected_profile_name)
            df_final.to_excel(ruta_guardado, index=False, sheet_name=sanitized_name)
            
            QMessageBox.information(self, "Proceso Completado", f"El archivo actualizado ha sido guardado con éxito en:\n{ruta_guardado}")
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"Ocurrió un error al generar el archivo.\n\nError: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GestorReportesApp()
    sys.exit(app.exec())