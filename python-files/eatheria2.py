import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QWidget, QFrame, QStackedWidget, 
                            QHBoxLayout, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QSize, QTimer

class MinecraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Launcher")
        self.setFixedSize(900, 600)
        
        # Set window icon (using a placeholder)
        self.setWindowIcon(QIcon.fromTheme("application-x-executable"))
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create UI components
        self.create_title_bar()
        self.create_main_content()
        self.create_pages()
        
        # Style settings
        self.setStyleSheet("""
            QMainWindow {
                background-color: #313233;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #3C8527;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #1E1E1E;
            }
            QListWidget {
                background-color: #252526;
                color: white;
                border: 1px solid #1E1E1E;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #2A2D2E;
            }
            QListWidget::item:selected {
                background-color: #37373D;
                border: 1px solid #4E4E50;
            }
        """)
    
    def create_title_bar(self):
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #2D2D2D; border-bottom: 1px solid #1E1E1E;")
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)
        
        title = QLabel("Minecraft Launcher")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("background-color: #F04747; font-weight: bold;")
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        self.main_layout.addWidget(title_bar)
    
    def create_main_content(self):
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar menu
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #252526; border-right: 1px solid #1E1E1E;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Profile selection
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("border: none;")
        
        # Add sample profiles
        profiles = ["Survival World", "Creative Builds", "Hardcore Mode", "Minecraft 1.20"]
        for profile in profiles:
            item = QListWidgetItem(profile)
            item.setIcon(QIcon.fromTheme("folder"))
            self.profile_list.addItem(item)
        
        # Menu buttons
        play_btn = QPushButton("Play")
        news_btn = QPushButton("News")
        settings_btn = QPushButton("Settings")
        
        play_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        news_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        # Add widgets to sidebar
        sidebar_layout.addWidget(self.profile_list)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(play_btn)
        sidebar_layout.addWidget(news_btn)
        sidebar_layout.addWidget(settings_btn)
        sidebar_layout.addSpacing(10)
        
        # Main content area
        self.stacked_widget = QStackedWidget()
        
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_frame)
    
    def create_pages(self):
        # Play Page
        play_page = QFrame()
        play_layout = QVBoxLayout(play_page)
        
        # Minecraft logo
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":images/minecraft-logo.png").scaledToWidth(400, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Version info
        version_label = QLabel("Minecraft Java Edition 1.20")
        version_label.setStyleSheet("font-size: 18px;")
        version_label.setAlignment(Qt.AlignCenter)
        
        # Play button
        self.play_button = QPushButton("PLAY")
        self.play_button.setFixedSize(200, 50)
        self.play_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.play_button.clicked.connect(self.launch_minecraft)
        
        # Loading animation
        self.loading_label = QLabel("Preparing to launch Minecraft...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        
        play_layout.addStretch()
        play_layout.addWidget(logo_label)
        play_layout.addSpacing(20)
        play_layout.addWidget(version_label)
        play_layout.addSpacing(30)
        play_layout.addWidget(self.play_button, 0, Qt.AlignCenter)
        play_layout.addSpacing(20)
        play_layout.addWidget(self.loading_label)
        play_layout.addStretch()
        
        # News Page
        news_page = QFrame()
        news_layout = QVBoxLayout(news_page)
        
        news_title = QLabel("Latest News")
        news_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        news_title.setAlignment(Qt.AlignCenter)
        
        news_content = QLabel(
            "<h3>Minecraft 1.20 Update</h3>"
            "<p>The Trails & Tales update is here! Explore new biomes, "
            "mobs, and crafting options.</p>"
            "<hr>"
            "<h3>Minecraft Live 2023</h3>"
            "<p>Watch the annual Minecraft event for news about upcoming features.</p>"
        )
        news_content.setWordWrap(True)
        news_content.setAlignment(Qt.AlignLeft)
        news_content.setStyleSheet("padding: 20px;")
        
        news_layout.addWidget(news_title)
        news_layout.addWidget(news_content)
        
        # Settings Page
        settings_page = QFrame()
        settings_layout = QVBoxLayout(settings_page)
        
        settings_title = QLabel("Settings")
        settings_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        settings_title.setAlignment(Qt.AlignCenter)
        
        settings_content = QLabel(
            "<p>Java Path: <code>/usr/bin/java</code></p>"
            "<p>Memory: 4GB allocated</p>"
            "<p>Resolution: 1280x720</p>"
        )
        settings_content.setWordWrap(True)
        settings_content.setAlignment(Qt.AlignLeft)
        settings_content.setStyleSheet("padding: 20px;")
        
        settings_layout.addWidget(settings_title)
        settings_layout.addWidget(settings_content)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(play_page)
        self.stacked_widget.addWidget(news_page)
        self.stacked_widget.addWidget(settings_page)
    
    def launch_minecraft(self):
        """Simulate launching Minecraft"""
        self.play_button.setEnabled(False)
        self.loading_label.show()
        
        # Simulate loading process
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_text)
        self.loading_counter = 0
        self.loading_texts = [
            "Downloading assets...",
            "Extracting native libraries...",
            "Verifying game files...",
            "Starting Minecraft..."
        ]
        self.loading_timer.start(1500)
    
    def update_loading_text(self):
        """Update loading text during launch simulation"""
        if self.loading_counter < len(self.loading_texts):
            self.loading_label.setText(self.loading_texts[self.loading_counter])
            self.loading_counter += 1
        else:
            self.loading_timer.stop()
            self.loading_label.setText("Launch failed - Minecraft not installed")
            self.play_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Create and show launcher
    launcher = MinecraftLauncher()
    launcher.show()
    
    sys.exit(app.exec_())