import sys
import threading
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QProgressBar, QStatusBar,
    QHBoxLayout, QTabWidget, QMessageBox, QPushButton, QTextEdit, QSplitter, QLabel, QFrame
)
from PySide6.QtGui import QAction, QFont, QTextCursor
from PySide6.QtCore import QUrl, Qt, QDateTime, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
import markdown
from bs4 import BeautifulSoup

# OpenRouter API details
API_KEY = "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"
MODEL = "meta-llama/llama-4-maverick:free"  # Geändert auf Llama 4 Maverick
API_URL = "https://openrouter.ai/api/v1/chat/completions"

class CustomWebView(QWebEngineView):
    def createWindow(self, web_window_type):
        main_win = self.window()
        main_win.add_tab()
        return main_win.current_browser()

class BrowserTab(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.browser = CustomWebView()
        self.browser.load(QUrl(url))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        self.browser.loadStarted.connect(lambda: self.window().progress_bar.setVisible(True))
        self.browser.loadProgress.connect(lambda p: self.window().progress_bar.setValue(p))
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(lambda q: self.window().url_bar.setText(q.toString()))

    def on_load_finished(self, ok):
        self.window().progress_bar.setVisible(False)
        if not ok:
            QMessageBox.warning(self, "Ladefehler", "Seite konnte nicht geladen werden.")

class ChatMessage(QFrame):
    def __init__(self, sender, message, timestamp, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(6)
        
        # Container für Nachricht
        msg_container = QFrame()
        msg_layout = QHBoxLayout(msg_container)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        
        # Styling basierend auf Sender
        if self.sender == "user":
            self.setStyleSheet("""
                ChatMessage {
                    background: rgba(137, 180, 250, 0.08);
                    border-left: 4px solid #89b4fa;
                    margin: 2px 0;
                    border-radius: 0 12px 12px 0;
                }
            """)
            
            # Avatar
            avatar = QLabel("👤")
            avatar.setFixedSize(32, 32)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet("""
                QLabel {
                    background: #89b4fa;
                    border-radius: 16px;
                    color: #1e1e2e;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            
            # Nachricht
            msg_label = QLabel(self.message)
            msg_label.setWordWrap(True)
            msg_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: #cdd6f4;
                    font-size: 14px;
                    padding: 8px 12px;
                    border-radius: 8px;
                }
            """)
            
            # Header mit Name und Zeit
            header = QLabel(f"<b style='color: #89b4fa;'>Du</b> <span style='color: #6c7086; font-size: 12px;'>• {self.timestamp}</span>")
            header.setStyleSheet("background: transparent; padding: 0; margin: 0;")
            
            msg_layout.addWidget(avatar)
            msg_content = QVBoxLayout()
            msg_content.setSpacing(4)
            msg_content.addWidget(header)
            msg_content.addWidget(msg_label)
            msg_layout.addLayout(msg_content)
            msg_layout.addStretch()
            
        elif self.sender == "ai":
            self.setStyleSheet("""
                ChatMessage {
                    background: rgba(166, 227, 161, 0.08);
                    border-left: 4px solid #a6e3a1;
                    margin: 2px 0;
                    border-radius: 12px 0 0 12px;
                }
            """)
            
            # Avatar
            avatar = QLabel("🦙")  # Lama-Icon für Llama
            avatar.setFixedSize(32, 32)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet("""
                QLabel {
                    background: #a6e3a1;
                    border-radius: 16px;
                    color: #1e1e2e;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            
            # Nachricht als TextEdit für Formatierung
            msg_text = QTextEdit()
            msg_text.setHtml(self.message)
            msg_text.setReadOnly(True)
            msg_text.setStyleSheet("""
                QTextEdit {
                    background: transparent;
                    color: #cdd6f4;
                    font-size: 14px;
                    padding: 8px 12px;
                    border-radius: 8px;
                    border: none;
                }
            """)
            msg_text.setFixedHeight(msg_text.document().size().height() + 20)
            
            # Header mit Name und Zeit
            header = QLabel(f"<b style='color: #a6e3a1;'>Llama AI</b> <span style='color: #6c7086; font-size: 12px;'>• {self.timestamp}</span>")
            header.setStyleSheet("background: transparent; padding: 0; margin: 0;")
            
            msg_layout.addWidget(avatar)
            msg_content = QVBoxLayout()
            msg_content.setSpacing(4)
            msg_content.addWidget(header)
            msg_content.addWidget(msg_text)
            msg_layout.addLayout(msg_content)
            msg_layout.addStretch()
            
        else:  # system
            self.setStyleSheet("""
                ChatMessage {
                    background: rgba(116, 199, 236, 0.05);
                    border: 1px solid rgba(116, 199, 236, 0.2);
                    border-radius: 8px;
                    margin: 4px 0;
                }
            """)
            
            # System-Nachricht zentriert
            msg_label = QLabel(f"💬 {self.message}")
            msg_label.setAlignment(Qt.AlignCenter)
            msg_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: #74c7ec;
                    font-size: 13px;
                    font-style: italic;
                    padding: 8px;
                }
            """)
            
            msg_layout.addWidget(msg_label)
        
        layout.addWidget(msg_container)

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            ChatWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e2e, stop:1 #313244);
                border-right: 1px solid #45475a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header mit Gradient
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #89b4fa, stop:0.5 #74c7ec, stop:1 #a6e3a1);
                border: none;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo und Titel
        logo_label = QLabel("🦙")
        logo_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 20px;
                font-size: 24px;
                padding: 8px;
            }
        """)
        logo_label.setFixedSize(40, 40)
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Llama AI Assistant")
        title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #1e1e2e;
                font-size: 18px;
                font-weight: bold;
                padding-left: 10px;
            }
        """)
        
        # Status Indikator
        self.status_indicator = QLabel("🟢")
        self.status_indicator.setToolTip("Online")
        self.status_indicator.setStyleSheet("background: transparent; font-size: 16px;")
        
        # Clear Button
        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.setFixedSize(36, 36)
        self.clear_btn.setToolTip("Chat löschen")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(243, 139, 168, 0.8);
                border: none;
                border-radius: 18px;
                color: #1e1e2e;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(243, 139, 168, 1.0);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: rgba(243, 139, 168, 0.6);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_chat)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.clear_btn)
        
        # Chat-Bereich mit Scroll
        self.chat_scroll = QTextEdit()
        self.chat_scroll.setReadOnly(True)
        self.chat_scroll.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 0;
                margin: 0;
            }
            QScrollBar:vertical {
                background: #313244;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #585b70;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6c7086;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        # Input-Bereich
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: #313244;
                border-top: 1px solid #45475a;
                padding: 0;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # Typing indicator
        self.typing_label = QLabel("KI denkt nach...")
        self.typing_label.setVisible(False)
        self.typing_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #74c7ec;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
            }
        """)
        
        # Input Container
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background: #1e1e2e;
                border: 2px solid #45475a;
                border-radius: 12px;
                padding: 0;
            }
        """)
        
        input_container_layout = QHBoxLayout(input_container)
        input_container_layout.setContentsMargins(15, 10, 15, 10)
        input_container_layout.setSpacing(10)
        
        # Input Field
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Schreibe eine Nachricht...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #cdd6f4;
                font-size: 14px;
                padding: 8px 0;
            }
            QLineEdit::placeholder {
                color: #6c7086;
            }
            QLineEdit:focus {
                background: transparent;
            }
        """)
        
        # Send Button
        self.send_btn = QPushButton("📤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #89b4fa, stop:1 #74c7ec);
                border: none;
                border-radius: 20px;
                color: #1e1e2e;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #74c7ec, stop:1 #89b4fa);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: #6c7086;
                transform: scale(0.95);
            }
            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }
        """)
        
        input_container_layout.addWidget(self.chat_input)
        input_container_layout.addWidget(self.send_btn)
        
        input_layout.addWidget(self.typing_label)
        input_layout.addWidget(input_container)
        
        # Layout zusammenfügen
        layout.addWidget(header)
        layout.addWidget(self.chat_scroll, 1)
        layout.addWidget(input_frame)
        
        # Event-Handler
        self.send_btn.clicked.connect(self.on_send)
        self.chat_input.returnPressed.connect(self.on_send)
        
        # Willkommensnachricht
        self.add_system_message("Willkommen! Ich bin dein persönlicher Llama AI-Assistent. Stelle mir gerne Fragen! 🚀")
    
    def format_ai_response(self, text):
        """Formatiert die AI-Antwort mit Markdown-Unterstützung"""
        # Basis-Formatierung
        formatted = text.replace("\n", "<br>")
        
        # Markdown zu HTML Konvertierung für grundlegende Formatierung
        html = markdown.markdown(formatted)
        
        # Weitere Anpassungen für Code-Blöcke
        html = html.replace("<pre><code>", '<pre style="background: #2a2a3e; padding: 10px; border-radius: 8px; color: #89b4fa;">')
        html = html.replace("</code></pre>", "</pre>")
        
        # Styling für Listen
        html = html.replace("<ul>", '<ul style="margin-left: 20px; padding-left: 10px;">')
        html = html.replace("<ol>", '<ol style="margin-left: 20px; padding-left: 10px;">')
        
        # Styling für Überschriften
        for i in range(1, 6):
            html = html.replace(f"<h{i}>", f'<h{i} style="color: #74c7ec; margin-bottom: 5px;">')
        
        return html
    
    def add_message(self, sender, message):
        """Fügt eine strukturierte Nachricht hinzu"""
        timestamp = QDateTime.currentDateTime().toString("HH:mm")
        
        if sender == "user":
            html = f"""
            <div style="margin: 8px 0; padding: 12px; background: rgba(137, 180, 250, 0.1); 
                       border-left: 4px solid #89b4fa; border-radius: 0 8px 8px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="background: #89b4fa; color: #1e1e2e; padding: 4px 8px; 
                               border-radius: 12px; font-size: 12px; font-weight: bold; margin-right: 8px;">
                        👤 Du
                    </span>
                    <span style="color: #6c7086; font-size: 11px;">{timestamp}</span>
                </div>
                <div style="color: #cdd6f4; font-size: 14px; line-height: 1.4; margin-left: 8px;">
                    {message}
                </div>
            </div>
            """
            
        elif sender == "ai":
            formatted_message = self.format_ai_response(message)
            html = f"""
            <div style="margin: 8px 0; padding: 12px; background: rgba(166, 227, 161, 0.1); 
                       border-left: 4px solid #a6e3a1; border-radius: 8px 0 0 8px;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="background: #a6e3a1; color: #1e1e2e; padding: 4px 8px; 
                               border-radius: 12px; font-size: 12px; font-weight: bold; margin-right: 8px;">
                        🦙 Llama AI
                    </span>
                    <span style="color: #6c7086; font-size: 11px;">{timestamp}</span>
                </div>
                <div style="color: #cdd6f4; font-size: 14px; line-height: 1.4; margin-left: 8px;">
                    {formatted_message}
                </div>
            </div>
            """
            
        else:  # system
            html = f"""
            <div style="margin: 12px 0; padding: 10px; text-align: center; 
                       background: rgba(116, 199, 236, 0.1); border: 1px solid rgba(116, 199, 236, 0.3); 
                       border-radius: 8px;">
                <div style="color: #74c7ec; font-size: 13px; font-style: italic;">
                    💬 {message}
                </div>
                <div style="color: #6c7086; font-size: 10px; margin-top: 4px;">
                    {timestamp}
                </div>
            </div>
            """
        
        self.chat_scroll.insertHtml(html)
        self.chat_scroll.ensureCursorVisible()
    
    def add_system_message(self, message):
        self.add_message("system", message)
    
    def on_send(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        
        # UI-Updates
        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳")
        self.typing_label.setVisible(True)
        self.status_indicator.setText("🟡")
        self.status_indicator.setToolTip("Verarbeitet...")
        
        # Nachricht hinzufügen
        self.add_message("user", text)
        self.chat_input.clear()
        self.chat_history.append({"role": "user", "content": text})
        
        # AI-Anfrage starten
        threading.Thread(target=self.request_ai, daemon=True).start()
    
    def clear_chat(self):
        """Leert den Chat"""
        self.chat_scroll.clear()
        self.chat_history.clear()
        self.add_system_message("Chat wurde geleert. Wie kann ich dir helfen? 🧹")
    
    def request_ai(self):
        """Sendet Anfrage an die AI"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mkweb-one.vercel.app",
            "X-Title": "MKWEB Browser"
        }
        
        # Kontext-Management (letzte 20 Nachrichten)
        messages = self.chat_history[-20:] if len(self.chat_history) > 20 else self.chat_history
        
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=45)
            response.raise_for_status()
            
            if not response.text.strip():
                ai_message = "❌ Die API hat eine leere Antwort gesendet."
            else:
                try:
                    data = response.json()
                    if "choices" in data and data["choices"]:
                        choice = data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            ai_message = choice["message"]["content"]
                            self.chat_history.append({"role": "assistant", "content": ai_message})
                        else:
                            ai_message = "❌ Unerwartete API-Antwortstruktur."
                    elif "error" in data:
                        ai_message = f"❌ API-Fehler: {data['error']}"
                    else:
                        ai_message = "❌ Unbekanntes Antwortformat von der API."
                except ValueError:
                    ai_message = "❌ Fehler beim Verarbeiten der API-Antwort."
                    
        except requests.exceptions.Timeout:
            ai_message = "⏱️ Timeout: Die Anfrage hat zu lange gedauert. Versuche es erneut!"
        except requests.exceptions.ConnectionError:
            ai_message = "🌐 Verbindungsfehler: Überprüfe deine Internetverbindung."
        except requests.exceptions.HTTPError as e:
            ai_message = f"❌ HTTP-Fehler {response.status_code}: {str(e)}"
        except Exception as e:
            ai_message = f"🔴 Unerwarteter Fehler: {str(e)}"
        
        # UI finalisieren
        self.finalize_response(ai_message)
    
    def finalize_response(self, ai_message):
        """Finalisiert die AI-Antwort und setzt UI zurück"""
        self.add_message("ai", ai_message)
        
        # UI zurücksetzen
        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤")
        self.typing_label.setVisible(False)
        self.status_indicator.setText("🟢")
        self.status_indicator.setToolTip("Online")
        
        # Fokus auf Input
        self.chat_input.setFocus()

class MKWebBrowser(QMainWindow):
    STARTPAGE = 'https://mkweb-one.vercel.app'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MKWEB 2.0 mit Llama AI-Assistent")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 900)
        self._setup_ui()
        self.show()

    def _setup_ui(self):
        # Hauptsplitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Browser-Panel
        browse_panel = QWidget()
        browse_layout = QVBoxLayout(browse_panel)
        browse_layout.setContentsMargins(0, 0, 0, 0)
        browse_layout.setSpacing(0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                border-bottom: 1px solid #45475a;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)
        toolbar_layout.setSpacing(8)
        
        # Toggle-Button
        self.toggle_btn = QPushButton("🦙 AI einblenden")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b35, stop:1 #ff8c42);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff8c42, stop:1 #ff6b35);
            }
            QPushButton:pressed {
                background: #e55a2b;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_assistant)
        
        # Navigation-Buttons
        nav_buttons = []
        for icon, tooltip, slot in [
            ("◀", "Zurück", self.back),
            ("▶", "Vorwärts", self.forward), 
            ("⟳", "Aktualisieren", self.reload),
            ("🏠", "Startseite", self.home)
        ]:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(36, 36)
            btn.setStyleSheet("""
                QPushButton {
                    background: #45475a;
                    border: none;
                    border-radius: 6px;
                    color: #cdd6f4;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #585b70;
                }
                QPushButton:pressed {
                    background: #6c7086;
                }
            """)
            btn.clicked.connect(slot)
            nav_buttons.append(btn)
        
        # URL-Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL eingeben...")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                border: 2px solid #45475a;
                border-radius: 8px;
                color: #cdd6f4;
                font-size: 14px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
            QLineEdit::placeholder {
                color: #6c7086;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate)
        
        # Neuer Tab Button
        new_tab_btn = QPushButton("+ Tab")
        new_tab_btn.setStyleSheet("""
            QPushButton {
                background: #a6e3a1;
                border: none;
                border-radius: 6px;
                color: #1e1e2e;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: #94d982;
            }
            QPushButton:pressed {
                background: #82c766;
            }
        """)
        new_tab_btn.clicked.connect(self.add_tab)
        
        # Toolbar zusammenfügen
        toolbar_layout.addWidget(self.toggle_btn)
        toolbar_layout.addWidget(QFrame())  # Spacer
        for btn in nav_buttons:
            toolbar_layout.addWidget(btn)
        toolbar_layout.addWidget(self.url_bar, 1)
        toolbar_layout.addWidget(new_tab_btn)
        
        # Tab-Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #1e1e2e;
            }
            QTabBar::tab {
                background: #313244;
                color: #cdd6f4;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1e1e2e;
                color: #89b4fa;
            }
            QTabBar::tab:hover {
                background: #45475a;
            }
        """)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #313244;
                height: 3px;
            }
            QProgressBar::chunk {
                background: #89b4fa;
            }
        """)
        
        # Status Bar
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(self.progress_bar)
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #1e1e2e;
                border-top: 1px solid #45475a;
                color: #6c7086;
                font-size: 12px;
            }
        """)
        
        # Browser-Layout zusammenfügen
        browse_layout.addWidget(toolbar)
        browse_layout.addWidget(self.tabs, 1)
        browse_layout.addWidget(status_bar)
        
        # Chat-Widget
        self.chat = ChatWidget()
        self.chat.setVisible(False)
        self.chat.setMinimumWidth(350)
        self.chat.setMaximumWidth(500)
        
        # Splitter konfigurieren
        self.splitter.addWidget(browse_panel)
        self.splitter.addWidget(self.chat)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([1200, 400])
        
        # Hauptwidget setzen
        self.setCentralWidget(self.splitter)
        
        # Ersten Tab hinzufügen
        self.add_tab()
        
        # Styling für Hauptfenster
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e2e;
            }
            QSplitter::handle {
                background: #45475a;
                width: 2px;
            }
            QSplitter::handle:hover {
                background: #74c7ec;
            }
        """)

    def toggle_assistant(self):
        """Schaltet den KI-Assistenten ein/aus"""
        is_visible = not self.chat.isVisible()
        self.chat.setVisible(is_visible)
        
        if is_visible:
            self.toggle_btn.setText("🦙 AI ausblenden")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #a6e3a1, stop:1 #74c7ec);
                    color: #1e1e2e;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #74c7ec, stop:1 #a6e3a1);
                }
                QPushButton:pressed {
                    background: #89b4fa;
                }
            """)
        else:
            self.toggle_btn.setText("🦙 AI einblenden")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ff6b35, stop:1 #ff8c42);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ff8c42, stop:1 #ff6b35);
                }
                QPushButton:pressed {
                    background: #e55a2b;
                }
            """)

    def add_tab(self, url=None):
        """Fügt einen neuen Tab hinzu"""
        target_url = url or self.STARTPAGE
        tab = BrowserTab(target_url, parent=self)
        
        # Tab-Titel dynamisch setzen
        tab_title = "Neue Seite"
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                tab_title = parsed.netloc or "Neue Seite"
            except:
                tab_title = "Neue Seite"
        
        tab_index = self.tabs.addTab(tab, tab_title)
        self.tabs.setCurrentIndex(tab_index)
        
        # Tab-Titel bei Seitenänderung aktualisieren
        def update_tab_title():
            if hasattr(tab.browser, 'title') and tab.browser.title():
                title = tab.browser.title()[:30] + "..." if len(tab.browser.title()) > 30 else tab.browser.title()
                self.tabs.setTabText(tab_index, title)
        
        tab.browser.titleChanged.connect(update_tab_title)

    def close_tab(self, index):
        """Schließt einen Tab"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            # Letzten Tab nicht schließen, sondern zur Startseite navigieren
            self.home()

    def current_browser(self):
        """Gibt den aktuellen Browser zurück"""
        current_tab = self.tabs.currentWidget()
        return current_tab.browser if current_tab else None

    def back(self):
        """Navigiert zurück"""
        browser = self.current_browser()
        if browser:
            browser.back()

    def forward(self):
        """Navigiert vorwärts"""
        browser = self.current_browser()
        if browser:
            browser.forward()

    def reload(self):
        """Lädt die Seite neu"""
        browser = self.current_browser()
        if browser:
            browser.reload()

    def home(self):
        """Navigiert zur Startseite"""
        browser = self.current_browser()
        if browser:
            browser.load(QUrl(self.STARTPAGE))
            self.url_bar.setText(self.STARTPAGE)

    def navigate(self):
        """Navigiert zur eingegebenen URL"""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        
        # URL-Validation und -Korrektur
        if not url_text.startswith(('http://', 'https://')):
            # Prüfen ob es eine Domain ist oder eine Suche
            if '.' in url_text and ' ' not in url_text:
                url_text = 'https://' + url_text
            else:
                # Als Google-Suche behandeln
                import urllib.parse
                search_query = urllib.parse.quote(url_text)
                url_text = f'https://www.google.com/search?q={search_query}'
        
        browser = self.current_browser()
        if browser:
            browser.load(QUrl(url_text))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # App-Icon setzen (optional)
    app.setApplicationName("MKWEB 2.0")
    app.setApplicationVersion("2.0.0")
    
    # Dunkles Theme
    app.setStyle('Fusion')
    
    # Hauptfenster erstellen
    window = MKWebBrowser()
    
    # Event-Loop starten
    sys.exit(app.exec())
