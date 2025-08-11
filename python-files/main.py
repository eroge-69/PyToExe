import sys
from PyQt5.QtWidgets import QApplication
from database import DatabaseManager  # Importar explícitamente para forzar inicialización
from main_window import MainWindow

def inicializar_sistema():
    ## Inicializa la base de datos antes de crear la aplicación
    print("Inicializando base de datos...")
    db = DatabaseManager()
    print("Base de datos lista")

def main():
    # Inicializar primero la base de datos
    inicializar_sistema()
    
    # Ahora crear la aplicación
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()