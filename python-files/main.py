import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# タブをインポート（各ファイルは tabs/ フォルダに置く想定）
from tabs.tab_main import MainTab
from tabs.tab_network import NetworkTab
from tabs.tab_tools import ToolsTab
from tabs.tab_music import MusicTab
from tabs.tab_settings import SettingsTab

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("オールインワンユーティリティアプリ")
        self.resize(1000, 700)

        # タブウィジェット
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 各タブのインスタンス作成
        self.main_tab = MainTab()
        self.network_tab = NetworkTab()
        self.tools_tab = ToolsTab()
        self.music_tab = MusicTab()
        # 設定タブにselfを渡し、背景反映をコントロール可能に
        self.settings_tab = SettingsTab(main_window=self)

        # タブを追加
        self.tabs.addTab(self.main_tab, "🏠 メイン")
        self.tabs.addTab(self.network_tab, "🌐 ネットワーク")
        self.tabs.addTab(self.tools_tab, "🛠 ツール")
        self.tabs.addTab(self.music_tab, "🎵 音楽")
        self.tabs.addTab(self.settings_tab, "⚙️ 設定")

    def apply_background_image(self, image_path):
        # ウィンドウ全体に背景画像を設定（スタイルシート利用）
        self.setStyleSheet(f"""
            QMainWindow {{
                background-image: url({image_path});
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

