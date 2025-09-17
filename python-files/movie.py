from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QTableWidget, QTableWidgetItem, \
    QHeaderView, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox, QLabel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import threading
import time
import os, sys

class Ui_Form(QWidget):
    def __init__(self):
        super().__init__()
        self.drivers = []
        self.setupUi()

    def setupUi(self):
        self.resize(900, 750)
        self.setWindowTitle("Controll Fb")

        main_layout = QVBoxLayout(self)

        # Checkbox for Add Friend
        top_layout = QHBoxLayout()
        self.checkBox = QCheckBox("Add Fri", self)
        self.checkBox.setFixedSize(75, 20)
        top_layout.addWidget(self.checkBox)
        top_layout.addStretch(1)
        main_layout.addLayout(top_layout)

        # UID input for random Add Friend
        uid_layout = QHBoxLayout()
        uid_label = QLabel("UIDs (one per line):")
        self.uidTextEdit = QTextEdit()
        self.uidTextEdit.setFixedHeight(80)
        uid_layout.addWidget(uid_label)
        uid_layout.addWidget(self.uidTextEdit)
        main_layout.addLayout(uid_layout)

        # Table input
        self.textEdit = QTextEdit()
        self.textEdit.setPlaceholderText("UID|Name|Password|ProfilePath")
        main_layout.addWidget(self.textEdit)

        # Buttons
        btn_layout = QHBoxLayout()
        self.pushButtonAdd = QPushButton("Add To Table")
        self.pushButtonPrint = QPushButton("Print Data")
        self.pushButtonSelenium = QPushButton("Run Selenium")
        self.pushButtonCloseAll = QPushButton("Close All Chrome")
        btn_layout.addWidget(self.pushButtonAdd)
        btn_layout.addWidget(self.pushButtonPrint)
        btn_layout.addWidget(self.pushButtonSelenium)
        btn_layout.addWidget(self.pushButtonCloseAll)
        main_layout.addLayout(btn_layout)

        # Table widget
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["UID", "Name", "Password", "Profile Path"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.MultiSelection)
        main_layout.addWidget(self.tableWidget)

        # Connect buttons
        self.pushButtonAdd.clicked.connect(self.add_to_table)
        self.pushButtonPrint.clicked.connect(self.print_table_data)
        self.pushButtonSelenium.clicked.connect(self.run_selenium_threads)
        self.pushButtonCloseAll.clicked.connect(self.close_all_chrome)

    def add_to_table(self):
        raw = self.textEdit.toPlainText().strip()
        if not raw:
            return
        for line in raw.splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                parts += [""] * (4 - len(parts))
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for col, val in enumerate(parts[:4]):
                self.tableWidget.setItem(row, col, QTableWidgetItem(val))
        self.textEdit.clear()

    def print_table_data(self):
        for r in range(self.tableWidget.rowCount()):
            values = [self.tableWidget.item(r, c).text() if self.tableWidget.item(r, c) else "" for c in range(self.tableWidget.columnCount())]
            print(" | ".join(values))

    def get_selected_rows(self):
        return [i.row() for i in self.tableWidget.selectionModel().selectedRows()]

    def run_selenium_for_row(self, uid, pwd, profile, position, add_friend, random_uids):
        try:
            options = webdriver.ChromeOptions()
            if profile and os.path.exists(profile):
                options.add_argument(f"user-data-dir={profile}")
            options.add_argument("--app=https://web.facebook.com")
            service = Service("chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_window_size(250, 430)
            driver.set_window_position(*position)
            self.drivers.append(driver)
            print(f"✅ Selenium running for UID={uid} at position {position}")

            if add_friend and random_uids:
                uid_index = 0
                while uid_index < len(random_uids):
                    target_uid = random_uids[uid_index].strip()
                    uid_index += 1
                    try:
                        driver.get(f"https://web.facebook.com/{target_uid}")
                        time.sleep(5)

                        # Try first XPath
                        try:
                            xpath1 = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[4]/div/div/div[1]"
                            element = driver.find_element(By.XPATH, xpath1)
                            element.click()
                            print(f"✅ Add Friend clicked (XPath1) for UID={target_uid}")
                        except:
                            # Try second XPath
                            xpath2 = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[4]/div/div/div[3]/div/div/div"
                            element = driver.find_element(By.XPATH, xpath2)
                            element.click()
                            print(f"✅ Add Friend clicked (XPath2) for UID={target_uid}")
                    except Exception as e:
                        print(f"⚠️ UID {target_uid} failed: {e}, skipping to next UID")
                print("✅ Finished all Add Friend UIDs for this row")
            else:
                driver.get("https://web.facebook.com")
                print(f"🔘 Add Fri unchecked or no UIDs, opening standard profile for UID={uid}")

        except Exception as e:
            print(f"⚠️ Error launching Selenium for UID={uid}: {e}")

    def run_selenium_threads(self):
        rows = self.get_selected_rows()
        if not rows:
            QMessageBox.warning(self, "Warning", "Please select at least one row")
            return

        add_friend = self.checkBox.isChecked()
        print("🔘 Add Friend mode is ON" if add_friend else "🔘 Add Friend mode is OFF")

        # Parse UIDs
        random_uids = []
        raw_uids = self.uidTextEdit.toPlainText().strip()
        if raw_uids:
            random_uids = [uid.strip() for uid in raw_uids.splitlines() if uid.strip()]

        # Window positions
        screen_width, screen_height = 1920, 1080
        win_width, win_height = 250, 430
        margin = 10
        positions = []
        x_offset = margin
        y_offset = margin
        for _ in rows:
            if x_offset + win_width > screen_width:
                x_offset = margin
                y_offset += win_height + margin
            if y_offset + win_height > screen_height:
                y_offset = margin
            positions.append((x_offset, y_offset))
            x_offset += win_width + margin

        # Launch threads
        for row, pos in zip(rows, positions):
            uid = self.tableWidget.item(row, 0).text()
            pwd = self.tableWidget.item(row, 2).text()
            profile = self.tableWidget.item(row, 3).text()
            t = threading.Thread(
                target=self.run_selenium_for_row,
                args=(uid, pwd, profile, pos, add_friend, random_uids)
            )
            t.start()
            time.sleep(0.2)

    def close_all_chrome(self):
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
        print("✅ All Chrome windows closed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_Form()
    window.show()
    sys.exit(app.exec())
