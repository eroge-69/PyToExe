import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import Qt, QSettings, QPoint, QSize, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>White-Blue Glow Bar</title>
<style>
  body { margin: 0; background: black; }
  #glow-bar { position: fixed; top: 0; left: 0; height: 100%; width: 100%; overflow: hidden; }
  .glow {
    position: absolute;
    top: 0;
    left: -25%;
    height: 100%;
    width: 25%;
    background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,1), rgba(0,153,255,1), rgba(255,255,255,0));
    box-shadow: 0 0 15px #ffffff, 0 0 30px #0099ff, 0 0 50px #ffffff;
    border-radius: 50%;
    animation: animeMove 5s infinite ease-in-out;
  }
  .glow2 { animation-delay: 2.5s; }
  @keyframes animeMove {
    0% { left: -30%; transform: scaleX(0.8); opacity: 0; }
    10% { opacity: 1; transform: scaleX(1); }
    50% { left: 100%; opacity: 1; transform: scaleX(1.2); }
    60% { opacity: 0; transform: scaleX(0.8); }
    100% { left: 100%; opacity: 0; }
  }
</style>
</head>
<body>
<div id="glow-bar">
  <div class="glow"></div>
  <div class="glow glow2"></div>
</div>
</body>
</html>
"""

class GlowBar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "GlowBarApp")
        self.locked = self.settings.value("locked", False, type=bool)

        # Web view for HTML animation
        self.view = QWebEngineView()
        self.view.setHtml(HTML)
        self.setCentralWidget(self.view)

        # Remove window frame & make transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Restore last position & size
        self.resize(self.settings.value("size", QSize(800, 4)))
        self.move(self.settings.value("pos", QPoint(100, 100)))

        # Right-click context menu
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)

        # Dragging variables
        self.dragging = False

    def show_context_menu(self, pos):
        menu = QMenu(self)

        lock_action = QAction("Unlock" if self.locked else "Lock", self)
        lock_action.triggered.connect(self.toggle_lock)
        menu.addAction(lock_action)

        inc_action = QAction("Increase Bar Size", self)
        inc_action.triggered.connect(self.increase_size)
        menu.addAction(inc_action)

        dec_action = QAction("Decrease Bar Size", self)
        dec_action.triggered.connect(self.decrease_size)
        menu.addAction(dec_action)

        menu.exec_(self.mapToGlobal(pos))

    def toggle_lock(self):
        self.locked = not self.locked
        self.settings.setValue("locked", self.locked)

    def increase_size(self):
        size = self.size()
        self.resize(size.width(), size.height() + 5)
        self.settings.setValue("size", self.size())

    def decrease_size(self):
        size = self.size()
        if size.height() > 5:
            self.resize(size.width(), size.height() - 5)
            self.settings.setValue("size", self.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.locked:
            self.dragging = True
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and not self.locked:
            self.move(event.globalPos() - self.drag_start)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.settings.setValue("pos", self.pos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GlowBar()
    window.show()
    sys.exit(app.exec_())
