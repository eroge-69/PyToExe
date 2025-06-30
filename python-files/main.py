from PySide6.QtWidgets import QMainWindow, QApplication

from controlador_pagina_inicial import Inicio
from controlador_pagina_simulacion import ControladorSimulacion
   
app = QApplication([])
ventana = Inicio()
ventana.show()
app.exec()