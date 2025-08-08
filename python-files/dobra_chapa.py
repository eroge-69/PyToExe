import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
import ezdxf

class SheetMetalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dobrador de Chapa Metálica v1.0")
        self.setGeometry(100, 100, 400, 300)
        
        # Widgets
        self.length_input = QLineEdit(placeholderText="Comprimento (mm)")
        self.width_input = QLineEdit(placeholderText="Largura (mm)")
        self.thickness_input = QLineEdit(placeholderText="Espessura (mm)")
        self.bend_angle_input = QLineEdit(placeholderText="Ângulo (graus)")
        self.bend_radius_input = QLineEdit(placeholderText="Raio (mm)")
        self.k_factor_input = QLineEdit(placeholderText="K-Factor (0.44 padrão)")
        self.calculate_button = QPushButton("Calcular e Exportar DXF")
        self.result_label = QLabel("Resultado aparecerá aqui.")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dimensões da Chapa:"))
        layout.addWidget(self.length_input)
        layout.addWidget(self.width_input)
        layout.addWidget(self.thickness_input)
        layout.addWidget(QLabel("\nParâmetros de Dobra:"))
        layout.addWidget(self.bend_angle_input)
        layout.addWidget(self.bend_radius_input)
        layout.addWidget(self.k_factor_input)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.result_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Conexão do botão
        self.calculate_button.clicked.connect(self.calculate_and_export)

    def calculate_bend_allowance(self, angle_deg, radius, thickness, k_factor):
        angle_rad = math.radians(angle_deg)
        return angle_rad * (radius + k_factor * thickness)

    def calculate_and_export(self):
        try:
            # Coleta dados
            length = float(self.length_input.text())
            width = float(self.width_input.text())
            thickness = float(self.thickness_input.text())
            angle = float(self.bend_angle_input.text())
            radius = float(self.bend_radius_input.text())
            k_factor = float(self.k_factor_input.text() or 0.44)  # Default 0.44
            
            # Cálculo do desenvolvimento
            bend_allowance = self.calculate_bend_allowance(angle, radius, thickness, k_factor)
            total_length = length + bend_allowance
            
            # Cria DXF
            doc = ezdxf.new()
            msp = doc.modelspace()
            msp.add_lwpolyline([(0, 0), (total_length, 0), (total_length, width), (0, width), (0, 0)])
            doc.saveas("planificacao.dxf")
            
            self.result_label.setText(f"Planificação salva como 'planificacao.dxf'!\nComprimento desenvolvido: {total_length:.2f} mm")
            QMessageBox.information(self, "Sucesso", "Arquivo DXF gerado com sucesso!")
        except ValueError:
            QMessageBox.critical(self, "Erro", "Dados inválidos! Verifique os números.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SheetMetalApp()
    window.show()
    sys.exit(app.exec_())