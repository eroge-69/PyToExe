import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtCore import QTimer, QDateTime

# نافذة التسجيل
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programme de Trésorerie - Login")
        self.resize(500, 350)

        layout = QVBoxLayout()

        # عنوان البرنامج
        title = QLabel("République Tunisienne – Ministère des Finances\nDirection Générale de la Comptabilité Publique et du Recouvrement")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # حقل المعرف
        self.user_id = QLineEdit()
        self.user_id.setPlaceholderText("Identifiant")
        layout.addWidget(self.user_id)

        # حقل كلمة السر
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # زر تسجيل الدخول
        login_button = QPushButton("Connexion")
        login_button.clicked.connect(self.check_login)
        layout.addWidget(login_button)

        # الوقت والتاريخ
        self.footer = QLabel(QDateTime.currentDateTime().toString("HH:mm dd/MM/yyyy"))
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

        # تحديث الوقت كل ثانية
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        self.setLayout(layout)

    def update_time(self):
        self.footer.setText(QDateTime.currentDateTime().toString("HH:mm dd/MM/yyyy"))

    def check_login(self):
        if self.user_id.text() == "admin" and self.password.text() == "1234567890ABCDE":
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiant ou mot de passe incorrect.")

# النافذة الرئيسية
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programme de Trésorerie - Tableau Principal")
        self.resize(800, 600)

        layout = QGridLayout()

        # Recettes مع 3 أقسام
        recettes_button = QPushButton("Recettes")
        recettes_button.clicked.connect(self.recettes_sections)
        layout.addWidget(recettes_button, 0, 0)

        # Dépenses مع 3 أقسام
        depenses_button = QPushButton("Dépenses")
        depenses_button.clicked.connect(self.depenses_sections)
        layout.addWidget(depenses_button, 0, 1)

        # Timbres fiscaux
        timbres_button = QPushButton("Timbres fiscaux")
        layout.addWidget(timbres_button, 0, 2)

        # Tableau quotidien
        daily_button = QPushButton("Tableau quotidien")
        daily_button.clicked.connect(self.daily_sections)
        layout.addWidget(daily_button, 1, 0)

        # Tableau mensuel
        monthly_button = QPushButton("Tableau mensuel")
        layout.addWidget(monthly_button, 1, 1)

        # Tableau annuel
        yearly_button = QPushButton("Tableau annuel")
        layout.addWidget(yearly_button, 1, 2)

        self.setLayout(layout)

    def recettes_sections(self):
        QMessageBox.information(self, "Recettes", "GRB\nRafiq\nAdab")

    def depenses_sections(self):
        QMessageBox.information(self, "Dépenses", "Rafiq\nAdab\nGRB")

    def daily_sections(self):
        QMessageBox.information(self, "Tableau quotidien",
                                "Chèques postaux et bancaires\nTransferts de solde interne et externe\nNom des écoles et instituts")

# تشغيل البرنامج
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout, QListWidget, QTextEdit
from PyQt5.QtCore import QTimer, QDateTime, Qt

# نافذة التسجيل
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programme de Trésorerie - Login")
        self.resize(500, 350)

        layout = QVBoxLayout()

        # عنوان البرنامج
        title = QLabel("République Tunisienne – Ministère des Finances\nDirection Générale de la Comptabilité Publique et du Recouvrement")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # حقل المعرف
        self.user_id = QLineEdit()
        self.user_id.setPlaceholderText("Identifiant")
        layout.addWidget(self.user_id)

        # حقل كلمة السر
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # زر تسجيل الدخول
        login_button = QPushButton("Connexion")
        login_button.clicked.connect(self.check_login)
        layout.addWidget(login_button)

        # الوقت والتاريخ
        self.footer = QLabel(QDateTime.currentDateTime().toString("HH:mm dd/MM/yyyy"))
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

        # تحديث الوقت كل ثانية
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        self.setLayout(layout)

    def update_time(self):
        self.footer.setText(QDateTime.currentDateTime().toString("HH:mm dd/MM/yyyy"))

    def check_login(self):
        if self.user_id.text() == "admin" and self.password.text() == "1234567890ABCDE":
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiant ou mot de passe incorrect.")

# نافذة الأقسام الفرعية
class SectionWindow(QWidget):
    def __init__(self, title, items):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout()
        label = QLabel(f"{title} Sections:")
        layout.addWidget(label)

        list_widget = QListWidget()
        for item in items:
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        self.setLayout(layout)

# نافذة Tableau quotidien مفصلة
class DailyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tableau quotidien")
        self.resize(500, 400)
        layout = QVBoxLayout()

        label = QLabel("Tableau quotidien:")
        layout.addWidget(label)

        # قائمة الشيكات والتحويلات
        list_widget = QListWidget()
        daily_items = [
            "Chèques postaux",
            "Chèques bancaires",
            "Transfert solde interne",
            "Transfert solde externe",
            "Nom des instituts et écoles"
        ]
        for item in daily_items:
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        self.setLayout(layout)

# نافذة Tableau mensuel/annuel
class TableWindow(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(500, 400)
        layout = QVBoxLayout()
        label = QLabel(title)
        layout.addWidget(label)

        # جدول نصي فارغ لتعبئة البيانات لاحقًا
        text_area = QTextEdit()
        text_area.setPlaceholderText("Remplir les données ici...")
        layout.addWidget(text_area)
        self.setLayout(layout)

# النافذة الرئيسية
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programme de Trésorerie - Tableau Principal")
        self.resize(800, 600)

        layout = QGridLayout()

        # Recettes مع الأقسام الثلاثة
        recettes_button = QPushButton("Recettes")
        recettes_button.clicked.connect(lambda: self.open_section("Recettes", ["GRB", "Rafiq", "Adab"]))
        layout.addWidget(recettes_button, 0, 0)

        # Dépenses مع الأقسام الثلاثة
        depenses_button = QPushButton("Dépenses")
        depenses_button.clicked.connect(lambda: self.open_section("Dépenses", ["Rafiq", "Adab", "GRB"]))
        layout.addWidget(depenses_button, 0, 1)

        # Timbres fiscaux
        timbres_button = QPushButton("Timbres fiscaux")
        layout.addWidget(timbres_button, 0, 2)

        # Tableau quotidien
        daily_button = QPushButton("Tableau quotidien")
        daily_button.clicked.connect(self.open_daily)
        layout.addWidget(daily_button, 1, 0)

        # Tableau mensuel
        monthly_button = QPushButton("Tableau mensuel")
        monthly_button.clicked.connect(lambda: self.open_table("Tableau mensuel"))
        layout.addWidget(monthly_button, 1, 1)

        # Tableau annuel
        yearly_button = QPushButton("Tableau annuel")
        yearly_button.clicked.connect(lambda: self.open_table("Tableau annuel"))
        layout.addWidget(yearly_button, 1, 2)

        self.setLayout(layout)

    def open_section(self, title, items):
        self.section_win = SectionWindow(title, items)
        self.section_win.show()

    def open_daily(self):
        self.daily_win = DailyWindow()
        self.daily_win.show()

    def open_table(self, title):
        self.table_win = TableWindow(title)
        self.table_win.show()

# تشغيل البرنامج
# بيانات الدخول للتجربة
IDENTIFIANT = "admin"
MOT_DE_PASSE = "1234567890ABCDE"


