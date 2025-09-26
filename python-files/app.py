"""
Toyota Random Data Generator (PySide6)

Features:
- Styled UI with colors, logo, headers
- Login screen (password = ari123, any username)
- Main screen shows company info, user name, and version
- Extract button generates 200–999 random rows of Toyota car data
- Each field has ~15% chance of being empty to simulate incomplete data
- Data saved automatically in same folder as script/exe
- Validation checks columns + empty fields; fails if anything missing

Requirements:
    pip install PySide6 pandas openpyxl
"""

import sys
import os
import random
import csv
import uuid
from datetime import datetime, timedelta, date

try:
    import pandas as pd
except Exception:
    pd = None

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox,
    QFileDialog, QDateEdit, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPixmap


# -------------------- Helper functions --------------------

def random_date_between(start_date: date, end_date: date) -> date:
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    delta = end_date - start_date
    if delta.days <= 0:
        return start_date
    offset = random.randint(0, delta.days)
    return start_date + timedelta(days=offset)

def random_vin():
    chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(17))

def random_registration():
    letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
    numbers = ''.join(random.choice('0123456789') for _ in range(4))
    return f"S{letters}{numbers}"

def maybe_empty(value, prob=0.15):
    """Return value or empty string based on probability."""
    return value if random.random() > prob else ""


# -------------------- Login Window --------------------

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Toyota Server")
        self.setGeometry(400, 250, 420, 260)
        self.setStyleSheet("background-color: #f0f4f7;")

        layout = QVBoxLayout()

        # Company Logo + Info
        header_layout = QVBoxLayout()
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "toyota_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo)

        title = QLabel("Toyota Server")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #c00;")
        header_layout.addWidget(title)

        subtitle = QLabel("Company: Toyota | Version: 56.10")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Login form
        form_layout = QGridLayout()
        form_layout.setContentsMargins(50, 20, 50, 20)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(15)

        form_layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_edit = QLineEdit()
        form_layout.addWidget(self.username_edit, 0, 1)

        form_layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_edit, 1, 1)

        layout.addLayout(form_layout)

        btn = QPushButton("Login")
        btn.setStyleSheet("background-color: #0078D7; color: white; font-weight: bold; padding: 6px;")
        btn.clicked.connect(self.try_login)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def try_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if password != 'ari123':
            QMessageBox.warning(self, "Login failed", "Wrong password. Hint: password is ari123")
            return
        if username == "":
            QMessageBox.warning(self, "Login failed", "Please enter a username")
            return
        self.main = MainWindow(username)
        self.main.show()
        self.close()


# -------------------- Main Window --------------------

class MainWindow(QWidget):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setWindowTitle("Toyota Server - Data Generator")
        self.setGeometry(200, 200, 850, 650)
        self.setStyleSheet("background-color: #ffffff;")
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with Logo + Info
        header_layout = QHBoxLayout()

        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "toyota_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
        header_layout.addWidget(logo)

        info_layout = QVBoxLayout()
        name_lbl = QLabel("Toyota Server")
        name_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        name_lbl.setStyleSheet("color: #c00;")
        version_lbl = QLabel("Company: Toyota | Version: 56.10")
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(version_lbl)
        header_layout.addLayout(info_layout)

        header_layout.addStretch()

        user_lbl = QLabel(f"Logged in as: {self.username}")
        user_lbl.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(user_lbl)

        main_layout.addLayout(header_layout)

        # Date range selection
        range_frame = QFrame()
        range_frame.setFrameShape(QFrame.StyledPanel)
        range_layout = QHBoxLayout()

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        past = QDate.currentDate().addYears(-10)
        self.from_date.setDate(past)

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())

        range_layout.addWidget(QLabel("From:"))
        range_layout.addWidget(self.from_date)
        range_layout.addWidget(QLabel("To:"))
        range_layout.addWidget(self.to_date)

        range_frame.setLayout(range_layout)
        main_layout.addWidget(QLabel("Select Launch Date Range:"))
        main_layout.addWidget(range_frame)

        # Extract button
        self.extract_btn = QPushButton("Extract Data From Server")
        self.extract_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.extract_btn.clicked.connect(self.on_extract)
        main_layout.addWidget(self.extract_btn, alignment=Qt.AlignCenter)

        # Last saved file
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Last saved file:"))
        self.last_saved_line = QLineEdit()
        self.last_saved_line.setReadOnly(True)
        file_layout.addWidget(self.last_saved_line)
        main_layout.addLayout(file_layout)

        # Validation / upload section
        upload_label = QLabel("Validate and Upload File:")
        upload_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(upload_label)

        upload_group = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        upload_group.addWidget(self.file_path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        upload_group.addWidget(browse_btn)
        self.upload_btn = QPushButton("Validate and Upload to Server")
        self.upload_btn.setStyleSheet("background-color: #0078D7; color: white; font-weight: bold; padding: 6px;")
        self.upload_btn.clicked.connect(self.validate_and_upload)
        upload_group.addWidget(self.upload_btn)
        main_layout.addLayout(upload_group)

        # Status messages
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #f8f9fa;")
        main_layout.addWidget(self.log)

        self.setLayout(main_layout)

    # -------------------- Actions --------------------

    def on_extract(self):
        from_date = self.from_date.date().toPython()
        to_date = self.to_date.date().toPython()
        self.generate_and_save(from_date, to_date)

    def generate_and_save(self, from_date, to_date):
        try:
            num_rows = random.randint(200, 999)
            rows = []
            for _ in range(num_rows):
                launch_date = random_date_between(from_date, to_date)
                rows.append({
                    "car_id": maybe_empty(str(uuid.uuid4())[:8]),
                    "model": maybe_empty(random.choice(["Corolla", "Camry", "Yaris", "Supra", "Hilux", "Fortuner"])),
                    "launch_date": maybe_empty(launch_date.isoformat()),
                    "spare_part_id": maybe_empty(str(uuid.uuid4())[:6]),
                    "spare_part_price": maybe_empty(round(random.uniform(50, 500), 2)),
                    "color": maybe_empty(random.choice(["Red", "Blue", "White", "Black", "Silver", "Gray"])),
                    "mileage_km": maybe_empty(random.randint(1000, 200000)),
                    "engine_type": maybe_empty(random.choice(["Petrol", "Diesel", "Hybrid", "Electric"])),
                    "transmission": maybe_empty(random.choice(["Manual", "Automatic", "CVT"])),
                    "price": maybe_empty(round(random.uniform(5000, 50000), 2)),
                    "registration_number": maybe_empty(random_registration()),
                    "owner_id": maybe_empty(str(uuid.uuid4())[:10]),
                    "service_count": maybe_empty(random.randint(0, 10)),
                    "last_service_date": maybe_empty(random_date_between(from_date, to_date).isoformat()),
                    "vin": maybe_empty(random_vin())
                })

            base_dir = os.path.dirname(sys.argv[0])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(base_dir, f"toyota_data_{timestamp}.csv")

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            self.last_saved_line.setText(file_path)
            self.status_label.setText(f"✅ File saved: {file_path}")
            self.log.append(f"[INFO] Generated {num_rows} rows between {from_date} and {to_date}")
            QMessageBox.information(self, "File Saved", f"Random data successfully saved to:\n\n{file_path}")

        except Exception as e:
            self.status_label.setText("⚠️ Could not generate file. Please try again.")
            self.log.append(f"[ERROR] Generation failed: {e}")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def validate_and_upload(self):
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "No file", "Please select a file to upload.")
            return
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File missing", "Selected file does not exist.")
            return

        required_columns = [
            "car_id", "model", "launch_date", "spare_part_id", "spare_part_price",
            "color", "mileage_km", "engine_type", "transmission", "price",
            "registration_number", "owner_id", "service_count", "last_service_date", "vin"
        ]

        try:
            if pd:
                df = pd.read_csv(file_path)

                # Check required columns
                for col in required_columns:
                    if col not in df.columns:
                        QMessageBox.critical(self, "Validation Failed",
                                             f"❌ Missing required column: {col}\nUpdate to server failed.")
                        self.log.append(f"[ERROR] Missing column: {col}")
                        return

                # Check for empty values
                if df.isnull().values.any() or (df.astype(str).apply(lambda x: x.str.strip() == "")).any().any():
                    QMessageBox.critical(self, "Validation Failed",
                                         "❌ File has missing/empty values.\nUpdate to server failed.")
                    self.log.append("[ERROR] Empty values found in file")
                    return

                rows = len(df)

            else:
                # Fallback without pandas
                import csv
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for col in required_columns:
                        if col not in reader.fieldnames:
                            QMessageBox.critical(self, "Validation Failed",
                                                 f"❌ Missing required column: {col}\nUpdate to server failed.")
                            self.log.append(f"[ERROR] Missing column: {col}")
                            return
                    for i, row in enumerate(reader, start=1):
                        for col in required_columns:
                            if row[col] is None or str(row[col]).strip() == "":
                                QMessageBox.critical(self, "Validation Failed",
                                                     f"❌ Empty value in column '{col}' (row {i})\nUpdate to server failed.")
                                self.log.append(f"[ERROR] Empty value in {col} row {i}")
                                return
                    rows = i

            process_id = f"PROC-{random.randint(10000, 99999)}"
            QMessageBox.information(self, "Success",
                                    f"✅ File validated and uploaded successfully.\nProcess ID: {process_id}")
            self.log.append(f"[UPLOAD] File validated with {rows} rows: {file_path}")
            self.log.append(f"[UPLOAD] Process ID: {process_id}")

        except Exception as e:
            QMessageBox.critical(self, "Upload failed", f"Could not validate/upload: {e}")
            self.log.append(f"[ERROR] Validation exception: {e}")


# -------------------- Run --------------------

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    sys.exit(app.exec())

