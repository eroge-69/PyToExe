import sys
import svgwrite
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class UrduDesignApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Urdu Vector Designer")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Paste your Urdu text:")
        layout.addWidget(self.label)

        self.textbox = QTextEdit()
        layout.addWidget(self.textbox)

        self.button_add = QPushButton("Add Text to Canvas")
        self.button_add.clicked.connect(self.add_text_to_canvas)
        layout.addWidget(self.button_add)

        self.button_export = QPushButton("Export as SVG")
        self.button_export.clicked.connect(self.export_svg)
        layout.addWidget(self.button_export)

        # Canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.setLayout(layout)

    def add_text_to_canvas(self):
        text = self.textbox.toPlainText().strip()
        if text:
            words = text.split(" ")
            x = 0
            for word in words:
                item = QGraphicsTextItem(word)
                item.setFont(QFont("Jameel Noori Nastaleeq", 32))
                item.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
                item.setPos(x, 100)
                self.scene.addItem(item)
                x += 150

    def export_svg(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg)")
        if file_path:
            dwg = svgwrite.Drawing(file_path, size=("800px", "600px"))
            for item in self.scene.items():
                if isinstance(item, QGraphicsTextItem):
                    pos = item.pos()
                    dwg.add(dwg.text(item.toPlainText(),
                                     insert=(pos.x(), pos.y()),
                                     font_size="32px",
                                     font_family="Jameel Noori Nastaleeq"))
            dwg.save()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UrduDesignApp()
    window.show()
    sys.exit(app.exec_())