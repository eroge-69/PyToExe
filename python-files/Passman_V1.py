# passman_final_v2.py
# Passman — full-featured local password manager with:
# - Frameless mac-style UI, blur-first fallback -> dark glass
# - Master password (KDF PBKDF2 + Fernet)
# - Vault encryption, autosave on add/edit/delete
# - Add uses bottom fields, Edit opens dialog
# - Copy Password + Copy Username
# - Settings gear: Open Vault Location, Reset Master Password, Import/Export .txt, Hotkeys
# - App-only customizable shortcuts (saved to config)
# - Safe startup, extensive error handling
#
# Requires: PySide6, cryptography, pyperclip
# pip install PySide6 cryptography pyperclip

import sys, os, json, time, traceback, base64, re, shutil
from pathlib import Path
from functools import partial

from PySide6 import QtCore, QtGui, QtWidgets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import pyperclip
import ctypes
import string
import random

# ---------------- paths & config ----------------
APPNAME = "Passman"
BASE_PATH = Path(sys.argv[0]).resolve().parent
VAULT_FILE = BASE_PATH / "passman_vault.bin"
MASTER_META = BASE_PATH / "passman_master.json"
CONFIG_FILE = BASE_PATH / "passman_config.json"

DEFAULT_CONFIG = {
    "hotkeys": {  # app-only QShortcut sequences
        "add": "Ctrl+N",
        "delete": "Del",
        "copy_pass": "Ctrl+Shift+C",
        "copy_user": "Ctrl+Shift+U",
        "lock": "Ctrl+L",
    },
    "ui": {
        "blur_attempt": True
    }
}

def load_config():
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to save config:", e)

cfg = load_config()

# ---------------- crypto helpers ----------------
KDF_SALT_BYTES = 16
KDF_ITERATIONS = 200_000

def _generate_salt():
    return os.urandom(KDF_SALT_BYTES)

def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    pwd = password.encode('utf-8')
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=KDF_ITERATIONS, backend=default_backend())
    raw = kdf.derive(pwd)
    return base64.urlsafe_b64encode(raw)  # fernet-compatible key

def encrypt_blob(plaintext: bytes, fernet_key_b64: bytes) -> bytes:
    return Fernet(fernet_key_b64).encrypt(plaintext)

def decrypt_blob(ct: bytes, fernet_key_b64: bytes) -> bytes:
    return Fernet(fernet_key_b64).decrypt(ct)

# ---------------- master management ----------------
def master_exists() -> bool:
    return MASTER_META.exists()

def create_master(password: str):
    salt = _generate_salt()
    key = _derive_key_from_password(password, salt)
    marker = f"passman_marker:{int(time.time())}".encode('utf-8')
    token = encrypt_blob(marker, key)
    data = {"salt": base64.b64encode(salt).decode('ascii'), "token": base64.b64encode(token).decode('ascii')}
    MASTER_META.write_text(json.dumps(data), encoding="utf-8")
    return True

def verify_master(password: str):
    try:
        data = json.loads(MASTER_META.read_text(encoding="utf-8"))
        salt = base64.b64decode(data["salt"])
        token = base64.b64decode(data["token"])
        key = _derive_key_from_password(password, salt)
        _ = decrypt_blob(token, key)
        return key
    except Exception:
        return None

# ---------------- vault load/save ----------------
def load_vault_with_key(key_b64: bytes):
    if not VAULT_FILE.exists():
        return []
    try:
        ct = VAULT_FILE.read_bytes()
        pt = decrypt_blob(ct, key_b64)
        return json.loads(pt.decode('utf-8'))
    except Exception as e:
        raise

def save_vault_with_key(entries: list, key_b64: bytes):
    pt = json.dumps(entries, separators=(',',':')).encode('utf-8')
    ct = encrypt_blob(pt, key_b64)
    VAULT_FILE.write_bytes(ct)

# ---------------- Windows blur attempt (safe) ----------------
def try_enable_windows_blur(hwnd):
    # try a simple DwmEnableBlurBehindWindow call; if it fails, return False
    try:
        dwmapi = ctypes.windll.dwmapi
        class DWM_BLURBEHIND(ctypes.Structure):
            _fields_ = [("dwFlags", ctypes.c_uint), ("fEnable", ctypes.c_bool), ("hRgnBlur", ctypes.c_void_p), ("fTransitionOnMaximized", ctypes.c_bool)]
        DWM_BB_ENABLE = 0x00000001
        bb = DWM_BLURBEHIND()
        bb.dwFlags = DWM_BB_ENABLE
        bb.fEnable = True
        bb.hRgnBlur = 0
        bb.fTransitionOnMaximized = False
        hwnd_c = ctypes.c_void_p(int(hwnd))
        res = dwmapi.DwmEnableBlurBehindWindow(hwnd_c, ctypes.byref(bb))
        return True
    except Exception:
        return False

# ---------------- UI helpers ----------------
class WordEdit(QtWidgets.QLineEdit):
    """Ctrl+Backspace deletes previous word"""
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Backspace and (event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
            s = self.text()
            pos = self.cursorPosition()
            if pos == 0:
                return
            left = s[:pos]
            m = re.search(r'(\w+|\s+|\W+)$', left)
            if m:
                start = pos - len(m.group(0))
                new = s[:start] + s[pos:]
                self.setText(new)
                self.setCursorPosition(start)
                return
        super().keyPressEvent(event)

# ---------------- Dialogs ----------------
class MasterDialog(QtWidgets.QDialog):
    def __init__(self, create_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Master Password" if create_mode else "Unlock Vault")
        self.create_mode = create_mode
        self.setModal(True)
        v = QtWidgets.QVBoxLayout(self)
        if create_mode:
            v.addWidget(QtWidgets.QLabel("Create a master password (min 8 chars). This cannot be recovered."))
            self.p1 = QtWidgets.QLineEdit(); self.p1.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.p2 = QtWidgets.QLineEdit(); self.p2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            v.addWidget(QtWidgets.QLabel("Password:")); v.addWidget(self.p1)
            v.addWidget(QtWidgets.QLabel("Confirm:")); v.addWidget(self.p2)
        else:
            v.addWidget(QtWidgets.QLabel("Enter master password to unlock vault:"))
            self.p1 = QtWidgets.QLineEdit(); self.p1.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            v.addWidget(self.p1)
            btn_forgot = QtWidgets.QPushButton("Forgot / Reset")
            btn_forgot.clicked.connect(self.on_forgot)
            v.addWidget(btn_forgot)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def on_forgot(self):
        res = QtWidgets.QMessageBox.question(self, "Reset Vault", "This will create an encrypted backup (if present) and delete the vault & master. Continue?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if res == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                # backup vault and master meta
                ts = time.strftime("%Y%m%d%H%M%S")
                if VAULT_FILE.exists():
                    shutil.copy2(VAULT_FILE, VAULT_FILE.with_suffix(".bak."+ts))
                if MASTER_META.exists():
                    shutil.copy2(MASTER_META, MASTER_META.with_suffix(".bak."+ts))
                # delete originals
                if VAULT_FILE.exists(): VAULT_FILE.unlink()
                if MASTER_META.exists(): MASTER_META.unlink()
                QtWidgets.QMessageBox.information(self, "Reset", "Vault and master removed. Restart app to create new master.")
                QtWidgets.QApplication.quit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Reset failed: {e}")

    def get_passwords(self):
        if self.create_mode:
            return self.p1.text(), self.p2.text()
        else:
            return self.p1.text()

class EntryDialog(QtWidgets.QDialog):
    def __init__(self, entry=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry" if entry else "New Entry")
        v = QtWidgets.QVBoxLayout(self)
        self.title = QtWidgets.QLineEdit(); self.title.setPlaceholderText("Website / Service")
        self.user = QtWidgets.QLineEdit(); self.user.setPlaceholderText("Username")
        self.pwd = WordEdit(); self.pwd.setPlaceholderText("Password")
        self.url = QtWidgets.QLineEdit(); self.url.setPlaceholderText("URL (optional)")
        self.notes = QtWidgets.QTextEdit(); self.notes.setPlaceholderText("Notes (optional)")
        v.addWidget(QtWidgets.QLabel("Title")); v.addWidget(self.title)
        v.addWidget(QtWidgets.QLabel("Username")); v.addWidget(self.user)
        v.addWidget(QtWidgets.QLabel("Password")); v.addWidget(self.pwd)
        v.addWidget(QtWidgets.QLabel("URL")); v.addWidget(self.url)
        v.addWidget(QtWidgets.QLabel("Notes")); v.addWidget(self.notes)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        v.addWidget(btns)
        if entry:
            self.title.setText(entry.get("title",""))
            self.user.setText(entry.get("username",""))
            self.pwd.setText(entry.get("password",""))
            self.url.setText(entry.get("url",""))
            self.notes.setPlainText(entry.get("notes",""))

    def get_entry(self):
        return {
            "title": self.title.text(),
            "username": self.user.text(),
            "password": self.pwd.text(),
            "url": self.url.text(),
            "notes": self.notes.toPlainText(),
            "ts": int(time.time())
        }

# ---------------- Main Window ----------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APPNAME)
        self.resize(980, 620)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.key = None
        self.entries = []
        self._show_passwords = False
        self._stay_on_top = False  # Track stay on top state

        # Frameless but keep native window shadow: remove native title bar
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        
        # Set up background with proper transparency handling
        try:
            if cfg.get("ui", {}).get("blur_attempt", True):
                hwnd = int(self.winId())
                try_enable_windows_blur(hwnd)
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
                # Use semi-transparent background instead of fully transparent
                # MODIFIED: Changed alpha value for transparency+blur
                self.setStyleSheet("MainWindow { background-color: rgba(40, 40, 40, 180); }")
            else:
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
                self.setStyleSheet("MainWindow { background-color: rgba(40, 40, 40, 180); }")
        except Exception:
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
            self.setStyleSheet("MainWindow { background-color: rgba(40, 40, 40, 180); }")

        self._drag_pos = None
        self._init_ui()
        self.run_master_flow()
        # register shortcuts from config (app-only)
        self.apply_shortcuts_from_config()

    # NEW: Password generation function
    def _generate_strong_password(self, length=16):
        """Generates a strong password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def _init_ui(self):
        root = QtWidgets.QVBoxLayout(self.central)
        root.setContentsMargins(10,10,10,10)
        root.setSpacing(8)

        # Create a container widget with solid background to prevent click-through
        container = QtWidgets.QWidget()
        container.setStyleSheet("""
            QWidget {
                /* MODIFIED: Changed alpha value for transparency+blur */
                background-color: rgba(30, 30, 30, 180);
                border-radius: 10px;
                /* REMOVED THE EXTRA BORDER: */
                /* border: 1px solid rgba(255, 255, 255, 0.1); */
            }
        """)
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(8)

        # top bar: traffic buttons + title (mac-like)
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(8)
        self.btn_close = QtWidgets.QPushButton(); self.btn_min = QtWidgets.QPushButton(); self.btn_max = QtWidgets.QPushButton()
        for b,c in ((self.btn_close, "#ff5f56"), (self.btn_min, "#ffbd2e"), (self.btn_max, "#27ca3f")):
            b.setFixedSize(14,14)
            b.setStyleSheet(f"border-radius:7px; background:{c}; border:1px solid rgba(0,0,0,0.25);")
        self.btn_close.clicked.connect(self.close)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)
        top.addWidget(self.btn_close); top.addWidget(self.btn_min); top.addWidget(self.btn_max)
        top.addSpacing(8)
        self.title_label = QtWidgets.QLabel("Password Manager")
        self.title_label.setStyleSheet("color: #fff; font-weight:600; font-size:14px;")
        top.addWidget(self.title_label)
        top.addStretch()
        container_layout.addLayout(top)

        # table
        self.table = QtWidgets.QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(["Website","Username","Password"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { 
                background: rgba(25,25,25,220); 
                color: #ddd; 
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            } 
            QHeaderView::section { 
                background: rgba(12,12,12,200); 
                color: #fff; border: none;
                padding: 5px;
            }
        """)
        container_layout.addWidget(self.table, stretch=3)

        # input fields (use these for Add)
        form = QtWidgets.QGridLayout()
        form.setSpacing(6)
        lbl_w = QtWidgets.QLabel("Website"); self.in_website = WordEdit()
        lbl_u = QtWidgets.QLabel("Username"); self.in_user = WordEdit()
        lbl_p = QtWidgets.QLabel("Password"); self.in_pass = WordEdit(); self.in_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        
        # Style labels and inputs
        for lbl in [lbl_w, lbl_u, lbl_p]:
            lbl.setStyleSheet("color: #ddd; font-weight: 500;")
        
        for inp in [self.in_website, self.in_user, self.in_pass]:
            inp.setStyleSheet("""
                QLineEdit {
                    background: rgba(50, 50, 50, 180);
                    color: #fff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    padding: 5px;
                }
                QLineEdit:focus {
                    border: 2px solid #4CAF50; }
            """)
        
        form.addWidget(lbl_w, 0, 0); form.addWidget(self.in_website, 0, 1)
        form.addWidget(lbl_u, 1, 0); form.addWidget(self.in_user, 1, 1)
        form.addWidget(lbl_p, 2, 0); 
        pwrow = QtWidgets.QHBoxLayout()
        pwrow.addWidget(self.in_pass)
        
        # NEW: Generate password button
        self.btn_gen_pass = QtWidgets.QPushButton("🔑")
        self.btn_gen_pass.setFixedSize(36,36)
        self.btn_gen_pass.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 60, 180);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 80, 200);
            }
        """)
        self.btn_gen_pass.clicked.connect(lambda: self.in_pass.setText(self._generate_strong_password()))
        pwrow.addWidget(self.btn_gen_pass)
        
        self.btn_eye = QtWidgets.QPushButton("👁"); self.btn_eye.setFixedSize(36,36); self.btn_eye.setCheckable(True)
        self.btn_eye.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 60, 180);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QPushButton:checked {
                background: rgba(80, 80, 80, 200);
            }
        """)
        self.btn_eye.toggled.connect(self.on_toggle_eye)
        pwrow.addWidget(self.btn_eye)
        form.addLayout(pwrow, 2, 1)
        container_layout.addLayout(form)

        # buttons row (Add uses bottom fields) - Removed Save Vault and Open Vault Location
        btn_row = QtWidgets.QHBoxLayout()
        add_color = "#4CAF50"; del_color = "#f44336"; copy_color = "#2196F3"; stay_color = "#FF9800"; lock_color = "#9C27B0"
        btn_style_tpl = """
            QPushButton {{ 
                background-color: rgba(50,50,50,210); 
                color: {c}; 
                border: 2px solid {c}; 
                font-weight:600; 
                border-radius: 5px;
                padding: 8px 12px;
            }} 
            QPushButton:hover {{ 
                background-color: {c}; 
                color: black; 
            }}
            QPushButton:checked {{
                background-color: {c};
                color: black;
            }}
        """
        
        self.btn_add = QtWidgets.QPushButton("Add"); self.btn_add.setFixedHeight(40); self.btn_add.setStyleSheet(btn_style_tpl.format(c=add_color))
        self.btn_delete = QtWidgets.QPushButton("Delete"); self.btn_delete.setFixedHeight(40); self.btn_delete.setStyleSheet(btn_style_tpl.format(c=del_color))
        self.btn_copy_pass = QtWidgets.QPushButton("Copy Pass"); self.btn_copy_pass.setFixedHeight(40); self.btn_copy_pass.setStyleSheet(btn_style_tpl.format(c=copy_color))
        self.btn_copy_user = QtWidgets.QPushButton("Copy User"); self.btn_copy_user.setFixedHeight(40); self.btn_copy_user.setStyleSheet(btn_style_tpl.format(c=copy_color))
        self.btn_stay = QtWidgets.QPushButton("Stay On Top"); self.btn_stay.setFixedHeight(40); self.btn_stay.setCheckable(True); self.btn_stay.setStyleSheet(btn_style_tpl.format(c=stay_color))
        self.btn_lock = QtWidgets.QPushButton("Lock"); self.btn_lock.setFixedHeight(40); self.btn_lock.setStyleSheet(btn_style_tpl.format(c=lock_color))
        self.btn_edit = QtWidgets.QPushButton("Edit"); self.btn_edit.setFixedHeight(40); self.btn_edit.setStyleSheet(btn_style_tpl.format(c="#ffffff"))

        for w in (self.btn_add, self.btn_delete, self.btn_edit, self.btn_copy_pass, self.btn_copy_user, self.btn_stay, self.btn_lock):
            btn_row.addWidget(w)
        container_layout.addLayout(btn_row)

        # gear settings bottom-right
        gear_layout = QtWidgets.QHBoxLayout()
        gear_layout.addStretch()
        self.btn_gear = QtWidgets.QPushButton("⚙")  # gear
        self.btn_gear.setFixedSize(36,36); self.btn_gear.setToolTip("Settings")
        self.btn_gear.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 60, 180);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 80, 200);
            }
        """)
        gear_layout.addWidget(self.btn_gear)
        container_layout.addLayout(gear_layout)

        # Add container to root layout
        root.addWidget(container)

        # status bar
        self.status = QtWidgets.QStatusBar()
        self.status.setStyleSheet("color: #ddd; background: transparent;")
        self.setStatusBar(self.status)

        # connect signals
        self.btn_add.clicked.connect(self.on_add)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_copy_pass.clicked.connect(self.on_copy_pass)
        self.btn_copy_user.clicked.connect(self.on_copy_user)
        self.btn_stay.clicked.connect(self.on_toggle_stay)
        self.btn_lock.clicked.connect(self.on_lock)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_gear.clicked.connect(self.on_open_settings)
        self.table.itemSelectionChanged.connect(self.on_table_select)

        # double click to edit
        self.table.doubleClicked.connect(lambda _: self.on_edit())

    # ---------------- startup master flow ----------------
    def run_master_flow(self):
        try:
            if not master_exists():
                dlg = MasterDialog(create_mode=True, parent=self)
                if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                    QtWidgets.QApplication.quit(); return
                p1,p2 = dlg.get_passwords()
                if len(p1) < 8 or p1 != p2:
                    QtWidgets.QMessageBox.warning(self, "Error", "Passwords must match and be at least 8 characters.")
                    QtWidgets.QApplication.quit(); return
                create_master(p1)
                key = verify_master(p1)
                if not key:
                    QtWidgets.QMessageBox.critical(self, "Error", "Failed to create master.")
                    QtWidgets.QApplication.quit(); return
                self.key = key
                self.entries = []
                save_vault_with_key(self.entries, self.key)
            else:
                ok = False; attempts = 0
                while not ok and attempts < 3:
                    dlg = MasterDialog(create_mode=False, parent=self)
                    if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                        QtWidgets.QApplication.quit(); return
                    pwd = dlg.get_passwords()
                    key = verify_master(pwd)
                    if key:
                        self.key = key
                        try:
                            self.entries = load_vault_with_key(self.key)
                        except Exception:
                            QtWidgets.QMessageBox.critical(self, "Error", "Vault corrupted or wrong password.")
                            QtWidgets.QApplication.quit(); return
                        ok = True; break
                    attempts += 1
                if not ok:
                    QtWidgets.QMessageBox.critical(self, "Error", "Failed to unlock. Exiting.")
                    QtWidgets.QApplication.quit(); return
            self.populate_table()
        except Exception as e:
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, "Fatal", f"Startup error: {e}")
            QtWidgets.QApplication.quit()

    # ---------------- table/populate ----------------
    def populate_table(self):
        self.table.setRowCount(0)
        for ent in self.entries:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QtWidgets.QTableWidgetItem(ent.get("title","")))
            self.table.setItem(r,1, QtWidgets.QTableWidgetItem(ent.get("username","")))
            pwd_display = ent.get("password","")
            if not self._show_passwords:
                pwd_display = "*" * len(pwd_display)
            self.table.setItem(r,2, QtWidgets.QTableWidgetItem(pwd_display))

    def on_table_select(self):
        r = self.table.currentRow()
        if r < 0:
            self.in_website.clear(); self.in_user.clear(); self.in_pass.clear(); return
        ent = self.entries[r]
        self.in_website.setText(ent.get("title",""))
        self.in_user.setText(ent.get("username",""))
        self.in_pass.setText(ent.get("password",""))

    # ---------------- core actions ----------------
    def on_add(self):
        title = self.in_website.text().strip()
        user = self.in_user.text().strip()
        pwd = self.in_pass.text()
        if not (title and user and pwd):
            QtWidgets.QMessageBox.warning(self, "Missing", "Please fill Website, Username and Password.")
            return
        ent = {"title": title, "username": user, "password": pwd, "url":"", "notes":"", "ts": int(time.time())}
        self.entries.append(ent)
        self.populate_table()
        self._autosave()
        self.status.showMessage("Added & saved", 2000)
        # clear inputs
        self.in_website.clear(); self.in_user.clear(); self.in_pass.clear()

    def on_delete(self):
        r = self.table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.information(self, "Select", "Select a row to delete.")
            return
        res = QtWidgets.QMessageBox.question(self, "Delete", "Delete selected entry?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if res == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.entries[r]
            self.populate_table()
            self._autosave()
            self.status.showMessage("Deleted & saved", 2000)

    def on_edit(self):
        r = self.table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.information(self, "Select", "Select a row to edit.")
            return
        ent = self.entries[r]
        dlg = EntryDialog(entry=ent, parent=self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_ent = dlg.get_entry()
            self.entries[r] = new_ent
            self.populate_table()
            self._autosave()
            self.status.showMessage("Edited & saved", 2000)

    def _autosave(self):
        try:
            save_vault_with_key(self.entries, self.key)
        except Exception as e:
            print("Autosave failed:", e)

    def on_copy_pass(self):
        r = self.table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.information(self, "Select", "Select a row to copy password.")
            return
        pyperclip.copy(self.entries[r].get("password",""))
        self.status.showMessage("Password copied to clipboard", 3000)

    def on_copy_user(self):
        r = self.table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.information(self, "Select", "Select a row to copy username.")
            return
        pyperclip.copy(self.entries[r].get("username",""))
        self.status.showMessage("Username copied to clipboard", 3000)

    def on_toggle_stay(self):
        # Fixed stay on top functionality
        self._stay_on_top = not self._stay_on_top
        self.btn_stay.setChecked(self._stay_on_top)
        
        # Clear existing flags first
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        
        if self._stay_on_top:
            # Add stay on top flag
            self.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint
            )
        
        # Important: show the window again after changing flags
        self.show()
        self.activateWindow()
        self.raise_()

    def on_lock(self):
        # lock the vault and ask to re-unlock
        self.key = None
        self.entries = []
        self.populate_table()
        dlg = MasterDialog(create_mode=False, parent=self)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            QtWidgets.QApplication.quit(); return
        pwd = dlg.get_passwords(); key = verify_master(pwd)
        if key:
            self.key = key
            self.entries = load_vault_with_key(self.key)
            self.populate_table()
            self.status.showMessage("Unlocked",2000)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Wrong password.")
            QtWidgets.QApplication.quit()

    def on_toggle_eye(self, checked):
        self._show_passwords = checked
        
        # MODIFIED: Show/hide password in the input box
        if checked:
            self.in_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background: rgba(100, 100, 100, 200);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }
            """)
        else:
            self.in_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 60, 60, 180);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                }
            """)
        self.populate_table()

    def toggle_max(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    # ---------------- Settings dialog ----------------
    def on_open_settings(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.resize(500, 400)
        v = QtWidgets.QVBoxLayout(dlg)
        
        # Open vault location (moved from main UI)
        btn_loc = QtWidgets.QPushButton("Open Vault Location")
        btn_loc.clicked.connect(lambda: os.startfile(str(BASE_PATH)))
        v.addWidget(btn_loc)
        
        # Save vault manually (moved from main UI)
        btn_save_vault = QtWidgets.QPushButton("Save Vault")
        def manual_save():
            try:
                save_vault_with_key(self.entries, self.key)
                QtWidgets.QMessageBox.information(dlg, "Saved", "Vault saved successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(dlg, "Error", f"Save failed: {e}")
        btn_save_vault.clicked.connect(manual_save)
        v.addWidget(btn_save_vault)
        
        # Reset master password
        btn_reset = QtWidgets.QPushButton("Reset Master Password (delete vault)")
        def do_reset():
            res = QtWidgets.QMessageBox.question(dlg, "Reset", "This will backup and delete your vault and master metadata. Continue?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if res != QtWidgets.QMessageBox.StandardButton.Yes: return
            try:
                ts = time.strftime("%Y%m%d%H%M%S")
                if VAULT_FILE.exists(): shutil.copy2(VAULT_FILE, VAULT_FILE.with_suffix(".bak."+ts))
                if MASTER_META.exists(): shutil.copy2(MASTER_META, MASTER_META.with_suffix(".bak."+ts))
                if VAULT_FILE.exists(): VAULT_FILE.unlink()
                if MASTER_META.exists(): MASTER_META.unlink()
                QtWidgets.QMessageBox.information(dlg, "Reset", "Vault and master removed. App will exit.")
                QtWidgets.QApplication.quit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(dlg, "Error", f"Reset failed: {e}")
        btn_reset.clicked.connect(do_reset)
        v.addWidget(btn_reset)
        
        # Import / Export
        btn_export = QtWidgets.QPushButton("Export vault to .txt (plaintext)")
        def do_export():
            # request master password to confirm
            ask = MasterDialog(create_mode=False, parent=self)
            if ask.exec() != QtWidgets.QDialog.DialogCode.Accepted: return
            pwd = ask.get_passwords(); key = verify_master(pwd)
            if not key: QtWidgets.QMessageBox.warning(dlg, "Auth", "Wrong master password"); return
            fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to .txt", str(BASE_PATH/"passman_export.txt"), "Text Files (*.txt)")
            if not fpath: return
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    for e in self.entries:
                        line = f"{e.get('title','')}\t{e.get('username','')}\t{e.get('password','')}\n"
                        f.write(line)
                QtWidgets.QMessageBox.information(dlg, "Exported", f"Exported to {fpath} (plaintext).")
            except Exception as e:
                QtWidgets.QMessageBox.critical(dlg, "Error", f"Export failed: {e}")
        btn_export.clicked.connect(do_export)
        v.addWidget(btn_export)

        btn_import = QtWidgets.QPushButton("Import from .txt (tab-separated title<tab>user<tab>pass)")
        def do_import():
            ask = MasterDialog(create_mode=False, parent=self)
            if ask.exec() != QtWidgets.QDialog.DialogCode.Accepted: return
            pwd = ask.get_passwords(); key = verify_master(pwd)
            if not key: QtWidgets.QMessageBox.warning(dlg, "Auth", "Wrong master password"); return
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select import .txt", str(BASE_PATH), "Text Files (*.txt)")
            if not path: return
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = [ln.strip() for ln in f if ln.strip()]
                for ln in lines:
                    parts = ln.split("\t")
                    if len(parts) < 3: continue
                    ent = {"title": parts[0], "username": parts[1], "password": parts[2], "url":"", "notes":"", "ts":int(time.time())}
                    self.entries.append(ent)
                self.populate_table()
                self._autosave()
                QtWidgets.QMessageBox.information(dlg, "Imported", "Imported entries and saved.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(dlg, "Error", f"Import failed: {e}")
        btn_import.clicked.connect(do_import)
        v.addWidget(btn_import)

        # Hotkeys customization (app-only)
        v.addWidget(QtWidgets.QLabel("Hotkeys (app-only)"))
        grid = QtWidgets.QGridLayout()
        row = 0
        self.hk_fields = {}
        for action in ["add","delete","copy_pass","copy_user","lock"]:
            grid.addWidget(QtWidgets.QLabel(action.replace("_"," ").title()), row, 0)
            seq = cfg.get("hotkeys", {}).get(action, DEFAULT_CONFIG["hotkeys"].get(action,""))
            le = QtWidgets.QLineEdit(seq)
            grid.addWidget(le, row, 1)
            self.hk_fields[action] = le
            row += 1
        v.addLayout(grid)

        btn_save_settings = QtWidgets.QPushButton("Save Settings")
        def save_settings_and_close():
            # write hotkeys
            if "hotkeys" not in cfg: cfg["hotkeys"] = {}
            for k,le in self.hk_fields.items():
                cfg["hotkeys"][k] = le.text().strip()
            save_config(cfg)
            self.apply_shortcuts_from_config()
            QtWidgets.QMessageBox.information(dlg, "Saved", "Settings saved.")
            dlg.accept()
        btn_save_settings.clicked.connect(save_settings_and_close)
        v.addWidget(btn_save_settings)

        dlg.exec()

    # ---------------- shortcuts ----------------
    def apply_shortcuts_from_config(self):
        # remove old shortcuts
        try:
            for sc in getattr(self, "_qshorts", []):
                sc.setParent(None)
            self._qshorts = []
        except Exception:
            self._qshorts = []
        hk = cfg.get("hotkeys", DEFAULT_CONFIG["hotkeys"])
        mapping = {
            "add": (self.on_add, hk.get("add","Ctrl+N")),
            "delete": (self.on_delete, hk.get("delete","Del")),
            "copy_pass": (self.on_copy_pass, hk.get("copy_pass","Ctrl+Shift+C")),
            "copy_user": (self.on_copy_user, hk.get("copy_user","Ctrl+Shift+U")),
            "lock": (self.on_lock, hk.get("lock","Ctrl+L"))
        }
        for name,(fn,seq) in mapping.items():
            try:
                if seq:
                    sc = QtGui.QShortcut(QtGui.QKeySequence(seq), self)
                    sc.activated.connect(fn)
                    self._qshorts.append(sc)
            except Exception:
                pass

    # ---------------- Window event handling ----------------
    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()
            ev.accept()

    def mouseMoveEvent(self, ev):
        if self._drag_pos is not None and ev.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._drag_pos)
            ev.accept()

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None
        ev.accept()

    def focusOutEvent(self, event):
        # Prevent the window from losing focus when clicking on transparent areas
        # if stay on top is enabled
        if self._stay_on_top:
            QtCore.QTimer.singleShot(10, self.activateWindow)
        super().focusOutEvent(event)

# ---------------- main ----------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APPNAME)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()