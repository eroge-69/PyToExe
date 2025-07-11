import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.optimize import fsolve


class EstimadorFuncion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estimador de función - Regresión progresiva")
        self.setGeometry(100, 100, 900, 600)

        self.datos_x = []
        self.datos_fx = []
        self.objetivo = None
        self.x_sugerido = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Objetivo
        objetivo_layout = QHBoxLayout()
        objetivo_layout.addWidget(QLabel("Valor objetivo f(x):"))
        self.input_objetivo = QLineEdit()
        self.input_objetivo.textChanged.connect(self.set_objetivo)
        objetivo_layout.addWidget(self.input_objetivo)
        layout.addLayout(objetivo_layout)

        # Ingreso de punto
        punto_layout = QHBoxLayout()
        punto_layout.addWidget(QLabel("x:"))
        self.input_x = QLineEdit()
        punto_layout.addWidget(self.input_x)

        punto_layout.addWidget(QLabel("f(x):"))
        self.input_fx = QLineEdit()
        punto_layout.addWidget(self.input_fx)

        self.btn_agregar = QPushButton("Agregar punto")
        self.btn_agregar.clicked.connect(self.agregar_punto)
        punto_layout.addWidget(self.btn_agregar)

        layout.addLayout(punto_layout)

        # Tabla de puntos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["x", "f(x)", "Error", "Próximo x sugerido"])
        layout.addWidget(self.tabla)

        # Gráfico
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def set_objetivo(self):
        try:
            texto = self.input_objetivo.text()
            if texto.strip() == "":
                return
            self.objetivo = float(texto)
        except ValueError:
            self.objetivo = None

    def agregar_punto(self):
        try:
            x = float(self.input_x.text())
            fx = float(self.input_fx.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos para x y f(x).")
            return

        self.datos_x.append(x)
        self.datos_fx.append(fx)

        self.input_x.clear()
        self.input_fx.clear()

        self.calcular_prediccion()
        self.actualizar_tabla()
        self.actualizar_grafico()

    def calcular_prediccion(self):
        self.x_sugerido = None
        self.prediccion_funcion = None

        if self.objetivo is None or len(self.datos_x) < 2:
            return

        x_array = np.array(self.datos_x)
        fx_array = np.array(self.datos_fx)

        # Seleccionar puntos según lógica mejorada
        if len(x_array) >= 5:
            errores = np.abs(fx_array - self.objetivo)
            indices_mejores = np.argsort(errores)[:5]
            x_seleccionados = x_array[indices_mejores]
            fx_seleccionados = fx_array[indices_mejores]
            grado = 3  # siempre cúbico con 5 mejores puntos
        else:
            x_seleccionados = x_array
            fx_seleccionados = fx_array
            grado = min(len(x_seleccionados) - 1, 3)

        try:
            coef = np.polyfit(x_seleccionados, fx_seleccionados, grado)
            p = np.poly1d(coef)
            def funcion_objetivo(x): return p(x) - self.objetivo

            x0 = x_seleccionados[np.argmin(np.abs(fx_seleccionados - self.objetivo))]
            self.x_sugerido = fsolve(funcion_objetivo, x0 + 0.1)[0]
            self.prediccion_funcion = p
        except Exception as e:
            self.x_sugerido = None
            self.prediccion_funcion = None
            QMessageBox.critical(self, "Error", f"No se pudo calcular predicción: {e}")

    def actualizar_tabla(self):
        self.tabla.setRowCount(0)
        for i in range(len(self.datos_x)):
            x = self.datos_x[i]
            fx = self.datos_fx[i]
            error = abs(fx - self.objetivo) if self.objetivo is not None else "-"
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(round(x, 6))))
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(round(fx, 6))))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(round(error, 6)) if error != "-" else "-"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(round(self.x_sugerido, 6)) if self.x_sugerido is not None else "-"))

    def actualizar_grafico(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.grid(True)
        ax.set_title("Puntos evaluados y curva de ajuste")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")

        if len(self.datos_x) == 0:
            self.canvas.draw()
            return

        ax.scatter(self.datos_x, self.datos_fx, color='blue', label='Puntos ingresados')

        if self.prediccion_funcion is not None:
            x_vals = np.linspace(min(self.datos_x) - 1, max(self.datos_x) + 1, 500)
            y_vals = self.prediccion_funcion(x_vals)
            ax.plot(x_vals, y_vals, 'r--', label=f'Ajuste polinómico')

            if self.x_sugerido is not None:
                y_sug = self.prediccion_funcion(self.x_sugerido)
                ax.plot(self.x_sugerido, y_sug, 'go', label=f"x próximo ≈ {round(self.x_sugerido, 4)}")

        ax.legend()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = EstimadorFuncion()
    ventana.show()
    sys.exit(app.exec_())
