import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QLineEdit, QTextEdit, QComboBox, QDateEdit,
                             QMessageBox, QHeaderView, QGroupBox, QSplitter,
                             QFormLayout, QStatusBar, QToolBar, QAction)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import random

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Dashboard de Controle Operacional")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # KPIs
        kpi_layout = QHBoxLayout()
        
        # KPI 1 - Ordens em Aberto
        kpi1 = QGroupBox("Ordens em Aberto")
        kpi1_layout = QVBoxLayout()
        kpi1_value = QLabel("24")
        kpi1_value.setFont(QFont("Arial", 24, QFont.Bold))
        kpi1_value.setAlignment(Qt.AlignCenter)
        kpi1_layout.addWidget(kpi1_value)
        kpi1.setLayout(kpi1_layout)
        kpi_layout.addWidget(kpi1)
        
        # KPI 2 - Concluídas Hoje
        kpi2 = QGroupBox("Concluídas Hoje")
        kpi2_layout = QVBoxLayout()
        kpi2_value = QLabel("8")
        kpi2_value.setFont(QFont("Arial", 24, QFont.Bold))
        kpi2_value.setAlignment(Qt.AlignCenter)
        kpi2_layout.addWidget(kpi2_value)
        kpi2.setLayout(kpi2_layout)
        kpi_layout.addWidget(kpi2)
        
        # KPI 3 - Atrasos
        kpi3 = QGroupBox("Ordens Atrasadas")
        kpi3_layout = QVBoxLayout()
        kpi3_value = QLabel("3")
        kpi3_value.setFont(QFont("Arial", 24, QFont.Bold))
        kpi3_value.setAlignment(Qt.AlignCenter)
        kpi3_value.setStyleSheet("color: red;")
        kpi3_layout.addWidget(kpi3_value)
        kpi3.setLayout(kpi3_layout)
        kpi_layout.addWidget(kpi3)
        
        # KPI 4 - Eficiência
        kpi4 = QGroupBox("Eficiência (%)")
        kpi4_layout = QVBoxLayout()
        kpi4_value = QLabel("87%")
        kpi4_value.setFont(QFont("Arial", 24, QFont.Bold))
        kpi4_value.setAlignment(Qt.AlignCenter)
        kpi4_value.setStyleSheet("color: green;")
        kpi4_layout.addWidget(kpi4_value)
        kpi4.setLayout(kpi4_layout)
        kpi_layout.addWidget(kpi4)
        
        layout.addLayout(kpi_layout)
        
        # Gráficos
        charts_layout = QHBoxLayout()
        
        # Gráfico 1 - Status das Ordens
        chart1_group = QGroupBox("Status das Ordens de Serviço")
        chart1_layout = QVBoxLayout()
        self.status_chart = FigureCanvas(Figure(figsize=(5, 4)))
        chart1_layout.addWidget(self.status_chart)
        self.plot_status_chart()
        chart1_group.setLayout(chart1_layout)
        charts_layout.addWidget(chart1_group)
        
        # Gráfico 2 - Desempenho Semanal
        chart2_group = QGroupBox("Desempenho Semanal")
        chart2_layout = QVBoxLayout()
        self.performance_chart = FigureCanvas(Figure(figsize=(5, 4)))
        chart2_layout.addWidget(self.performance_chart)
        self.plot_performance_chart()
        chart2_group.setLayout(chart2_layout)
        charts_layout.addWidget(chart2_group)
        
        layout.addLayout(charts_layout)
        
        self.setLayout(layout)
    
    def plot_status_chart(self):
        figure = self.status_chart.figure
        figure.clear()
        ax = figure.add_subplot(111)
        
        status = ['Abertas', 'Em Andamento', 'Concluídas', 'Atrasadas']
        values = [24, 15, 8, 3]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        ax.pie(values, labels=status, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        self.status_chart.draw()
    
    def plot_performance_chart(self):
        figure = self.performance_chart.figure
        figure.clear()
        ax = figure.add_subplot(111)
        
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        planned = [20, 22, 20, 23, 24, 12]
        completed = [18, 20, 19, 21, 22, 10]
        
        ax.plot(days, planned, 'b-', label='Planejado')
        ax.plot(days, completed, 'g-', label='Realizado')
        ax.set_xlabel('Dia da Semana')
        ax.set_ylabel('Ordens de Serviço')
        ax.legend()
        ax.grid(True)
        
        self.performance_chart.draw()

class OrdensServicoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        title = QLabel("Ordens de Serviço")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        btn_nova_os = QPushButton("Nova OS")
        btn_nova_os.clicked.connect(self.nova_os)
        header_layout.addWidget(btn_nova_os)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Cliente", "Descrição", "Status", "Data Início", "Data Prevista"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        # Dados de exemplo
        data = [
            [1001, "Cliente A", "Manutenção Preventiva", "Em Andamento", "10/05/2023", "15/05/2023"],
            [1002, "Cliente B", "Reparo Equipamento", "Concluída", "05/05/2023", "10/05/2023"],
            [1003, "Cliente C", "Instalação Nova", "Aberta", "12/05/2023", "18/05/2023"],
            [1004, "Cliente D", "Calibração", "Atrasada", "01/05/2023", "05/05/2023"],
            [1005, "Cliente E", "Troca de Peças", "Em Andamento", "08/05/2023", "12/05/2023"]
        ]
        
        self.table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # Colorir baseado no status
                if col == 3:  # Coluna de status
                    if value == "Atrasada":
                        item.setBackground(QColor(255, 200, 200))
                    elif value == "Concluída":
                        item.setBackground(QColor(200, 255, 200))
                    elif value == "Em Andamento":
                        item.setBackground(QColor(200, 200, 255))
                
                self.table.setItem(row, col, item)
    
    def nova_os(self):
        dialog = NovaOSDialog(self)
        if dialog.exec_():
            # Aqui você adicionaria a nova OS ao banco de dados
            QMessageBox.information(self, "Sucesso", "Nova OS criada com sucesso!")

class EquipesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        title = QLabel("Gestão de Equipes")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Tabela de equipes
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Equipe", "Líder", "Membros", "OSs Ativas"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        data = [
            ["Equipe Alpha", "João Silva", "5", "3"],
            ["Equipe Beta", "Maria Santos", "4", "2"],
            ["Equipe Gama", "Pedro Costa", "6", "4"],
            ["Equipe Delta", "Ana Oliveira", "5", "3"]
        ]
        
        self.table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

class RelatoriosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        title = QLabel("Relatórios e Analytics")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Botões de relatório
        report_layout = QGridLayout()
        
        btn_diario = QPushButton("Relatório Diário")
        btn_diario.clicked.connect(lambda: self.gerar_relatorio("diário"))
        report_layout.addWidget(btn_diario, 0, 0)
        
        btn_semanal = QPushButton("Relatório Semanal")
        btn_semanal.clicked.connect(lambda: self.gerar_relatorio("semanal"))
        report_layout.addWidget(btn_semanal, 0, 1)
        
        btn_mensal = QPushButton("Relatório Mensal")
        btn_mensal.clicked.connect(lambda: self.gerar_relatorio("mensal"))
        report_layout.addWidget(btn_mensal, 1, 0)
        
        btn_equipes = QPushButton("Desempenho de Equipes")
        btn_equipes.clicked.connect(lambda: self.gerar_relatorio("equipes"))
        report_layout.addWidget(btn_equipes, 1, 1)
        
        layout.addLayout(report_layout)
        
        # Área de visualização do relatório
        self.relatorio_text = QTextEdit()
        self.relatorio_text.setPlaceholderText("Selecione um relatório para visualizar...")
        layout.addWidget(self.relatorio_text)
        
        self.setLayout(layout)
    
    def gerar_relatorio(self, tipo):
        if tipo == "diário":
            texto = self.gerar_relatorio_diario()
        elif tipo == "semanal":
            texto = self.gerar_relatorio_semanal()
        elif tipo == "mensal":
            texto = self.gerar_relatorio_mensal()
        else:
            texto = self.gerar_relatorio_equipes()
        
        self.relatorio_text.setHtml(texto)
    
    def gerar_relatorio_diario(self):
        return """
        <h2>Relatório Diário - {data}</h2>
        <h3>Resumo</h3>
        <ul>
            <li>Ordens abertas: 5</li>
            <li>Ordens concluídas: 8</li>
            <li>Ordens em andamento: 15</li>
            <li>Ordens atrasadas: 3</li>
        </ul>
        <h3>Principais atividades</h3>
        <ol>
            <li>Manutenção preventiva no setor A</li>
            <li>Reparo da máquina X concluído</li>
            <li>Instalação nova no setor B em andamento</li>
        </ol>
        """.format(data=datetime.now().strftime("%d/%m/%Y"))
    
    def gerar_relatorio_semanal(self):
        return """
        <h2>Relatório Semanal - Semana 20</h2>
        <h3>Métricas</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Metrica</th>
                <th>Valor</th>
                <th>Variação vs Semana Anterior</th>
            </tr>
            <tr>
                <td>Ordens Concluídas</td>
                <td>42</td>
                <td style="color: green;">+5%</td>
            </tr>
            <tr>
                <td>Eficiência</td>
                <td>87%</td>
                <td style="color: green;">+2%</td>
            </tr>
            <tr>
                <td>Ordens Atrasadas</td>
                <td>5</td>
                <td style="color: red;">+1</td>
            </tr>
        </table>
        """
    
    def gerar_relatorio_mensal(self):
        return """
        <h2>Relatório Mensal - Maio/2023</h2>
        <h3>Visão Geral</h3>
        <p>O mês de maio apresentou um bom desempenho operacional, com aumento de 8% na produtividade
        em comparação com o mês anterior. A taxa de conclusão de ordens de serviço foi de 92%, 
        superando a meta estabelecida de 90%.</p>
        
        <h3>Estatísticas Principais</h3>
        <ul>
            <li>Total de ordens recebidas: 185</li>
            <li>Ordens concluídas: 170</li>
            <li>Taxa de conclusão: 92%</li>
            <li>Tempo médio de conclusão: 3.2 dias</li>
            <li>Ordens com atraso: 15</li>
        </ul>
        """
    
    def gerar_relatorio_equipes(self):
        return """
        <h2>Desempenho por Equipe - Maio/2023</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Equipe</th>
                <th>Ordens Concluídas</th>
                <th>Tempo Médio (dias)</th>
                <th>Eficiência</th>
                <th>Avaliação</th>
            </tr>
            <tr>
                <td>Equipe Alpha</td>
                <td>45</td>
                <td>2.8</td>
                <td>94%</td>
                <td>Excelente</td>
            </tr>
            <tr>
                <td>Equipe Beta</td>
                <td>42</td>
                <td>3.1</td>
                <td>91%</td>
                <td>Bom</td>
            </tr>
            <tr>
                <td>Equipe Gama</td>
                <td>40</td>
                <td>3.5</td>
                <td>88%</td>
                <td>Bom</td>
            </tr>
            <tr>
                <td>Equipe Delta</td>
                <td>43</td>
                <td>3.0</td>
                <td>90%</td>
                <td>Bom</td>
            </tr>
        </table>
        """

class NovaOSDialog(QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Nova Ordem de Serviço")
        
        # Criar um widget personalizado para o diálogo
        self.widget = QWidget()
        layout = QFormLayout()
        
        self.cliente_input = QLineEdit()
        layout.addRow("Cliente:", self.cliente_input)
        
        self.descricao_input = QTextEdit()
        self.descricao_input.setMaximumHeight(100)
        layout.addRow("Descrição:", self.descricao_input)
        
        self.prioridade_combo = QComboBox()
        self.prioridade_combo.addItems(["Baixa", "Média", "Alta", "Urgente"])
        layout.addRow("Prioridade:", self.prioridade_combo)
        
        self.data_prevista = QDateEdit()
        self.data_prevista.setDate(QDate.currentDate().addDays(7))
        layout.addRow("Data Prevista:", self.data_prevista)
        
        self.equipe_combo = QComboBox()
        self.equipe_combo.addItems(["Equipe Alpha", "Equipe Beta", "Equipe Gama", "Equipe Delta"])
        layout.addRow("Equipe:", self.equipe_combo)
        
        self.widget.setLayout(layout)
        self.layout().addWidget(self.widget, 0, 0, 1, self.layout().columnCount())
        
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Sistema de Controle Operacional")
        self.setGeometry(100, 100, 1200, 800)
        
        # Barra de ferramentas
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Ações da barra de ferramentas
        dashboard_action = QAction(QIcon(), "Dashboard", self)
        dashboard_action.triggered.connect(self.show_dashboard)
        toolbar.addAction(dashboard_action)
        
        os_action = QAction(QIcon(), "Ordens de Serviço", self)
        os_action.triggered.connect(self.show_ordens_servico)
        toolbar.addAction(os_action)
        
        equipes_action = QAction(QIcon(), "Equipes", self)
        equipes_action.triggered.connect(self.show_equipes)
        toolbar.addAction(equipes_action)
        
        relatorios_action = QAction(QIcon(), "Relatórios", self)
        relatorios_action.triggered.connect(self.show_relatorios)
        toolbar.addAction(relatorios_action)
        
        # Widget central com abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Adicionar as abas
        self.dashboard_tab = DashboardWidget()
        self.os_tab = OrdensServicoWidget()
        self.equipes_tab = EquipesWidget()
        self.relatorios_tab = RelatoriosWidget()
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.os_tab, "Ordens de Serviço")
        self.tabs.addTab(self.equipes_tab, "Equipes")
        self.tabs.addTab(self.relatorios_tab, "Relatórios")
        
        # Barra de status
        self.statusBar().showMessage("Sistema carregado com sucesso")
        
    def show_dashboard(self):
        self.tabs.setCurrentIndex(0)
        
    def show_ordens_servico(self):
        self.tabs.setCurrentIndex(1)
        
    def show_equipes(self):
        self.tabs.setCurrentIndex(2)
        
    def show_relatorios(self):
        self.tabs.setCurrentIndex(3)

def main():
    app = QApplication(sys.argv)
    
    # Estilo básico
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()