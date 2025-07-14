import sys
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QFileDialog, QAbstractItemView
)
from PyQt5.QtCore import Qt

class TrinkerPro(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Eletronica Vargas - Sistema Profissional de Assistência Técnica')
        self.setGeometry(100, 100, 1200, 700)
        self.os_counter = 1

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Header
        header = QLabel('Eletronica Vargas - Sistema Profissional de Assistência Técnica')
        header.setStyleSheet(
            'font-size: 22pt; font-weight: bold; color: #ffffff; background-color: #0056b3; padding: 15px; border-radius: 5px;'
        )
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Form layout
        form_layout = QHBoxLayout()
        self.inputs = {}
        fields = [
            ('Número Cliente', 'Ex: 12345'),
            ('Cliente', 'Nome completo'),
            ('Telefone', 'Ex: (11) 99999-9999'),
            ('Email', 'Ex: cliente@email.com'),
            ('Equipamento', 'Ex: Notebook, Celular'),
            ('Acessórios Recebidos', 'Ex: Carregador, Cabo'),
            ('Defeito', 'Descrição do problema'),
            ('Diagnóstico Técnico', 'Ex: Tela com problema'),
            ('Previsão de Entrega', 'dd/mm/aaaa'),
            ('Valor', 'R$ 0,00'),
        ]

        for field, placeholder in fields:
            col = QVBoxLayout()
            label = QLabel(field)
            label.setStyleSheet('font-weight: 600;')
            entry = QLineEdit()
            entry.setPlaceholderText(placeholder)
            self.inputs[field] = entry
            col.addWidget(label)
            col.addWidget(entry)
            form_layout.addLayout(col)

        main_layout.addLayout(form_layout)

        # Buttons: Criar OS
        btn_create = QPushButton('Criar OS')
        btn_create.setStyleSheet(
            'background-color: #007acc; color: white; font-weight: bold; padding: 10px; border-radius: 5px;'
        )
        btn_create.setFixedWidth(150)
        btn_create.clicked.connect(self.create_os)
        main_layout.addWidget(btn_create, alignment=Qt.AlignLeft)

        # Table for OS
        self.table = QTableWidget(0, len(fields) + 3)
        headers = ['Nº OS'] + [f[0] for f in fields] + ['Status', 'Data Criação']
        self.table.setHorizontalHeaderLabels(headers)

        # Permitir edição apenas em colunas específicas:
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet('font-size: 10pt;')

        # Ajusta larguras colunas
        self.table.setColumnWidth(0, 60)  # Nº OS
        self.table.setColumnWidth(len(headers) - 2, 130)  # Status
        self.table.setColumnWidth(len(headers) - 1, 150)  # Data Criação

        main_layout.addWidget(self.table)

        # Controls: Status Combo + Buttons
        control_layout = QHBoxLayout()

        self.status_combo = QComboBox()
        self.status_combo.addItems(['Em Análise', 'Em Manutenção', 'Aguardando Peça', 'Finalizado', 'Entregue', 'Cancelado'])
        self.status_combo.setFixedWidth(180)
        control_layout.addWidget(QLabel('Atualizar Status para:'))
        control_layout.addWidget(self.status_combo)

        btn_update_status = QPushButton('Atualizar Status')
        btn_update_status.setStyleSheet(
            'background-color: #28a745; color: white; font-weight: bold; padding: 8px; border-radius: 5px;'
        )
        btn_update_status.clicked.connect(self.update_status)
        control_layout.addWidget(btn_update_status)

        btn_export_csv = QPushButton('Exportar CSV')
        btn_export_csv.setStyleSheet(
            'background-color: #17a2b8; color: white; font-weight: bold; padding: 8px; border-radius: 5px;'
        )
        btn_export_csv.clicked.connect(self.export_csv)
        control_layout.addWidget(btn_export_csv)

        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_os(self):
        # Validação: Cliente, Equipamento e Defeito são obrigatórios
        cliente = self.inputs['Cliente'].text().strip()
        equipamento = self.inputs['Equipamento'].text().strip()
        defeito = self.inputs['Defeito'].text().strip()

        if not cliente or not equipamento or not defeito:
            QMessageBox.warning(self, 'Erro', 'Preencha os campos obrigatórios: Cliente, Equipamento e Defeito.')
            return

        # Coleta dados do formulário
        data = [self.inputs[field].text().strip() for field in self.inputs]

        data_criacao = datetime.now().strftime('%d/%m/%Y %H:%M')
        row_data = [self.os_counter] + data + ['Em Análise', data_criacao]

        self.add_table_row(row_data)
        self.os_counter += 1

        # Limpar campos após criar OS
        for field in self.inputs:
            self.inputs[field].clear()

        QMessageBox.information(self, 'Sucesso', 'Ordem de Serviço criada com sucesso!')

    def add_table_row(self, row_data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col, item in enumerate(row_data):
            cell = QTableWidgetItem(str(item))
            # Bloqueia edição da coluna Nº OS e Data Criação
            if col == 0 or col == self.table.columnCount() - 1:
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                cell.setTextAlignment(Qt.AlignCenter)
            else:
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row_position, col, cell)

    def update_status(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Erro', 'Selecione uma OS para atualizar o status.')
            return
        status = self.status_combo.currentText()
        col_status = len(self.inputs) + 1  # coluna de status
        self.table.setItem(selected, col_status, QTableWidgetItem(status))
        QMessageBox.information(self, 'Status Atualizado', f'Status da OS atualizado para: {status}')

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Salvar CSV', '', 'Arquivos CSV (*.csv)')
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    headers = ['Nº OS'] + list(self.inputs.keys()) + ['Status', 'Data Criação']
                    writer.writerow(headers)

                    for row in range(self.table.rowCount()):
                        row_data = [
                            self.table.item(row, col).text() if self.table.item(row, col) else ''
                            for col in range(self.table.columnCount())
                        ]
                        writer.writerow(row_data)

                QMessageBox.information(self, 'Exportado', f'Arquivo exportado com sucesso em:\n{path}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Falha ao exportar arquivo:\n{str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrinkerPro()
    window.show()
    sys.exit(app.exec_())