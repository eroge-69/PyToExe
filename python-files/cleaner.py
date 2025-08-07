import os
import shutil
import sys
import getpass
from PyQt5.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QCheckBox, QPushButton, QVBoxLayout, QMessageBox
import win32com.client
import tempfile

class InstallWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temizleyici Kurulum Sihirbazı")
        self.addPage(WelcomePage())
        self.addPage(InstallPage())
        self.addPage(FinishPage())
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Temizleyiciye Hoş Geldiniz")
        layout = QVBoxLayout()
        label = QLabel("Bu sihirbaz, Temizleyici programını kurmanıza yardımcı olacak.")
        layout.addWidget(label)
        self.setLayout(layout)

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Kurulum Ayarları")
        layout = QVBoxLayout()
        self.checkbox = QCheckBox("Kurulum tamamlandıktan sonra programı çalıştır")
        self.checkbox.setChecked(True)
        layout.addWidget(QLabel("Kurulum ayarlarını yapılandırın:"))
        layout.addWidget(self.checkbox)
        self.setLayout(layout)

    def cleanup(self):
        return self.checkbox.isChecked()

class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Kurulum Tamamlandı")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Temizleyici başarıyla kuruldu!"))
        self.setLayout(layout)

    def initializePage(self):
        self.create_shortcut()
        if self.wizard().page(1).cleanup():
            self.run_cleaner()

    def create_shortcut(self):
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut_path = os.path.join(desktop, "Temizleyici.lnk")
        target = os.path.abspath(sys.argv[0])
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.WindowStyle = 1
        shortcut.Description = "Temizleyici Programı"
        shortcut.save()

    def run_cleaner(self):
        app = QApplication(sys.argv)
        cleaner = CleanerWindow()
        cleaner.show()
        app.exec_()

class CleanerWindow(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temizleyici")
        self.setWizardStyle(QWizard.ModernStyle)
        self.addPage(CleanPage())

class CleanPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Bilgisayar Temizleyici")
        layout = QVBoxLayout()
        self.clean_button = QPushButton("Temizliği Başlat")
        self.clean_button.clicked.connect(self.start_cleaning)
        layout.addWidget(self.clean_button)
        self.setLayout(layout)

    def start_cleaning(self):
        self.clean_button.setEnabled(False)
        self.clean_button.setText("Temizlik Yapılıyor...")
        QApplication.processEvents()  # GUI'nin güncellenmesini sağla

        # Temizlenecek klasörler
        folders = [
            tempfile.gettempdir(),  # %temp%
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp'),  # temp
            os.path.join(os.environ['SYSTEMROOT'], 'Prefetch'),  # prefetch
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent')  # recent
        ]

        for folder in folders:
            try:
                if os.path.exists(folder):
                    for item in os.listdir(folder):
                        item_path = os.path.join(folder, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        except Exception as e:
                            print(f"Hata: {item_path} silinirken: {e}")
            except Exception as e:
                print(f"Hata: {folder} işlenirken: {e}")

        QMessageBox.information(self, "Temizlik Tamamlandı", "Geçici dosyalar başarıyla temizlendi!")
        self.clean_button.setText("Temizliği Başlat")
        self.clean_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    wizard = InstallWizard()
    wizard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()