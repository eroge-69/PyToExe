"""
Coffre‑fort Médias — Edition PRO (GUI)
--------------------------------------

Nouvelles demandes intégrées :
• Menu **PDF caché** (au lieu de « Outils ») avec :
  - **Créer un PDF avec fichier caché…** (attache un fichier dans un PDF)
  - **Extraire les fichiers d’un PDF…** (récupère les pièces jointes d’un PDF)
• Déverrouillage sécurisé : **Fichier clé uniquement** (glisser‑déposer). 
  Validation stricte du fichier requis.
• Déchiffrement recrée le **dossier racine**.
• Chiffrement **supprime automatiquement** le dossier source (effacement sécurisé activé par défaut).
• Destination par défaut : `NomDuDossier.encrypt` **à côté du dossier source** (case pour personnaliser).

Dépendances :
    pip install pyqt6 cryptography PyPDF2

Build exécutable (optionnel) :
    pip install pyinstaller
    pyinstaller -F -n CoffreFortPro app_encrypt.py
"""
from __future__ import annotations
import os
import sys
import tarfile
import tempfile
import secrets
import shutil
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from PyPDF2 import PdfWriter, PdfReader

# PyQt6
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QProgressBar, QMessageBox, QTextEdit, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QMenuBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction

# ---- Format & constantes ----
MAGIC = b"LCENCR01"      # 8 bytes : signature d'application
VERSION = (1, 2)          # 1.2 : support PIN + keyfile
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
CHUNK_SIZE = 1024 * 1024  # 1 MiB
DEFAULT_EXT = ".encrypt"

@dataclass
class JobConfig:
    src_path: Path
    dst_path: Path
    keyfile_hash_hex: str
    secure_wipe: bool = True
    mode: str = "encrypt"  # or "decrypt"

# ---- Utilitaires crypto ----

# ---- Utilitaires crypto ----

def _validate_keyfile_content(keyfile_path: str) -> bool:
    """Vérifie que le fichier clé a le bon nom et contenu sans exposer les valeurs attendues."""
    # Hash du nom de fichier attendu
    expected_filename_hash = "91d894495aa09bfea19ae5a8a095b81b4d8fa33bfaa7de306306474a9c1afc2d"
    # Hash du contenu attendu  
    expected_content_hash = "e5f9705491bc81851e3be57222c9287d979193739d05829c4f3bc4c34116606b"
    
    try:
        # Vérifier le nom du fichier
        filename = Path(keyfile_path).name
        filename_hash = hashlib.sha256(filename.encode("utf-8")).hexdigest()
        if filename_hash != expected_filename_hash:
            return False
        
        # Vérifier le contenu du fichier
        with open(keyfile_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return content_hash == expected_content_hash
    except Exception:
        return False

def _derive_key(keyfile_hash_hex: str, salt: bytes) -> bytes:
    # Utilise uniquement le hash du fichier‑clé comme matériel de base
    material = keyfile_hash_hex.encode("utf-8")
    kdf = Scrypt(salt=salt, length=KEY_LEN, n=2**15, r=8, p=1)
    return kdf.derive(material)

# ---- Archivage ----

def make_tar_gz_of_folder(folder: Path, out_path: Path, progress_cb=None):
    """Crée un tar.gz contenant un dossier racine = folder.name."""
    total_files = sum(1 for p in folder.rglob("*") if p.is_file()) or 1
    done = 0
    root = folder.name
    with tarfile.open(out_path, mode="w:gz") as tar:
        for item in folder.rglob("*"):
            if item.is_file():
                arcname = Path(root) / item.relative_to(folder)
                tar.add(item, arcname=str(arcname))
                done += 1
                if progress_cb:
                    progress_cb(min(95, int(done / total_files * 45)))


def extract_tar_gz_to_folder(tar_gz_path: Path, out_dir: Path):
    with tarfile.open(tar_gz_path, mode="r:gz") as tar:
        tar.extractall(path=out_dir)

# ---- Chiffrement flux ----

def encrypt_stream(plaintext_path: Path, vault_path: Path, keyfile_hash_hex: str, progress_cb=None):
    salt = secrets.token_bytes(SALT_LEN)
    key = _derive_key(keyfile_hash_hex, salt)
    nonce = secrets.token_bytes(NONCE_LEN)

    backend = default_backend()
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=backend).encryptor()

    total = plaintext_path.stat().st_size or 1
    processed = 0

    with open(plaintext_path, "rb") as f_in, open(vault_path, "wb") as f_out:
        # En‑tête : MAGIC(8) + ver(2x1) + SALT + NONCE
        f_out.write(MAGIC)
        f_out.write(bytes([VERSION[0], VERSION[1]]))
        f_out.write(salt)
        f_out.write(nonce)

        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            data = encryptor.update(chunk)
            if data:
                f_out.write(data)
            processed += len(chunk)
            if progress_cb:
                progress = 45 + int(processed / total * 50)
                progress_cb(min(95, progress))

        f_out.write(encryptor.finalize())
        f_out.write(encryptor.tag)

    if progress_cb:
        progress_cb(100)


def decrypt_stream(vault_path: Path, out_plain_path: Path, keyfile_hash_hex: str, progress_cb=None):
    with open(vault_path, "rb") as f_in:
        magic = f_in.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Fichier incompatible : non créé par cette application.")
        ver_major = int.from_bytes(f_in.read(1), "big")
        ver_minor = int.from_bytes(f_in.read(1), "big")
        if (ver_major, ver_minor) != VERSION:
            raise ValueError(f"Version de format non prise en charge : {ver_major}.{ver_minor}")
        salt = f_in.read(SALT_LEN)
        nonce = f_in.read(NONCE_LEN)
        rest = f_in.read()

    if len(rest) < 16:
        raise ValueError("Fichier corrompu (tag manquant).")

    tag = rest[-16:]
    ciphertext = rest[:-16]

    key = _derive_key(keyfile_hash_hex, salt)
    backend = default_backend()
    decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=backend).decryptor()

    total = len(ciphertext) or 1
    processed = 0

    with open(out_plain_path, "wb") as f_out:
        for i in range(0, len(ciphertext), CHUNK_SIZE):
            chunk = ciphertext[i:i+CHUNK_SIZE]
            plain = decryptor.update(chunk)
            if plain:
                f_out.write(plain)
            processed += len(chunk)
            if progress_cb:
                progress_cb(int(processed / total * 95))
        decryptor.finalize()

    if progress_cb:
        progress_cb(100)

# ---- Effacement sécurisé ----

def secure_delete(path: Path, passes: int = 3):
    try:
        if path.is_file():
            size = path.stat().st_size
            with open(path, "r+b") as f:
                for _ in range(passes):
                    f.seek(0); f.write(os.urandom(size)); f.flush(); os.fsync(f.fileno())
            path.unlink(missing_ok=True)
        elif path.is_dir():
            for sub in sorted(path.rglob("*"), reverse=True):
                if sub.is_file():
                    secure_delete(sub, passes)
                else:
                    try: sub.rmdir()
                    except Exception: pass
            path.rmdir()
    except Exception:
        try:
            if path.is_file():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass

# ---- Thread de travail ----
class Worker(QThread):
    progress = pyqtSignal(int)
    done = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, cfg: JobConfig):
        super().__init__()
        self.cfg = cfg

    def run(self):
        try:
            if self.cfg.mode == "encrypt":
                folder = self.cfg.src_path
                if not folder.exists() or not folder.is_dir():
                    raise ValueError("Dossier source invalide.")
                with tempfile.TemporaryDirectory() as td:
                    tar_gz = Path(td) / "payload.tar.gz"
                    make_tar_gz_of_folder(folder, tar_gz, self.progress.emit)
                    encrypt_stream(tar_gz, self.cfg.dst_path, self.cfg.keyfile_hash_hex, self.progress.emit)
                if self.cfg.secure_wipe:
                    secure_delete(folder)
                self.done.emit("Chiffrement terminé. Dossier source supprimé.")
            elif self.cfg.mode == "decrypt":
                vault = self.cfg.src_path
                if not vault.exists() or not vault.is_file():
                    raise ValueError("Fichier chiffré invalide.")
                with tempfile.TemporaryDirectory() as td:
                    tar_gz = Path(td) / "payload.tar.gz"
                    decrypt_stream(vault, tar_gz, self.cfg.keyfile_hash_hex, self.progress.emit)
                    extract_tar_gz_to_folder(tar_gz, self.cfg.dst_path)
                self.done.emit("Déchiffrement terminé. Dossier recréé.")
            else:
                raise ValueError("Mode inconnu.")
        except Exception as e:
            self.failed.emit(str(e))

# ---- Zone de dépôt pour fichier‑clé ----
class DropLabel(QLabel):
    def __init__(self, placeholder: str = " "):
        super().__init__(placeholder)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed #999; border-radius: 8px; padding: 16px; color: #666;")
        self.setAcceptDrops(True)
        self.file_path: Optional[str] = None
        self.mousePressEvent = self._open_dialog

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            self.file_path = urls[0].toLocalFile()
            self.setText(self.file_path)

    def _open_dialog(self, _):
        path, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier clé", filter="Tous fichiers (*)")
        if path:
            self.file_path = path
            self.setText(self.file_path)

# ---- Boîte de dialogue fichier‑clé uniquement ----
class UnlockDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Déverrouillage")
        self.setModal(True)
        self.drop = DropLabel(" ")

        form = QFormLayout(); form.addRow("", self.drop)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout = QVBoxLayout(); layout.addLayout(form); layout.addWidget(btns)
        self.setLayout(layout)

    def get_keyfile_hash(self) -> Optional[str]:
        if self.exec() == QDialog.DialogCode.Accepted:
            keyfile = self.drop.file_path
            if not keyfile or not Path(keyfile).exists():
                QMessageBox.warning(self, "Fichier clé manquant", "Veuillez sélectionner un fichier clé.")
                return self.get_keyfile_hash()
            
            # Vérifier le fichier
            if not _validate_keyfile_content(keyfile):
                QMessageBox.warning(self, "Fichier incorrect", "Le fichier clé fourni n'est pas valide.")
                return self.get_keyfile_hash()
            
            # Calculer hash du contenu pour la dérivation de clé
            try:
                with open(keyfile, "rb") as f:
                    key_hash_hex = hashlib.sha256(f.read()).hexdigest()
            except Exception as e:
                QMessageBox.critical(self, "Erreur fichier clé", str(e))
                return None
            return key_hash_hex
        return None

# ---- Interface principale ----
class App(QWidget):
    def __init__(self, key_hash_hex: str):
        super().__init__()
        self.key_hash_hex = key_hash_hex
        self.setWindowTitle("Coffre‑fort Médias — PRO")
        self.resize(860, 620)
        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QGroupBox { font-weight: bold; border: 1px solid #ddd; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton { padding: 8px 14px; border-radius: 8px; }
            QTextEdit { background: #fafafa; }
        """)

        # --- Menu ---
        self.menubar = QMenuBar()
        self.menu_pdf = self.menubar.addMenu("PDF caché")
        self.act_make_pdf = QAction("Créer un PDF avec fichier caché…", self)
        self.act_extract_pdf = QAction("Extraire les fichiers d’un PDF…", self)
        self.menu_pdf.addAction(self.act_make_pdf)
        self.menu_pdf.addAction(self.act_extract_pdf)
        self.act_make_pdf.triggered.connect(self.action_make_pdf)
        self.act_extract_pdf.triggered.connect(self.action_extract_pdf)

        # Widgets
        self.src_edit = QLineEdit(); self.src_edit.setPlaceholderText("Dossier à chiffrer…")
        self.btn_browse_src = QPushButton("Parcourir…")

        self.chk_custom_dst = QCheckBox("Destination personnalisée")
        self.dst_edit = QLineEdit(); self.dst_edit.setPlaceholderText("Fichier de sortie (*.encrypt)…")
        self.btn_browse_dst = QPushButton("Parcourir…")
        self.dst_edit.setEnabled(False); self.btn_browse_dst.setEnabled(False)

        self.chk_wipe = QCheckBox("Supprimer automatiquement le dossier source après chiffrement (effacement sécurisé)")
        self.chk_wipe.setChecked(True)

        self.btn_encrypt = QPushButton("Chiffrer le dossier → .encrypt")
        self.btn_decrypt = QPushButton("Déchiffrer un fichier .encrypt → dossier…")

        self.progress = QProgressBar()
        self.log = QTextEdit(); self.log.setReadOnly(True)

        # Groupes
        grp_enc = QGroupBox("Chiffrement")
        f1 = QFormLayout()
        row1 = QHBoxLayout(); row1.addWidget(self.src_edit); row1.addWidget(self.btn_browse_src)
        row2 = QHBoxLayout(); row2.addWidget(self.dst_edit); row2.addWidget(self.btn_browse_dst)
        f1.addRow("Source", row1)
        f1.addRow(self.chk_custom_dst)
        f1.addRow("Destination", row2)
        f1.addRow(self.chk_wipe)
        f1.addRow(self.btn_encrypt)
        grp_enc.setLayout(f1)

        grp_dec = QGroupBox("Déchiffrement")
        v2 = QVBoxLayout(); v2.addWidget(self.btn_decrypt)
        grp_dec.setLayout(v2)

        grp_log = QGroupBox("Journal & progression")
        v3 = QVBoxLayout(); v3.addWidget(self.progress); v3.addWidget(self.log)
        grp_log.setLayout(v3)

        root = QVBoxLayout(); root.setMenuBar(self.menubar)
        root.addWidget(grp_enc); root.addWidget(grp_dec); root.addWidget(grp_log)
        self.setLayout(root)

        # Signaux
        self.btn_browse_src.clicked.connect(self.browse_src)
        self.btn_browse_dst.clicked.connect(self.browse_dst)
        self.chk_custom_dst.stateChanged.connect(self.toggle_custom_dst)
        self.btn_encrypt.clicked.connect(self.do_encrypt)
        self.btn_decrypt.clicked.connect(self.do_decrypt)

        self.worker: Optional[Worker] = None

    # ---- Helpers UI ----
    def log_msg(self, msg: str):
        self.log.append(msg)

    def browse_src(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier à chiffrer")
        if folder:
            self.src_edit.setText(folder)
            src = Path(folder)
            default_dst = src.parent / (src.name + DEFAULT_EXT)
            if not self.chk_custom_dst.isChecked():
                self.dst_edit.setText(str(default_dst))

    def toggle_custom_dst(self):
        custom = self.chk_custom_dst.isChecked()
        self.dst_edit.setEnabled(custom)
        self.btn_browse_dst.setEnabled(custom)
        if not custom and self.src_edit.text().strip():
            src = Path(self.src_edit.text().strip())
            self.dst_edit.setText(str(src.parent / (src.name + DEFAULT_EXT)))

    def browse_dst(self):
        path, _ = QFileDialog.getSaveFileName(self, "Choisir le fichier de sortie", filter="Fichier chifré (*.encrypt)")
        if path:
            if not path.endswith(DEFAULT_EXT):
                path += DEFAULT_EXT
            self.dst_edit.setText(path)

    def ensure_ready_encrypt(self) -> Optional[JobConfig]:
        src = Path(self.src_edit.text())
        if not src.exists() or not src.is_dir():
            QMessageBox.warning(self, "Source invalide", "Sélectionnez un dossier source valide.")
            return None
        if self.chk_custom_dst.isChecked():
            dst_txt = self.dst_edit.text().strip()
            if not dst_txt:
                QMessageBox.warning(self, "Destination manquante", "Choisissez un fichier de sortie .encrypt.")
                return None
            dst = Path(dst_txt)
        else:
            dst = src.parent / (src.name + DEFAULT_EXT)
            self.dst_edit.setText(str(dst))
        return JobConfig(src, dst, self.key_hash_hex, self.chk_wipe.isChecked(), "encrypt")

    def do_encrypt(self):
        cfg = self.ensure_ready_encrypt()
        if not cfg:
            return
        self.progress.setValue(0); self.log.clear()
        self.log_msg(f"Chiffrement de {cfg.src_path} → {cfg.dst_path}")
        self.toggle_ui(False)
        self.worker = Worker(cfg)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def do_decrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier chiffré", filter="Fichier chiffré (*.encrypt)")
        if not file_path:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie (le dossier racine sera recréé)")
        if not out_dir:
            return
        cfg = JobConfig(Path(file_path), Path(out_dir), self.key_hash_hex, False, "decrypt")
        self.progress.setValue(0); self.log.clear()
        self.log_msg(f"Déchiffrement de {cfg.src_path} → {cfg.dst_path}")
        self.toggle_ui(False)
        self.worker = Worker(cfg)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_done(self, msg: str):
        self.toggle_ui(True); self.progress.setValue(100)
        QMessageBox.information(self, "Succès", msg)
        self.log_msg(msg)

    def on_failed(self, err: str):
        self.toggle_ui(True)
        QMessageBox.critical(self, "Erreur", err)
        self.log_msg(f"Erreur : {err}")

    def toggle_ui(self, enabled: bool):
        for w in [self.src_edit, self.btn_browse_src, self.dst_edit, self.btn_browse_dst,
                  self.chk_wipe, self.btn_encrypt, self.btn_decrypt, self.chk_custom_dst]:
            w.setEnabled(enabled)

    # ---- PDF caché ----
    def action_make_pdf(self):
        file_to_hide, _ = QFileDialog.getOpenFileName(self, "Choisir le fichier à cacher dans un PDF", filter="Tous fichiers (*)")
        if not file_to_hide:
            return
        out_pdf, _ = QFileDialog.getSaveFileName(self, "Enregistrer le PDF", filter="Fichier PDF (*.pdf)")
        if not out_pdf:
            return
        if not out_pdf.lower().endswith(".pdf"):
            out_pdf += ".pdf"
        try:
            writer = PdfWriter(); writer.add_blank_page(width=595, height=842)
            with open(file_to_hide, "rb") as f: payload = f.read()
            writer.add_attachment(os.path.basename(file_to_hide), payload)
            with open(out_pdf, "wb") as f_out: writer.write(f_out)
            QMessageBox.information(self, "PDF créé", f"PDF généré avec fichier caché : {out_pdf}")
            self.log_msg(f"PDF créé avec pièce jointe cachée: {out_pdf}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", str(e))
            self.log_msg(f"Erreur PDF : {e}")

    def action_extract_pdf(self):
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un PDF", filter="Fichier PDF (*.pdf)")
        if not pdf_path:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie pour les fichiers extraits")
        if not out_dir:
            return
        try:
            reader = PdfReader(pdf_path)
            extracted = 0
            
            # Méthode alternative plus robuste pour extraire les pièces jointes
            if hasattr(reader, 'attachments') and reader.attachments:
                # Nouvelle API PyPDF2
                for name, data in reader.attachments.items():
                    out_path = Path(out_dir) / name
                    with open(out_path, "wb") as f:
                        f.write(data)
                    extracted += 1
            else:
                # Méthode manuelle pour les versions plus anciennes
                catalog = reader.trailer["/Root"]
                if hasattr(catalog, 'get_object'):
                    catalog = catalog.get_object()
                
                if "/Names" in catalog:
                    names = catalog["/Names"]
                    if hasattr(names, 'get_object'):
                        names = names.get_object()
                    
                    if "/EmbeddedFiles" in names:
                        embedded = names["/EmbeddedFiles"]
                        if hasattr(embedded, 'get_object'):
                            embedded = embedded.get_object()
                        
                        if "/Names" in embedded:
                            arr = embedded["/Names"]
                            if hasattr(arr, 'get_object'):
                                arr = arr.get_object()
                            
                            # arr = [name1, dict1, name2, dict2, ...]
                            for i in range(0, len(arr), 2):
                                name = arr[i]
                                file_spec = arr[i+1]
                                if hasattr(file_spec, 'get_object'):
                                    file_spec = file_spec.get_object()
                                
                                if "/EF" in file_spec:
                                    ef = file_spec["/EF"]
                                    if hasattr(ef, 'get_object'):
                                        ef = ef.get_object()
                                    
                                    fstream = ef.get("/F") or ef.get("/UF")
                                    if fstream and hasattr(fstream, 'get_object'):
                                        fstream = fstream.get_object()
                                    
                                    if fstream and hasattr(fstream, 'get_data'):
                                        data = fstream.get_data()
                                        out_path = Path(out_dir) / str(name)
                                        with open(out_path, "wb") as f:
                                            f.write(data)
                                        extracted += 1
            
            if extracted == 0:
                QMessageBox.information(self, "Aucune pièce jointe", "Ce PDF ne contient pas de fichier caché.")
            else:
                QMessageBox.information(self, "Extraction terminée", f"{extracted} fichier(s) extrait(s) dans : {out_dir}")
                self.log_msg(f"Extraction PDF: {extracted} fichier(s) → {out_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur extraction PDF", str(e))
            self.log_msg(f"Erreur extraction PDF : {e}")

# ---- Entrée principale ----
def main():
    app = QApplication(sys.argv)
    # Demander fichier‑clé uniquement
    dlg = UnlockDialog()
    key_hash_hex = dlg.get_keyfile_hash()
    if not key_hash_hex:
        sys.exit(0)
    w = App(key_hash_hex)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
