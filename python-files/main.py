#!/usr/bin/env python3
"""
letters_app_fixed.py — single-file Letters app (fixed renderer)
Features:
- Choose storage folder (startup + Settings)
- Save letters as HTML (preserve bold/italic/underline)
- Paper view paints ruled-paper and places a QTextBrowser on top for reliable HTML rendering
- Default filename: Sender_YYYY-MM-DD_HH-MM-SS.let
- AES-256 encryption optional
- Image mode supported
- Zoom support for both text and image modes with toolbar, mouse wheel, and keyboard shortcuts
Requirements: PySide6, cryptography, Pillow
"""
import sys, os, io, struct, json, traceback
from pathlib import Path
import datetime, platform, subprocess
from PIL import Image

# PySide6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget, QListWidgetItem, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox, QComboBox, QScrollArea, QGroupBox,
    QSizePolicy, QTextBrowser, QToolBar
)
from PySide6.QtGui import (
    QFontDatabase, QFont, QImage, QPixmap, QTextCursor, QTextCharFormat,
    QPainter, QColor, QPen, QBrush, QAction, QIcon
)
from PySide6.QtCore import Qt, QSize, QRect, QTimer

# Crypto
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# -------------------------
# Config / constants
# -------------------------
APP_NAME = "Letters"
DEFAULT_DIR = Path.home() / ".letters_do_not_delete"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = DEFAULT_DIR / "config.json"
icon_path = Path(__file__).parent / "icon.png"
LAST_FILES_FILE = DEFAULT_DIR / ".last_letter_snapshot.json"



if getattr(sys, 'frozen', False):
    # running from .exe
    FONT_FILE = Path(sys._MEIPASS) / "handwriting.ttf"
else:
    FONT_FILE = Path(__file__).parent / "handwriting.ttf"

CHAR_LIMIT = 2000
MAGIC = b"LET1"

def now_iso():
    return datetime.datetime.now().astimezone().isoformat()

def load_config():
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

# -------------------------
# Crypto helpers
# -------------------------
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000, backend=default_backend())
    return kdf.derive(password.encode("utf-8"))

def aes_encrypt(plaintext: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    p = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    ct = cipher.encryptor().update(p) + cipher.encryptor().finalize()
    return salt + iv + struct.pack(">I", len(ct)) + ct

def aes_decrypt(payload: bytes, password: str) -> bytes:
    if len(payload) < 36:
        raise ValueError("Invalid encrypted payload")
    salt = payload[:16]; iv = payload[16:32]
    clen = struct.unpack(">I", payload[32:36])[0]
    ct = payload[36:36+clen]
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padded = cipher.decryptor().update(ct) + cipher.decryptor().finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

# -------------------------
# .let file helpers
# -------------------------
def save_letter(path: Path, metadata: dict, content: bytes, password: str | None):
    meta_json = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
    with open(path, "wb") as f:
        f.write(MAGIC)
        flags = 0
        if password:
            flags |= 1
            f.write(bytes([flags]))
            plaintext = struct.pack(">I", len(meta_json)) + meta_json + content
            enc = aes_encrypt(plaintext, password)
            f.write(struct.pack(">I", len(enc)))
            f.write(enc)
        else:
            f.write(bytes([flags]))
            f.write(struct.pack(">I", len(meta_json)))
            f.write(meta_json)
            f.write(content)

def load_letter_header(path: Path):
    data = path.read_bytes()
    if data[:4] != MAGIC:
        raise ValueError("Not a .let file")
    p = 4
    flags = data[p]; p += 1
    encrypted = bool(flags & 1)
    if encrypted:
        enc_len = struct.unpack(">I", data[p:p+4])[0]; p += 4
        enc = data[p:p+enc_len]
        return True, enc
    else:
        meta_len = struct.unpack(">I", data[p:p+4])[0]; p += 4
        meta_json = data[p:p+meta_len]; p += meta_len
        content = data[p:]
        meta = json.loads(meta_json.decode("utf-8"))
        return False, (meta, content)

def decrypt_encrypted_payload(enc_payload: bytes, password: str):
    plaintext = aes_decrypt(enc_payload, password)
    meta_len = struct.unpack(">I", plaintext[:4])[0]
    meta_json = plaintext[4:4+meta_len]
    content = plaintext[4+meta_len:]
    meta = json.loads(meta_json.decode("utf-8"))
    return meta, content

# -------------------------
# small dialogs
# -------------------------
class PasswordDialog(QDialog):
    def __init__(self, prompt="Enter password", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(prompt))
        self.pw = QLineEdit(); self.pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    def password(self):
        return self.pw.text()

# -------------------------
# PaperRenderer: paints paper and places QTextBrowser/QLabel over it
# -------------------------
class PaperRenderer(QWidget):
    def __init__(self, handwriting_font: QFont | None = None, parent=None):
        super().__init__(parent)
        self.hand_font = handwriting_font or QFont("Segoe Script", 14)
        self.ruling_spacing = 28
        self.left_margin = 100
        self.top_margin = 50
        self.bottom_margin = 40

        # content widgets (children)
        self.text_widget = QTextBrowser(self)
        self.text_widget.setReadOnly(True)
        self.text_widget.setStyleSheet("background: transparent; border: none;")

        self.image_scroll = QScrollArea(self)
        self.image_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.image_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.image_scroll.setWidgetResizable(True)

        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_scroll.setWidget(self.image_label)
        self.image_scroll.hide()

        self.html_text = ""
        self.ps = ""
        self.mode = "text"  # or 'image'
        self.setMinimumSize(600, 800)

        # Added: Zoom state for text and image modes
        self.text_zoom = 1.0  # Default zoom level (1.0 = 100%)
        self.image_zoom = 1.0  # Independent zoom for image mode
        self.original_pixmap = None  # Store original image for scaling
        self.original_font_size = self.hand_font.pointSize()  # Base font size

        # Ensure widget can receive keyboard focus for shortcuts
        self.setFocusPolicy(Qt.StrongFocus)

    def set_html(self, html: str, ps: str = "", reset_zoom=True):
        self.mode = "text"
        self.html_text = html or ""
        self.ps = ps or ""
        if reset_zoom:
            self.text_zoom = 1.0
        css = (
            f"p {{ margin:0; line-height: {self.ruling_spacing * self.text_zoom}px; color:black; }}"
            f"body {{ margin:0; font-family: '{self.hand_font.family()}'; "
            f"font-size: {self.original_font_size * self.text_zoom}pt; color: black; }}"
        )
        content_html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{self.html_text}"
        if self.ps:
            content_html += "<p>&nbsp;</p>" * 3  # three blank lines
            content_html += f"<p><b>P.S.</b> {self.ps}</p>"
        content_html += "</body></html>"
        self.text_widget.setHtml(content_html)
        self.text_widget.show()
        self.image_scroll.hide()

        self.update()


    def set_plain(self, text: str, ps: str = ""):
        self.set_html(f"<pre style='font-family: {self.hand_font.family()};'>{text}</pre>", ps)
    
    def set_image_bytes(self, img_bytes: bytes):
        self.mode = "image"
        self.html_text = ""
        self.ps = ""
        img = QImage.fromData(img_bytes)
        if img.isNull():
            self.image_label.hide()
        else:
            self.original_pixmap = QPixmap()
            self.original_pixmap.loadFromData(img_bytes)
            self._fit_image_to_viewport(self.width(), self.height(), initial=True)
            self.image_label.show()
        self.image_scroll.show()
        self.text_widget.hide()

        self.update()

    def _fit_image_to_viewport(self, available_width, available_height, initial=False):
        if not self.original_pixmap:
            return
        pix_width = self.original_pixmap.width()
        pix_height = self.original_pixmap.height()
        scale_x = (available_width - 40) / pix_width
        scale_y = (available_height - 40) / pix_height
        fit_scale = min(scale_x, scale_y, 1.0)

        if initial:
            # Start at 70% of fit size
            self.base_scale = fit_scale * 0.7
        else:
            # Keep existing base scale for later recalculations
            self.base_scale = getattr(self, "base_scale", fit_scale)

        self.image_zoom = 1.0  # logical zoom factor (1.0 = base scale)
        self._update_image()

    # Added: Update image with current zoom level
    def _update_image(self):
        if not self.original_pixmap:
            return

        # Scale image according to base scale and current zoom
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_pixmap.width() * self.base_scale * self.image_zoom,
            self.original_pixmap.height() * self.base_scale * self.image_zoom,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

        # Center the QLabel in PaperRenderer
        x = max(0, (self.width() - scaled_pixmap.width()) // 2)
        y = max(0, (self.height() - scaled_pixmap.height()) // 2)
        self.image_label.resize(scaled_pixmap.size())
        self.image_label.setPixmap(scaled_pixmap)

    # Added: Zoom methods
    def zoom_in(self):
        if self.mode == "text" and self.text_zoom < 3.0:
            self.text_zoom = min(self.text_zoom + 0.1, 3.0)
            self.set_html(self.html_text, self.ps, reset_zoom=False)
        elif self.mode == "image" and self.image_zoom < 3.0:
            self.image_zoom = min(self.image_zoom + 0.1, 3.0)
            self._update_image()

    def zoom_out(self):
        if self.mode == "text" and self.text_zoom > 0.1:
            self.text_zoom = max(self.text_zoom - 0.1, 0.1)
            self.set_html(self.html_text, self.ps, reset_zoom=False)
        elif self.mode == "image" and self.image_zoom > 0.1:
            self.image_zoom = max(self.image_zoom - 0.1, 0.1)
            self._update_image()

    def reset_zoom(self):
        if self.mode == "text":
            self.text_zoom = 1.0
            self.set_html(self.html_text, self.ps, reset_zoom=False)
        elif self.mode == "image":
            self.image_zoom = 1.0
            self._update_image()

    # Added: Fit content to window size
    def fit_to_window(self, available_width, available_height):
        if self.mode == "text":
            # Adjust text zoom to fit content (approximate)
            doc = self.text_widget.document()
            doc.setTextWidth(available_width - self.left_margin - 40)
            content_height = doc.size().height()
            if content_height > available_height:
                scale = (available_height - self.top_margin - self.bottom_margin) / content_height
                self.text_zoom = max(0.5, min(scale, 1.0))
                self.set_html(self.html_text, self.ps)
        else:
            if self.original_pixmap:
                pix_width = self.original_pixmap.width()
                pix_height = self.original_pixmap.height()
                scale_x = (available_width - 40) / pix_width
                scale_y = (available_height - 40) / pix_height
                self.image_zoom = max(0.5, min(scale_x, scale_y, 1.0))
                self._update_image()

    def resizeEvent(self, ev):
        if self.mode == "text":
            rect = self.rect().adjusted(20, 20, -20, -20)
            inner_left = rect.left() + self.left_margin
            inner_top = rect.top() + self.top_margin
            inner_width = rect.width() - (inner_left - rect.left()) - 40
            inner_height = rect.height() - (inner_top - rect.top()) - self.bottom_margin
            self.text_widget.setGeometry(inner_left, inner_top, inner_width, inner_height)
            # Scrollbars handled by parent QScrollArea
        elif self.mode == "image" and self.original_pixmap:
            if not hasattr(self, "base_scale"):
                self._fit_image_to_viewport(self.width(), self.height(), initial=True)
            self.image_scroll.setGeometry(self.rect().adjusted(20, 20, -20, -20))
            self._update_image()

    
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        rect = self.rect().adjusted(20,20,-20,-20)
        # background card
        painter.setBrush(QBrush(QColor(250,250,247)))
        painter.setPen(QPen(QColor(220,220,220)))
        painter.drawRoundedRect(rect, 12, 12)
        # draw ruled lines
        painter.setPen(QPen(QColor(220,230,255)))
        y = rect.top() + self.top_margin
        while y < rect.bottom() - self.bottom_margin:
            painter.drawLine(rect.left() + 40, int(y), rect.right() - 40, int(y))
            y += self.ruling_spacing
        # left margin line
        painter.setPen(QPen(QColor(255,200,200)))
        painter.drawLine(rect.left() + self.left_margin - 10, rect.top() + 10, rect.left() + self.left_margin - 10, rect.bottom() - 10)
        painter.end()

# -------------------------
# Create window
# -------------------------
class CreateLetterWindow(QMainWindow):
    def __init__(self, handwriting_font=None, storage_folder: Path | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Letter")
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(900,700)
        self.hand_font = handwriting_font
        self.storage_folder = Path(storage_folder) if storage_folder else DEFAULT_DIR
        self.img_path = None
        self._build_ui()

    def _build_ui(self):
        c = QWidget(); self.setCentralWidget(c)
        v = QVBoxLayout(c)
        top = QHBoxLayout()
        self.sender_input = QLineEdit(); self.sender_input.setPlaceholderText("Sender name")
        self.mode_select = QComboBox(); self.mode_select.addItems(["Text Mode","Image Mode"])
        top.addWidget(QLabel("Sender:")); top.addWidget(self.sender_input); top.addWidget(QLabel("Mode:")); top.addWidget(self.mode_select)
        v.addLayout(top)

        fmt = QHBoxLayout()
        self.bold_btn = QPushButton("B"); self.italic_btn = QPushButton("I"); self.underline_btn = QPushButton("U")
        fmt.addWidget(self.bold_btn); fmt.addWidget(self.italic_btn); fmt.addWidget(self.underline_btn)
        fmt.addStretch(); self.char_count = QLabel(f"0 / {CHAR_LIMIT}"); fmt.addWidget(self.char_count)
        v.addLayout(fmt)

        self.editor = QTextEdit(); self.editor.setAcceptRichText(True)
        self.image_box = QGroupBox("Image Mode"); il = QVBoxLayout(self.image_box)
        self.img_preview = QLabel("No image"); self.img_preview.setAlignment(Qt.AlignCenter); self.img_preview.setFixedHeight(180)
        self.upload_btn = QPushButton("Upload handwriting image"); il.addWidget(self.img_preview); il.addWidget(self.upload_btn)
        v.addWidget(self.editor); v.addWidget(self.image_box)
        self.image_box.hide()

        self.ps_input = QLineEdit(); self.ps_input.setPlaceholderText("P.S. (optional)"); v.addWidget(self.ps_input)

        actions = QHBoxLayout(); self.save_btn = QPushButton("Save"); self.cancel_btn = QPushButton("Cancel")
        actions.addStretch(); actions.addWidget(self.save_btn); actions.addWidget(self.cancel_btn); v.addLayout(actions)

        # signals
        self.mode_select.currentIndexChanged.connect(self._toggle_mode)
        self.upload_btn.clicked.connect(self._upload_image)
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.close)
        self.bold_btn.clicked.connect(lambda: self._apply_format("bold"))
        self.italic_btn.clicked.connect(lambda: self._apply_format("italic"))
        self.underline_btn.clicked.connect(lambda: self._apply_format("underline"))
        self.editor.textChanged.connect(self._on_text_changed)

    def _toggle_mode(self, idx):
        is_text = (idx == 0)
        self.editor.setVisible(is_text)
        self.image_box.setVisible(not is_text)
        self.bold_btn.setVisible(is_text)
        self.italic_btn.setVisible(is_text)
        self.underline_btn.setVisible(is_text)
        self.char_count.setVisible(is_text)
        self.ps_input.setVisible(is_text)

        
    def _apply_format(self, fmt):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        fmtobj = QTextCharFormat()
        if fmt == "bold":
            fmtobj.setFontWeight(QFont.Bold)
        elif fmt == "italic":
            fmtobj.setFontItalic(True)
        elif fmt == "underline":
            fmtobj.setFontUnderline(True)
        cursor.mergeCharFormat(fmtobj)
        self.editor.mergeCurrentCharFormat(fmtobj)

    def _on_text_changed(self):
        text = self.editor.toPlainText()
        if len(text) > CHAR_LIMIT:
            self.editor.blockSignals(True)
            self.editor.setPlainText(text[:CHAR_LIMIT])
            cur = self.editor.textCursor(); cur.setPosition(CHAR_LIMIT); self.editor.setTextCursor(cur)
            self.editor.blockSignals(False)
        self.char_count.setText(f"{len(self.editor.toPlainText())} / {CHAR_LIMIT}")
    
    def _upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select handwriting image", str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        try:
            im = Image.open(path)
            w, h = im.size
            min_short_side = 720
            min_long_side = 1280
            short_side, long_side = sorted((w, h))

            if short_side < min_short_side or long_side < min_long_side:
                QMessageBox.warning(
                    self, "Too small",
                    f"Image must be at least {min_long_side}×{min_short_side} "
                    "(either orientation)."
                )
                return

            self.img_path = Path(path)
            pix = QPixmap(str(path)).scaledToHeight(160, Qt.SmoothTransformation)
            self.img_preview.setPixmap(pix)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load image: {e}")
    
    def _on_save(self):
        sender = self.sender_input.text().strip() or "Unknown"
        meta = {"sender": sender, "first_opened": None, "created": now_iso(),
                "mode": "text" if self.mode_select.currentIndex()==0 else "image"}
        if meta["mode"] == "text":
            ps_text = self.ps_input.text()
            payload = {"text": self.editor.toHtml(), "ps": ps_text}
            content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        else:
            if not self.img_path:
                QMessageBox.warning(self, "No image", "Please upload an image."); return
            im = Image.open(self.img_path).convert("RGBA")
            bio = io.BytesIO(); im.save(bio, format="PNG")
            content = b"IMGPNG" + bio.getvalue()

        cfg = load_config()
        folder = Path(cfg.get("storage_folder", str(DEFAULT_DIR)))
        folder.mkdir(parents=True, exist_ok=True)
        safe_sender = "".join(c for c in sender if c.isalnum() or c in (' ', '_')).rstrip() or "sender"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_name = f"{safe_sender}_{timestamp}.let"
        default_path = folder / default_name

        fname, _ = QFileDialog.getSaveFileName(self, "Save letter", str(default_path), "LET files (*.let)")
        if not fname:
            return

        pw = None
        r = QMessageBox.question(self, "Password?", "Protect file with password?", QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            pd = PasswordDialog("Enter password", self)
            if pd.exec() != QDialog.Accepted: return
            pw = pd.password()
            if not pw:
                QMessageBox.warning(self, "Empty", "Empty password not allowed."); return

        try:
            save_letter(Path(fname), meta, content, pw)
            QMessageBox.information(self, "Saved", f"Saved: {fname}")
            self.close()
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Save failed", str(e))

# -------------------------
# Open window
# -------------------------
class OpenLetterWindow(QMainWindow):
    def __init__(self, handwriting_font=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Letter")
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(820,1000)
        self.hand_font = handwriting_font
        self._build_ui()
        self.current_path = None; self.current_meta = None; self.current_content = None
        self.current_enc = False; self.current_pw = None
        # Added: Enable focus for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def _build_ui(self):
        # --- Toolbar ---
        toolbar = QToolBar("Zoom Controls")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        zoom_in_action = QAction("Zoom In (+)", self)
        zoom_out_action = QAction("Zoom Out (-)", self)
        zoom_reset_action = QAction("Reset Zoom", self)

        toolbar.addAction(zoom_in_action)
        toolbar.addAction(zoom_out_action)
        toolbar.addAction(zoom_reset_action)

        # --- Central Widget ---
        container = QWidget()
        self.setCentralWidget(container)
        v = QVBoxLayout(container)

        self.meta_label = QLabel("Sender: ---    First opened: ---")
        v.addWidget(self.meta_label)

        # --- Renderer inside scroll area ---
        self.renderer = PaperRenderer(handwriting_font=self.hand_font)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.renderer)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        v.addWidget(self.scroll_area)

        # --- Bottom Buttons ---
        bottom = QHBoxLayout()
        self.save_copy_btn = QPushButton("Save Copy")
        self.close_btn = QPushButton("Close")
        bottom.addStretch()
        bottom.addWidget(self.save_copy_btn)
        bottom.addWidget(self.close_btn)
        v.addLayout(bottom)

        # --- Connections ---
        self.close_btn.clicked.connect(self.close)
        self.save_copy_btn.clicked.connect(self._save_copy)

        zoom_in_action.triggered.connect(self.renderer.zoom_in)
        zoom_out_action.triggered.connect(self.renderer.zoom_out)
        zoom_reset_action.triggered.connect(self.renderer.reset_zoom)

    def load_file(self, path: Path):
        try:
            enc_flag, payload = load_letter_header(path)
            if enc_flag:
                pd = PasswordDialog("Enter password to open letter", self)
                if pd.exec() != QDialog.Accepted:
                    return False
                pw = pd.password()
                try:
                    meta, content = decrypt_encrypted_payload(payload, pw)
                    self.current_pw = pw
                except Exception:
                    QMessageBox.critical(self, "Decrypt failed", "Wrong password or corrupt file.")
                    return False
            else:
                meta, content = payload

            if not meta.get("first_opened"):
                meta["first_opened"] = now_iso()
                try:
                    if enc_flag:
                        save_letter(path, meta, content, self.current_pw)
                    else:
                        save_letter(path, meta, content, None)
                except Exception:
                    pass

            self.current_path = path; self.current_meta = meta; self.current_content = content; self.current_enc = enc_flag

            self.meta_label.setText(f"Sender: {meta.get('sender','(unknown)')}    First opened: {meta.get('first_opened') or '(not opened)'}")
            if meta.get("mode") == "text":
                try:
                    payload = json.loads(content.decode("utf-8"))
                    html = payload.get("text","")
                    ps = payload.get("ps","")
                    self.renderer.set_html(html, ps)
                except Exception:
                    try:
                        text = content.decode("utf-8")
                        self.renderer.set_plain(text, "")
                    except Exception:
                        QMessageBox.warning(self, "Open", "Could not decode text content.")
            else:
                if content.startswith(b"IMGPNG"):
                    png = content[6:]; self.renderer.set_image_bytes(img_bytes=png)
                else:
                    QMessageBox.warning(self, "Unsupported", "Unknown embedded image format.")
            # Added: Fit content to window on load
            scroll = self.renderer.parentWidget()
            # inside load_file(), at the end:
            QTimer.singleShot(0, lambda: self.renderer.fit_to_window(
                self.scroll_area.viewport().width(),
                self.scroll_area.viewport().height()
            ))
            return True
        
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Open failed", str(e)); return False

    # Added: Wheel event for zooming
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.renderer.zoom_in()
            elif delta < 0:
                self.renderer.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    # Added: Keyboard shortcuts for zooming
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.renderer.zoom_in()
                event.accept()
            elif event.key() == Qt.Key_Minus:
                self.renderer.zoom_out()
                event.accept()
            elif event.key() == Qt.Key_0:
                self.renderer.reset_zoom()
                event.accept()
        else:
            super().keyPressEvent(event)

    def _save_copy(self):
        if not self.current_path or not self.current_meta:
            QMessageBox.warning(self, "No letter", "No letter loaded."); return
        dest, _ = QFileDialog.getSaveFileName(self, "Save copy", str(self.current_path.name), "LET files (*.let)")
        if not dest: return
        try:
            save_letter(Path(dest), self.current_meta, self.current_content, self.current_pw if self.current_enc else None)
            QMessageBox.information(self, "Saved", "Copy saved.")
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Save failed", str(e))

# -------------------------
# Main window (history + menu)
# -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(1100,700)
        self.hand_font = self._load_font()
        self.open_win = OpenLetterWindow(handwriting_font=self.hand_font)
        self.create_win = None
        self._build_ui()
        self._ensure_storage()
        self._refresh_history()

        # First check at startup
        self.check_for_new_letters(show_popup=True)
        #timer to check
        self.letter_check_timer = QTimer(self)
        self.letter_check_timer.timeout.connect(
            lambda: self.check_for_new_letters(show_popup=True)
        )
        self.letter_check_timer.start(30 * 60 * 1000)  # 30 minutes in ms


    def _load_font(self):
        if FONT_FILE.exists():
            id_ = QFontDatabase.addApplicationFont(str(FONT_FILE))
            fam = QFontDatabase.applicationFontFamilies(id_)
            if fam:
                return QFont(fam[0], 14)
        return QFont("Segoe Script" if platform.system()=="Windows" else "Cursive", 14)

    def _ensure_storage(self):
        cfg = load_config()
        if not cfg.get("storage_folder"):
            folder = QFileDialog.getExistingDirectory(self, "Select folder to store letters (history reads from here)", str(DEFAULT_DIR))
            if folder:
                cfg["storage_folder"] = folder
            else:
                cfg["storage_folder"] = str(DEFAULT_DIR)
            save_config(cfg)

    def _build_ui(self):
        menubar = self.menuBar(); file_menu = menubar.addMenu("File")
        settings_action = QAction("Settings", self); file_menu.addAction(settings_action); settings_action.triggered.connect(self._settings)

        c = QWidget(); self.setCentralWidget(c)
        h = QHBoxLayout(c)
        left = QVBoxLayout(); topbar = QHBoxLayout()
        self.new_btn = QPushButton("New"); self.open_btn = QPushButton("Open")
        self.search = QLineEdit(); self.search.setPlaceholderText("Search sender / filename / date...")
        topbar.addWidget(self.new_btn); topbar.addWidget(self.open_btn); topbar.addWidget(self.search)
        left.addLayout(topbar)
        self.list = QListWidget(); left.addWidget(self.list); h.addLayout(left, 3)

        right = QVBoxLayout()
        self.preview = QLabel("Select a letter to preview metadata"); self.preview.setWordWrap(True); right.addWidget(self.preview)
        actions = QHBoxLayout(); self.open_paper_btn = QPushButton("Open (paper)"); self.send_btn = QPushButton("Send"); self.delete_btn = QPushButton("Delete")
        actions.addWidget(self.open_paper_btn); actions.addWidget(self.send_btn); actions.addWidget(self.delete_btn)
        right.addLayout(actions); right.addStretch(); h.addLayout(right, 4)

        self.new_btn.clicked.connect(self._open_create)
        self.open_btn.clicked.connect(self._open_file_dialog)
        self.list.itemSelectionChanged.connect(self._on_select)
        self.open_paper_btn.clicked.connect(self._open_selected)
        self.delete_btn.clicked.connect(self._delete_selected)
        self.send_btn.clicked.connect(self._send_selected)
        self.search.textChanged.connect(self._refresh_history)
        self.list.itemDoubleClicked.connect(lambda _: self._open_selected())

    def _settings(self):
        cfg = load_config(); current = cfg.get("storage_folder", str(DEFAULT_DIR))
        folder = QFileDialog.getExistingDirectory(self, "Choose storage folder", current)
        if folder:
            cfg["storage_folder"] = folder; save_config(cfg); QMessageBox.information(self, "Saved", f"Storage folder set to:\n{folder}"); self._refresh_history()

    def _history_files(self):
        cfg = load_config(); folder = Path(cfg.get("storage_folder", str(DEFAULT_DIR)))
        if not folder.exists(): return []
        q = self.search.text().strip().lower()
        files = sorted(folder.glob("*.let"), key=lambda p: p.stat().st_mtime, reverse=True)
        rows = []
        for f in files:
            try:
                enc_flag, payload = load_letter_header(f)
                if enc_flag:
                    sender = f.name
                    first = "[LOCKED]"
                else:
                    meta, _ = payload
                    sender = meta.get("sender", "(unknown)")
                    first = meta.get("first_opened") or "(not opened)"
                label = f"{f.name} — {sender} — {first}"
                if q and q not in label.lower() and q not in f.name.lower(): continue
                rows.append((f, sender, first))
            except Exception:
                if q and q not in f.name.lower(): continue
                rows.append((f, f.name, "(corrupt)"))
        return rows

    def _refresh_history(self):
        self.list.clear()
        for f, sender, first in self._history_files():
            item = QListWidgetItem(f"{f.name}\n{sender} — {first}")
            item.setData(Qt.UserRole, str(f))
            item.setSizeHint(QSize(260,50))
            self.list.addItem(item)

    def _on_select(self):
        items = self.list.selectedItems()
        if not items:
            self.preview.setText("Select a letter to preview metadata"); return
        path = Path(items[0].data(Qt.UserRole))
        try:
            enc_flag, payload = load_letter_header(path)
            if enc_flag:
                self.preview.setText(f"Locked: {path.name}\n(Select and open to enter password)")
            else:
                meta, _ = payload
                self.preview.setText(f"Sender: {meta.get('sender','(unknown)')}\nFirst opened: {meta.get('first_opened') or '(not opened)'}")
        except Exception:
            self.preview.setText("Could not read metadata")

    def _open_create(self):
        cfg = load_config(); folder = Path(cfg.get("storage_folder", str(DEFAULT_DIR)))
        self.create_win = CreateLetterWindow(handwriting_font=self.hand_font, storage_folder=folder, parent=self)
        self.create_win.show(); self.create_win.destroyed.connect(self._refresh_history)

    def _open_file_dialog(self):
        cfg = load_config(); folder = cfg.get("storage_folder", str(DEFAULT_DIR))
        path, _ = QFileDialog.getOpenFileName(self, "Open .let file", folder, "LET files (*.let)")
        if not path: return
        self._open_path(Path(path))

    def _selected(self):
        items = self.list.selectedItems()
        if not items: return None
        return Path(items[0].data(Qt.UserRole))

    def _open_selected(self):
        p = self._selected()
        if not p:
            QMessageBox.information(self, "Select", "Please select a letter first"); return
        self._open_path(p)

    def _open_path(self, path: Path):
        ok = self.open_win.load_file(path)
        if ok:
            self.open_win.show(); self.open_win.raise_(); self._refresh_history()

    def _delete_selected(self):
        p = self._selected()
        if not p:
            QMessageBox.information(self, "Select", "Select a letter first"); return
        r = QMessageBox.question(self, "Delete", f"Delete {p.name}?", QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            try:
                p.unlink(); self._refresh_history()
            except Exception as e:
                QMessageBox.critical(self, "Delete failed", str(e))

    def _send_selected(self):
        p = self._selected()
        if not p:
            QMessageBox.information(self, "Select", "Select a letter first"); return
        subject = f"Letter: {p.stem}"; body = "Please find attached letter (.let file)."
        import webbrowser; webbrowser.open(f"mailto:?subject={subject}&body={body}")
        try:
            if platform.system()=="Windows": subprocess.run(["explorer", "/select,", str(p)])
            elif platform.system()=="Darwin": subprocess.run(["open", "-R", str(p)])
            else: subprocess.run(["xdg-open", str(p.parent)])
        except Exception:
            pass
        QMessageBox.information(self, "Send", "Mail composer opened. Attach the .let file from the revealed folder.")


    def check_for_new_letters(self, show_popup=True, popup_title="New Letter Found"):
        """Checks for new or updated .let files since last run."""
        try:
            cfg = load_config()
            folder = Path(cfg.get("storage_folder", str(DEFAULT_DIR)))
            if not folder.exists():
                return []

            # Load previous snapshot
            if LAST_FILES_FILE.exists():
                try:
                    prev_snapshot = json.loads(LAST_FILES_FILE.read_text(encoding="utf-8"))
                except Exception:
                    prev_snapshot = {}
            else:
                prev_snapshot = {}

            # Build current snapshot {filename: creation_time}
            current_snapshot = {
                f.name: get_creation_time(f)
                for f in folder.glob("*.let")
            }

            # Compare snapshots
            new_files = []
            for fname, ctime in current_snapshot.items():
                if fname not in prev_snapshot:
                    # Absolute new file
                    new_files.append(fname)
                elif ctime != prev_snapshot[fname]:
                    # Same file name but replaced/overwritten
                    new_files.append(fname)

            # Save current snapshot for next run
            LAST_FILES_FILE.write_text(
                json.dumps(current_snapshot, indent=2),
                encoding="utf-8"
            )

            # Show popup if needed
            if new_files and show_popup:
                QMessageBox.information(self, popup_title, ", ".join(new_files))
                self._refresh_history()

            return new_files

        except Exception as e:
            print("Error checking for new letters:", e)
            return []

    def closeEvent(self, event):
        self.check_for_new_letters(
            show_popup=True,
            popup_title="Files were found right after you closed:"
        )
        super().closeEvent(event)

 
# -------------------------
# Main
# -------------------------

def get_creation_time(path):
    """
    Returns the creation time of the file in seconds since epoch.
    On Windows, uses birth time; on other systems, falls back to modified time.
    """
    try:
        return os.path.getctime(path)  # Works as creation time on Windows
    except Exception:
        return os.path.getmtime(path)  # Fallback

def main():
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
