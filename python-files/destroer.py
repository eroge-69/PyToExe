import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from telethon.sync import TelegramClient

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

class AccountDestroyer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('TG Account Destroyer')
        layout = QVBoxLayout()
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона (+7XXXXXXXXXX)")
        layout.addWidget(self.phone_input)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Код из Telegram")
        layout.addWidget(self.code_input)
        
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)
        
        self.btn_destroy = QPushButton("УНИЧТОЖИТЬ АККАУНТ")
        self.btn_destroy.clicked.connect(self.destroy_account)
        layout.addWidget(self.btn_destroy)
        
        self.setLayout(layout)
        
    def destroy_account(self):
        phone = self.phone_input.text()
        code = self.code_input.text()
        
        if not phone or not code:
            self.result_area.append("❌ Введите номер и код!")
            return
            
        try:
            with TelegramClient('destroyer', API_ID, API_HASH) as client:
                client.connect()
                client.sign_in(phone, code)
                client.delete_account()
                self.result_area.append(f"💀 АККАУНТ {phone} УНИЧТОЖЕН!")
        except Exception as e:
            self.result_area.append(f"⚠️ ОШИБКА: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AccountDestroyer()
    ex.show()
    sys.exit(app.exec_())