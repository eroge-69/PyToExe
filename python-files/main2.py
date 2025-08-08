import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, Qt

# Esta función es vital para que PyInstaller encuentre los archivos
# de recursos como 'screen.ico' después de la compilación.
def resource_path(relative_path):
    """Obtiene la ruta absoluta de un recurso, funciona en modo de desarrollo y con PyInstaller."""
    try:
        # PyInstaller crea una carpeta temporal y la almacena en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En modo de desarrollo, la ruta base es el directorio actual
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WebApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DWService - Login")
        
        # El icono se carga usando la función resource_path.
        # Asegúrate de que el archivo 'screen.ico' esté en el mismo
        # directorio que tu script de Python antes de compilar.
        self.setWindowIcon(QIcon(resource_path("screen.ico")))
        
        self.setGeometry(100, 100, 1024, 768)
        self.windows = []

    def closeEvent(self, event):
        for window in self.windows:
            window.close()
        event.accept()

class CustomWebEngineView(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

    def createWindow(self, type):
        new_window = QMainWindow()
        new_browser = CustomWebEngineView(self.main_window)
        new_window.setCentralWidget(new_browser)
        new_window.setWindowTitle("DWService")
        
        main_geometry = self.main_window.geometry()
        new_window.setGeometry(main_geometry)

        self.main_window.windows.append(new_window)
        new_window.setAttribute(Qt.WA_DeleteOnClose)
        new_window.destroyed.connect(lambda: self.main_window.windows.remove(new_window))

        new_window.show()
        return new_browser

if __name__ == '__main__':
    # Usar sys.frozen para detectar si el script se está ejecutando desde un
    # ejecutable de PyInstaller, lo cual es útil para la depuración.
    if getattr(sys, 'frozen', False):
        print("Ejecutando desde PyInstaller")
    else:
        print("Ejecutando en modo de desarrollo")

    app = QApplication(sys.argv)
    main_window = WebApp()
    browser = CustomWebEngineView(main_window)
    browser.setUrl(QUrl("https://access.dwservice.net/login.dw?localeid=es#s"))
    main_window.setCentralWidget(browser)
    main_window.show()
    sys.exit(app.exec_())
