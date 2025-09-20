import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QMessageBox, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt


class RowWidget(QWidget):
    def __init__(self, text1="", text2=""):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.text1 = QLineEdit(text1)
        self.text2 = QLineEdit(text2)

        self.lock_btn = QCheckBox("🔒")
        self.lock_btn.setToolTip("Lock/Unlock row")
        self.lock_btn.stateChanged.connect(self.toggle_lock)

        self.remove_btn = QPushButton("❌")
        self.remove_btn.setFixedWidth(30)
        self.remove_btn.clicked.connect(self.deleteLater)

        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.text2)
        self.layout.addWidget(self.lock_btn)
        self.layout.addWidget(self.remove_btn)

    def toggle_lock(self, state):
        locked = state == Qt.Checked
        self.text1.setReadOnly(locked)
        self.text2.setReadOnly(locked)

    def get_data(self):
        return [self.text1.text(), self.text2.text()]


class TabContent(QWidget):
    def __init__(self, name="New Tab"):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.rows_layout = QVBoxLayout()
        self.layout.addLayout(self.rows_layout)

        self.add_btn = QPushButton("+ Add Row")
        self.add_btn.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_btn)

    def add_row(self, text1="", text2=""):
        row = RowWidget(text1, text2)
        self.rows_layout.addWidget(row)

    def get_data(self):
        data = []
        for i in range(self.rows_layout.count()):
            row = self.rows_layout.itemAt(i).widget()
            if row:
                data.append(row.get_data())
        return data


class CarsInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cars Info")
        self.resize(800, 600)

        self.layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QHBoxLayout()
        self.export_btn = QPushButton("⬆ Export")
        self.import_btn = QPushButton("⬇ Import")
        self.add_tab_btn = QPushButton("+ Add Tab")

        self.export_btn.clicked.connect(self.export_data)
        self.import_btn.clicked.connect(self.import_data)
        self.add_tab_btn.clicked.connect(self.add_tab)

        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.add_tab_btn)
        toolbar.addStretch()
        self.layout.addLayout(toolbar)

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tabs)

        # Start with one tab
        self.add_tab("Tab 1")

    def add_tab(self, name="New Tab"):
        tab = TabContent(name)
        index = self.tabs.addTab(tab, name)
        self.tabs.setCurrentIndex(index)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)

    def close_tab(self, index):
        reply = QMessageBox.question(
            self, "Remove Tab",
            f"Are you sure you want to remove tab '{self.tabs.tabText(index)}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.tabs.removeTab(index)

    def export_data(self):
        data = {}
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            name = self.tabs.tabText(i)
            data[name] = tab.get_data()

        fname, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Export", f"Data exported to {fname}")

    def import_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.tabs.clear()
            for name, rows in data.items():
                tab = TabContent(name)
                for row in rows:
                    tab.add_row(row[0], row[1])
                self.tabs.addTab(tab, name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarsInfoApp()
    window.show()
    sys.exit(app.exec_())
