import sys
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidget, 
                            QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, 
                            QLabel, QProgressBar, QStatusBar)
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QDesktopServices, QPixmap, QImage
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import requests

class ThumbnailLoader(QThread):
    """Thread para carregar thumbnails de forma assíncrona"""
    thumbnail_loaded = pyqtSignal(int, QPixmap)
    progress_updated = pyqtSignal(int, int)  # current, total
    
    def __init__(self, thumbnail_data):
        super().__init__()
        self.thumbnail_data = thumbnail_data  # Lista de (row, url)
        self.session = requests.Session()
        # Configurar timeout e headers para otimizar requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def run(self):
        total = len(self.thumbnail_data)
        
        # Usar ThreadPoolExecutor para carregar múltiplas thumbnails simultaneamente
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_row = {
                executor.submit(self.load_thumbnail, url): row 
                for row, url in self.thumbnail_data if url
            }
            
            completed = 0
            for future in as_completed(future_to_row):
                row = future_to_row[future]
                completed += 1
                
                try:
                    pixmap = future.result(timeout=10)
                    if pixmap:
                        self.thumbnail_loaded.emit(row, pixmap)
                except Exception as e:
                    print(f"Erro ao carregar thumbnail da linha {row}: {e}")
                
                self.progress_updated.emit(completed, total)
    
    @lru_cache(maxsize=100)
    def load_thumbnail(self, url):
        """Carrega uma thumbnail com cache"""
        try:
            response = self.session.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                image_data = response.content
                image = QImage.fromData(image_data)
                if not image.isNull():
                    # Redimensionar para economizar memória
                    image = image.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Erro ao carregar thumbnail {url}: {e}")
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.thumbnail_loader = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configuração da interface otimizada"""
        self.setWindowTitle("Visualizador de JSONs do YouTube por Comquister")
        self.setGeometry(100, 100, 1405, 720)

        # Configurar tabela com otimizações
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Video ID", "Published At", "Title", "Description", "Thumbnail", "Availability"
        ])

        # Otimizações da tabela
        self.table_widget.verticalHeader().setDefaultSectionSize(100)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Definir larguras das colunas
        column_widths = [120, 150, 250, 300, 160, 100]
        for i, width in enumerate(column_widths):
            self.table_widget.setColumnWidth(i, width)

        # Otimizações de performance da tabela
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Menu
        self.setup_menu()

        # Conectar sinais
        self.table_widget.cellClicked.connect(self.open_youtube)

    def setup_menu(self):
        """Configurar menu"""
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("Arquivo")

        open_action = self.file_menu.addAction("Abrir JSON")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = self.file_menu.addAction("Salvar Excel")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

    def open_file(self):
        """Abrir arquivo JSON com otimizações"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Abrir arquivo JSON", "", "Arquivos JSON (*.json)"
        )

        if file_path:
            self.status_bar.showMessage("Carregando arquivo...")
            self.setWindowTitle(f"Visualizador de JSONs do YouTube - {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                QTimer.singleShot(10, lambda: self.display_data(data))
                
            except Exception as e:
                self.status_bar.showMessage(f"Erro ao carregar arquivo: {str(e)}")

    def display_data(self, data):
        """Exibir dados de forma otimizada"""
        if not data:
            return

        self.status_bar.showMessage("Processando dados...")
        
        # Limpar tabela anterior
        self.table_widget.clearContents()
        self.table_widget.setRowCount(len(data))

        thumbnail_data = []  # Para carregar thumbnails depois

        # Processar dados básicos rapidamente
        for i, item in enumerate(data):
            try:
                video_id = item['contentDetails']['videoId']
                published_at = item['contentDetails'].get('videoPublishedAt', 'N/A')
                title = item['snippet']['title']
                description = item['snippet'].get('description', 'N/A')
                
                # Truncar descrição longa para melhor performance
                if len(description) > 200:
                    description = description[:200] + "..."
                
                thumbnail_url = item['snippet'].get('thumbnails', {}).get('maxres', {}).get('url', '')
                if not thumbnail_url:
                    # Tentar outras resoluções
                    thumbnails = item['snippet'].get('thumbnails', {})
                    for res in ['high', 'medium', 'default']:
                        if res in thumbnails:
                            thumbnail_url = thumbnails[res]['url']
                            break

                availability = 'Disponível' if 'videoId' in item['contentDetails'] else 'Não disponível'

                # Criar items da tabela
                video_id_item = QTableWidgetItem(video_id)
                video_id_item.setTextAlignment(Qt.AlignCenter)
                video_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                published_at_item = QTableWidgetItem(published_at)
                title_item = QTableWidgetItem(title)
                description_item = QTableWidgetItem(description)
                availability_item = QTableWidgetItem(availability)

                # Adicionar items à tabela
                self.table_widget.setItem(i, 0, video_id_item)
                self.table_widget.setItem(i, 1, published_at_item)
                self.table_widget.setItem(i, 2, title_item)
                self.table_widget.setItem(i, 3, description_item)
                self.table_widget.setItem(i, 5, availability_item)

                # Adicionar placeholder para thumbnail
                thumbnail_label = QLabel("Carregando...")
                thumbnail_label.setAlignment(Qt.AlignCenter)
                thumbnail_label.setStyleSheet("QLabel { color: gray; }")
                self.table_widget.setCellWidget(i, 4, thumbnail_label)

                # Guardar dados da thumbnail para carregar depois
                if thumbnail_url:
                    thumbnail_data.append((i, thumbnail_url))

            except Exception as e:
                print(f"Erro ao processar item {i}: {e}")
                continue

        self.status_bar.showMessage(f"Dados carregados: {len(data)} vídeos")
        
        # Iniciar carregamento das thumbnails
        if thumbnail_data:
            self.load_thumbnails(thumbnail_data)

    def load_thumbnails(self, thumbnail_data):
        """Carregar thumbnails de forma assíncrona"""
        if self.thumbnail_loader and self.thumbnail_loader.isRunning():
            self.thumbnail_loader.terminate()

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(thumbnail_data))
        self.progress_bar.setValue(0)

        self.thumbnail_loader = ThumbnailLoader(thumbnail_data)
        self.thumbnail_loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
        self.thumbnail_loader.progress_updated.connect(self.on_progress_updated)
        self.thumbnail_loader.finished.connect(self.on_thumbnails_finished)
        self.thumbnail_loader.start()

    def on_thumbnail_loaded(self, row, pixmap):
        """Callback quando uma thumbnail é carregada"""
        thumbnail_label = QLabel()
        thumbnail_label.setPixmap(pixmap)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setScaledContents(True)
        thumbnail_label.setFixedSize(150, 100)
        self.table_widget.setCellWidget(row, 4, thumbnail_label)

    def on_progress_updated(self, current, total):
        """Atualizar barra de progresso"""
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Carregando thumbnails: {current}/{total}")

    def on_thumbnails_finished(self):
        """Callback quando todas as thumbnails foram processadas"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Thumbnails carregadas")

    def open_youtube(self, row, column):
        """Abrir vídeo no YouTube"""
        if column == 0:  # Coluna Video ID
            video_id_item = self.table_widget.item(row, column)
            if video_id_item:
                video_id = video_id_item.text()
                url = f"https://www.youtube.com/watch?v={video_id}"
                QDesktopServices.openUrl(QUrl(url))

    def save_file(self):
        """Salvar dados em Excel"""
        if self.table_widget.rowCount() == 0:
            self.status_bar.showMessage("Nenhum dado para salvar")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Salvar arquivo Excel", "", "Arquivos Excel (*.xlsx)"
        )

        if file_path:
            try:
                self.status_bar.showMessage("Salvando arquivo...")
                df = self.get_table_data()
                df.to_excel(file_path, index=False)
                self.status_bar.showMessage(f"Arquivo salvo: {file_path}")
            except Exception as e:
                self.status_bar.showMessage(f"Erro ao salvar: {str(e)}")

    def get_table_data(self):
        """Extrair dados da tabela para DataFrame"""
        columns = ["Video ID", "Published At", "Title", "Description", "Availability"]
        data = []

        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in [0, 1, 2, 3, 5]:  # Pular coluna thumbnail
                item = self.table_widget.item(row, col)
                row_data.append(item.text() if item else '')
            data.append(row_data)

        return pd.DataFrame(data, columns=columns)

    def closeEvent(self, event):
        """Limpar recursos ao fechar"""
        if self.thumbnail_loader and self.thumbnail_loader.isRunning():
            self.thumbnail_loader.terminate()
            self.thumbnail_loader.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Otimizações da aplicação
    app.setStyle('Fusion')  # Style mais rápido
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())