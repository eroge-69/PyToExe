import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange
)


class LoyaltyPointsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loyalty Points Manager")
        self.resize(800, 600)

        self.tabs = QTabWidget()
        self.customers_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.customers_tab, "All Customers")
        self.tabs.addTab(self.settings_tab, "Settings")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.init_customers_tab()
        self.init_settings_tab()

    def init_customers_tab(self):
        layout = QVBoxLayout()

        # جدول العملاء (بيانات مؤقتة للتجربة)
        self.table = QTableWidget(5, 3)  # 5 عملاء × 3 أعمدة
        self.table.setHorizontalHeaderLabels(["Customer Name", "Points", "Level"])
        customers = [
            ("Ali", "120", "3 Stars"),
            ("Sara", "500", "4 Stars"),
            ("Omar", "50", "1 Star"),
            ("Mona", "800", "5 Stars"),
            ("Hassan", "300", "2 Stars"),
        ]
        for i, (name, points, level) in enumerate(customers):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(points))
            self.table.setItem(i, 2, QTableWidgetItem(level))

        layout.addWidget(self.table)
        self.customers_tab.setLayout(layout)

    def init_settings_tab(self):
        layout = QVBoxLayout()

        # Database path
        db_layout = QHBoxLayout()
        db_label = QLabel("Database Path:")
        self.db_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_db)
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_path)
        db_layout.addWidget(browse_btn)
        layout.addLayout(db_layout)

        # Points per dollar
        points_layout = QHBoxLayout()
        points_label = QLabel("Points per 1 US Dollar:")
        self.points_per_dollar = QLineEdit("100")
        points_layout.addWidget(points_label)
        points_layout.addWidget(self.points_per_dollar)
        layout.addLayout(points_layout)

        # Threshold
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Payment Threshold:")
        self.threshold = QLineEdit("100")
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold)
        layout.addLayout(threshold_layout)

        # WhatsApp template
        msg_label = QLabel("WhatsApp Message Template:")
        self.msg_template = QTextEdit("Dear {customer_name}, you earned {points} points.")
        layout.addWidget(msg_label)
        layout.addWidget(self.msg_template)

        # Shop name
        shop_layout = QHBoxLayout()
        shop_label = QLabel("Shop Name:")
        self.shop_name = QLineEdit("My Shop")
        shop_layout.addWidget(shop_label)
        shop_layout.addWidget(self.shop_name)
        layout.addLayout(shop_layout)

        # Save button
        save_btn = QPushButton("Update Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.settings_tab.setLayout(layout)

    def browse_db(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Database", "", "Database Files (*.db *.sqlite)")
        if file:
            self.db_path.setText(file)

    def save_settings(self):
        settings = {
            "db_path": self.db_path.text(),
            "points_per_dollar": self.points_per_dollar.text(),
            "threshold": self.threshold.text(),
            "msg_template": self.msg_template.toPlainText(),
            "shop_name": self.shop_name.text(),
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        print("✅ Settings saved!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoyaltyPointsManager()
    window.show()
    sys.exit(app.exec())
