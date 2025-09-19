import os
import shutil
import smtplib
import sqlite3
import sys
import re  # Добавлено
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.parser import parse  # Добавлено

import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QPalette, QColor, QDesktopServices, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit, QCheckBox,
    QPushButton, QFileDialog, QMessageBox, QListWidget, QTabWidget,
    QGroupBox, QGridLayout, QSplitter, QFrame, QSizePolicy, QScrollArea,
    QDialog, QDialogButtonBox, QFormLayout, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QCompleter, QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog
)

# Добавим импорт для обработки файлов
try:
    from docx import Document
except ImportError:
    Document = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import spacy

    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

# Загрузка модели при инициализации класса
if HAS_SPACY:
    nlp = spacy.load("ru_core_news_sm")


def extract_entities_with_ml(self, text):
    """Извлечение сущностей с использованием машинного обучения"""
    if not HAS_SPACY:
        return {}

    doc = nlp(text)
    entities = {}

    for ent in doc.ents:
        if ent.label_ == "ORG" and "counterparty_name" not in entities:
            entities["counterparty_name"] = ent.text
        elif ent.label_ == "DATE" and "contract_date" not in entities:
            # Попытка преобразовать дату
            try:
                date_obj = parse(ent.text, languages=['ru'])
                entities["contract_date"] = date_obj.strftime("%Y-%m-%d")
            except:
                pass
        elif ent.label_ == "MONEY" and "amount" not in entities:
            entities["amount"] = ent.text

    return entities


def exception_hook(exctype, value, traceback_obj):
    error_message = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("Произошла непредвиденная ошибка")
    msg.setInformativeText(str(value))
    msg.setDetailedText(error_message)
    msg.exec()

sys.excepthook = exception_hook
# Для открытия файлов в Windows

class ProjectCard(QFrame):
    clicked = pyqtSignal(dict)  # Добавьте этот сигнал в начало класса

    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
                border: 1px solid #4a86e8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Номер проекта - компактно
        number_label = QLabel(f"<b>№:</b> {self.project_data['project_number']}")
        number_label.setTextFormat(Qt.TextFormat.RichText)
        number_label.setStyleSheet("margin: 0; padding: 0;")
        number_label.setWordWrap(True)
        layout.addWidget(number_label)

        # Название проекта - с переносом
        name_label = QLabel(f"<b>Проект:</b> {self.project_data['project_name']}")
        name_label.setTextFormat(Qt.TextFormat.RichText)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("margin: 0; padding: 0;")
        name_label.setMaximumHeight(40)  # Ограничиваем высоту
        layout.addWidget(name_label)

        # Адрес объекта - с переносом
        address_label = QLabel(f"<b>Адрес:</b> {self.project_data['object_address']}")
        address_label.setTextFormat(Qt.TextFormat.RichText)
        address_label.setWordWrap(True)
        address_label.setStyleSheet("margin: 0; padding: 0;")
        address_label.setMaximumHeight(40)  # Ограничиваем высоту
        layout.addWidget(address_label)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def get_project_data(self):
        return self.project_data

    def mousePressEvent(self, event):
        # Снимаем выделение со всех карточек
        parent_widget = self.parentWidget()
        while parent_widget and not hasattr(parent_widget, 'projects_grid_layout'):
            parent_widget = parent_widget.parentWidget()

        if parent_widget:
            for i in range(parent_widget.projects_grid_layout.count()):
                widget = parent_widget.projects_grid_layout.itemAt(i).widget()
                if isinstance(widget, ProjectCard):
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: white;
                            border-radius: 5px;
                            padding: 5px;
                            margin: 2px;
                        }
                        QFrame:hover {
                            background-color: #f0f0f0;
                            border: 1px solid #4a86e8;
                        }
                    """)
                    widget.setProperty("selected", False)

        # Выделяем текущую карточку
        self.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 2px solid #4a86e8;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
        """)
        self.setProperty("selected", True)

        # Эмитируем сигнал при клике
        self.clicked.emit(self.project_data)

        # Показываем детали проекта при двойном клике
        if event.type() == event.Type.MouseButtonDblClick:
            # Нужно вызвать метод show_project_details у родительского окна
            main_window = self.window()
            if hasattr(main_window, 'show_project_details'):
                main_window.show_project_details(self.project_data)

        super().mousePressEvent(event)
# Добавим диалог для просмотра подробной информации о проекте
class ProjectDetailsDialog(QDialog):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Детальная информация о проекте")
        self.setModal(True)
        self.project_data = project_data
        self.setup_ui()

    def setup_ui(self):
        # Увеличиваем минимальный размер диалога
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        scroll_area = ModernScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # Создаем форму для отображения данных
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(8)

        # Отображаем все поля проекта
        fields = [
            ("Номер проекта:", self.project_data.get('project_number', '')),
            ("Название проекта:", self.project_data.get('project_name', '')),
            ("Адрес объекта:", self.project_data.get('object_address', '')),
            ("Номер договора:", self.project_data.get('contract_number', '')),
            ("Клиент:", self.project_data.get('client', '')),
            ("Наименование объекта:", self.project_data.get('object_name', '')),
            ("Объем работ:", self.project_data.get('work_scope', '')),
            ("Количество копий:", self.project_data.get('copies_count', '')),
            ("Авторизованный email:", self.project_data.get('authorized_email', '')),
            ("Процедура доставки:", self.project_data.get('delivery_procedure', '')),
            ("Контактное лицо:", self.project_data.get('contact_person', '')),
            ("Шифр:", self.project_data.get('cipher', '')),
            ("Ответственный EDA:", self.project_data.get('responsible_eda', '')),
            ("Заместитель EDA:", self.project_data.get('substitute_eda', '')),
            ("Дата email доставки:", self.project_data.get('email_delivery_date', '')),
            ("Дата бумажной доставки:", self.project_data.get('paper_delivery_date', ''))
        ]

        for label, value in fields:
            if value:  # Показываем только заполненные поля
                value_label = QLabel(str(value))
                value_label.setWordWrap(True)
                value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                value_label.setMinimumWidth(500)  # Устанавливаем минимальную ширину для значений
                form_layout.addRow(QLabel(f"<b>{label}</b>"), value_label)

        scroll_layout.addLayout(form_layout)
        scroll_layout.addStretch()

        # Устанавливаем политику размера для содержимого
        scroll_content.setMinimumWidth(700)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Кнопка закрытия
        close_button = ModernButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class EmailWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, settings, to_emails, subject, text_body, html_body):
        super().__init__()
        self.settings = settings
        self.to_emails = to_emails
        self.subject = subject
        self.text_body = text_body
        self.html_body = html_body

    def run(self):
        try:
            # Создаем multipart сообщение
            msg = MIMEMultipart('alternative')
            msg['From'] = self.settings['email_from']
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = self.subject

            # Добавляем обе версии: текстовую и HTML
            part1 = MIMEText(self.text_body, 'plain', 'utf-8')
            part2 = MIMEText(self.html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            if self.settings.get('connection_type', 'TLS') == "SSL":
                server = smtplib.SMTP_SSL(self.settings['smtp_server'],
                                          int(self.settings['smtp_port']))
            else:
                server = smtplib.SMTP(self.settings['smtp_server'],
                                      int(self.settings['smtp_port']))
                server.starttls()

            server.login(self.settings['email_from'], self.settings['email_password'])
            server.send_message(msg)
            server.quit()

            self.finished.emit(True, "Письмо отправлено успешно!")
        except Exception as e:
            self.finished.emit(False, f"Ошибка отправки email: {str(e)}")


class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setMaximumHeight(35)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)


class ModernScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Стилизация скроллбаров
        scrollbar_style = """
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
        self.setStyleSheet(scrollbar_style)


class DocumentLinksDialog(QDialog):
    def __init__(self, parent=None, contract_id=None, contract_info=None):
        super().__init__(parent)
        self.setWindowTitle("Связи документа")
        self.contract_id = contract_id
        self.contract_info = contract_info
        self.main_window = parent  # Сохраняем ссылку на главное окно
        self.setModal(True)
        self.setup_ui()
        self.load_links()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setMinimumSize(800, 500)

        # Информация о документе
        info_label = QLabel(f"Документ: {self.contract_info}")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Таблица связей
        self.links_table = QTableWidget()
        self.links_table.setColumnCount(5)
        self.links_table.setHorizontalHeaderLabels(["Тип связи", "Документ", "Номер", "Дата", "Действия"])
        self.links_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.links_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.links_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.links_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.links_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.links_table.verticalHeader().setDefaultSectionSize(40)
        layout.addWidget(self.links_table)

        # Кнопки
        buttons_layout = QHBoxLayout()

        close_button = ModernButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)

        layout.addLayout(buttons_layout)

    def load_links(self):
        self.links_table.setRowCount(0)
        if self.contract_id and self.main_window:
            links = self.main_window.get_document_links(self.contract_id)
            self.links_table.setRowCount(len(links))

            for row, link in enumerate(links):
                # Тип связи
                self.links_table.setItem(row, 0, QTableWidgetItem(link['link_type']))

                # Информация о связанном документе
                doc_info = f"{link['counterparty_name']} {link['counterparty_opf']} - {link['contract_type']}"
                self.links_table.setItem(row, 1, QTableWidgetItem(doc_info))
                self.links_table.setItem(row, 2, QTableWidgetItem(link['contract_number']))
                self.links_table.setItem(row, 3, QTableWidgetItem(link['contract_date']))

                # Кнопка удаления связи
                delete_button = ModernButton("Удалить")
                delete_button.clicked.connect(lambda checked, link_id=link['id']: self.delete_link(link_id))

                # Устанавливаем кнопку в ячейку с помощью setCellWidget
                self.links_table.setCellWidget(row, 4, delete_button)
                # Устанавливаем высоту строки
                self.links_table.setRowHeight(row, 40)

    def delete_link(self, link_id):
        result = QMessageBox.question(self, "Подтверждение",
                                      "Вы уверены, что хотите удалить эту связь?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            if self.main_window and hasattr(self.main_window, 'delete_document_link'):
                self.main_window.delete_document_link(link_id)
                self.load_links()


class StageDialog(QDialog):
    def __init__(self, parent=None, stages=None):
        super().__init__(parent)
        self.setWindowTitle("Управление этапами")
        self.setModal(True)
        self.stages = stages if stages else []
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(600)
        layout = QVBoxLayout(self)
        self.setMinimumSize(500, 400)

        # Таблица этапов
        self.stages_table = QTableWidget()
        self.stages_table.setColumnCount(3)
        self.stages_table.setHorizontalHeaderLabels(["Описание", "Тип", "Значение"])
        self.stages_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.stages_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.stages_table.verticalHeader().setDefaultSectionSize(40)
        self.update_stages_table()
        layout.addWidget(self.stages_table)

        # Кнопки управления этапами
        buttons_layout = QHBoxLayout()

        add_button = ModernButton("Добавить этап")
        add_button.clicked.connect(self.add_stage)
        buttons_layout.addWidget(add_button)

        edit_button = ModernButton("Редактировать этап")
        edit_button.clicked.connect(self.edit_stage)
        buttons_layout.addWidget(edit_button)

        delete_button = ModernButton("Удалить этап")
        delete_button.clicked.connect(self.delete_stage)
        buttons_layout.addWidget(delete_button)

        layout.addLayout(buttons_layout)

        # Кнопки OK/Cancel
        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

    def update_stages_table(self):
        self.stages_table.setRowCount(len(self.stages))
        for row, stage in enumerate(self.stages):
            self.stages_table.setItem(row, 0, QTableWidgetItem(stage['description']))
            self.stages_table.setItem(row, 1, QTableWidgetItem(stage['type']))
            self.stages_table.setItem(row, 2, QTableWidgetItem(str(stage['value'])))
            self.stages_table.setRowHeight(row, 40)

    def add_stage(self):
        dialog = StageEditDialog(self)
        if dialog.exec():
            description, stage_type, value = dialog.get_stage_data()
            self.stages.append({
                'description': description,
                'type': stage_type,
                'value': value
            })
            self.update_stages_table()

    def edit_stage(self):
        current_row = self.stages_table.currentRow()
        if current_row >= 0:
            dialog = StageEditDialog(self, self.stages[current_row])
            if dialog.exec():
                description, stage_type, value = dialog.get_stage_data()
                self.stages[current_row] = {
                    'description': description,
                    'type': stage_type,
                    'value': value
                }
                self.update_stages_table()

    def delete_stage(self):
        current_row = self.stages_table.currentRow()
        if current_row >= 0:
            self.stages.pop(current_row)
            self.update_stages_table()

    def get_stages(self):
        return self.stages


class StageEditDialog(QDialog):
    def __init__(self, parent=None, stage=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/редактирование этапа")
        self.setModal(True)
        self.stage = stage
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.description_edit = QLineEdit()
        if self.stage:
            self.description_edit.setText(self.stage['description'])
        layout.addRow("Описание этапа:", self.description_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Процент", "Сумма"])
        if self.stage:
            self.type_combo.setCurrentText(self.stage['type'])
        layout.addRow("Тип значения:", self.type_combo)

        self.value_edit = QLineEdit()
        if self.stage:
            self.value_edit.setText(str(self.stage['value']))
        layout.addRow("Значение:", self.value_edit)

        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_stage_data(self):
        return self.description_edit.text(), self.type_combo.currentText(), self.value_edit.text()


class EmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка email")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.smtp_server = QLineEdit()
        self.smtp_server.setPlaceholderText("smtp.gmail.com")
        form_layout.addRow("SMTP сервер:", self.smtp_server)

        self.smtp_port = QLineEdit()
        self.smtp_port.setPlaceholderText("587")
        form_layout.addRow("SMTP порт:", self.smtp_port)

        # Добавляем выбор типа соединения
        self.connection_type = QComboBox()
        self.connection_type.addItems(["TLS", "SSL"])
        form_layout.addRow("Тип соединения:", self.connection_type)

        self.email_from = QLineEdit()
        self.email_from.setPlaceholderText("your.email@gmail.com")
        form_layout.addRow("Email отправителя:", self.email_from)

        self.email_password = QLineEdit()
        self.email_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль:", self.email_password)

        layout.addLayout(form_layout)

        # Кнопка для тестового письма
        self.test_button = ModernButton("Отправить тестове письмо")
        self.test_button.clicked.connect(self.send_test_email)
        layout.addWidget(self.test_button)

        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            'smtp_server': self.smtp_server.text(),
            'smtp_port': self.smtp_port.text(),
            'connection_type': self.connection_type.currentText(),
            'email_from': self.email_from.text(),
            'email_password': self.email_password.text()
        }

    def send_test_email(self):
        settings = self.get_settings()

        if not all([settings['smtp_server'], settings['smtp_port'],
                    settings['email_from'], settings['email_password']]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля настроек")
            return

        # Создаем и запускаем worker в отдельном потоке
        self.email_worker = EmailWorker(
            settings,
            [settings['email_from']],
            "Тестовое письмо от реестра договоров",
            "Это тестовое письмо, отправленное для проверки настроек электронной почты.",
            "<html><body>Это тестовое письмо, отправленное для проверки настроек электронной почты.</body></html>"
        )
        self.email_worker.finished.connect(self.handle_test_email_result)
        self.email_worker.start()

        # Показываем индикатор загрузки
        self.test_button.setEnabled(False)
        self.test_button.setText("Отправка...")

    def handle_test_email_result(self, success, message):
        self.test_button.setEnabled(True)
        self.test_button.setText("Отправить тестовое письмо")

        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)


class ContractFormWidget(QWidget):
    def __init__(self, parent=None, edit_mode=False, contract_id=None):
        super().__init__(parent)
        self.stages = []  # Список этапов договора
        self.main_window = parent  # Сохраняем ссылку на главное окно
        self.edit_mode = edit_mode
        self.contract_id = contract_id
        self.setup_ui()

        # Подключаем сигналы для автозаполнения
        self.contract_number.textChanged.connect(self.on_contract_data_changed)
        self.contract_date.dateChanged.connect(self.on_contract_data_changed)

    def on_contract_data_changed(self):
        """Автозаполнение данных при изменении номера или даты договора"""
        if self.edit_mode:
            return  # Не автозаполняем в режиме редактирования

        contract_number = self.contract_number.text().strip()
        contract_date = self.contract_date.date().toString("yyyy-MM-dd")

        if contract_number and contract_date:
            # Ищем договор в базе данных
            contract_data = self.main_window.find_contract(contract_number, contract_date)
            if contract_data:
                self.fill_form_from_existing(contract_data)

    def fill_form_from_existing(self, contract_data):
        """Заполнение формы данными из существующего договора"""
        # Заполняем основные поля
        self.counterparty_name.setText(contract_data.get('counterparty_name', ''))
        self.counterparty_opf.setCurrentText(contract_data.get('counterparty_opf', ''))
        self.counterparty_type.setCurrentText(contract_data.get('counterparty_type', ''))

        # Заполняем проект, если есть
        project_info = contract_data.get('project_info', '')
        if project_info:
            index = self.project_info.findText(project_info)
            if index >= 0:
                self.project_info.setCurrentIndex(index)
            else:
                self.project_info.setCurrentText(project_info)

        # Заполняем финансовые данные
        self.amount_edit.setText(str(contract_data.get('amount', '')))
        self.currency_combo.setCurrentText(contract_data.get('currency', 'RUB'))
        self.tax_edit.setText(str(contract_data.get('tax_percent', '')))

        # Заполняем аванс
        advance_value = contract_data.get('advance_value', '')
        if advance_value:
            self.advance_value_edit.setText(str(advance_value))
            self.advance_type_combo.setCurrentText(contract_data.get('advance_type', '%'))

        # Отмечаем аванс, если есть
        self.advance_checkbox.setChecked(bool(contract_data.get('has_advance', False)))

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # Создаем прокручиваемую область
        scroll_area = ModernScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f0f0f0;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
                border-radius: 5px;
            }
        """)
        scroll_content = QWidget()
        scroll_content.setMinimumWidth(600)  # Добавьте эту строку
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_area.setWidget(scroll_content)

        # Тип документа
        type_group = QGroupBox("Тип документа")
        type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        type_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        type_layout = QVBoxLayout(type_group)
        self.doc_type = QComboBox()
        self.doc_type.addItems(["Договор", "Допсоглашение", "Приложение", "Спецификация", "Соглашение о расторжении"])
        self.doc_type.currentTextChanged.connect(self.on_doc_type_changed)
        type_layout.addWidget(self.doc_type)

        # Переключатель для типа приложения/спецификации
        self.doc_subtype_widget = QWidget()
        self.doc_subtype_layout = QHBoxLayout(self.doc_subtype_widget)
        self.doc_subtype_layout.setContentsMargins(0, 10, 0, 0)
        self.doc_subtype_label = QLabel("Тип документа:")
        self.doc_subtype_combo = QComboBox()
        self.doc_subtype_combo.addItems(["К договору", "К допсоглашению"])
        self.doc_subtype_combo.currentTextChanged.connect(self.on_doc_subtype_changed)
        self.doc_subtype_layout.addWidget(self.doc_subtype_label)
        self.doc_subtype_layout.addWidget(self.doc_subtype_combo)
        self.doc_subtype_layout.addStretch()
        self.doc_subtype_widget.setVisible(False)
        type_layout.addWidget(self.doc_subtype_widget)

        scroll_layout.addWidget(type_group)
        scroll_layout.addSpacing(15)

        # Информация о контрагенте
        counterparty_group = QGroupBox("Информация о контрагенте")
        counterparty_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        counterparty_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        counterparty_layout = QFormLayout(counterparty_group)
        counterparty_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        counterparty_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        counterparty_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.counterparty_name = QLineEdit()
        counterparty_layout.addRow("Наименование контрагента:", self.counterparty_name)

        self.counterparty_opf = QComboBox()
        self.counterparty_opf.addItems(
            ["ООО", "БФ", "ИП", "СЗ", "ГПХ", "ООО СЗ", "ООО БФ", "ТОО", "ПАО", "CO. LCC", "LCC", "АО", "НКО", "ГУП"])
        counterparty_layout.addRow("ОПФ контрагента:", self.counterparty_opf)

        self.counterparty_type = QComboBox()
        self.counterparty_type.addItems(["Клиент", "Поставщик", "Страховка", "Сборка"])
        counterparty_layout.addRow("Тип контрагента:", self.counterparty_type)

        scroll_layout.addWidget(counterparty_group)
        scroll_layout.addSpacing(15)

        # Информация о договоре
        contract_info_group = QGroupBox("Информация о Договоре")
        contract_info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        contract_info_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        contract_info_layout = QFormLayout(contract_info_group)
        contract_info_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        contract_info_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.contract_number = QLineEdit()
        contract_info_layout.addRow("Номер Договора:", self.contract_number)

        self.contract_date = QDateEdit()
        self.contract_date.setDate(QDate.currentDate())
        self.contract_date.setCalendarPopup(True)
        contract_info_layout.addRow("Дата Договора:", self.contract_date)

        self.project_info = QComboBox()
        self.project_info.setEditable(True)
        self.project_info.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.project_info.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        contract_info_layout.addRow("Проект/Объект/Объем работ:", self.project_info)

        # Добавлено поле для краткого описания
        self.brief_description = QLineEdit()
        contract_info_layout.addRow("Краткое описание:", self.brief_description)

        scroll_layout.addWidget(contract_info_group)
        scroll_layout.addSpacing(15)

        # Финансовая информация
        financial_group = QGroupBox("Финансовая информация")
        financial_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        financial_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        financial_layout = QFormLayout(financial_group)
        financial_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        financial_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.amount_edit = QLineEdit()
        financial_layout.addRow("Сумма документа:", self.amount_edit)

        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["RUB", "USD", "EUR", "KZT"])
        financial_layout.addRow("Валюта:", self.currency_combo)

        self.tax_edit = QLineEdit()
        financial_layout.addRow("Налог (%):", self.tax_edit)

        # Аванс с комбинированным полем
        advance_widget = QWidget()
        advance_layout = QHBoxLayout(advance_widget)
        advance_layout.setContentsMargins(0, 0, 0, 0)
        self.advance_value_edit = QLineEdit()
        self.advance_type_combo = QComboBox()
        self.advance_type_combo.addItems(["%", "Сумма"])
        advance_layout.addWidget(self.advance_value_edit)
        advance_layout.addWidget(self.advance_type_combo)
        financial_layout.addRow("Аванс:", advance_widget)

        # Кнопка управления этапами
        self.stages_button = ModernButton("Управление этапами")
        self.stages_button.clicked.connect(self.manage_stages)
        financial_layout.addRow("Этапы:", self.stages_button)

        scroll_layout.addWidget(financial_group)
        scroll_layout.addSpacing(15)

        # Дополнительная информация для допсоглашений
        self.supplementary_group = QGroupBox("Информация о допсоглашении")
        self.supplementary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        self.supplementary_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        supplementary_layout = QFormLayout(self.supplementary_group)
        supplementary_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        supplementary_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.supplementary_number = QLineEdit()
        supplementary_layout.addRow("Номер допсоглашения:", self.supplementary_number)

        self.supplementary_date = QDateEdit()
        self.supplementary_date.setDate(QDate.currentDate())
        self.supplementary_date.setCalendarPopup(True)
        supplementary_layout.addRow("Дата допсоглашения:", self.supplementary_date)

        self.supplementary_content = QTextEdit()
        self.supplementary_content.setFixedHeight(60)
        self.supplementary_content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        supplementary_layout.addRow("Содержание допсоглашения:", self.supplementary_content)

        self.supplementary_group.setVisible(False)
        scroll_layout.addWidget(self.supplementary_group)
        scroll_layout.addSpacing(15)

        # Дополнительная информация (для допсоглашений, приложений и спецификаций)
        self.additional_group = QGroupBox("Информация о документе")
        self.additional_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f8f8f8;
            }
        """)
        self.additional_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        additional_layout = QFormLayout(self.additional_group)
        additional_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        additional_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.additional_number = QLineEdit()
        additional_layout.addRow("Номер:", self.additional_number)

        self.additional_date = QDateEdit()
        self.additional_date.setDate(QDate.currentDate())
        self.additional_date.setCalendarPopup(True)
        additional_layout.addRow("Дата:", self.additional_date)

        self.additional_content = QTextEdit()
        self.additional_content.setFixedHeight(100)
        self.additional_content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        additional_layout.addRow("Содержание:", self.additional_content)

        self.additional_group.setVisible(False)
        scroll_layout.addWidget(self.additional_group)
        scroll_layout.addSpacing(15)

        # Добавляем растягивающий элемент в конец
        scroll_layout.addStretch()

        layout.addWidget(scroll_area)

    def on_doc_type_changed(self, text):
        # Показываем/скрываем дополнительные поля в зависимости от типа документа
        if text == "Договор":
            self.additional_group.setVisible(False)
            self.supplementary_group.setVisible(False)
            self.doc_subtype_widget.setVisible(False)
            self.additional_group.setTitle("Информация о документе")
        elif text == "Допсоглашение":
            self.additional_group.setVisible(True)
            self.supplementary_group.setVisible(False)
            self.doc_subtype_widget.setVisible(False)
            self.additional_group.setTitle("Информация о допсоглашении")
        elif text == "Соглашение о расторжении":
            self.additional_group.setVisible(True)
            self.supplementary_group.setVisible(False)
            self.doc_subtype_widget.setVisible(False)
            self.additional_group.setTitle("Информация о соглашении о расторжении")
        elif text in ["Приложение", "Спецификация"]:
            self.doc_subtype_widget.setVisible(True)
            self.doc_subtype_label.setText(f"Тип {text.lower()}:")
            self.on_doc_subtype_changed(self.doc_subtype_combo.currentText())
            self.additional_group.setTitle(f"Информация о {text.lower()}")

    def on_doc_subtype_changed(self, text):
        if self.doc_type.currentText() in ["Приложение", "Спецификация"]:
            if text == "К договору":
                self.additional_group.setVisible(True)
                self.supplementary_group.setVisible(False)
            else:  # К допсоглашению
                self.additional_group.setVisible(True)
                self.supplementary_group.setVisible(True)

    def manage_stages(self):
        dialog = StageDialog(self, self.stages)
        if dialog.exec():
            self.stages = dialog.get_stages()

    def clear_form(self):
        self.counterparty_name.clear()
        self.counterparty_opf.setCurrentIndex(0)
        self.counterparty_type.setCurrentIndex(0)
        self.contract_number.clear()
        self.contract_date.setDate(QDate.currentDate())
        self.project_info.clear()
        self.brief_description.clear()  # Добавлено
        self.supplementary_number.clear()
        self.supplementary_date.setDate(QDate.currentDate())
        self.supplementary_content.clear()
        self.additional_number.clear()
        self.additional_date.setDate(QDate.currentDate())
        self.additional_content.clear()
        self.amount_edit.clear()
        self.currency_combo.setCurrentIndex(0)
        self.tax_edit.clear()
        self.advance_value_edit.clear()
        self.advance_type_combo.setCurrentIndex(0)
        self.stages = []
        self.doc_type.setCurrentIndex(0)
        self.doc_subtype_combo.setCurrentIndex(0)
        self.doc_subtype_widget.setVisible(False)

    def fill_form(self, data):
        """Заполняет форму данными из БД"""
        self.clear_form()

        # Заполняем основные поля
        self.doc_type.setCurrentText(data['contract_type'])
        self.counterparty_name.setText(data['counterparty_name'])
        self.counterparty_opf.setCurrentText(data['counterparty_opf'])
        self.counterparty_type.setCurrentText(data['counterparty_type'])
        self.contract_number.setText(data['contract_number'])
        self.contract_date.setDate(QDate.fromString(data['contract_date'], "yyyy-MM-dd"))

        if data['project_info'] and self.main_window:
            # Используем главное окно для выполнения запроса
            project = self.main_window.get_project_by_id(data.get('project_id'))
            if project:
                project_text = f"{project[1]}, {project[2]}, {project[3]}, {project[4]}"
                self.project_info.setCurrentText(project_text)

        # Заполняем краткое описание
        if 'brief_description' in data and data['brief_description']:
            self.brief_description.setText(data['brief_description'])

        # Финансовая информация
        self.amount_edit.setText(str(data['amount']) if data['amount'] else "")
        self.currency_combo.setCurrentText(data['currency'] if data['currency'] else "RUB")
        self.tax_edit.setText(str(data['tax_percent']) if data['tax_percent'] else "")
        self.advance_value_edit.setText(str(data['advance_value']) if data['advance_value'] else "")
        self.advance_type_combo.setCurrentText(data['advance_type'] if data['advance_type'] else "%")

        # Дополнительная информация для допсоглашений и приложений
        if data['contract_type'] == "Допсоглашение":
            self.additional_number.setText(data['additional_number'])
            self.additional_date.setDate(QDate.fromString(data['additional_date'], "yyyy-MM-dd") if data[
                'additional_date'] else QDate.currentDate())
            self.additional_content.setText(data['additional_content'])
        elif data['contract_type'] in ["Приложение", "Спецификация"]:
            self.doc_subtype_combo.setCurrentText(data['app_type'])
            self.additional_number.setText(data['additional_number'])
            self.additional_date.setDate(QDate.fromString(data['additional_date'], "yyyy-MM-dd") if data[
                'additional_date'] else QDate.currentDate())
            self.additional_content.setText(data['additional_content'])

            if data['app_type'] == "К допсоглашению":
                self.supplementary_number.setText(data['supplementary_number'])
                self.supplementary_date.setDate(QDate.fromString(data['supplementary_date'], "yyyy-MM-dd") if data[
                    'supplementary_date'] else QDate.currentDate())
                self.supplementary_content.setText(data['supplementary_content'])

        # Загружаем этапы
        if self.main_window and self.contract_id:
            self.stages = self.main_window.get_contract_stages(self.contract_id)

        # Обновляем видимость полей в зависимости от типа документа
        self.on_doc_type_changed(data['contract_type'])

    def get_form_data(self):
        """Возвращает все данные формы в виде словаря"""
        return {
            'doc_type': self.doc_type.currentText(),
            'doc_subtype': self.doc_subtype_combo.currentText() if self.doc_type.currentText() in ["Приложение",
                                                                                                   "Спецификация"] else "",
            'counterparty_name': self.counterparty_name.text(),
            'counterparty_opf': self.counterparty_opf.currentText(),
            'counterparty_type': self.counterparty_type.currentText(),
            'contract_number': self.contract_number.text(),
            'contract_date': self.contract_date.date().toString("yyyy-MM-dd"),
            'project_info': self.project_info.currentText(),
            'brief_description': self.brief_description.text(),  # Добавлено поле
            'supplementary_number': self.supplementary_number.text(),
            'supplementary_date': self.supplementary_date.date().toString("yyyy-MM-dd"),
            'supplementary_content': self.supplementary_content.toPlainText(),
            'additional_number': self.additional_number.text(),
            'additional_date': self.additional_date.date().toString("yyyy-MM-dd"),
            'additional_content': self.additional_content.toPlainText(),
            'amount': self.amount_edit.text(),
            'currency': self.currency_combo.currentText(),
            'tax': self.tax_edit.text(),
            'advance_value': self.advance_value_edit.text(),
            'advance_type': self.advance_type_combo.currentText(),
            'stages': self.stages
        }


class ProjectDialog(QDialog):
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/редактирование проекта")
        self.setModal(True)
        self.project_data = project_data
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.project_number = QLineEdit()
        layout.addRow("Номер проекта:", self.project_number)

        self.project_name = QLineEdit()
        layout.addRow("Название проекта:", self.project_name)

        self.object_address = QLineEdit()
        layout.addRow("Адрес объекта:", self.object_address)

        # Заполняем форму, если переданы данные
        if self.project_data:
            self.fill_form(self.project_data)

        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def fill_form(self, data):
        self.project_number.setText(data.get('project_number', ''))
        self.project_name.setText(data.get('project_name', ''))
        self.object_address.setText(data.get('object_address', ''))

    def get_project_data(self):
        return {
            'project_number': self.project_number.text(),
            'project_name': self.project_name.text(),
            'object_address': self.object_address.text()
        }


class AutoFillDialog(QDialog):
    def __init__(self, extracted_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтверждение извлеченных данных")
        self.extracted_data = extracted_data
        self.corrected_data = extracted_data.copy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel("Были извлечены следующие данные из документа:")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        self.fields = {}
        for field_name, value in self.extracted_data.items():
            label = QLabel(field_name.replace('_', ' ').title() + ":")
            line_edit = QLineEdit(str(value))
            self.fields[field_name] = line_edit
            form_layout.addRow(label, line_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_corrected_data(self):
        for field_name, line_edit in self.fields.items():
            self.corrected_data[field_name] = line_edit.text()
        return self.corrected_data


class GenerateNumberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация внутреннего номера договора")
        self.setModal(True)
        self.generated_number = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Выбор типа договора
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип договора:"))
        self.contract_type = QComboBox()
        self.contract_type.addItems(["Доходный", "Расходный"])
        self.contract_type.currentTextChanged.connect(self.update_code_options)
        type_layout.addWidget(self.contract_type)
        layout.addLayout(type_layout)

        # Выбор буквенного кода
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("Буквенный код:"))
        self.code_combo = QComboBox()
        code_layout.addWidget(self.code_combo)
        layout.addLayout(code_layout)

        # Обновляем варианты кодов при инициализации
        self.update_code_options()

        # Сгенерированный номер
        self.number_label = QLabel("Сгенерированный номер появится здесь")
        self.number_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.number_label)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.generate_button = ModernButton("Сгенерировать номер")
        self.generate_button.clicked.connect(self.generate_number)
        buttons_layout.addWidget(self.generate_button)

        self.copy_button = ModernButton("Копировать номер")
        self.copy_button.clicked.connect(self.copy_number)
        self.copy_button.setEnabled(False)
        buttons_layout.addWidget(self.copy_button)

        close_button = ModernButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)

        layout.addLayout(buttons_layout)

    def update_code_options(self):
        contract_type = self.contract_type.currentText()
        self.code_combo.clear()

        if contract_type == "Доходный":
            self.code_combo.addItems(["У", "Т"])  # Услуги, Товары
        else:  # Расходный
            self.code_combo.addItems(["СЗ", "ГПХ", "ИП", "КМ"])  # Самозанятый, ГПХ, ИП, Коммерция

    def generate_number(self):
        # Получаем максимальный номер из БД
        max_number = self.parent().get_max_internal_number()

        # Извлекаем порядковый номер
        if max_number:
            try:
                serial_part = max_number.split('-')[0]
                next_serial = int(serial_part) + 1
            except:
                next_serial = 1
        else:
            next_serial = 1

        # Форматируем порядковый номер
        serial_str = f"{next_serial:03d}"

        # Текущий месяц и год
        current_date = datetime.now()
        month_year = current_date.strftime("%m%y")  # ММГГ

        # Буквенный код
        code = self.code_combo.currentText()

        # Формируем полный номер
        self.generated_number = f"{serial_str}-{month_year}-{code}"
        self.number_label.setText(self.generated_number)
        self.copy_button.setEnabled(True)

    def copy_number(self):
        if self.generated_number:
            QApplication.clipboard().setText(self.generated_number)
            QMessageBox.information(self, "Успех", "Номер скопирован в буфер обмена")


class ArchiveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Архивация документа")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.folder_name = QLineEdit()
        layout.addRow("Наименование папки:", self.folder_name)

        self.box_number = QLineEdit()
        layout.addRow("Номер короба:", self.box_number)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return self.folder_name.text(), self.box_number.text()

class ContractManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Реестр договоров EDA")

        # Получаем размер экрана с учетом панели задач
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Устанавливаем размер окна (90% от доступного экрана)
        width = int(screen_geometry.width() * 0.9)
        height = int(screen_geometry.height() * 0.9)
        self.setGeometry(100, 100, width, height)

        self.email_settings = {}
        self.email_recipients = []  # Список email-адресов
        self.setup_database()
        self.current_files = []
        self.batch_files = []  # отдельный список для пакетной загрузки
        self.batch_index = 0
        self.batch_mode = False
        self.batch_form_widget = None  # Будем создавать новый виджет для каждой формы
        self.stages = []  # Список этапов договора
        self.current_edit_id = None  # ID документа в режиме редактирования

        self.projects_search_filter = ""
        self.projects_sort_column = 0
        self.projects_sort_order = Qt.SortOrder.AscendingOrder

        self.income_filter_text = ""
        self.expense_filter_text = ""
        self.income_sort_column = 0
        self.income_sort_order = Qt.SortOrder.AscendingOrder
        self.expense_sort_column = 0
        self.expense_sort_order = Qt.SortOrder.AscendingOrder

        ## Загружаем настройки
        self.load_email_settings()
        self.load_email_recipients()

        # Инициализация UI
        self.init_ui()

        # Центрируем окно на экране
        self.center_on_screen()

        self.selected_project_data = None

    def find_contract(self, contract_number, contract_date):
        """Поиск договора по номеру и дате"""
        try:
            self.cursor.execute("""
                SELECT * FROM contracts 
                WHERE contract_number = ? AND contract_date = ?
                ORDER BY upload_date DESC 
                LIMIT 1
            """, (contract_number, contract_date))

            contract = self.cursor.fetchone()
            if contract:
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, contract))
        except Exception as e:
            print(f"Ошибка при поиске договора: {e}")
        return None

    def extract_text_from_file(self, file_path):
        """Извлечение текста из файла для автозаполнения"""
        text = ""
        try:
            if file_path.lower().endswith('.pdf') and PyPDF2:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"

            elif file_path.lower().endswith(('.doc', '.docx')) and Document:
                doc = Document(file_path)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"

            elif file_path.lower().endswith(('.xls', '.xlsx')):
                # Для Excel файлов пытаемся прочитать все листы
                df = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, sheet_data in df.items():
                    text += f"--- {sheet_name} ---\n"
                    text += sheet_data.to_string() + "\n\n"

            else:
                # Пробуем прочитать как текстовый файл
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    text = file.read()

        except Exception as e:
            print(f"Ошибка при извлечении текста из файла: {e}")

        return text

    def parse_contract_data(self, text):
        """Улучшенное извлечение данных договора из текста"""
        data = {}

        # Поиск номера договора (более гибкий паттерн)
        number_patterns = [
            r'договор[а-я]*\s*[№n]?\s*([\w\/\-\.]+)',  # Русский и английский №
            r'contract\s*(?:no\.?|number)?\s*([\w\/\-\.]+)',  # Английские варианты
            r'дог\.?\s*[№n]?\s*([\w\/\-\.]+)'  # Сокращенный вариант
        ]

        for pattern in number_patterns:
            number_match = re.search(pattern, text, re.IGNORECASE)
            if number_match:
                data['contract_number'] = number_match.group(1).strip()
                break

        # Поиск даты договора (разные форматы)
        date_patterns = [
            r'от\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',  # дд.мм.гггг
            r'дата[:\s]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'contract date[:\s]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'(\d{1,2}\s+[а-я]+\s+\d{4})'  # "15 января 2023"
        ]

        months = {
            'январ': '01', 'феврал': '02', 'март': '03', 'апрел': '04',
            'мая': '05', 'июн': '06', 'июл': '07', 'август': '08',
            'сентябр': '09', 'октябр': '10', 'ноябр': '11', 'декабр': '12'
        }

        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1)
                try:
                    # Обработка формата "15 января 2023"
                    if re.search(r'[а-я]', date_str, re.IGNORECASE):
                        for month_name, month_num in months.items():
                            if month_name in date_str.lower():
                                date_str = re.sub(
                                    r'[а-я]+',
                                    f'.{month_num}.',
                                    date_str,
                                    flags=re.IGNORECASE
                                )
                                break

                    # Преобразование в стандартный формат
                    date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                    data['contract_date'] = date_obj.strftime('%Y-%m-%d')
                    break
                except:
                    continue

        # Поиск контрагента (улучшенный)
        counterparty_patterns = [
            r'между\s+(.+?)\s+и\s+',  # "между ООО Ромашка и ..."
            r'([А-ЯЁ][А-Яа-яё\s]+\s+[ООО|ЗАО|АО|ИП])',  # Юридические формы
            r'([А-ЯЁ][А-Яа-яё\s]+)\s+именуем',  # "ООО Ромашка именуем"
            r'company[:\s]+([^\n]+)',  # Английский вариант
        ]

        for pattern in counterparty_patterns:
            counterparty_match = re.search(pattern, text, re.IGNORECASE)
            if counterparty_match:
                data['counterparty_name'] = counterparty_match.group(1).strip()
                break

        # Поиск суммы (разные форматы)
        sum_patterns = [
            r'сумм[а-я]*\s*[:\s]*([\d\s,]+\.?\d*)\s*([₽$€]|руб|USD|EUR|RUB)',
            r'amount[:\s]*([\d\s,]+\.?\d*)\s*([₽$€]|руб|USD|EUR|RUB)',
            r'цена\s*договора[:\s]*([\d\s,]+\.?\d*)\s*([₽$€]|руб|USD|EUR|RUB)',
            r'total[:\s]*([\d\s,]+\.?\d*)\s*([₽$€]|руб|USD|EUR|RUB)'
        ]

        for pattern in sum_patterns:
            sum_match = re.search(pattern, text, re.IGNORECASE)
            if sum_match:
                amount = sum_match.group(1).replace(' ', '').replace(',', '.')
                currency = sum_match.group(2)

                # Нормализация валюты
                currency_map = {
                    '₽': 'RUB', 'руб': 'RUB', 'RUB': 'RUB',
                    '$': 'USD', 'USD': 'USD',
                    '€': 'EUR', 'EUR': 'EUR'
                }

                data['amount'] = amount
                data['currency'] = currency_map.get(currency, 'RUB')
                break

        return data

    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы договора", "",
            "Все файлы (*);;Документы (*.doc *.docx *.pdf *.xls *.xlsx);;Изображения (*.jpg *.png)"
        )
        if file_paths:
            self.current_files.extend(file_paths)
            self.update_files_list()
            self.view_file_button.setEnabled(True)
            self.upload_button.setEnabled(True)

            # Пытаемся извлечь данные из первого файла для автозаполнения
            if len(self.current_files) == 1:  # Только для первого файла
                self.auto_fill_from_file(file_paths[0])

    def auto_fill_from_file(self, file_path):
        """Автозаполнение формы из файла с подтверждением"""
        try:
            # Извлекаем текст из файла
            text = self.extract_text_from_file(file_path)
            if not text:
                return

            # Парсим данные из текста
            contract_data = self.parse_contract_data(text)

            if contract_data:
                # Показываем диалог для подтверждения/редактирования
                dialog = AutoFillDialog(contract_data, self)
                if dialog.exec():
                    corrected_data = dialog.get_corrected_data()

                    # Заполняем форму исправленными данными
                    if 'contract_number' in corrected_data:
                        self.main_form.contract_number.setText(corrected_data['contract_number'])

                    if 'contract_date' in corrected_data:
                        try:
                            date = QDate.fromString(corrected_data['contract_date'], "yyyy-MM-dd")
                            if date.isValid():
                                self.main_form.contract_date.setDate(date)
                        except:
                            pass

                    if 'counterparty_name' in corrected_data:
                        self.main_form.counterparty_name.setText(corrected_data['counterparty_name'])

                    if 'amount' in corrected_data:
                        self.main_form.amount_edit.setText(corrected_data['amount'])

                    if 'currency' in corrected_data:
                        index = self.main_form.currency_combo.findText(corrected_data['currency'])
                        if index >= 0:
                            self.main_form.currency_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"Ошибка при автозаполнении из файла: {e}")

    def sort_projects(self, index):
        """Изменяет поле для сортировки проектов"""
        self.projects_sort_column = index
        self.update_projects_cards()

    def toggle_sort_order(self):
        """Переключает порядок сортировки"""
        if self.projects_sort_order == Qt.SortOrder.AscendingOrder:
            self.projects_sort_order = Qt.SortOrder.DescendingOrder
            self.projects_sort_order_btn.setText("По убыванию")
        else:
            self.projects_sort_order = Qt.SortOrder.AscendingOrder
            self.projects_sort_order_btn.setText("По возрастанию")
        self.update_projects_cards()

    def on_project_card_clicked(self, project_data):
        """Обработчик клика по карточке проекта"""
        self.selected_project_data = project_data

    def get_project_id(self, project_info):
        """Получает ID проекта на основе информации о проекте"""
        if not project_info:
            return None

        # project_info может быть в формате "номер, название, адрес, ..."
        # мы будем искать по номеру проекта (первая часть до запятой)
        project_number = project_info.split(',')[0].strip()

        self.cursor.execute("SELECT id FROM projects WHERE project_number = ?", (project_number,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_project_by_id(self, project_id):
        """Получает проект по ID"""
        if not project_id:
            return None
        self.cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        return self.cursor.fetchone()

    def import_projects_from_excel(self):
        """Импорт проектов из Excel файла - только номер, название и адрес"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл Excel", "", "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            # Читаем оба листа из Excel файла
            df_2025 = pd.read_excel(file_path, sheet_name='2025')
            df_2024 = pd.read_excel(file_path, sheet_name='2024')

            # Объединяем данные из обоих листов
            df = pd.concat([df_2025, df_2024], ignore_index=True)

            # Оставляем только нужные столбцы
            required_columns = {
                'Проект_ номер папки': 'project_number',
                'Проект_ название': 'project_name',
                'Адрес объекта': 'object_address'
            }

            # Переименовываем столбцы и оставляем только нужные
            df = df.rename(columns=required_columns)
            df = df[list(required_columns.values())]

            # Удаляем пустые строки и преобразуем данные
            df = df.dropna(how='all')
            df = df.fillna('')

            # Импортируем данные
            success_count = 0
            error_count = 0
            errors = []

            for _, row in df.iterrows():
                try:
                    project_data = {
                        'project_number': str(row['project_number']) if pd.notna(row['project_number']) else '',
                        'project_name': str(row['project_name']) if pd.notna(row['project_name']) else '',
                        'object_address': str(row['object_address']) if pd.notna(row['object_address']) else ''
                    }

                    # Проверяем, что номер проекта указан
                    if not project_data['project_number']:
                        raise ValueError("Не указан номер проекта")

                    # Сохраняем в базу данных
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO projects (
                            project_number, project_name, object_address
                        ) VALUES (?, ?, ?)
                    ''', (
                        project_data['project_number'],
                        project_data['project_name'],
                        project_data['object_address']
                    ))
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Строка {_ + 2}: {str(e)}")

            self.conn.commit()

            # Показываем результат импорта
            message = f"Импорт завершен!\nУспешно: {success_count}\nОшибок: {error_count}"
            if errors:
                message += "\n\nОшибки:\n" + "\n".join(errors[:10])
                if error_count > 10:
                    message += f"\n... и еще {error_count - 10} ошибок"

            QMessageBox.information(self, "Результат импорта", message)

            # Обновляем таблицу
            self.update_projects_cards()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать файл Excel: {str(e)}")

    def update_buttons_state(self):
        """Обновляет состояние кнопок в зависимости от режима (редактирование/новая загрузка)"""
        try:
            if not hasattr(self, 'upload_button') or not self.upload_button:
                return  # Кнопка ещё не создана

            if self.current_edit_id is not None:
                self.upload_button.setEnabled(True)
                self.upload_button.setText("Сохранить изменения")
            else:
                self.upload_button.setEnabled(len(self.current_files) > 0)
                self.upload_button.setText("Загрузить договор")

            if hasattr(self, 'view_file_button') and self.view_file_button:
                self.view_file_button.setEnabled(len(self.current_files) > 0)
        except RuntimeError as e:
            print(f"Ошибка обновления кнопок: {e}")

    def load_email_recipients(self):
        """Загружает список email-адресов из файла"""
        try:
            with open('email_recipients.txt', 'r', encoding='utf-8') as f:
                self.email_recipients = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.email_recipients = []

    def save_email_recipients(self):
        """Сохраняет список email-адресов в файл"""
        with open('email_recipients.txt', 'w', encoding='utf-8') as f:
            for email in self.email_recipients:
                f.write(f"{email}\n")

    def add_email_recipient(self):
        """Добавляет новый email-адрес в список"""
        email, ok = QInputDialog.getText(self, "Добавить email", "Введите email адрес:")
        if ok and email:
            if email not in self.email_recipients:
                self.email_recipients.append(email)
                self.update_email_list()
                self.save_email_recipients()

    def remove_email_recipient(self):
        """Удаляет выбранный email-адрес из спика"""
        current_row = self.email_list.currentRow()
        if current_row >= 0:
            self.email_recipients.pop(current_row)
            self.update_email_list()
            self.save_email_recipients()

    def update_email_list(self):
        """Обновляет список email-адресов в интерфейсе"""
        self.email_list.clear()
        for email in self.email_recipients:
            self.email_list.addItem(email)

    # Переместите метод load_email_settings сюда
    def load_email_settings(self):
        try:
            with open('email_settings.txt', 'r') as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    self.email_settings[key] = value
        except FileNotFoundError:
            pass

    def save_email_settings(self):
        with open('email_settings.txt', 'w') as f:
            for key, value in self.email_settings.items():
                f.write(f"{key}={value}\n")

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def setup_database(self):
        self.conn = sqlite3.connect('contracts.db')
        self.cursor = self.conn.cursor()

        # Создание таблицы contracts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_type TEXT,
                app_type TEXT,
                counterparty_name TEXT,
                counterparty_opf TEXT,
                contract_number TEXT,
                contract_date TEXT,
                project_info TEXT,
                brief_description TEXT,  -- Добавлен столбец для краткого описания
                supplementary_number TEXT,
                supplementary_date TEXT,
                supplementary_content TEXT,
                additional_number TEXT,
                additional_date TEXT,
                additional_content TEXT,
                has_advance INTEGER,
                file_path TEXT,
                original_file_name TEXT,
                editable INTEGER,
                upload_date TEXT,
                counterparty_type TEXT,
                amount REAL,
                currency TEXT,
                tax_percent REAL,
                advance_value REAL,
                advance_type TEXT,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Добавьте этот код для добавления столбца, если он не существует
        try:
            self.cursor.execute("PRAGMA table_info(contracts)")
            columns = [column[1] for column in self.cursor.fetchall()]
            if 'project_id' not in columns:
                self.cursor.execute('ALTER TABLE contracts ADD COLUMN project_id INTEGER')
                self.conn.commit()
                print("Добавлен столбец project_id в таблицу contracts")
        except Exception as e:
            print(f"Ошибка при добавлении столбца project_id: {e}")

        # Таблица для хранения этапов договора
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contract_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                description TEXT,
                type TEXT,
                value TEXT,
                FOREIGN KEY (contract_id) REFERENCES contracts (id)
            )
        ''')

        # Таблица для хранения связей между документами
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_doc_id INTEGER,
                target_doc_id INTEGER,
                link_type TEXT,
                created_date TEXT,
                FOREIGN KEY (source_doc_id) REFERENCES contracts (id),
                FOREIGN KEY (target_doc_id) REFERENCES contracts (id)
            )
        ''')

        # Таблица для хранения проектов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_number TEXT UNIQUE,
                project_name TEXT,
                contract_number TEXT,
                client TEXT,
                object_name TEXT,
                object_address TEXT,
                work_scope TEXT,
                copies_count TEXT,
                authorized_email TEXT,
                delivery_procedure TEXT,
                contact_person TEXT,
                cipher TEXT,
                responsible_eda TEXT,
                substitute_eda TEXT,
                email_delivery_date TEXT,
                paper_delivery_date TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS archived_contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                folder_name TEXT,
                box_number TEXT,
                archive_date TEXT,
                FOREIGN KEY (contract_id) REFERENCES contracts (id)
            )
        ''')

        self.conn.commit()

    def setup_autocompletion(self):
        """Настраивает автодополнение для полей ввода"""
        # Добавить проверку на существование виджетов
        if hasattr(self, 'main_form') and self.main_form:
            # Автодополнение для наименования контрагента
            self.cursor.execute("SELECT DISTINCT counterparty_name FROM contracts")
            counterparties = [row[0] for row in self.cursor.fetchall()]
            counterparty_completer = QCompleter(counterparties)
            counterparty_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.main_form.counterparty_name.setCompleter(counterparty_completer)

            # Автодополнение для проекта/объекта
            self.cursor.execute("SELECT DISTINCT project_info FROM contracts WHERE project_info != ''")
            projects = [row[0] for row in self.cursor.fetchall()]
            project_completer = QCompleter(projects)
            project_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.main_form.project_info.setCompleter(project_completer)

    def filter_projects(self):
        """Фильтрует проекты по введенным текстам в полях поиска"""
        # Получаем тексты из всех полей поиска
        number_filter = self.projects_search_number_edit.text().strip().lower()
        name_filter = self.projects_search_name_edit.text().strip().lower()
        address_filter = self.projects_search_address_edit.text().strip().lower()

        # Базовый запрос
        query = "SELECT * FROM projects"
        params = []
        conditions = []

        # Добавляем условия для каждого поля поиска
        if number_filter:
            conditions.append("LOWER(project_number) LIKE ?")
            params.append(f"%{number_filter}%")  # Ищем в любой части номера

        if name_filter:
            conditions.append("LOWER(project_name) LIKE ?")
            params.append(f"%{name_filter}%")  # Ищем в любой части названия

        if address_filter:
            conditions.append("LOWER(object_address) LIKE ?")
            params.append(f"%{address_filter}%")  # Ищем в любой части адреса

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Добавляем сортировку
        sort_columns = ["project_number", "project_name", "object_address"]
        if self.projects_sort_column < len(sort_columns):
            order = "ASC" if self.projects_sort_order == Qt.SortOrder.AscendingOrder else "DESC"

            # Особый случай для числовой сортировки номеров проектов
            if sort_columns[self.projects_sort_column] == "project_number":
                query += f" ORDER BY CAST(project_number AS INTEGER) {order}, project_number {order}"
            else:
                query += f" ORDER BY {sort_columns[self.projects_sort_column]} {order}"

        self.cursor.execute(query, params)
        projects = self.cursor.fetchall()

        # Очищаем текущие карточки
        for i in reversed(range(self.projects_grid_layout.count())):
            widget = self.projects_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Получаем названия колонок
        columns = [description[0] for description in self.cursor.description]

        # Создаем карточки для каждого проекта
        for i, project in enumerate(projects):
            # Преобразуем в словарь
            project_data = dict(zip(columns, project))

            # Создаем карточку
            card = ProjectCard(project_data, self)
            card.clicked.connect(self.on_project_card_clicked)

            # Добавляем карточку в сетку (3 колонки)
            row = i // 3
            col = i % 3
            self.projects_grid_layout.addWidget(card, row, col)

    def sort_projects(self, index):
        """Изменяет поле для сортировки проектов"""
        self.projects_sort_column = index
        self.update_projects_cards()

    def toggle_sort_order(self):
        """Переключает порядок сортировки"""
        if self.projects_sort_order == Qt.SortOrder.AscendingOrder:
            self.projects_sort_order = Qt.SortOrder.DescendingOrder
            self.projects_sort_order_btn.setText("По убыванию")
        else:
            self.projects_sort_order = Qt.SortOrder.AscendingOrder
            self.projects_sort_order_btn.setText("По возрастанию")
        self.update_projects_cards()

    def update_projects_cards(self):
        """Обновляет отображение карточек проектов с учетом фильтров и сортировки"""
        # Очищаем текущие карточки
        for i in reversed(range(self.projects_grid_layout.count())):
            widget = self.projects_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Базовый запрос
        query = "SELECT * FROM projects"
        params = []
        conditions = []

        # Улучшенный поиск с учетом большего количества полей
        if self.projects_search_filter:
            search_pattern = f"%{self.projects_search_filter}%"
            # Добавляем больше полей для поиска
            search_fields = [
                'project_number', 'project_name', 'object_address',
                'client', 'object_name', 'work_scope', 'contact_person',
                'contract_number', 'cipher', 'responsible_eda', 'substitute_eda'
            ]

            search_conditions = []
            for field in search_fields:
                search_conditions.append(f"{field} LIKE ?")
                params.append(search_pattern)

            conditions.append("(" + " OR ".join(search_conditions) + ")")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Улучшенная сортировка
        sort_columns = ["project_number", "project_name", "object_address"]
        if self.projects_sort_column < len(sort_columns):
            order = "ASC" if self.projects_sort_order == Qt.SortOrder.AscendingOrder else "DESC"

            # Особый случай для числовой сортировки номеров проектов
            if sort_columns[self.projects_sort_column] == "project_number":
                # Пытаемся извлечь числовую часть из номера проекта для правильной сортировки
                query += f" ORDER BY CAST(project_number AS INTEGER) {order}, project_number {order}"
            else:
                query += f" ORDER BY {sort_columns[self.projects_sort_column]} {order}"

        self.cursor.execute(query, params)
        projects = self.cursor.fetchall()

        # Получаем названия колонок
        columns = [description[0] for description in self.cursor.description]

        # Создаем карточки для каждого проекта
        for i, project in enumerate(projects):
            # Преобразуем в словарь
            project_data = dict(zip(columns, project))

            # Создаем карточку
            card = ProjectCard(project_data, self)
            card.clicked.connect(self.on_project_card_clicked)

            # Добавляем карточку в сетку (3 колонки)
            row = i // 3
            col = i % 3
            self.projects_grid_layout.addWidget(card, row, col)

    # Добавим метод для показа деталей проекта
    def show_project_details(self, project_data):
        dialog = ProjectDetailsDialog(project_data, self)
        dialog.exec()

    def update_projects_combo(self):
        """Обновляет список проектов в комбобоксе"""
        current_text = self.main_form.project_info.currentText()
        self.main_form.project_info.clear()

        self.cursor.execute("SELECT project_number, project_name FROM projects ORDER BY project_number")
        projects = self.cursor.fetchall()

        for project in projects:
            display_text = f"{project[0]}, {project[1]}"
            self.main_form.project_info.addItem(display_text)

        if current_text:
            index = self.main_form.project_info.findText(current_text)
            if index >= 0:
                self.main_form.project_info.setCurrentIndex(index)
            else:
                self.main_form.project_info.setCurrentText(current_text)

    def add_project(self):
        dialog = ProjectDialog(self)
        if dialog.exec():
            project_data = dialog.get_project_data()

            # Проверяем, что номер проекта указан
            if not project_data['project_number']:
                QMessageBox.warning(self, "Ошибка", "Необходимо указать номер проекта")
                return

            try:
                self.cursor.execute('''
                    INSERT INTO projects (
                        project_number, project_name, object_address
                    ) VALUES (?, ?, ?)
                ''', (
                    project_data['project_number'],
                    project_data['project_name'],
                    project_data['object_address']
                ))
                self.conn.commit()
                self.update_projects_cards()
                self.update_projects_combo()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", "Проект с таким номером уже существует")

    def edit_project(self):
        try:
            # Проверяем, выбран ли проект
            if not self.selected_project_data:
                QMessageBox.warning(self, "Ошибка", "Выберите проект для редактирования")
                return

            project_number = self.selected_project_data['project_number']

            self.cursor.execute(
                "SELECT project_number, project_name, object_address FROM projects WHERE project_number = ?",
                (project_number,))
            project_data = self.cursor.fetchone()

            if not project_data:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти данные проекта")
                return

            # Преобразуем данные в словарь
            project_dict = {
                'project_number': project_data[0],
                'project_name': project_data[1],
                'object_address': project_data[2]
            }

            dialog = ProjectDialog(self, project_dict)
            if dialog.exec():
                updated_data = dialog.get_project_data()

                try:
                    self.cursor.execute('''
                        UPDATE projects SET
                            project_number = ?, project_name = ?, object_address = ?
                        WHERE project_number = ?
                    ''', (
                        updated_data['project_number'],
                        updated_data['project_name'],
                        updated_data['object_address'],
                        project_number
                    ))
                    self.conn.commit()
                    self.update_projects_cards()
                    self.update_projects_combo()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Ошибка", "Проект с таким номером уже существует")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при редактировании проекта: {str(e)}")

    def delete_project(self):
        # Проверяем, выбран ли проект
        if not self.selected_project_data:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для удаления")
            return

        project_number = self.selected_project_data['project_number']

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить этот проект?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.cursor.execute("DELETE FROM projects WHERE project_number = ?", (project_number,))
            self.conn.commit()
            self.update_projects_cards()
            self.update_projects_combo()
            self.selected_project_data = None  # Сбрасываем выбранный проект

    def clear_form(self):
        self.main_form.clear_form()
        self.current_files = []
        self.update_files_list()
        self.current_edit_id = None
        self.update_buttons_state()

    def upload_contract(self):
        # Режим редактирования
        if self.current_edit_id:
            try:
                form_data = self.main_form.get_form_data()

                # Проверяем обязательные поля
                if not form_data['counterparty_name'].strip():
                    QMessageBox.warning(self, "Ошибка", "Введите наименование контрагента")
                    return

                if not form_data['contract_number'].strip():
                    QMessageBox.warning(self, "Ошибка", "Введите номер договора")
                    return

                # Начинаем транзакцию
                self.conn.execute("BEGIN TRANSACTION")

                try:
                    # Обновляем информацию в БД и переименовываем файл
                    self.update_contract_in_db(self.current_edit_id, form_data)

                    # Сохраняем этапы договора
                    self.save_contract_stages(self.current_edit_id, form_data['stages'])

                    # Фиксируем транзакцию
                    self.conn.commit()

                    QMessageBox.information(self, "Успех", "Договор успешно обновлен!")
                    self.clear_form()
                    self.update_contracts_list()
                    self.update_income_tree()
                    self.update_expense_tree()
                    self.update_buttons_state()
                    return  # Добавьте этот return

                except Exception as e:
                    # Откатываем транзакцию в случае ошибки
                    self.conn.rollback()
                    raise e

            except Exception as e:
                # Показываем подробное сообщение об ошибке
                error_details = traceback.format_exc()
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось сохранить договор: {str(e)}\n\nДетали ошибки:\n{error_details}"
                )
                # Откатываем транзакцию если была начата
                try:
                    self.conn.rollback()
                except:
                    pass
                return  # Добавьте return здесь тоже

        # Режим загрузки нового договора
        if not self.current_files:  # Этот блок теперь только для нового договора
            QMessageBox.warning(self, "Ошибка", "Сначала выберите файл для загрузки")
            return

        form_data = self.main_form.get_form_data()

        if not form_data['counterparty_name'].strip():
            QMessageBox.warning(self, "Ошибка", "Введите наименование контрагента")
            return

        if not form_data['contract_number'].strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер договора")
            return

        # Начинаем транзакцию
        self.conn.execute("BEGIN TRANSACTION")

        try:
            # Обрабатываем каждый файл
            for file_path in self.current_files:
                # Определяем, редактируемый ли файл
                is_editable = self.is_editable(file_path)

                # Получаем путь для сохранения
                save_dir = self.get_save_path(form_data['counterparty_type'], is_editable)

                # Создаем директорию, если не существует
                os.makedirs(save_dir, exist_ok=True)

                # Генерируем имя файла
                file_name = self.generate_file_name(
                    form_data['doc_type'],
                    form_data['doc_subtype'],
                    form_data['counterparty_name'],
                    form_data['counterparty_opf'],
                    form_data['contract_number'],
                    form_data['contract_date'],
                    form_data['project_info'],
                    form_data['supplementary_number'],
                    form_data['supplementary_date'],
                    form_data['supplementary_content'],
                    form_data['additional_number'],
                    form_data['additional_date'],
                    form_data['additional_content'],
                    form_data['brief_description']  # Добавлено
                )

                ext = os.path.splitext(file_path)[1]
                new_file_path = os.path.join(save_dir, file_name + ext)

                # Если файл с таким именем уже существует, добавляем суффикс
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(save_dir, f"{file_name}_{counter}{ext}")
                    counter += 1

                # Копируем файл
                shutil.copy2(file_path, new_file_path)

                # Сохраняем информацию в БД
                contract_id = self.save_to_database(
                    form_data['doc_type'],
                    form_data['doc_subtype'],
                    form_data['counterparty_name'],
                    form_data['counterparty_opf'],
                    form_data['counterparty_type'],
                    form_data['contract_number'],
                    form_data['contract_date'],
                    form_data['project_info'],
                    form_data['supplementary_number'],
                    form_data['supplementary_date'],
                    form_data['supplementary_content'],
                    form_data['additional_number'],
                    form_data['additional_date'],
                    form_data['additional_content'],
                    form_data['has_advance'],
                    new_file_path,
                    os.path.basename(file_path),
                    is_editable,
                    form_data['amount'],
                    form_data['currency'],
                    form_data['tax'],
                    form_data['advance_value'],
                    form_data['advance_type'],
                    form_data['brief_description']  # Добавлено
                )

                # Сохраняем этапы договора
                if contract_id and form_data['stages']:
                    for stage in form_data['stages']:
                        self.cursor.execute('''
                            INSERT INTO contract_stages (contract_id, description, type, value)
                            VALUES (?, ?, ?, ?)
                        ''', (contract_id, stage['description'], stage['type'], stage['value']))

                # Автоматически создаем связи на основе введенных данных
                self.auto_create_document_links(contract_id, form_data)

            # Фиксируем транзакцию
            self.conn.commit()

            self.current_files = []
            self.update_files_list()
            self.view_file_button.setEnabled(False)
            self.upload_button.setEnabled(False)
            self.update_contracts_list()
            self.update_income_tree()
            self.update_expense_tree()
            QMessageBox.information(self, "Успех", "Договор успешно загружен!")

        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            self.conn.rollback()
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось загрузить файлы: {str(e)}. Все изменения отменены.")

    def auto_create_document_links(self, contract_id, form_data):
        """Автоматически создает связи между документами на основе введенных данных"""
        doc_type = form_data['doc_type']

        if doc_type == "Договор":
            # Договор не имеет родительских документов
            return

        elif doc_type == "Допсоглашение":
            # Ищем договор, к которому относится это допсоглашение
            self.cursor.execute("""
                SELECT id FROM contracts 
                WHERE contract_number = ? AND contract_date = ? AND contract_type = 'Договор'
            """, (form_data['contract_number'], form_data['contract_date']))

            parent_contract = self.cursor.fetchone()
            if parent_contract:
                parent_id = parent_contract[0]
                self.add_document_link(parent_id, contract_id, "Допсоглашение")

        elif doc_type == "Соглашение о расторжении":
            # Ищем договор, к которому относится это СОР
            self.cursor.execute("""
                SELECT id FROM contracts 
                WHERE contract_number = ? AND contract_date = ? AND contract_type = 'Договор'
            """, (form_data['contract_number'], form_data['contract_date']))

            parent_contract = self.cursor.fetchone()
            if parent_contract:
                parent_id = parent_contract[0]
                self.add_document_link(parent_id, contract_id, "Соглашение о расторжении")

        elif doc_type in ["Приложение", "Спецификация"]:
            # Определяем тип связи
            link_type = "Приложение" if doc_type == "Приложение" else "Спецификация"

            if form_data['doc_subtype'] == "К договору":
                # Ищем договор, к которому относится это приложение/спецификация
                self.cursor.execute("""
                    SELECT id FROM contracts 
                    WHERE contract_number = ? AND contract_date = ? AND contract_type = 'Договор'
                """, (form_data['contract_number'], form_data['contract_date']))

                parent_contract = self.cursor.fetchone()
                if parent_contract:
                    parent_id = parent_contract[0]
                    self.add_document_link(parent_id, contract_id, link_type)

            else:  # К допсоглашению
                # Ищем допсоглашение, к которому относится это приложение/спецификация
                self.cursor.execute("""
                    SELECT id FROM contracts 
                    WHERE contract_number = ? AND contract_date = ? 
                    AND additional_number = ? AND additional_date = ?
                    AND contract_type = 'Допсоглашение'
                """, (form_data['contract_number'], form_data['contract_date'],
                      form_data['supplementary_number'], form_data['supplementary_date']))

                parent_supplementary = self.cursor.fetchone()
                if parent_supplementary:
                    parent_id = parent_supplementary[0]
                    self.add_document_link(parent_id, contract_id, link_type)

                # Также связываем с договором
                self.cursor.execute("""
                    SELECT id FROM contracts 
                    WHERE contract_number = ? AND contract_date = ? AND contract_type = 'Договор'
                """, (form_data['contract_number'], form_data['contract_date']))

                parent_contract = self.cursor.fetchone()
                if parent_contract:
                    parent_id = parent_contract[0]
                    self.add_document_link(parent_id, contract_id, link_type)

    def add_document_link(self, source_doc_id, target_doc_id, link_type):
        """Добавляет связь между документами"""
        # Проверяем, не существует ли уже такая связь
        self.cursor.execute("""
            SELECT id FROM document_links 
            WHERE source_doc_id = ? AND target_doc_id = ? AND link_type = ?
        """, (source_doc_id, target_doc_id, link_type))

        if not self.cursor.fetchone():
            self.cursor.execute("""
                INSERT INTO document_links (source_doc_id, target_doc_id, link_type, created_date)
                VALUES (?, ?, ?, ?)
            """, (source_doc_id, target_doc_id, link_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()

    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы договора", "",
            "Все файлы (*);;Документы (*.doc *.docx *.pdf *.xls *.xlsx);;Изображения (*.jpg *.png)"
        )
        if file_paths:
            self.current_files.extend(file_paths)
            self.update_files_list()
            self.view_file_button.setEnabled(True)
            self.upload_button.setEnabled(True)

    def remove_file(self):
        current_row = self.files_list.currentRow()
        if current_row >= 0 and current_row < len(self.current_files):
            self.current_files.pop(current_row)
            self.update_files_list()
            if not self.current_files:
                self.view_file_button.setEnabled(False)
                self.upload_button.setEnabled(False)

    def view_file(self):
        if self.current_files:
            current_row = self.files_list.currentRow()
            if current_row >= 0 and current_row < len(self.current_files):
                try:
                    file_path = self.current_files[current_row]
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                    # Уменьшаем окно для удобства просмотра
                    self.showNormal()
                    self.resize(self.width() // 2, self.height())
                    self.move(self.x(), self.y())
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def add_batch_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы для пакетной загрузки", "",
            "Все файлы (*);;Документы (*.doc *.docx *.pdf *.xls *.xlsx);;Изображения (*.jpg *.png)"
        )
        if file_paths:
            self.batch_files = file_paths  # используем отдельный список
            self.batch_files_list.clear()
            for file_path in file_paths:
                self.batch_files_list.addItem(os.path.basename(file_path))
            self.process_batch_button.setEnabled(True)

    def clear_batch_files(self):
        self.batch_files = []  # очищаем отдельный список
        self.batch_files_list.clear()
        self.process_batch_button.setEnabled(False)

    def process_batch_files(self):
        if not self.batch_files:
            QMessageBox.warning(self, "Ошибка", "Нет файлов для обработки")
            return

        self.batch_mode = True
        self.batch_index = 0
        # Показываем область с формой
        self.batch_form_scroll.setVisible(True)
        self.process_next_batch_file()

    def process_next_batch_file(self):
        if self.batch_index >= len(self.batch_files):
            self.batch_mode = False
            self.batch_index = 0
            self.batch_files = []
            self.batch_files_list.clear()
            self.process_batch_button.setEnabled(False)
            self.batch_form_scroll.setVisible(False)
            QMessageBox.information(self, "Готово", "Все файлы обработаны!")
            return

        current_file = self.batch_files[self.batch_index]
        self.show_batch_form(current_file)

        # Очищаем форму для нового файла и обновляем автодополнение
        if hasattr(self, 'batch_form'):
            self.batch_form.clear_form()
            self.update_projects_combo_batch()
            self.setup_autocompletion_batch()

    def on_period_changed(self, period):
        if period == "Произвольный":
            self.custom_start_date.setVisible(True)
            self.custom_end_date.setVisible(True)
        else:
            self.custom_start_date.setVisible(False)
            self.custom_end_date.setVisible(False)

    def configure_email(self):
        dialog = EmailDialog(self)
        if dialog.exec():
            self.email_settings = dialog.get_settings()
            self.save_email_settings()

    def send_report(self):
        if not self.email_recipients:
            QMessageBox.warning(self, "Ошибка", "Нет email получателей")
            return

        if not self.email_settings:
            QMessageBox.warning(self, "Ошибка", "Сначала настройте параметры email")
            self.configure_email()
            return

        period = self.period_combo.currentText()

        # Определяем даты для отчета
        end_date = QDate.currentDate()
        if period == "День":
            start_date = end_date
        elif period == "Неделя":
            start_date = end_date.addDays(-7)
        elif period == "Месяц":
            start_date = end_date.addMonths(-1)
        elif period == "Квартал":
            start_date = end_date.addMonths(-3)
        elif period == "Год":
            start_date = end_date.addYears(-1)
        elif period == "Произвольный":
            start_date = self.custom_start_date.date()
            end_date = self.custom_end_date.date()
        else:
            start_date = end_date

        # Получаем значения фильтров
        advance_filter = self.advance_filter.currentText()
        filetype_filter = self.filetype_filter.currentText()
        contract_type_filter = self.contract_type_filter.currentText()
        order_reversed = self.order_checkbox.isChecked()

        # Формируем отчет
        html_report, text_report = self.generate_report(start_date, end_date, advance_filter, filetype_filter,
                                                        contract_type_filter, order_reversed)

        # Проверяем, есть ли данные для отчета
        if not html_report or "загруженные документы отсутствуют" in text_report:
            QMessageBox.information(self, "Информация", "Нет данных для отчета за выбранный период")
            return

        # Отправляем email
        try:
            self.send_email(self.email_recipients, f"Отчет по договорам за {period}", text_report, html_report)
            QMessageBox.information(self, "Успех", f"Отчет за {period} отправлен на {', '.join(self.email_recipients)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось отправить отчет: {str(e)}")

    def update_contracts_list(self):
        self.contracts_list.clear()
        self.cursor.execute("""
                        SELECT id, counterparty_name, contract_number, contract_date, file_path, has_advance 
                        FROM contracts 
                        ORDER BY upload_date DESC 
                        LIMIT 50
                    """)
        contracts = self.cursor.fetchall()

        for contract in contracts:
            item = QListWidgetItem(f"{contract[1]} - №{contract[2]} от {contract[3]}")
            if contract[5]:  # has_advance
                item.setBackground(QColor(255, 255, 200))  # светло-желтый для аванса
            item.setData(Qt.ItemDataRole.UserRole, contract[0])
            self.contracts_list.addItem(item)

    def view_contract_stages(self, contract_id):
        self.cursor.execute("""
                        SELECT description, type, value FROM contract_stages 
                        WHERE contract_id = ? ORDER BY id
                    """, (contract_id,))
        stages = self.cursor.fetchall()

        stages_text = "Этапы договора:\n\n"
        for stage in stages:
            stages_text += f"{stage[0]}: {stage[2]} {stage[1]}\n"

        QMessageBox.information(self, "Этапы договора", stages_text)

    def view_document_links(self):
        current_item = self.registry_tree.currentItem()
        if current_item:
            contract_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.cursor.execute("""
                        SELECT contract_type, counterparty_name, counterparty_opf, contract_number, contract_date 
                        FROM contracts WHERE id = ?
                    """, (contract_id,))
            contract_info = self.cursor.fetchone()

            if contract_info:
                info_text = f"{contract_info[1]} {contract_info[2]} - {contract_info[0]} №{contract_info[3]} от {contract_info[4]}"
                dialog = DocumentLinksDialog(self, contract_id, info_text)
                dialog.exec()

    def show_batch_form(self, file_path):
        # Создаем виджет формы
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        # Информация о файле - используем обычный виджет вместо QGroupBox
        file_info_widget = QWidget()
        file_info_layout = QVBoxLayout(file_info_widget)
        file_info_layout.setContentsMargins(0, 0, 0, 10)  # Добавляем отступ снизу

        # Заголовок раздела
        file_section_label = QLabel("Информация о файле")
        file_section_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-bottom: 5px;")
        file_info_layout.addWidget(file_section_label)

        # Название файла
        file_name_label = QLabel(f"<b>Файл:</b> {os.path.basename(file_path)}")
        file_name_label.setTextFormat(Qt.TextFormat.RichText)
        file_info_layout.addWidget(file_name_label)

        # Путь к файлу (с переносами)
        file_path_label = QLabel(f"<b>Путь:</b> {file_path}")
        file_path_label.setWordWrap(True)  # Разрешаем перенос текста
        file_path_label.setTextFormat(Qt.TextFormat.RichText)
        file_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)  # Разрешаем выделение текста
        file_info_layout.addWidget(file_path_label)

        # Кнопки для работы с файлом
        file_buttons_layout = QHBoxLayout()
        view_batch_file_button = ModernButton("Просмотреть файл")
        view_batch_file_button.clicked.connect(lambda: self.view_batch_file(file_path))
        file_buttons_layout.addWidget(view_batch_file_button)

        open_batch_folder_button = ModernButton("Открыть папку")
        open_batch_folder_button.clicked.connect(lambda: self.open_batch_folder(file_path))
        file_buttons_layout.addWidget(open_batch_folder_button)

        file_info_layout.addLayout(file_buttons_layout)
        form_layout.addWidget(file_info_widget)

        # Добавляем форму договора
        self.batch_form = ContractFormWidget(self)  # Создаем экземпляр формы для пакетной загрузки
        form_layout.addWidget(self.batch_form)
        # ОБНОВЛЯЕМ АВТОДОПОЛНЕНИЕ ДЛЯ ПАКЕТНОЙ ФОРМЫ
        self.setup_autocompletion_batch()  # <- Добавьте эту строку
        self.update_projects_combo_batch()
        # Настраиваем автодополнение для пакетной формы
        self.setup_autocompletion_batch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        skip_button = ModernButton("Пропустить файл")
        skip_button.clicked.connect(self.skip_batch_file)
        buttons_layout.addWidget(skip_button)

        save_button = ModernButton("Сохранить и продолжить")
        save_button.clicked.connect(lambda: self.save_batch_file(file_path))
        buttons_layout.addWidget(save_button)

        form_layout.addLayout(buttons_layout)
        form_layout.addStretch()

        # Устанавливаем виджет в область прокрутки
        self.batch_form_scroll.setWidget(form_widget)

    def update_projects_combo_batch(self):
        """Обновляет список проектов в комбобоксе пакетной загрузки"""
        if hasattr(self, 'batch_form') and self.batch_form:
            current_text = self.batch_form.project_info.currentText()
            self.batch_form.project_info.clear()

            self.cursor.execute("SELECT project_number, project_name FROM projects ORDER BY project_number")
            projects = self.cursor.fetchall()

            for project in projects:
                display_text = f"{project[0]}, {project[1]}"
                self.batch_form.project_info.addItem(display_text)

            if current_text:
                index = self.batch_form.project_info.findText(current_text)
                if index >= 0:
                    self.batch_form.project_info.setCurrentIndex(index)

    def setup_autocompletion_batch(self):
        """Настраивает автодополнение для формы пакетной загрузки"""
        if hasattr(self, 'batch_form') and self.batch_form:
            # Автодополнение для наименования контрагента
            self.cursor.execute("SELECT DISTINCT counterparty_name FROM contracts")
            counterparties = [row[0] for row in self.cursor.fetchall()]
            counterparty_completer = QCompleter(counterparties)
            counterparty_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.batch_form.counterparty_name.setCompleter(counterparty_completer)

            # Автодополнение для проекта/объекта
            self.cursor.execute("SELECT DISTINCT project_info FROM contracts WHERE project_info != ''")
            projects = [row[0] for row in self.cursor.fetchall()]
            project_completer = QCompleter(projects)
            project_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.batch_form.project_info.setCompleter(project_completer)

    def view_batch_file(self, file_path):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def open_batch_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
        if os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            QMessageBox.warning(self, "Ошибка", "Папка не существует")

    def skip_batch_file(self):
        self.batch_index += 1
        self.process_next_batch_file()

    def save_batch_file(self, file_path):
        try:
            form_data = self.batch_form.get_form_data()

            # Проверяем обязательные поля
            if not form_data['counterparty_name'].strip():
                QMessageBox.warning(self, "Ошибка", "Введите наименование контрагента")
                return

            if not form_data['contract_number'].strip():
                QMessageBox.warning(self, "Ошибка", "Введите номер договора")
                return

            # Определяем, редактируемый ли файл
            is_editable = self.is_editable(file_path)

            # Получаем путь для сохранения
            save_dir = self.get_save_path(form_data['counterparty_type'], is_editable)

            # Создаем директорию, если не существует
            os.makedirs(save_dir, exist_ok=True)

            # Генерируем имя файла
            file_name = self.generate_file_name(
                form_data['doc_type'],
                form_data['doc_subtype'],
                form_data['counterparty_name'],
                form_data['counterparty_opf'],
                form_data['contract_number'],
                form_data['contract_date'],
                form_data['project_info'],
                form_data['supplementary_number'],
                form_data['supplementary_date'],
                form_data['supplementary_content'],
                form_data['additional_number'],
                form_data['additional_date'],
                form_data['additional_content'],
                form_data['brief_description']  # Добавлено
            )

            ext = os.path.splitext(file_path)[1]
            new_file_path = os.path.join(save_dir, file_name + ext)

            # Если файл с таким именем уже существует, добавляем суффикс
            counter = 1
            while os.path.exists(new_file_path):
                new_file_path = os.path.join(save_dir, f"{file_name}_{counter}{ext}")
                counter += 1

            # Копируем файл
            shutil.copy2(file_path, new_file_path)

            # Сохраняем информацию в БД
            contract_id = self.save_to_database(
                form_data['doc_type'],
                form_data['doc_subtype'],
                form_data['counterparty_name'],
                form_data['counterparty_opf'],
                form_data['counterparty_type'],
                form_data['contract_number'],
                form_data['contract_date'],
                form_data['project_info'],
                form_data['supplementary_number'],
                form_data['supplementary_date'],
                form_data['supplementary_content'],
                form_data['additional_number'],
                form_data['additional_date'],
                form_data['additional_content'],
                form_data['has_advance'],
                new_file_path,
                os.path.basename(file_path),
                is_editable,
                form_data['amount'],
                form_data['currency'],
                form_data['tax'],
                form_data['advance_value'],
                form_data['advance_type'],
                form_data['brief_description']  # Добавлено
            )

            # Сохраняем этапы договора
            if contract_id and form_data['stages']:
                for stage in form_data['stages']:
                    self.cursor.execute('''
                        INSERT INTO contract_stages (contract_id, description, type, value)
                        VALUES (?, ?, ?, ?)
                    ''', (contract_id, stage['description'], stage['type'], stage['value']))
                self.conn.commit()

            # Автоматически создаем связи на основе введенных данных
            self.auto_create_document_links(contract_id, form_data)

            # Переходим к следующему файлу
            self.batch_index += 1
            self.process_next_batch_file()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def open_contract_file(self, item):
        # Получаем путь к файлу из базы данных
        contract_id = item.data(Qt.ItemDataRole.UserRole)
        self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
        result = self.cursor.fetchone()
        if result:
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(result[0]))
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def open_contract_folder(self):
        current_item = self.contracts_list.currentItem()
        if current_item:
            contract_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
            result = self.cursor.fetchone()
            if result:
                folder_path = os.path.dirname(result[0])
                if os.path.exists(folder_path):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
                else:
                    QMessageBox.warning(self, "Ошибка", "Папка не существует")

    def is_editable(self, file_path):
        # Определяем, является ли файл редактируемым
        editable_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in editable_extensions

    def get_save_path(self, counterparty_type, is_editable):
        year = datetime.now().year
        base_path = "N:\\"

        # Проверяем доступность сетевого диска
        if not os.path.exists(base_path):
            # Альтернативный путь, если сетевой диск недоступен
            base_path = os.path.expanduser("~/MartelaContracts/")
            # Создаем все подпапки, если их нет
            os.makedirs(base_path, exist_ok=True)

        if is_editable:
            if counterparty_type == "Клиент":
                final_path = f"{base_path}Finance\\MARTELA\\05-КЛИЕНТЫ\\{year}"
            else:  # Поставщик, Страховка, Сборка
                final_path = f"{base_path}Finance\\MARTELA\\06-ПОСТАВЩИКИ\\{year}"
        else:
            if counterparty_type == "Клиент":
                final_path = f"{base_path}Agreements\\01-CLIENTS\\{year}"
            elif counterparty_type == "Поставщик":
                final_path = f"{base_path}Agreements\\02-SUPPLIERS\\{year}"
            elif counterparty_type == "Страховка":
                final_path = f"{base_path}Agreements\\06-Insurance"
            elif counterparty_type == "Сборка":
                final_path = f"{base_path}Agreements\\04-Assembly"
            else:
                final_path = f"{base_path}Agreements\\Other"

        # Создаем конечную папку, если ее нет
        os.makedirs(final_path, exist_ok=True)
        return final_path

    def generate_file_name(self, doc_type, doc_subtype, counterparty, opf, contract_num,
                           contract_date, project, supp_number, supp_date, supp_content,
                           add_number, add_date, add_content, brief_description):  # Добавлен параметр brief_description
        # Преобразуем дату из формата "yyyy-MM-dd" в "dd.MM.yyyy"
        try:
            date_obj = datetime.strptime(contract_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
        except:
            formatted_date = contract_date

        # Словарь сокращений
        abbreviations = {
            "Договор": "Дог.",
            "Допсоглашение": "ДС",
            "Приложение": "Прил.",
            "Спецификация": "Спец.",
            "Соглашение о расторжении": "СОР"  # Добавлено сокращение
        }

        # Используем сокращение вместо полного названия
        doc_type_abbr = abbreviations.get(doc_type, doc_type)

        file_name = f"{counterparty} {opf}-{doc_type_abbr} №{contract_num} от {formatted_date}"

        if project:
            # Берем только номер и название проекта (первые два элемента через запятую)
            project_parts = project.split(',')
            if len(project_parts) >= 2:
                short_project = f"{project_parts[0].strip()}, {project_parts[1].strip()}"
            else:
                short_project = project

            # Добавляем краткое описание через запятую после проекта
            if brief_description:  # новое условие
                file_name += f" ({short_project}, {brief_description})"
            else:
                file_name += f" ({short_project})"

        if doc_type == "Допсоглашение":
            try:
                add_date_obj = datetime.strptime(add_date, "%Y-%m-%d")
                formatted_add_date = add_date_obj.strftime("%d.%m.%Y")
            except:
                formatted_add_date = add_date

            file_name += f" {abbreviations['Допсоглашение']} №{add_number} от {formatted_add_date}"

            if add_content:
                file_name += f" ({add_content})"

        if doc_type == "Соглашение о расторжении":
            # Формируем базовое имя как для договора
            base_name = f"{counterparty} {opf}-{abbreviations['Договор']} №{contract_num} от {formatted_date}"

            if project:
                project_parts = project.split(',')
                if len(project_parts) >= 2:
                    short_project = f"{project_parts[0].strip()}, {project_parts[1].strip()}"
                else:
                    short_project = project

                if brief_description:
                    base_name += f" ({short_project}, {brief_description})"
                else:
                    base_name += f" ({short_project})"

            # Добавляем часть СОР
            try:
                add_date_obj = datetime.strptime(add_date, "%Y-%m-%d")
                formatted_add_date = add_date_obj.strftime("%d.%m.%Y")
            except:
                formatted_add_date = add_date

            file_name = f"{base_name}-{abbreviations['Соглашение о расторжении']} №{add_number} от {formatted_add_date}"

            if add_content:
                file_name += f" ({add_content})"

        elif doc_type in ["Приложение", "Спецификация"]:
            try:
                add_date_obj = datetime.strptime(add_date, "%Y-%m-%d")
                formatted_add_date = add_date_obj.strftime("%d.%m.%Y")
            except:
                formatted_add_date = add_date

            if doc_subtype == "К договору":
                file_name += f" {abbreviations[doc_type]} №{add_number} от {formatted_add_date}"
                if add_content:
                    file_name += f" ({add_content})"
            else:
                try:
                    supp_date_obj = datetime.strptime(supp_date, "%Y-%m-%d")
                    formatted_supp_date = supp_date_obj.strftime("%d.%m.%Y")
                except:
                    formatted_supp_date = supp_date

                file_name += f" {abbreviations['Допсоглашение']} №{supp_number} от {formatted_supp_date}"
                if supp_content:
                    file_name += f" ({supp_content})"

                file_name += f" {abbreviations[doc_type]} №{add_number} от {formatted_add_date}"
                if add_content:
                    file_name += f" ({add_content})"

                file_name += f" {abbreviations['Соглашение о расторжении']} №{supp_number} от {formatted_supp_date}"
                if supp_content:
                    file_name += f" ({supp_content})"

                file_name += f" {abbreviations[doc_type]} №{add_number} от {formatted_add_date}"
                if add_content:
                    file_name += f" ({add_content})"

        return file_name

    def save_to_database(self, doc_type, doc_subtype, counterparty_name, counterparty_opf, counterparty_type,
                         contract_number, contract_date, project_info, supplementary_number,
                         supplementary_date, supplementary_content, additional_number,
                         additional_date, additional_content, has_advance, file_path,
                         original_file_name, is_editable, amount="", currency="", tax="",
                         advance_value="", advance_type="",
                         brief_description=""):  # Добавлен параметр brief_description

        # Получаем project_id
        project_id = self.get_project_id(project_info)

        # Преобразуем числовые значения
        try:
            amount_val = float(amount) if amount else None
        except ValueError:
            amount_val = None

        try:
            tax_val = float(tax) if tax else None
        except ValueError:
            tax_val = None

        try:
            advance_val = float(advance_value) if advance_value else None
        except ValueError:
            advance_val = None

        # Вычисляем has_advance на основе значения аванса
        has_advance_val = 1 if advance_val is not None and advance_val != 0 else 0

        try:
            self.cursor.execute('''
                INSERT INTO contracts (
                    contract_type, app_type, counterparty_name, counterparty_opf, counterparty_type,
                    contract_number, contract_date, project_info, supplementary_number,
                    supplementary_date, supplementary_content, additional_number,
                    additional_date, additional_content, has_advance,
                    file_path, original_file_name, editable, upload_date, amount, currency,
                    tax_percent, advance_value, advance_type, project_id, brief_description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_type,
                doc_subtype if doc_type in ["Приложение", "Спецификация"] else "",
                counterparty_name,
                counterparty_opf,
                counterparty_type,
                contract_number,
                contract_date,
                project_info,
                supplementary_number if doc_type in ["Приложение",
                                                     "Спецификация"] and doc_subtype == "К допсоглашению" else "",
                supplementary_date if doc_type in ["Приложение",
                                                   "Спецификация"] and doc_subtype == "К допсоглашению" else "",
                supplementary_content if doc_type in ["Приложение",
                                                      "Спецификация"] and doc_subtype == "К допсоглашению" else "",
                additional_number if doc_type != "Договор" else "",
                additional_date if doc_type != "Договор" else "",
                additional_content if doc_type != "Договор" else "",
                has_advance_val,  # Используем вычисленное значение
                file_path,
                original_file_name,
                1 if is_editable else 0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                amount_val,
                currency if currency else "RUB",
                tax_val,
                advance_val,
                advance_type if advance_type else "%",
                project_id,
                brief_description  # Новое значение
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка при сохранении: {str(e)}")

    def generate_report(self, start_date, end_date, advance_filter, filetype_filter, contract_type_filter,
                        order_reversed):
        # Формируем отчет на основе данных из БД
        start_str = start_date.toString("yyyy-MM-dd")
        end_str = end_date.toString("yyyy-MM-dd")

        # Формируем SQL-запрос с учетом фильтров
        query = """
            SELECT id, contract_type, app_type, counterparty_name, counterparty_opf, contract_number, 
                   contract_date, project_info, supplementary_number, supplementary_date,
                   supplementary_content, additional_number, additional_date, additional_content, 
                   has_advance, file_path, editable, upload_date, amount, currency, 
                   tax_percent, advance_value, advance_type, counterparty_type
            FROM contracts 
            WHERE date(upload_date) BETWEEN ? AND ?
        """

        params = [start_str, end_str]

        # Добавляем фильтры
        if advance_filter == "С авансом":
            query += " AND has_advance = 1"
        elif advance_filter == "Без аванса":
            query += " AND has_advance = 0"

        if filetype_filter == "Редактируемые":
            query += " AND editable = 1"
        elif filetype_filter == "Не редактируемые":
            query += " AND editable = 0"

        if contract_type_filter == "Доходные":
            query += " AND counterparty_type = 'Клиент'"
        elif contract_type_filter == "Расходные":
            query += " AND counterparty_type IN ('Поставщик', 'Страховка', 'Сборка')"

        query += " ORDER BY upload_date"

        self.cursor.execute(query, params)
        contracts = self.cursor.fetchall()

        if not contracts:
            text_report = f"За период с {start_date.toString('dd.MM.yyyy')} по {end_date.toString('dd.MM.yyyy')} загруженные документы отсутствуют"
            return "", text_report

        # Сортируем договоры по типу (доходные/расходные)
        if order_reversed:
            # Сначала расходные, потом доходные
            income_contracts = [c for c in contracts if c[23] == "Клиент"]
            expense_contracts = [c for c in contracts if c[23] != "Клиент"]
            contracts = expense_contracts + income_contracts
        else:
            # Сначала доходные, потом расходные
            income_contracts = [c for c in contracts if c[23] == "Клиент"]
            expense_contracts = [c for c in contracts if c[23] != "Клиент"]
            contracts = income_contracts + expense_contracts

        # Текстовая версия отчета
        text_report = f"Отчет о загруженных договорах за период с {start_date.toString('dd.MM.yyyy')} по {end_date.toString('dd.MM.yyyy')}\n\n"
        text_report += f"Всего документов: {len(contracts)}\n\n"
        text_report += f"Фильтр по авансу: {advance_filter}\n"
        text_report += f"Фильтр по типу файла: {filetype_filter}\n"
        text_report += f"Фильтр по типу договора: {contract_type_filter}\n"
        text_report += f"Порядок: {'Сначала расходные' if order_reversed else 'Сначала доходные'}\n\n"

        for i, contract in enumerate(contracts, 1):
            # Получаем полную информацию о документе
            doc_info = self.get_document_info(contract)

            # Определяем тип контрагента
            counterparty_type_display = "Доходный (Клиент)" if contract[
                                                                   23] == "Клиент" else f"Расходный ({contract[23]})"

            text_report += f"{i}. {counterparty_type_display}\n"
            text_report += f"   Контрагент: {contract[3]} {contract[4]}\n"
            text_report += f"   {doc_info}\n"

            if contract[7]:
                text_report += f"   Проект: {contract[7]}\n"

            if contract[18]:
                text_report += f"   Сумма: {contract[18]} {contract[19]}\n"

            if contract[20]:
                text_report += f"   Налог: {contract[20]}%\n"

            if contract[21]:
                text_report += f"   Аванс: {contract[21]} {contract[22]}\n"

            # Получаем информацию о связях документа
            document_relations = self.get_document_relations_info(contract[0])
            if document_relations:
                text_report += f"   Взаимосвязь с документом:\n{document_relations}\n"

            text_report += f"   Тип файла: {'Черновик (редактируемый)' if contract[16] else 'Документ подписан (не редактируемый)'}\n"
            text_report += f"   Дата загрузки: {contract[17]}\n"
            text_report += f"   Путь к файлу: {contract[15]}\n\n"

        # HTML версия отчета
        html_report = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4a86e8; color: white; }}
                    tr.advance {{ background-color: #fff2cc; }}
                    tr.income {{ background-color: #d4edda; }}
                    tr.expense {{ background-color: #f8d7da; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .summary {{ margin-bottom: 20px; }}
                    .relations {{ white-space: pre-line; }}
                </style>
            </head>
            <body>
                <h1>Отчет о загруженных договорах</h1>
                <div class="summary">
                    <p>Период: с {start_date.toString('dd.MM.yyyy')} по {end_date.toString('dd.MM.yyyy')}</p>
                    <p>Всего документов: {len(contracts)}</p>
                    <p>Фильтр по авансу: {advance_filter}</p>
                    <p>Фильтр по типу файла: {filetype_filter}</p>
                    <p>Фильтр по типу договора: {contract_type_filter}</p>
                    <p>Порядок: {'Сначала расходные' if order_reversed else 'Сначала доходные'}</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>№</th>
                            <th>Тип контрагента</th>
                            <th>Контрагент</th>
                            <th>Тип документа</th>
                            <th>Информация о документе</th>
                            <th>Проект</th>
                            <th>Сумма</th>
                            <th>Налог</th>
                            <th>Аванс</th>
                            <th>Взаимосвязь с документом</th>
                            <th>Тип файла</th>
                            <th>Дата загрузки</th>
                            <th>Путь к файлу</th>
                        </tr>
                    </thead>
                    <tbody>
            """

        for i, contract in enumerate(contracts, 1):
            # Получаем полную информацию о документе
            doc_info = self.get_document_info(contract)

            # Определяем тип контрагента
            counterparty_type_display = "Доходный (Клиент)" if contract[
                                                                   23] == "Клиент" else f"Расходный ({contract[23]})"

            contract_class = "class='income'" if contract[23] == "Клиент" else "class='expense'"
            if contract[14]:  # has_advance
                contract_class += " advance"

            # Получаем информацию о связях документа
            document_relations = self.get_document_relations_info(contract[0])

            html_report += f"""
                        <tr {contract_class}>
                            <td>{i}</td>
                            <td>{counterparty_type_display}</td>
                            <td>{contract[3]} {contract[4]}</td>
                            <td>{contract[1]}</td>
                            <td>{doc_info}</td>
                            <td>{contract[7] or ''}</td>
                            <td>{contract[18] or ''} {contract[19] or ''}</td>
                            <td>{contract[20] or ''}%</td>
                            <td>{contract[21] or ''} {contract[22] or ''}</td>
                            <td class="relations">{document_relations or ''}</td>
                            <td>{'Черновик (редактируемый)' if contract[16] else 'Документ подписан (не редактируемый)'}</td>
                            <td>{contract[17]}</td>
                            <td>{contract[15]}</td>
                        </tr>
                """

        html_report += """
                    </tbody>
                </table>
            </body>
            </html>
            """

        return html_report, text_report

    def get_document_info(self, contract):
        """Формирует полную информацию о документе для отчета"""
        doc_type = contract[1]
        contract_number = contract[5] or ""
        contract_date = contract[6] or ""
        additional_number = contract[11] or ""
        additional_date = contract[12] or ""
        additional_content = contract[13] or ""
        supplementary_number = contract[8] or ""
        supplementary_date = contract[9] or ""
        supplementary_content = contract[10] or ""

        if doc_type == "Договор":
            return f"Номер: {contract_number}, Дата: {contract_date}"
        elif doc_type == "Допсоглашение":
            info = f"Номер договора: {contract_number}, Дата договора: {contract_date}"
            if additional_number:
                info += f", Номер допсоглашения: {additional_number}"
            if additional_date:
                info += f", Дата допсоглашения: {additional_date}"
            if additional_content:
                info += f", Содержание: {additional_content}"
            return info
        elif doc_type == "Соглашение о расторжении":
            info = f"Номер договора: {contract_number}, Дата договора: {contract_date}"
            if additional_number:
                info += f", Номер СОР: {additional_number}"
            if additional_date:
                info += f", Дата СОР: {additional_date}"
            if additional_content:
                info += f", Содержание: {additional_content}"
            return info
        elif doc_type in ["Приложение", "Спецификация"]:
            info = f"Номер договора: {contract_number}, Дата договора: {contract_date}"
            if additional_number:
                info += f", Номер {doc_type.lower()}: {additional_number}"
            if additional_date:
                info += f", Дата {doc_type.lower()}: {additional_date}"
            if additional_content:
                info += f", Содержание: {additional_content}"
            if supplementary_number and contract[2] == "К допсоглашению":
                info += f", Номер допсоглашения: {supplementary_number}"
            if supplementary_date and contract[2] == "К допсоглашению":
                info += f", Дата допсоглашения: {supplementary_date}"
            if supplementary_content and contract[2] == "К допсоглашению":
                info += f", Содержание допсоглашения: {supplementary_content}"
            return info
        return ""

    def get_document_relations_info(self, contract_id):
        """
        Получает информацию о связях документа для отчета
        """
        relations_info = ""

        # Получаем все связи документа
        links = self.get_document_links(contract_id)

        if not links:
            return relations_info

        for link in links:
            link_type = link['link_type']
            doc_info = f"{link['counterparty_name']} {link['counterparty_opf']} - {link['contract_type']} №{link['contract_number']} от {link['contract_date']}"

            relations_info += f"{link_type}: {doc_info}\n"

        return relations_info

    def send_email(self, to_emails, subject, text_body, html_body):
        # Создаем и запускаем worker в отдельном потоке
        self.email_worker = EmailWorker(
            self.email_settings,
            to_emails,
            subject,
            text_body,
            html_body
        )
        self.email_worker.finished.connect(self.handle_email_result)
        self.email_worker.start()

        # Показываем индикатор загрузки
        self.send_report_button.setEnabled(False)
        self.send_report_button.setText("Отправка...")

    def handle_email_result(self, success, message):
        self.send_report_button.setEnabled(True)
        self.send_report_button.setText("Отправить отчет")

        if not success:
            QMessageBox.warning(self, "Ошибка", message)

    def export_registry(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт реестра", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Это упрощенная реализация - в реальном приложении лучше использовать библиотеку pandas
                if file_path.endswith('.csv'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # Заголовки
                        headers = ["Контрагент", "Номер", "Дата", "Сумма", "Налог", "Аванс", "Путь"]
                        f.write(','.join(headers) + '\n')

                        # Данные - обходим все элементы дерева
                        def export_tree_items(item, level=0):
                            row_data = [
                                '"' + item.text(0) + '"',
                                '"' + item.text(1) + '"',
                                '"' + item.text(2) + '"',
                                '"' + item.text(3) + '"',
                                '"' + item.text(4) + '"',
                                '"' + item.text(5) + '"',
                                '"' + item.text(6) + '"'
                            ]
                            f.write(','.join(row_data) + '\n')

                            for i in range(item.childCount()):
                                export_tree_items(item.child(i), level + 1)

                        for i in range(self.registry_tree.topLevelItemCount()):
                            export_tree_items(self.registry_tree.topLevelItem(i))

                QMessageBox.information(self, "Успех", "Реестр успешно экспортирован")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось экспортировать реестра: {str(e)}")

    # Методы для работы со связями документов
    def get_document_links(self, contract_id):
        self.cursor.execute("""
                    SELECT dl.id, dl.link_type, 
                           c.id as doc_id, c.contract_type, c.counterparty_name, c.counterparty_opf, 
                           c.contract_number, c.contract_date
                    FROM document_links dl
                    JOIN contracts c ON (dl.source_doc_id = c.id OR dl.target_doc_id = c.id)
                    WHERE (dl.source_doc_id = ? OR dl.target_doc_id = ?) AND c.id != ?
                """, (contract_id, contract_id, contract_id))

        links = []
        for row in self.cursor.fetchall():
            links.append({
                'id': row[0],
                'link_type': row[1],
                'doc_id': row[2],
                'contract_type': row[3],
                'counterparty_name': row[4],
                'counterparty_opf': row[5],
                'contract_number': row[6],
                'contract_date': row[7]
            })
        return links

    def get_all_documents(self, filter_text=""):
        query = """
                    SELECT id, contract_type, counterparty_name, counterparty_opf, 
                           contract_number, contract_date 
                    FROM contracts 
                    WHERE counterparty_name LIKE ? OR contract_number LIKE ?
                    ORDER BY upload_date DESC
                """
        search_pattern = f"%{filter_text}%"
        self.cursor.execute(query, (search_pattern, search_pattern))

        documents = []
        for row in self.cursor.fetchall():
            documents.append({
                'id': row[0],
                'contract_type': row[1],
                'counterparty_name': row[2] if row[2] else "",
                'counterparty_opf': row[3] if row[3] else "",
                'contract_number': row[4] if row[4] else "",
                'contract_date': row[5] if row[5] else ""
            })
        return documents

    def delete_document_link(self, link_id):
        self.cursor.execute("DELETE FROM document_links WHERE id = ?", (link_id,))
        self.conn.commit()

    # Новые методы для редактирования и удаления документов
    def edit_contract(self):
        current_item = self.contracts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите договор для редактирования")
            return

        contract_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Проверяем, есть ли у документа связи
        self.cursor.execute("SELECT COUNT(*) FROM document_links WHERE source_doc_id = ? OR target_doc_id = ?",
                            (contract_id, contract_id))
        link_count = self.cursor.fetchone()[0]

        if link_count > 0:
            reply = QMessageBox.question(self, "Предупреждение",
                                         "Этот документ имеет связи с другими документами. "
                                         "При изменении данных связи могут быть обновлены. "
                                         "Продолжить?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        # Получаем данные договора из БД
        self.cursor.execute("""
            SELECT * FROM contracts WHERE id = ?
        """, (contract_id,))
        contract_data = self.cursor.fetchone()

        if not contract_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти данные договора")
            return

        # Преобразуем данные в словарь
        columns = [description[0] for description in self.cursor.description]
        contract_dict = dict(zip(columns, contract_data))

        # Заполняем форму данными
        self.main_form.fill_form(contract_dict)

        # Устанавливаем режим редактирования
        self.current_edit_id = contract_id
        # Добавьте эту строку
        self.update_buttons_state()

        # Показываем сообщение
        QMessageBox.information(self, "Редактирование",
                                "Данные договора загружены в форму. Внесите изменения и нажмите 'Сохранить изменения'")

    def delete_contract(self):
        current_item = self.contracts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите договор для удаления")
            return

        contract_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Подтверждение удаления
        reply = QMessageBox.question(self, "Подтверждение удаления",
                                     "Вы уверены, что хотите удалить этот договор? Это действие нельзя отменить.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        try:
            # Удаляем этапы договора
            self.cursor.execute("DELETE FROM contract_stages WHERE contract_id = ?", (contract_id,))

            # Удаляем связи документа
            self.cursor.execute("DELETE FROM document_links WHERE source_doc_id = ? OR target_doc_id = ?",
                                (contract_id, contract_id))

            # Получаем путь к файлу для удаления
            self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
            file_path = self.cursor.fetchone()[0]

            # Удаляем запись из БД
            self.cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
            self.conn.commit()

            # Удаляем файл
            if os.path.exists(file_path):
                os.remove(file_path)

            # Обновляем списки
            self.update_contracts_list()
            self.update_income_tree()
            self.update_expense_tree()

            QMessageBox.information(self, "Успех", "Договор успешно удален")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить договор: {str(e)}")

    def get_contract_stages(self, contract_id):
        """Получает этапы договора из БД"""
        self.cursor.execute("""
            SELECT description, type, value FROM contract_stages WHERE contract_id = ? ORDER BY id
        """, (contract_id,))

        stages = []
        for row in self.cursor.fetchall():
            stages.append({
                'description': row[0],
                'type': row[1],
                'value': row[2]
            })

        return stages

    def update_contract_in_db(self, contract_id, form_data):
        """Обновляет данные договора в БД и возвращает новый путь к файлу"""
        # Сначала переименовываем файл
        new_file_path = self.rename_contract_file(contract_id, form_data)

        # Получаем project_id
        project_id = self.get_project_id(form_data['project_info'])

        # Преобразуем числовые значения
        try:
            amount_val = float(form_data['amount']) if form_data['amount'] else None
        except ValueError:
            amount_val = None

        try:
            tax_val = float(form_data['tax']) if form_data['tax'] else None
        except ValueError:
            tax_val = None

        try:
            advance_val = float(form_data['advance_value']) if form_data['advance_value'] else None
        except ValueError:
            advance_val = None

        # Обновляем информацию в БД
        self.cursor.execute('''
            UPDATE contracts SET
                contract_type = ?,
                app_type = ?,
                counterparty_name = ?,
                counterparty_opf = ?,
                counterparty_type = ?,
                contract_number = ?,
                contract_date = ?,
                project_info = ?,
                supplementary_number = ?,
                supplementary_date = ?,
                supplementary_content = ?,
                additional_number = ?,
                additional_date = ?,
                additional_content = ?,
                has_advance = ?,
                amount = ?,
                currency = ?,
                tax_percent = ?,
                advance_value = ?,
                advance_type = ?,
                file_path = ?,
                project_id = ?
            WHERE id = ?
        ''', (
            form_data['doc_type'],
            form_data['doc_subtype'],
            form_data['counterparty_name'],
            form_data['counterparty_opf'],
            form_data['counterparty_type'],
            form_data['contract_number'],
            form_data['contract_date'],
            form_data['project_info'],
            form_data['supplementary_number'],
            form_data['supplementary_date'],
            form_data['supplementary_content'],
            form_data['additional_number'],
            form_data['additional_date'],
            form_data['additional_content'],
            1 if form_data.get('advance_value') and str(form_data['advance_value']).strip() not in ['', '0'] else 0,
            amount_val,
            form_data['currency'],
            tax_val,
            advance_val,
            form_data['advance_type'],
            new_file_path,
            project_id,
            contract_id
        ))
        self.conn.commit()

        # Заново создаем автоматические связи на основе обновленных данных
        self.auto_create_document_links(contract_id, form_data)

        return new_file_path

    def rename_contract_file(self, contract_id, form_data):
        """Переименовывает файл договора при изменении данных"""
        # Получаем текущий путь к файлу
        self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
        result = self.cursor.fetchone()
        if not result:
            return None

        old_file_path = result[0]

        if not old_file_path or not os.path.exists(old_file_path):
            return old_file_path  # Файл не существует, возвращаем старый путь

        # Определяем, редактируемый ли файл
        is_editable = self.is_editable(old_file_path)

        # Получаем новый путь для сохранения
        new_save_dir = self.get_save_path(form_data['counterparty_type'], is_editable)

        # Создаем директорию, если не существует
        os.makedirs(new_save_dir, exist_ok=True)

        # Генерируем новое имя файла
        new_file_name = self.generate_file_name(
            form_data['doc_type'],
            form_data['doc_subtype'],
            form_data['counterparty_name'],
            form_data['counterparty_opf'],
            form_data['contract_number'],
            form_data['contract_date'],
            form_data['project_info'],
            form_data['supplementary_number'],
            form_data['supplementary_date'],
            form_data['supplementary_content'],
            form_data['additional_number'],
            form_data['additional_date'],
            form_data['additional_content'],
            form_data['brief_description']  # Добавлено
        )

        # Получаем расширение файла
        ext = os.path.splitext(old_file_path)[1]
        new_file_path = os.path.join(new_save_dir, new_file_name + ext)

        # Если файл с таким именем уже существует, добавляем суффикс
        counter = 1
        while os.path.exists(new_file_path) and new_file_path != old_file_path:
            new_file_path = os.path.join(new_save_dir, f"{new_file_name}_{counter}{ext}")
            counter += 1

        # Переименовываем файл, если путь изменился
        if new_file_path != old_file_path:
            try:
                # Создаем целевую директорию, если она не существует
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

                # Перемещаем файл
                shutil.move(old_file_path, new_file_path)
                return new_file_path
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось переименовать файл: {str(e)}")
                return old_file_path

        return old_file_path

    def save_contract_stages(self, contract_id, stages):
        """Сохраняет этапы договора в БД"""
        # Удаляем старые этапы
        self.cursor.execute("DELETE FROM contract_stages WHERE contract_id = ?", (contract_id,))

        # Добавляем новые этапы
        for stage in stages:
            self.cursor.execute('''
                INSERT INTO contract_stages (contract_id, description, type, value)
                VALUES (?, ?, ?, ?)
            ''', (contract_id, stage['description'], stage['type'], stage['value']))

        self.conn.commit()

    def get_max_internal_number(self):
        """Находит максимальный внутренний номер договора в базе данных"""
        try:
            self.cursor.execute("SELECT contract_number FROM contracts")
            all_numbers = [row[0] for row in self.cursor.fetchall()]

            # Фильтруем только внутренние номера (формат: 000-0000-XXX)
            internal_numbers = []
            pattern = r'^\d{3}-\d{4}-[А-ЯA-Z]+$'

            for number in all_numbers:
                if number and re.match(pattern, number):
                    internal_numbers.append(number)

            if internal_numbers:
                # Сортируем по порядковому номеру (первая часть)
                internal_numbers.sort(key=lambda x: int(x.split('-')[0]))
                return internal_numbers[-1]

            return None
        except Exception as e:
            print(f"Ошибка при поиске внутренних номеров: {e}")
            return None

    def archive_contract(self, contract_id):
        dialog = ArchiveDialog(self)
        if dialog.exec():
            folder_name, box_number = dialog.get_data()
            if not folder_name or not box_number:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return False

            try:
                archive_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute('''
                    INSERT INTO archived_contracts (contract_id, folder_name, box_number, archive_date)
                    VALUES (?, ?, ?, ?)
                ''', (contract_id, folder_name, box_number, archive_date))
                self.conn.commit()

                QMessageBox.information(self, "Успех", "Документ отправлен в архив")
                return True
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось архивировать документ: {str(e)}")
                return False

    def update_archive_table(self):
        # Очищаем таблицу
        self.archive_table.setRowCount(0)

        # Получаем данные из БД
        query = """
            SELECT c.id, c.contract_number, c.contract_date, c.counterparty_name, 
                   a.folder_name, a.box_number, a.archive_date
            FROM contracts c
            JOIN archived_contracts a ON c.id = a.contract_id
            WHERE 1=1
        """

        params = []

        # Применяем фильтры
        if self.archive_search_text:
            query += " AND (c.contract_number LIKE ? OR c.contract_date LIKE ? OR c.counterparty_name LIKE ?)"
            params.extend([f"%{self.archive_search_text}%"] * 3)

        self.cursor.execute(query, params)
        archived_contracts = self.cursor.fetchall()

        # Заполняем таблицу
        for row, contract in enumerate(archived_contracts):
            self.archive_table.insertRow(row)
            for col, value in enumerate(contract):
                self.archive_table.setItem(row, col, QTableWidgetItem(str(value)))

        # Скрываем колонку с ID
        self.archive_table.setColumnHidden(0, True)

    def export_archive_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт архива", "", "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            # Создаем DataFrame с данными архива
            self.cursor.execute("""
                SELECT c.contract_number, c.contract_date, c.counterparty_name, 
                       a.folder_name, a.box_number, a.archive_date
                FROM contracts c
                JOIN archived_contracts a ON c.id = a.contract_id
                ORDER BY a.archive_date DESC
            """)

            data = self.cursor.fetchall()
            columns = ["Номер документа", "Дата документа", "Контрагент",
                       "Папка", "Короб", "Дата архивации"]

            df = pd.DataFrame(data, columns=columns)

            # Группируем по годам и номерам коробов
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Общий отчет
                df.to_excel(writer, sheet_name='Весь архив', index=False)

                # Отчет по годам
                years = df['Дата архивации'].str[:4].unique()
                for year in years:
                    year_data = df[df['Дата архивации'].str.startswith(year)]
                    year_data.to_excel(writer, sheet_name=f'Архив {year}', index=False)

                # Отчет по коробам
                boxes = df['Короб'].unique()
                for box in boxes:
                    box_data = df[df['Короб'] == box]
                    box_data.to_excel(writer, sheet_name=f'Короб {box}', index=False)

            QMessageBox.information(self, "Успех", "Архив успешно экспортирован в Excel")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось экспортировать архив: {str(e)}")

    def init_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QHBoxLayout(central_widget)

        # Создаем разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - форма ввода
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
                        QTabWidget::pane {
                            border: 1px solid #cccccc;
                            border-radius: 4px;
                            padding: 5px;
                        }
                        QTabBar::tab {
                            background: #f0f0f0;
                            border: 1px solid #cccccc;
                            padding: 8px 12px;
                            margin-right: 2px;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px;
                        }
                        QTabBar::tab:selected {
                            background: #ffffff;
                            border-bottom-color: #ffffff;
                        }
                    """)

        # Вкладка основного договора
        contract_tab = QWidget()
        contract_layout = QVBoxLayout(contract_tab)

        # Создаем основную форму
        self.main_form = ContractFormWidget(self)
        contract_layout.addWidget(self.main_form)

        # Файлы
        files_group = QGroupBox("Файлы документа")
        files_group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        margin-top: 15px;
                        padding-top: 10px;
                        background-color: #f8f8f8;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top center;
                        padding: 0 5px;
                        background-color: #f8f8f8;
                    }
                """)
        files_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        files_layout = QVBoxLayout(files_group)

        self.files_list = QListWidget()
        self.files_list.setFixedHeight(100)
        files_layout.addWidget(self.files_list)

        # Кнопки для файлов
        file_buttons_layout = QHBoxLayout()
        self.add_file_button = ModernButton("Добавить файл")
        self.add_file_button.clicked.connect(self.add_file)
        file_buttons_layout.addWidget(self.add_file_button)

        self.remove_file_button = ModernButton("Удалить файл")
        self.remove_file_button.clicked.connect(self.remove_file)
        file_buttons_layout.addWidget(self.remove_file_button)

        self.view_file_button = ModernButton("Просмотреть файл")
        self.view_file_button.clicked.connect(self.view_file)
        self.view_file_button.setEnabled(False)
        file_buttons_layout.addWidget(self.view_file_button)

        files_layout.addLayout(file_buttons_layout)
        contract_layout.addWidget(files_group)
        contract_layout.addSpacing(15)

        # Кнопки внизу формы
        buttons_layout = QHBoxLayout()
        self.clear_button = ModernButton("Очистить формы")
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_button)

        self.upload_button = ModernButton("Загрузить договор")
        self.upload_button.clicked.connect(self.upload_contract)
        self.upload_button.setEnabled(False)
        buttons_layout.addWidget(self.upload_button)

        contract_layout.addLayout(buttons_layout)

        # Добавляем вкладку
        tabs.addTab(contract_tab, "Договор")

        # Вкладка пакетной загрузки
        batch_tab = QWidget()
        batch_layout = QVBoxLayout(batch_tab)

        batch_info = QLabel(
            "Выберите несколько файлов для пакетной загрузки. Для каждого файла нужно будет заполнить информацию.")
        batch_info.setWordWrap(True)
        batch_layout.addWidget(batch_info)

        self.batch_files_list = QListWidget()
        self.batch_files_list.setMaximumHeight(150)
        batch_layout.addWidget(self.batch_files_list)

        batch_buttons_layout = QHBoxLayout()
        self.add_batch_files_button = ModernButton("Добавить файлы")
        self.add_batch_files_button.clicked.connect(self.add_batch_files)
        batch_buttons_layout.addWidget(self.add_batch_files_button)

        self.clear_batch_button = ModernButton("Очистить список")
        self.clear_batch_button.clicked.connect(self.clear_batch_files)
        batch_buttons_layout.addWidget(self.clear_batch_button)

        self.process_batch_button = ModernButton("Обработать файлы")
        self.process_batch_button.clicked.connect(self.process_batch_files)
        self.process_batch_button.setEnabled(False)
        batch_buttons_layout.addWidget(self.process_batch_button)

        batch_layout.addLayout(batch_buttons_layout)

        # Область для отображения формы пакетной загрузки
        self.batch_form_scroll = ModernScrollArea()
        self.batch_form_scroll.setVisible(False)
        batch_layout.addWidget(self.batch_form_scroll)

        tabs.addTab(batch_tab, "Пакетная загрузка")

        # Вкладка отчетов
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)

        reports_group = QGroupBox("Отправка отчетов")
        reports_group.setStyleSheet("QGroupBox { font-weight: bold; border-radius: 5px; }")
        reports_form_layout = QVBoxLayout(reports_group)

        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Период:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["День", "Неделя", "Месяц", "Квартал", "Год", "Произвольный"])
        period_layout.addWidget(self.period_combo)

        self.custom_start_date = QDateEdit()
        self.custom_start_date.setDate(QDate.currentDate().addDays(-7))
        self.custom_start_date.setCalendarPopup(True)
        self.custom_start_date.setVisible(False)
        period_layout.addWidget(self.custom_start_date)

        self.custom_end_date = QDateEdit()
        self.custom_end_date.setDate(QDate.currentDate())
        self.custom_end_date.setCalendarPopup(True)
        self.custom_end_date.setVisible(False)
        period_layout.addWidget(self.custom_end_date)

        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        reports_form_layout.addLayout(period_layout)

        # Добавляем фильтры для отчетов
        filters_layout = QGridLayout()

        # Фильтр по авансу
        filters_layout.addWidget(QLabel("Фильтр по авансу:"), 0, 0)
        self.advance_filter = QComboBox()
        self.advance_filter.addItems(["Все", "С авансом", "Без аванса"])
        filters_layout.addWidget(self.advance_filter, 0, 1)

        # Фильтр по типу файла
        filters_layout.addWidget(QLabel("Фильтр по типу файла:"), 1, 0)
        self.filetype_filter = QComboBox()
        self.filetype_filter.addItems(["Все", "Редактируемые", "Не редактируемые"])
        filters_layout.addWidget(self.filetype_filter, 1, 1)

        # Фильтр по типу договора
        filters_layout.addWidget(QLabel("Тип договора:"), 2, 0)
        self.contract_type_filter = QComboBox()
        self.contract_type_filter.addItems(["Все", "Доходные", "Расходные"])
        filters_layout.addWidget(self.contract_type_filter, 2, 1)

        # Чек-бокс для порядка
        self.order_checkbox = QCheckBox("Сначала расходные")
        filters_layout.addWidget(self.order_checkbox, 3, 0, 1, 2)

        reports_form_layout.addLayout(filters_layout)

        # Заменяем поле ввода email на список с кнопками управления
        emails_group = QGroupBox("Email получателей")
        emails_group_layout = QVBoxLayout(emails_group)

        self.email_list = QListWidget()
        self.email_list.setMaximumHeight(100)
        emails_group_layout.addWidget(self.email_list)

        email_buttons_layout = QHBoxLayout()
        self.add_email_button = ModernButton("Добавить email")
        self.add_email_button.clicked.connect(self.add_email_recipient)
        email_buttons_layout.addWidget(self.add_email_button)

        self.remove_email_button = ModernButton("Удалить email")
        self.remove_email_button.clicked.connect(self.remove_email_recipient)
        email_buttons_layout.addWidget(self.remove_email_button)

        emails_group_layout.addLayout(email_buttons_layout)
        reports_form_layout.addWidget(emails_group)

        email_settings_layout = QHBoxLayout()
        self.email_settings_button = ModernButton("Настройка email")
        self.email_settings_button.clicked.connect(self.configure_email)
        email_settings_layout.addWidget(self.email_settings_button)

        self.send_report_button = ModernButton("Отправить отчет")
        self.send_report_button.clicked.connect(self.send_report)
        email_settings_layout.addWidget(self.send_report_button)

        reports_form_layout.addLayout(email_settings_layout)

        reports_layout.addWidget(reports_group)

        tabs.addTab(reports_tab, "Отчеты")

        # Вкладка реестра с подвкладками
        registry_tab = QWidget()
        registry_layout = QVBoxLayout(registry_tab)

        # Создаем подвкладки для доходных и расходных
        registry_sub_tabs = QTabWidget()
        income_tab = QWidget()
        expense_tab = QWidget()

        # Настраиваем вкладку доходных
        income_layout = QVBoxLayout(income_tab)

        # Панель поиска и сортировки для доходных
        income_search_sort_widget = QWidget()
        income_search_sort_layout = QHBoxLayout(income_search_sort_widget)

        income_search_sort_layout.addWidget(QLabel("Поиск:"))
        self.income_search_edit = QLineEdit()
        self.income_search_edit.setPlaceholderText("Поиск по доходным...")
        self.income_search_edit.textChanged.connect(self.filter_income_tree)
        income_search_sort_layout.addWidget(self.income_search_edit)

        income_search_sort_layout.addWidget(QLabel("Сортировка:"))
        self.income_sort_combo = QComboBox()
        self.income_sort_combo.addItems(["Контрагент", "Номер", "Дата", "Сумма"])
        self.income_sort_combo.currentIndexChanged.connect(self.sort_income_tree)
        income_search_sort_layout.addWidget(self.income_sort_combo)

        self.income_sort_order_btn = ModernButton("По возрастанию")
        self.income_sort_order_btn.clicked.connect(self.toggle_income_sort_order)
        income_search_sort_layout.addWidget(self.income_sort_order_btn)

        income_search_sort_layout.addStretch()
        income_layout.addWidget(income_search_sort_widget)

        # Дерево доходных договоров
        self.income_tree = QTreeWidget()
        self.income_tree.setHeaderLabels(["Контрагент", "Номер", "Дата", "Сумма", "Налог", "Аванс", "Путь"])
        self.income_tree.setColumnWidth(0, 250)
        self.income_tree.setColumnWidth(6, 200)
        self.income_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.income_tree.customContextMenuRequested.connect(self.show_income_tree_context_menu)
        self.income_tree.itemDoubleClicked.connect(self.open_income_contract_file)
        income_layout.addWidget(self.income_tree)

        # Аналогично для расходных
        expense_layout = QVBoxLayout(expense_tab)

        # Панель поиска и сортировки для расходных
        expense_search_sort_widget = QWidget()
        expense_search_sort_layout = QHBoxLayout(expense_search_sort_widget)

        expense_search_sort_layout.addWidget(QLabel("Поиск:"))
        self.expense_search_edit = QLineEdit()
        self.expense_search_edit.setPlaceholderText("Поиск по расходным...")
        self.expense_search_edit.textChanged.connect(self.filter_expense_tree)
        expense_search_sort_layout.addWidget(self.expense_search_edit)

        expense_search_sort_layout.addWidget(QLabel("Сортировка:"))
        self.expense_sort_combo = QComboBox()
        self.expense_sort_combo.addItems(["Контрагент", "Номер", "Дата", "Сумма"])
        self.expense_sort_combo.currentIndexChanged.connect(self.sort_expense_tree)
        expense_search_sort_layout.addWidget(self.expense_sort_combo)

        self.expense_sort_order_btn = ModernButton("По возрастанию")
        self.expense_sort_order_btn.clicked.connect(self.toggle_expense_sort_order)
        expense_search_sort_layout.addWidget(self.expense_sort_order_btn)

        expense_search_sort_layout.addStretch()
        expense_layout.addWidget(expense_search_sort_widget)

        # Дерево расходных договоров
        self.expense_tree = QTreeWidget()
        self.expense_tree.setHeaderLabels(["Контрагент", "Номер", "Дата", "Сумма", "Налог", "Аванс", "Путь"])
        self.expense_tree.setColumnWidth(0, 250)
        self.expense_tree.setColumnWidth(6, 200)
        self.expense_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.expense_tree.customContextMenuRequested.connect(self.show_expense_tree_context_menu)
        self.expense_tree.itemDoubleClicked.connect(self.open_expense_contract_file)
        expense_layout.addWidget(self.expense_tree)

        registry_sub_tabs.addTab(income_tab, "Доходные")
        registry_sub_tabs.addTab(expense_tab, "Расходные")
        registry_layout.addWidget(registry_sub_tabs)

        self.update_income_tree()
        self.update_expense_tree()

        # Кнопки управления реестром
        registry_buttons_layout = QHBoxLayout()
        self.refresh_registry_button = ModernButton("Обновить реестр")
        self.refresh_registry_button.clicked.connect(self.update_registry_trees)
        registry_buttons_layout.addWidget(self.refresh_registry_button)

        self.export_registry_button = ModernButton("Экспорт в Excel")
        self.export_registry_button.clicked.connect(self.export_registry)
        registry_buttons_layout.addWidget(self.export_registry_button)

        self.view_links_button = ModernButton("Просмотреть связи")
        self.view_links_button.clicked.connect(self.view_document_links)
        registry_buttons_layout.addWidget(self.view_links_button)

        registry_layout.addLayout(registry_buttons_layout)

        tabs.addTab(registry_tab, "Реестр")

        # Добавим вкладку "Архив"
        archive_tab = QWidget()
        archive_layout = QVBoxLayout(archive_tab)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.archive_search_edit = QLineEdit()
        self.archive_search_edit.setPlaceholderText("Поиск по номеру, дате, контрагенту...")
        self.archive_search_edit.textChanged.connect(self.on_archive_search_changed)
        search_layout.addWidget(self.archive_search_edit)

        archive_layout.addLayout(search_layout)

        # Таблица архива
        self.archive_table = QTableWidget()
        self.archive_table.setColumnCount(7)
        self.archive_table.setHorizontalHeaderLabels([
            "ID", "Номер документа", "Дата документа", "Контрагент",
            "Папка", "Короб", "Дата архивации"
        ])
        self.archive_table.setColumnHidden(0, True)
        archive_layout.addWidget(self.archive_table)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.export_archive_button = ModernButton("Экспорт в Excel")
        self.export_archive_button.clicked.connect(self.export_archive_to_excel)
        buttons_layout.addWidget(self.export_archive_button)

        archive_layout.addLayout(buttons_layout)

        tabs.addTab(archive_tab, "Архив")

        # Инициализируем таблицу архива
        self.archive_search_text = ""
        self.update_archive_table()

        # Правая панель - список загруженных файлов
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        right_layout.addWidget(QLabel("Последние загруженные договоры:"))

        self.contracts_list = QListWidget()
        self.contracts_list.itemDoubleClicked.connect(self.open_contract_file)
        right_layout.addWidget(self.contracts_list)

        # Кнопки для правой панели
        right_buttons_layout = QHBoxLayout()
        self.refresh_button = ModernButton("Обновить список")
        self.refresh_button.clicked.connect(self.update_contracts_list)
        right_buttons_layout.addWidget(self.refresh_button)

        self.open_folder_button = ModernButton("Открыть папку")
        self.open_folder_button.clicked.connect(self.open_contract_folder)
        right_buttons_layout.addWidget(self.open_folder_button)

        # Добавляем кнопки редактирования и удаления
        self.edit_button = ModernButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_contract)
        right_buttons_layout.addWidget(self.edit_button)

        self.delete_button = ModernButton("Удалить")
        self.delete_button.clicked.connect(self.delete_contract)
        right_buttons_layout.addWidget(self.delete_button)

        self.generate_number_button = ModernButton("Сгенерировать номер")
        self.generate_number_button.clicked.connect(self.show_generate_number_dialog)
        right_buttons_layout.addWidget(self.generate_number_button)

        right_layout.addLayout(right_buttons_layout)

        # Добавляем панели в разделитель
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 600])

        main_layout.addWidget(splitter)

        # Обновляем список договоров и реестр
        self.update_contracts_list()
        self.update_income_tree()
        self.update_expense_tree()
        self.update_email_list()
        # Настраиваем автодополнение после создания всех виджетов
        self.setup_autocompletion()

        # Вкладка проектов
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)

        # Блок поиска и сортировки проектов
        search_sort_widget = QWidget()
        search_sort_layout = QVBoxLayout(search_sort_widget)

        # Создаем виджет для полей поиска
        search_widget = QWidget()
        search_layout = QGridLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # Поле для поиска по номеру проекта
        search_layout.addWidget(QLabel("Номер:"), 0, 0)
        self.projects_search_number_edit = QLineEdit()
        self.projects_search_number_edit.setPlaceholderText("Поиск по номеру...")
        self.projects_search_number_edit.textChanged.connect(self.filter_projects)
        search_layout.addWidget(self.projects_search_number_edit, 0, 1)

        # Поле для поиска по названию проекта
        search_layout.addWidget(QLabel("Название:"), 1, 0)
        self.projects_search_name_edit = QLineEdit()
        self.projects_search_name_edit.setPlaceholderText("Поиск по названию...")
        self.projects_search_name_edit.textChanged.connect(self.filter_projects)
        search_layout.addWidget(self.projects_search_name_edit, 1, 1)

        # Поле для поиска по адресу
        search_layout.addWidget(QLabel("Адрес:"), 2, 0)
        self.projects_search_address_edit = QLineEdit()
        self.projects_search_address_edit.setPlaceholderText("Поиск по адресу...")
        self.projects_search_address_edit.textChanged.connect(self.filter_projects)
        search_layout.addWidget(self.projects_search_address_edit, 2, 1)

        search_sort_layout.addWidget(search_widget)

        # Блок сортировки
        sort_widget = QWidget()
        sort_layout = QHBoxLayout(sort_widget)
        sort_layout.setContentsMargins(0, 0, 0, 0)

        sort_layout.addWidget(QLabel("Сортировка по:"))
        self.projects_sort_combo = QComboBox()
        self.projects_sort_combo.addItems(["Номер", "Название", "Адрес"])
        self.projects_sort_combo.currentIndexChanged.connect(self.sort_projects)
        sort_layout.addWidget(self.projects_sort_combo)

        self.projects_sort_order_btn = ModernButton("По возрастанию")
        self.projects_sort_order_btn.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.projects_sort_order_btn)

        search_sort_layout.addWidget(sort_widget)

        projects_layout.addWidget(search_sort_widget)

        # Создаем область прокрутки для карточек
        self.projects_scroll_area = ModernScrollArea()
        self.projects_scroll_area.setWidgetResizable(True)

        # Контейнер для карточек с сеточным layout
        self.projects_container = QWidget()
        self.projects_grid_layout = QGridLayout(self.projects_container)
        self.projects_scroll_area.setWidget(self.projects_container)

        projects_layout.addWidget(self.projects_scroll_area)

        # Кнопки управления проектами
        projects_buttons_layout = QHBoxLayout()
        self.add_project_button = ModernButton("Добавить проект")
        self.add_project_button.clicked.connect(self.add_project)
        projects_buttons_layout.addWidget(self.add_project_button)

        self.edit_project_button = ModernButton("Редактировать проект")
        self.edit_project_button.clicked.connect(self.edit_project)
        projects_buttons_layout.addWidget(self.edit_project_button)

        self.delete_project_button = ModernButton("Удалить проект")
        self.delete_project_button.clicked.connect(self.delete_project)
        projects_buttons_layout.addWidget(self.delete_project_button)

        # Добавляем кнопку импорта из Excel
        self.import_excel_button = ModernButton("Импорт из Excel")
        self.import_excel_button.clicked.connect(self.import_projects_from_excel)
        projects_buttons_layout.addWidget(self.import_excel_button)

        projects_layout.addLayout(projects_buttons_layout)

        tabs.addTab(projects_tab, "Проекты")

        # Обновляем список проектов
        self.update_projects_cards()
        # Обновляем комбобокс проектов
        self.update_projects_combo()

        self.update_buttons_state()

        left_layout.addWidget(tabs)

    def on_archive_search_changed(self, text):
        self.archive_search_text = text
        self.update_archive_table()

    def show_generate_number_dialog(self):
        dialog = GenerateNumberDialog(self)
        dialog.exec()

    def update_registry_trees(self):
        """Обновляет оба дерева реестра"""
        self.update_income_tree()
        self.update_expense_tree()

    def update_income_tree(self):
        """Обновляет дерево доходных договоров"""
        self.income_tree.clear()

        # Запрос для доходных договоров (клиенты)
        self.cursor.execute("""
            SELECT c.id, c.contract_type, c.counterparty_name, c.counterparty_opf, 
                   c.contract_number, c.contract_date, c.amount, c.currency, 
                   c.tax_percent, c.advance_value, c.advance_type, c.file_path
            FROM contracts c
            WHERE c.counterparty_type = 'Клиент'
            ORDER BY c.contract_date DESC
        """)
        contracts = self.cursor.fetchall()

        # Создаем элементы для доходных договоров
        for contract in contracts:
            contract_item = QTreeWidgetItem(self.income_tree)
            contract_item.setText(0, f"{contract[2]} {contract[3]}")
            contract_item.setText(1, contract[4])
            contract_item.setText(2, contract[5])
            contract_item.setText(3, f"{contract[6]} {contract[7]}" if contract[6] else "")
            contract_item.setText(4, f"{contract[8]}%" if contract[8] else "")
            contract_item.setText(5, f"{contract[9]} {contract[10]}" if contract[9] else "")
            contract_item.setText(6, contract[11])
            contract_item.setData(0, Qt.ItemDataRole.UserRole, contract[0])

            # Устанавливаем цвет фона для доходных
            for i in range(7):
                contract_item.setBackground(i, QColor(220, 255, 220))  # Светло-зеленый

            # Добавляем дочерние документы
            self.add_child_documents(contract[0], contract_item, "Клиент")

        # Применяем фильтрацию и сортировку
        self.apply_income_filters()

    def update_expense_tree(self):
        """Обновляет дерево расходных договоров"""
        self.expense_tree.clear()

        # Запрос для расходных договоров (поставщики, страховки, сборка)
        self.cursor.execute("""
            SELECT c.id, c.contract_type, c.counterparty_name, c.counterparty_opf, 
                   c.contract_number, c.contract_date, c.amount, c.currency, 
                   c.tax_percent, c.advance_value, c.advance_type, c.file_path
            FROM contracts c
            WHERE c.counterparty_type != 'Клиент'
            ORDER BY c.contract_date DESC
        """)
        contracts = self.cursor.fetchall()

        # Создаем элементы для расходных договоров
        for contract in contracts:
            contract_item = QTreeWidgetItem(self.expense_tree)
            contract_item.setText(0, f"{contract[2]} {contract[3]}")
            contract_item.setText(1, contract[4])
            contract_item.setText(2, contract[5])
            contract_item.setText(3, f"{contract[6]} {contract[7]}" if contract[6] else "")
            contract_item.setText(4, f"{contract[8]}%" if contract[8] else "")
            contract_item.setText(5, f"{contract[9]} {contract[10]}" if contract[9] else "")
            contract_item.setText(6, contract[11])
            contract_item.setData(0, Qt.ItemDataRole.UserRole, contract[0])

            # Устанавливаем цвет фона для расходных
            for i in range(7):
                contract_item.setBackground(i, QColor(255, 220, 220))  # Светло-красный

            # Добавляем дочерние документы
            self.add_child_documents(contract[0], contract_item, "Расход")

        # Применяем фильтрацию и сортировку
        self.apply_expense_filters()

    def add_child_documents(self, parent_id, parent_item, counterparty_type):
        """Добавляет дочерние документы к родительскому элементу"""
        self.cursor.execute("""
            SELECT dl.link_type, c.id, c.contract_type, c.counterparty_name, c.counterparty_opf, 
                   c.contract_number, c.contract_date, c.amount, c.currency, 
                   c.tax_percent, c.advance_value, c.advance_type, c.file_path
            FROM document_links dl
            JOIN contracts c ON dl.target_doc_id = c.id
            WHERE dl.source_doc_id = ?
            ORDER BY dl.link_type, c.contract_date
        """, (parent_id,))

        child_documents = self.cursor.fetchall()

        for doc in child_documents:
            child_item = QTreeWidgetItem(parent_item)
            child_item.setText(0, f"{doc[3]} {doc[4]} ({doc[0]})")
            child_item.setText(1, doc[5])
            child_item.setText(2, doc[6])
            child_item.setText(3, f"{doc[7]} {doc[8]}" if doc[7] else "")
            child_item.setText(4, f"{doc[9]}%" if doc[9] else "")
            child_item.setText(5, f"{doc[10]} {doc[11]}" if doc[10] else "")
            child_item.setText(6, doc[12])
            child_item.setData(0, Qt.ItemDataRole.UserRole, doc[1])

            # Устанавливаем цвет в зависимости от типа
            for i in range(7):
                if counterparty_type == "Клиент":
                    child_item.setBackground(i, QColor(230, 255, 230))  # Более светлый зеленый
                else:
                    child_item.setBackground(i, QColor(255, 230, 230))  # Более светлый красный

            # Рекурсивно добавляем дочерние документы
            self.add_child_documents(doc[1], child_item, counterparty_type)

    def filter_income_tree(self, text):
        self.income_filter_text = text.lower()
        self.update_income_tree()  # Обновляем данные с учетом фильтра

    def filter_expense_tree(self, text):
        self.expense_filter_text = text.lower()
        self.update_expense_tree()  # Обновляем данные с учетом фильтра

    def apply_income_filters(self):
        """Применяет фильтры и сортировку к дереву доходных"""
        self.apply_filters_to_tree(self.income_tree, self.income_filter_text,
                                   self.income_sort_column, self.income_sort_order)

    def apply_expense_filters(self):
        """Применяет фильтры и сортировку к дереву расходных"""
        self.apply_filters_to_tree(self.expense_tree, self.expense_filter_text,
                                   self.expense_sort_column, self.expense_sort_order)

    def apply_filters_to_tree(self, tree, filter_text, sort_column, sort_order):
        """Применяет фильтры и сортировку к указанному дереву"""
        # Скрываем/показываем элементы based on filter
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            self.filter_tree_item(item, filter_text)

        # Сортируем дерево
        tree.sortItems(sort_column, sort_order)

    def filter_tree_item(self, item, filter_text):
        """Рекурсивно фильтрует элементы дерева"""
        visible = False

        # Проверяем, соответствует ли элемент фильтру
        for i in range(item.columnCount()):
            if filter_text in item.text(i).lower():
                visible = True
                break

        # Проверяем дочерние элементы
        for i in range(item.childCount()):
            child_visible = self.filter_tree_item(item.child(i), filter_text)
            visible = visible or child_visible

        item.setHidden(not visible)
        return visible

    def sort_income_tree(self, index):
        """Сортирует дерево доходных по выбранному столбцу"""
        self.income_sort_column = index
        self.apply_income_filters()

    def sort_expense_tree(self, index):
        """Сортирует дерево расходных по выбранному столбцу"""
        self.expense_sort_column = index
        self.apply_expense_filters()

    def toggle_income_sort_order(self):
        """Переключает порядок сортировки для доходных"""
        if self.income_sort_order == Qt.SortOrder.AscendingOrder:
            self.income_sort_order = Qt.SortOrder.DescendingOrder
            self.income_sort_order_btn.setText("По убыванию")
        else:
            self.income_sort_order = Qt.SortOrder.AscendingOrder
            self.income_sort_order_btn.setText("По возрастанию")
        self.apply_income_filters()

    def toggle_expense_sort_order(self):
        """Переключает порядок сортировки для расходных"""
        if self.expense_sort_order == Qt.SortOrder.AscendingOrder:
            self.expense_sort_order = Qt.SortOrder.DescendingOrder
            self.expense_sort_order_btn.setText("По убыванию")
        else:
            self.expense_sort_order = Qt.SortOrder.AscendingOrder
            self.expense_sort_order_btn.setText("По возрастанию")
        self.apply_expense_filters()

    def show_income_tree_context_menu(self, position):
        """Показывает контекстное меню для дерева доходных"""
        self.show_tree_context_menu(self.income_tree, position)

    def show_expense_tree_context_menu(self, position):
        """Показывает контекстное меню для дерева расходных"""
        self.show_tree_context_menu(self.expense_tree, position)

    def show_tree_context_menu(self, tree, position):
        """Показывает контекстное меню для указанного дерева"""
        item = tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        open_file_action = QAction("Открыть файл", self)
        open_file_action.triggered.connect(lambda: self.open_tree_contract_file(tree))
        menu.addAction(open_file_action)

        open_folder_action = QAction("Открыть папку", self)
        open_folder_action.triggered.connect(lambda: self.open_tree_contract_folder(tree))
        menu.addAction(open_folder_action)

        menu.addSeparator()

        view_links_action = QAction("Просмотреть связи", self)
        view_links_action.triggered.connect(self.view_document_links)
        menu.addAction(view_links_action)

        # Добавляем пункт "Отправить в архив"
        archive_action = QAction("Отправить в архив", self)
        archive_action.triggered.connect(lambda: self.on_archive_action(tree))
        menu.addAction(archive_action)

        menu.exec(tree.viewport().mapToGlobal(position))

    def on_archive_action(self, tree):
        current_item = tree.currentItem()
        if current_item:
            contract_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if self.archive_contract(contract_id):
                # Обновляем деревья и архив
                self.update_income_tree()
                self.update_expense_tree()
                self.update_archive_table()

    def open_income_contract_file(self, item, column):
        """Открывает файл доходного договора"""
        self.open_tree_contract_file(self.income_tree)

    def open_expense_contract_file(self, item, column):
        """Открывает файл расходного договора"""
        self.open_tree_contract_file(self.expense_tree)

    def open_tree_contract_file(self, tree):
        """Открывает файл выбранного договора в указанном дереве"""
        current_item = tree.currentItem()
        if current_item:
            contract_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
            result = self.cursor.fetchone()
            if result:
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(result[0]))
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def open_tree_contract_folder(self, tree):
        """Открывает папку выбранного договора в указанном дереве"""
        current_item = tree.currentItem()
        if current_item:
            contract_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.cursor.execute("SELECT file_path FROM contracts WHERE id = ?", (contract_id,))
            result = self.cursor.fetchone()
            if result:
                folder_path = os.path.dirname(result[0])
                if os.path.exists(folder_path):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
                else:
                    QMessageBox.warning(self, "Ошибка", "Папка не существует")

    def update_files_list(self):
        self.files_list.clear()
        for file_path in self.current_files:
            self.files_list.addItem(os.path.basename(file_path))
        self.update_buttons_state()

    def show_document_links(self):
        current_item = self.contracts_list.currentItem()
        if current_item:
            contract_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.cursor.execute("""
                                SELECT contract_type, counterparty_name, counterparty_opf, contract_number, contract_date 
                                FROM contracts WHERE id = ?
                            """, (contract_id,))
            contract_info = self.cursor.fetchone()

            if contract_info:
                info_text = f"{contract_info[1]} {contract_info[2]} - {contract_info[0]} №{contract_info[3]} от {contract_info[4]}"
                dialog = DocumentLinksDialog(self, contract_id, info_text)
                dialog.exec()
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите документ из списка")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Устанавливаем современный стиль
    app.setStyle('Fusion')

    # Настройка палитры для темной темы
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 130, 180))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)

    window = ContractManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()