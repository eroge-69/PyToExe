import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QSlider, QColorDialog, QFontDialog, QFileDialog,
                             QShortcut, QTextEdit, QDialog)
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QKeySequence, QIcon, QPixmap, QScreen)
from PyQt5.QtCore import Qt, QPoint, QSize, QRect, QTimer

# --- Annotation Data Classes ---

class Annotation:
    """Base class for an annotation object."""
    def __init__(self, color, thickness):
        self.color = color
        self.thickness = thickness

    def draw(self, painter):
        raise NotImplementedError

class FreehandAnnotation(Annotation):
    """Represents a freehand drawing."""
    def __init__(self, color, thickness):
        super().__init__(color, thickness)
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    def draw(self, painter):
        if len(self.points) > 1:
            pen = QPen(self.color, self.thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline(*self.points)

class ShapeAnnotation(Annotation):
    """Base class for shape annotations."""
    def __init__(self, color, thickness, start_point, end_point):
        super().__init__(color, thickness)
        self.start_point = start_point
        self.end_point = end_point

    def get_rect(self):
        return QRect(self.start_point, self.end_point).normalized()

class LineAnnotation(ShapeAnnotation):
    """Represents a line."""
    def draw(self, painter):
        pen = QPen(self.color, self.thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.start_point, self.end_point)

class RectangleAnnotation(ShapeAnnotation):
    """Represents a rectangle."""
    def draw(self, painter):
        pen = QPen(self.color, self.thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.get_rect())

class EllipseAnnotation(ShapeAnnotation):
    """Represents an ellipse."""
    def draw(self, painter):
        pen = QPen(self.color, self.thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(self.get_rect())

class TextAnnotation(Annotation):
    """Represents a text annotation."""
    def __init__(self, color, text, position, font):
        super().__init__(color, 0)
        self.text = text
        self.position = position
        self.font = font

    def draw(self, painter):
        pen = QPen(self.color)
        painter.setPen(pen)
        painter.setFont(self.font)
        painter.drawText(self.position, self.text)

# --- GUI Classes ---

class DrawingCanvas(QMainWindow):
    """The main window for drawing. It can be transparent or show a screenshot."""
    def __init__(self, toolbar):
        super().__init__()
        self.toolbar = toolbar
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.desktop().screenGeometry())

        self.annotations = []
        self.undo_stack = []
        self.redo_stack = []
        self.drawing = False
        self.current_annotation = None
        self.start_point = QPoint()
        self.end_point = QPoint()

        self.background_pixmap = None
        self.background_color = QColor(0, 0, 0, 0)

    def _add_undo_state(self):
        """Saves the current state of annotations for undo."""
        self.undo_stack.append(list(self.annotations))
        self.redo_stack.clear()

    def show_canvas_and_toolbar(self):
        """Makes the canvas and toolbar visible, ensuring toolbar is on top."""
        self.showFullScreen()
        self.toolbar.show()
        self.update()

    def prepare_for_screenshot(self):
        """Hides UI and waits to capture screen."""
        self.toolbar.hide()
        QTimer.singleShot(200, self._capture_and_show)

    def _capture_and_show(self):
        """Performs the screen capture and then shows the drawing UI."""
        screen = QApplication.primaryScreen()
        self.background_pixmap = screen.grabWindow(0)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.clear_screen(clear_background=False, can_undo=False)
        self.show_canvas_and_toolbar()

    def prepare_for_solid_background(self, color):
        """Hides UI and sets a solid color background."""
        self.toolbar.hide()
        self.background_pixmap = None
        self.background_color = color
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.clear_screen(clear_background=False, can_undo=False)
        QTimer.singleShot(10, self.show_canvas_and_toolbar)

    def enter_mouse_mode(self):
        """Makes the drawing canvas invisible to allow interaction with desktop."""
        self.background_pixmap = None
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.clear_screen(can_undo=False)
        self.hide()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background_pixmap:
            painter.drawPixmap(self.rect(), self.background_pixmap)
        else:
            painter.fillRect(self.rect(), self.background_color)

        for annotation in self.annotations:
            annotation.draw(painter)
        if self.current_annotation:
            self.current_annotation.draw(painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.toolbar.is_drawing_mode:
            if not self.drawing:
                self._add_undo_state()
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            
            tool = self.toolbar.current_tool
            color = self.toolbar.color
            thickness = self.toolbar.thickness

            if tool in ["pen", "highlighter"]:
                if tool == "highlighter":
                    color = QColor(color)
                    color.setAlpha(128)
                self.current_annotation = FreehandAnnotation(color, thickness)
                self.current_annotation.add_point(self.start_point)
            elif tool == "eraser":
                self.erase(event.pos())
            elif tool == "text":
                self.add_text_annotation(event.pos())
                self.drawing = False
            
            self.toolbar.raise_()

    def mouseMoveEvent(self, event):
        if self.drawing and self.toolbar.is_drawing_mode:
            self.end_point = event.pos()
            tool = self.toolbar.current_tool
            color = self.toolbar.color
            thickness = self.toolbar.thickness

            if tool == "highlighter":
                color = QColor(color)
                color.setAlpha(128)

            if tool in ["pen", "highlighter"]:
                self.current_annotation.add_point(self.end_point)
            elif tool == "line":
                self.current_annotation = LineAnnotation(color, thickness, self.start_point, self.end_point)
            elif tool == "rectangle":
                self.current_annotation = RectangleAnnotation(color, thickness, self.start_point, self.end_point)
            elif tool == "ellipse":
                self.current_annotation = EllipseAnnotation(color, thickness, self.start_point, self.end_point)
            elif tool == "eraser":
                self.erase(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing and self.toolbar.is_drawing_mode:
            self.drawing = False
            if self.current_annotation:
                self.annotations.append(self.current_annotation)
                self.current_annotation = None
            self.update()

    def add_text_annotation(self, position):
        self._add_undo_state()
        text, ok = TextDialog.getText(self, self.toolbar.font)
        if ok and text:
            annotation = TextAnnotation(self.toolbar.color, text, position, self.toolbar.font)
            self.annotations.append(annotation)
        else: # If user cancels, pop the undo state we just added
            self.undo_stack.pop()
        self.update()

    def erase(self, pos):
        erase_radius = self.toolbar.thickness * 2
        items_removed = False
        
        # Create a new list excluding erased items
        new_annotations = []
        for ann in self.annotations:
            should_keep = True
            if isinstance(ann, FreehandAnnotation):
                for point in ann.points:
                    if (point - pos).manhattanLength() < erase_radius:
                        should_keep = False
                        break
            elif isinstance(ann, ShapeAnnotation):
                 if ann.get_rect().adjusted(-10, -10, 10, 10).contains(pos):
                    should_keep = False
            elif isinstance(ann, TextAnnotation):
                metrics = self.fontMetrics()
                rect = metrics.boundingRect(ann.position, Qt.AlignLeft, ann.text)
                if rect.adjusted(-10, -10, 10, 10).contains(pos):
                    should_keep = False
            
            if should_keep:
                new_annotations.append(ann)
            else:
                items_removed = True
        
        if items_removed:
            self.annotations = new_annotations
            self.update()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(list(self.annotations))
            self.annotations = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(list(self.annotations))
            self.annotations = self.redo_stack.pop()
            self.update()

    def clear_screen(self, clear_background=True, can_undo=True):
        if can_undo:
            self._add_undo_state()

        self.annotations.clear()
        if clear_background:
            self.background_color = QColor(0, 0, 0, 0)
            self.background_pixmap = None
        self.update()

    def take_screenshot_with_annotations(self):
        self.hide()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        self.show()
        if file_path:
            pixmap = self.grab()
            pixmap.save(file_path)

class Toolbar(QWidget):
    """The floating toolbar with all the annotation tools."""
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.current_tool = "pen"
        self.color = Qt.red
        self.thickness = 5
        self.font = QFont("Arial", 16)
        self.is_drawing_mode = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # --- Mode Switching ---
        self.mouse_button = self.create_button("icons/mouse.png", "Mouse Mode (Esc)", self.activate_mouse_mode)
        self.draw_button = self.create_button("icons/draw.png", "Draw Mode (Freeze Screen)", self.activate_draw_mode)

        # --- Tools ---
        self.pen_button = self.create_button("icons/pen.png", "Pen (P)", self.select_pen)
        self.highlighter_button = self.create_button("icons/highlighter.png", "Highlighter (H)", self.select_highlighter)
        self.eraser_button = self.create_button("icons/eraser.png", "Eraser (E)", self.select_eraser)
        self.line_button = self.create_button("icons/line.png", "Line (L)", self.select_line)
        self.rect_button = self.create_button("icons/rectangle.png", "Rectangle (R)", self.select_rectangle)
        self.ellipse_button = self.create_button("icons/ellipse.png", "Ellipse (C)", self.select_ellipse)
        self.text_button = self.create_button("icons/text.png", "Text (T)", self.select_text)
        self.color_button = self.create_button("icons/color.png", "Color", self.select_color)
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(1, 50)
        self.thickness_slider.setValue(self.thickness)
        self.thickness_slider.valueChanged.connect(self.change_thickness)
        self.undo_button = self.create_button("icons/undo.png", "Undo (Ctrl+Z)", self.canvas.undo)
        self.redo_button = self.create_button("icons/redo.png", "Redo (Ctrl+Y)", self.canvas.redo)
        self.clear_button = self.create_button("icons/clear.png", "Clear", self.canvas.clear_screen)
        self.screenshot_button = self.create_button("icons/screenshot.png", "Screenshot (S)", self.canvas.take_screenshot_with_annotations)
        self.whiteboard_button = self.create_button("icons/whiteboard.png", "Whiteboard (W)", self.toggle_whiteboard)
        self.blackboard_button = self.create_button("icons/blackboard.png", "Blackboard (B)", self.toggle_blackboard)
        self.exit_button = self.create_button("icons/exit.png", "Exit", self.close_app)

        self.tool_buttons = [
            self.pen_button, self.highlighter_button, self.eraser_button,
            self.line_button, self.rect_button, self.ellipse_button, self.text_button,
            self.color_button, self.thickness_slider, self.undo_button, self.redo_button,
            self.clear_button, self.screenshot_button, self.whiteboard_button, self.blackboard_button
        ]

        layout.addWidget(self.mouse_button)
        layout.addWidget(self.draw_button)
        for widget in self.tool_buttons:
            layout.addWidget(widget)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)
        self.setup_shortcuts()
        self.oldPos = self.pos()
        self.activate_mouse_mode()

    def create_button(self, icon_path, tooltip, on_click):
        button = QPushButton(QIcon(icon_path), "")
        button.setToolTip(tooltip)
        button.clicked.connect(on_click)
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(24, 24))
        return button

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Esc"), self, self.activate_mouse_mode)
        QShortcut(QKeySequence("P"), self, self.select_pen)
        QShortcut(QKeySequence("H"), self, self.select_highlighter)
        QShortcut(QKeySequence("E"), self, self.select_eraser)
        QShortcut(QKeySequence("L"), self, self.select_line)
        QShortcut(QKeySequence("R"), self, self.select_rectangle)
        QShortcut(QKeySequence("C"), self, self.select_ellipse)
        QShortcut(QKeySequence("T"), self, self.select_text)
        QShortcut(QKeySequence("S"), self, self.canvas.take_screenshot_with_annotations)
        QShortcut(QKeySequence("W"), self, self.toggle_whiteboard)
        QShortcut(QKeySequence("B"), self, self.toggle_blackboard)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self, self.canvas.undo)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Y), self, self.canvas.redo)

    def _enter_drawing_mode(self):
        self.is_drawing_mode = True
        for button in self.tool_buttons:
            button.setEnabled(True)

    def activate_draw_mode(self):
        self._enter_drawing_mode()
        self.canvas.prepare_for_screenshot()

    def activate_mouse_mode(self):
        self.is_drawing_mode = False
        for button in self.tool_buttons:
            button.setEnabled(False)
        self.canvas.enter_mouse_mode()

    def toggle_whiteboard(self):
        self._enter_drawing_mode()
        self.canvas.prepare_for_solid_background(QColor(255, 255, 255, 255))

    def toggle_blackboard(self):
        self._enter_drawing_mode()
        self.canvas.prepare_for_solid_background(QColor(0, 0, 0, 255))

    def select_pen(self): self.current_tool = "pen"
    def select_highlighter(self): self.current_tool = "highlighter"
    def select_eraser(self): self.current_tool = "eraser"
    def select_line(self): self.current_tool = "line"
    def select_rectangle(self): self.current_tool = "rectangle"
    def select_ellipse(self): self.current_tool = "ellipse"

    def select_text(self):
        self.current_tool = "text"
        self.canvas.hide()
        font, ok = QFontDialog.getFont(self.font, self)
        self.canvas.show()
        if ok:
            self.font = font

    def select_color(self):
        self.canvas.hide()
        new_color = QColorDialog.getColor(self.color)
        self.canvas.show()
        if new_color.isValid():
            self.color = new_color

    def change_thickness(self, value):
        self.thickness = value

    def close_app(self):
        self.canvas.close()
        self.close()
        QApplication.quit()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

class TextDialog(QDialog):
    """A dialog for entering text annotations."""
    def __init__(self, parent=None, font=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Text")
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        if font:
            self.text_edit.setCurrentFont(font)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_text(self):
        return self.text_edit.toPlainText()

    @staticmethod
    def getText(parent=None, font=None):
        dialog = TextDialog(parent, font)
        result = dialog.exec_()
        text = dialog.get_text()
        return text, result == QDialog.Accepted

def create_dummy_icons():
    """Creates placeholder icons if the 'icons' directory or files are missing."""
    if not os.path.exists("icons"):
        os.makedirs("icons")

    icon_map = {
        "pen.png": "P", "highlighter.png": "H", "eraser.png": "E", "line.png": "/",
        "rectangle.png": "口", "ellipse.png": "O", "text.png": "T", "color.png": "🎨",
        "undo.png": "↶", "redo.png": "↷", "clear.png": "X", "screenshot.png": "📷",
        "whiteboard.png": "W", "blackboard.png": "B", "exit.png": "⏏",
        "mouse.png": "🐁", "draw.png": "✏️"
    }

    for name, text in icon_map.items():
        path = os.path.join("icons", name)
        if not os.path.exists(path):
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor("lightgrey"))
            painter = QPainter(pixmap)
            painter.setPen(Qt.black)
            font = QFont()
            font.setPointSize(16)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
            painter.end()
            pixmap.save(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    create_dummy_icons()

    main_window = DrawingCanvas(None)
    toolbar = Toolbar(main_window)
    main_window.toolbar = toolbar
    
    toolbar.show()

    sys.exit(app.exec_())