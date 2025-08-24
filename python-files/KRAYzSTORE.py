import sys
import os
import requests
import shutil
import zipfile
import subprocess
import tempfile
import time
import platform
import webbrowser
import atexit

from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QLabel,
                             QLineEdit, QPushButton, QProgressBar, QMessageBox, QVBoxLayout,
                             QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QDialog, QComboBox,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEasingCurve, QPropertyAnimation, QUrl, QRect
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette, QMovie, QDesktopServices, QPainter, QBrush, QLinearGradient


# Only import winreg if on Windows
if platform.system() == "Windows":
    import winreg

# --- Global Style Constants for Glassmorphism & Theming (NEW WHITE THEME) ---
WHITE_THEME_COLORS = {
    "BACKGROUND_BASE": "#F5F5F5", # Very Light Gray for the deepest background
    "GLASS_BACKGROUND": "#FFFFFF", # Semi-transparent white for glass effect
    "GLASS_BORDER": "rgba(180, 180, 180, 0.2)", # Slightly darker transparent for borders
    "PRIMARY_GRADIENT_START": "#0DA2AD", # Darker Purple
    "PRIMARY_GRADIENT_END": "#007ACC", # Darker Blue
    "SECONDARY_GRADIENT_START": "#C0C0C0", # Silver for secondary buttons
    "SECONDARY_GRADIENT_END": "#A0A0A0", # Gray for secondary buttons
    "CANCEL_GRADIENT_START": "#7FFFFB", # Light Red for a faint effect
    "CANCEL_GRADIENT_END": "#4C76FF", # A bit more red
    "TEXT": "#000000", # Dark Gray for general text
    "SUBTLE_TEXT": "#606060", # Medium Gray for hints/secondary text
    "ERROR": "#CC0000", # Darker Red
    "SUCCESS": "#61C0FF", # Darker Green
    "FOREGROUND_COLOR": "rgba(240, 240, 240, 0.9)", # Used for combo box dropdowns etc.
}

DALTONISM_MODES = {
    "Normal": {},
    "Protanopia": { # Reduced sensitivity to red light
        "PRIMARY_ADJ_START": "#4B0082", # Indigo
        "PRIMARY_ADJ_END": "#1E90FF", # Dodger Blue
        "TEXT_ADJ": "#404040", # Slightly darker gray for readability on light
        "SUBTLE_TEXT_ADJ": "#707070",
    },
    "Deuteranopia": { # Reduced sensitivity to green light
        "PRIMARY_ADJ_START": "#8B008B", # Dark Magenta
        "PRIMARY_ADJ_END": "#87CEFA", # Light Sky Blue
        "TEXT_ADJ": "#303030",
        "SUBTLE_TEXT_ADJ": "#606060",
    },
    "Tritanopia": { # Reduced sensitivity to blue light
        "PRIMARY_ADJ_START": "#FF69B4", # Hot Pink
        "PRIMARY_ADJ_END": "#3CB371", # Medium Sea Green
        "TEXT_ADJ": "#404040",
        "SUBTLE_TEXT_ADJ": "#707070",
    }
}

FONT_FAMILY = "Segoe UI"
FONT_SIZE_TITLE = 36
FONT_SIZE_HEADING = 24
FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12

GLASS_BOX_SHADOW = "0px 8px 20px rgba(0, 0, 0, 0.2)" # Lighter shadow for white theme

class UrlFetchThread(QThread):
    url_fetched = pyqtSignal(str)
    url_fetch_error = pyqtSignal(str, str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.max_retries = 3
        self.retry_delay = 5

    def run(self):
        for attempt in range(self.max_retries):
            try:
                print(f"Tentativa {attempt + 1}/{self.max_retries} para buscar a URL de: {self.url}")
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

                # Assuming the response content is the URL string itself
                url_content = response.text.strip()
                if not url_content.startswith(('http://', 'https://')):
                    raise ValueError("A URL obtida não é válida.")
                
                self.url_fetched.emit(url_content)
                return # Success, exit the thread
            
            except requests.exceptions.HTTPError as e:
                msg = f"Erro HTTP {e.response.status_code} ao buscar a URL: {e.response.reason}"
                print(msg)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.url_fetch_error.emit(msg, "Erro na Busca da URL")
            except requests.exceptions.ConnectionError as e:
                msg = f"Erro de Conexão: Verifique sua internet. {e}"
                print(msg)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.url_fetch_error.emit(msg, "Erro de Conexão")
            except Exception as e:
                msg = f"Erro inesperado ao buscar a URL: {e}"
                print(msg)
                self.url_fetch_error.emit(msg, "Erro Inesperado")
                return


class DownloadThread(QThread):
    update_progress = pyqtSignal(int)
    update_status_message = pyqtSignal(str)
    download_complete = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str, str)
    download_started = pyqtSignal()

    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination
        self._is_running = True
        self._is_paused = False # Added for pausing functionality
        self.max_retries = 3
        self.retry_delay = 5

    def run(self):
        self.download_started.emit()
        self.update_status_message.emit("AGUARDE...")

        for attempt in range(self.max_retries):
            if not self._is_running:
                # The file is not removed here anymore, the main thread will handle it
                self.update_status_message.emit("Download cancelado.")
                self.download_complete.emit(False, "Download cancelado pelo usuário.")
                return

            try:
                print(f"Tentativa {attempt + 1}/{self.max_retries} para baixar de: {self.url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
                    'Referer': "https://www.mediafire.com/"
                }

                with requests.get(self.url, stream=True, headers=headers, timeout=60) as response:
                    response.raise_for_status()

                    total_size = int(response.headers.get('content-length', 0))
                    if total_size == 0:
                        raise ValueError("Arquivo de tamanho zero ou URL inválida. Não foi possível determinar o tamanho do arquivo.")

                    downloaded = 0
                    with open(self.destination, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            # Handle pausing logic
                            while self._is_paused and self._is_running:
                                self.update_status_message.emit("Download pausado...")
                                QThread.msleep(100) # Sleep for a short period to keep UI responsive
                                QApplication.processEvents() # Process events to avoid UI freeze
                            
                            if not self._is_running:
                                f.close()
                                self.update_status_message.emit("Download cancelado pelo usuário.")
                                self.download_complete.emit(False, "Download cancelado pelo usuário.")
                                return
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = int((downloaded / total_size) * 100)
                            self.update_progress.emit(progress)
                            self.update_status_message.emit(f"({downloaded / (1024*1024):.2f}MB de {total_size / (1024*1024):.2f}MB)")

                self.download_complete.emit(True, "Download concluído com sucesso!")
                return

            except requests.exceptions.HTTPError as e:
                msg = f"Erro HTTP {e.response.status_code} ao baixar: {e.response.reason}"
                print(msg)
                if attempt < self.max_retries - 1:
                    self.update_status_message.emit(f"{msg}. Tentando novamente em {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    self.error_occurred.emit(f"Falha no download após {self.max_retries} tentativas: {msg}", "Erro no Download")
                    self.download_complete.emit(False, msg)
            except requests.exceptions.ConnectionError as e:
                msg = f"Erro de conexão: Verifique sua internet. {e}"
                print(msg)
                if attempt < self.max_retries - 1:
                    self.update_status_message.emit(f"{msg}. Tentando novamente em {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    self.error_occurred.emit(f"Falha no download após {self.max_retries} tentativas: {msg}", "Erro de Conexão")
                    self.download_complete.emit(False, msg)
            except requests.exceptions.Timeout:
                msg = "Tempo limite da requisição excedido ao baixar. O servidor demorou muito para responder."
                print(msg)
                if attempt < self.max_retries - 1:
                    self.update_status_message.emit(f"{msg}. Tentando novamente em {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    self.error_occurred.emit(f"Falha no download após {self.max_retries} tentativas: {msg}", "Tempo Limite Excedido")
                    self.download_complete.emit(False, msg)
            except ValueError as e:
                msg = f"Erro de arquivo: {e}"
                print(msg)
                self.error_occurred.emit(msg, "Erro no Arquivo")
                self.download_complete.emit(False, msg)
                return
            except Exception as e:
                msg = f"Erro inesperado no download: {e}"
                print(msg)
                if attempt < self.max_retries - 1:
                    self.update_status_message.emit(f"{msg}. Tentando novamente em {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    self.error_occurred.emit(f"Falha no download após {self.max_retries} tentativas: {msg}", "Erro Inesperado")
                    self.download_complete.emit(False, msg)

    def stop(self):
        """Signals the thread to stop its operation gracefully."""
        self._is_running = False

    def pause(self):
        """Pauses the download process."""
        self._is_paused = True

    def resume(self):
        """Resumes the download process."""
        self._is_paused = False

class ActivationThread(QThread):
    progress_update = pyqtSignal(str)
    activation_complete = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str, str)
    requires_admin = pyqtSignal()

    def __init__(self, zip_path, temp_dir):
        super().__init__()
        self.zip_path = zip_path
        self.temp_dir = temp_dir # Temporary directory where the ZIP was downloaded and will be extracted

    def run(self):
        extract_target_dir = None # Initialize to None
        try:
            self.progress_update.emit("Ativando...")
            if not zipfile.is_zipfile(self.zip_path):
                self.error_occurred.emit("O arquivo baixado não é válido.", "Erro")
                self.activation_complete.emit(False, "Arquivo inválido.")
                return

            # Determine the effective root folder after extraction
            # Extract to a subfolder within temp_dir to avoid clutter
            extract_target_dir = os.path.join(self.temp_dir, "extracted_krayz_content")
            os.makedirs(extract_target_dir, exist_ok=True)

            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    member_path = os.path.join(extract_target_dir, member)
                    # Basic security check to prevent path traversal
                    if not os.path.normpath(member_path).startswith(os.path.normpath(extract_target_dir)):
                        self.error_occurred.emit(f"Aviso de segurança: Caminho inválido: {member}", "Erro de Segurança")
                        self.activation_complete.emit(False, "Conteúdo suspeito.")
                        return
                zip_ref.extractall(extract_target_dir)

            self.progress_update.emit("Jogos Adicionados")
            if not self.find_steam_paths():
                self.error_occurred.emit(
                    "Não foi possível localizar o caminho da Steam no registro. Certifique-se de que a Steam está instalada e configurada corretamente.",
                    "Steam Não Encontrada"
                )
                self.activation_complete.emit(False, "Steam não encontrada.")
                return

            self.progress_update.emit("Fechando Steam...")
            self.stop_steam()
            time.sleep(2) # Give Steam a moment to close

            self.progress_update.emit("Aplicando Jogos...")
            self.remove_steam_cache()

            # --- NEW ADDITION: DELETE THE ZIP FILE AFTER SUCCESSFUL COPY ---
            self.progress_update.emit("Limpando arquivos temporários de download...")
            if os.path.exists(self.zip_path):
                try:
                    os.remove(self.zip_path)
                    print(f"Removed downloaded zip file: {self.zip_path}")
                except Exception as e:
                    print(f"Warning: Could not remove downloaded zip file '{self.zip_path}': {e}")
                    self.progress_update.emit(f"Aviso: Não foi possível remover o arquivo de download: {e}")
            # ----------------------------------------------------------------

            self.progress_update.emit("Otimizando biblioteca (limpando cache temporário)...")
            self.optimize_steam_library()

            self.progress_update.emit("Reiniciando Steam...")
            self.start_steam()
            time.sleep(3) # Give Steam a moment to start

            self.activation_complete.emit(True, "Ativação concluída com sucesso! Verifique sua biblioteca Steam.")

        except zipfile.BadZipFile:
            self.error_occurred.emit("O arquivo baixado não é válido ou está corrompido.", "ZIP Inválido")
            self.activation_complete.emit(False, "Arquivo corrompido.")
        except Exception as e:
            # Esta exceção agora capturará erros de permissão de acesso
            self.error_occurred.emit(f"Erro inesperado durante a ativação: {str(e)}", "Erro de Ativação")
            self.activation_complete.emit(False, f"Erro inesperado: {str(e)}")
        finally:
            # Clean up extracted content in temp_dir after activation attempt
            if extract_target_dir and os.path.exists(extract_target_dir):
                shutil.rmtree(extract_target_dir, ignore_errors=True)
                print(f"Extracted content directory '{extract_target_dir}' cleaned.")

    def is_admin(self):
        # Mantenha o método, mas ele não será mais chamado no método run().
        try:
            return os.getuid() == 0 # Linux/macOS
        except AttributeError:
            import ctypes
            try:
                return ctypes.windll.shell32.IsUserAdmin() != 0 # Windows
            except:
                return False # Not admin, or some other error

    def find_steam_paths(self):
        if platform.system() == "Windows":
            try:
                # Open the Steam registry key
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                self.steam_exe, _ = winreg.QueryValueEx(key, "SteamExe")
                winreg.CloseKey(key)

                self.steam_dir = os.path.dirname(self.steam_exe)
                self.config_dir = os.path.join(self.steam_dir, "config")

                print(f"Steam Executable: {self.steam_exe}")
                print(f"Steam Directory: {self.steam_dir}")
                print(f"Config Directory: {self.config_dir}")

                if not os.path.exists(self.steam_exe) or not os.path.exists(self.config_dir):
                    raise FileNotFoundError("Steam paths found in registry but do not exist on disk.")
                return True
            except Exception as e:
                print(f"Erro ao encontrar Steam: {e}")
                return False
        else:
            self.error_occurred.emit("Este ativador suporta apenas sistemas Windows.", "Sistema Operacional Não Suportado")
            return False

    def stop_steam(self):
        if platform.system() == "Windows":
            try:
                # Terminate Steam process using taskkill (more robust than powershell for quick kill)
                subprocess.run(["taskkill", "/f", "/im", "steam.exe"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                print(f"Erro ao tentar fechar a Steam: {e}")
        # Add logic for other OS if supported in future

    def remove_steam_cache(self):
        # This part implements the rmdir /s /q functionality
        paths_to_remove = [
            os.path.join(self.config_dir, "depotcache"),
            os.path.join(self.config_dir, "stplug-in")
        ]
        for path in paths_to_remove:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    self.progress_update.emit(f"Atualizando: {os.path.basename(path)}")
                except Exception as e:
                    self.progress_update.emit(f"Aviso: Não foi possível {os.path.basename(path)}: {e}")

    def copy_activation_files(self, extracted_source_dir):
        # Corresponds to:
        # xcopy /e /i /y "%temp%\krayz_temp\Config\*" "%configDir%\" >nul
        # copy /y "%temp%\krayz_temp\Hid.dll" "%steamDir%\" >nul

        source_config_dir = os.path.join(extracted_source_dir, "Config")
        source_hid_dll = os.path.join(extracted_source_dir, "Hid.dll") # Assuming Hid.dll is directly in the extracted root

        if os.path.exists(source_config_dir) and os.path.isdir(source_config_dir):
            try:
                # Use distutils.dir_util.copy_tree for xcopy /e /i /y equivalent
                # shutil.copytree requires destination to not exist, so copy individual files
                # Or use custom recursive copy logic
                for root, dirs, files in os.walk(source_config_dir):
                    relative_path = os.path.relpath(root, source_config_dir)
                    dest_dir = os.path.join(self.config_dir, relative_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    for file in files:
                        shutil.copy2(os.path.join(root, file), os.path.join(dest_dir, file))
                self.progress_update.emit("Arquivos de configuração copiados.")
            except Exception as e:
                self.error_occurred.emit(f"Erro ao copiar arquivos de configuração: {e}", "Erro de Cópia")
                raise # Re-raise to trigger parent error handling

        if os.path.exists(source_hid_dll):
            try:
                shutil.copy2(source_hid_dll, self.steam_dir)
                self.progress_update.emit("Hid.dll copiada.")
            except Exception as e:
                self.error_occurred.emit(f"Erro ao copiar Hid.dll: {e}", "Erro de Cópia")
                raise

    def optimize_steam_library(self):
        # This part implements cleaning cache:
        # "%steamDir%\cache", "%steamDir%\temp", "%steamDir%\tmp", "*.tmp", "*.bak"
        # The *.tmp and *.bak are more complex, will focus on directories.
        folders_to_clean = [
            os.path.join(self.steam_dir, "cache"),
            os.path.join(self.steam_dir, "temp"),
            os.path.join(self.steam_dir, "tmp")
        ]

        for folder in folders_to_clean:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    self.progress_update.emit(f"Limpado: {os.path.basename(folder)}")
                except Exception as e:
                    self.progress_update.emit(f"Aviso: Não foi possível limpar {os.path.basename(folder)}: {e}")

        # For *.tmp and *.bak files within steamDir, we can iterate
        # This can be heavy, but let's try for the top level.
        try:
            for item in os.listdir(self.steam_dir):
                item_path = os.path.join(self.steam_dir, item)
                if os.path.isfile(item_path) and (item.lower().endswith(".tmp") or item.lower().endswith(".bak")):
                    try:
                        os.remove(item_path)
                        self.progress_update.emit(f"Limpado arquivo temporário: {item}")
                    except Exception as e:
                        self.progress_update.emit(f"Aviso: Não foi possível remover {item}: {e}")
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários no diretório Steam: {e}")

    def start_steam(self):
        if self.steam_exe and os.path.exists(self.steam_exe):
            try:
                subprocess.Popen([self.steam_exe], creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
            except Exception as e:
                self.error_occurred.emit(f"Não foi possível iniciar a Steam: {e}", "Erro de Inicialização")
        else:
            self.error_occurred.emit("Caminho do executável da Steam não encontrado ou inválido.", "Erro de Inicialização")

class StyledButton(QPushButton):
    def __init__(self, text, primary=True, parent=None, colors=WHITE_THEME_COLORS,
                 custom_gradient_start=None, custom_gradient_end=None):
        super().__init__(text, parent)
        self.colors = colors
        self.setFont(QFont(FONT_FAMILY, FONT_SIZE_NORMAL, QFont.Bold if primary else QFont.Normal))
        self.setFixedSize(300, 55)
        self.primary = primary
        self.custom_gradient_start = custom_gradient_start
        self.custom_gradient_end = custom_gradient_end
        self.set_shadow_effect()
        self.update_style()

    def set_colors(self, colors):
        self.colors = colors
        self.update_style()

    def set_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 90)) # Slightly lighter shadow for white theme
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)

    def update_style(self):
        if self.custom_gradient_start and self.custom_gradient_end:
            start_color = self.custom_gradient_start
            end_color = self.custom_gradient_end
            text_color = "white"
            hover_start = self.custom_gradient_end
            hover_end = self.custom_gradient_start
        elif self.primary:
            start_color = self.colors['PRIMARY_GRADIENT_START']
            end_color = self.colors['PRIMARY_GRADIENT_END']
            text_color = "white"
            hover_start = self.colors['PRIMARY_GRADIENT_END']
            hover_end = self.colors['PRIMARY_GRADIENT_START']
        else: # Secondary gradient
            start_color = self.colors['SECONDARY_GRADIENT_START']
            end_color = self.colors['SECONDARY_GRADIENT_END']
            text_color = self.colors['TEXT']
            hover_start = self.colors['SECONDARY_GRADIENT_END']
            hover_end = self.colors['SECONDARY_GRADIENT_START']

        self.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {self.colors['GLASS_BORDER']};
                border-radius: 12px;
                padding: 12px 25px;
                font-weight: bold;
                color: {text_color};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {start_color}, stop:1 {end_color});
                transition: all 0.2s ease-in-out;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {start_color}, stop:1 {end_color});
                border: 2px solid rgba(255, 255, 255, 0.5); /* Lighter border on press */
            }}
            QPushButton:disabled {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(150, 150, 150, 0.7), stop:1 rgba(100, 100, 100, 0.7));
                color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(13, 180, 180, 0.3);
            }}
        """)


class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder="", echo_mode=QLineEdit.Normal, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__(placeholder, parent)
        self.colors = colors
        self.setPlaceholderText(placeholder)
        self.setEchoMode(echo_mode)
        self.setFont(QFont(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.setFixedSize(300, 50)
        self.set_shadow_effect()
        self.update_style()

    def set_colors(self, colors):
        self.colors = colors
        self.update_style()

    def set_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60)) # Lighter shadow for white theme
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def update_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['GLASS_BACKGROUND']};
                color: {self.colors['TEXT']};
                border: 1px solid {self.colors['GLASS_BORDER']};
                border-radius: 12px;
                padding: 10px;
                selection-background-color: {self.colors['PRIMARY_GRADIENT_START']}; /* Use primary gradient for selection */
                selection-color: white;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['PRIMARY_GRADIENT_START']};
                background-color: rgba(240, 240, 240, 0.8); /* Slightly less transparent white on focus */
            }}
        """)

class WelcomePage(QWidget):
    start_app = pyqtSignal() # Changed from start_animation

    def __init__(self, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__(parent)
        self.parent = parent # MainWindow
        self.colors = colors
        self.setup_ui()
        self.update_style()

    def set_colors(self, colors):
        self.colors = colors
        self.update_style()
        self.findChild(StyledButton, "start_btn").set_colors(self.colors)

    def update_style(self):
        self.findChild(QLabel, "title_label").setStyleSheet(f"color: {self.colors['PRIMARY_GRADIENT_START']}; background-color: transparent;")
        self.findChild(QLabel, "subtitle_label").setStyleSheet(f"color: {self.colors['TEXT']}; background-color: transparent;")
        self.findChild(QLabel, "footer_label").setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']}; background-color: transparent;")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(60, 60, 60, 60)

        main_layout.addStretch(1)

        title_label = QLabel("KRAYz STORE")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_TITLE, QFont.ExtraBold))
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Bem-Vindo ao Ativador Oficial")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING))
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(40)

        start_btn = StyledButton("INICIAR", primary=True, parent=self, colors=self.colors)
        start_btn.setObjectName("start_btn")
        start_btn.clicked.connect(self.start_app.emit) # Connect to new signal
        main_layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        main_layout.addStretch(1)

        footer_label = QLabel("Desenvolvido por @Krayzstore. Todos os direitos reservados.")
        footer_label.setObjectName("footer_label")
        footer_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_SMALL))
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)

class PasswordPage(QWidget):
    def __init__(self, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__(parent)
        self.parent = parent
        self.colors = colors
        self.setup_ui()
        self.update_style()

    def set_colors(self, colors):
        self.colors = colors
        self.update_style()
        self.password_input.set_colors(colors)
        self.findChild(StyledButton, "login_btn").set_colors(colors)

    def update_style(self):
        self.findChild(QLabel, "title_label").setStyleSheet(f"color: {self.colors['PRIMARY_GRADIENT_START']}; background-color: transparent;")
        self.findChild(QLabel, "subtitle_label").setStyleSheet(f"color: {self.colors['TEXT']}; background-color: transparent;")
        self.findChild(QLabel, "footer_label").setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']}; background-color: transparent;")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(60, 60, 60, 60)

        title_label = QLabel("KRAYz STORE")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_TITLE, QFont.ExtraBold))
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Digite a key de acesso:")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING))
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(30)

        self.password_input = StyledLineEdit(
            echo_mode=QLineEdit.Password,
            parent=self,
            colors=self.colors
        )
        main_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        login_btn = StyledButton("ACESSAR", primary=True, parent=self, colors=self.colors)
        login_btn.setObjectName("login_btn")
        login_btn.clicked.connect(self.check_password)
        main_layout.addWidget(login_btn, alignment=Qt.AlignCenter)

        main_layout.addStretch(1)

        footer_label = QLabel("Desenvolvido por @Krayzstore. Todos os direitos reservados.")
        footer_label.setObjectName("footer_label")
        footer_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_SMALL))
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)

    def check_password(self):
        if self.password_input.text() == "KRAYz": # Corrected password
            self.parent.stacked_widget.setCurrentIndex(2) # Go to MainPage
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Senha Incorreta")
            msg_box.setText("<b>Senha Incorreta!</b>")
            msg_box.setInformativeText("A senha digitada está incorreta. Por favor, tente novamente.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            # Apply consistent styling to QMessageBox
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.parent.current_colors['GLASS_BACKGROUND']};
                    color: {self.parent.current_colors['TEXT']};
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE_NORMAL}px;
                    border-radius: 10px;
                    border: 1px solid {self.parent.current_colors['GLASS_BORDER']};
                }}
                QMessageBox QLabel {{
                    color: {self.parent.current_colors['TEXT']};
                    padding: 5px;
                }}
                QMessageBox QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.parent.current_colors['ERROR']}, stop:1 #FF4500);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }}
                QMessageBox QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF4500, stop:1 {self.parent.current_colors['ERROR']});
                }}
            """)
            msg_box.exec_()
            self.password_input.clear()
            self.password_input.setFocus()

class MainPage(QWidget):
    def __init__(self, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__(parent)
        self.parent = parent
        self.colors = colors
        self.download_thread = None
        self.activation_thread = None
        self.url_fetch_thread = None # Re-added the URL fetch thread
        
        # O self.temp_dir agora é inicializado como None. Será criado quando o download começar.
        self.temp_dir = None
        self.zip_path = None
        
        # Google Drive direct download URL for your .txt file
        self.google_drive_txt_url = "https://fafaawfwkzst2342424.github.io/meu-app/update.txt"
        self.dynamic_download_url = None
        
        self.setup_ui()
        self.update_style()
        self.is_downloading = False
        self.is_activating = False
        self.is_user_cancelling = False # New flag to indicate user-initiated cancellation

    def set_colors(self, colors):
        self.colors = colors
        self.update_style()
        self.action_button.set_colors(colors)
        self.support_button.set_colors(colors) # Renamed contact_btn to support_button
        self.cancel_button.set_colors(colors)

    def update_style(self):
        self.findChild(QLabel, "main_title_label").setStyleSheet(f"color: {self.colors['PRIMARY_GRADIENT_START']}; background-color: transparent;")
        self.status_label.setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']}; background-color: transparent;")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.colors['GLASS_BORDER']};
                border-radius: 10px;
                text-align: center;
                background-color: {self.colors['GLASS_BACKGROUND']};
                color: {self.colors['TEXT']};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_START']}, stop:1 {self.colors['PRIMARY_GRADIENT_END']});
                border-radius: 9px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self.progress_bar)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.progress_bar.setGraphicsEffect(shadow)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(50, 50, 50, 50)

        main_title_label = QLabel("KRAYz STORE")
        main_title_label.setObjectName("main_title_label")
        main_title_label.setAlignment(Qt.AlignCenter)
        main_title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING, QFont.Bold))
        main_layout.addWidget(main_title_label)

        main_layout.addSpacing(20)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFont(QFont(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.progress_bar.setFixedHeight(35)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pressione 'Iniciar Download' para começar.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_NORMAL))
        main_layout.addWidget(self.status_label)

        main_layout.addSpacing(30)

        self.action_button = StyledButton("INICIAR DOWNLOAD", primary=True, parent=self, colors=self.colors)
        self.action_button.clicked.connect(self.handle_action_button_click)
        main_layout.addWidget(self.action_button, alignment=Qt.AlignCenter)

        self.cancel_button = StyledButton(
            "CANCELAR",
            primary=False,
            parent=self,
            colors=self.colors,
            custom_gradient_start=self.colors['CANCEL_GRADIENT_START'],
            custom_gradient_end=self.colors['CANCEL_GRADIENT_END']
        )
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setVisible(False) # Initially hidden
        main_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.support_button = StyledButton("Suporte / Contato", primary=False, parent=self, colors=self.colors)
        self.support_button.clicked.connect(self.open_support_link)
        main_layout.addWidget(self.support_button, alignment=Qt.AlignCenter)

        main_layout.addStretch(1)

    def handle_action_button_click(self):
        current_text = self.action_button.text()

        if current_text == "INICIAR DOWNLOAD" or current_text == "TENTAR NOVAMENTE" or current_text == "REFAZER DOWNLOAD":
            self.fetch_and_start_download()
            self.action_button.setText("PAUSAR DOWNLOAD")
            self.action_button.primary = True # Ensure it stays primary color
            self.action_button.set_colors(self.colors)
            self.cancel_button.setVisible(True)
            self.support_button.setVisible(False) # Hide support button
        elif current_text == "PAUSAR DOWNLOAD":
            if self.download_thread and self.download_thread.isRunning():
                self.download_thread.pause()
                self.action_button.setText("RETOMAR DOWNLOAD")
        elif current_text == "RETOMAR DOWNLOAD":
            if self.download_thread and self.download_thread.isRunning():
                self.download_thread.resume()
                self.action_button.setText("PAUSAR DOWNLOAD")
        elif current_text == "ATIVAR":
            self.start_activation_from_button()
        elif current_text == "REINICIAR COM ADMIN":
            QApplication.quit() # User needs to restart as admin manually

    def fetch_and_start_download(self):
        self.action_button.setEnabled(False) # Disable button while fetching URL
        self.status_label.setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']};")
        self.status_label.setText("Buscando URL de download...")
        self.progress_bar.setValue(0)

        # Ensure any old threads are stopped
        if self.url_fetch_thread and self.url_fetch_thread.isRunning():
            self.url_fetch_thread.quit()
            self.url_fetch_thread.wait(1000)
            if self.url_fetch_thread.isRunning():
                self.url_fetch_thread.terminate()

        self.url_fetch_thread = UrlFetchThread(self.google_drive_txt_url)
        self.url_fetch_thread.url_fetched.connect(self.on_url_fetched)
        self.url_fetch_thread.url_fetch_error.connect(self.on_url_fetch_error)
        self.url_fetch_thread.start()

    def on_url_fetched(self, url):
        self.action_button.setEnabled(True)
        self.dynamic_download_url = url
        self.start_download()

    def on_url_fetch_error(self, message, title):
        self.action_button.setEnabled(True)
        self.show_error_message(message, title)
        self.status_label.setText("Falha ao buscar URL de download.")
        self.status_label.setStyleSheet(f"color: {self.colors['ERROR']};")
        self.action_button.setText("TENTAR NOVAMENTE")
        self.action_button.primary = True
        self.action_button.set_colors(self.colors)
        self.cancel_button.setVisible(False)
        self.support_button.setVisible(True)

    def prepare_download_directory(self):
        """Creates a new temporary directory for the download."""
        # Clean up any old directory before creating a new one
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"Diretório temporário antigo '{self.temp_dir}' limpo.")

        self.temp_dir = tempfile.mkdtemp(prefix="krayz_activator_")
        self.zip_path = os.path.join(self.temp_dir, "KRAYz_STORE.zip")
        print(f"Novo diretório temporário criado: {self.temp_dir}")


    def start_download(self):
        self.action_button.setEnabled(True) # Re-enable the action button (now PAUSAR DOWNLOAD)
        if not self.dynamic_download_url:
            self.on_url_fetch_error("URL de download não encontrada.", "Erro")
            return

        # Prepare a new, clean temporary directory for this download attempt
        self.prepare_download_directory()

        self.is_downloading = True
        self.status_label.setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']};")
        self.status_label.setText("Conectando ao servidor para download...")
        self.progress_bar.setValue(0)

        # Ensure any old threads are stopped
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(1000)
            if self.download_thread.isRunning():
                self.download_thread.terminate()
                print("Warning: Download thread forcefully terminated.")

        self.download_thread = DownloadThread(self.dynamic_download_url, self.zip_path)
        self.download_thread.update_progress.connect(self.update_progress)
        self.download_thread.update_status_message.connect(self.update_status)
        self.download_thread.download_complete.connect(self.on_download_complete)
        self.download_thread.error_occurred.connect(self.show_error_message)
        self.download_thread.start()

    def cancel_download(self):
        # Set flag to indicate user cancellation, so on_download_complete knows not to show another message
        self.is_user_cancelling = True 
        
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop() # Signal the thread to stop
            # The on_download_complete will be called with success=False, handling UI reset
        else:
            self.status_label.setText("Nenhum download em andamento para cancelar.")
            self.action_button.setText("INICIAR DOWNLOAD")
            self.action_button.primary = True
            self.action_button.set_colors(self.colors)
            self.cancel_button.setVisible(False)
            self.support_button.setVisible(True)

        # Show the desired warning message here, as it's the direct result of user action
        QMessageBox.warning(self, "Download Cancelado", "O download foi cancelado pelo usuário.", QMessageBox.Ok)
        # We no longer call clean_temp_files() here. It will be called in on_download_complete.

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def on_download_complete(self, success, message):
        self.is_downloading = False
        self.action_button.setEnabled(True) # Re-enable button after download attempt

        if self.is_user_cancelling:
            # If it was a user-initiated cancel, the message box has already been shown in cancel_download()
            # Just reset the state and UI, and clear the flag.
            self.status_label.setText("Download cancelado pelo usuário.")
            self.status_label.setStyleSheet(f"color: {self.colors['ERROR']};")
            self.action_button.setText("INICIAR DOWNLOAD")
            self.action_button.primary = True
            self.action_button.set_colors(self.colors)
            self.cancel_button.setVisible(False)
            self.support_button.setVisible(True)
            self.is_user_cancelling = False # Reset the flag
            self.clean_temp_files() # Garante a limpeza após um cancelamento
            return # Exit to prevent further processing for this specific scenario

        if success:
            self.status_label.setText("Download concluído!")
            self.status_label.setStyleSheet(f"color: {self.colors['SUCCESS']};")
            self.progress_bar.setValue(100)

            reply = QMessageBox.question(self, 'Download Concluído',
                                         "Download do pacote de ativação concluído com sucesso.\n\n"
                                         "Deseja prosseguir com a ativação agora?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.action_button.setText("ATIVAR")
                self.action_button.primary = True # Keep primary style for activate
                self.action_button.set_colors(self.colors)
                self.status_label.setText("Pronto para ativar. Pressione 'ATIVAR'.")
            else:
                self.action_button.setText("REFAZER DOWNLOAD")
                self.action_button.primary = True
                self.action_button.set_colors(self.colors)
                self.status_label.setText("Download concluído. Aguardando sua ação.")
            
            self.cancel_button.setVisible(False) # Hide cancel after complete
            self.support_button.setVisible(True) # Show support button
        else:
            # This branch is for download failures (not user-initiated cancel)
            self.show_error_message(message, "Erro de Download")
            self.action_button.setText("TENTAR NOVAMENTE")
            self.action_button.primary = True # Keep primary if it's an error state
            self.action_button.set_colors(self.colors)
            
            # Reset buttons after error
            self.cancel_button.setVisible(False)
            self.support_button.setVisible(True)

    def start_activation_from_button(self):
        self.action_button.setEnabled(False) # Disable during activation
        self.is_activating = True
        self.status_label.setText("Iniciando processo de ativação...")
        self.status_label.setStyleSheet(f"color: {self.colors['SUBTLE_TEXT']};")
        self.progress_bar.setValue(0) # Reset progress bar for activation

        # Hide cancel button during activation
        self.cancel_button.setVisible(False)
        self.support_button.setVisible(False) # Support button should remain hidden

        if self.activation_thread and self.activation_thread.isRunning():
            self.activation_thread.terminate() # Forceful termination if still running
            self.activation_thread.wait(1000)
            if self.activation_thread.isRunning():
                print("Warning: Activation thread forcefully terminated.")
        
        if not self.temp_dir or not os.path.exists(self.zip_path):
            self.show_error_message(
                "O arquivo de ativação não foi encontrado. Por favor, refaça o download.",
                "Arquivo Não Encontrado"
            )
            self.status_label.setText("Pronto para iniciar novo download.")
            self.action_button.setText("INICIAR DOWNLOAD")
            self.action_button.primary = True
            self.action_button.set_colors(self.colors)
            self.action_button.setEnabled(True)
            self.support_button.setVisible(True)
            return

        self.activation_thread = ActivationThread(self.zip_path, self.temp_dir)
        self.activation_thread.progress_update.connect(self.update_status)
        self.activation_thread.activation_complete.connect(self.on_activation_complete)
        self.activation_thread.error_occurred.connect(self.show_error_message)
        self.activation_thread.requires_admin.connect(self.handle_admin_required)
        self.activation_thread.start()

    def handle_admin_required(self):
        QMessageBox.warning(self, "Permissão Necessária",
                            "Para que o ativador funcione corretamente, é necessário executá-lo como Administrador.\n\n"
                            "Por favor, feche este aplicativo e execute-o novamente como Administrador (clique com o botão direito no ícone do aplicativo e selecione 'Executar como administrador').",
                            QMessageBox.Ok)
        self.status_label.setText("Ativação falhou: Permissões de administrador necessárias.")
        self.status_label.setStyleSheet(f"color: {self.colors['ERROR']};")
        self.action_button.setText("REINICIAR COM ADMIN")
        self.action_button.primary = True
        self.action_button.set_colors(self.colors)
        self.action_button.setEnabled(True) # Allow user to try again
        
        # Reset visibility for buttons
        self.cancel_button.setVisible(False)
        self.support_button.setVisible(True)


    def on_activation_complete(self, success, message):
        self.is_activating = False
        self.action_button.setEnabled(True) # Re-enable button after activation attempt

        if success:
            QMessageBox.information(self, "Sucesso", message, QMessageBox.Ok)
            self.status_label.setText("Ativação concluída com sucesso!")
            self.status_label.setStyleSheet(f"color: {self.colors['SUCCESS']};")
            self.progress_bar.setValue(100)
            self.action_button.setText("ATIVADO!")
            self.action_button.setEnabled(False) # Disable button as activation is complete
            self.action_button.primary = False # Can be secondary as it's a final state
            self.action_button.set_colors(self.colors)
        else:
            # Error message is handled by show_error_message connected to error_occurred signal
            self.status_label.setText("Erro na ativação. Verifique a mensagem acima.")
            self.status_label.setStyleSheet(f"color: {self.colors['ERROR']};")
            self.action_button.setText("TENTAR ATIVAÇÃO NOVAMENTE")
            self.action_button.primary = True
            self.action_button.set_colors(self.colors)
        
        # Reset visibility for buttons after activation complete
        self.cancel_button.setVisible(False)
        self.support_button.setVisible(True)

        self.clean_temp_files() # Garante a limpeza após a conclusão (sucesso ou falha) da ativação

    def show_error_message(self, message, title="Erro"):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"<b>{title}:</b>")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.parent.current_colors['GLASS_BACKGROUND']};
                color: {self.parent.current_colors['TEXT']};
                font-family: "{FONT_FAMILY}";
                font-size: {FONT_SIZE_NORMAL}px;
                border-radius: 10px;
                border: 1px solid {self.parent.current_colors['GLASS_BORDER']};
            }}
            QMessageBox QLabel {{
                color: {self.parent.current_colors['TEXT']};
                padding: 5px;
            }}
            QMessageBox QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.parent.current_colors['ERROR']}, stop:1 #FF4500);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QMessageBox QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF4500, stop:1 {self.parent.current_colors['ERROR']});
            }}
        """)
        msg_box.exec_()
        self.status_label.setStyleSheet(f"color: {self.colors['ERROR']};")

    def clean_temp_files(self):
        """
        Melhoria: Limpa a pasta temporária onde o ZIP e o conteúdo extraído
        estão localizados. Esta função agora é mais robusta.
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            print(f"Iniciando limpeza da pasta temporária: {self.temp_dir}")
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"Diretório temporário '{self.temp_dir}' limpo com sucesso.")
            except OSError as e:
                print(f"Erro ao limpar o diretório temporário '{self.temp_dir}': {e}")
        
    @staticmethod
    def cleanup_old_temp_dirs():
        """
        Função estática para procurar e remover diretórios temporários antigos
        criados por este aplicativo. Chamada na inicialização do programa.
        """
        temp_root = tempfile.gettempdir()
        prefix = "krayz_activator_"
        for item in os.listdir(temp_root):
            if item.startswith(prefix):
                full_path = os.path.join(temp_root, item)
                if os.path.isdir(full_path):
                    print(f"Encontrado e removendo diretório temporário antigo: {full_path}")
                    try:
                        shutil.rmtree(full_path, ignore_errors=True)
                    except OSError as e:
                        print(f"Erro ao remover o diretório temporário antigo '{full_path}': {e}")


    def open_support_link(self):
        support_url = "https://www.instagram.com/krayzstore/"
        QDesktopServices.openUrl(QUrl(support_url))


class FloatingSiteButton(QPushButton):
    def __init__(self, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__("🌐", parent)
        self.colors = colors
        self.setFixedSize(50, 50)
        self.setFont(QFont("Segoe UI Symbol", 20))
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_START']}, stop:1 {self.colors['PRIMARY_GRADIENT_END']});
                border: none;
                border-radius: 25px;
                color: white;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_END']}, stop:1 {self.colors['PRIMARY_GRADIENT_START']});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_START']}, stop:1 {self.colors['PRIMARY_GRADIENT_END']});
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(5, 5)
        self.setGraphicsEffect(shadow)

        self.clicked.connect(self.open_site)

    def set_colors(self, colors):
        self.colors = colors
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_START']}, stop:1 {self.colors['PRIMARY_GRADIENT_END']});
                border: none;
                border-radius: 25px;
                color: white;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_END']}, stop:1 {self.colors['PRIMARY_GRADIENT_START']});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['PRIMARY_GRADIENT_START']}, stop:1 {self.colors['PRIMARY_GRADIENT_END']});
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)

    def open_site(self):
        site_url = "http://krayz.store"
        if not site_url.startswith(("http://", "https://")):
            site_url = "http://" + site_url 

        if QDesktopServices.openUrl(QUrl(site_url)):
            print(f"Opened {site_url} in default browser.")
        else:
            QMessageBox.warning(self.parent(), "Erro ao Abrir Site",
                                f"Não foi possível abrir o site: {site_url}.\n"
                                "Por favor, verifique sua conexão com a internet ou as configurações do seu navegador.\n"
                                "Você pode tentar copiar e colar a URL manualmente.",
                                QMessageBox.Ok)


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, colors=WHITE_THEME_COLORS):
        super().__init__(parent)
        self.parent_window = parent
        self.colors = colors
        self.setFixedHeight(40) # Height of the custom title bar
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Removed the title label here to meet the user's request.
        layout.addStretch() # Pushes buttons to the right

        # Minimize Button
        self.minimize_button = QPushButton("-")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setFont(QFont(FONT_FAMILY, 16))
        self.minimize_button.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.minimize_button)

        # Close Button
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setFont(QFont(FONT_FAMILY, 12))
        self.close_button.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.update_button_style()

    def update_style(self):
        # No title_label to style here anymore
        self.update_button_style()

    def update_button_style(self):
        button_style = f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.3); /* Semi-opaque white background */
                color: {self.colors['TEXT']};
                border: none;
                border-radius: 9px; /* Rounded corners 9px */
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.5); /* More opaque white on hover */
                border-radius: 9px; /* Consistent rounded corners */
            }}
            QPushButton#close_button:hover {{
                background-color: {self.colors['ERROR']}; /* Keep red for close button */
                color: white;
                border-radius: 9px; /* Consistent rounded corners */
            }}
        """
        self.minimize_button.setStyleSheet(button_style)
        self.close_button.setObjectName("close_button") # Set object name to apply specific hover style
        self.close_button.setStyleSheet(button_style) # Apply the style initially


    def set_colors(self, colors):
        self.colors = colors
        self.update_style()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KRAYz STORE - Oficial")
        self.setMinimumSize(700, 600)

        self.current_colors = WHITE_THEME_COLORS
        self.current_daltonism_mode = "Normal" # Kept for potential future use

        # --- Window Flags for Frameless Window ---
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground) # For rounded corners to show properly
        # --- End Window Flags ---

        self.dragging = False
        self.offset = None

        self.setup_ui()
        self.apply_theme()

        # Adiciona a limpeza garantida de arquivos temporários na saída do programa
        atexit.register(self.main_page.clean_temp_files)


    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # No margins for the main layout within central widget

        # Custom Title Bar
        self.title_bar = CustomTitleBar(self, colors=self.current_colors)
        main_layout.addWidget(self.title_bar)

        # Stacked Widget for pages
        self.stacked_widget = QStackedWidget(central_widget) # Make stacked_widget child of central_widget
        self.stacked_widget.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {self.current_colors['GLASS_BACKGROUND']};
                border-radius: 20px;
                border: 1px solid {self.current_colors['GLASS_BORDER']};
                padding: 20px;
            }}
        """)
        # Add padding around the stacked widget, inside the main_layout.
        # This acts as the inner margin for your content relative to the window edge.
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 0, 40, 40) # Left, Top (0, as title bar takes top space), Right, Bottom
        content_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(content_layout)

        # Add shadow to stacked widget (directly on the stacked_widget)
        shadow = QGraphicsDropShadowEffect(self.stacked_widget)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.stacked_widget.setGraphicsEffect(shadow)


        self.welcome_page = WelcomePage(self, colors=self.current_colors)
        self.password_page = PasswordPage(self, colors=self.current_colors)
        self.main_page = MainPage(self, colors=self.current_colors)

        self.stacked_widget.addWidget(self.welcome_page) # Index 0
        self.stacked_widget.addWidget(self.password_page) # Index 1
        self.stacked_widget.addWidget(self.main_page)     # Index 2

        self.stacked_widget.setCurrentIndex(0)

        # Connect start_app signal to direct page change
        self.welcome_page.start_app.connect(self.go_to_password_page)

        # Floating site button needs to be added directly to the QMainWindow itself (self)
        # to ensure it floats over the central widget and its stacked widget.
        self.floating_site_button = FloatingSiteButton(self, colors=self.current_colors)
        # Position the floating button
        # Adjusting 30 pixels from right and top to avoid touching the edge
        self.floating_site_button.move(self.width() - self.floating_site_button.width() - 30, 30 + self.title_bar.height())
        self.floating_site_button.raise_() # Bring to front


    def create_content_layout(self):
        # Create a layout to hold the stacked widget with its own padding
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 0, 40, 40) # Left, Top (0, as title bar takes top space), Right, Bottom
        content_layout.addWidget(self.stacked_widget)
        return content_layout

    # Override resize event to reposition the floating button
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Recalculate position relative to the QMainWindow (self)
        # Offset by title bar height
        self.floating_site_button.move(self.width() - self.floating_site_button.width() - 30, 30 + self.title_bar.height())
        self.floating_site_button.raise_() # Ensure it's always on top after resize

    def go_to_password_page(self):
        """Directly switch to the password page without animation."""
        self.stacked_widget.setCurrentIndex(1)
        self.password_page.password_input.setFocus() # Set focus for immediate input

    def apply_theme(self):
        # Apply border-radius to the QMainWindow (root window)
        # The background for the QMainWindow needs to be transparent for this to work.
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_colors['BACKGROUND_BASE']};
                border-radius: 12px; /* Apply rounded corners here */
            }}
            QMainWindow::menu-bar {{
                background-color: transparent; /* Ensure menu bar area is also transparent if exists */
            }}
        """)

        # Update stacked widget background (the "glass pane" for content)
        self.stacked_widget.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {self.current_colors['GLASS_BACKGROUND']};
                border-radius: 20px;
                border: 1px solid {self.current_colors['GLASS_BORDER']};
                padding: 20px;
            }}
        """)
        # Re-apply shadow to stacked widget
        shadow = QGraphicsDropShadowEffect(self.stacked_widget)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.stacked_widget.setGraphicsEffect(shadow)

        for widget in [self.welcome_page, self.password_page, self.main_page]:
            widget.set_colors(self.current_colors)
            widget.update()

        self.floating_site_button.set_colors(self.current_colors)
        self.title_bar.set_colors(self.current_colors)


    def apply_daltonism_effect(self, mode_name):
        self.current_daltonism_mode = mode_name

        if mode_name == "Normal":
            self.current_colors = WHITE_THEME_COLORS
        else:
            adj = DALTONISM_MODES[mode_name]

            adjusted_colors = WHITE_THEME_COLORS.copy()
            adjusted_colors['PRIMARY_GRADIENT_START'] = adj.get('PRIMARY_ADJ_START', WHITE_THEME_COLORS['PRIMARY_GRADIENT_START'])
            adjusted_colors['PRIMARY_GRADIENT_END'] = adj.get('PRIMARY_ADJ_END', WHITE_THEME_COLORS['PRIMARY_GRADIENT_END'])
            adjusted_colors['TEXT'] = adj.get('TEXT_ADJ', WHITE_THEME_COLORS['TEXT'])
            adjusted_colors['SUBTLE_TEXT'] = adj.get('SUBTLE_TEXT_ADJ', WHITE_THEME_COLORS['SUBTLE_TEXT'])

            self.current_colors = adjusted_colors

        self.apply_theme()

    # --- Custom Dragging Implementation ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    # --- End Custom Dragging Implementation ---

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmar Saída',
                                     "Você tem certeza que deseja fechar o aplicativo? ",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.main_page.download_thread and self.main_page.download_thread.isRunning():
                self.main_page.download_thread.stop()
                self.main_page.download_thread.wait(5000)
                if self.main_page.download_thread.isRunning():
                    self.main_page.download_thread.terminate()
                    print("Download thread forcefully terminated during close.")

            if self.main_page.activation_thread and self.main_page.activation_thread.isRunning():
                self.main_page.activation_thread.terminate()
                self.main_page.activation_thread.wait(5000)
                if self.main_page.activation_thread.isRunning():
                    print("Activation thread forcefully terminated during close.")

            # Also stop the URL fetch thread if it's running
            if self.main_page.url_fetch_thread and self.main_page.url_fetch_thread.isRunning():
                self.main_page.url_fetch_thread.quit()
                self.main_page.url_fetch_thread.wait(1000)
                if self.main_page.url_fetch_thread.isRunning():
                    print("URL fetch thread forcefully terminated during close.")

            # A função de limpeza agora é chamada na MainPage e no atexit
            # Não é mais necessário chamá-la aqui explicitamente, mas podemos
            # manter a chamada para redundância e clareza.
            self.main_page.clean_temp_files()

            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":

    # Tenta limpar diretórios temporários de sessões anteriores na inicialização
    MainPage.cleanup_old_temp_dirs()

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setApplicationName("KRAYz STORE")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
