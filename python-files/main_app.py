import subprocess
import sys
import os
import threading
import streamlit as st
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import pandas as pd

# Flag para verificar se o Streamlit já foi iniciado
streamlit_running = False

# Função para carregar e limpar os dados
@st.cache_data
def load_data(path):
    df = pd.read_excel(
        path,
        sheet_name="Controle",
        header=5  # Cabeçalho real está na linha 6
    )
    
    # Remover colunas "Unnamed"
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Garantir que 'Status' seja numérico
    df['Status'] = pd.to_numeric(df['Status'], errors='coerce')

    # Mapear status numérico para texto + emoji
    status_map = {
        3: "✅ Finalizado",
        2: "⚠️ Pendente Implementação",
        1: "❌ Aguardando Disposição"
    }
    df['Status'] = df['Status'].map(status_map)

    # Converter coluna de data
    df['Data da Emissão'] = pd.to_datetime(df['Data da Emissão'], errors='coerce')

    # Criar colunas auxiliares para mês
    df['Mês_Num'] = df['Data da Emissão'].dt.month

    # Mapear o número do mês para o nome do mês (abreviado)
    meses = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['Mês'] = df['Mês_Num'].map(meses)

    return df

# Função para iniciar o Streamlit no subprocesso
def run_streamlit():
    global streamlit_running
    if not streamlit_running:
        # Caminho para o executável do Streamlit
        # Assumindo que o executável está na mesma pasta "dist" do mainapp.exe
        executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_rnc.exe")
        
        # Inicia o executável do dashboard como um subprocesso
        subprocess.Popen([executable_path])
        
        # Definir a flag como True para impedir a reinicialização
        streamlit_running = True

# Criando a interface gráfica com PyQt5
class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Janela principal
        self.setWindowTitle("Dashboard RNC 2025")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("your_icon_path.png"))  # Substitua pelo caminho do ícone

        # Layout principal
        layout = QVBoxLayout()

        # Estilo da fonte
        title_font = QFont("Arial", 24, QFont.Bold)

        # Título
        self.title_label = QLabel("📊 Controle de RNC's - Dashboard 2025", self)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Espaçamento
        layout.addStretch()

        # Botão para iniciar o Streamlit
        self.start_button = QPushButton("Iniciar Dashboard", self)
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 10px; padding: 10px;")
        self.start_button.setFixedHeight(50)
        self.start_button.clicked.connect(self.run_streamlit_action)
        layout.addWidget(self.start_button)

        # Espaçamento inferior
        layout.addStretch()

        # Configuração do layout
        self.setLayout(layout)

    def run_streamlit_action(self):
        threading.Thread(target=run_streamlit, daemon=True).start()

# Função principal
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MyApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
