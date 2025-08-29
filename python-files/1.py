import sys
import math
import os
from dataclasses import dataclass
from typing import List, Dict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
                             QSpinBox, QDoubleSpinBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

@dataclass
class DuctSection:
    """Класс для участка воздуховода"""
    diameter: float
    length: float
    roughness: float = 0.0001
    zeta_local: float = 0.0

@dataclass
class VentilationBranch:
    """Класс для ответвления вентиляционной сети"""
    name: str
    sections: List[DuctSection]
    density: float = 1.2
    
    def calculate_resistance(self, flow_rate_m3s: float) -> float:
        total_resistance = 0.0
        
        for section in self.sections:
            area = math.pi * (section.diameter / 2) ** 2
            velocity = flow_rate_m3s / area if area > 0 else 0
            
            dynamic_viscosity = 1.8e-5
            Re = (velocity * section.diameter) / dynamic_viscosity if dynamic_viscosity > 0 else 0
            
            if Re > 0:
                lambda_friction = 0.11 * (section.roughness/section.diameter + 68/Re) ** 0.25
            else:
                lambda_friction = 0.02
            
            friction_loss = lambda_friction * (section.length / section.diameter) * (self.density * velocity ** 2) / 2
            local_loss = section.zeta_local * (self.density * velocity ** 2) / 2
            
            total_resistance += friction_loss + local_loss
        
        if flow_rate_m3s > 0:
            k = total_resistance / (flow_rate_m3s ** 2)
        else:
            k = 0
            
        return k
    
    def calculate_pressure_loss(self, flow_rate_m3s: float) -> float:
        k = self.calculate_resistance(flow_rate_m3s)
        return k * (flow_rate_m3s ** 2)

class VentilationSystem:
    def __init__(self, total_flow_m3h: float, air_density: float = 1.2):
        self.total_flow_m3h = total_flow_m3h
        self.total_flow_m3s = total_flow_m3h / 3600
        self.air_density = air_density
        self.branches = []
        self.collecting_duct = None
    
    def add_branch(self, branch: VentilationBranch):
        self.branches.append(branch)
    
    def set_collecting_duct(self, duct_section: DuctSection):
        self.collecting_duct = duct_section
    
    def calculate_flow_distribution(self, max_iterations: int = 50, tolerance: float = 1e-6):
        if len(self.branches) != 2:
            raise ValueError("Метод реализован для двух ответвлений")
        
        Q1_m3s = self.total_flow_m3s / 2
        Q2_m3s = self.total_flow_m3s / 2
        
        log = []
        log.append("Начинаем расчет распределения расходов...")
        log.append(f"Общий расход: {self.total_flow_m3h:.1f} м³/ч")
        log.append(f"Плотность воздуха: {self.air_density:.3f} кг/м³")
        
        for iteration in range(max_iterations):
            ΔP1 = self.branches[0].calculate_pressure_loss(Q1_m3s)
            ΔP2 = self.branches[1].calculate_pressure_loss(Q2_m3s)
            
            pressure_diff = abs(ΔP1 - ΔP2)
            if pressure_diff < tolerance:
                log.append(f"✅ Система сошлась за {iteration + 1} итераций!")
                break
            
            if iteration < 3:
                log.append(f"Итерация {iteration + 1}: Q1={Q1_m3s*3600:.1f} м³/ч, Q2={Q2_m3s*3600:.1f} м³/ч")
            
            if ΔP1 > ΔP2:
                Q1_new_m3s = Q1_m3s * math.sqrt(ΔP2 / ΔP1)
                Q2_new_m3s = self.total_flow_m3s - Q1_new_m3s
            else:
                Q2_new_m3s = Q2_m3s * math.sqrt(ΔP1 / ΔP2)
                Q1_new_m3s = self.total_flow_m3s - Q2_new_m3s
            
            Q1_m3s, Q2_m3s = Q1_new_m3s, Q2_new_m3s
        
        return {
            self.branches[0].name: Q1_m3s,
            self.branches[1].name: Q2_m3s
        }, log
    
    def calculate_total_pressure_loss(self, flows: Dict[str, float]) -> float:
        branch_losses = []
        for branch in self.branches:
            flow_m3s = flows[branch.name]
            loss = branch.calculate_pressure_loss(flow_m3s)
            branch_losses.append(loss)
        
        collector_loss = 0
        if self.collecting_duct:
            collector_branch = VentilationBranch("Сборный", [self.collecting_duct], self.air_density)
            collector_loss = collector_branch.calculate_pressure_loss(self.total_flow_m3s)
        
        return max(branch_losses) + collector_loss

class SectionInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Диаметр (мм):"))
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(50, 1000)
        self.diameter_input.setValue(200)
        layout.addWidget(self.diameter_input)
        
        layout.addWidget(QLabel("Длина (м):"))
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0.1, 100)
        self.length_input.setValue(10.0)
        layout.addWidget(self.length_input)
        
        layout.addWidget(QLabel("КМС (ζ):"))
        self.zeta_input = QDoubleSpinBox()
        self.zeta_input.setRange(0, 100)
        self.zeta_input.setValue(2.5)
        layout.addWidget(self.zeta_input)
        
        self.setLayout(layout)
    
    def get_section(self):
        return DuctSection(
            diameter=self.diameter_input.value() / 1000,
            length=self.length_input.value(),
            zeta_local=self.zeta_input.value()
        )

class VentilationCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор вентиляционной сети")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.setup_ui()
    
    def setup_ui(self):
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Вкладка ввода
        self.input_tab = QWidget()
        self.tabs.addTab(self.input_tab, "Ввод данных")
        self.setup_input_tab()
        
        # Вкладка результатов
        self.results_tab = QWidget()
        self.tabs.addTab(self.results_tab, "Результаты")
        self.setup_results_tab()
        
        # Кнопка расчета
        self.calculate_btn = QPushButton("Рассчитать")
        self.calculate_btn.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_btn)
    
    def setup_input_tab(self):
        layout = QVBoxLayout(self.input_tab)
        
        # Основные параметры
        main_group = QGroupBox("Основные параметры")
        main_layout = QVBoxLayout()
        
        main_layout.addWidget(QLabel("Общий расход (м³/ч):"))
        self.total_flow_input = QDoubleSpinBox()
        self.total_flow_input.setRange(100, 10000)
        self.total_flow_input.setValue(1800)
        main_layout.addWidget(self.total_flow_input)
        
        main_layout.addWidget(QLabel("Плотность воздуха (кг/м³):"))
        self.density_input = QDoubleSpinBox()
        self.density_input.setRange(0.8, 1.3)
        self.density_input.setValue(1.2)
        main_layout.addWidget(self.density_input)
        
        main_layout.addWidget(QLabel("Макс. итераций:"))
        self.max_iter_input = QSpinBox()
        self.max_iter_input.setRange(10, 500)
        self.max_iter_input.setValue(100)
        main_layout.addWidget(self.max_iter_input)
        
        main_layout.addWidget(QLabel("Точность (Па):"))
        self.tolerance_input = QDoubleSpinBox()
        self.tolerance_input.setRange(0.0001, 1.0)
        self.tolerance_input.setValue(0.001)
        main_layout.addWidget(self.tolerance_input)
        
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        
        # Ответвления
        branches_group = QGroupBox("Ответвления")
        branches_layout = QVBoxLayout()
        
        branches_layout.addWidget(QLabel("Ответвление 1:"))
        self.branch1_section = SectionInputWidget()
        branches_layout.addWidget(self.branch1_section)
        
        branches_layout.addWidget(QLabel("Ответвление 2:"))
        self.branch2_section = SectionInputWidget()
        branches_layout.addWidget(self.branch2_section)
        
        branches_group.setLayout(branches_layout)
        layout.addWidget(branches_group)
        
        # Сборный воздуховод
        collector_group = QGroupBox("Сборный воздуховод")
        collector_layout = QVBoxLayout()
        self.collector_section = SectionInputWidget()
        collector_layout.addWidget(self.collector_section)
        collector_group.setLayout(collector_layout)
        layout.addWidget(collector_group)
    
    def setup_results_tab(self):
        layout = QVBoxLayout(self.results_tab)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
    
    def calculate(self):
        try:
            total_flow = self.total_flow_input.value()
            air_density = self.density_input.value()
            max_iterations = self.max_iter_input.value()
            tolerance = self.tolerance_input.value()
            
            system = VentilationSystem(total_flow, air_density)
            
            # Создаем ответвления
            branch1 = VentilationBranch(
                "Ответвление 1",
                [self.branch1_section.get_section()],
                air_density
            )
            
            branch2 = VentilationBranch(
                "Ответвление 2",
                [self.branch2_section.get_section()],
                air_density
            )
            
            system.add_branch(branch1)
            system.add_branch(branch2)
            
            # Сборный воздуховод
            system.set_collecting_duct(self.collector_section.get_section())
            
            # Расчет
            flows, log = system.calculate_flow_distribution(max_iterations, tolerance)
            total_pressure = system.calculate_total_pressure_loss(flows)
            
            # Вывод результатов
            result_text = "РЕЗУЛЬТАТЫ РАСЧЕТА\n"
            result_text += "=" * 50 + "\n"
            
            for branch_name, flow_m3s in flows.items():
                flow_m3h = flow_m3s * 3600
                result_text += f"\n{branch_name}:\n"
                result_text += f"  Расход: {flow_m3h:.1f} м³/ч\n"
                result_text += f"  Доля: {flow_m3s/system.total_flow_m3s*100:.1f}%\n"
            
            result_text += f"\nОбщие потери давления: {total_pressure:.2f} Па\n"
            result_text += f"Требуемое давление вентилятора: {total_pressure:.2f} Па\n"
            
            self.results_text.setText(result_text)
            self.tabs.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расчета: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = VentilationCalculator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()