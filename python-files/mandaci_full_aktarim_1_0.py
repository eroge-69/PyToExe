"""
Mandacı Full Aktarım 1.0
Python 3.x GUI uygulaması (PyQt5)

Özellikler (en iyi çaba ile uygulanmıştır):
- Giriş ekranı (kullanıcı: yagiz, şifre: 17) + "Beni hatırla"
- Tam ekran ana arayüz, şık/dark-blue tasarım, beyaz kalın yazılar
- Cihazdan ADB aracılığıyla: DCIM, Pictures, Download klasörlerini çekme (adb pull)
- Rehber bilgilerini en iyi çabayla alma (content query ile) ve .vcf olarak kaydetme (basit VCF)
- Cihazdaki üçüncü taraf uygulamaların listesi (pm list packages -3) -> txt (sistem ve Google uygulamaları hariç)
- Yedekleme klasör düzeni: <SeçilenKlasor>/<DeviceName>Yedek/{gallery,rehber,bilgiler}
- Yedekleri geri yükleme (adb push ile) — medya dosyalarını uygun yerlere atacaktır
- Cihazda açık olan uygulamanın paket adını gösterme (dumpsys ile) ve uygulamayı silme (adb uninstall)

NOTLAR ve SINIRLAMALAR:
- Bu araç adb'nin PATH içinde yüklü olduğunu varsayar (kullanıcının belirttiği gibi).
- Android'in bazı sürümlerinde `adb backup` ve /data alanına erişim kısıtlıdır; rehber alma için en iyi çaba yöntemi uygulanır ama bazı telefonlarda tam VCF yapılamayabilir.
- Rehber içeriğini tam, düzgün bir vCard olarak almak için cihazda Contacts uygulamasından manuel export veya cihazın root erişimi gerekebilir.
- Uygulama ADB komutlarını çalışma zamanı boyunca çağırır; bağlı cihazın USB hata ayıklaması açık olmalıdır.

Gereksinimler (kurulum):
- Python 3.8+
- PyQt5

pip install pyqt5

Çalıştırma:
python Mandaci_Full_Aktarim_1.0.py

"""

import sys
import os
import subprocess
import json
import threading
import shutil
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

CREDENTIALS_FILE = os.path.join(os.path.expanduser('~'), '.mandaci_credentials.json')

# ---------------------- Yardımcı Fonksiyonlar ----------------------

def adb(cmd_args, capture_output=True):
    """adb komutunu çağırır, hata yakalar ve çıktı döndürür."""
    cmd = ['adb'] + cmd_args
    try:
        if capture_output:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return out.decode('utf-8', errors='ignore')
        else:
            subprocess.check_call(cmd)
            return ''
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='ignore')
    except FileNotFoundError:
        return None


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def sanitize_filename(name):
    return ''.join(c for c in name if c.isalnum() or c in '._-')

# ---------------------- UI Bileşenleri ----------------------

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Giriş - Mandacı Full Aktarım 1.0')
        self.setFixedSize(420, 260)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.init_ui()
        self.load_credentials()

    def init_ui(self):
        # Stil
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor('#0b2340'))
        self.setPalette(palette)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)

        title = QtWidgets.QLabel('Mandacı Full Aktarım 1.0')
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet('color: white; font-weight: 700; font-size: 18px;')

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)

        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText('Kullanıcı adı')
        self.username_edit.setStyleSheet('color: white; font-weight: 700; background: transparent;')

        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setPlaceholderText('Şifre')
        self.password_edit.setStyleSheet('color: white; font-weight: 700; background: transparent;')

        self.remember_cb = QtWidgets.QCheckBox('Beni hatırla')
        self.remember_cb.setStyleSheet('color: white; font-weight: 700;')

        form.addRow('Kullanıcı:', self.username_edit)
        form.addRow('Şifre:', self.password_edit)

        btn_login = QtWidgets.QPushButton('Giriş')
        btn_login.clicked.connect(self.on_login)
        btn_login.setDefault(True)
        btn_login.setStyleSheet('padding:10px; border-radius:8px;')

        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.remember_cb)
        layout.addStretch()
        layout.addWidget(btn_login)

        self.setLayout(layout)

    def load_credentials(self):
        try:
            if os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('remember'):
                        self.username_edit.setText(data.get('username', ''))
                        self.password_edit.setText(data.get('password', ''))
                        self.remember_cb.setChecked(True)
        except Exception:
            pass

    def save_credentials(self):
        try:
            data = {'remember': self.remember_cb.isChecked()}
            if self.remember_cb.isChecked():
                data['username'] = self.username_edit.text()
                data['password'] = self.password_edit.text()
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def on_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if username == 'yagiz' and password == '17':
            self.save_credentials()
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, 'Hata', 'Kullanıcı adı veya şifre yanlış.')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mandacı Full Aktarım 1.0')
        self.init_ui()

    def init_ui(self):
        # Tam ekran
        self.showMaximized()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)

        # Stil
        self.setStyleSheet('QWidget { background-color: #0b2340; color: white; font-weight:700; }')

        # Toolbar / Controls
        top_bar = QtWidgets.QHBoxLayout()

        self.device_label = QtWidgets.QLabel('Bağlı cihaz: (yükleniyor...)')
        btn_refresh = QtWidgets.QPushButton('Cihaz Yenile')
        btn_refresh.clicked.connect(self.refresh_device)

        btn_choose_folder = QtWidgets.QPushButton('Hedef Klasör Seç')
        btn_choose_folder.clicked.connect(self.choose_folder)

        btn_backup = QtWidgets.QPushButton('Yedek Al (Media + Rehber + Bilgiler)')
        btn_backup.clicked.connect(self.start_backup_thread)

        btn_restore = QtWidgets.QPushButton('Yedekten Yükle')
        btn_restore.clicked.connect(self.start_restore_thread)

        top_bar.addWidget(self.device_label)
        top_bar.addStretch()
        top_bar.addWidget(btn_refresh)
        top_bar.addWidget(btn_choose_folder)
        top_bar.addWidget(btn_backup)
        top_bar.addWidget(btn_restore)

        layout.addLayout(top_bar)

        # Middle area with info and actions
        middle = QtWidgets.QHBoxLayout()

        left_card = QtWidgets.QGroupBox('Cihaz İşlemleri')
        left_layout = QtWidgets.QVBoxLayout()

        btn_show_foreground = QtWidgets.QPushButton('Ekranda Açık Uygulama')
        btn_show_foreground.clicked.connect(self.show_foreground)

        btn_list_apps = QtWidgets.QPushButton('Üçüncü Taraf Uygulama Listele')
        btn_list_apps.clicked.connect(self.list_third_party_apps)

        btn_uninstall = QtWidgets.QPushButton('Seçili Paketi Kaldır')
        btn_uninstall.clicked.connect(self.uninstall_package)

        left_layout.addWidget(btn_show_foreground)
        left_layout.addWidget(btn_list_apps)
        left_layout.addWidget(btn_uninstall)
        left_layout.addStretch()
        left_card.setLayout(left_layout)

        right_card = QtWidgets.QGroupBox('Günlük / Durum')
        right_layout = QtWidgets.QVBoxLayout()
        self.log_edit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        right_layout.addWidget(self.log_edit)
        right_card.setLayout(right_layout)

        middle.addWidget(left_card, 1)
        middle.addWidget(right_card, 2)

        layout.addLayout(middle)

        # Varsayılan hedef klasör
        self.target_base = os.path.join(os.path.expanduser('~'), 'MandaciYedekler')
        ensure_dir(self.target_base)

        # Başlangıçta cihaz kontrolü
        self.refresh_device()

    # ---------------------- UI Yardımcıları ----------------------
    def log(self, text):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_edit.append(f'[{ts}] {text}')

    def refresh_device(self):
        out = adb(['devices'])
        if out is None:
            QtWidgets.QMessageBox.critical(self, 'Hata', 'adb bulunamadı. Lütfen adb PATH içinde olduğundan emin olun.')
            self.device_label.setText('Bağlı cihaz: (adb yok)')
            return
        lines = [l for l in out.splitlines() if l.strip()]
        devices = []
        for l in lines[1:]:
            if '\tdevice' in l:
                devices.append(l.split('\t')[0])
        if devices:
            self.device_serial = devices[0]
            self.device_label.setText(f'Bağlı cihaz: {self.device_serial}')
            self.log(f'Cihaz bulundu: {self.device_serial}')
        else:
            self.device_serial = None
            self.device_label.setText('Bağlı cihaz: (yok)')
            self.log('Cihaz bağlı değil')

    def choose_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Hedef Klasör Seç', self.target_base)
        if folder:
            self.target_base = folder
            self.log(f'Hedef klasör: {self.target_base}')

    # ---------------------- Özellik: Yedek Alma ----------------------
    def start_backup_thread(self):
        t = threading.Thread(target=self.backup_flow)
        t.start()

    def backup_flow(self):
        if not self.device_serial:
            self.log('Yedekleme: cihaz bağlı değil.')
            return
        # Cihaz adı alma
        dev_name = self.get_device_model()
        folder_name = f"{sanitize_filename(dev_name)}Yedek"
        dest = os.path.join(self.target_base, folder_name)
        ensure_dir(dest)
        self.log(f'Yedek klasörü: {dest}')

        # gallery klasörü
        gallery_dir = os.path.join(dest, 'gallery')
        ensure_dir(gallery_dir)

        # Media klasörleri çek
        media_paths = ['/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download']
        for p in media_paths:
            self.log(f'Media çekiliyor: {p}')
            # adb pull için alt klasör ismi
            base = os.path.basename(p)
            local_target = os.path.join(gallery_dir, base)
            ensure_dir(local_target)
            out = adb(['-s', self.device_serial, 'pull', p, local_target])
            if out is None:
                self.log('adb bulunamadı veya çekilemedi.')
                return
            self.log(out)

        # Rehber alma - en iyi çaba: content query ile isimleri çek ve basit vcf oluştur
        rehber_dir = os.path.join(dest, 'rehber')
        ensure_dir(rehber_dir)
        vcf_path = os.path.join(rehber_dir, 'contacts.vcf')
        self.log('Rehber bilgileri çekiliyor (en iyi çaba).')
        contacts_raw = adb(['-s', self.device_serial, 'shell', 'content', 'query', '--uri', 'content://com.android.contacts/contacts'])
        if contacts_raw:
            try:
                vcfs = self.parse_contacts_to_vcf(contacts_raw)
                with open(vcf_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(vcfs))
                self.log(f'Rehber kaydedildi: {vcf_path}')
            except Exception as e:
                self.log(f'Rehber kaydedilirken hata: {e}')
        else:
            self.log('Rehber verisi çekilemedi veya cihaz content provider kısıtlı.')

        # Bilgiler klasörü: e-posta ve uygulama listesi (üçüncü taraf)
        infos_dir = os.path.join(dest, 'bilgiler')
        ensure_dir(infos_dir)

        # E-posta adresleri (cihaz hesapları)
        self.log('Cihazdaki hesaplar çekiliyor...')
        accounts_out = adb(['-s', self.device_serial, 'shell', 'dumpsys', 'account'])
        emails = self.extract_emails(accounts_out)
        emails_file = os.path.join(infos_dir, 'emails.txt')
        with open(emails_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(emails))
        self.log(f'E-posta adresleri kaydedildi: {emails_file}')

        # Uygulama listesi (sistem ve Google uygulamaları dahil etmeyecek şekilde en iyi çaba)
        self.log('Üçüncü taraf uygulamalar listeleniyor...')
        apps_out = adb(['-s', self.device_serial, 'shell', 'pm', 'list', 'packages', '-3'])
        app_lines = [l.strip() for l in apps_out.splitlines() if l.strip()]
        apps = [l.replace('package:', '') for l in app_lines]
        apps_file = os.path.join(infos_dir, 'third_party_apps.txt')
        with open(apps_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(apps))
        self.log(f'Uygulama listesi kaydedildi: {apps_file}')

        self.log('Yedek alma işlemi tamamlandı.')

    def get_device_model(self):
        out = adb(['-s', self.device_serial, 'shell', 'getprop', 'ro.product.model'])
        if out:
            return out.strip().replace(' ', '')
        return 'AndroidDevice'

    def parse_contacts_to_vcf(self, raw):
        # content query çıktısını parse edip minimal vCard üretir ( sadece DISPLAY_NAME kullanılır )
        vcfs = []
        lines = raw.splitlines()
        for line in lines:
            if 'display_name=' in line:
                parts = line.split(',')
                name = None
                for p in parts:
                    p = p.strip()
                    if p.startswith('display_name='):
                        name = p.split('=', 1)[1]
                if name:
                    name = name.strip()
                    vcfs.append('BEGIN:VCARD')
                    vcfs.append('VERSION:3.0')
                    vcfs.append(f'FN:{name}')
                    vcfs.append('END:VCARD')
        return vcfs

    def extract_emails(self, dumpsys_output):
        emails = set()
        if not dumpsys_output:
            return []
        import re
        for m in re.finditer(r'[\w\.-]+@[\w\.-]+', dumpsys_output):
            emails.add(m.group(0))
        return list(emails)

    # ---------------------- Özellik: Yedekten Yükleme ----------------------
    def start_restore_thread(self):
        t = threading.Thread(target=self.restore_flow)
        t.start()

    def restore_flow(self):
        if not self.device_serial:
            self.log('Yükleme: cihaz bağlı değil.')
            return
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Yedek Klasörü Seç', self.target_base)
        if not folder:
            self.log('Yedek yükleme iptal edildi.')
            return
        # assume selected is device folder
        self.log(f'Yedekten yükleme başlıyor: {folder}')
        # Media push back to sdcard
        gallery_dir = os.path.join(folder, 'gallery')
        if os.path.exists(gallery_dir):
            for sub in os.listdir(gallery_dir):
                local_path = os.path.join(gallery_dir, sub)
                target_remote = f'/sdcard/{sub}'
                self.log(f'Yüklenecek: {local_path} -> {target_remote}')
                out = adb(['-s', self.device_serial, 'push', local_path, target_remote])
                self.log(out)
        # Rehber yükleme: push vcf and try to launch import intent
        rehber_dir = os.path.join(folder, 'rehber')
        if os.path.exists(rehber_dir):
            for f in os.listdir(rehber_dir):
                local = os.path.join(rehber_dir, f)
                remote = f'/sdcard/{f}'
                self.log(f'Rehber yükleniyor: {local} -> {remote}')
                out = adb(['-s', self.device_serial, 'push', local, remote])
                self.log(out)
                # try to launch import intent (may require user interaction)
                try:
                    adb(['-s', self.device_serial, 'shell', 'am', 'start', '-t', 'text/x-vcard', '-d', f'file://{remote}', 'android.intent.action.VIEW'])
                except Exception as e:
                    self.log(f'Import intent başlatılamadı: {e}')
        self.log('Yedekten yükleme tamamlandı (en iyi çaba).')

    # ---------------------- Özellik: Ekranda açık uygulamayı gösterme ----------------------
    def show_foreground(self):
        if not self.device_serial:
            self.log('Cihaz bağlı değil.')
            return
        out = adb(['-s', self.device_serial, 'shell', 'dumpsys', 'window', 'windows'])
        pkg = None
        for line in out.splitlines():
            if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                import re
                m = re.search(r'([\w\.]+)/(\S+)', line)
                if m:
                    pkg = m.group(1)
                    break
        if not pkg:
            # alternatif
            out2 = adb(['-s', self.device_serial, 'shell', 'dumpsys', 'activity', 'activities'])
            for line in out2.splitlines():
                if 'mResumedActivity' in line or 'ResumedActivity' in line:
                    import re
                    m = re.search(r'([\w\.]+)/(\S+)', line)
                    if m:
                        pkg = m.group(1)
                        break
        if pkg:
            self.log(f'Ekranda açık uygulama: {pkg}')
            QtWidgets.QMessageBox.information(self, 'Açık Uygulama', pkg)
            self.last_foreground_pkg = pkg
        else:
            self.log('Açık uygulama bulunamadı.')

    def list_third_party_apps(self):
        if not self.device_serial:
            self.log('Cihaz bağlı değil.')
            return
        out = adb(['-s', self.device_serial, 'shell', 'pm', 'list', 'packages', '-3'])
        apps = [l.replace('package:', '') for l in out.splitlines() if l.strip()]
        QtWidgets.QMessageBox.information(self, 'Üçüncü Taraf Uygulamalar', f'{len(apps)} uygulama bulundu. Kayıt edilecek.')
        self.log(f'{len(apps)} üçüncü taraf uygulama bulundu.')
        # Kaydet
        target_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Uygulama listesini kaydetmek için klasör seçin', self.target_base)
        if target_folder:
            infos_dir = os.path.join(target_folder, 'bilgiler')
            ensure_dir(infos_dir)
            apps_file = os.path.join(infos_dir, 'third_party_apps.txt')
            with open(apps_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(apps))
            self.log(f'Uygulama listesi kaydedildi: {apps_file}')

    def uninstall_package(self):
        pkg, ok = QtWidgets.QInputDialog.getText(self, 'Kaldır', 'Kaldırmak istediğiniz paket adı:')
        if ok and pkg:
            confirm = QtWidgets.QMessageBox.question(self, 'Onay', f'{pkg} paketini kaldırmak istediğinize emin misiniz?')
            if confirm == QtWidgets.QMessageBox.Yes:
                out = adb(['-s', self.device_serial, 'uninstall', pkg])
                self.log(out)
                QtWidgets.QMessageBox.information(self, 'Sonuç', out)

# ---------------------- Uygulama Başlatma ----------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    # global uygulama fontu
    font = QtGui.QFont('Segoe UI', 10)
    app.setFont(font)

    login = LoginDialog()
    login.setWindowModality(QtCore.Qt.ApplicationModal)
    login.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
    login.exec_()
    if login.result() == QtWidgets.QDialog.Accepted:
        mainw = MainWindow()
        mainw.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
