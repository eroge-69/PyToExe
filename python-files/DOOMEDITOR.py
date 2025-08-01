import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QFileDialog, QLabel, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt


class STRTextEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Arquivos .STR")
        self.resize(800, 600)
        self.text_edits = []

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QLabel("Selecione um arquivo .str com blocos de texto (2 bytes de tamanho + texto UTF-8)")
        self.layout.addWidget(self.info_label)

        # Scroll area para os textos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QFrame()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Botões
        self.load_button = QPushButton("📂 Selecionar Arquivo")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.save_button = QPushButton("💾 Salvar como .str")
        self.save_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_button)

        self.about_button = QPushButton("ℹ️ Sobre")
        self.about_button.clicked.connect(self.show_about)
        self.layout.addWidget(self.about_button)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir arquivo .str", "", "Arquivos STR (*.str);;Todos os arquivos (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir arquivo", str(e))
            return

        self.clear_edits()
        pos = 0

        while pos + 2 <= len(data):
            length = int.from_bytes(data[pos:pos+2], byteorder='little')
            pos += 2

            if pos + length > len(data):
                break

            text_bytes = data[pos:pos+length]
            try:
                text = text_bytes.decode('utf-8')
            except UnicodeDecodeError:
                text = text_bytes.decode('latin-1', errors='replace')

            pos += length
            self.add_text_block(text)

        QMessageBox.information(self, "Arquivo carregado", f"Total de textos carregados: {len(self.text_edits)}")

    def add_text_block(self, text):
        edit = QTextEdit()
        edit.setPlainText(text)
        edit.setFixedHeight(50)
        self.scroll_layout.addWidget(edit)
        self.text_edits.append(edit)

    def clear_edits(self):
        for edit in self.text_edits:
            self.scroll_layout.removeWidget(edit)
            edit.deleteLater()
        self.text_edits.clear()

    def save_file(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar arquivo .str", "", "Arquivos STR (*.str)"
        )
        if not save_path:
            return

        if not save_path.lower().endswith(".str"):
            save_path += ".str"

        output = bytearray()
        for edit in self.text_edits:
            text = edit.toPlainText()
            text_bytes = text.encode('utf-8')  # usa UTF-8 para suportar acentos
            length = len(text_bytes)
            output.extend(length.to_bytes(2, byteorder='little'))
            output.extend(text_bytes)

        try:
            with open(save_path, 'wb') as f:
                f.write(output)
            QMessageBox.information(self, "Salvo com sucesso", f"Arquivo salvo em: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", str(e))

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Sobre o Editor")

        msg.setTextFormat(Qt.RichText)  # habilita HTML
        msg.setText(
            "<h3>📝 Editor de Arquivos .STR</h3>"
            "<p><b>Versão:</b> 1.0<br>"
            "<b>Autor:</b> William Paiva + ChatGPT</p>"
            "<p>Este editor permite abrir arquivos .str com textos no formato:<br>"
            "<code>[2 bytes (Little Endian) + texto UTF-8]</code></p>"
            "<p>Para suporte e dúvidas, junte-se ao nosso Discord:<br>"
            "<a href='https://discord.gg/uVmfnWVuda' style='color:#5865F2;'>https://discord.gg/uVmfnWVuda</a></p>"
        )

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)  # permite clicar no link
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = STRTextEditor()
    editor.show()
    sys.exit(app.exec_())