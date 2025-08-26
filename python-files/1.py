import sys, io, secrets, struct
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QLineEdit, QTabWidget, QMessageBox
)
from PIL import Image
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------- AES helpers ----------------

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_bytes(data: bytes, password: str):
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ct

def decrypt_bytes(blob: bytes, password: str):
    salt = blob[:16]
    nonce = blob[16:28]
    ct = blob[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)

# ---------------- LSB helpers ----------------

def bytes_to_bits_2bits(data: bytes):
    for b in data:
        for i in range(6, -2, -2):  # 2 bits à la fois
            yield (b >> i) & 0b11

def bits_to_bytes_2bits(bits):
    out = bytearray()
    acc = 0
    n = 0
    for bit in bits:
        acc = (acc << 2) | bit
        n += 2
        if n == 8:
            out.append(acc)
            acc = 0
            n = 0
    return bytes(out)

# ---------------- Hide / Extract ----------------

def hide_image_large(cover_path, secret_path, output_path, password):
    cover = Image.open(cover_path).convert("RGB")
    secret_img = Image.open(secret_path).convert("RGB")
    buf = io.BytesIO()
    secret_img.save(buf, format="PNG")
    secret_data = buf.getvalue()

    payload = encrypt_bytes(secret_data, password)
    payload_with_len = struct.pack(">I", len(payload)) + payload

    max_bits = cover.width * cover.height * 3 * 2  # 2 bits par canal
    if len(payload_with_len)*8 > max_bits:
        raise ValueError("Image trop petite pour contenir le fichier secret !")

    bits = list(bytes_to_bits_2bits(payload_with_len))
    pixels = cover.load()
    idx = 0
    for y in range(cover.height):
        for x in range(cover.width):
            r, g, b = pixels[x, y]
            if idx < len(bits):
                r = (r & ~0b11) | bits[idx]; idx += 1
            if idx < len(bits):
                g = (g & ~0b11) | bits[idx]; idx += 1
            if idx < len(bits):
                b = (b & ~0b11) | bits[idx]; idx += 1
            pixels[x, y] = (r, g, b)
            if idx >= len(bits):
                break
        if idx >= len(bits):
            break

    cover.save(output_path, format="PNG")

def extract_image_large(stego_path, output_path, password):
    stego = Image.open(stego_path).convert("RGB")
    pixels = stego.load()
    bits = []
    for y in range(stego.height):
        for x in range(stego.width):
            r, g, b = pixels[x, y]
            bits.extend([r & 0b11, g & 0b11, b & 0b11])

    data = bits_to_bytes_2bits(bits)
    if len(data) < 4:
        raise ValueError("Image stégo trop petite.")

    payload_len = struct.unpack(">I", data[:4])[0]
    payload = data[4:4+payload_len]

    if len(payload) != payload_len:
        raise ValueError("Données stégo corrompues ou incomplètes.")

    secret_bytes = decrypt_bytes(payload, password)
    secret_img = Image.open(io.BytesIO(secret_bytes))
    secret_img.save(output_path)

# ---------------- GUI ----------------

class StegoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stego Image Fiable - 2bits par canal")
        self.resize(450, 280)

        tabs = QTabWidget()
        tabs.addTab(self.build_hide_tab(), "Cacher")
        tabs.addTab(self.build_extract_tab(), "Extraire")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def build_hide_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.cover_edit = QLineEdit(); self.cover_edit.setPlaceholderText("Image banale")
        btn_cover = QPushButton("Choisir image banale")
        btn_cover.clicked.connect(lambda: self.choose_file(self.cover_edit))

        self.secret_edit = QLineEdit(); self.secret_edit.setPlaceholderText("Image secrète")
        btn_secret = QPushButton("Choisir image secrète")
        btn_secret.clicked.connect(lambda: self.choose_file(self.secret_edit))

        self.out_edit = QLineEdit(); self.out_edit.setPlaceholderText("Image sortie (.png)")
        btn_out = QPushButton("Choisir emplacement sortie")
        btn_out.clicked.connect(lambda: self.save_file(self.out_edit))

        self.pwd_edit = QLineEdit(); self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.setPlaceholderText("Mot de passe")

        btn_hide = QPushButton("Cacher")
        btn_hide.clicked.connect(self.do_hide)

        layout.addWidget(self.cover_edit)
        layout.addWidget(btn_cover)
        layout.addWidget(self.secret_edit)
        layout.addWidget(btn_secret)
        layout.addWidget(self.out_edit)
        layout.addWidget(btn_out)
        layout.addWidget(self.pwd_edit)
        layout.addWidget(btn_hide)

        w.setLayout(layout)
        return w

    def build_extract_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.stego_edit = QLineEdit(); self.stego_edit.setPlaceholderText("Image stégo")
        btn_stego = QPushButton("Choisir image stégo")
        btn_stego.clicked.connect(lambda: self.choose_file(self.stego_edit))

        self.out_secret_edit = QLineEdit(); self.out_secret_edit.setPlaceholderText("Sauvegarder image extraite")
        btn_out = QPushButton("Choisir emplacement sortie")
        btn_out.clicked.connect(lambda: self.save_file(self.out_secret_edit))

        self.pwd_edit2 = QLineEdit(); self.pwd_edit2.setPlaceholderText("Mot de passe")
        self.pwd_edit2.setEchoMode(QLineEdit.Password)

        btn_extract = QPushButton("Extraire")
        btn_extract.clicked.connect(self.do_extract)

        layout.addWidget(self.stego_edit)
        layout.addWidget(btn_stego)
        layout.addWidget(self.out_secret_edit)
        layout.addWidget(btn_out)
        layout.addWidget(self.pwd_edit2)
        layout.addWidget(btn_extract)

        w.setLayout(layout)
        return w

    def choose_file(self, lineedit):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir fichier", "", 
                                              "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)")
        if path:
            lineedit.setText(path)

    def save_file(self, lineedit):
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder fichier", "", "PNG (*.png)")
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            lineedit.setText(path)

    def do_hide(self):
        if not all([self.cover_edit.text(), self.secret_edit.text(), self.out_edit.text(), self.pwd_edit.text()]):
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
        try:
            hide_image_large(self.cover_edit.text(), self.secret_edit.text(),
                             self.out_edit.text(), self.pwd_edit.text())
            QMessageBox.information(self, "Succès", "Image secrète cachée avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def do_extract(self):
        if not all([self.stego_edit.text(), self.out_secret_edit.text(), self.pwd_edit2.text()]):
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
        try:
            extract_image_large(self.stego_edit.text(), self.out_secret_edit.text(),
                                self.pwd_edit2.text())
            QMessageBox.information(self, "Succès", "Image secrète extraite avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

# ---------------- Main ----------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StegoApp()
    win.show()
    sys.exit(app.exec())
