import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
import hashlib
import requests
from urllib.parse import urlparse
import re
import webbrowser
from datetime import datetime


class SOAPAPITester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Суп")
        self.setGeometry(100, 100, 1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.create_ui()
        self.set_default_request()
        self.setup_hotkeys()

    def create_ui(self):
        # WSDL URL
        wsdl_group = QGroupBox("URL WSDL")
        wsdl_layout = QVBoxLayout()
        self.wsdl_edit = QLineEdit("https://api.intickets.ru/soap/?wsdl&ver=2.2")
        wsdl_layout.addWidget(self.wsdl_edit)
        wsdl_group.setLayout(wsdl_layout)
        self.main_layout.addWidget(wsdl_group)

        # Accounts buttons
        accounts_layout = QHBoxLayout()
        self.accounts_btn = QPushButton("Аккаунты шлюзов")
        self.accounts_btn.clicked.connect(self.open_accounts_link)
        accounts_layout.addWidget(self.accounts_btn)
        self.test_request_btn = QPushButton("Тестовый запрос к kassy.ru_sochi_gate")
        self.test_request_btn.clicked.connect(self.set_test_credentials)
        accounts_layout.addWidget(self.test_request_btn)
        self.main_layout.addLayout(accounts_layout)

        # Authentication
        auth_group = QGroupBox("Авторизация")
        auth_layout = QVBoxLayout()
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Логин:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        auth_layout.addLayout(username_layout)
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Стандартный пароль, не MD5")
        password_layout.addWidget(self.password_edit)
        auth_layout.addLayout(password_layout)
        auth_group.setLayout(auth_layout)
        self.main_layout.addWidget(auth_group)

        # Show ID
        show_group = QGroupBox("ID Сеанса")
        show_layout = QHBoxLayout()
        show_layout.addWidget(QLabel("ID Сеанса:"))
        self.show_id_edit = QLineEdit()
        self.show_id_edit.setPlaceholderText("Не обязательно для заполнения, будет получен список всех сеансов")
        show_layout.addWidget(self.show_id_edit)
        show_group.setLayout(show_layout)
        self.main_layout.addWidget(show_group)

        # Request and Response
        req_res_layout = QHBoxLayout()
        req_group = QGroupBox("Запрос")
        req_layout = QVBoxLayout()
        self.request_edit = QTextEdit()
        req_layout.addWidget(self.request_edit)
        req_group.setLayout(req_layout)
        req_res_layout.addWidget(req_group)
        res_group = QGroupBox("Ответ")
        res_layout = QVBoxLayout()
        self.response_edit = QTextEdit()
        res_layout.addWidget(self.response_edit)
        res_group.setLayout(res_layout)
        req_res_layout.addWidget(res_group)
        self.main_layout.addLayout(req_res_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.send_btn = QPushButton("Отправить запрос")
        self.send_btn.clicked.connect(self.send_request)
        buttons_layout.addWidget(self.send_btn)
        self.save_btn = QPushButton("Сохранить запрос/ответ")
        self.save_btn.clicked.connect(self.save_to_file)
        buttons_layout.addWidget(self.save_btn)
        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_request)
        buttons_layout.addWidget(self.reset_btn)
        self.main_layout.addLayout(buttons_layout)

        # Connect signals
        self.username_edit.textChanged.connect(self.update_xml_username)
        self.password_edit.textChanged.connect(self.update_xml_password)
        self.show_id_edit.textChanged.connect(self.update_xml_show_id)

    def setup_hotkeys(self):
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_text)
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste_text)
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo_text)
        self.cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), self)
        self.cut_shortcut.activated.connect(self.cut_text)

    def copy_text(self):
        widget = self.focusWidget()
        if isinstance(widget, (QTextEdit, QLineEdit)):
            widget.copy()

    def paste_text(self):
        widget = self.focusWidget()
        if isinstance(widget, (QTextEdit, QLineEdit)):
            widget.paste()

    def undo_text(self):
        widget = self.focusWidget()
        if isinstance(widget, QTextEdit):
            widget.undo()

    def cut_text(self):
        widget = self.focusWidget()
        if isinstance(widget, (QTextEdit, QLineEdit)):
            widget.cut()

    def reset_request(self):
        self.username_edit.clear()
        self.password_edit.clear()
        self.show_id_edit.clear()
        self.set_default_request()
        self.response_edit.clear()
        QMessageBox.information(self, "Сброс", "Форма сброшена к исходному состоянию")

    def set_default_request(self):
        default_request = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:InticketsAPI">
   <soapenv:Header>
      <urn:Auth>
         <username></username>
         <password_md5></password_md5>
      </urn:Auth>
   </soapenv:Header>
   <soapenv:Body>
      <urn:getShows>
         <params>
            <show_id></show_id>
            <event_id></event_id>
            <hall_id></hall_id>
            <since_date></since_date>
            <to_date></to_date>
            <with_events>true</with_events>
            <with_halls>true</with_halls>
            <with_principal_info>true</with_principal_info>
            <with_personal_data>true</with_personal_data>
            <city></city>
         </params>
      </urn:getShows>
   </soapenv:Body>
</soapenv:Envelope>"""
        self.request_edit.setPlainText(default_request)

    def set_test_credentials(self):
        self.username_edit.setText("kassy.ru_sochi_gate")
        self.password_edit.setText("myFrN1bw")

    def get_md5_password(self):
        password = self.password_edit.text()
        return hashlib.md5(password.encode('utf-8')).hexdigest() if password else ""

    def update_xml_username(self):
        username = self.username_edit.text()
        self.update_xml_tag("username", username)

    def update_xml_password(self):
        md5_hash = self.get_md5_password()
        self.update_xml_tag("password_md5", md5_hash)

    def update_xml_show_id(self):
        show_id = self.show_id_edit.text()
        self.update_xml_tag("show_id", show_id)

    def update_xml_tag(self, tag_name, value):
        request = self.request_edit.toPlainText()
        pattern = re.compile(rf'<{tag_name}>(.*?)</{tag_name}>')

        if pattern.search(request):
            new_content = pattern.sub(f'<{tag_name}>{value}</{tag_name}>', request)
            self.request_edit.setPlainText(new_content)

    def open_accounts_link(self):
        webbrowser.open("https://disk.yandex.ru/edit/d/igXBAKIbB-MgsfJwwhzOkSPegnqahzm72s0qoIz-cKg6alFhTW1JN2ZiZw")

    def send_request(self):
        request_xml = self.request_edit.toPlainText().strip()
        if not request_xml:
            QMessageBox.critical(self, "Ошибка", "Тело запроса пустое")
            return

        wsdl_url = self.wsdl_edit.text().strip()
        if not wsdl_url:
            QMessageBox.critical(self, "Ошибка", "URL WSDL не указан")
            return

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            parsed_url = urlparse(wsdl_url)
            endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "urn:InticketsAPI#getShows",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "Apache-HttpClient/4.5.5 (Java/1.8.0_231)",
                "Connection": "keep-alive",
                "Accept": "text/xml"
            }

            params = {"ver": "2.2"}

            session = requests.Session()
            response = session.post(
                endpoint,
                data=request_xml.encode('utf-8'),
                headers=headers,
                params=params,
                timeout=30
            )

            # Обработка и форматирование XML
            xml_response = response.text

            # Заменяем namespace
            xml_response = xml_response.replace('ns0:Envelope', 'SOAP-ENV:Envelope')
            xml_response = xml_response.replace('xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"',
                                                'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"')
            xml_response = xml_response.replace('ns0:Body', 'SOAP-ENV:Body')
            xml_response = xml_response.replace('ns1:', 'ns1:')
            xml_response = xml_response.replace(' />', '/>')

            # Добавляем xsi namespace если его нет
            if 'xmlns:xsi=' not in xml_response:
                xml_response = xml_response.replace('SOAP-ENV:Envelope',
                                                    'SOAP-ENV:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                                                    1)

            # Форматируем XML с отступами
            try:
                from xml.dom import minidom
                dom = minidom.parseString(xml_response)
                formatted_xml = dom.toprettyxml(indent="   ", encoding='utf-8').decode('utf-8')

                # Убираем лишние пустые строки из prettyxml
                formatted_xml = '\n'.join([line for line in formatted_xml.split('\n') if line.strip()])
                self.response_edit.setPlainText(formatted_xml)
            except:
                # Если не удалось отформатировать, выводим как есть
                self.response_edit.setPlainText(xml_response)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка сети", f"Ошибка при отправке запроса: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def save_to_file(self):
        request_content = self.request_edit.toPlainText()
        request_content = re.sub(r'<password_md5>.*?</password_md5>', '<password_md5>***</password_md5>',
                                 request_content)
        response_content = self.response_edit.toPlainText()

        file_content = f"""Тело запроса
{'-' * 50}
{request_content}

Ответ
{'-' * 50}
{response_content}"""

        # Generate default filename
        current_date = datetime.now().strftime("%d%m%Y")
        username = self.username_edit.text() or "unknown"
        default_filename = f"soap_{current_date}_{username}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить запрос и ответ",
            default_filename,
            "Текстовые файлы (*.txt);;XML файлы (*.xml);;Все файлы (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                QMessageBox.information(self, "Успешно", f"Файл успешно сохранен:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SOAPAPITester()
    window.show()
    sys.exit(app.exec())