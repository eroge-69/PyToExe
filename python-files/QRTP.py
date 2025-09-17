import sys, qrcode
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QInputDialog, QSpinBox, QColorDialog, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
from PIL.ImageQt import ImageQt
from pyzbar.pyzbar import decode
from docx import Document
from docx.shared import Inches
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -----------------------------
# Temas
# -----------------------------
TEMAS = {
    "Claro": {"bg": "#f0f0f0", "fg": "#000000"},
    "Oscuro": {"bg": "#2b2b2b", "fg": "#f0f0f0"},
}

# -----------------------------
# Ventana de personalización
# -----------------------------
class PersonalizarQR(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Personalizar QR")
        self.setGeometry(400, 250, 450, 400)
        self.parent = parent
        self.color_fg = "#000000"
        self.color_bg = "#ffffff"
        self.logo_path = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Botones de color
        self.btn_color_fg = QPushButton("Color QR")
        self.btn_color_fg.clicked.connect(self.seleccionar_color_fg)
        self.layout.addWidget(self.btn_color_fg)

        self.btn_color_bg = QPushButton("Color fondo")
        self.btn_color_bg.clicked.connect(self.seleccionar_color_bg)
        self.layout.addWidget(self.btn_color_bg)

        # Tamaño QR
        self.layout.addWidget(QLabel("Tamaño del QR:"))
        self.spin_size = QSpinBox()
        self.spin_size.setRange(50, 1000)
        self.spin_size.setValue(250)
        self.spin_size.valueChanged.connect(self.actualizar_preview)
        self.layout.addWidget(self.spin_size)

        # Logo
        self.btn_logo = QPushButton("Agregar logo")
        self.btn_logo.clicked.connect(self.agregar_logo)
        self.layout.addWidget(self.btn_logo)

        # Vista previa
        self.preview_label = QLabel("Vista previa")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.preview_label)

        # Botón aplicar
        self.btn_aplicar = QPushButton("Aplicar")
        self.btn_aplicar.clicked.connect(self.aplicar_personalizacion)
        self.layout.addWidget(self.btn_aplicar)

    def seleccionar_color_fg(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_fg = color.name()
            self.actualizar_preview()

    def seleccionar_color_bg(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_bg = color.name()
            self.actualizar_preview()

    def agregar_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar logo", "", "Imágenes (*.png *.jpg *.bmp)")
        if path:
            self.logo_path = path
            self.actualizar_preview()

    def actualizar_preview(self):
        data = self.parent.text_input.toPlainText().strip()
        if not data:
            self.preview_label.clear()
            return
        try:
            # Generar QR
            qr = qrcode.QRCode(border=1)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            img = img.resize((self.spin_size.value(), self.spin_size.value()))

            # Aplicar colores
            fg = Image.new("RGB", img.size, self.color_fg)
            bg = Image.new("RGB", img.size, self.color_bg)
            mask = img.convert("L")
            img_colored = Image.composite(fg, bg, mask)

            # Agregar logo
            if self.logo_path:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo_size = self.spin_size.value() // 4
                logo = logo.resize((logo_size, logo_size))
                pos = ((img_colored.size[0]-logo_size)//2, (img_colored.size[1]-logo_size)//2)
                img_colored.paste(logo, pos, mask=logo.split()[3])

            # Guardamos para aplicar
            self.current_img = img_colored

            # Mostrar preview
            qt_img = ImageQt(img_colored)
            pixmap = QPixmap.fromImage(qt_img)
            self.preview_label.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar preview: {e}")

    def aplicar_personalizacion(self):
        data = self.parent.text_input.toPlainText().strip()
        if not data:
            QMessageBox.warning(self, "Error", "Escribe algo primero")
            return
        if hasattr(self, "current_img"):
            self.parent.img = self.current_img
            self.parent.mostrar_preview(self.parent.img)
            self.parent.agregar_historial(f"Personalizado: {data}", self.parent.img)
            QMessageBox.information(self, "Éxito", "QR personalizado aplicado")
            self.close()

# -----------------------------
# Ventana principal
# -----------------------------
class QRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Tool Plus - Generador y Lector")
        self.setGeometry(300, 200, 750, 650)
        self.img = None
        self.historial_img_dict = {}
        self.ventana_personalizar = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Texto o link...")
        self.layout.addWidget(self.text_input)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generar QR")
        self.btn_generate.clicked.connect(self.generar_qr_action)
        btn_layout.addWidget(self.btn_generate)

        self.btn_read = QPushButton("Leer QR")
        self.btn_read.clicked.connect(self.leer_qr_action)
        btn_layout.addWidget(self.btn_read)

        self.btn_download = QPushButton("Descargar")
        self.btn_download.clicked.connect(self.descargar_qr_action)
        btn_layout.addWidget(self.btn_download)

        self.btn_personalizar = QPushButton("Personalizar")
        self.btn_personalizar.clicked.connect(self.abrir_personalizar)
        btn_layout.addWidget(self.btn_personalizar)

        self.tema_combo = QComboBox()
        self.tema_combo.addItems(TEMAS.keys())
        self.tema_combo.currentTextChanged.connect(self.aplicar_tema)
        btn_layout.addWidget(self.tema_combo)

        self.layout.addLayout(btn_layout)

        # Vista previa
        self.qr_preview = QLabel("Vista previa QR")
        self.qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.qr_preview)

        # Historial
        self.historial_list = QListWidget()
        self.historial_list.setMaximumHeight(180)
        self.historial_list.itemClicked.connect(self.mostrar_historial_preview)
        self.historial_list.itemDoubleClicked.connect(self.editar_historial)
        self.historial_list.keyPressEvent = self.borrar_historial_key
        self.layout.addWidget(QLabel("Historial (doble clic=editar, seleccionar+Supr=borrar)"))
        self.layout.addWidget(self.historial_list)

    # -----------------------------
    # Funciones QR
    # -----------------------------
    def generar_qr_action(self):
        data = self.text_input.toPlainText().strip()
        if not data:
            QMessageBox.warning(self, "Error", "Escribe algo")
            return
        img = qrcode.make(data).convert("RGB").resize((250, 250))
        self.img = img
        self.mostrar_preview(img)
        self.agregar_historial(f"Generado: {data}", img)

    def leer_qr_action(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona QR", "", "Imágenes (*.png *.jpg *.bmp)")
        if not path:
            return
        img = Image.open(path)
        result = decode(img)
        if result:
            QMessageBox.information(self, "QR leído", result[0].data.decode("utf-8"))
        else:
            QMessageBox.warning(self, "Error", "No se detectó QR válido")

    def mostrar_preview(self, img):
        try:
            qt_img = ImageQt(img)
            pixmap = QPixmap.fromImage(qt_img)
            self.qr_preview.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo mostrar preview: {e}")

    def descargar_qr_action(self):
        if not self.img:
            QMessageBox.warning(self, "Error", "Primero genera QR")
            return
        formatos = ["PNG", "JPG", "BMP", "PDF", "Word"]
        formato, ok = QInputDialog.getItem(self, "Formato", "Formato:", formatos, 0, False)
        if not ok: return
        try:
            if formato in ["PNG","JPG","BMP"]:
                path,_ = QFileDialog.getSaveFileName(self, "Guardar", f"QR.{formato.lower()}", f"{formato} Files (*.{formato.lower()})")
                if path: self.img.save(path)
            elif formato=="PDF":
                path,_ = QFileDialog.getSaveFileName(self,"Guardar PDF","QR.pdf","PDF Files (*.pdf)")
                if path:
                    c=canvas.Canvas(path,pagesize=letter)
                    c.drawInlineImage(self.img.resize((400,400)),100,500)
                    c.showPage()
                    c.save()
            elif formato=="Word":
                path,_ = QFileDialog.getSaveFileName(self,"Guardar Word","QR.docx","Word Files (*.docx)")
                if path:
                    doc = Document()
                    temp_path="temp_doc_img.png"
                    self.img.save(temp_path)
                    doc.add_picture(temp_path,width=Inches(2))
                    doc.save(path)
            QMessageBox.information(self,"Éxito","QR guardado")
        except Exception as e:
            QMessageBox.warning(self,"Error",f"No se pudo guardar: {e}")

    # -----------------------------
    # Historial
    # -----------------------------
    def agregar_historial(self,texto,img):
        i=1
        texto_final=texto
        while texto_final in self.historial_img_dict:
            texto_final=f"{texto} ({i})"
            i+=1
        item=QListWidgetItem(texto_final)
        self.historial_list.addItem(item)
        self.historial_img_dict[texto_final]=img

    def mostrar_historial_preview(self,item):
        texto=item.text()
        if texto in self.historial_img_dict:
            self.img=self.historial_img_dict[texto]
            self.mostrar_preview(self.img)

    def editar_historial(self,item):
        nuevo_texto, ok = QInputDialog.getText(self,"Editar historial","Modificar item:",text=item.text())
        if ok and nuevo_texto:
            if nuevo_texto in self.historial_img_dict:
                QMessageBox.warning(self,"Error","Ya existe ese texto en el historial")
                return
            self.historial_img_dict[nuevo_texto]=self.historial_img_dict.pop(item.text())
            item.setText(nuevo_texto)

    def borrar_historial_key(self,event):
        if event.key()==Qt.Key.Key_Delete:
            for item in self.historial_list.selectedItems():
                t=item.text()
                self.historial_list.takeItem(self.historial_list.row(item))
                if t in self.historial_img_dict:
                    del self.historial_img_dict[t]
        else:
            QListWidget.keyPressEvent(self.historial_list,event)

    # -----------------------------
    # Personalizar
    # -----------------------------
    def abrir_personalizar(self):
        if self.ventana_personalizar is None:
            self.ventana_personalizar=PersonalizarQR(self)
        self.ventana_personalizar.show()
        self.ventana_personalizar.raise_()
        self.ventana_personalizar.activateWindow()

    # -----------------------------
    # Temas
    # -----------------------------
    def aplicar_tema(self,nombre):
        tema=TEMAS.get(nombre,TEMAS["Claro"])
        self.setStyleSheet(f"background-color:{tema['bg']};color:{tema['fg']};")

# -----------------------------
# Main
# -----------------------------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = QRApp()
    window.show()
    sys.exit(app.exec())
