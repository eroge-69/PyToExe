import sys
import wmi
import os
import subprocess
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QInputDialog, QLineEdit, QCheckBox, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt



def activate10f():
    os.system('slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX')
    os.system('slmgr /skms kms.digiboy.ir')
    os.system('slmgr /ato')

def rebootf():
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/r", "/t", "1"], check=True)
    elif sys.platform == "linux" or sys.platform == "darwin":
        subprocess.run(["sudo", "reboot"], check=True)

def activatebykey():
    text, ok = QInputDialog.getText(None, 'активация своим ключом', 'ключ активации:')  
    if ok:  
        os.system('slmgr /ipk ' + text)
        os.system('slmgr /skms kms.digiboy.ir')
        os.system('slmgr /ato')

def activate7f():
    os.system('slmgr -rearm') 

def activatexpf():
    os.system('slmgr /skms kms.digiboy.ir')
    os.system('slmgr /ato')
    os.system('slmgr /xpr')

class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        def on_checkbox_toggled(is_checked):
            if is_checked:
                xpr_enabled.setChecked(False)
                kms_enabled.setChecked(False)
                ato_enabled.setChecked(False)
            else:
                kms_enabled.setChecked(True)
                xpr_enabled.setChecked(True)
                ato_enabled.setChecked(True)
        def start():
            pass

        def cancel():
            self.close()
        
        def reset_activ():
            reply = QMessageBox.question(
            self,  # Родительское окно
            'Подтверждение',  # Заголовок
            'Вы действительно хотите удалить активацию?',  # Текст вопроса
            QMessageBox.Yes | QMessageBox.No,  # Кнопки
            QMessageBox.No  # Кнопка по умолчанию
        )
        
            if reply == QMessageBox.Yes:
                os.system('slmgr /upk')
                os.system('slmgr /cpky')
                pass

        self.setWindowTitle("кастомная активация")
        self.setGeometry(500, 300, 500, 400)
        self.setWindowIcon(QIcon('icon.png'))
        code = QLineEdit()
        argscode = QLineEdit()
        code.setPlaceholderText('ключ активации')
        argscode.setPlaceholderText('дополнительные комманды')
        get_code = QPushButton('оприделить')
        key_enabled = QCheckBox('ввод ключа')
        ato_enabled = QCheckBox('slmgr /ato')
        xpr_enabled = QCheckBox('slmgr /xpr')
        kms_enabled = QCheckBox('slmgr /skms kms.digiboy.ir')
        btn_start = QPushButton('начать')
        btn_cancel = QPushButton('отмена')
        btn_reset = QPushButton('сбросить активацию')

        get_code.setStyleSheet("font: 12pt times")
        code.setStyleSheet("font: 12pt times")
        argscode.setStyleSheet("font: 12pt times")
        key_enabled.setStyleSheet("font: 12pt times")
        ato_enabled.setStyleSheet("font: 12pt times")
        xpr_enabled.setStyleSheet("font: 12pt times")
        kms_enabled.setStyleSheet("font: 12pt times")
        btn_start.setStyleSheet("font: 12pt times")
        btn_cancel.setStyleSheet("font: 12pt times")
        btn_reset.setStyleSheet("font: 12pt times")

        layout = QVBoxLayout()
        input_code = QHBoxLayout()
        navi = QHBoxLayout()

        input_code.addWidget(code)
        input_code.addWidget(get_code)
        layout.addLayout(input_code)
        layout.addWidget(key_enabled)
        layout.addWidget(kms_enabled)
        layout.addWidget(ato_enabled)
        layout.addWidget(xpr_enabled)
        layout.addWidget(argscode)
        navi.addWidget(btn_start)
        navi.addWidget(btn_cancel)
        navi.addWidget(btn_reset)
        layout.addLayout(navi)

        key_enabled.setChecked(True)

        key_enabled.toggled.connect(on_checkbox_toggled)
        btn_cancel.clicked.connect(cancel)
        btn_reset.clicked.connect(reset_activ)

        btn_start.setToolTip("начать активацию с задаными параметрами") 
        btn_reset.setToolTip("сбросить текущюю активацию системы")
        btn_cancel.setToolTip("закрыть окно") 
        get_code.setToolTip("попробовать найти ключ в репозитории") 
        code.setToolTip("код активации") 
        argscode.setToolTip("дополнительные комманды") 
        key_enabled.setToolTip("вставить ваш ключ активации") 

        self.setLayout(layout)

    

    def closeEvent(self, event):
        #window.setGeometry(500, 300, 500, 500)
        if hasattr(self, 'parent_window'):
            self.parent_window.second_window = None
        event.accept()



def custactive():
    second_window.show()
    #window.setGeometry(200, 100, 500, 500)

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("lime activator")
window.setWindowIcon(QIcon('icon.png'))

window.setGeometry(500, 300, 500, 500)

title = QLabel('')

second_window = SecondWindow()
second_window.setWindowModality(Qt.ApplicationModal)

def windows_activated():
    try:
        c = wmi.WMI()
        for os in c.Win32_OperatingSystem():
            if os.LicenseStatus == 1:
                return 'система активирована'
            else: return 'система не активирована'
    except Exception:
        return 'ошибка оприделения'
        


title.setText(str(windows_activated()))


title.setFont(QFont("Times", 20))

activate10 = QPushButton('активация вин 10')
activate7 = QPushButton('активация вин 7')
activate11 = QPushButton('активация вин 11')
activatexp = QPushButton('активация вин xp')
activateall = QPushButton('активация всех (работает не всегда)')
activatemykey = QPushButton('активация своим ключом')
custom = QPushButton('кастомная активация')
reboot = QPushButton('перезагрузка')

activate10.setStyleSheet("font: 12pt times")
activate7.setStyleSheet("font: 12pt times")
activatexp.setStyleSheet("font: 12pt times")
activateall.setStyleSheet("font: 12pt times")
reboot.setStyleSheet("font: 12pt times")
activatemykey.setStyleSheet("font: 12pt times")
custom.setStyleSheet("font: 12pt times")
activate11.setStyleSheet("font: 12pt times")

activate10.setToolTip("стандартная активация вин 10") 
activate7.setToolTip("стандартная активация вин 7") 
activatexp.setToolTip("стандартная активация вин xp") 
activateall.setToolTip("попытка активации любой ос (может не сработать)") 
reboot.setToolTip("перезагрузка (рекомендуется после активации ос)") 
activatemykey.setToolTip("стандартная активация ос вашим ключом") 
custom.setToolTip("кастомная активация с большим количеством настроек (рекомендуется для проффесионалов)") 
activate11.setToolTip("стандартная активация вин 11") 

activate10.clicked.connect(activate10f)
activate11.clicked.connect(activate10f)
reboot.clicked.connect(rebootf)
activatemykey.clicked.connect(activatebykey)
activate7.clicked.connect(activate7f)
activateall.clicked.connect(activate7f)
activatexp.clicked.connect(activatexpf)
custom.clicked.connect(custactive)


main = QVBoxLayout()

main.addWidget(title)
main.addWidget(activate11)
main.addWidget(activate10)
main.addWidget(activate7)
main.addWidget(activatexp)
main.addWidget(activatemykey)
main.addWidget(activateall)
main.addWidget(custom)
main.addWidget(reboot)
window.setLayout(main)

window.show()

app.exec_()