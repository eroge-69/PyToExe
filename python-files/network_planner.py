import sys
import json
import base64
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QGraphicsLineItem, QGraphicsTextItem, QInputDialog, QMessageBox,
    QDialog, QListWidget, QVBoxLayout, QLabel
)
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QColor, QFont, QImage
from PyQt5.QtCore import Qt, QPointF

JOINT_COLORS = [
    Qt.blue, QColor("orange"), Qt.green, QColor("brown"), QColor("slategray"),
    Qt.white, Qt.red, Qt.black, Qt.yellow, QColor("violet"), QColor("pink"), QColor("aqua")
]

class ZoomableView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(zoom_factor, zoom_factor)

class NetworkPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FAZAL INTERNET SERVICE   03057114234")
        self.setGeometry(100, 100, 1200, 800)
        font = QFont("Arial", 12, QFont.Bold)
        self.setFont(font)

        self.scene = QGraphicsScene()
        self.view = ZoomableView(self.scene, self)
        self.view.setGeometry(200, 20, 980, 750)

        self.map_item = None
        self.map_path = None
        self.map_base64 = None

        self.points = []
        self.lines = []

        self.undo_stack = []
        self.redo_stack = []

        self.wire_mode = False
        self.selected_wire_points = []
        self.awaiting_point_click = False

        self.init_ui()
        self.view.viewport().installEventFilter(self)

    def init_ui(self):
        button_style = "color: white; font-weight: bold;"

        self.upload_btn = QPushButton("Upload Map", self)
        self.upload_btn.setGeometry(20, 30, 150, 40)
        self.upload_btn.setStyleSheet(f"background-color: green; {button_style}")
        self.upload_btn.clicked.connect(self.upload_map)

        self.add_point_btn = QPushButton("Add Point", self)
        self.add_point_btn.setGeometry(20, 90, 150, 40)
        self.add_point_btn.setStyleSheet(f"background-color: orange; {button_style}")
        self.add_point_btn.clicked.connect(self.prepare_add_point)

        self.add_wire_btn = QPushButton("Add Wire", self)
        self.add_wire_btn.setGeometry(20, 150, 150, 40)
        self.add_wire_btn.setStyleSheet(f"background-color: dodgerblue; {button_style}")
        self.add_wire_btn.clicked.connect(self.enable_wire_mode)

        self.undo_btn = QPushButton("Undo", self)
        self.undo_btn.setGeometry(20, 210, 150, 40)
        self.undo_btn.setStyleSheet(f"background-color: red; {button_style}")
        self.undo_btn.clicked.connect(self.undo)

        self.redo_btn = QPushButton("Redo", self)
        self.redo_btn.setGeometry(20, 270, 150, 40)
        self.redo_btn.setStyleSheet(f"background-color: purple; {button_style}")
        self.redo_btn.clicked.connect(self.redo)

        self.backup_btn = QPushButton("Backup", self)
        self.backup_btn.setGeometry(20, 330, 150, 40)
        self.backup_btn.setStyleSheet(f"background-color: gray; {button_style}")
        self.backup_btn.clicked.connect(self.backup_data)

        self.restore_btn = QPushButton("Restore", self)
        self.restore_btn.setGeometry(20, 390, 150, 40)
        self.restore_btn.setStyleSheet(f"background-color: darkgray; {button_style}")
        self.restore_btn.clicked.connect(self.restore_data)

        self.export_btn = QPushButton("Export as Image", self)
        self.export_btn.setGeometry(20, 450, 150, 40)
        self.export_btn.setStyleSheet(f"background-color: teal; {button_style}")
        self.export_btn.clicked.connect(self.export_as_image)

    def upload_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Map Image", "", "Image Files (*.png *.jpg *.bmp)")
        if path:
            self.map_path = path
            with open(path, "rb") as img_file:
                self.map_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            self.set_map(QPixmap(path))

    def set_map(self, pixmap):
        if self.map_item:
            self.scene.removeItem(self.map_item)
        self.map_item = QGraphicsPixmapItem(pixmap)
        self.map_item.setZValue(-100)
        self.scene.addItem(self.map_item)
        self.view.setSceneRect(self.map_item.boundingRect())
        self.view.fitInView(self.map_item, Qt.KeepAspectRatio)

    def prepare_add_point(self):
        QMessageBox.information(self, "Add Point", "Click on the map to place the point.")
        self.awaiting_point_click = True

    def enable_wire_mode(self):
        self.wire_mode = True
        self.selected_wire_points = []
        QMessageBox.information(self, "Wire Mode", "Click any two points to draw a wire.")

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress and obj is self.view.viewport():
            self.handle_click(event)
        return super().eventFilter(obj, event)

    def handle_click(self, event):
        pos = self.view.mapToScene(event.pos())

        if self.awaiting_point_click:
            self.awaiting_point_click = False
            self.collect_point_info(pos)
            return

        if self.wire_mode:
            self.selected_wire_points.append(pos)
            if len(self.selected_wire_points) == 2:
                name, ok = QInputDialog.getText(self, "Wire Name", "Enter wire name:")
                if ok:
                    line = {'name': name, 'start': self.selected_wire_points[0], 'end': self.selected_wire_points[1]}
                    self.lines.append(line)
                    self.undo_stack.append(('add_line', line))
                    self.redo_stack.clear()
                    self.update_scene()
                self.wire_mode = False
                self.selected_wire_points = []
            return

        for point in self.points:
            if (point['pos'] - pos).manhattanLength() < 10:
                self.show_point_details(point)
                return

    def collect_point_info(self, pos):
        name, ok = QInputDialog.getText(self, "Point Name", "Enter name for the point:")
        if not (ok and name):
            return

        joints = []
        joint_count, ok = QInputDialog.getInt(self, "Joint Count", "How many joints?", 1, 1, 10)
        if not ok:
            return

        for i in range(joint_count):
            joint_type, ok = QInputDialog.getItem(self, f"Joint {i+1}", "Select joint type:", ["Simple", "Splitter"], 0, False)
            if not ok:
                continue
            if joint_type == "Simple":
                conn, ok = QInputDialog.getText(self, "Connection", "Connected to (point name or number):")
                if ok:
                    joints.append({"type": "simple", "connected_to": conn})
            elif joint_type == "Splitter":
                out_count, ok = QInputDialog.getItem(self, "Splitter Outputs", "Number of outputs:", ["2", "4", "8", "16"], 0, False)
                if not ok:
                    continue
                outputs = {}
                for j in range(int(out_count)):
                    out_name, ok = QInputDialog.getText(self, f"Output {j+1}", f"Enter name for output {j+1}:")
                    if ok:
                        outputs[f"Out{j+1}"] = out_name
                joints.append({"type": "splitter", "outputs": outputs})

        point = {'name': name, 'pos': pos, 'joints': joints}
        self.points.append(point)
        self.undo_stack.append(('add_point', point))
        self.redo_stack.clear()
        self.update_scene()

    def update_scene(self):
        self.scene.clear()
        if self.map_item:
            self.scene.addItem(self.map_item)

        for line in self.lines:
            line_item = QGraphicsLineItem(line['start'].x(), line['start'].y(), line['end'].x(), line['end'].y())
            pen = QPen(Qt.black, 1)
            line_item.setPen(pen)
            line_item.setToolTip(line['name'])
            self.scene.addItem(line_item)

        for point in self.points:
            rect_item = QGraphicsRectItem(point['pos'].x() - 5, point['pos'].y() - 5, 10, 10)
            rect_item.setBrush(QBrush(Qt.red))
            rect_item.setToolTip(point['name'])
            self.scene.addItem(rect_item)

    def undo(self):
        if not self.undo_stack:
            return
        action, data = self.undo_stack.pop()
        if action == 'add_point':
            self.points.remove(data)
            self.redo_stack.append((action, data))
        elif action == 'add_line':
            self.lines.remove(data)
            self.redo_stack.append((action, data))
        self.update_scene()

    def redo(self):
        if not self.redo_stack:
            return
        action, data = self.redo_stack.pop()
        if action == 'add_point':
            self.points.append(data)
            self.undo_stack.append((action, data))
        elif action == 'add_line':
            self.lines.append(data)
            self.undo_stack.append((action, data))
        self.update_scene()

    def show_point_details(self, point):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Point: {point['name']}")
        layout = QVBoxLayout()

        label_simple = QLabel("<b>Simple Joints:</b>")
        layout.addWidget(label_simple)
        list_simple = QListWidget()
        for i, joint in enumerate(point.get('joints', [])):
            if joint['type'] == 'simple':
                list_simple.addItem(f"Joint {i+1}: Connected to {joint['connected_to']}")
        layout.addWidget(list_simple)

        label_splitter = QLabel("<b>Splitter Joints:</b>")
        layout.addWidget(label_splitter)
        list_splitter = QListWidget()
        for i, joint in enumerate(point.get('joints', [])):
            if joint['type'] == 'splitter':
                for key, val in joint['outputs'].items():
                    list_splitter.addItem(f"Joint {i+1} → {key}: {val}")
        layout.addWidget(list_splitter)

        dlg.setLayout(layout)
        dlg.setMinimumWidth(400)
        dlg.exec_()

    def backup_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup File", "", "JSON Files (*.json)")
        if path:
            data = {
                'map_base64': self.map_base64,
                'points': [
                    {
                        'name': p['name'],
                        'x': p['pos'].x(),
                        'y': p['pos'].y(),
                        'joints': p['joints']
                    } for p in self.points
                ],
                'lines': [
                    {
                        'name': l['name'],
                        'x1': l['start'].x(),
                        'y1': l['start'].y(),
                        'x2': l['end'].x(),
                        'y2': l['end'].y()
                    } for l in self.lines
                ]
            }
            with open(path, 'w') as f:
                json.dump(data, f)
            QMessageBox.information(self, "Success", "Backup completed.")

    def restore_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Restore File", "", "JSON Files (*.json)")
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            self.points = [
                {
                    'name': p['name'],
                    'pos': QPointF(p['x'], p['y']),
                    'joints': p.get('joints', [])
                } for p in data.get('points', [])
            ]
            self.lines = [
                {
                    'name': l['name'],
                    'start': QPointF(l['x1'], l['y1']),
                    'end': QPointF(l['x2'], l['y2'])
                } for l in data.get('lines', [])
            ]
            base64_data = data.get('map_base64')
            if base64_data:
                image_data = base64.b64decode(base64_data)
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap.fromImage(image)
                self.set_map(pixmap)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.update_scene()

    def export_as_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Image", "", "JPEG Files (*.jpg)")
        if path:
            rect = self.scene.sceneRect()
            image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            image.save(path, "JPG")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NetworkPlanner()
    window.show()
    sys.exit(app.exec_())